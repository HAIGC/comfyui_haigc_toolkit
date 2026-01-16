"""
分镜音视频裁剪节点
根据分镜信息同步裁剪视频和音频片段
"""

import json
from typing import Dict, Tuple

import torch


class VideoSceneAVSplitNode:
    """
    分镜音视频裁剪节点

    功能：
    - 根据分镜识别节点输出的场景数据，裁剪对应的视频片段
    - 同步裁剪音频，保证音视频时长一致
    - 输出独立的视频/音频对，可用于预览或保存
    """

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "images": ("IMAGE",),
                "audio": ("AUDIO",),
                "场景数据": ("STRING",),
                "场景序号": ("INT", {
                    "default": 1,
                    "min": 1,
                    "max": 100,
                    "step": 1,
                    "tooltip": "选择需要裁剪的场景（从 1 开始）"
                }),
            },
        }

    RETURN_TYPES = ("IMAGE", "AUDIO", "STRING")
    RETURN_NAMES = ("视频", "音频", "场景信息")
    FUNCTION = "split_scene_av"
    CATEGORY = "HAIGC工具集/视频剪辑"

    def split_scene_av(
        self,
        images: torch.Tensor,
        audio: Dict[str, torch.Tensor],
        场景数据: str,
        场景序号: int,
    ) -> Tuple[torch.Tensor, Dict[str, torch.Tensor], str]:
        """同步裁剪分镜的视频与音频"""
        try:
            if images.dim() != 4:
                raise ValueError("视频张量应为4维 (帧, 高, 宽, 通道)")

            scene_data = json.loads(场景数据)
            scene_changes = scene_data.get("scene_changes", [])
            scene_count = scene_data.get("scene_count", 0)
            frame_rate = float(scene_data.get("frame_rate", 30.0) or 30.0)
            total_frames = images.shape[0]

            if scene_count == 0 or len(scene_changes) == 0:
                raise ValueError("场景数据无效或未检测到场景，请先运行分镜识别节点。")

            scene_idx = max(0, min(场景序号 - 1, scene_count - 1))
            if scene_idx != 场景序号 - 1:
                print(f"[分镜音视频裁剪] 提示：场景序号 {场景序号} 超出范围，已调整为 {scene_idx + 1}")

            start_frame = scene_changes[scene_idx]
            end_frame = scene_changes[scene_idx + 1] if scene_idx + 1 < len(scene_changes) else total_frames

            start_frame = max(0, min(start_frame, total_frames - 1))
            end_frame = max(start_frame + 1, min(end_frame, total_frames))

            video_clip = images[start_frame:end_frame].clone()

            start_time = start_frame / frame_rate
            end_time = end_frame / frame_rate
            duration = end_time - start_time

            audio_clip = self._slice_audio(audio, start_time, end_time)

            info = (
                f"场景{scene_idx + 1}: "
                f"{start_time:.2f}s - {end_time:.2f}s "
                f"(时长 {duration:.2f}s, 帧 {start_frame}-{end_frame})"
            )

            print(f"[分镜音视频裁剪] {info}")
            print(f"[分镜音视频裁剪] 视频片段: {video_clip.shape}, 音频片段: {audio_clip['waveform'].shape}")

            return (video_clip, audio_clip, info)

        except Exception as exc:
            print(f"[分镜音视频裁剪] 错误: {exc}")
            import traceback
            traceback.print_exc()

            dummy_video = images[:1].clone() if images.numel() > 0 else torch.zeros((1, 64, 64, 3))
            dummy_audio = {
                "waveform": torch.zeros((1, 2, 0)),
                "sample_rate": int(audio.get("sample_rate", 44100) or 44100) if isinstance(audio, dict) else 44100,
            }
            return (dummy_video, dummy_audio, f"出错: {exc}")

    def _slice_audio(
        self,
        audio: Dict[str, torch.Tensor],
        start_time: float,
        end_time: float,
    ) -> Dict[str, torch.Tensor]:
        """根据时间范围裁剪音频"""
        if not isinstance(audio, dict) or "waveform" not in audio:
            return {"waveform": torch.zeros((1, 2, 0)), "sample_rate": 44100}

        waveform = audio.get("waveform")
        sample_rate = int(audio.get("sample_rate", 44100) or 44100)

        if waveform is None or waveform.numel() == 0:
            return {"waveform": torch.zeros((1, 2, 0)), "sample_rate": sample_rate}

        if waveform.dim() == 2:
            waveform = waveform.unsqueeze(0)

        total_samples = waveform.shape[-1]
        start_sample = int(round(max(0.0, start_time) * sample_rate))
        end_sample = int(round(max(start_time, end_time) * sample_rate))
        start_sample = min(start_sample, total_samples)
        end_sample = min(max(start_sample + 1, end_sample), total_samples)

        sliced = waveform[..., start_sample:end_sample].clone()

        return {
            "waveform": sliced,
            "sample_rate": sample_rate,
        }


NODE_CLASS_MAPPINGS = {
    "VideoSceneAVSplitNode": VideoSceneAVSplitNode,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "VideoSceneAVSplitNode": "分镜音视频裁剪 🎧",
}

