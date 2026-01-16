"""
视频字幕添加节点 - 增强版（v2.6.0-stable）
支持渐变、多段字幕、横竖排版、旋转等高级功能
性能优化、质量提升、稳定性增强

v2.6.0更新：
  - 新增：去除标点符号功能（5种模式）
  - 支持：中文标点、英文标点、所有标点、所有符号
  - 增强：字幕文本预处理能力

v2.5.0更新：
  - 对齐：与专业版节点参数顺序保持一致
  - 优化：基础→字体→描边→投影→位置→渐变→动画→时间→高级
  - 改进：相同功能模块位置统一，便于切换使用

v2.4.0更新：
  - 优化：参数按功能分组排序，提升易用性
  - 分组：基础设置→字体样式→位置对齐→渐变→描边→投影→动画→时间→高级
  - 改进：更符合工作流程的参数布局
  - 增强：添加清晰的emoji图标分组标识

v2.3.0更新：
  - 新增：位置预设功能（12种预设位置）
  - 新增：文字对齐方式（左对齐、居中对齐、右对齐）
  - 改进：更灵活的字幕定位系统

v2.2.1更新：修复字体加载失败导致显示无效的问题
v2.2.0更新：添加"按字裁剪"智能边界处理
v2.0.1更新：精简输出端口
"""

import torch
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import os
import math
import gc
import re
from collections import OrderedDict
from typing import Tuple, Dict, Any, Optional
import folder_paths
import torch.nn.functional as F

class VideoSubtitleEnhancedNode:
    """视频字幕添加节点 - 增强版（v2.6.0-stable）
    
    特性：
    - 高性能渐变算法（使用numpy矢量化）
    - 高质量描边（优化算法）
    - 丰富的动效（28种）
    - 完整的错误处理和输入验证
    - 优化的LRU字体缓存机制
    - 横竖排全功能支持
    - 精简输出端口（图像、开始时间、结束时间）
    - 内存占用优化
    - 智能按字裁剪（v2.2.0新增）
    - 可靠的字体fallback机制（v2.2.1修复）
    - 位置预设和文字对齐（v2.3.0新增）
    - 优化参数排序布局（v2.4.0新增）
    - 与专业版参数顺序对齐（v2.5.0新增）
    - 去除标点符号功能（v2.6.0新增）
    """
    
    # 使用OrderedDict实现LRU字体缓存
    _font_cache = OrderedDict()
    _max_font_cache = 30  # 减少缓存大小
    
    def __init__(self):
        self.type = "HAIGC_VideoSubtitleEnhanced"
        
    @classmethod
    def INPUT_TYPES(cls):
        fonts_list = cls.get_available_fonts()
        
        return {
            "required": {
                # === 📝 基础设置 ===
                "images": ("IMAGE",),
                "字幕文本": ("STRING", {
                    "default": """这是视频添加时间戳字幕的节点
作者网名：HAIGC(全网同名)
作者微信号：HAIGC1994
剪映接口只有早上到下午3点左右可以用""",
                    "multiline": True
                }),
                
                # === 🎨 字体样式 ===
                "字体选择": (fonts_list, {
                    "default": fonts_list[0] if fonts_list else "AlibabaHealthFont2.0CN-45R"
                }),
                "字体大小": ("INT", {
                    "default": 48,
                    "min": 12,
                    "max": 300,
                    "step": 1
                }),
                "最大行数": ("INT", {
                    "default": 1,
                    "min": 1,
                    "max": 10,
                    "step": 1
                }),
                "字体粗细": (["常规", "粗体", "特粗", "超粗"], {
                    "default": "常规"
                }),
                "字体颜色": ("STRING", {
                    "default": "#FFFFFF",
                    "multiline": False,
                    "placeholder": "十六进制(#FFFFFF)或十进制(16777215)"
                }),
                "不透明度": ("FLOAT", {
                    "default": 1.0,
                    "min": 0.0,
                    "max": 1.0,
                    "step": 0.01
                }),
                
                # === 🖊️ 描边设置 ===
                "描边大小": ("INT", {
                    "default": 0,
                    "min": 0,
                    "max": 50,
                    "step": 1,
                    "display": "number"
                }),
                "描边颜色": ("STRING", {
                    "default": "#000000",
                    "multiline": False,
                    "placeholder": "十六进制或十进制"
                }),
                "描边位置": (["外部", "居中", "内部"], {
                    "default": "外部"
                }),
                "描边不透明度": ("FLOAT", {
                    "default": 1.0,
                    "min": 0.0,
                    "max": 1.0,
                    "step": 0.01,
                    "display": "number"
                }),
                
                # === 🌟 投影设置 ===
                "投影角度": ("INT", {
                    "default": 135,
                    "min": 0,
                    "max": 360,
                    "step": 1
                }),
                "投影距离": ("INT", {
                    "default": 5,
                    "min": 0,
                    "max": 100,
                    "step": 1
                }),
                "投影强度": ("FLOAT", {
                    "default": 0.75,
                    "min": 0.0,
                    "max": 1.0,
                    "step": 0.01
                }),
                "投影模糊": ("INT", {
                    "default": 4,
                    "min": 0,
                    "max": 30,
                    "step": 1
                }),
                
                # === 📍 位置与对齐 ===
                "位置预设": ([
                    "自定义", "底部居中", "顶部居中", "中心", 
                    "左下角", "右下角", "左上角", "右上角",
                    "左侧居中", "右侧居中", "底部三分之一", "顶部三分之一"
                ], {
                    "default": "底部居中"
                }),
                "文字对齐": (["左对齐", "居中对齐", "右对齐"], {
                    "default": "居中对齐"
                }),
                "位置X百分比": ("FLOAT", {
                    "default": 50.0,
                    "min": 0.0,
                    "max": 100.0,
                    "step": 0.1
                }),
                "位置Y百分比": ("FLOAT", {
                    "default": 85.0,
                    "min": 0.0,
                    "max": 100.0,
                    "step": 0.1
                }),
                "排版方向": (["横排", "竖排"], {
                    "default": "横排"
                }),
                "字体角度": ("INT", {
                    "default": 0,
                    "min": -180,
                    "max": 180,
                    "step": 1
                }),
                
                # === 🌈 渐变效果 ===
                "渐变效果": (["无", "线性渐变", "径向渐变", "对角渐变"], {
                    "default": "无"
                }),
                "渐变开头颜色": ("STRING", {
                    "default": "#FFFFFF",
                    "multiline": False,
                    "placeholder": "十六进制或十进制"
                }),
                "渐变中间颜色": ("STRING", {
                    "default": "#FFFF00",
                    "multiline": False,
                    "placeholder": "十六进制或十进制"
                }),
                "渐变末尾颜色": ("STRING", {
                    "default": "#FF0000",
                    "multiline": False,
                    "placeholder": "十六进制或十进制"
                }),
                "渐变过渡强度": ("FLOAT", {
                    "default": 1.0,
                    "min": 0.0,
                    "max": 2.0,
                    "step": 0.05
                }),
                
                # === 🎬 动画效果 ===
                "动效类型": ([
                    "无", "淡入", "淡出", "滚动上升", "滚动下降", 
                    "打字机", "缩放出现", "左飞入", "右飞入", "上飞入", "下飞入",
                    "弹跳出现", "旋转淡入", "波浪效果", "闪烁", "抖动出现",
                    "渐进放大", "分裂合并", "弹性进入", "3D翻转",
                    "爆炸进入（增强）", "螺旋出现（增强）", "粒子聚合（增强）", 
                    "光速飞入（增强）", "弹簧抖动（增强）", "翻书效果（增强）",
                    "液体流动（增强）", "闪电出现（增强）", "碎片重组（增强）"
                ], {
                    "default": "无"
                }),
                "动效强度": ("FLOAT", {
                    "default": 1.0,
                    "min": 0.1,
                    "max": 3.0,
                    "step": 0.1
                }),
                "动效时长": ("FLOAT", {
                    "default": 1.0,
                    "min": 0.01,
                    "max": 300.0,
                    "step": 0.01,
                    "display": "number"
                }),
                "动效速度调节": ("FLOAT", {
                    "default": 1.0,
                    "min": 0.1,
                    "max": 5.0,
                    "step": 0.1,
                    "display": "number"
                }),
                
                # === ⏱️ 时间控制 ===
                "开始时间": ("FLOAT", {
                    "default": 0.0,
                    "min": 0.0,
                    "max": 3600.0,
                    "step": 0.01
                }),
                "结束时间": ("FLOAT", {
                    "default": 0.0,
                    "min": 0.0,
                    "max": 3600.0,
                    "step": 0.01
                }),
                "时间单位": (["帧数", "秒数"], {
                    "default": "秒数"
                }),
                "视频帧率": ("FLOAT", {
                    "default": 30.0,
                    "min": 1.0,
                    "max": 120.0,
                    "step": 0.01
                }),
                
                # === ⚙️ 高级选项 ===
                "字间距": ("INT", {
                    "default": 0,
                    "min": -50,
                    "max": 200,
                    "step": 1,
                    "display": "number"
                }),
                "去除标点符号": (["不去除", "中文标点", "英文标点", "所有标点", "所有符号"], {
                    "default": "不去除"
                }),
                "限定在画布内": (["否", "自动缩放", "按字裁剪"], {
                    "default": "自动缩放"
                }),
            },
        }
    
    RETURN_TYPES = ("IMAGE", "FLOAT", "FLOAT")
    RETURN_NAMES = ("图像", "开始时间", "结束时间")
    FUNCTION = "add_subtitle"
    CATEGORY = "HAIGC工具集/视频处理"
    
    @staticmethod
    def get_available_fonts():
        """获取可用字体列表（仅自定义字体）"""
        # 扫描 font 文件夹中的自定义字体
        custom_fonts = []
        current_dir = os.path.dirname(os.path.abspath(__file__))
        font_dir = os.path.join(current_dir, "font")
        
        if os.path.exists(font_dir):
            for filename in sorted(os.listdir(font_dir)):
                if filename.lower().endswith(('.ttf', '.otf', '.ttc')):
                    # 使用文件名（不含扩展名）作为字体名称
                    font_name = os.path.splitext(filename)[0]
                    custom_fonts.append(font_name)
        
        # 如果没有自定义字体，返回一个提示
        if not custom_fonts:
            custom_fonts = ["请在font文件夹中添加字体文件"]
        
        return custom_fonts
    
    @classmethod
    def get_font_path(cls, font_name: str) -> Optional[str]:
        """根据字体名称获取字体文件路径（仅支持自定义字体）"""
        
        # 查找自定义 font 文件夹
        current_dir = os.path.dirname(os.path.abspath(__file__))
        custom_font_dir = os.path.join(current_dir, "font")
        
        if os.path.exists(custom_font_dir):
            # 查找匹配的字体文件
            for ext in ['.ttf', '.otf', '.ttc']:
                custom_font_path = os.path.join(custom_font_dir, font_name + ext)
                if os.path.exists(custom_font_path):
                    print(f"[字体加载] 使用自定义字体: {font_name}{ext}")
                    return custom_font_path
        
        # 如果没找到，尝试使用默认字体
        default_font_path = os.path.join(custom_font_dir, "AlibabaHealthFont2.0CN-45R.ttf")
        if os.path.exists(default_font_path):
            print(f"[字体加载] 字体 '{font_name}' 不存在，使用默认字体")
            return default_font_path
        
        print(f"[字体加载] 错误: 字体 '{font_name}' 不存在，且默认字体也不存在！")
        return None
    
    @classmethod
    def get_cached_font(cls, font_name: str, size: int) -> Optional[ImageFont.FreeTypeFont]:
        """获取缓存的字体对象（优化的LRU缓存）"""
        size = max(12, min(500, size))  # 边界检查
        cache_key = f"{font_name}_{size}"
        
        # LRU缓存：如果存在，移到末尾
        if cache_key in cls._font_cache:
            cls._font_cache.move_to_end(cache_key)
            return cls._font_cache[cache_key]
        
        font_path = cls.get_font_path(font_name)
        if not font_path:
            print(f"[字体缓存] 无法加载字体 '{font_name}'")
            return None
        
        try:
            font = ImageFont.truetype(font_path, size)
            
            # LRU缓存管理：超过限制时移除最旧的
            if len(cls._font_cache) >= cls._max_font_cache:
                removed_key, removed_font = cls._font_cache.popitem(last=False)
                del removed_font  # 显式删除
            
            cls._font_cache[cache_key] = font
            return font
        except Exception as e:
            print(f"[字体缓存] 字体加载失败: {font_name}, 错误: {e}")
            return None
    
    @classmethod
    def clear_cache(cls):
        """清空所有缓存，释放内存"""
        cls._font_cache.clear()
        gc.collect()
        print(f"[性能优化] 缓存已清空，内存已释放")
    
    def parse_color(self, color_input: str) -> Tuple[int, int, int]:
        """解析颜色输入（支持十六进制和十进制）
        
        支持的格式：
        - 十六进制：#FFFFFF 或 FFFFFF
        - 十进制：16777215
        """
        if not color_input:
            return (255, 255, 255)
        
        try:
            if isinstance(color_input, str):
                color_input = color_input.strip()
                
                # 十六进制格式
                if color_input.startswith('#') or any(c in 'abcdefABCDEF' for c in color_input):
                    hex_color = color_input.lstrip('#')
                    if len(hex_color) != 6:
                        raise ValueError(f"无效的十六进制颜色: {color_input}")
                    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
                else:
                    # 十进制格式
                    decimal_value = int(color_input)
                    if decimal_value < 0 or decimal_value > 16777215:
                        raise ValueError(f"颜色值超出范围: {decimal_value}")
                    r = (decimal_value >> 16) & 0xFF
                    g = (decimal_value >> 8) & 0xFF
                    b = decimal_value & 0xFF
                    return (r, g, b)
            elif isinstance(color_input, int):
                r = (color_input >> 16) & 0xFF
                g = (color_input >> 8) & 0xFF
                b = color_input & 0xFF
                return (r, g, b)
        except Exception as e:
            print(f"颜色解析失败: {color_input}, 错误: {e}, 使用默认白色")
            return (255, 255, 255)
        
        return (255, 255, 255)
    
    def get_position_preset(self, preset: str, width: int, height: int) -> Tuple[float, float]:
        """获取位置预设的X,Y百分比
        
        Args:
            preset: 位置预设名称
            width: 画布宽度
            height: 画布高度
        
        Returns:
            (X百分比, Y百分比)
        """
        presets = {
            "底部居中": (50.0, 85.0),
            "顶部居中": (50.0, 15.0),
            "中心": (50.0, 50.0),
            "左下角": (15.0, 85.0),
            "右下角": (85.0, 85.0),
            "左上角": (15.0, 15.0),
            "右上角": (85.0, 15.0),
            "左侧居中": (15.0, 50.0),
            "右侧居中": (85.0, 50.0),
            "底部三分之一": (50.0, 75.0),
            "顶部三分之一": (50.0, 25.0),
        }
        return presets.get(preset, (50.0, 85.0))
    
    def create_gradient_image_optimized(self, width: int, height: int, 
                                       start_rgb: Tuple[int, int, int],
                                       mid_rgb: Tuple[int, int, int],
                                       end_rgb: Tuple[int, int, int],
                                       gradient_type: str, intensity: float) -> Image.Image:
        """使用numpy创建高性能渐变图像（优化版）"""
        
        # 无渐变快速返回
        if gradient_type == "无":
            return Image.new('RGB', (width, height), start_rgb)
        
        # 创建坐标网格（优化内存分配）
        if gradient_type == "线性渐变":
            # 横向渐变
            x = np.linspace(0, intensity, width, dtype=np.float32)
            progress = np.clip(x, 0, 1)
            progress = np.broadcast_to(progress, (height, width))
            
        elif gradient_type == "径向渐变":
            # 径向渐变（优化计算）
            y, x = np.ogrid[:height, :width]
            center_y, center_x = height // 2, width // 2
            max_dist = np.sqrt(center_x**2 + center_y**2, dtype=np.float32)
            dist = np.sqrt((x - center_x)**2 + (y - center_y)**2, dtype=np.float32)
            progress = np.clip(dist / max_dist * intensity, 0, 1)
            
        elif gradient_type == "对角渐变":
            # 对角渐变
            y, x = np.ogrid[:height, :width]
            progress = (x / width + y / height) / 2 * intensity
            progress = np.clip(progress, 0, 1, dtype=np.float32)
        else:
            return Image.new('RGB', (width, height), start_rgb)
        
        # 向量化计算渐变颜色（更高效）
        rgb = np.zeros((height, width, 3), dtype=np.uint8)
        start_array = np.array(start_rgb, dtype=np.float32)
        mid_array = np.array(mid_rgb, dtype=np.float32)
        end_array = np.array(end_rgb, dtype=np.float32)
        
        # 前半段：开头→中间
        mask1 = progress < 0.5
        t1 = progress * 2
        for i in range(3):
            rgb[:, :, i] = np.where(mask1, 
                                   start_array[i] * (1 - t1) + mid_array[i] * t1,
                                   rgb[:, :, i])
        
        # 后半段：中间→末尾
        mask2 = progress >= 0.5
        t2 = (progress - 0.5) * 2
        for i in range(3):
            rgb[:, :, i] = np.where(mask2,
                                   mid_array[i] * (1 - t2) + end_array[i] * t2,
                                   rgb[:, :, i])
        
        gradient_img = Image.fromarray(rgb, mode='RGB')
        return gradient_img
    
    def create_gradient_text(self, text: str, font: ImageFont.FreeTypeFont, 
                           渐变效果: str, 开头颜色: str, 中间颜色: str, 末尾颜色: str, 
                           过渡强度: float, 排版方向: str = "横排", 字间距: int = 0,
                           字体粗细: str = "常规", align: str = "center",
                           visible_chars: int = -1) -> Image.Image:
        """创建渐变文字图像（全功能版 - 支持字体粗细、多行、Typing效果）"""
        
        # 计算文本尺寸
        temp_img = Image.new('RGBA', (1, 1))
        temp_draw = ImageDraw.Draw(temp_img)
        
        # 计算文本边界
        if 排版方向 == "竖排":
            chars = list(text.replace('\n', ''))
            char_info = []
            max_width = 0
            total_height = 0
            for char in chars:
                bbox = temp_draw.textbbox((0, 0), char, font=font)
                char_width = bbox[2] - bbox[0]
                char_height = bbox[3] - bbox[1]
                char_info.append((char, char_width, char_height))
                max_width = max(max_width, char_width)
                total_height += char_height
            text_width = max_width
            text_height = total_height + (len(chars) - 1) * max(0, 字间距)
        else:
            # 横排多行测量
            lines = text.split('\n')
            max_width = 0
            total_height = 0
            
            bbox = temp_draw.textbbox((0, 0), "A", font=font)
            line_height_default = bbox[3] - bbox[1]
            line_gap = int(line_height_default * 0.2)
            
            for i, line in enumerate(lines):
                if not line:
                    total_height += line_height_default
                else:
                    chars = list(line)
                    line_w = 0
                    line_h = 0
                    for char in chars:
                        bbox = temp_draw.textbbox((0, 0), char, font=font)
                        cw = bbox[2] - bbox[0]
                        ch = bbox[3] - bbox[1]
                        line_w += cw
                        line_h = max(line_h, ch)
                    
                    line_w += (len(chars) - 1) * max(0, 字间距)
                    max_width = max(max_width, line_w)
                    total_height += line_h
                
                if i < len(lines) - 1:
                    total_height += line_gap
            
            text_width = max_width
            text_height = total_height
        
        # 添加边距
        padding = 50
        canvas_width = text_width + padding * 2
        canvas_height = text_height + padding * 2
        
        # 解析颜色
        start_rgb = self.parse_color(开头颜色)
        mid_rgb = self.parse_color(中间颜色)
        end_rgb = self.parse_color(末尾颜色)
        
        if 渐变效果 == "无":
            text_img = Image.new('RGBA', (canvas_width, canvas_height), (0, 0, 0, 0))
            text_img = self._draw_text_with_bold(
                text_img, text, font, start_rgb + (255,),
                canvas_width, canvas_height, 字体粗细, 排版方向, 字间距, align, visible_chars
            )
            return text_img
        
        # 创建渐变背景（高性能numpy版本）
        gradient_img = self.create_gradient_image_optimized(
            text_width, text_height, start_rgb, mid_rgb, end_rgb, 
            渐变效果 if 排版方向 == "横排" else "线性渐变", 过渡强度
        )
        
        # 创建完整画布
        full_gradient = Image.new('RGBA', (canvas_width, canvas_height), (0, 0, 0, 0))
        full_gradient.paste(gradient_img, (padding, padding))
        full_gradient = full_gradient.convert('RGBA')
        
        text_mask = Image.new('L', (canvas_width, canvas_height), 0)
        text_mask = self._draw_text_with_bold(
            text_mask, text, font, 255,
            canvas_width, canvas_height, 字体粗细, 排版方向, 字间距, align, visible_chars
        )
        
        # 应用遮罩
        result = Image.new('RGBA', (canvas_width, canvas_height), (0, 0, 0, 0))
        result.paste(full_gradient, mask=text_mask)
        
        return result
    
    def create_vertical_text(self, text: str, font: ImageFont.FreeTypeFont, 
                           color: Tuple[int, int, int], 字间距: int = 0, 
                           bold_level: str = "常规") -> Image.Image:
        """创建竖排文字（支持字体粗细）"""
        chars = list(text.replace('\n', ''))
        
        # 计算尺寸
        temp_img = Image.new('RGBA', (1, 1))
        temp_draw = ImageDraw.Draw(temp_img)
        
        char_info = []
        max_width = 0
        total_height = 0
        
        for char in chars:
            bbox = temp_draw.textbbox((0, 0), char, font=font)
            char_width = bbox[2] - bbox[0]
            char_height = bbox[3] - bbox[1]
            char_info.append((char, char_width, char_height))
            max_width = max(max_width, char_width)
            total_height += char_height
        
        total_height += (len(chars) - 1) * max(0, 字间距)
        
        # 根据粗细级别添加额外边距
        padding_map = {"常规": 20, "粗体": 25, "特粗": 30, "超粗": 35}
        padding = padding_map.get(bold_level, 20)
        
        # 创建竖排文字图像
        vert_img = Image.new('RGBA', (max_width + padding, total_height + padding), (0, 0, 0, 0))
        vert_draw = ImageDraw.Draw(vert_img)
        
        y_offset = padding // 2
        for char, char_width, char_height in char_info:
            x_offset = (max_width - char_width) // 2 + padding // 2
            
            # 使用字体粗细功能（竖排文字逐字绘制）
            if bold_level == "常规":
                vert_draw.text((x_offset, y_offset), char, font=font, fill=color + (255,))
            elif bold_level == "粗体":
                # 绘制2次，微调位置
                offsets = [(0, 0), (1, 0), (0, 1), (1, 1)]
                for dx, dy in offsets:
                    vert_draw.text((x_offset + dx, y_offset + dy), char, font=font, fill=color + (255,))
            elif bold_level == "特粗":
                # 绘制4次，更大范围
                offsets = [(0, 0), (1, 0), (2, 0), (0, 1), (1, 1), (2, 1), (0, 2), (1, 2)]
                for dx, dy in offsets:
                    vert_draw.text((x_offset + dx, y_offset + dy), char, font=font, fill=color + (255,))
            elif bold_level == "超粗":
                # 绘制多次，环绕方式
                offsets = [(dx, dy) for dx in range(-1, 3) for dy in range(-1, 3)]
                for dx, dy in offsets:
                    vert_draw.text((x_offset + dx, y_offset + dy), char, font=font, fill=color + (255,))
            
            y_offset += char_height + max(0, 字间距)
        
        return vert_img
    
    def apply_animation_enhanced(self, frame_idx: int, effect_type: str, 
                                effect_duration: int, intensity: float, 
                                width: int = 0) -> Dict[str, Any]:
        """增强动画效果（优化版）"""
        
        # 淡出特殊处理
        if effect_type == "淡出" and frame_idx >= effect_duration:
            return {
                "opacity": 0.0, "offset_x": 0, "offset_y": 0,
                "scale": 1.0, "char_reveal": 1.0, "rotation": 0, "distortion": 0
            }
        
        if effect_type == "无" or frame_idx >= effect_duration:
            return {
                "opacity": 1.0, "offset_x": 0, "offset_y": 0,
                "scale": 1.0, "char_reveal": 1.0, "rotation": 0, "distortion": 0
            }
        
        progress = min(frame_idx / effect_duration, 1.0)
        ease_out = 1 - (1 - progress) ** 2
        ease_in_out = (math.sin((progress - 0.5) * math.pi) + 1) / 2
        
        # 增强动效
        if effect_type == "爆炸进入（增强）":
            scale = 1.0 + (1.5 * intensity * (1 - ease_out))
            opacity = ease_out
            rotation = int(720 * (1 - ease_out) * intensity)
            scatter = int((1 - ease_out) * 30 * intensity)
            offset_x = int(math.sin(progress * 12) * scatter)
            offset_y = int(math.cos(progress * 12) * scatter)
            return {
                "opacity": opacity, "offset_x": offset_x, "offset_y": offset_y,
                "scale": scale, "char_reveal": 1.0, "rotation": rotation, "distortion": 0
            }
        
        elif effect_type == "螺旋出现（增强）":
            angle = progress * math.pi * 4 * intensity
            radius = 200 * (1 - ease_out) * intensity
            offset_x = int(math.cos(angle) * radius)
            offset_y = int(math.sin(angle) * radius)
            rotation = int(progress * 720 * intensity)
            return {
                "opacity": ease_out, "offset_x": offset_x, "offset_y": offset_y,
                "scale": ease_out, "char_reveal": 1.0, "rotation": rotation, "distortion": 0
            }
        
        elif effect_type == "粒子聚合（增强）":
            scatter = (1 - ease_out) * 300 * intensity
            offset_x = int(math.sin(progress * 10) * scatter)
            offset_y = int(math.cos(progress * 10) * scatter)
            return {
                "opacity": ease_out, "offset_x": offset_x, "offset_y": offset_y,
                "scale": 0.3 + ease_out * 0.7, "char_reveal": 1.0, "rotation": 0, 
                "distortion": int((1-ease_out) * 20 * intensity)
            }
        
        elif effect_type == "光速飞入（增强）":
            offset_x = -int((1 - progress) ** 3 * width * 2 * intensity)
            scale = 0.2 + ease_out * 0.8
            return {
                "opacity": min(progress * 2, 1.0), "offset_x": offset_x, "offset_y": 0,
                "scale": scale, "char_reveal": 1.0, "rotation": 0, 
                "distortion": int((1-ease_out) * 30 * intensity)
            }
        
        elif effect_type == "弹簧抖动（增强）":
            freq = 8 * intensity
            damp = ease_out
            shake = math.sin(progress * math.pi * freq) * (1 - damp) * 30 * intensity
            return {
                "opacity": min(progress * 1.5, 1.0), "offset_x": int(shake), 
                "offset_y": int(shake * 0.5), "scale": 1.0, "char_reveal": 1.0, 
                "rotation": int(shake), "distortion": 0
            }
        
        elif effect_type == "翻书效果（增强）":
            if progress < 0.5:
                rotation_y = progress * 180 * intensity
                scale_x = math.cos(math.radians(rotation_y))
            else:
                rotation_y = 180 - (progress - 0.5) * 180 * intensity
                scale_x = -math.cos(math.radians(rotation_y))
            return {
                "opacity": 1.0, "offset_x": 0, "offset_y": 0,
                "scale": max(abs(scale_x), 0.1), "char_reveal": 1.0, 
                "rotation": 0, "distortion": 0
            }
        
        elif effect_type == "液体流动（增强）":
            wave = math.sin(progress * math.pi * 3) * 20 * intensity * (1 - ease_out)
            return {
                "opacity": ease_out, "offset_x": 0, "offset_y": int(wave),
                "scale": 0.8 + ease_out * 0.2, "char_reveal": 1.0, "rotation": 0,
                "distortion": int(abs(wave))
            }
        
        elif effect_type == "闪电出现（增强）":
            if progress < 0.7:
                flash_count = 5
                flash_progress = (progress / 0.7 * flash_count) % 1.0
                opacity = 1.0 if flash_progress > 0.5 else 0.0
            else:
                opacity = 1.0
            jitter = (1 - ease_out) * 15 * intensity
            offset_x = int(math.sin(progress * 50) * jitter)
            offset_y = int(math.cos(progress * 50) * jitter)
            return {
                "opacity": opacity, "offset_x": offset_x, "offset_y": offset_y,
                "scale": 1.0, "char_reveal": 1.0, "rotation": 0, "distortion": 0
            }
        
        elif effect_type == "碎片重组（增强）":
            scatter_x = int(math.sin(progress * 20) * (1 - ease_out) * 150 * intensity)
            scatter_y = int(math.cos(progress * 15) * (1 - ease_out) * 150 * intensity)
            rotation = int((1 - ease_out) * 360 * intensity)
            return {
                "opacity": ease_out, "offset_x": scatter_x, "offset_y": scatter_y,
                "scale": 0.5 + ease_out * 0.5, "char_reveal": 1.0, "rotation": rotation,
                "distortion": int((1-ease_out) * 25 * intensity)
            }
        
        # 基础动效
        elif effect_type == "淡入":
            return {
                "opacity": ease_out, "offset_x": 0, "offset_y": 0,
                "scale": 1.0, "char_reveal": 1.0, "rotation": 0, "distortion": 0
            }
        
        elif effect_type == "淡出":
            return {
                "opacity": 1.0 - ease_out, "offset_x": 0, "offset_y": 0,
                "scale": 1.0, "char_reveal": 1.0, "rotation": 0, "distortion": 0
            }
        
        elif effect_type == "滚动下降":
            offset_y = int((1 - ease_out) * 100 * intensity)
            return {
                "opacity": ease_out, "offset_x": 0, "offset_y": -offset_y,
                "scale": 1.0, "char_reveal": 1.0, "rotation": 0, "distortion": 0
            }
        
        elif effect_type == "滚动上升":
            offset_y = int((1 - ease_out) * 100 * intensity)
            return {
                "opacity": ease_out, "offset_x": 0, "offset_y": offset_y,
                "scale": 1.0, "char_reveal": 1.0, "rotation": 0, "distortion": 0
            }
        
        elif effect_type == "打字机":
            return {
                "opacity": 1.0, "offset_x": 0, "offset_y": 0,
                "scale": 1.0, "char_reveal": ease_out, "rotation": 0, "distortion": 0
            }
        
        elif effect_type == "缩放出现":
            scale = 0.3 + ease_out * 0.7
            return {
                "opacity": ease_out, "offset_x": 0, "offset_y": 0,
                "scale": scale, "char_reveal": 1.0, "rotation": 0, "distortion": 0
            }
        
        elif effect_type == "左飞入":
            offset_x = -int((1 - ease_out) * width * intensity)
            return {
                "opacity": ease_out, "offset_x": offset_x, "offset_y": 0,
                "scale": 1.0, "char_reveal": 1.0, "rotation": 0, "distortion": 0
            }
        
        elif effect_type == "右飞入":
            offset_x = int((1 - ease_out) * width * intensity)
            return {
                "opacity": ease_out, "offset_x": offset_x, "offset_y": 0,
                "scale": 1.0, "char_reveal": 1.0, "rotation": 0, "distortion": 0
            }
        
        elif effect_type == "上飞入":
            offset_y = -int((1 - ease_out) * 200 * intensity)
            return {
                "opacity": ease_out, "offset_x": 0, "offset_y": offset_y,
                "scale": 1.0, "char_reveal": 1.0, "rotation": 0, "distortion": 0
            }
        
        elif effect_type == "下飞入":
            offset_y = int((1 - ease_out) * 200 * intensity)
            return {
                "opacity": ease_out, "offset_x": 0, "offset_y": offset_y,
                "scale": 1.0, "char_reveal": 1.0, "rotation": 0, "distortion": 0
            }
        
        elif effect_type == "弹跳出现":
            bounce = abs(math.sin(progress * math.pi * 3)) * (1 - ease_out) * 50 * intensity
            return {
                "opacity": ease_out, "offset_x": 0, "offset_y": -int(bounce),
                "scale": 1.0, "char_reveal": 1.0, "rotation": 0, "distortion": 0
            }
        
        elif effect_type == "旋转淡入":
            rotation = int((1 - ease_out) * 360 * intensity)
            return {
                "opacity": ease_out, "offset_x": 0, "offset_y": 0,
                "scale": ease_out, "char_reveal": 1.0, "rotation": rotation, "distortion": 0
            }
        
        elif effect_type == "波浪效果":
            wave = math.sin(progress * math.pi * 4) * 30 * intensity
            return {
                "opacity": 1.0, "offset_x": 0, "offset_y": int(wave),
                "scale": 1.0, "char_reveal": 1.0, "rotation": 0, "distortion": 0
            }
        
        elif effect_type == "闪烁":
            flash = 1.0 if (int(progress * 10) % 2 == 0) else 0.3
            return {
                "opacity": flash, "offset_x": 0, "offset_y": 0,
                "scale": 1.0, "char_reveal": 1.0, "rotation": 0, "distortion": 0
            }
        
        elif effect_type == "抖动出现":
            jitter = (1 - ease_out) * 10 * intensity
            offset_x = int(math.sin(progress * 50) * jitter)
            offset_y = int(math.cos(progress * 50) * jitter)
            return {
                "opacity": ease_out, "offset_x": offset_x, "offset_y": offset_y,
                "scale": 1.0, "char_reveal": 1.0, "rotation": 0, "distortion": 0
            }
        
        elif effect_type == "渐进放大":
            scale = 0.1 + ease_out * 0.9
            return {
                "opacity": ease_out, "offset_x": 0, "offset_y": 0,
                "scale": scale, "char_reveal": 1.0, "rotation": 0, "distortion": 0
            }
        
        elif effect_type == "分裂合并":
            if progress < 0.5:
                spread = (0.5 - progress) * 200 * intensity
            else:
                spread = (progress - 0.5) * 200 * intensity
            offset_x = int(math.sin(progress * 10) * spread)
            return {
                "opacity": ease_out, "offset_x": offset_x, "offset_y": 0,
                "scale": 1.0, "char_reveal": 1.0, "rotation": 0, "distortion": 0
            }
        
        elif effect_type == "弹性进入":
            if progress < 0.5:
                elastic = progress * 2
            else:
                elastic = 1.0 + math.sin((progress - 0.5) * math.pi * 4) * (1 - progress) * 0.3
            scale = 0.5 + elastic * 0.5
            return {
                "opacity": min(progress * 1.5, 1.0), "offset_x": 0, "offset_y": 0,
                "scale": scale, "char_reveal": 1.0, "rotation": 0, "distortion": 0
            }
        
        elif effect_type == "3D翻转":
            rotation = int(progress * 180 * intensity)
            scale = abs(math.cos(math.radians(rotation)))
            scale = max(scale, 0.1)
            return {
                "opacity": 1.0, "offset_x": 0, "offset_y": 0,
                "scale": scale, "char_reveal": 1.0, "rotation": rotation, "distortion": 0
            }
        
        # 默认无动效
        return {
            "opacity": 1.0, "offset_x": 0, "offset_y": 0, 
            "scale": 1.0, "char_reveal": 1.0, "rotation": 0, "distortion": 0
        }
    
    def create_bold_text(self, draw: ImageDraw.ImageDraw, position: Tuple[int, int], 
                        text: str, font: ImageFont.FreeTypeFont, 
                        fill: Tuple[int, int, int, int], bold_level: str):
        """创建加粗文字（优化版）"""
        x, y = position
        
        if bold_level == "常规":
            draw.text((x, y), text, font=font, fill=fill, anchor='mm')
        elif bold_level == "粗体":
            offsets = [(0, 0), (1, 0), (0, 1), (1, 1)]
            for dx, dy in offsets:
                draw.text((x + dx, y + dy), text, font=font, fill=fill, anchor='mm')
        elif bold_level == "特粗":
            offsets = [(0, 0), (1, 0), (2, 0), (0, 1), (1, 1), (2, 1), (0, 2), (1, 2)]
            for dx, dy in offsets:
                draw.text((x + dx, y + dy), text, font=font, fill=fill, anchor='mm')
        elif bold_level == "超粗":
            offsets = [(dx, dy) for dx in range(-1, 3) for dy in range(-1, 3)]
            for dx, dy in offsets:
                draw.text((x + dx, y + dy), text, font=font, fill=fill, anchor='mm')
    
    def create_stroke_text(self, text: str, font: ImageFont.FreeTypeFont, 
                          text_color: Tuple[int, int, int], 
                          stroke_color: Tuple[int, int, int], 
                          stroke_size: int, stroke_position: str, 
                          stroke_opacity: float, width: int, height: int, 
                          字间距: int = 0, 排版方向: str = "横排", 
                          字体粗细: str = "常规", align: str = "center",
                          visible_chars: int = -1) -> Image.Image:
        """创建描边文字（全功能版 - 支持横竖排+字体粗细）"""
        
        text_layer = Image.new('RGBA', (width, height), (0, 0, 0, 0))
        
        # 映射对齐方式
        pil_align = "left"
        if align == "居中" or align == "center":
            pil_align = "center"
        elif align == "左对齐" or align == "left":
            pil_align = "left"
        elif align == "右对齐" or align == "right":
            pil_align = "right"
        
        if stroke_size == 0:
            # 无描边，直接绘制文字（支持粗细和排版）
            return self._draw_text_with_bold(text_layer, text, font, text_color + (255,), 
                                            width, height, 字体粗细, 排版方向, 字间距, pil_align, visible_chars)
        
        stroke_rgba = stroke_color + (int(255 * stroke_opacity),)
        
        # 创建描边层
        stroke_layer = Image.new('RGBA', (width, height), (0, 0, 0, 0))
        stroke_draw = ImageDraw.Draw(stroke_layer)
        
        center_x = width // 2
        center_y = height // 2
        
        # 动态采样密度
        angle_step = 10 if stroke_size <= 5 else 15
        
        # 预计算偏移量
        offsets = []
        for angle in range(0, 360, int(angle_step)):
            rad = math.radians(angle)
            cos_val = math.cos(rad)
            sin_val = math.sin(rad)
            for distance in range(1, stroke_size + 1):
                offset_x = int(cos_val * distance)
                offset_y = int(sin_val * distance)
                if (offset_x, offset_y) not in offsets:
                    offsets.append((offset_x, offset_y))

        if 排版方向 == "竖排":
            # 竖排描边 - 逐字符绘制
            chars = list(text.replace('\n', ''))
            temp_img = Image.new('RGBA', (1, 1))
            temp_draw = ImageDraw.Draw(temp_img)
            
            # 计算竖排尺寸
            char_heights = []
            max_width = 0
            for char in chars:
                bbox = temp_draw.textbbox((0, 0), char, font=font)
                char_width = bbox[2] - bbox[0]
                char_height = bbox[3] - bbox[1]
                char_heights.append(char_height)
                max_width = max(max_width, char_width)
            
            total_height = sum(char_heights) + (len(chars) - 1) * max(0, 字间距)
            start_y = (height - total_height) // 2
            y_offset = start_y
            
            # 绘制竖排描边
            for i, (char, char_height) in enumerate(zip(chars, char_heights)):
                if visible_chars >= 0 and i >= visible_chars:
                    break
                for offset_x, offset_y in offsets:
                    # 绘制描边（支持粗细）
                    if 字体粗细 == "常规":
                        stroke_draw.text((center_x + offset_x, y_offset + offset_y), 
                                       char, font=font, fill=stroke_rgba, anchor='mm')
                    else:
                        self.create_bold_text(stroke_draw, (center_x + offset_x, y_offset + offset_y), 
                                           char, font, stroke_rgba, 字体粗细, anchor='mm')
                
                y_offset += char_height + max(0, 字间距)
        else:
            # 横排描边 (使用 _calculate_multiline_metrics 统一处理)
            char_positions, _, _ = self._calculate_multiline_metrics(stroke_draw, text, font, 字间距, pil_align, width, height)
            
            # 绘制描边
            for offset_x, offset_y in offsets:
                for i, (char, x, y) in enumerate(char_positions):
                    if visible_chars >= 0 and i >= visible_chars:
                        break
                    if 字体粗细 == "常规":
                        stroke_draw.text((x + offset_x, y + offset_y), char, font=font, fill=stroke_rgba, anchor='mm')
                    else:
                        self.create_bold_text(stroke_draw, (x + offset_x, y + offset_y), char, font, stroke_rgba, 字体粗细, anchor='mm')
        
        # 根据描边位置合成
        if stroke_position == "外部":
            # 外部描边：先描边，后文字
            text_layer = Image.alpha_composite(text_layer, stroke_layer)
            text_layer = self._draw_text_with_bold(text_layer, text, font, text_color + (255,), 
                                                   width, height, 字体粗细, 排版方向, 字间距, pil_align, visible_chars)
        elif stroke_position == "居中":
            # 居中描边：描边和文字混合
            text_layer = Image.alpha_composite(text_layer, stroke_layer)
            text_layer = self._draw_text_with_bold(text_layer, text, font, text_color + (255,), 
                                                   width, height, 字体粗细, 排版方向, 字间距, pil_align, visible_chars)
        else:  # 内部
            # 内部描边：先文字，后用文字遮罩裁剪描边
            text_mask = Image.new('L', (width, height), 0)
            text_mask = self._draw_text_with_bold(text_mask, text, font, 255, 
                                                  width, height, 字体粗细, 排版方向, 字间距, pil_align, visible_chars)
            stroke_layer.putalpha(text_mask.split()[0] if text_mask.mode == 'L' else text_mask)
            text_layer = self._draw_text_with_bold(text_layer, text, font, text_color + (255,), 
                                                   width, height, 字体粗细, 排版方向, 字间距, pil_align, visible_chars)
            text_layer = Image.alpha_composite(text_layer, stroke_layer)
        
        return text_layer
    
    def _calculate_multiline_metrics(self, draw, text, font, spacing, align, width, height):
        """辅助函数：计算多行文字每个字符的位置"""
        lines = text.split('\n')
        line_metrics = []
        max_block_width = 0
        total_text_height = 0
        
        bbox = draw.textbbox((0, 0), "A", font=font)
        default_line_height = bbox[3] - bbox[1]
        line_gap = int(default_line_height * 0.2) # 行间距
        
        # 第一遍：计算尺寸
        for i, line in enumerate(lines):
            if not line:
                line_metrics.append({'chars': [], 'width': 0, 'height': default_line_height})
                total_text_height += default_line_height
            else:
                chars = list(line)
                char_widths = []
                max_line_height = 0
                for char in chars:
                    bbox = draw.textbbox((0, 0), char, font=font)
                    char_widths.append(bbox[2] - bbox[0])
                    max_line_height = max(max_line_height, bbox[3] - bbox[1])
                
                total_line_width = sum(char_widths) + (len(chars) - 1) * max(0, spacing)
                line_metrics.append({
                    'chars': chars,
                    'char_widths': char_widths,
                    'width': total_line_width,
                    'height': max_line_height
                })
                max_block_width = max(max_block_width, total_line_width)
                total_text_height += max_line_height
            
            if i < len(lines) - 1:
                total_text_height += line_gap

        # 垂直居中起始Y
        current_y = (height - total_text_height) // 2
        
        # 块级水平位置（默认居中于画布）
        block_start_x = (width - max_block_width) // 2
        
        char_positions = []
        
        # 第二遍：计算位置
        for metric in line_metrics:
            if not metric['chars']:
                current_y += metric['height'] + line_gap
                continue
            
            # 计算当前行X
            if align == 'center':
                start_x = (width - metric['width']) // 2
            elif align == 'right':
                start_x = block_start_x + (max_block_width - metric['width'])
            else: # left
                start_x = block_start_x
            
            current_x = start_x
            for char, char_w in zip(metric['chars'], metric['char_widths']):
                char_center_x = current_x + char_w // 2
                char_center_y = current_y + metric['height'] // 2
                char_positions.append((char, char_center_x, char_center_y))
                current_x += char_w + max(0, spacing)
            
            current_y += metric['height'] + line_gap
            
        return char_positions, max_block_width, total_text_height

    def _draw_multiline_text_with_spacing(self, draw, text, font, fill, width, height, spacing, align, bold_level, visible_chars=-1):
        """辅助函数：绘制多行带字间距文字"""
        char_positions, _, _ = self._calculate_multiline_metrics(draw, text, font, spacing, align, width, height)
        
        for i, (char, x, y) in enumerate(char_positions):
            if visible_chars >= 0 and i >= visible_chars:
                break
                
            if bold_level == "常规":
                draw.text((x, y), char, font=font, fill=fill, anchor='mm')
            else:
                self.create_bold_text(draw, (x, y), char, font, fill, bold_level, anchor='mm')

    def _draw_text_with_bold(self, layer, text: str, font: ImageFont.FreeTypeFont, 
                            fill, width: int, height: int, bold_level: str, 
                            direction: str, spacing: int, align: str = "center",
                            visible_chars: int = -1):
        """辅助函数：绘制支持粗细和排版的文字"""
        draw = ImageDraw.Draw(layer)
        center_x = width // 2
        center_y = height // 2
        
        if direction == "竖排":
            # 竖排
            chars = list(text.replace('\n', ''))
            temp_img = Image.new('RGBA', (1, 1))
            temp_draw = ImageDraw.Draw(temp_img)
            
            char_heights = []
            for char in chars:
                bbox = temp_draw.textbbox((0, 0), char, font=font)
                char_heights.append(bbox[3] - bbox[1])
            
            total_height = sum(char_heights) + (len(chars) - 1) * max(0, spacing)
            y_offset = (height - total_height) // 2
            
            for i, (char, char_height) in enumerate(zip(chars, char_heights)):
                if visible_chars >= 0 and i >= visible_chars:
                    break
                if bold_level == "常规":
                    draw.text((center_x, y_offset + char_height//2), char, font=font, fill=fill, anchor='mm')
                else:
                    self.create_bold_text(draw, (center_x, y_offset + char_height//2), char, font, fill, bold_level, anchor='mm')
                y_offset += char_height + max(0, spacing)
        else:
            # 横排
            if spacing != 0:
                self._draw_multiline_text_with_spacing(draw, text, font, fill, width, height, spacing, align, bold_level, visible_chars)
            else:
                # 无字间距时，整体绘制（注意：这里如果是多行且无字间距，可能无法正确应用typing效果）
                # 为了支持typing效果，即使字间距为0，也建议走multiline逻辑
                # 但为了保持兼容性，如果visible_chars被设置，我们强制走multiline逻辑
                if visible_chars >= 0 or '\n' in text:
                    self._draw_multiline_text_with_spacing(draw, text, font, fill, width, height, spacing, align, bold_level, visible_chars)
                else:
                    if bold_level == "常规":
                        draw.text((center_x, center_y), text, font=font, fill=fill, anchor='mm', align=align)
                    else:
                        self.create_bold_text(draw, (center_x, center_y), text, font, fill, bold_level, align=align, anchor='mm')
        
        return layer
    
    def _draw_bold_char(self, draw, position: Tuple[int, int], char: str, 
                       font: ImageFont.FreeTypeFont, fill, bold_level: str):
        """辅助函数：绘制单个粗体字符"""
        x, y = position
        
        if bold_level == "粗体":
            offsets = [(0, 0), (1, 0), (0, 1), (1, 1)]
        elif bold_level == "特粗":
            offsets = [(0, 0), (1, 0), (2, 0), (0, 1), (1, 1), (2, 1), (0, 2), (1, 2)]
        elif bold_level == "超粗":
            offsets = [(dx, dy) for dx in range(-1, 3) for dy in range(-1, 3)]
        else:
            offsets = [(0, 0)]
        
        for dx, dy in offsets:
            draw.text((x + dx, y + dy), char, font=font, fill=fill)
    
    def calculate_optimal_font_size(self, text: str, font_name: str, initial_size: int,
                                    canvas_width: int, canvas_height: int, 
                                    stroke_size: int, 字间距: int, 排版方向: str) -> int:
        """计算最适合画布的字号
        
        Args:
            text: 字幕文本
            font_name: 字体名称
            initial_size: 初始字号
            canvas_width: 画布宽度
            canvas_height: 画布高度
            stroke_size: 描边大小
            字间距: 字间距
            排版方向: 排版方向
        
        Returns:
            最适合的字号
        """
        # 留5%边距
        max_width = int(canvas_width * 0.95)
        max_height = int(canvas_height * 0.95)
        
        # 从初始字号开始尝试
        test_size = initial_size
        
        for _ in range(20):  # 最多尝试20次
            font = self.get_cached_font(font_name, test_size)
            if font is None:
                break
            
            # 创建临时图像测量尺寸
            temp_img = Image.new('RGBA', (1, 1))
            temp_draw = ImageDraw.Draw(temp_img)
            
            # 计算文本边界（包括描边和字间距）
            if 排版方向 == "竖排":
                chars = list(text.replace('\n', ''))
                max_char_width = 0
                total_height = 0
                for char in chars:
                    bbox = temp_draw.textbbox((0, 0), char, font=font)
                    char_width = bbox[2] - bbox[0]
                    char_height = bbox[3] - bbox[1]
                    max_char_width = max(max_char_width, char_width)
                    total_height += char_height
                total_height += (len(chars) - 1) * max(0, 字间距)
                text_width = max_char_width + stroke_size * 2
                text_height = total_height + stroke_size * 2
            else:
                if 字间距 != 0:
                    chars = list(text.replace('\n', ''))
                    total_width = 0
                    max_height = 0
                    for char in chars:
                        bbox = temp_draw.textbbox((0, 0), char, font=font)
                        total_width += bbox[2] - bbox[0]
                        max_height = max(max_height, bbox[3] - bbox[1])
                    total_width += (len(chars) - 1) * max(0, 字间距)
                    text_width = total_width + stroke_size * 2
                    text_height = max_height + stroke_size * 2
                else:
                    bbox = temp_draw.textbbox((0, 0), text, font=font)
                    text_width = bbox[2] - bbox[0] + stroke_size * 2
                    text_height = bbox[3] - bbox[1] + stroke_size * 2
            
            # 检查是否适合
            if text_width <= max_width and text_height <= max_height:
                # 适合，返回此字号
                return test_size
            
            # 不适合，缩小字号
            scale = min(max_width / text_width, max_height / text_height)
            test_size = max(12, int(test_size * scale * 0.95))  # 最小12px
            
            # 如果字号变化太小，结束循环
            if abs(test_size - int(initial_size * scale)) < 2:
                break
        
        return test_size
    
    def constrain_to_canvas_by_char(self, text_img: Image.Image, paste_x: int, paste_y: int,
                                     canvas_width: int, canvas_height: int) -> Tuple[Image.Image, int, int]:
        """按字裁剪：只保留完全在画布内的字符，超出边界的字整个不显示
        
        Args:
            text_img: 文字图像
            paste_x: 粘贴X位置
            paste_y: 粘贴Y位置
            canvas_width: 画布宽度
            canvas_height: 画布高度
        
        Returns:
            裁剪后的图像和新的粘贴位置
        """
        if text_img.mode != 'RGBA':
            text_img = text_img.convert('RGBA')
        
        # 获取alpha通道
        alpha = np.array(text_img.split()[3])
        
        # 如果完全在画布内，直接返回
        if (paste_x >= 0 and paste_y >= 0 and 
            paste_x + text_img.width <= canvas_width and 
            paste_y + text_img.height <= canvas_height):
            return text_img, paste_x, paste_y
        
        # 检测每列和每行的内容
        has_content_cols = np.any(alpha > 30, axis=0)  # 每列是否有内容
        has_content_rows = np.any(alpha > 30, axis=1)  # 每行是否有内容
        
        # 找到所有内容块的列范围（字符区域）
        char_regions = []
        in_region = False
        start_col = 0
        
        for col in range(len(has_content_cols)):
            if has_content_cols[col] and not in_region:
                # 开始一个新区域
                start_col = col
                in_region = True
            elif not has_content_cols[col] and in_region:
                # 结束当前区域
                char_regions.append((start_col, col))
                in_region = False
        
        if in_region:
            char_regions.append((start_col, len(has_content_cols)))
        
        # 检查每个字符区域是否完全在画布内
        valid_regions = []
        for start_col, end_col in char_regions:
            # 计算这个字符区域在画布上的实际位置
            char_left = paste_x + start_col
            char_right = paste_x + end_col
            
            # 判断是否完全在画布内（水平方向）
            if char_left >= 0 and char_right <= canvas_width:
                # 再检查垂直方向
                # 找到这个字符区域的上下边界
                char_alpha = alpha[:, start_col:end_col]
                rows_with_content = np.any(char_alpha > 30, axis=1)
                if np.any(rows_with_content):
                    top_row = np.where(rows_with_content)[0][0]
                    bottom_row = np.where(rows_with_content)[0][-1] + 1
                    
                    # 检查垂直方向是否完全在画布内
                    char_top = paste_y + top_row
                    char_bottom = paste_y + bottom_row
                    
                    if char_top >= 0 and char_bottom <= canvas_height:
                        valid_regions.append((start_col, end_col))
        
        if not valid_regions:
            # 没有完全在画布内的字符，返回空图像
            print(f"[按字裁剪] 所有字符都超出边界，已隐藏")
            empty_img = Image.new('RGBA', (1, 1), (0, 0, 0, 0))
            return empty_img, paste_x, paste_y
        
        # 创建只包含有效字符的新图像
        # 找到所有有效区域的总范围
        min_col = min(r[0] for r in valid_regions)
        max_col = max(r[1] for r in valid_regions)
        
        # 创建掩码
        mask = np.zeros_like(alpha)
        for start_col, end_col in valid_regions:
            mask[:, start_col:end_col] = alpha[:, start_col:end_col]
        
        # 应用掩码
        new_img = Image.new('RGBA', text_img.size, (0, 0, 0, 0))
        new_img_array = np.array(new_img)
        text_img_array = np.array(text_img)
        
        # 只保留有效区域的像素
        for c in range(4):
            new_img_array[:, :, c] = np.where(mask > 0, text_img_array[:, :, c], 0)
        
        new_img = Image.fromarray(new_img_array, 'RGBA')
        
        removed_chars = len(char_regions) - len(valid_regions)
        print(f"[按字裁剪] 检测到 {len(char_regions)} 个字符，保留 {len(valid_regions)} 个，裁剪 {removed_chars} 个")
        
        return new_img, paste_x, paste_y
    
    def constrain_to_canvas_crop(self, text_img: Image.Image, paste_x: int, paste_y: int,
                                 canvas_width: int, canvas_height: int) -> Tuple[Image.Image, int, int]:
        """裁剪超出画布的字幕边缘（已废弃，保留用于兼容）
        
        Args:
            text_img: 文字图像
            paste_x: 粘贴X位置
            paste_y: 粘贴Y位置
            canvas_width: 画布宽度
            canvas_height: 画布高度
        
        Returns:
            裁剪后的图像和新的粘贴位置
        """
        text_width = text_img.width
        text_height = text_img.height
        
        # 裁剪超出画布的部分
        crop_left = max(0, -paste_x)
        crop_top = max(0, -paste_y)
        crop_right = min(text_width, canvas_width - paste_x)
        crop_bottom = min(text_height, canvas_height - paste_y)
        
        if crop_left > 0 or crop_top > 0 or crop_right < text_width or crop_bottom < text_height:
            # 需要裁剪
            if crop_right > crop_left and crop_bottom > crop_top:
                text_img = text_img.crop((crop_left, crop_top, crop_right, crop_bottom))
                paste_x = max(0, paste_x)
                paste_y = max(0, paste_y)
                print(f"[画布限定] 裁剪边缘: 从 {text_width}x{text_height} 裁剪到 {text_img.width}x{text_img.height}")
            else:
                # 完全超出画布，返回空图像
                text_img = Image.new('RGBA', (1, 1), (0, 0, 0, 0))
                print(f"[画布限定] 字幕完全超出画布范围")
        
        return text_img, paste_x, paste_y
    
    def create_projection(self, text_img: Image.Image, angle: int, 
                         distance: int, intensity: float, blur: int) -> Image.Image:
        """创建投影（优化版）"""
        if distance == 0 or intensity == 0:
            return Image.new('RGBA', text_img.size, (0, 0, 0, 0))
        
        angle_rad = math.radians(angle)
        offset_x = int(math.cos(angle_rad) * distance)
        offset_y = int(math.sin(angle_rad) * distance)
        
        # 提取alpha通道并调整强度
        shadow_alpha = text_img.split()[3]
        shadow_alpha = shadow_alpha.point(lambda p: int(p * intensity))
        
        # 创建黑色阴影
        black_img = Image.new('RGB', text_img.size, (0, 0, 0))
        shadow = black_img.convert('RGBA')
        shadow.putalpha(shadow_alpha)
        
        # 应用高斯模糊
        if blur > 0:
            shadow = shadow.filter(ImageFilter.GaussianBlur(radius=blur))
        
        # 创建偏移的投影
        result = Image.new('RGBA', text_img.size, (0, 0, 0, 0))
        result.paste(shadow, (offset_x, offset_y), shadow)
        
        return result
    
    def remove_punctuation(self, text: str, mode: str) -> str:
        """去除标点符号
        
        Args:
            text: 输入文本
            mode: 去除模式（不去除、中文标点、英文标点、所有标点、所有符号）
        
        Returns:
            处理后的文本
        """
        if mode == "不去除":
            return text
        
        if mode == "中文标点":
            chinese_punctuation = "，。！？、；：""''（）【】《》〈〉「」『』〔〕…—·～"
            for punct in chinese_punctuation:
                text = text.replace(punct, "")
        
        elif mode == "英文标点":
            english_punctuation = ",.!?;:'\"()[]<>{}-"
            for punct in english_punctuation:
                text = text.replace(punct, "")
        
        elif mode == "所有标点":
            all_punctuation = "，。！？、；：""''（）【】《》〈〉「」『』〔〕…—·～,.!?;:'\"()[]<>{}-"
            for punct in all_punctuation:
                text = text.replace(punct, "")
        
        elif mode == "所有符号":
            text = re.sub(r'[^\u4e00-\u9fa5a-zA-Z0-9\s\n]', '', text)
        
        return text
    
    def wrap_text_smart(self, text: str, font: ImageFont.FreeTypeFont, max_width: int, max_lines: int) -> str:
        """智能文本换行"""
        if max_lines <= 1 or not text or '\n' in text:
            return text
            
        try:
            # 使用临时画布测量宽度
            draw = ImageDraw.Draw(Image.new('L', (1, 1)))
            bbox = draw.textbbox((0, 0), text, font=font)
            text_width = bbox[2] - bbox[0]
        except:
            return text
            
        if text_width <= max_width:
            return text
            
        # 计算需要的行数
        num_lines = min(max_lines, math.ceil(text_width / max_width))
        if num_lines <= 1:
            return text
            
        # 均匀分割
        length = len(text)
        chunk_size = math.ceil(length / num_lines)
        lines = [text[i:i+chunk_size] for i in range(0, length, chunk_size)]
        
        return "\n".join(lines)

    def add_subtitle(self, images, 字幕文本,
                    字体选择, 字体大小, 最大行数, 字体粗细, 字体颜色, 不透明度,
                    描边大小, 描边颜色, 描边位置, 描边不透明度,
                    投影角度, 投影距离, 投影强度, 投影模糊,
                    位置预设, 文字对齐, 位置X百分比, 位置Y百分比, 排版方向, 字体角度,
                    渐变效果, 渐变开头颜色, 渐变中间颜色, 渐变末尾颜色, 渐变过渡强度,
                    动效类型, 动效强度, 动效时长, 动效速度调节,
                    开始时间, 结束时间, 时间单位, 视频帧率,
                    字间距, 去除标点符号, 限定在画布内):
        """添加字幕（v2.6.0 - 新增去除标点符号功能）"""
        
        # 输入验证
        if not 字幕文本 or not 字幕文本.strip():
            print("警告: 字幕文本为空，跳过处理")
            return (images, 开始时间, 结束时间)
        
        # 应用去除标点符号功能
        if 去除标点符号 != "不去除":
            原始文本 = 字幕文本
            字幕文本 = self.remove_punctuation(字幕文本, 去除标点符号)
            if 字幕文本 != 原始文本:
                print(f"[去除标点] 模式:{去除标点符号}, 原长度:{len(原始文本)}, 新长度:{len(字幕文本)}")
        
        batch_size = images.shape[0]
        height = images.shape[1]
        width = images.shape[2]
        
        video_duration_seconds = round(batch_size / 视频帧率, 2)
        
        # 时间计算
        if 时间单位 == "秒数":
            start_frame = int(开始时间 * 视频帧率)
            end_frame = int(结束时间 * 视频帧率) if 结束时间 > 0 else batch_size
            动效时长帧数 = max(1, int(动效时长 * 视频帧率 / 动效速度调节))
        else:
            start_frame = int(开始时间)
            end_frame = int(结束时间) if 结束时间 > 0 else batch_size
            动效时长帧数 = max(1, int(动效时长 / 动效速度调节))
        
        end_frame = min(end_frame, batch_size)
        
        # 智能换行处理
        if 最大行数 > 1 and 排版方向 == "横排":
            # 预先获取字体用于测量（使用初始字号）
            temp_font = self.get_cached_font(字体选择, 字体大小)
            if temp_font:
                # 留5%边距
                wrap_width = int(width * 0.9)
                print(f"[智能换行] 最大行数: {最大行数}, 限制宽度: {wrap_width}px")
                字幕文本 = self.wrap_text_smart(字幕文本, temp_font, wrap_width, 最大行数)
        
        # 如果启用自动缩放，先计算最优字号
        final_font_size = 字体大小
        if 限定在画布内 == "自动缩放":
            optimal_size = self.calculate_optimal_font_size(
                字幕文本, 字体选择, 字体大小, width, height, 
                描边大小, 字间距, 排版方向
            )
            if optimal_size != 字体大小:
                final_font_size = optimal_size
                print(f"[画布限定] 自动调整字号: {字体大小}px → {final_font_size}px")
        
        # 获取缓存字体
        font = self.get_cached_font(字体选择, final_font_size)
        if font is None:
            print("错误: 字体加载失败")
            return (images, 开始时间, 结束时间)
        
        # 预解析颜色
        text_color = self.parse_color(字体颜色)
        stroke_color = self.parse_color(描边颜色)
        
        output_images = []
        
        # 日志输出
        if 时间单位 == "秒数":
            print(f"[增强字幕] 秒数模式: 开始={开始时间:.2f}s(帧{start_frame}), "
                  f"结束={结束时间:.2f}s(帧{end_frame}), 总帧数={batch_size}")
            print(f"[增强字幕] 动效={动效类型}, 时长={动效时长:.2f}s({动效时长帧数}帧), "
                  f"强度={动效强度:.1f}x, 速度={动效速度调节}x")
        else:
            print(f"[增强字幕] 帧数模式: 开始=第{start_frame}帧, 结束=第{end_frame}帧, "
                  f"总帧数={batch_size}")
            print(f"[增强字幕] 动效={动效类型}, 时长={动效时长:.0f}帧(实际{动效时长帧数}帧)")
        
        print(f"[增强字幕] 字体={字体选择}, 大小={final_font_size}px, 粗细={字体粗细}, "
              f"描边={描边大小}px, 字间距={字间距}px, 限定画布={限定在画布内}")
        
        # 应用位置预设
        if 位置预设 != "自定义":
            位置X百分比, 位置Y百分比 = self.get_position_preset(位置预设, width, height)
            print(f"[位置预设] 使用预设: {位置预设}, 位置: X={位置X百分比:.1f}%, Y={位置Y百分比:.1f}%")
        
        print(f"[文字对齐] {文字对齐}, 位置: X={位置X百分比:.1f}%, Y={位置Y百分比:.1f}%")
        
        pil_align = "center"
        if 文字对齐 == "左对齐":
            pil_align = "left"
        elif 文字对齐 == "右对齐":
            pil_align = "right"
            
        # GPU内存优化：批量处理前先移到CPU
        images_cpu = images.cpu()
        
        canvas_width = width * 2
        canvas_height = height * 2
        base_text_img = None
        if 动效类型 != "打字机":
            display_text_base = 字幕文本
            if 描边大小 > 0 and 渐变效果 != "无":
                base_text_img = self.create_gradient_text(
                    display_text_base, font, 渐变效果,
                    渐变开头颜色, 渐变中间颜色, 渐变末尾颜色, 渐变过渡强度, 排版方向, 字间距, 字体粗细
                )
            elif 描边大小 > 0:
                base_text_img = self.create_stroke_text(
                    display_text_base, font, text_color, stroke_color, 描边大小,
                    描边位置, 描边不透明度, canvas_width, canvas_height, 
                    字间距, 排版方向, 字体粗细
                )
            elif 渐变效果 != "无":
                base_text_img = self.create_gradient_text(
                    display_text_base, font, 渐变效果,
                    渐变开头颜色, 渐变中间颜色, 渐变末尾颜色, 渐变过渡强度, 排版方向, 字间距, 字体粗细
                )
            elif 排版方向 == "竖排":
                base_text_img = self.create_vertical_text(display_text_base, font, text_color, 字间距, 字体粗细)
            else:
                temp_img = Image.new('RGBA', (canvas_width, canvas_height), (0, 0, 0, 0))
                temp_draw = ImageDraw.Draw(temp_img)
                alpha_full = 255
                if 字间距 != 0:
                    chars = list(display_text_base.replace('\n', ''))
                    measure_img = Image.new('RGBA', (1, 1))
                    measure_draw = ImageDraw.Draw(measure_img)
                    char_widths = []
                    for char in chars:
                        bbox = measure_draw.textbbox((0, 0), char, font=font)
                        char_widths.append(bbox[2] - bbox[0])
                    total_width = sum(char_widths) + (len(chars) - 1) * max(0, 字间距)
                    x_offset = (canvas_width - total_width) // 2
                    for char, char_width in zip(chars, char_widths):
                        char_x = x_offset + char_width // 2
                        if 字体粗细 == "常规":
                            temp_draw.text((char_x, canvas_height//2), char, 
                                         font=font, fill=text_color + (alpha_full,), anchor='mm')
                        else:
                            self.create_bold_text(temp_draw, (char_x, canvas_height//2), 
                                                char, font, text_color + (alpha_full,), 字体粗细)
                        x_offset += char_width + max(0, 字间距)
                else:
                    if 字体粗细 == "常规":
                        temp_draw.text((canvas_width//2, canvas_height//2), display_text_base, 
                                     font=font, fill=text_color + (alpha_full,), anchor='mm', align=pil_align)
                    else:
                        self.create_bold_text(temp_draw, (canvas_width//2, canvas_height//2), 
                                            display_text_base, font, text_color + (alpha_full,), 字体粗细, align=pil_align)
                base_text_img = temp_img
        
        for i in range(batch_size):
            # 定期清理GPU显存（每100帧清理一次）
            if i > 0 and i % 100 == 0 and torch.cuda.is_available():
                torch.cuda.empty_cache()
            
            # 转换当前帧（从CPU tensor）
            img_array = images_cpu[i].numpy()
            img_array = (img_array * 255).astype(np.uint8)
            img_pil = Image.fromarray(img_array)
            
            # 判断是否在显示范围
            if i < start_frame or i >= end_frame:
                result = img_pil.convert('RGB')
                result_array = np.array(result).astype(np.float32) / 255.0
                output_images.append(result_array)
                continue
            
            relative_frame = i - start_frame
            
            # 淡出特殊处理
            if 动效类型 == "淡出":
                total_display_frames = end_frame - start_frame
                fade_start_frame = max(0, total_display_frames - 动效时长帧数)
                
                if relative_frame < fade_start_frame:
                    anim_params = {
                        "opacity": 1.0, "offset_x": 0, "offset_y": 0,
                        "scale": 1.0, "char_reveal": 1.0, "rotation": 0, "distortion": 0
                    }
                else:
                    fade_relative_frame = relative_frame - fade_start_frame
                    anim_params = self.apply_animation_enhanced(
                        fade_relative_frame, 动效类型, 动效时长帧数, 动效强度, width
                    )
            else:
                anim_params = self.apply_animation_enhanced(
                    relative_frame, 动效类型, 动效时长帧数, 动效强度, width
                )
            
            # 打字机效果
            display_text = 字幕文本
            visible_chars = -1
            if 动效类型 == "打字机":
                char_count = int(len(字幕文本) * anim_params["char_reveal"])
                # 对于复杂效果（描边/渐变/竖排），暂时使用截断文本（可能会有抖动）
                # 对于标准绘制，使用visible_chars实现无抖动打字机
                is_complex_style = (描边大小 > 0) or (渐变效果 != "无") or (排版方向 == "竖排")
                
                if is_complex_style:
                    display_text = 字幕文本[:max(0, char_count)]
                    if not display_text:
                        result = img_pil.convert('RGB')
                        result_array = np.array(result).astype(np.float32) / 255.0
                        output_images.append(result_array)
                        continue
                else:
                    # 标准模式，传递完整文本和可见字符数
                    display_text = 字幕文本
                    visible_chars = max(0, char_count)
                    if visible_chars == 0:
                        result = img_pil.convert('RGB')
                        result_array = np.array(result).astype(np.float32) / 255.0
                        output_images.append(result_array)
                        continue
            
            # 创建文字图层
            canvas_width = width * 2
            canvas_height = height * 2
            
            # 全功能渲染逻辑（支持所有组合）
            if base_text_img is not None and 动效类型 != "打字机":
                text_img = base_text_img.copy()
                if 不透明度 < 1.0 or anim_params["opacity"] < 1.0:
                    combined_opacity = 不透明度 * anim_params["opacity"]
                    alpha_mask = text_img.split()[3].point(lambda p: int(p * combined_opacity))
                    text_img.putalpha(alpha_mask)
            else:
                if 描边大小 > 0 and 渐变效果 != "无":
                    text_img = self.create_gradient_text(
                        display_text, font, 渐变效果,
                        渐变开头颜色, 渐变中间颜色, 渐变末尾颜色, 渐变过渡强度, 排版方向, 字间距, 字体粗细
                    )
                    if 不透明度 < 1.0 or anim_params["opacity"] < 1.0:
                        combined_opacity = 不透明度 * anim_params["opacity"]
                        alpha_mask = text_img.split()[3].point(lambda p: int(p * combined_opacity))
                        text_img.putalpha(alpha_mask)
                elif 描边大小 > 0:
                    text_img = self.create_stroke_text(
                        display_text, font, text_color, stroke_color, 描边大小,
                        描边位置, 描边不透明度, canvas_width, canvas_height, 
                        字间距, 排版方向, 字体粗细
                    )
                    if 不透明度 < 1.0 or anim_params["opacity"] < 1.0:
                        combined_opacity = 不透明度 * anim_params["opacity"]
                        alpha_mask = text_img.split()[3].point(lambda p: int(p * combined_opacity))
                        text_img.putalpha(alpha_mask)
                elif 渐变效果 != "无":
                    text_img = self.create_gradient_text(
                        display_text, font, 渐变效果,
                        渐变开头颜色, 渐变中间颜色, 渐变末尾颜色, 渐变过渡强度, 排版方向, 字间距, 字体粗细
                    )
                    if 不透明度 < 1.0 or anim_params["opacity"] < 1.0:
                        combined_opacity = 不透明度 * anim_params["opacity"]
                        alpha_mask = text_img.split()[3].point(lambda p: int(p * combined_opacity))
                        text_img.putalpha(alpha_mask)
                elif 排版方向 == "竖排":
                    text_img = self.create_vertical_text(display_text, font, text_color, 字间距, 字体粗细)
                    if 不透明度 < 1.0 or anim_params["opacity"] < 1.0:
                        combined_opacity = 不透明度 * anim_params["opacity"]
                        alpha_mask = text_img.split()[3].point(lambda p: int(p * combined_opacity))
                        text_img.putalpha(alpha_mask)
                else:
                    temp_img = Image.new('RGBA', (canvas_width, canvas_height), (0, 0, 0, 0))
                    temp_draw = ImageDraw.Draw(temp_img)
                    alpha = int(255 * 不透明度 * anim_params["opacity"])
                    self._draw_multiline_text_with_spacing(
                        temp_draw, display_text, font, text_color + (alpha,),
                        canvas_width, canvas_height, 字间距, pil_align, 字体粗细
                    )
                    text_img = temp_img
            
            # 应用缩放（使用高质量LANCZOS算法）
            if anim_params["scale"] != 1.0 and anim_params["scale"] > 0:
                new_size = (
                    max(1, int(text_img.width * anim_params["scale"])), 
                    max(1, int(text_img.height * anim_params["scale"]))
                )
                text_img = text_img.resize(new_size, Image.LANCZOS)
            
            # 应用旋转
            total_rotation = 字体角度 + anim_params["rotation"]
            if total_rotation != 0:
                text_img = text_img.rotate(-total_rotation, expand=True, resample=Image.BICUBIC)
            
            # 创建最终图层
            final_layer = Image.new('RGBA', (width, height), (0, 0, 0, 0))
            
            # 计算位置（根据对齐方式）
            text_x = int(width * 位置X百分比 / 100.0) + anim_params["offset_x"]
            text_y = int(height * 位置Y百分比 / 100.0) + anim_params["offset_y"]
            
            # 根据文字对齐方式计算粘贴位置
            if 文字对齐 == "左对齐":
                paste_x = text_x
            elif 文字对齐 == "右对齐":
                paste_x = text_x - text_img.width
            else:  # 居中对齐
                paste_x = text_x - text_img.width // 2
            
            paste_y = text_y - text_img.height // 2
            
            # 限定在画布内处理（按字裁剪模式）
            if 限定在画布内 == "按字裁剪":
                text_img, paste_x, paste_y = self.constrain_to_canvas_by_char(
                    text_img, paste_x, paste_y, width, height
                )
            
            # 添加投影
            if 投影距离 > 0 and 投影强度 > 0:
                projection = self.create_projection(text_img, 投影角度, 投影距离, 投影强度, 投影模糊)
                try:
                    final_layer.paste(projection, (paste_x, paste_y), projection)
                except Exception as e:
                    print(f"警告: 投影粘贴失败 - {e}")
            
            # 粘贴文字
            try:
                final_layer.paste(text_img, (paste_x, paste_y), text_img)
            except Exception as e:
                print(f"警告: 文字粘贴失败 - {e}")
            
            # 合成最终图像
            img_pil = img_pil.convert('RGBA')
            result = Image.alpha_composite(img_pil, final_layer)
            result = result.convert('RGB')
            
            result_array = np.array(result).astype(np.float32) / 255.0
            output_images.append(result_array)
        
        # 转换为tensor
        output_tensor = torch.from_numpy(np.stack(output_images))
        
        # 清理临时数据，释放内存
        del output_images
        gc.collect()
        
        # 清理GPU显存
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
            torch.cuda.synchronize()
        
        print(f"[增强字幕] 完成: 处理{batch_size}帧, 字幕显示{end_frame - start_frame}帧")
        
        # 返回图像和时间参数
        return (output_tensor, 开始时间, 结束时间)


# 节点已在 __init__.py 中统一注册，此处不再重复注册
