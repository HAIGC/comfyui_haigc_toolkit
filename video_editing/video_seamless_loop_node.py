"""
无限循环节点
首尾平滑过渡，创建无缝循环效果
"""

import torch

class VideoSeamlessLoopNode:
    """无限循环节点"""
    
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
                "过渡时长": ("FLOAT", {
                    "default": 0.5,
                    "min": 0.1,
                    "max": 5.0,
                    "step": 0.1
                }),
                "过渡模式": (["线性淡化", "交叉淡化", "帧混合"], {
                    "default": "交叉淡化"
                }),
                "循环次数": ("INT", {
                    "default": 2,
                    "min": 1,
                    "max": 20,
                    "step": 1
                }),
            },
        }
    
    RETURN_TYPES = ("IMAGE", "INT", "FLOAT")
    RETURN_NAMES = ("视频", "输出帧数", "输出时长")
    FUNCTION = "create_seamless_loop"
    CATEGORY = "HAIGC工具集/视频剪辑"
    
    def create_seamless_loop(self, images, 视频帧率, 过渡时长, 过渡模式, 循环次数):
        """创建无缝循环"""
        batch_size = images.shape[0]
        transition_frames = int(过渡时长 * 视频帧率)
        transition_frames = min(transition_frames, batch_size // 2)
        
        if 过渡模式 == "线性淡化":
            # 线性淡化：结尾渐暗，开头渐亮
            fade_curve = torch.linspace(0, 1, transition_frames, device=images.device)
            fade_curve = fade_curve.view(-1, 1, 1, 1)
            
            # 修改结尾帧
            end_frames = images[-transition_frames:].clone()
            end_frames = end_frames * (1 - fade_curve)
            
            # 修改开头帧
            start_frames = images[:transition_frames].clone()
            start_frames = start_frames * fade_curve
            
            # 合成单次循环
            middle = images[transition_frames:-transition_frames]
            loop_segment = torch.cat([start_frames, middle, end_frames], dim=0)
            
        elif 过渡模式 == "交叉淡化":
            # 交叉淡化：首尾混合
            fade_curve = torch.linspace(0, 1, transition_frames, device=images.device)
            fade_curve = fade_curve.view(-1, 1, 1, 1)
            
            # 提取首尾帧
            start_frames = images[:transition_frames]
            end_frames = images[-transition_frames:]
            
            # 交叉混合
            blended = end_frames * (1 - fade_curve) + start_frames * fade_curve
            
            # 合成单次循环（移除原始的首尾过渡帧）
            middle = images[transition_frames:-transition_frames]
            loop_segment = torch.cat([blended, middle], dim=0)
            
        elif 过渡模式 == "帧混合":
            # 帧混合：首尾帧直接混合
            blend_ratio = 0.5
            start_frames = images[:transition_frames]
            end_frames = images[-transition_frames:]
            
            blended = start_frames * blend_ratio + end_frames * (1 - blend_ratio)
            
            middle = images[transition_frames:-transition_frames]
            loop_segment = torch.cat([blended, middle], dim=0)
        
        else:
            loop_segment = images
        
        # 循环复制
        result = loop_segment.repeat(循环次数, 1, 1, 1)
        
        output_frames = result.shape[0]
        output_duration = output_frames / 视频帧率
        
        print(f"[无限循环] 过渡:{过渡时长}s ({transition_frames}帧), 循环{循环次数}次")
        print(f"  单次循环:{loop_segment.shape[0]}帧, 总输出:{output_frames}帧")
        
        return (result, output_frames, output_duration)

