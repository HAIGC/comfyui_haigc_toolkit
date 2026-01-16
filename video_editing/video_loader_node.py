"""
视频加载器节点
从文件加载视频为图像序列和音频
支持上传视频或从路径加载
"""

import torch
import os
import sys
import numpy as np

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
    print(f"[视频加载] OpenCV 导入失败: {_cv2_import_error}")
    print("[视频加载] 可能的解决方案:")
    print("  1. 卸载所有 OpenCV 版本: pip uninstall opencv-python opencv-contrib-python opencv-python-headless -y")
    print("  2. 重新安装: pip install opencv-python")
    print("  3. 如果使用 conda: conda install -c conda-forge opencv")

class VideoLoaderNode:
    """视频加载器节点"""
    
    @classmethod
    def INPUT_TYPES(cls):
        # 获取input目录下的视频文件
        input_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), "input")
        if not os.path.exists(input_dir):
            os.makedirs(input_dir)
        
        video_extensions = ['.mp4', '.avi', '.mov', '.mkv', '.flv', '.wmv', '.webm', '.m4v']
        video_files = []
        
        if os.path.exists(input_dir):
            for file in os.listdir(input_dir):
                if os.path.splitext(file)[1].lower() in video_extensions:
                    video_files.append(file)
        
        if not video_files:
            video_files = [""]
        
        return {
            "required": {
                "视频文件": (sorted(video_files), {
                    "video_upload": True
                }),
                "起始帧": ("INT", {
                    "default": 0,
                    "min": 0,
                    "max": 100000,
                    "step": 1
                }),
                "结束帧": ("INT", {
                    "default": 0,
                    "min": 0,
                    "max": 100000,
                    "step": 1,
                    "display": "number"
                }),
                "帧率": ("FLOAT", {
                    "default": 0.0,
                    "min": 0.0,
                    "max": 120.0,
                    "step": 0.1,
                    "tooltip": "设置为0时自动使用视频原始帧率"
                }),
                "跳帧": ("INT", {
                    "default": 1,
                    "min": 1,
                    "max": 10,
                    "step": 1
                }),
            },
            "optional": {
                "视频路径": ("STRING", {
                    "default": "",
                    "multiline": False
                }),
                "目标宽度": ("INT", {
                    "default": 0,
                    "min": 0,
                    "max": 4096,
                    "step": 1,
                    "tooltip": "0 表示保持原始宽度"
                }),
                "目标高度": ("INT", {
                    "default": 0,
                    "min": 0,
                    "max": 4096,
                    "step": 1,
                    "tooltip": "0 表示保持原始高度"
                }),
            },
        }
    
    RETURN_TYPES = ("IMAGE", "AUDIO", "HAIGC_VIDEOINFO")
    RETURN_NAMES = ("视频", "音频", "video_info")
    FUNCTION = "load_video"
    CATEGORY = "HAIGC工具集/视频剪辑"
    
    @classmethod
    def IS_CHANGED(cls, 视频文件, 视频路径=None, **kwargs):
        # 当视频文件改变时重新加载
        # 优先使用视频路径
        if 视频路径 and 视频路径.strip():
            if os.path.isfile(视频路径):
                return os.path.getmtime(视频路径)
        else:
            input_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), "input")
            video_path = os.path.join(input_dir, 视频文件)
            if os.path.isfile(video_path):
                return os.path.getmtime(video_path)
        return float("nan")
    
    @classmethod
    def VALIDATE_INPUTS(cls, 视频文件, 视频路径=None, **kwargs):
        # 路径是有效文件则通过；否则忽略视频路径，使用“视频文件”进行校验
        if 视频路径 and 视频路径.strip() and os.path.isfile(视频路径.strip()):
            return True
        if not 视频文件:
            return "请选择或上传视频文件，或输入视频路径"
        input_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), "input")
        video_path = os.path.join(input_dir, 视频文件)
        if not os.path.isfile(video_path):
            return f"视频文件不存在: {视频文件}"
        return True
    
    def load_video(
        self,
        视频文件,
        起始帧,
        结束帧,
        帧率,
        跳帧,
        视频路径=None,
        目标宽度: int = 0,
        目标高度: int = 0
    ):
        """加载视频文件"""
        
        # 确定最终使用的视频路径
        if 视频路径 and 视频路径.strip():
            # 优先使用自定义路径
            final_path = 视频路径.strip() if os.path.isfile(视频路径.strip()) else None
        else:
            # 使用input目录中的文件
            input_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), "input")
            final_path = os.path.join(input_dir, 视频文件)
        
        if final_path is None:
            # 回退到input目录中选择的文件
            input_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), "input")
            final_path = os.path.join(input_dir, 视频文件)
        
        if not os.path.exists(final_path):
            print(f"[视频加载器] 错误：视频文件不存在: {final_path}")
            # 返回一个黑色帧作为占位
            dummy = torch.zeros((1, 480, 640, 3))
            # 返回空音频（不自动添加静音）
            dummy_audio = {"waveform": torch.zeros((1, 2, 0)), "sample_rate": 44100}
            dummy_info = {
                "width": 640,
                "height": 480,
                "fps": 30.0,
                "frame_count": 1,
                "duration": 1 / 30.0,
                "filename": os.path.basename(final_path),
                "source_path": final_path,
                "has_audio": False,
                "file_size_mb": 0.0,
                "video_bitrate_kbps": 0,
                "audio_bitrate_kbps": 0,
                "error": "视频文件不存在"
            }
            # 构建基本UI信息用于前端显示
            try:
                ui_info = self._build_video_preview(
                    video_path=final_path,
                    fps=dummy_info["fps"],
                    frame_count=dummy_info["frame_count"],
                    duration=dummy_info["duration"],
                    has_audio=dummy_info["has_audio"],
                    file_size_mb=dummy_info["file_size_mb"],
                    width=dummy_info["width"],
                    height=dummy_info["height"],
                    video_bitrate_kbps=0,
                    audio_bitrate_kbps=0
                )
            except Exception:
                ui_info = {"videos": []}
            return {
                "ui": ui_info,
                "result": (dummy, dummy_audio, dummy_info)
            }
        
        try:
            # 检查 OpenCV 是否成功导入
            if _cv2 is None:
                error_msg = f"错误：OpenCV 导入失败\n{_cv2_import_error or '未知错误'}\n\n解决方案:\n1. 卸载所有 OpenCV 版本: pip uninstall opencv-python opencv-contrib-python opencv-python-headless -y\n2. 重新安装: pip install opencv-python\n3. 重启 ComfyUI"
                print(f"[视频加载] {error_msg}")
                dummy = torch.zeros((1, 480, 640, 3))
                dummy_audio = {"waveform": torch.zeros((1, 2, 0)), "sample_rate": 44100}
                dummy_info = {
                    "width": 640,
                    "height": 480,
                    "fps": 30.0,
                    "frame_count": 1,
                    "duration": 1 / 30.0,
                    "filename": os.path.basename(final_path),
                    "source_path": final_path,
                    "has_audio": False,
                    "file_size_mb": 0.0,
                    "video_bitrate_kbps": 0,
                    "audio_bitrate_kbps": 0,
                    "error": error_msg
                }
                try:
                    ui_info = self._build_video_preview(
                        video_path=final_path,
                        fps=dummy_info["fps"],
                        frame_count=dummy_info["frame_count"],
                        duration=dummy_info["duration"],
                        has_audio=dummy_info["has_audio"],
                        file_size_mb=dummy_info["file_size_mb"],
                        width=dummy_info["width"],
                        height=dummy_info["height"],
                        video_bitrate_kbps=0,
                        audio_bitrate_kbps=0
                    )
                except Exception:
                    ui_info = {"videos": []}
                return {
                    "ui": ui_info,
                    "result": (dummy, dummy_audio, dummy_info)
                }
            
            # 使用模块级别导入的 cv2
            cv2 = _cv2
            
            cap = cv2.VideoCapture(final_path)
            
            if not cap.isOpened():
                raise Exception("无法打开视频文件")
            
            # 获取视频信息
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            original_fps = cap.get(cv2.CAP_PROP_FPS)
            target_width, target_height = self._determine_target_size(
                width, height, 目标宽度, 目标高度
            )
            
            # 如果帧率参数为0，使用视频原始帧率
            if 帧率 <= 0:
                fps = original_fps if original_fps > 0 else 30.0
            else:
                fps = 帧率
            
            # 确定读取范围
            start = 起始帧
            end = 结束帧 if 结束帧 > 0 else total_frames
            end = min(end, total_frames)
            
            print(f"[视频加载器] 文件: {os.path.basename(final_path)}")
            print(f"  总帧数: {total_frames}, FPS: {fps:.2f}, 分辨率: {width}x{height}")
            if (target_width, target_height) != (width, height):
                print(f"  调整分辨率 -> {target_width}x{target_height}")
            print(f"  加载范围: 第{start}-{end}帧, 跳帧:{跳帧}")
            
            # 读取帧
            frames = []
            cap.set(cv2.CAP_PROP_POS_FRAMES, start)
            
            for i in range(start, end, 跳帧):
                ret, frame = cap.read()
                if not ret:
                    break
                
                # OpenCV读取的是BGR，转换为RGB
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                if (target_width, target_height) != (width, height):
                    frame_rgb = cv2.resize(
                        frame_rgb,
                        (target_width, target_height),
                        interpolation=cv2.INTER_AREA if target_width < width else cv2.INTER_LINEAR
                    )
                # 转换为[0, 1]范围的float
                frame_normalized = frame_rgb.astype(np.float32) / 255.0
                frames.append(frame_normalized)
                
                # 跳过额外的帧
                if 跳帧 > 1:
                    for _ in range(跳帧 - 1):
                        cap.read()
            
            cap.release()
            
            if len(frames) == 0:
                print(f"[视频加载器] 警告：未读取到任何帧")
                dummy = torch.zeros((1, height, width, 3))
                dummy_audio = {"waveform": torch.zeros((1, 2, 0)), "sample_rate": 44100}
                dummy_info = {
                    "width": width,
                    "height": height,
                    "fps": fps,
                    "frame_count": 0,
                    "duration": 0.0,
                    "filename": os.path.basename(final_path),
                    "source_path": final_path,
                    "has_audio": False,
                    "file_size_mb": os.path.getsize(final_path) / (1024 * 1024) if os.path.exists(final_path) else 0.0,
                    "video_bitrate_kbps": 0,
                    "audio_bitrate_kbps": 0,
                    "error": "未读取到任何帧"
                }
                try:
                    ui_info = self._build_video_preview(
                        video_path=final_path,
                        fps=fps,
                        frame_count=0,
                        duration=0.0,
                        has_audio=False,
                        file_size_mb=dummy_info["file_size_mb"],
                        width=width,
                        height=height,
                        video_bitrate_kbps=0,
                        audio_bitrate_kbps=0
                    )
                except Exception:
                    ui_info = {"videos": []}
                return {
                    "ui": ui_info,
                    "result": (dummy, dummy_audio, dummy_info)
                }
            
            # 转换为tensor
            images = torch.from_numpy(np.stack(frames, axis=0))
            
            output_frames = images.shape[0]
            output_duration = output_frames / fps
            
            print(f"[视频加载器] 成功加载 {output_frames} 帧, 时长: {output_duration:.2f}秒")
            
            # 提取音频
            audio_data = self._extract_audio(final_path, start, end, fps)
            
            # 获取文件大小
            file_size_mb = os.path.getsize(final_path) / (1024 * 1024)  # MB
            
            # 检查是否有音频（检查原始视频文件）
            has_audio = self._check_audio_track(final_path)
            
            # 计算原始视频时长
            original_duration = total_frames / (original_fps if original_fps and original_fps > 0 else fps)
            
            # 获取视频比特率（失败不影响预览显示）
            video_bitrate_kbps = 0
            audio_bitrate_kbps = 0
            try:
                video_bitrate_kbps = self._get_video_bitrate(final_path)
                if has_audio:
                    audio_bitrate_kbps = self._get_audio_bitrate(final_path)
            except Exception as e:
                print(f"[视频加载器] 警告：无法获取比特率信息: {str(e)}")
            
            # 构建UI预览信息（使用原始视频信息，而不是处理后的）
            try:
                ui_info = self._build_video_preview(
                    video_path=final_path,
                    fps=original_fps,
                    frame_count=total_frames,
                    duration=original_duration,
                    has_audio=has_audio,
                    file_size_mb=round(file_size_mb, 2),
                    width=width,  # 原始宽度
                    height=height,  # 原始高度
                    video_bitrate_kbps=video_bitrate_kbps,
                    audio_bitrate_kbps=audio_bitrate_kbps
                )
            except Exception as e:
                print(f"[视频加载器] 错误：构建预览信息失败: {str(e)}")
                import traceback
                traceback.print_exc()
                # 返回基本预览信息
                ui_info = self._build_video_preview(
                    video_path=final_path,
                    fps=original_fps,
                    frame_count=total_frames,
                    duration=original_duration,
                    has_audio=has_audio,
                    file_size_mb=round(file_size_mb, 2),
                    width=width,
                    height=height,
                    video_bitrate_kbps=0,
                    audio_bitrate_kbps=0
                )
            
            return {
                "ui": ui_info,
                "result": (images, audio_data, {
                    "width": target_width,
                    "height": target_height,
                    "fps": fps,
                    "frame_count": output_frames,
                    "duration": output_duration,
                    "total_frames": total_frames,
                    "filename": os.path.basename(final_path),
                    "source_path": final_path,
                    "has_audio": bool(has_audio),
                    "file_size_mb": round(file_size_mb, 2),
                    "video_bitrate_kbps": int(video_bitrate_kbps) if video_bitrate_kbps else 0,
                    "audio_bitrate_kbps": int(audio_bitrate_kbps) if audio_bitrate_kbps else 0,
                })
            }
            
        except ImportError:
            print("[视频加载器] 错误：需要安装opencv-python")
            print("  请运行: pip install opencv-python")
            dummy = torch.zeros((1, 480, 640, 3))
            dummy_audio = {"waveform": torch.zeros((1, 2, 0)), "sample_rate": 44100}
            dummy_info = {
                "width": 640,
                "height": 480,
                "fps": 30.0,
                "frame_count": 0,
                "duration": 0.0,
                "filename": os.path.basename(final_path),
                "source_path": final_path,
                "has_audio": False,
                "file_size_mb": 0.0,
                "video_bitrate_kbps": 0,
                "audio_bitrate_kbps": 0,
                "error": "需要安装opencv-python"
            }
            try:
                ui_info = self._build_video_preview(
                    video_path=final_path,
                    fps=dummy_info["fps"],
                    frame_count=dummy_info["frame_count"],
                    duration=dummy_info["duration"],
                    has_audio=dummy_info["has_audio"],
                    file_size_mb=dummy_info["file_size_mb"],
                    width=dummy_info["width"],
                    height=dummy_info["height"],
                    video_bitrate_kbps=0,
                    audio_bitrate_kbps=0
                )
            except Exception:
                ui_info = {"videos": []}
            return {
                "ui": ui_info,
                "result": (dummy, dummy_audio, dummy_info)
            }
            
        except Exception as e:
            print(f"[视频加载器] 错误：{str(e)}")
            dummy = torch.zeros((1, 480, 640, 3))
            dummy_audio = {"waveform": torch.zeros((1, 2, 0)), "sample_rate": 44100}
            dummy_info = {
                "width": 640,
                "height": 480,
                "fps": 30.0,
                "frame_count": 0,
                "duration": 0.0,
                "filename": os.path.basename(final_path),
                "source_path": final_path,
                "has_audio": False,
                "file_size_mb": 0.0,
                "video_bitrate_kbps": 0,
                "audio_bitrate_kbps": 0,
                "error": str(e)
            }
            try:
                ui_info = self._build_video_preview(
                    video_path=final_path,
                    fps=dummy_info["fps"],
                    frame_count=dummy_info["frame_count"],
                    duration=dummy_info["duration"],
                    has_audio=dummy_info["has_audio"],
                    file_size_mb=dummy_info["file_size_mb"],
                    width=dummy_info["width"],
                    height=dummy_info["height"],
                    video_bitrate_kbps=0,
                    audio_bitrate_kbps=0
                )
            except Exception:
                ui_info = {"videos": []}
            return {
                "ui": ui_info,
                "result": (dummy, dummy_audio, dummy_info)
            }
    
    def _determine_target_size(
        self,
        original_width: int,
        original_height: int,
        target_width: int,
        target_height: int
    ):
        """根据用户输入计算目标尺寸，保持宽高比"""
        new_width = original_width
        new_height = original_height
        
        width_specified = target_width and target_width > 0
        height_specified = target_height and target_height > 0
        
        if width_specified and height_specified:
            new_width = target_width
            new_height = target_height
        elif width_specified:
            scale = target_width / original_width
            new_width = target_width
            new_height = max(1, int(round(original_height * scale)))
        elif height_specified:
            scale = target_height / original_height
            new_height = target_height
            new_width = max(1, int(round(original_width * scale)))
        
        new_width = int(max(1, new_width))
        new_height = int(max(1, new_height))
        return new_width, new_height
    
    def _get_video_bitrate(self, video_path: str) -> int:
        """获取视频比特率（Kbps）"""
        try:
            import subprocess
            import shutil
            ffprobe_path = shutil.which("ffprobe")
            if ffprobe_path is None:
                return 0
            
            cmd = [
                ffprobe_path,
                "-v", "error",
                "-select_streams", "v:0",
                "-show_entries", "stream=bit_rate",
                "-of", "default=noprint_wrappers=1:nokey=1",
                video_path
            ]
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode == 0 and result.stdout.strip():
                bitrate_bps = int(result.stdout.strip())
                return bitrate_bps // 1000  # 转换为 Kbps
        except Exception:
            pass
        return 0
    
    def _get_audio_bitrate(self, video_path: str) -> int:
        """获取音频比特率（Kbps）"""
        try:
            import subprocess
            import shutil
            ffprobe_path = shutil.which("ffprobe")
            if ffprobe_path is None:
                return 0
            
            cmd = [
                ffprobe_path,
                "-v", "error",
                "-select_streams", "a:0",
                "-show_entries", "stream=bit_rate",
                "-of", "default=noprint_wrappers=1:nokey=1",
                video_path
            ]
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode == 0 and result.stdout.strip():
                bitrate_bps = int(result.stdout.strip())
                return bitrate_bps // 1000  # 转换为 Kbps
        except Exception:
            pass
        return 0
    
    def _check_audio_track(self, video_path: str) -> bool:
        """检查视频文件是否包含音频轨道"""
        try:
            import subprocess
            import shutil
            ffprobe_path = shutil.which("ffprobe")
            if ffprobe_path is None:
                # 如果没有 ffprobe，返回 False（更保守）
                print(f"[视频加载器] 警告：未找到 ffprobe，无法准确检测音频轨道")
                return False
            
            # 使用 ffprobe 检查音频流
            cmd = [
                ffprobe_path,
                "-v", "error",
                "-select_streams", "a:0",
                "-show_entries", "stream=codec_type",
                "-of", "default=noprint_wrappers=1:nokey=1",
                str(video_path)
            ]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=5)
            
            # 如果返回 "audio" 说明有音频轨道
            if result.returncode == 0 and result.stdout.strip() == "audio":
                return True
            
            # 如果命令失败或返回空，说明没有音频轨道
            return False
        except subprocess.TimeoutExpired:
            print(f"[视频加载器] 警告：音频检测超时")
            return False
        except Exception as e:
            print(f"[视频加载器] 警告：音频检测失败: {str(e)}")
            return False  # 默认假设无音频，更保守
    
    def _build_video_preview(
        self,
        video_path: str,
        fps: float,
        frame_count: int,
        duration: float,
        has_audio: bool,
        file_size_mb: float,
        width: int,
        height: int,
        video_bitrate_kbps: int = 0,
        audio_bitrate_kbps: int = 0
    ):
        """构建前端UI所需的视频预览信息"""
        from pathlib import Path
        import folder_paths
        
        video_path_obj = Path(video_path)
        input_dir = Path(folder_paths.get_input_directory())
        
        try:
            relative_path = video_path_obj.resolve().relative_to(input_dir)
            subfolder = str(relative_path.parent).replace("\\", "/")
            if subfolder == ".":
                subfolder = ""
        except ValueError:
            subfolder = ""
        
        video_info = {
            "filename": video_path_obj.name,
            "subfolder": subfolder,
            "type": "input",
            "format": video_path_obj.suffix.lstrip(".").lower() or "mp4",
            "fps": round(float(fps), 3),
            "frame_count": int(frame_count),
            "duration": round(float(duration), 3),
            "absolute_path": str(video_path_obj),
            "has_audio": has_audio,
            "file_size_mb": file_size_mb,
            "width": width,
            "height": height,
            "video_bitrate_kbps": int(video_bitrate_kbps) if video_bitrate_kbps else 0,
            "audio_bitrate_kbps": int(audio_bitrate_kbps) if audio_bitrate_kbps else 0,
        }
        
        print(f"[视频加载器] UI预览信息: {video_info}")
        return {"videos": [video_info]}
    
    def _extract_audio(self, video_path, start_frame, end_frame, fps):
        """从视频中提取音频"""
        try:
            import subprocess
            import shutil
            import tempfile
            
            # 计算时间范围
            start_time = start_frame / max(fps, 1e-6)
            duration = (end_frame - start_frame) / max(fps, 1e-6)
            if duration <= 0:
                duration = 1.0 / max(fps, 1.0)  # 至少一帧时长
            
            # 如果视频不包含音频轨道，直接返回空音频
            try:
                if not self._check_audio_track(video_path):
                    print(f"[视频加载器] 提示：源视频无音轨，跳过音频提取")
                    return {"waveform": torch.zeros((1, 2, 0)), "sample_rate": 44100}
            except Exception:
                # 检测失败不影响后续流程
                pass
            
            ffmpeg_path = shutil.which("ffmpeg")
            if ffmpeg_path is None:
                print("[视频加载器] 警告：未安装 ffmpeg，无法提取音频")
                return {"waveform": torch.zeros((1, 2, 0)), "sample_rate": 44100}
            
            # 创建临时文件保存音频
            temp_audio = tempfile.NamedTemporaryFile(suffix='.wav', delete=False)
            temp_audio_path = temp_audio.name
            temp_audio.close()
            
            # 使用ffmpeg提取音频
            cmd = [
                ffmpeg_path,
                '-i', video_path,
                '-ss', str(start_time),
                '-t', str(duration),
                '-vn',  # 不要视频
                '-acodec', 'pcm_s16le',  # PCM 16位
                '-ar', '44100',  # 采样率
                '-ac', '2',  # 双声道
                '-y',  # 覆盖输出文件
                temp_audio_path
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0 and os.path.exists(temp_audio_path):
                # 读取音频文件（优先使用 torchaudio，缺失时回退到 wave）
                try:
                    import torchaudio
                    waveform, sample_rate = torchaudio.load(temp_audio_path)
                except ImportError:
                    import wave
                    with wave.open(temp_audio_path, 'rb') as wf:
                        sample_rate = wf.getframerate()
                        channels = wf.getnchannels()
                        sampwidth = wf.getsampwidth()
                        frames = wf.getnframes()
                        audio_bytes = wf.readframes(frames)
                    import numpy as np
                    dtype = np.int16 if sampwidth == 2 else np.int8
                    audio_np = np.frombuffer(audio_bytes, dtype=dtype)
                    if channels > 1:
                        audio_np = audio_np.reshape(-1, channels).T
                    else:
                        audio_np = audio_np.reshape(1, -1)
                    audio_np = (audio_np.astype(np.float32) / 32768.0)
                    import torch as _torch
                    waveform = _torch.from_numpy(audio_np).unsqueeze(0)
                finally:
                    try:
                        os.unlink(temp_audio_path)
                    except:
                        pass
                
                # 统一为 (1, 2, samples)
                if waveform.dim() == 2:
                    waveform = waveform.unsqueeze(0)
                elif waveform.dim() == 1:
                    waveform = waveform.view(1, 1, -1)
                if waveform.shape[1] == 1:
                    waveform = waveform.repeat(1, 2, 1)
                
                # 如果提取到的音频为空，尝试全音轨提取后再切片
                if waveform.shape[-1] == 0:
                    try:
                        # 提取整段音频
                        fallback_audio = tempfile.NamedTemporaryFile(suffix='.wav', delete=False)
                        fallback_audio_path = fallback_audio.name
                        fallback_audio.close()
                        
                        full_cmd = [
                            ffmpeg_path,
                            '-i', video_path,
                            '-vn',
                            '-acodec', 'pcm_s16le',
                            '-ar', '44100',
                            '-ac', '2',
                            '-y',
                            fallback_audio_path
                        ]
                        full_res = subprocess.run(full_cmd, capture_output=True, text=True)
                        if full_res.returncode == 0 and os.path.exists(fallback_audio_path):
                            try:
                                # 读取整段音频
                                try:
                                    import torchaudio as _ta
                                    full_wav, full_sr = _ta.load(fallback_audio_path)
                                except ImportError:
                                    import wave
                                    with wave.open(fallback_audio_path, 'rb') as wf:
                                        full_sr = wf.getframerate()
                                        channels = wf.getnchannels()
                                        sampwidth = wf.getsampwidth()
                                        frames = wf.getnframes()
                                        audio_bytes = wf.readframes(frames)
                                    import numpy as _np
                                    dtype = np.int16 if sampwidth == 2 else np.int8
                                    audio_np = _np.frombuffer(audio_bytes, dtype=dtype)
                                    if channels > 1:
                                        audio_np = audio_np.reshape(-1, channels).T
                                    else:
                                        audio_np = audio_np.reshape(1, -1)
                                    audio_np = (audio_np.astype(np.float32) / 32768.0)
                                    import torch as _torch2
                                    full_wav = _torch2.from_numpy(audio_np).unsqueeze(0)
                            finally:
                                try:
                                    os.unlink(fallback_audio_path)
                                except:
                                    pass
                            
                            # 统一形状
                            if full_wav.dim() == 2:
                                full_wav = full_wav.unsqueeze(0)
                            elif full_wav.dim() == 1:
                                full_wav = full_wav.view(1, 1, -1)
                            if full_wav.shape[1] == 1:
                                full_wav = full_wav.repeat(1, 2, 1)
                            
                            # 根据时间范围切片整段音频
                            sr = int(full_sr or 44100)
                            total_samples = full_wav.shape[-1]
                            start_sample = int(round(start_time * sr))
                            end_sample = int(round((start_time + duration) * sr))
                            start_sample = min(max(start_sample, 0), total_samples)
                            end_sample = min(max(end_sample, start_sample + 1), total_samples)
                            sliced = full_wav[..., start_sample:end_sample].clone()
                            
                            if sliced.shape[-1] > 0:
                                return {"waveform": sliced, "sample_rate": sr}
                    except Exception as _fallback_err:
                        print(f"[视频加载器] 警告：音频全轨回退失败: {_fallback_err}")
                    
                    # 仍为空则返回空音频
                    return {"waveform": torch.zeros((1, 2, 0)), "sample_rate": int(sample_rate or 44100)}
                
                audio_data = {"waveform": waveform, "sample_rate": int(sample_rate or 44100)}
                print(f"[视频加载器] 成功提取音频: {waveform.shape}, 采样率: {sample_rate}")
                return audio_data
            else:
                print(f"[视频加载器] 警告：无法提取音频，视频可能不包含音轨")
                return {"waveform": torch.zeros((1, 2, 0)), "sample_rate": 44100}
                
        except ImportError as e:
            print(f"[视频加载器] 警告：缺少音频处理库，跳过音频提取")
            print(f"  请安装: pip install torchaudio")
            return {"waveform": torch.zeros((1, 2, 0)), "sample_rate": 44100}
        except Exception as e:
            print(f"[视频加载器] 警告：音频提取失败: {str(e)}")
            return {"waveform": torch.zeros((1, 2, 0)), "sample_rate": 44100}
