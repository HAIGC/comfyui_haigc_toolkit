"""
批量视频保存节点
一次性保存多个视频文件，适用于分镜转接等场景
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
    print(f"[批量视频保存] OpenCV 导入失败: {_cv2_import_error}")
    print("[批量视频保存] 可能的解决方案:")
    print("  1. 卸载所有 OpenCV 版本: pip uninstall opencv-python opencv-contrib-python opencv-python-headless -y")
    print("  2. 重新安装: pip install opencv-python")
    print("  3. 如果使用 conda: conda install -c conda-forge opencv")

class VideoBatchWriterNode:
    """批量视频保存节点 - 一次性保存多个视频"""
    
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
        "WEBM (VP9)": {
            "extension": ".webm",
            "supports_audio": True,
            "video_args_builder": "vp9",
            "audio_args": ["-c:a", "libopus", "-b:a", "128k"],
            "bitrate_codec": "libvpx-vp9",
            "audio_codec": "libopus",
        },
    }
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "视频1": ("IMAGE",),
                "视频帧率": ("FLOAT", {
                    "default": 30.0,
                    "min": 1.0,
                    "max": 120.0,
                    "step": 0.1
                }),
                "输出目录": ("STRING", {
                    "default": "output/scenes",
                    "multiline": False
                }),
                "文件名前缀": ("STRING", {
                    "default": "scene",
                    "multiline": False
                }),
                "视频编码": (["H264", "H265", "VP9", "XVID"], {
                    "default": "H264"
                }),
                "视频质量": (["高", "中", "低"], {
                    "default": "高"
                }),
                "输出格式": (list(cls.VIDEO_FORMATS.keys()), {
                    "default": "MP4 (H264)"
                }),
                "自动添加时间戳": (["是", "否"], {
                    "default": "是"
                }),
            },
            "optional": {
                "视频2": ("IMAGE",),
                "视频3": ("IMAGE",),
                "视频4": ("IMAGE",),
                "视频5": ("IMAGE",),
            }
        }
    
    RETURN_TYPES = ("STRING", "STRING", "INT", "STRING")
    RETURN_NAMES = ("保存路径", "文件列表", "成功数量", "报告")
    FUNCTION = "save_batch_videos"
    CATEGORY = "HAIGC工具集/视频剪辑"
    OUTPUT_NODE = True
    
    def save_batch_videos(
        self,
        视频1: torch.Tensor,
        视频帧率: float,
        输出目录: str,
        文件名前缀: str,
        视频编码: str,
        视频质量: str,
        输出格式: str,
        自动添加时间戳: str,
        视频2: Optional[torch.Tensor] = None,
        视频3: Optional[torch.Tensor] = None,
        视频4: Optional[torch.Tensor] = None,
        视频5: Optional[torch.Tensor] = None
    ) -> Tuple[str, str, int, str]:
        """
        批量保存多个视频
        
        Args:
            视频1-5: 要保存的视频张量
            视频帧率: 视频帧率
            输出目录: 保存目录
            文件名前缀: 文件名前缀
            其他参数: 视频编码和质量设置
            
        Returns:
            保存路径、文件列表、成功数量、报告
        """
        # 检查 OpenCV 是否成功导入
        if _cv2 is None:
            error_msg = f"错误：OpenCV 导入失败\n{_cv2_import_error or '未知错误'}\n\n解决方案:\n1. 卸载所有 OpenCV 版本: pip uninstall opencv-python opencv-contrib-python opencv-python-headless -y\n2. 重新安装: pip install opencv-python\n3. 重启 ComfyUI"
            print(f"[批量视频保存] {error_msg}")
            return ("", "", 0, error_msg)
        
        # 使用模块级别导入的 cv2
        cv2 = _cv2
        
        # 收集所有非空视频
        videos = []
        video_names = []
        
        if 视频1 is not None and 视频1.shape[0] > 0:
            videos.append(("视频1", 视频1))
        if 视频2 is not None and 视频2.shape[0] > 0:
            videos.append(("视频2", 视频2))
        if 视频3 is not None and 视频3.shape[0] > 0:
            videos.append(("视频3", 视频3))
        if 视频4 is not None and 视频4.shape[0] > 0:
            videos.append(("视频4", 视频4))
        if 视频5 is not None and 视频5.shape[0] > 0:
            videos.append(("视频5", 视频5))
        
        if len(videos) == 0:
            error_msg = "[批量视频保存] 错误: 没有有效的视频输入"
            print(error_msg)
            return ("", "", 0, error_msg)
        
        print(f"[批量视频保存] 开始保存 {len(videos)} 个视频...")
        
        # 获取输出目录
        output_dir = Path(输出目录)
        if not output_dir.is_absolute():
            # 相对路径，使用ComfyUI的输出目录
            output_dir = Path(folder_paths.get_output_directory()) / output_dir
        
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # 获取格式配置
        format_config = self.VIDEO_FORMATS.get(输出格式, self.VIDEO_FORMATS["MP4 (H264)"])
        extension = format_config["extension"]
        
        # 时间戳
        timestamp = ""
        if 自动添加时间戳 == "是":
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        saved_files = []
        success_count = 0
        error_messages = []
        
        # 保存每个视频
        for idx, (video_name, images) in enumerate(videos, 1):
            try:
                batch_size, height, width, channels = images.shape
                
                # 生成文件名
                if timestamp:
                    filename = f"{文件名前缀}_{idx}_{timestamp}{extension}"
                else:
                    filename = f"{文件名前缀}_{idx}{extension}"
                
                video_path = output_dir / filename
                
                # 检查是否为空视频占位符（单帧黑色图像，通常是64x64）
                # 更智能的检测：检查是否为全黑图像
                is_empty = False
                if batch_size == 1:
                    # 检查是否为全黑或接近全黑
                    frame = images[0].cpu().numpy()
                    if np.allclose(frame, 0.0, atol=0.01):
                        is_empty = True
                
                if is_empty:
                    print(f"[批量视频保存] 跳过 {video_name}: 检测到空视频占位符")
                    continue
                
                print(f"[批量视频保存] 正在保存 {video_name} -> {filename}")
                print(f"  尺寸: {width}x{height}, 帧数: {batch_size}, 帧率: {视频帧率}")
                
                # 使用OpenCV保存视频
                fourcc = cv2.VideoWriter_fourcc(*'mp4v')
                working_video_path = str(video_path).replace(extension, '_temp' + extension)
                
                out = cv2.VideoWriter(
                    working_video_path,
                    fourcc,
                    视频帧率,
                    (width, height)
                )
                
                if not out.isOpened():
                    raise Exception(f"无法创建视频文件: {working_video_path}")
                
                # 写入每一帧
                for i in range(batch_size):
                    frame = images[i].cpu().numpy()
                    frame = (frame * 255).astype(np.uint8)
                    frame_bgr = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
                    out.write(frame_bgr)
                
                out.release()
                
                # 转码到最终格式（如果需要）
                if working_video_path != str(video_path):
                    self._transcode_video_simple(
                        source_path=working_video_path,
                        target_path=str(video_path),
                        format_config=format_config,
                        fps=视频帧率,
                        视频质量=视频质量
                    )
                    # 删除临时文件
                    if os.path.exists(working_video_path):
                        os.remove(working_video_path)
                
                # 获取文件信息
                file_size = os.path.getsize(video_path) / (1024 * 1024)  # MB
                duration = batch_size / 视频帧率
                
                saved_files.append(str(video_path))
                success_count += 1
                
                print(f"[批量视频保存] ✅ {video_name} 保存成功!")
                print(f"  文件: {filename}")
                print(f"  大小: {file_size:.2f} MB")
                print(f"  时长: {duration:.2f} 秒")
                
            except Exception as e:
                error_msg = f"{video_name} 保存失败: {str(e)}"
                error_messages.append(error_msg)
                print(f"[批量视频保存] ❌ {error_msg}")
                import traceback
                traceback.print_exc()
        
        # 生成报告
        report_lines = [
            f"批量保存完成: {success_count}/{len(videos)} 个视频",
            f"输出目录: {output_dir}",
            ""
        ]
        
        if saved_files:
            report_lines.append("成功保存的文件:")
            for i, file_path in enumerate(saved_files, 1):
                report_lines.append(f"  {i}. {Path(file_path).name}")
        
        if error_messages:
            report_lines.append("")
            report_lines.append("错误信息:")
            for msg in error_messages:
                report_lines.append(f"  - {msg}")
        
        report = "\n".join(report_lines)
        file_list = "\n".join(saved_files) if saved_files else ""
        
        print(f"[批量视频保存] 全部完成! 成功: {success_count}/{len(videos)}")
        print(report)
        
        return (str(output_dir), file_list, success_count, report)
    
    def _transcode_video_simple(
        self,
        source_path: str,
        target_path: str,
        format_config: Dict[str, Any],
        fps: float,
        视频质量: str
    ):
        """简单的视频转码"""
        try:
            # 检查是否有ffmpeg
            try:
                subprocess.run(
                    ["ffmpeg", "-version"],
                    capture_output=True,
                    check=True
                )
                has_ffmpeg = True
            except:
                has_ffmpeg = False
            
            if not has_ffmpeg:
                # 没有ffmpeg，直接复制文件
                shutil.copy2(source_path, target_path)
                return
            
            # 构建ffmpeg命令
            quality_preset = self.QUALITY_PRESETS.get(视频质量, self.QUALITY_PRESETS["中"])
            
            cmd = [
                "ffmpeg", "-y",
                "-i", source_path,
                "-c:v", format_config.get("bitrate_codec", "libx264"),
                "-crf", quality_preset.get("crf", "23"),
                "-preset", "medium",
                "-r", str(fps),
                target_path
            ]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True
            )
            
            if result.returncode != 0:
                print(f"[批量视频保存] 转码警告: {result.stderr}")
                # 转码失败，直接复制
                shutil.copy2(source_path, target_path)
            
        except Exception as e:
            print(f"[批量视频保存] 转码错误: {str(e)}")
            # 转码失败，直接复制
            if os.path.exists(source_path):
                shutil.copy2(source_path, target_path)

NODE_CLASS_MAPPINGS = {
    "VideoBatchWriterNode": VideoBatchWriterNode
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "VideoBatchWriterNode": "批量视频保存 💾"
}

