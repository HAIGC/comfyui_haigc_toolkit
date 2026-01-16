"""
视频信息预览节点
显示视频的详细信息（分辨率、帧率、时长、比特率等）
"""

import os
import folder_paths
from pathlib import Path
import shutil
import subprocess

class VideoInfoPreviewNode:
    """视频信息预览节点"""
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "video_info": ("HAIGC_VIDEOINFO",),
            },
        }
    
    RETURN_TYPES = ("HAIGC_VIDEOINFO",)
    RETURN_NAMES = ("video_info",)
    FUNCTION = "preview_info"
    CATEGORY = "HAIGC工具集/视频剪辑"
    OUTPUT_NODE = True
    
    def preview_info(self, video_info):
        """预览视频信息"""
        
        video_path = video_info.get("source_path", "")
        has_file = bool(video_path) and os.path.exists(video_path)
        
        if has_file:
            file_size_mb = os.path.getsize(video_path) / (1024 * 1024)
            has_audio = self._check_audio_track(video_path)
            video_bitrate_kbps = 0
            audio_bitrate_kbps = 0
            try:
                video_bitrate_kbps = self._get_video_bitrate(video_path)
                if has_audio:
                    audio_bitrate_kbps = self._get_audio_bitrate(video_path)
            except Exception:
                video_bitrate_kbps = 0
                audio_bitrate_kbps = 0
        else:
            file_size_mb = float(video_info.get("file_size_mb", 0) or 0)
            has_audio = bool(video_info.get("has_audio", False))
            video_bitrate_kbps = int(video_info.get("video_bitrate_kbps", 0) or 0)
            audio_bitrate_kbps = int(video_info.get("audio_bitrate_kbps", 0) or 0)
            
        # 构建预览信息
        # 使用 video_info 中的宽高等信息，因为可能是处理过的
        width = video_info.get("width", 0)
        height = video_info.get("height", 0)
        fps = video_info.get("fps", 0)
        frame_count = video_info.get("frame_count", 0)
        duration = video_info.get("duration", 0)
        
        # 如果原始信息中有 total_frames，优先使用
        if "total_frames" in video_info:
            # 这里的逻辑视情况而定，VideoLoader输出的video_info可能包含裁剪后的信息
            # 但用户想看的可能是"完整"信息，或者当前流的信息
            # 这里我们显示当前流的信息
            pass

        ui_info = self._build_video_preview(
            video_path=video_path,
            fps=fps,
            frame_count=frame_count,
            duration=duration,
            has_audio=has_audio,
            file_size_mb=round(file_size_mb, 2),
            width=width,
            height=height,
            video_bitrate_kbps=video_bitrate_kbps,
            audio_bitrate_kbps=audio_bitrate_kbps
        )
        
        return {
            "ui": ui_info,
            "result": (video_info,)
        }

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
        video_path_obj = Path(video_path)
        input_dir = Path(folder_paths.get_input_directory())
        
        subfolder = ""
        try:
            # 尝试计算相对于 input 目录的路径
            if str(video_path_obj).startswith(str(input_dir)):
                relative_path = video_path_obj.resolve().relative_to(input_dir)
                subfolder = str(relative_path.parent).replace("\\", "/")
                if subfolder == ".":
                    subfolder = ""
            else:
                # 如果不在 input 目录下，可能需要特殊处理，或者直接显示文件名
                # 这里为了前端显示方便，还是传完整信息
                pass
        except ValueError:
            pass
        
        info = {
            "filename": video_path_obj.name,
            "subfolder": subfolder,
            "type": "input", # 这里假设是 input 类型，以便前端能通过 view 接口读取
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
        
        return {"videos": [info]}

    def _get_video_bitrate(self, video_path: str) -> int:
        try:
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
                return bitrate_bps // 1000
        except Exception:
            pass
        return 0
    
    def _get_audio_bitrate(self, video_path: str) -> int:
        try:
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
                return bitrate_bps // 1000
        except Exception:
            pass
        return 0
    
    def _check_audio_track(self, video_path: str) -> bool:
        try:
            ffprobe_path = shutil.which("ffprobe")
            if ffprobe_path is None:
                return False
            
            cmd = [
                ffprobe_path,
                "-v", "error",
                "-select_streams", "a:0",
                "-show_entries", "stream=codec_type",
                "-of", "default=noprint_wrappers=1:nokey=1",
                str(video_path)
            ]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=5)
            if result.returncode == 0 and result.stdout.strip() == "audio":
                return True
            return False
        except Exception:
            return False
