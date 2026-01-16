"""
视频时间裁剪节点
按时间或帧数精确裁剪视频片段
"""

import torch

class VideoTrimNode:
    """视频时间裁剪节点"""
    
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
                "裁剪模式": (["按时间", "按帧数"], {
                    "default": "按时间"
                }),
                "开始时间": ("FLOAT", {
                    "default": 0.0,
                    "min": 0.0,
                    "max": 3600.0,
                    "step": 0.01
                }),
                "结束时间": ("FLOAT", {
                    "default": 0.0,
                    "min": 0.0,
                    "max": 3600.0,
                    "step": 0.01
                }),
                "开始帧": ("INT", {
                    "default": 0,
                    "min": 0,
                    "max": 100000,
                    "step": 1
                }),
                "结束帧": ("INT", {
                    "default": 0,
                    "min": 0,
                    "max": 100000,
                    "step": 1
                }),
            },
            "optional": {
                "audio": ("AUDIO",),
            }
        }
    
    RETURN_TYPES = ("IMAGE", "AUDIO", "INT", "FLOAT")
    RETURN_NAMES = ("视频", "音频", "输出帧数", "输出时长")
    FUNCTION = "trim_video"
    CATEGORY = "HAIGC工具集/视频剪辑"
    
    def trim_video(self, images, 视频帧率, 裁剪模式, 开始时间, 结束时间, 开始帧, 结束帧, audio=None):
        """视频时间裁剪"""
        batch_size = images.shape[0]
        
        if 裁剪模式 == "按时间":
            start_idx = int(开始时间 * 视频帧率)
            end_idx = int(结束时间 * 视频帧率) if 结束时间 > 0 else batch_size
        else:  # 按帧数
            start_idx = 开始帧
            end_idx = 结束帧 if 结束帧 > 0 else batch_size
        
        # 边界检查
        start_idx = max(0, min(start_idx, batch_size - 1))
        end_idx = max(start_idx + 1, min(end_idx, batch_size))
        
        result = images[start_idx:end_idx]
        output_frames = result.shape[0]
        output_duration = output_frames / 视频帧率
        
        trimmed_audio = self._trim_audio(audio, start_idx, end_idx, 视频帧率)
        
        print(f"[视频裁剪] {batch_size}帧 → {output_frames}帧 (第{start_idx}-{end_idx}帧)")
        
        return (result, trimmed_audio, output_frames, output_duration)

    def _trim_audio(self, audio, start_idx, end_idx, fps):
        """根据帧区间裁剪音频"""
        if audio is None or not isinstance(audio, dict) or "waveform" not in audio:
            return {"waveform": torch.zeros((1, 2, 0)), "sample_rate": 44100}
        
        waveform = audio.get("waveform")
        sample_rate = int(audio.get("sample_rate", 44100) or 44100)
        
        if waveform is None or waveform.numel() == 0:
            return {"waveform": torch.zeros((1, 2, 0)), "sample_rate": sample_rate}
        
        if waveform.dim() == 2:
            waveform = waveform.unsqueeze(0)
        
        start_time = start_idx / fps
        end_time = end_idx / fps
        
        total_samples = waveform.shape[-1]
        start_sample = int(round(start_time * sample_rate))
        end_sample = int(round(end_time * sample_rate))
        start_sample = min(max(start_sample, 0), total_samples)
        end_sample = min(max(end_sample, start_sample + 1), total_samples)
        
        trimmed = waveform[..., start_sample:end_sample].clone()
        
        return {
            "waveform": trimmed,
            "sample_rate": sample_rate
        }

