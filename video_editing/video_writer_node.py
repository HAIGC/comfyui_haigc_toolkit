"""
视频保存节点
将图像序列合并保存为视频文件,可选合并音频,并在前端显示预览
"""

import os
import sys
import shutil
import subprocess
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
import torch

import folder_paths

def _cleanup_opencv_env():
    return

# 尝试导入 OpenCV，如果失败则提供详细错误信息
_cv2_import_error = None
_cv2 = None

try:
    _cleanup_opencv_env()
    import cv2 as _cv2
except Exception as e:
    _cv2_import_error = str(e)
    print(f"[视频保存] OpenCV 导入失败: {_cv2_import_error}")
    print("[视频保存] 可能的解决方案:")
    print("  1. 卸载所有 OpenCV 版本: pip uninstall opencv-python opencv-contrib-python opencv-python-headless -y")
    print("  2. 重新安装: pip install opencv-python")
    print("  3. 如果使用 conda: conda install -c conda-forge opencv")

class VideoWriterNode:
    """视频保存节点"""
    
    QUALITY_PRESETS = {
        "高": {"crf": "18", "vp9": "28"},
        "中": {"crf": "23", "vp9": "32"},
        "低": {"crf": "28", "vp9": "38"},
    }
    
    VIDEO_FORMATS = {
        "MP4 (H264)": {
            "extension": ".mp4",
            "requires_ffmpeg": False,
            "supports_audio": True,
            "video_args": ["-c:v", "copy", "-movflags", "faststart"],
            "audio_args": ["-c:a", "aac", "-b:a", "192k"],
            "bitrate_codec": "libx264",
            "audio_codec": "aac",
        },
        "MOV (H264)": {
            "extension": ".mov",
            "supports_audio": True,
            "video_args": ["-c:v", "copy"],
            "audio_args": ["-c:a", "aac", "-b:a", "192k"],
            "bitrate_codec": "libx264",
            "audio_codec": "aac",
        },
        "MOV (ProRes422)": {
            "extension": ".mov",
            "supports_audio": True,
            "video_args": ["-c:v", "prores_ks", "-profile:v", "3"],
            "audio_args": ["-c:a", "aac", "-b:a", "192k"],
            "audio_codec": "aac",
        },
        "WEBM (VP9)": {
            "extension": ".webm",
            "supports_audio": True,
            "video_args_builder": "vp9",
            "audio_args": ["-c:a", "libopus", "-b:a", "128k"],
            "bitrate_codec": "libvpx-vp9",
            "audio_codec": "libopus",
        },
        "GIF (动画)": {
            "extension": ".gif",
            "supports_audio": False,
            "video_args": ["-vf", "fps=12,scale=iw:-1:flags=lanczos", "-loop", "0", "-f", "gif"],
        },
        "GIF (高质量)": {
            "extension": ".gif",
            "supports_audio": False,
            "mode": "gif_palette",
            "palette_fps": 18,
            "scale_expr": "scale=min(960\\,iw):-1:flags=lanczos",
            "dither": "bayer",
        },
        "GIF (原画质)": {
            "extension": ".gif",
            "supports_audio": False,
            "mode": "gif_palette",
            "palette_fps": None,  # 使用源帧率
            "scale_expr": "scale=iw:-1:flags=lanczos",
            "dither": "none",
        },
        "MPEG-2": {
            "extension": ".mpg",
            "requires_ffmpeg": True,
            "supports_audio": True,
            "video_args": ["-c:v", "mpeg2video", "-q:v", "2"],
            "audio_args": ["-c:a", "mp2", "-b:a", "192k"],
            "bitrate_codec": "mpeg2video",
            "audio_codec": "mp2",
        },
        "AVI (MPEG-4)": {
            "extension": ".avi",
            "requires_ffmpeg": True,
            "supports_audio": True,
            "video_args": ["-c:v", "mpeg4"],
            "audio_args": ["-c:a", "mp3", "-b:a", "192k"],
            "bitrate_codec": "mpeg4",
            "audio_codec": "libmp3lame",
        },
        "AVI (H264)": {
            "extension": ".avi",
            "requires_ffmpeg": True,
            "supports_audio": True,
            "video_args": ["-c:v", "libx264"],
            "audio_args": ["-c:a", "aac", "-b:a", "192k"],
            "bitrate_codec": "libx264",
            "audio_codec": "aac",
        },
    }
    
    DEFAULT_FORMAT = "MP4 (H264)"
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "images": ("IMAGE",),
                "视频帧率": ("FLOAT", {
                    "default": 30.0,
                    "min": 1.0,
                    "max": 120.0,
                    "step": 0.1
                }),
                "输出路径": ("STRING", {
                    "default": "output/video.mp4",
                    "multiline": False
                }),
                "视频编码": (["H264", "H265", "VP9", "XVID"], {
                    "default": "H264"
                }),
                "视频质量": (["高", "中", "低"], {
                    "default": "高"
                }),
                "输出格式": (list(cls.VIDEO_FORMATS.keys()), {
                    "default": cls.DEFAULT_FORMAT
                }),
                "自动添加时间戳": (["是", "否"], {
                    "default": "是"
                }),
            },
            "optional": {
                "音频": ("AUDIO",),
                "自定义比特率_Kbps": ("FLOAT", {
                    "default": 1500.0,
                    "min": 0.0,
                    "max": 200000.0,
                    "step": 10.0,
                    "tooltip": "0 表示使用预设质量; >0 时按填写的 Kbps 重新编码"
                }),
                "音频比特率_Kbps": ("FLOAT", {
                    "default": 0.0,
                    "min": 0.0,
                    "max": 512.0,
                    "step": 8.0,
                    "tooltip": "0 表示使用默认音频比特率"
                }),
            },
        }
    
    RETURN_TYPES = ("STRING", "INT", "FLOAT")
    RETURN_NAMES = ("文件路径", "总帧数", "视频时长")
    FUNCTION = "save_video"
    CATEGORY = "HAIGC工具集/视频剪辑"
    OUTPUT_NODE = True
    
    def save_video(
        self,
        images,
        视频帧率,
        输出路径,
        视频编码,
        视频质量,
        输出格式,
        自动添加时间戳,
        音频: Optional[Dict[str, Any]] = None,
        自定义比特率_Kbps: float = 0.0,
        音频比特率_Kbps: float = 0.0
    ):
        """保存视频文件"""
        
        # 检查 OpenCV 是否成功导入
        if _cv2 is None:
            error_msg = f"错误：OpenCV 导入失败\n{_cv2_import_error or '未知错误'}\n\n解决方案:\n1. 卸载所有 OpenCV 版本: pip uninstall opencv-python opencv-contrib-python opencv-python-headless -y\n2. 重新安装: pip install opencv-python\n3. 重启 ComfyUI"
            print(f"[视频保存] {error_msg}")
            return {"result": (error_msg, 0, 0.0)}
        
        # 使用模块级别导入的 cv2
        cv2 = _cv2
        
        audio_temp_path: Optional[Path] = None
        working_video_path: Optional[Path] = None
        
        try:
            batch_size, height, width, channels = images.shape
            
            format_config = self.VIDEO_FORMATS.get(输出格式, self.VIDEO_FORMATS[self.DEFAULT_FORMAT])
            final_extension = format_config.get("extension", ".mp4")
            
            # 解析并规范输出路径
            output_root = Path(folder_paths.get_output_directory()).resolve()
            video_path = self._resolve_output_path(
                输出路径,
                output_root,
                final_extension,
                自动添加时间戳 == "是"
            )
            
            working_video_path = self._get_working_path(video_path)
            
            video_path.parent.mkdir(parents=True, exist_ok=True)
            
            # 如果提供了音频，先导出临时wav文件
            if 音频:
                try:
                    audio_temp_path = self._export_audio_temp(音频)
                except Exception as audio_error:
                    audio_temp_path = None
                    print(f"[视频保存] 音频处理失败: {audio_error}")
            
            # 编码器映射
            codec_map = {
                "H264": "avc1",  # H.264
                "H265": "hev1",  # H.265/HEVC
                "VP9": "vp09",   # VP9
                "XVID": "XVID"   # XVID
            }
            
            # 如果编码器不支持，回退到mp4v
            fourcc_str = codec_map.get(视频编码, "mp4v")
            
            try:
                fourcc = cv2.VideoWriter_fourcc(*fourcc_str)
            except:
                print(f"[视频保存] 警告：编码器 {视频编码} 不可用，使用默认编码器")
                fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            
            # 创建视频写入器
            out = cv2.VideoWriter(str(working_video_path), fourcc, 视频帧率, (width, height))
            
            if not out.isOpened():
                raise Exception("无法创建视频写入器")
            
            print(f"[视频保存] 开始保存视频...")
            print(f"  文件: {video_path}")
            print(f"  帧数: {batch_size}, FPS: {视频帧率}, 分辨率: {width}x{height}")
            print(f"  编码: {视频编码}, 质量: {视频质量}")
            
            # 写入每一帧
            for i in range(batch_size):
                # 转换为numpy数组 [0, 1] -> [0, 255]
                frame = images[i].cpu().numpy()
                frame = (frame * 255).astype(np.uint8)
                
                # RGB转BGR（OpenCV需要）
                frame_bgr = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
                
                # 根据质量调整（可选的额外处理）
                if 视频质量 == "低":
                    # 可以添加额外的压缩或降采样
                    pass
                
                out.write(frame_bgr)
                
                # 进度显示
                if (i + 1) % 30 == 0 or i == batch_size - 1:
                    progress = (i + 1) / batch_size * 100
                    print(f"  进度: {progress:.1f}% ({i+1}/{batch_size})")
            
            out.release()
            
            duration = batch_size / 视频帧率
            
            audio_attached = self._transcode_video(
                source_path=working_video_path,
                target_path=video_path,
                format_config=format_config,
                audio_path=audio_temp_path,
                视频质量=视频质量,
                fps=视频帧率,
                video_duration=duration,
                bitrate_kbps=self._sanitize_bitrate(自定义比特率_Kbps),
                audio_bitrate_kbps=self._sanitize_bitrate(音频比特率_Kbps)
            )
            
            # 获取文件信息
            file_size = os.path.getsize(video_path) / (1024 * 1024)  # MB
            
            print(f"[视频保存] ✅ 保存完成！")
            print(f"  文件大小: {file_size:.2f} MB")
            print(f"  视频时长: {duration:.2f} 秒")
            
            # 获取实际使用的比特率
            actual_video_bitrate = 0
            actual_audio_bitrate = 0
            
            try:
                actual_video_bitrate = self._sanitize_bitrate(自定义比特率_Kbps) if 自定义比特率_Kbps > 0 else 0
                actual_audio_bitrate = self._sanitize_bitrate(音频比特率_Kbps) if 音频比特率_Kbps > 0 else 0
                
                # 如果未指定，尝试从输出文件获取
                if actual_video_bitrate == 0 or (actual_audio_bitrate == 0 and audio_attached):
                    try:
                        output_bitrates = self._get_output_bitrates(video_path)
                        if actual_video_bitrate == 0:
                            actual_video_bitrate = output_bitrates.get("video", 0)
                        if actual_audio_bitrate == 0 and audio_attached:
                            actual_audio_bitrate = output_bitrates.get("audio", 0)
                    except Exception as e:
                        print(f"[视频保存] 警告：无法获取输出文件比特率: {str(e)}")
            except Exception as e:
                print(f"[视频保存] 警告：比特率处理失败: {str(e)}")
            
            try:
                ui_info = self._build_video_preview(
                    video_path=video_path,
                    output_root=output_root,
                    fps=视频帧率,
                    frame_count=batch_size,
                    duration=duration,
                    has_audio=audio_attached,
                    format_label=输出格式,
                    file_size_mb=round(file_size, 2),
                    width=int(images.shape[2]),
                    height=int(images.shape[1]),
                    video_bitrate_kbps=actual_video_bitrate,
                    audio_bitrate_kbps=actual_audio_bitrate
                )
            except Exception as e:
                print(f"[视频保存] 错误：构建预览信息失败: {str(e)}")
                import traceback
                traceback.print_exc()
                # 返回基本预览信息
                ui_info = self._build_video_preview(
                    video_path=video_path,
                    output_root=output_root,
                    fps=视频帧率,
                    frame_count=batch_size,
                    duration=duration,
                    has_audio=audio_attached,
                    format_label=输出格式,
                    file_size_mb=round(file_size, 2),
                    width=int(images.shape[2]),
                    height=int(images.shape[1]),
                    video_bitrate_kbps=0,
                    audio_bitrate_kbps=0
                )
            
            return {
                "ui": ui_info,
                "result": (str(video_path), batch_size, duration)
            }
            
        except Exception as e:
            error_msg = f"保存失败：{str(e)}"
            print(f"[视频保存] {error_msg}")
            return {"result": (error_msg, 0, 0.0)}
        finally:
            if audio_temp_path and audio_temp_path.exists():
                try:
                    audio_temp_path.unlink()
                except OSError:
                    pass
            if working_video_path and working_video_path.exists():
                try:
                    working_video_path.unlink()
                except OSError:
                    pass
    
    def _resolve_output_path(
        self,
        path_str: str,
        output_root: Path,
        extension: str,
        add_timestamp: bool
    ) -> Path:
        """
        解析用户输入的输出路径：
        - 相对路径默认相对于 ComfyUI 的 output 目录
        - 绝对路径直接使用
        """
        raw_path = Path(path_str.strip()).expanduser()
        if raw_path.suffix == "":
            raw_path = raw_path.with_suffix(extension)
        else:
            raw_path = raw_path.with_suffix(extension)
        
        if raw_path.is_absolute():
            resolved = raw_path.resolve()
        else:
            resolved = (output_root / raw_path).resolve()
        
        if add_timestamp:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            resolved = resolved.with_name(f"{resolved.stem}_{timestamp}{resolved.suffix}")
        
        return resolved
    
    def _sanitize_bitrate(self, bitrate_value: float) -> int:
        try:
            bitrate_kbps = int(bitrate_value)
        except (ValueError, TypeError):
            return 0
        return max(0, bitrate_kbps)
    
    def _get_working_path(self, final_path: Path) -> Path:
        counter = 0
        while True:
            candidate = final_path.with_name(f"{final_path.stem}_working_{counter}.mp4")
            if not candidate.exists():
                return candidate
            counter += 1
    
    def _export_audio_temp(self, audio_data: Dict[str, Any]) -> Optional[Path]:
        """将音频张量导出为临时 wav 文件"""
        waveform = audio_data.get("waveform")
        sample_rate = int(audio_data.get("sample_rate", 44100) or 44100)
        
        if waveform is None or not isinstance(waveform, torch.Tensor):
            return None
        if waveform.numel() == 0:
            return None
        
        # 统一为 2D (channels, samples)
        waveform = waveform.detach().cpu()
        if waveform.dim() == 3:
            waveform = waveform[0]
        elif waveform.dim() == 1:
            waveform = waveform.unsqueeze(0)
        elif waveform.dim() != 2:
            waveform = waveform.reshape(1, -1)
        
        # 尝试优先使用 torchaudio 保存
        try:
            import torchaudio
            fd, temp_path = tempfile.mkstemp(prefix="haigc_audio_", suffix=".wav")
            os.close(fd)
            temp_path = Path(temp_path)
            torchaudio.save(str(temp_path), waveform, sample_rate)
            return temp_path
        except ImportError:
            # 回退到标准库 wave 保存
            try:
                import wave
                import numpy as np
                
                # 限制到 [-1, 1] 并转换为 int16
                wav = waveform.float().numpy()
                wav = np.clip(wav, -1.0, 1.0)
                wav_int16 = (wav * 32767.0).astype(np.int16)
                
                # 交错通道数据（wave 需要 interleaved）
                channels, samples = wav_int16.shape
                interleaved = wav_int16.T.reshape(samples * channels)
                
                fd, temp_path = tempfile.mkstemp(prefix="haigc_audio_", suffix=".wav")
                os.close(fd)
                temp_path = Path(temp_path)
                
                with wave.open(str(temp_path), 'wb') as wf:
                    wf.setnchannels(channels)
                    wf.setsampwidth(2)  # int16
                    wf.setframerate(sample_rate)
                    wf.writeframes(interleaved.tobytes())
                
                return temp_path
            except Exception as e:
                print(f"[视频保存] 警告：wave 回退保存失败: {e}")
                return None
    
    def _build_video_args(
        self,
        format_config: Dict[str, Any],
        视频质量: str,
        bitrate_kbps: int
    ) -> List[str]:
        builder = format_config.get("video_args_builder")
        if callable(builder):
            return builder(视频质量)
        if builder == "vp9":
            preset = self.QUALITY_PRESETS.get(视频质量, self.QUALITY_PRESETS["中"])
            return [
                "-c:v", "libvpx-vp9",
                "-crf", preset["vp9"],
                "-b:v", "0"
            ]
        args = format_config.get("video_args")
        args = list(args) if args else ["-c:v", "copy"]
        
        if bitrate_kbps and bitrate_kbps > 0:
            codec = format_config.get("bitrate_codec")
            if codec:
                bitrate_str = f"{bitrate_kbps}k"
                args = [
                    "-c:v", codec,
                    "-b:v", bitrate_str,
                    "-maxrate", bitrate_str,
                    "-bufsize", f"{bitrate_kbps * 2}k"
                ]
            else:
                print("[视频保存] 提示：当前格式未定义自定义比特率编码器，已忽略自定义比特率。")
        return args
    
    def _build_audio_args(
        self,
        format_config: Dict[str, Any],
        audio_bitrate_kbps: int
    ) -> List[str]:
        if audio_bitrate_kbps and audio_bitrate_kbps > 0:
            codec = format_config.get("audio_codec")
            if codec:
                return ["-c:a", codec, "-b:a", f"{audio_bitrate_kbps}k"]
            else:
                print("[视频保存] 提示：当前格式未定义音频编码器，已忽略自定义音频比特率。")
        audio_args = format_config.get("audio_args")
        return list(audio_args) if audio_args else []
    
    def _transcode_video(
        self,
        source_path: Path,
        target_path: Path,
        format_config: Dict[str, Any],
        audio_path: Optional[Path],
        视频质量: str,
        fps: float,
        video_duration: Optional[float],
        bitrate_kbps: int,
        audio_bitrate_kbps: int
    ) -> bool:
        """使用 ffmpeg 进行最终格式转换并合并音频"""
        ffmpeg_path = shutil.which("ffmpeg")
        requires_ffmpeg = format_config.get("requires_ffmpeg", True)
        supports_audio = format_config.get("supports_audio", True)
        mode = format_config.get("mode")
        
        enforce_ffmpeg = requires_ffmpeg or (bitrate_kbps and bitrate_kbps > 0)
        if ffmpeg_path is None:
            if enforce_ffmpeg:
                raise RuntimeError("此输出格式需要安装 ffmpeg，请安装后重试。")
            if audio_path:
                print("[视频保存] 警告：未安装 ffmpeg，无法合并音频。")
            os.replace(source_path, target_path)
            return False
        
        if mode == "gif_palette":
            return self._create_palette_gif(
                ffmpeg_path=ffmpeg_path,
                source_path=source_path,
                target_path=target_path,
                palette_fps=format_config.get("palette_fps", 18),
                scale_expr=format_config.get("scale_expr", "scale=iw:-1:flags=lanczos"),
                dither_mode=format_config.get("dither", "bayer"),
                source_fps=fps
            )
        
        cmd = [ffmpeg_path, "-y", "-i", str(source_path)]
        if audio_path and supports_audio:
            cmd += ["-i", str(audio_path)]
        elif audio_path and not supports_audio:
            print("[视频保存] 提示：目标格式不支持音频，已忽略音频输入。")
        
        cmd += ["-map", "0:v:0"]
        if audio_path and supports_audio:
            cmd += ["-map", "1:a:0"]
        
        video_args = self._build_video_args(format_config, 视频质量, bitrate_kbps)
        if format_config.get("force_fps"):
            cmd += ["-r", str(fps)]
        cmd += video_args
        
        audio_attached = False
        audio_args = self._build_audio_args(format_config, audio_bitrate_kbps)
        if audio_path and supports_audio:
            if video_duration and video_duration > 0:
                duration_str = f"{video_duration:.6f}"
                cmd += ["-filter:a", f"atrim=0:{duration_str},asetpts=N/SR/TB"]
            if audio_args:
                cmd += audio_args
            audio_attached = True
        
        cmd.append(str(target_path))
        
        result = subprocess.run(cmd, capture_output=True)
        if result.returncode != 0:
            stderr = result.stderr.decode(errors="ignore")
            raise RuntimeError(f"ffmpeg 转码失败: {stderr or '未知错误'}")
        
        return audio_attached
    
    def _create_palette_gif(
        self,
        ffmpeg_path: str,
        source_path: Path,
        target_path: Path,
        palette_fps: Optional[int],
        scale_expr: str,
        dither_mode: str,
        source_fps: float
    ) -> bool:
        """使用 palettegen/paletteuse 流程生成高质量 GIF"""
        palette_path = source_path.with_name(f"{source_path.stem}_palette.png")
        try:
            fps_value = (
                palette_fps
                if palette_fps is not None and palette_fps > 0
                else max(1, int(round(source_fps)) or 1)
            )
            palette_cmd = [
                ffmpeg_path,
                "-y",
                "-i", str(source_path),
                "-vf", f"fps={fps_value},{scale_expr},palettegen",
                str(palette_path)
            ]
            result = subprocess.run(palette_cmd, capture_output=True)
            if result.returncode != 0:
                stderr = result.stderr.decode(errors="ignore")
                raise RuntimeError(f"GIF 调色板生成失败: {stderr or '未知错误'}")
            
            render_cmd = [
                ffmpeg_path,
                "-y",
                "-i", str(source_path),
                "-i", str(palette_path),
                "-lavfi", f"fps={fps_value},{scale_expr}[x];[x][1:v]paletteuse=dither={dither_mode}",
                "-loop", "0",
                str(target_path)
            ]
            result = subprocess.run(render_cmd, capture_output=True)
            if result.returncode != 0:
                stderr = result.stderr.decode(errors="ignore")
                raise RuntimeError(f"GIF 渲染失败: {stderr or '未知错误'}")
            
            return False  # GIF 无音频
        finally:
            if palette_path.exists():
                try:
                    palette_path.unlink()
                except OSError:
                    pass
    
    def _get_output_bitrates(self, video_path: Path) -> Dict[str, int]:
        """从输出文件获取比特率"""
        result = {"video": 0, "audio": 0}
        try:
            import subprocess
            import time
            
            # 确保文件存在且可读
            if not video_path.exists():
                return result
            
            # 等待文件完全写入（最多等待1秒）
            for _ in range(10):
                try:
                    if video_path.stat().st_size > 0:
                        break
                except OSError:
                    pass
                time.sleep(0.1)
            
            ffprobe_path = shutil.which("ffprobe")
            if ffprobe_path is None:
                return result
            
            # 获取视频比特率
            try:
                cmd = [
                    ffprobe_path,
                    "-v", "error",
                    "-select_streams", "v:0",
                    "-show_entries", "stream=bit_rate",
                    "-of", "default=noprint_wrappers=1:nokey=1",
                    str(video_path)
                ]
                proc = subprocess.run(cmd, capture_output=True, text=True, timeout=5)
                if proc.returncode == 0 and proc.stdout.strip():
                    bitrate_str = proc.stdout.strip()
                    if bitrate_str and bitrate_str != "N/A":
                        result["video"] = int(bitrate_str) // 1000
            except (ValueError, subprocess.TimeoutExpired, Exception) as e:
                pass
            
            # 获取音频比特率
            try:
                cmd = [
                    ffprobe_path,
                    "-v", "error",
                    "-select_streams", "a:0",
                    "-show_entries", "stream=bit_rate",
                    "-of", "default=noprint_wrappers=1:nokey=1",
                    str(video_path)
                ]
                proc = subprocess.run(cmd, capture_output=True, text=True, timeout=5)
                if proc.returncode == 0 and proc.stdout.strip():
                    bitrate_str = proc.stdout.strip()
                    if bitrate_str and bitrate_str != "N/A":
                        result["audio"] = int(bitrate_str) // 1000
            except (ValueError, subprocess.TimeoutExpired, Exception) as e:
                pass
        except Exception as e:
            # 静默失败，不影响预览显示
            pass
        return result
    
    def _build_video_preview(
        self,
        video_path: Path,
        output_root: Path,
        fps: float,
        frame_count: int,
        duration: float,
        has_audio: bool,
        format_label: str,
        file_size_mb: float,
        width: Optional[int],
        height: Optional[int],
        video_bitrate_kbps: int = 0,
        audio_bitrate_kbps: int = 0
    ) -> Dict[str, Any]:
        """构建前端UI所需的视频预览信息"""
        try:
            relative_path = video_path.resolve().relative_to(output_root)
            subfolder = str(relative_path.parent).replace("\\", "/")
            if subfolder == ".":
                subfolder = ""
        except ValueError:
            subfolder = ""
        
        video_info = {
            "filename": video_path.name,
            "subfolder": subfolder,
            "type": "output",
            "format": video_path.suffix.lstrip(".").lower() or "mp4",
            "fps": round(float(fps), 3),
            "frame_count": int(frame_count),
            "duration": round(float(duration), 3),
            "absolute_path": str(video_path),
            "has_audio": has_audio,
            "format_label": format_label,
            "file_size_mb": file_size_mb,
            "width": width,
            "height": height,
            "video_bitrate_kbps": video_bitrate_kbps,
            "audio_bitrate_kbps": audio_bitrate_kbps,
        }
        
        return {"videos": [video_info]}
