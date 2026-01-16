"""
视频倒放节点
反向播放视频
"""

import torch

class VideoReverseNode:
    """视频倒放节点"""
    
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
            },
        }
    
    RETURN_TYPES = ("IMAGE", "INT", "FLOAT")
    RETURN_NAMES = ("视频", "输出帧数", "输出时长")
    FUNCTION = "reverse_video"
    CATEGORY = "HAIGC工具集/视频剪辑"
    
    def reverse_video(self, images, 视频帧率):
        """视频倒放"""
        result = torch.flip(images, dims=[0])
        output_frames = result.shape[0]
        output_duration = output_frames / 视频帧率
        
        print(f"[视频倒放] {output_frames}帧")
        
        return (result, output_frames, output_duration)

