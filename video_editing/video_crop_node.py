"""
画面裁切节点
裁切视频画面区域
"""

import torch

class VideoCropNode:
    """画面裁切节点"""
    
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
                "裁切X坐标": ("INT", {
                    "default": 0,
                    "min": 0,
                    "max": 10000,
                    "step": 1
                }),
                "裁切Y坐标": ("INT", {
                    "default": 0,
                    "min": 0,
                    "max": 10000,
                    "step": 1
                }),
                "裁切宽度": ("INT", {
                    "default": 1920,
                    "min": 1,
                    "max": 10000,
                    "step": 1
                }),
                "裁切高度": ("INT", {
                    "default": 1080,
                    "min": 1,
                    "max": 10000,
                    "step": 1
                }),
            },
        }
    
    RETURN_TYPES = ("IMAGE", "INT", "FLOAT")
    RETURN_NAMES = ("视频", "输出帧数", "输出时长")
    FUNCTION = "crop_video"
    CATEGORY = "HAIGC工具集/视频剪辑"
    
    def crop_video(self, images, 视频帧率, 裁切X坐标, 裁切Y坐标, 裁切宽度, 裁切高度):
        """画面裁切"""
        batch_size, height, width, channels = images.shape
        
        # 边界检查
        x = max(0, min(裁切X坐标, width - 1))
        y = max(0, min(裁切Y坐标, height - 1))
        crop_width = min(裁切宽度, width - x)
        crop_height = min(裁切高度, height - y)
        
        # 裁切
        result = images[:, y:y+crop_height, x:x+crop_width, :]
        output_frames = result.shape[0]
        output_duration = output_frames / 视频帧率
        
        print(f"[画面裁切] {width}x{height} → {crop_width}x{crop_height}")
        
        return (result, output_frames, output_duration)

