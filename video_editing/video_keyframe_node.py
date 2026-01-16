"""
关键帧动画节点
参数动画控制（位置、缩放、旋转、透明度）
"""

import torch
import torch.nn.functional as F
import math

class VideoKeyframeNode:
    """关键帧动画节点"""
    
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
                "动画类型": (["位移", "缩放", "旋转", "淡入淡出", "组合"], {
                    "default": "位移"
                }),
                # 位移参数
                "起始X": ("FLOAT", {
                    "default": 0.0,
                    "min": -1.0,
                    "max": 1.0,
                    "step": 0.01
                }),
                "结束X": ("FLOAT", {
                    "default": 0.0,
                    "min": -1.0,
                    "max": 1.0,
                    "step": 0.01
                }),
                "起始Y": ("FLOAT", {
                    "default": 0.0,
                    "min": -1.0,
                    "max": 1.0,
                    "step": 0.01
                }),
                "结束Y": ("FLOAT", {
                    "default": 0.0,
                    "min": -1.0,
                    "max": 1.0,
                    "step": 0.01
                }),
                # 缩放参数
                "起始缩放": ("FLOAT", {
                    "default": 1.0,
                    "min": 0.1,
                    "max": 3.0,
                    "step": 0.05
                }),
                "结束缩放": ("FLOAT", {
                    "default": 1.0,
                    "min": 0.1,
                    "max": 3.0,
                    "step": 0.05
                }),
                # 透明度参数
                "起始透明度": ("FLOAT", {
                    "default": 1.0,
                    "min": 0.0,
                    "max": 1.0,
                    "step": 0.05
                }),
                "结束透明度": ("FLOAT", {
                    "default": 1.0,
                    "min": 0.0,
                    "max": 1.0,
                    "step": 0.05
                }),
                # 缓动函数
                "缓动方式": (["线性", "缓入", "缓出", "缓入缓出", "弹性"], {
                    "default": "缓入缓出"
                }),
            },
        }
    
    RETURN_TYPES = ("IMAGE", "INT", "FLOAT")
    RETURN_NAMES = ("视频", "输出帧数", "输出时长")
    FUNCTION = "apply_keyframe_animation"
    CATEGORY = "HAIGC工具集/视频剪辑"
    
    def ease_function(self, t, 缓动方式):
        """缓动函数"""
        if 缓动方式 == "线性":
            return t
        elif 缓动方式 == "缓入":
            return t * t
        elif 缓动方式 == "缓出":
            return 1 - (1 - t) * (1 - t)
        elif 缓动方式 == "缓入缓出":
            if t < 0.5:
                return 2 * t * t
            else:
                return 1 - 2 * (1 - t) * (1 - t)
        elif 缓动方式 == "弹性":
            if t == 0 or t == 1:
                return t
            return math.pow(2, -10 * t) * math.sin((t - 0.075) * (2 * math.pi) / 0.3) + 1
        return t
    
    def apply_keyframe_animation(self, images, 视频帧率, 动画类型,
                                  起始X, 结束X, 起始Y, 结束Y,
                                  起始缩放, 结束缩放, 起始透明度, 结束透明度,
                                  缓动方式):
        """应用关键帧动画"""
        batch_size, height, width, channels = images.shape
        result = images.clone()
        
        for i in range(batch_size):
            # 计算当前帧的插值比例
            t = i / max(batch_size - 1, 1)
            t_eased = self.ease_function(t, 缓动方式)
            
            current_frame = result[i]
            
            if 动画类型 == "位移" or 动画类型 == "组合":
                # 计算当前位移
                offset_x = 起始X + (结束X - 起始X) * t_eased
                offset_y = 起始Y + (结束Y - 起始Y) * t_eased
                
                # 转换为像素偏移
                pixel_offset_x = int(offset_x * width)
                pixel_offset_y = int(offset_y * height)
                
                # 应用位移（通过滚动实现）
                if pixel_offset_x != 0:
                    current_frame = torch.roll(current_frame, pixel_offset_x, dims=1)
                if pixel_offset_y != 0:
                    current_frame = torch.roll(current_frame, pixel_offset_y, dims=0)
            
            if 动画类型 == "缩放" or 动画类型 == "组合":
                # 计算当前缩放
                scale = 起始缩放 + (结束缩放 - 起始缩放) * t_eased
                
                if scale != 1.0:
                    # 缩放实现（通过裁剪和插值）
                    new_h = int(height / scale)
                    new_w = int(width / scale)
                    
                    center_y, center_x = height // 2, width // 2
                    y1 = max(0, center_y - new_h // 2)
                    y2 = min(height, center_y + new_h // 2)
                    x1 = max(0, center_x - new_w // 2)
                    x2 = min(width, center_x + new_w // 2)
                    
                    # 裁剪
                    cropped = current_frame[y1:y2, x1:x2, :].unsqueeze(0).permute(0, 3, 1, 2)
                    # 缩放回原尺寸
                    scaled = F.interpolate(cropped, size=(height, width), mode='bilinear', align_corners=False)
                    current_frame = scaled.squeeze(0).permute(1, 2, 0)
            
            if 动画类型 == "淡入淡出" or 动画类型 == "组合":
                # 计算当前透明度
                opacity = 起始透明度 + (结束透明度 - 起始透明度) * t_eased
                current_frame = current_frame * opacity
            
            result[i] = current_frame
        
        # 裁剪到有效范围
        result = torch.clamp(result, 0, 1)
        
        output_frames = result.shape[0]
        output_duration = output_frames / 视频帧率
        
        print(f"[关键帧动画] 类型:{动画类型}, 缓动:{缓动方式}")
        if 动画类型 == "位移" or 动画类型 == "组合":
            print(f"  位移: ({起始X:.2f},{起始Y:.2f}) → ({结束X:.2f},{结束Y:.2f})")
        if 动画类型 == "缩放" or 动画类型 == "组合":
            print(f"  缩放: {起始缩放:.2f} → {结束缩放:.2f}")
        if 动画类型 == "淡入淡出" or 动画类型 == "组合":
            print(f"  透明度: {起始透明度:.2f} → {结束透明度:.2f}")
        
        return (result, output_frames, output_duration)

