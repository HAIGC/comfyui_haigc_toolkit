"""
淡入淡出节点
开头/结尾渐变效果
"""

import torch

class VideoFadeNode:
    """淡入淡出节点"""
    
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
                "淡入时长": ("FLOAT", {
                    "default": 0.0,
                    "min": 0.0,
                    "max": 10.0,
                    "step": 0.1
                }),
                "淡出时长": ("FLOAT", {
                    "default": 0.0,
                    "min": 0.0,
                    "max": 10.0,
                    "step": 0.1
                }),
            },
        }
    
    RETURN_TYPES = ("IMAGE", "INT", "FLOAT")
    RETURN_NAMES = ("视频", "输出帧数", "输出时长")
    FUNCTION = "apply_fade"
    CATEGORY = "HAIGC工具集/视频剪辑"
    
    def apply_fade(self, images, 视频帧率, 淡入时长, 淡出时长):
        """淡入淡出效果"""
        batch_size = images.shape[0]
        
        # 计算淡入淡出的帧数
        fade_in_frames = int(淡入时长 * 视频帧率)
        fade_out_frames = int(淡出时长 * 视频帧率)
        
        # 限制帧数
        fade_in_frames = min(fade_in_frames, batch_size // 2)
        fade_out_frames = min(fade_out_frames, batch_size // 2)
        
        if fade_in_frames > 0 or fade_out_frames > 0:
            # 创建alpha遮罩
            alpha = torch.ones(batch_size, 1, 1, 1, device=images.device)
            
            # 淡入
            if fade_in_frames > 0:
                fade_in_curve = torch.linspace(0, 1, fade_in_frames, device=images.device)
                alpha[:fade_in_frames] = fade_in_curve.view(-1, 1, 1, 1)
            
            # 淡出
            if fade_out_frames > 0:
                fade_out_curve = torch.linspace(1, 0, fade_out_frames, device=images.device)
                alpha[-fade_out_frames:] = fade_out_curve.view(-1, 1, 1, 1)
            
            # 应用淡化
            result = images * alpha
            print(f"[淡入淡出] 淡入:{淡入时长}s ({fade_in_frames}帧), 淡出:{淡出时长}s ({fade_out_frames}帧)")
        else:
            result = images
        
        output_frames = result.shape[0]
        output_duration = output_frames / 视频帧率
        
        return (result, output_frames, output_duration)

