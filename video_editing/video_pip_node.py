"""
画中画节点
双画面叠加显示
"""

import torch
import torch.nn.functional as F

class VideoPiPNode:
    """画中画节点"""
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "主视频": ("IMAGE",),
                "副视频": ("IMAGE",),
                "视频帧率": ("FLOAT", {
                    "default": 30.0,
                    "min": 1.0,
                    "max": 120.0,
                    "step": 0.1
                }),
                "副画面位置": (["左上", "右上", "左下", "右下", "中心"], {
                    "default": "右下"
                }),
                "副画面大小": ("FLOAT", {
                    "default": 0.25,
                    "min": 0.1,
                    "max": 0.8,
                    "step": 0.05
                }),
                "边距": ("INT", {
                    "default": 20,
                    "min": 0,
                    "max": 200,
                    "step": 10
                }),
                "副画面不透明度": ("FLOAT", {
                    "default": 1.0,
                    "min": 0.0,
                    "max": 1.0,
                    "step": 0.05
                }),
                "添加边框": (["否", "是"], {
                    "default": "是"
                }),
                "边框颜色": (["白色", "黑色", "灰色"], {
                    "default": "白色"
                }),
                "边框宽度": ("INT", {
                    "default": 3,
                    "min": 1,
                    "max": 20,
                    "step": 1
                }),
            },
        }
    
    RETURN_TYPES = ("IMAGE", "INT", "FLOAT")
    RETURN_NAMES = ("视频", "输出帧数", "输出时长")
    FUNCTION = "create_pip"
    CATEGORY = "HAIGC工具集/视频剪辑"
    
    def create_pip(self, 主视频, 副视频, 视频帧率, 副画面位置, 副画面大小, 
                   边距, 副画面不透明度, 添加边框, 边框颜色, 边框宽度):
        """创建画中画"""
        main_batch, main_h, main_w, main_c = 主视频.shape
        sub_batch, sub_h, sub_w, sub_c = 副视频.shape
        
        # 匹配帧数（使用较短的）
        min_batch = min(main_batch, sub_batch)
        主视频 = 主视频[:min_batch]
        副视频 = 副视频[:min_batch]
        
        # 计算副画面尺寸
        pip_w = int(main_w * 副画面大小)
        pip_h = int(pip_w * sub_h / sub_w)  # 保持副视频的宽高比
        
        # 缩放副视频
        sub_permuted = 副视频.permute(0, 3, 1, 2)
        pip_resized = F.interpolate(
            sub_permuted,
            size=(pip_h, pip_w),
            mode='bilinear',
            align_corners=False
        )
        pip_resized = pip_resized.permute(0, 2, 3, 1)
        
        # 添加边框
        if 添加边框 == "是":
            border_color_map = {
                "白色": 1.0,
                "黑色": 0.0,
                "灰色": 0.5
            }
            border_color = border_color_map[边框颜色]
            
            # 创建带边框的画面
            bordered_h = pip_h + 2 * 边框宽度
            bordered_w = pip_w + 2 * 边框宽度
            bordered = torch.ones(min_batch, bordered_h, bordered_w, main_c, 
                                 device=主视频.device) * border_color
            bordered[:, 边框宽度:边框宽度+pip_h, 边框宽度:边框宽度+pip_w, :] = pip_resized
            pip_resized = bordered
            pip_h, pip_w = bordered_h, bordered_w
        
        # 计算副画面位置
        if 副画面位置 == "左上":
            y_pos = 边距
            x_pos = 边距
        elif 副画面位置 == "右上":
            y_pos = 边距
            x_pos = main_w - pip_w - 边距
        elif 副画面位置 == "左下":
            y_pos = main_h - pip_h - 边距
            x_pos = 边距
        elif 副画面位置 == "右下":
            y_pos = main_h - pip_h - 边距
            x_pos = main_w - pip_w - 边距
        elif 副画面位置 == "中心":
            y_pos = (main_h - pip_h) // 2
            x_pos = (main_w - pip_w) // 2
        else:
            y_pos, x_pos = 边距, 边距
        
        # 确保位置在有效范围内
        y_pos = max(0, min(y_pos, main_h - pip_h))
        x_pos = max(0, min(x_pos, main_w - pip_w))
        
        # 合成画中画
        result = 主视频.clone()
        
        # 混合副画面（支持透明度）
        for i in range(min_batch):
            result[i, y_pos:y_pos+pip_h, x_pos:x_pos+pip_w, :] = \
                result[i, y_pos:y_pos+pip_h, x_pos:x_pos+pip_w, :] * (1 - 副画面不透明度) + \
                pip_resized[i] * 副画面不透明度
        
        output_frames = result.shape[0]
        output_duration = output_frames / 视频帧率
        
        print(f"[画中画] 位置:{副画面位置}, 大小:{副画面大小:.2f}, PIP尺寸:{pip_w}x{pip_h}")
        
        return (result, output_frames, output_duration)

