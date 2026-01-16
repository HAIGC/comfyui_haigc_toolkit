"""
视频变速节点
加速、减速、定格效果
"""

import torch

class VideoSpeedNode:
    """视频变速节点"""
    
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
                "变速模式": (["正常速度", "加速", "减速", "定格"], {
                    "default": "加速"
                }),
                "速度倍数": ("FLOAT", {
                    "default": 2.0,
                    "min": 0.1,
                    "max": 10.0,
                    "step": 0.1
                }),
                "定格帧位置": ("INT", {
                    "default": 0,
                    "min": 0,
                    "max": 100000,
                    "step": 1
                }),
                "定格时长": ("FLOAT", {
                    "default": 1.0,
                    "min": 0.1,
                    "max": 60.0,
                    "step": 0.1
                }),
            },
        }
    
    RETURN_TYPES = ("IMAGE", "INT", "FLOAT")
    RETURN_NAMES = ("视频", "输出帧数", "输出时长")
    FUNCTION = "change_speed"
    CATEGORY = "HAIGC工具集/视频剪辑"
    
    def change_speed(self, images, 视频帧率, 变速模式, 速度倍数, 定格帧位置, 定格时长):
        """视频变速"""
        batch_size = images.shape[0]
        
        if 变速模式 == "定格":
            # 定格效果
            freeze_frame = min(定格帧位置, batch_size - 1)
            freeze_frames_count = int(定格时长 * 视频帧率)
            
            frozen_frame = images[freeze_frame:freeze_frame+1]
            frozen_segment = frozen_frame.repeat(freeze_frames_count, 1, 1, 1)
            
            before = images[:freeze_frame+1]
            after = images[freeze_frame+1:]
            result = torch.cat([before, frozen_segment, after], dim=0)
            
            print(f"[定格效果] 第{freeze_frame}帧定格{定格时长}秒 ({freeze_frames_count}帧)")
            
        elif 变速模式 in ["加速", "减速"]:
            # 变速效果
            target_frames = int(batch_size / 速度倍数)
            target_frames = max(1, target_frames)
            
            # 帧索引+线性插值
            original_indices = torch.linspace(0, batch_size - 1, target_frames, device=images.device)
            indices_low = original_indices.long()
            indices_high = (indices_low + 1).clamp(max=batch_size - 1)
            weight = (original_indices - indices_low.float()).view(-1, 1, 1, 1)
            
            frames_low = images[indices_low]
            frames_high = images[indices_high]
            result = frames_low * (1 - weight) + frames_high * weight
            
            print(f"[视频变速] {变速模式} {速度倍数}x: {batch_size}帧 → {target_frames}帧")
        else:
            result = images
        
        output_frames = result.shape[0]
        output_duration = output_frames / 视频帧率
        
        return (result, output_frames, output_duration)

