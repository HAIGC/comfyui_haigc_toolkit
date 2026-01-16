"""
视频旋转节点
90/180/270度旋转
"""

import torch

class VideoRotateNode:
    """视频旋转节点"""
    
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
                "旋转角度": (["0度", "90度顺时针", "180度", "90度逆时针"], {
                    "default": "90度顺时针"
                }),
            },
        }
    
    RETURN_TYPES = ("IMAGE", "INT", "FLOAT")
    RETURN_NAMES = ("视频", "输出帧数", "输出时长")
    FUNCTION = "rotate_video"
    CATEGORY = "HAIGC工具集/视频剪辑"
    
    def rotate_video(self, images, 视频帧率, 旋转角度):
        """视频旋转"""
        if 旋转角度 == "90度顺时针":
            result = torch.rot90(images, k=-1, dims=[1, 2])
        elif 旋转角度 == "180度":
            result = torch.rot90(images, k=2, dims=[1, 2])
        elif 旋转角度 == "90度逆时针":
            result = torch.rot90(images, k=1, dims=[1, 2])
        else:
            result = images
        
        output_frames = result.shape[0]
        output_duration = output_frames / 视频帧率
        
        print(f"[视频旋转] {旋转角度}, 输出尺寸: {result.shape[2]}x{result.shape[1]}")
        
        return (result, output_frames, output_duration)

