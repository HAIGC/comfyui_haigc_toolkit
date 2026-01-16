"""
视频缩放节点
改变视频分辨率
"""

import torch
import torch.nn.functional as F

class VideoResizeNode:
    """视频缩放节点"""
    
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
                "目标宽度": ("INT", {
                    "default": 1920,
                    "min": 1,
                    "max": 10000,
                    "step": 1
                }),
                "目标高度": ("INT", {
                    "default": 1080,
                    "min": 1,
                    "max": 10000,
                    "step": 1
                }),
                "缩放算法": (["双线性", "双三次", "最近邻"], {
                    "default": "双三次"
                }),
            },
        }
    
    RETURN_TYPES = ("IMAGE", "INT", "FLOAT")
    RETURN_NAMES = ("视频", "输出帧数", "输出时长")
    FUNCTION = "resize_video"
    CATEGORY = "HAIGC工具集/视频剪辑"
    
    def resize_video(self, images, 视频帧率, 目标宽度, 目标高度, 缩放算法):
        """视频缩放"""
        batch_size, height, width, channels = images.shape
        
        # 选择插值算法
        mode_map = {
            "双线性": "bilinear",
            "双三次": "bicubic",
            "最近邻": "nearest"
        }
        mode = mode_map.get(缩放算法, "bicubic")
        
        # [B, H, W, C] -> [B, C, H, W]
        images_permuted = images.permute(0, 3, 1, 2)
        
        # 缩放
        resized = F.interpolate(
            images_permuted,
            size=(目标高度, 目标宽度),
            mode=mode,
            align_corners=False if mode in ["bilinear", "bicubic"] else None
        )
        
        # [B, C, H, W] -> [B, H, W, C]
        result = resized.permute(0, 2, 3, 1)
        output_frames = result.shape[0]
        output_duration = output_frames / 视频帧率
        
        print(f"[视频缩放] {width}x{height} → {目标宽度}x{目标高度} ({缩放算法})")
        
        return (result, output_frames, output_duration)

