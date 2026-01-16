"""
视频循环节点
重复播放视频
"""

import torch

class VideoLoopNode:
    """视频循环节点"""
    
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
                "循环次数": ("INT", {
                    "default": 2,
                    "min": 2,
                    "max": 100,
                    "step": 1
                }),
            },
        }
    
    RETURN_TYPES = ("IMAGE", "INT", "FLOAT")
    RETURN_NAMES = ("视频", "输出帧数", "输出时长")
    FUNCTION = "loop_video"
    CATEGORY = "HAIGC工具集/视频剪辑"
    
    def loop_video(self, images, 视频帧率, 循环次数):
        """视频循环"""
        result = images.repeat(循环次数, 1, 1, 1)
        output_frames = result.shape[0]
        output_duration = output_frames / 视频帧率
        
        print(f"[视频循环] {循环次数}次, {images.shape[0]}帧 → {output_frames}帧")
        
        return (result, output_frames, output_duration)

