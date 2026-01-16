"""
视频翻转节点
水平/垂直翻转
"""

import torch

class VideoFlipNode:
    """视频翻转节点"""
    
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
                "翻转方式": (["不翻转", "水平翻转", "垂直翻转", "水平+垂直"], {
                    "default": "水平翻转"
                }),
            },
        }
    
    RETURN_TYPES = ("IMAGE", "INT", "FLOAT")
    RETURN_NAMES = ("视频", "输出帧数", "输出时长")
    FUNCTION = "flip_video"
    CATEGORY = "HAIGC工具集/视频剪辑"
    
    def flip_video(self, images, 视频帧率, 翻转方式):
        """视频翻转"""
        if 翻转方式 == "水平翻转":
            result = torch.flip(images, dims=[2])
        elif 翻转方式 == "垂直翻转":
            result = torch.flip(images, dims=[1])
        elif 翻转方式 == "水平+垂直":
            result = torch.flip(images, dims=[1, 2])
        else:
            result = images
        
        output_frames = result.shape[0]
        output_duration = output_frames / 视频帧率
        
        print(f"[视频翻转] {翻转方式}")
        
        return (result, output_frames, output_duration)

