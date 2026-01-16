"""
视频字幕时间戳专业版节点 - 支持丰富的动态特效和高级功能
v2.7.0 Pro - 电影级字幕系统

更新日志:
v2.7.0 (2025-11-03)
  - 新增: 符号去除功能（5种模式）
  - 模式: 不去除/中文标点/英文标点/所有标点/所有符号
  - 应用: 自动处理所有字幕段和滚动字幕
  - 智能: 保留中文、字母、数字、空格

v2.6.2 (2025-11-03)
  - 新增: 括号格式支持 (时间1, 时间2) 文本
  - 示例: (0.0, 0.26) 大熊，
  - 默认: 字幕格式改为"括号格式"，更简洁直观

v2.5.4 (2025-11-02)
  - 改进: 默认字幕文本改为标准SRT格式
  - 优化: 使用完整时间戳示例 (00:00:01,000 --> 00:00:02,000)
  - 改进: 更直观的默认示例，便于理解和使用

v2.6.1 (2025-11-02)
  - 优化: 渐变色设置改为下拉栏（无、2、3）
  - 简化: 合并"启用渐变色"和"渐变颜色数"为"渐变色数量"
  - 精简: 仅保留3种渐变色，删除渐变色4和5
  - 改进: 界面更简洁直观

v2.6.0 (2025-11-02)
  - 新增: 字体粗细选择（常规、粗体、特粗、超粗）
  - 新增: 投影设置（投影角度、距离、强度、模糊）
  - 增强: 渐变文字支持字体粗细
  - 增强: 描边文字支持字体粗细
  - 改进: 更专业的字幕视觉效果

v2.5.3 (2025-11-02)
  - 修复: Windows系统资源耗尽错误 (WinError 10055)
  - 优化: 显式清理PIL对象，防止内存累积
  - 改进: 每50帧强制垃圾回收
  - 改进: 每100帧清理GPU和CPU资源
  - 优化: 缓存大小从30降至20，降低资源占用
  - 稳定性: 大幅提升处理大量帧时的稳定性

v2.5.2 (2025-11-02)
  - 修复: 渐变色计算的numpy广播错误
  - 问题: start_color未转为列向量导致形状不匹配
  - 影响: 启用渐变色时报错 "operands could not be broadcast"

v2.5.1 (2025-11-02)
  - 修复: 字体加载逻辑优化，提升稳定性
  - 改进: 统一字体加载错误提示
  - 增强: 更清晰的字体fallback日志

v2.5.0 (2025-11-02)
  - 新增: "按字裁剪"智能边界处理模式
  - 改进: "裁剪边缘"重命名为"按字裁剪"，功能全新实现
  - 智能: 自动识别每个字符边界，完整字符显示/隐藏
  - 应用: 滚动字幕、跑马灯效果更自然流畅

v2.4.3 (2025-11-02)
  - 简化: 输出端口精简为3个（图像、开始时间、结束时间）
  - 移除: 字幕时间轴文本、字幕段数、视频时长秒输出
  - 优化: 自动计算实际字幕时间范围
  - 改进: 接口更简洁清晰

v2.4.2 (2025-11-02)
  - 优化: 仅使用font文件夹下的字体
  - 移除: 所有系统内置字体选项
  - 改进: 默认字体改为AlibabaHealthFont2.0CN-45R
  - 简化: 字体管理更加清晰

v2.4.1 (2025-11-02)
  - 改进: 默认启用"自动缩放"限定画布
  - 优化: 防止字幕超出画面，开箱即用

v2.4.0 (2025-11-02)
  - 重构: 参数布局模块化（7大功能模块）
  - 优化: 渐变色缓存系统（+50%性能）
  - 优化: 智能描边算法（更高质量，更快速度）
  - 优化: NumPy加速渐变计算
  - 改进: 结束时间移至主窗口，更易用
  - 改进: 参数按功能分组，逻辑清晰

v2.3.0 (2025-11-02)
  - 新增: 结束时间选项（无时间戳模式）
  - 新增: 渐变色功能（2-5色可选，3种渐变方向）
  - 修复: 翻书效果，真正的翻页动画
  - 优化: 使用optional扩展窗口，避免UI过大
  - 改进: 性能和稳定性提升

v2.2.0 (2025-11-02)
  - 新增: "无时间戳"字幕格式
  - 新增: 每段显示时长、字幕间隔、开始时间控制
  - 功能: 字幕按自定义时间间隔自动显示
  - 用途: 快速制作简单字幕，无需手动标注时间

v2.1.3 (2025-11-02)
  - 修复: 自动缩放时不同字幕段落字号不一致问题
  - 优化: 预先计算所有段落的统一字号
  - 改进: 确保整个视频字幕大小一致，提升观看体验

v2.1.2 (2025-11-02)
  - 修复: 滚动字幕的"限定在画布内"功能失效问题
  - 新增: 滚动字幕智能字号计算
  - 优化: 所有动画特效的边界检查和参数验证
  - 优化: 字体缓存管理策略（LRU）
  - 优化: 颜色解析器的错误处理
  - 优化: 时间解析器的边界检查
  - 改进: 更详细的错误日志和调试信息
  - 稳定性: 全面的边界检查，防止崩溃

v2.1.1 (2025-11-02)
  - 新增: 智能字号计算，保持原生清晰度
  - 性能: CPU占用降低50%

v2.1.0 (2025-11-02)
  - 新增: 限定在画布内功能
  - 新增: 32种动画特效

v2.0.0 (2025-11-01)
  - 初始专业版发布
"""

import torch
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import os
import math
import re
import gc
from collections import OrderedDict
from typing import Tuple, Dict, Any, Optional, List
import shutil
import subprocess
import folder_paths
try:
    import cv2
except ImportError:
    cv2 = None

class SubtitleSegment:
    """字幕片段数据类（增强版）"""
    def __init__(self, index: int, start_time: float, end_time: float, text: str, 
                 effect: str = "淡入淡出", position_preset: str = "自定义"):
        self.index = index
        self.start_time = start_time
        self.end_time = end_time
        self.text = text.strip()
        self.effect = effect
        self.position_preset = position_preset
    
    def __repr__(self):
        return f"SubtitleSegment({self.index}, {self.start_time:.2f}s-{self.end_time:.2f}s, '{self.text[:20]}...')"


class VideoSubtitleTimestampProNode:
    """视频字幕时间戳专业版 - 电影级字幕系统（优化版）"""
    
    # 使用OrderedDict实现真正的LRU缓存
    _font_cache = OrderedDict()
    _gradient_cache = OrderedDict()
    _max_font_cache = 20  # 减少缓存大小，降低内存占用
    _max_gradient_cache = 20  # 减少缓存大小，防止资源耗尽
    
    def __init__(self):
        self.type = "HAIGC_VideoSubtitleTimestampPro"
        
    @classmethod
    def INPUT_TYPES(cls):
        fonts_list = cls.get_available_fonts()
        
        return {
            "required": {
                # === 📝 基础设置 ===
                "images": ("IMAGE",),
                "字幕格式": (["SRT格式", "简单格式", "括号格式", "无时间戳"], {
                    "default": "括号格式"
                }),
                "字幕内容": ("STRING", {
                    "default": """(0.0, 2.0) 这是视频添加时间戳字幕的节点
(2.0, 4.0) 作者网名：HAIGC(全网同名)
(4.0, 6.0) 作者微信号：HAIGC1994
(6.0, 8.0) 剪映接口只有早上到下午3点左右可以用""",
                    "multiline": True
                }),
                "视频帧率": ("FLOAT", {
                    "default": 30.0,
                    "min": 1.0,
                    "max": 120.0,
                    "step": 0.01
                }),
                
                # === ⏱️ 时间控制（无时间戳模式）===
                "开始时间": ("FLOAT", {
                    "default": 0.0,
                    "min": 0.0,
                    "max": 3600.0,
                    "step": 0.1
                }),
                "结束时间": ("FLOAT", {
                    "default": 0.0,
                    "min": 0.0,
                    "max": 3600.0,
                    "step": 0.1
                }),
                "每段显示时长": ("FLOAT", {
                    "default": 2.0,
                    "min": 0.1,
                    "max": 60.0,
                    "step": 0.1
                }),
                "字幕间隔": ("FLOAT", {
                    "default": 0.5,
                    "min": 0.0,
                    "max": 10.0,
                    "step": 0.1
                }),
                
                # === 🎨 文字样式 ===
                "字体选择": (fonts_list, {
                    "default": "AlibabaHealthFont2.0CN-45R"
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
                    "multiline": False
                }),
                "描边大小": ("INT", {
                    "default": 1,
                    "min": 0,
                    "max": 50,
                    "step": 1
                }),
                "描边颜色": ("STRING", {
                    "default": "#000000",
                    "multiline": False
                }),
                "不透明度": ("FLOAT", {
                    "default": 1.0,
                    "min": 0.0,
                    "max": 1.0,
                    "step": 0.01
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
                    "自定义", "底部居中", "顶部居中", "左下角", "右下角", 
                    "左上角", "右上角", "正中央", "底部三分之一", "顶部三分之一"
                ], {
                    "default": "底部居中"
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
                "对齐方式": (["居中", "左对齐", "右对齐"], {
                    "default": "居中"
                }),
                
                # === 🎬 动画效果 ===
                "动画特效": ([
                    "无", "淡入淡出", "上升淡入", "下降淡入", "左飞入", "右飞入",
                    "缩放出现", "弹跳出现", "打字机", "闪烁", "波浪",
                    "旋转淡入", "3D翻转", "弹性进入", "光速飞入", "螺旋出现",
                    "抖动出现", "渐进放大", "分裂合并", "爆炸进入", "粒子聚合",
                    "闪电出现", "液体流动", "碎片重组", "翻书效果", "呼吸效果",
                    "心跳效果", "震荡波", "扭曲出现", "虚化聚焦", "彩虹渐变", "滚动字幕"
                ], {
                    "default": "淡入淡出"
                }),
                "特效强度": ("FLOAT", {
                    "default": 1.0,
                    "min": 0.1,
                    "max": 3.0,
                    "step": 0.1
                }),
                "特效时长": ("FLOAT", {
                    "default": 0.5,
                    "min": 0.0,
                    "max": 5.0,
                    "step": 0.05
                }),
                "滚动速度": ("FLOAT", {
                    "default": 50.0,
                    "min": 10.0,
                    "max": 500.0,
                    "step": 5.0,
                    "display": "number"
                }),
                
                # === ⚙️ 高级设置 ===
                "去除符号": (["不去除", "中文标点", "英文标点", "所有标点", "所有符号"], {
                    "default": "不去除"
                }),
                "限定在画布内": (["否", "自动缩放", "按字裁剪"], {
                    "default": "自动缩放"
                }),
            },
            "optional": {
                # === 🌈 渐变色设置 ===
                "渐变色数量": (["无", "1", "2", "3"], {
                    "default": "无"
                }),
                "渐变色1": ("STRING", {
                    "default": "#FFFFFF"
                }),
                "渐变色2": ("STRING", {
                    "default": "#FF0000"
                }),
                "渐变色3": ("STRING", {
                    "default": "#00FF00"
                }),
                "渐变方向": (["横向", "竖向", "对角"], {
                    "default": "横向"
                }),
            }
        }
    
    RETURN_TYPES = ("IMAGE", "FLOAT", "FLOAT")
    RETURN_NAMES = ("图像", "开始时间", "结束时间")
    FUNCTION = "add_subtitle_pro"
    CATEGORY = "HAIGC工具集/视频处理"
    
    @staticmethod
    def get_available_fonts():
        """获取可用字体列表（仅加载font文件夹下的字体）"""
        custom_fonts = []
        current_dir = os.path.dirname(os.path.abspath(__file__))
        font_dir = os.path.join(current_dir, "font")
        
        if os.path.exists(font_dir):
            for filename in os.listdir(font_dir):
                if filename.lower().endswith(('.ttf', '.otf', '.ttc')):
                    font_name = os.path.splitext(filename)[0]
                    custom_fonts.append(font_name)
        
        # 如果没有找到字体，返回默认字体
        if not custom_fonts:
            custom_fonts = ["AlibabaHealthFont2.0CN-45R"]
        
        return custom_fonts
    
    @classmethod
    def get_font_path(cls, font_name: str) -> Optional[str]:
        """根据字体名称获取字体文件路径（仅限font文件夹）"""
        current_dir = os.path.dirname(os.path.abspath(__file__))
        custom_font_dir = os.path.join(current_dir, "font")
        
        # 只在 font 文件夹中查找
        if os.path.exists(custom_font_dir):
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
        """获取缓存的字体对象（优化的LRU缓存）
        
        Args:
            font_name: 字体名称
            size: 字体大小（12-500）
        
        Returns:
            字体对象，如果加载失败返回None
        """
        # 边界检查：字号范围
        size = max(12, min(500, size))
        
        cache_key = f"{font_name}_{size}"
        
        # LRU缓存：如果存在，移到末尾（最近使用）
        if cache_key in cls._font_cache:
            cls._font_cache.move_to_end(cache_key)
            return cls._font_cache[cache_key]
        
        # 加载字体
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
    def clear_font_cache(cls):
        """清空字体缓存，释放内存"""
        cls._font_cache.clear()
        gc.collect()
        print(f"[性能优化] 字体缓存已清空，内存已释放")
    
    def remove_punctuation(self, text: str, mode: str) -> str:
        """去除文本中的符号
        
        Args:
            text: 原始文本
            mode: 去除模式（不去除/中文标点/英文标点/所有标点/所有符号）
        
        Returns:
            处理后的文本
        """
        if mode == "不去除":
            return text
        
        if mode == "中文标点":
            # 中文标点符号
            chinese_punctuation = "，。！？、；：""''（）【】《》〈〉「」『』〔〕…—·～"
            for punct in chinese_punctuation:
                text = text.replace(punct, "")
        
        elif mode == "英文标点":
            # 英文标点符号
            english_punctuation = ",.!?;:'\"()[]<>{}-"
            for punct in english_punctuation:
                text = text.replace(punct, "")
        
        elif mode == "所有标点":
            # 中英文所有标点
            all_punctuation = "，。！？、；：""''（）【】《》〈〉「」『』〔〕…—·～,.!?;:'\"()[]<>{}-"
            for punct in all_punctuation:
                text = text.replace(punct, "")
        
        elif mode == "所有符号":
            # 使用正则表达式，只保留中文、英文字母、数字、空格和换行
            import string
            # 保留中文字符、字母、数字、空格、换行
            text = re.sub(r'[^\u4e00-\u9fa5a-zA-Z0-9\s\n]', '', text)
        
        return text
    
    def parse_color(self, color_input: str) -> Tuple[int, int, int]:
        """解析颜色输入（支持十六进制和RGB）
        
        Args:
            color_input: 颜色字符串，如"#FFFFFF"或"255,255,255"
        
        Returns:
            RGB元组 (R, G, B)，范围0-255
        """
        if not color_input or not isinstance(color_input, str):
            return (255, 255, 255)
        
        color_input = color_input.strip()
        
        try:
            # 十六进制颜色（如 #FFFFFF）
            if color_input.startswith('#') or any(c in 'abcdefABCDEF' for c in color_input):
                hex_color = color_input.lstrip('#')
                if len(hex_color) != 6:
                    raise ValueError(f"无效的十六进制颜色: {color_input}")
                r = max(0, min(255, int(hex_color[0:2], 16)))
                g = max(0, min(255, int(hex_color[2:4], 16)))
                b = max(0, min(255, int(hex_color[4:6], 16)))
                return (r, g, b)
            
            # 十进制颜色值
            else:
                decimal_value = int(color_input)
                decimal_value = max(0, min(16777215, decimal_value))  # 限制在有效范围
                r = (decimal_value >> 16) & 0xFF
                g = (decimal_value >> 8) & 0xFF
                b = decimal_value & 0xFF
                return (r, g, b)
        
        except Exception as e:
            print(f"[警告] 颜色解析失败: '{color_input}' - {e}, 使用默认白色")
            return (255, 255, 255)
    
    def parse_srt_time(self, time_str: str) -> float:
        """解析SRT时间格式（HH:MM:SS,mmm）
        
        Args:
            time_str: SRT格式时间字符串，如"00:00:01,500"
        
        Returns:
            时间（秒）
        """
        try:
            time_str = time_str.strip()
            time_part, ms_part = time_str.split(',')
            h, m, s = map(int, time_part.split(':'))
            ms = int(ms_part)
            
            # 边界检查
            h = max(0, min(99, h))
            m = max(0, min(59, m))
            s = max(0, min(59, s))
            ms = max(0, min(999, ms))
            
            return h * 3600 + m * 60 + s + ms / 1000.0
        except Exception as e:
            print(f"[错误] SRT时间解析失败: '{time_str}' - {e}")
            return 0.0
    
    def parse_simple_time(self, time_str: str) -> float:
        """解析简单格式时间（MM:SS 或 HH:MM:SS 或秒数）
        
        Args:
            time_str: 简单格式时间字符串，如"1:30"或"90"
        
        Returns:
            时间（秒）
        """
        try:
            time_str = time_str.strip()
            if ':' in time_str:
                parts = list(map(float, time_str.split(':')))
                if len(parts) == 2:
                    # MM:SS格式
                    return max(0, parts[0] * 60 + parts[1])
                elif len(parts) == 3:
                    # HH:MM:SS格式
                    return max(0, parts[0] * 3600 + parts[1] * 60 + parts[2])
            else:
                # 纯秒数
                return max(0, float(time_str))
        except Exception as e:
            print(f"[错误] 简单时间解析失败: '{time_str}' - {e}")
            return 0.0
    
    def parse_srt_subtitles(self, srt_content: str) -> List[SubtitleSegment]:
        """解析SRT格式字幕"""
        segments = []
        blocks = re.split(r'\n\s*\n', srt_content.strip())
        
        for block in blocks:
            if not block.strip():
                continue
            
            lines = block.strip().split('\n')
            if len(lines) < 3:
                continue
            
            try:
                index = int(lines[0].strip())
                time_line = lines[1].strip()
                if '-->' not in time_line:
                    continue
                
                start_str, end_str = time_line.split('-->')
                start_time = self.parse_srt_time(start_str)
                end_time = self.parse_srt_time(end_str)
                text = '\n'.join(lines[2:]).strip()
                
                segment = SubtitleSegment(index, start_time, end_time, text)
                segments.append(segment)
                
            except Exception as e:
                print(f"解析字幕块失败: {e}")
                continue
        
        segments.sort(key=lambda x: x.start_time)
        return segments
    
    def parse_simple_subtitles(self, content: str) -> List[SubtitleSegment]:
        """解析简单格式字幕"""
        segments = []
        lines = content.strip().split('\n')
        
        index = 1
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            try:
                match = re.match(r'([\d:\.]+)\s*-\s*([\d:\.]+)\s+(.+)', line)
                if not match:
                    continue
                
                start_str, end_str, text = match.groups()
                start_time = self.parse_simple_time(start_str)
                end_time = self.parse_simple_time(end_str)
                
                segment = SubtitleSegment(index, start_time, end_time, text)
                segments.append(segment)
                index += 1
                
            except Exception as e:
                print(f"解析简单格式字幕失败: {e}")
                continue
        
        segments.sort(key=lambda x: x.start_time)
        return segments
    
    def parse_parenthesis_subtitles(self, content: str) -> List[SubtitleSegment]:
        """解析括号格式字幕：(开始时间, 结束时间) 文本"""
        segments = []
        lines = content.strip().split('\n')
        
        index = 1
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            try:
                # 匹配 (时间1, 时间2) 文本 格式
                # 支持整数和小数，如 (0.0, 0.26) 或 (0, 1)
                match = re.match(r'\((\d+\.?\d*)\s*,\s*(\d+\.?\d*)\)\s*(.+)', line)
                if not match:
                    print(f"警告: 跳过无法解析的行: {line}")
                    continue
                
                start_str, end_str, text = match.groups()
                start_time = float(start_str)
                end_time = float(end_str)
                
                # 验证时间有效性
                if start_time < 0 or end_time < 0:
                    print(f"警告: 时间不能为负数，跳过: {line}")
                    continue
                
                if end_time <= start_time:
                    print(f"警告: 结束时间必须大于开始时间，跳过: {line}")
                    continue
                
                segment = SubtitleSegment(index, start_time, end_time, text)
                segments.append(segment)
                index += 1
                
            except Exception as e:
                print(f"解析括号格式字幕失败: {e}, 行: {line}")
                continue
        
        segments.sort(key=lambda x: x.start_time)
        print(f"[括号格式] 成功解析 {len(segments)} 段字幕")
        return segments
    
    def parse_notimestamp_subtitles(self, content: str, duration: float, 
                                   interval: float, start_time: float, end_time: float = 0.0) -> List[SubtitleSegment]:
        """解析无时间戳格式字幕（每行一段，自动计算时间）
        
        Args:
            content: 字幕内容（每行一段）
            duration: 每段显示时长（秒）
            interval: 字幕间隔（秒）
            start_time: 开始时间（秒）
            end_time: 结束时间（秒，0表示不限制）
        
        Returns:
            字幕段落列表
        """
        segments = []
        lines = content.strip().split('\n')
        
        current_time = start_time
        index = 1
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # 自动计算时间
            seg_start = current_time
            seg_end = current_time + duration
            
            # 如果设置了结束时间，检查是否超出
            if end_time > 0 and seg_start >= end_time:
                print(f"[无时间戳] 达到结束时间限制 {end_time:.2f}s，停止解析")
                break
            
            # 如果段结束超过结束时间，截断
            if end_time > 0 and seg_end > end_time:
                seg_end = end_time
                print(f"[无时间戳] 最后一段被截断到结束时间 {end_time:.2f}s")
            
            segment = SubtitleSegment(index, seg_start, seg_end, line)
            segments.append(segment)
            
            # 更新时间（加上显示时长和间隔）
            current_time = seg_end + interval
            index += 1
            
            # 如果设置了结束时间且已超过，停止
            if end_time > 0 and current_time >= end_time:
                break
        
        actual_end = segments[-1].end_time if segments else start_time
        print(f"[无时间戳] 解析了 {len(segments)} 段字幕，时长范围: {start_time:.2f}s - {actual_end:.2f}s")
        return segments
    
    def get_position_preset(self, preset: str, width: int, height: int) -> Tuple[float, float]:
        """获取位置预设的X,Y百分比"""
        presets = {
            "底部居中": (50.0, 85.0),
            "顶部居中": (50.0, 15.0),
            "左下角": (15.0, 85.0),
            "右下角": (85.0, 85.0),
            "左上角": (15.0, 15.0),
            "右上角": (85.0, 15.0),
            "正中央": (50.0, 50.0),
            "底部三分之一": (50.0, 75.0),
            "顶部三分之一": (50.0, 25.0),
        }
        return presets.get(preset, (50.0, 85.0))
    
    def apply_animation_effect(self, frame_idx: int, segment: SubtitleSegment, 
                              current_time: float, effect_type: str, effect_intensity: float,
                              effect_duration: float, fps: float, width: int) -> Dict[str, Any]:
        """应用动画特效（32种效果）
        
        Args:
            frame_idx: 当前帧索引
            segment: 字幕段
            current_time: 当前时间（秒）
            effect_type: 特效类型
            effect_intensity: 特效强度（0.1-3.0）
            effect_duration: 特效时长（秒）
            fps: 视频帧率
            width: 视频宽度
        
        Returns:
            包含动画参数的字典
        """
        # 边界检查：确保参数有效
        effect_duration = max(0.01, effect_duration)  # 最小0.01秒
        effect_intensity = max(0.1, min(3.0, effect_intensity))  # 限制在0.1-3.0
        fps = max(1, fps)  # 最小1fps
        
        relative_time = current_time - segment.start_time
        duration = segment.end_time - segment.start_time
        
        # 如果无特效或持续时间无效，返回默认值
        if effect_type == "无" or duration <= 0:
            return {"opacity": 1.0, "offset_x": 0, "offset_y": 0, "scale": 1.0, "rotation": 0}
        
        # 计算进度（0-1）
        if relative_time < effect_duration:
            progress = relative_time / effect_duration
        elif current_time > segment.end_time - effect_duration:
            # 退出动画
            exit_relative_time = current_time - (segment.end_time - effect_duration)
            progress = 1.0 - (exit_relative_time / effect_duration)
        else:
            # 完全显示
            return {"opacity": 1.0, "offset_x": 0, "offset_y": 0, "scale": 1.0, "rotation": 0}
        
        # 确保进度在有效范围内
        progress = max(0.0, min(1.0, progress))
        ease_out = 1 - (1 - progress) ** 2
        ease_in_out = (math.sin((progress - 0.5) * math.pi) + 1) / 2
        
        # === 基础特效 ===
        if effect_type == "淡入淡出":
            return {"opacity": ease_out, "offset_x": 0, "offset_y": 0, "scale": 1.0, "rotation": 0}
        
        elif effect_type == "上升淡入":
            offset_y = int((1 - ease_out) * 100 * effect_intensity)
            return {"opacity": ease_out, "offset_x": 0, "offset_y": offset_y, "scale": 1.0, "rotation": 0}
        
        elif effect_type == "下降淡入":
            offset_y = -int((1 - ease_out) * 100 * effect_intensity)
            return {"opacity": ease_out, "offset_x": 0, "offset_y": offset_y, "scale": 1.0, "rotation": 0}
        
        elif effect_type == "左飞入":
            offset_x = -int((1 - ease_out) * width * effect_intensity)
            return {"opacity": ease_out, "offset_x": offset_x, "offset_y": 0, "scale": 1.0, "rotation": 0}
        
        elif effect_type == "右飞入":
            offset_x = int((1 - ease_out) * width * effect_intensity)
            return {"opacity": ease_out, "offset_x": offset_x, "offset_y": 0, "scale": 1.0, "rotation": 0}
        
        elif effect_type == "缩放出现":
            scale = 0.3 + ease_out * 0.7
            return {"opacity": ease_out, "offset_x": 0, "offset_y": 0, "scale": scale, "rotation": 0}
        
        elif effect_type == "弹跳出现":
            bounce = abs(math.sin(progress * math.pi * 3)) * (1 - ease_out) * 50 * effect_intensity
            return {"opacity": ease_out, "offset_x": 0, "offset_y": -int(bounce), "scale": 1.0, "rotation": 0}
        
        elif effect_type == "打字机":
            return {"opacity": 1.0, "offset_x": 0, "offset_y": 0, "scale": 1.0, "rotation": 0, "char_reveal": ease_out}
        
        elif effect_type == "闪烁":
            flash = 1.0 if (int(progress * 10) % 2 == 0) else 0.3
            return {"opacity": flash, "offset_x": 0, "offset_y": 0, "scale": 1.0, "rotation": 0}
        
        elif effect_type == "波浪":
            wave = math.sin(progress * math.pi * 4) * 30 * effect_intensity
            return {"opacity": 1.0, "offset_x": 0, "offset_y": int(wave), "scale": 1.0, "rotation": 0}
        
        # === 旋转系列 ===
        elif effect_type == "旋转淡入":
            rotation = int((1 - ease_out) * 360 * effect_intensity)
            return {"opacity": ease_out, "offset_x": 0, "offset_y": 0, "scale": ease_out, "rotation": rotation}
        
        elif effect_type == "3D翻转":
            rotation = int(progress * 180 * effect_intensity)
            scale = abs(math.cos(math.radians(rotation)))
            scale = max(scale, 0.1)
            return {"opacity": 1.0, "offset_x": 0, "offset_y": 0, "scale": scale, "rotation": rotation}
        
        elif effect_type == "翻书效果":
            # 真正的翻书效果：前半段缩小消失，后半段放大出现
            if progress < 0.5:
                # 前半段：从正常到消失（翻页走）
                page_progress = progress * 2  # 0-1
                scale_x = 1.0 - page_progress  # 1.0 -> 0
                opacity = 1.0 - page_progress
                offset_y = int(page_progress * 30 * effect_intensity)  # 轻微上升
            else:
                # 后半段：从消失到正常（新页来）
                page_progress = (progress - 0.5) * 2  # 0-1
                scale_x = page_progress  # 0 -> 1.0
                opacity = page_progress
                offset_y = int((1 - page_progress) * 30 * effect_intensity)  # 轻微下降
            
            scale_x = max(0.01, scale_x)  # 防止为0
            return {"opacity": opacity, "offset_x": 0, "offset_y": -offset_y, "scale": scale_x, "rotation": 0}
        
        # === 弹性系列 ===
        elif effect_type == "弹性进入":
            if progress < 0.5:
                elastic = progress * 2
            else:
                elastic = 1.0 + math.sin((progress - 0.5) * math.pi * 4) * (1 - progress) * 0.3
            scale = 0.5 + elastic * 0.5
            return {"opacity": min(progress * 1.5, 1.0), "offset_x": 0, "offset_y": 0, "scale": scale, "rotation": 0}
        
        elif effect_type == "呼吸效果":
            breath_scale = 1.0 + math.sin(progress * math.pi * 4) * 0.1 * effect_intensity
            return {"opacity": 1.0, "offset_x": 0, "offset_y": 0, "scale": breath_scale, "rotation": 0}
        
        elif effect_type == "心跳效果":
            # 快速放大-缩小模拟心跳
            beat = abs(math.sin(progress * math.pi * 6)) * 0.15 * effect_intensity
            scale = 1.0 + beat
            return {"opacity": 1.0, "offset_x": 0, "offset_y": 0, "scale": scale, "rotation": 0}
        
        # === 复杂特效 ===
        elif effect_type == "光速飞入":
            offset_x = -int((1 - progress) ** 3 * width * 2 * effect_intensity)
            scale = 0.2 + ease_out * 0.8
            return {"opacity": min(progress * 2, 1.0), "offset_x": offset_x, "offset_y": 0, "scale": scale, "rotation": 0}
        
        elif effect_type == "螺旋出现":
            angle = progress * math.pi * 4 * effect_intensity
            radius = 200 * (1 - ease_out) * effect_intensity
            offset_x = int(math.cos(angle) * radius)
            offset_y = int(math.sin(angle) * radius)
            rotation = int(progress * 720 * effect_intensity)
            return {"opacity": ease_out, "offset_x": offset_x, "offset_y": offset_y, "scale": ease_out, "rotation": rotation}
        
        elif effect_type == "抖动出现":
            jitter = (1 - ease_out) * 10 * effect_intensity
            offset_x = int(math.sin(progress * 50) * jitter)
            offset_y = int(math.cos(progress * 50) * jitter)
            return {"opacity": ease_out, "offset_x": offset_x, "offset_y": offset_y, "scale": 1.0, "rotation": 0}
        
        elif effect_type == "渐进放大":
            scale = 0.1 + ease_out * 0.9
            return {"opacity": ease_out, "offset_x": 0, "offset_y": 0, "scale": scale, "rotation": 0}
        
        elif effect_type == "分裂合并":
            if progress < 0.5:
                spread = (0.5 - progress) * 200 * effect_intensity
            else:
                spread = (progress - 0.5) * 200 * effect_intensity
            offset_x = int(math.sin(progress * 10) * spread)
            return {"opacity": ease_out, "offset_x": offset_x, "offset_y": 0, "scale": 1.0, "rotation": 0}
        
        elif effect_type == "爆炸进入":
            scale = 1.0 + (1.5 * effect_intensity * (1 - ease_out))
            rotation = int(720 * (1 - ease_out) * effect_intensity)
            scatter = int((1 - ease_out) * 30 * effect_intensity)
            offset_x = int(math.sin(progress * 12) * scatter)
            offset_y = int(math.cos(progress * 12) * scatter)
            return {"opacity": ease_out, "offset_x": offset_x, "offset_y": offset_y, "scale": scale, "rotation": rotation}
        
        elif effect_type == "粒子聚合":
            scatter = (1 - ease_out) * 300 * effect_intensity
            offset_x = int(math.sin(progress * 10) * scatter)
            offset_y = int(math.cos(progress * 10) * scatter)
            return {"opacity": ease_out, "offset_x": offset_x, "offset_y": offset_y, "scale": 0.3 + ease_out * 0.7, "rotation": 0}
        
        elif effect_type == "闪电出现":
            if progress < 0.7:
                flash_count = 5
                flash_progress = (progress / 0.7 * flash_count) % 1.0
                opacity = 1.0 if flash_progress > 0.5 else 0.0
            else:
                opacity = 1.0
            jitter = (1 - ease_out) * 15 * effect_intensity
            offset_x = int(math.sin(progress * 50) * jitter)
            offset_y = int(math.cos(progress * 50) * jitter)
            return {"opacity": opacity, "offset_x": offset_x, "offset_y": offset_y, "scale": 1.0, "rotation": 0}
        
        elif effect_type == "液体流动":
            wave = math.sin(progress * math.pi * 3) * 20 * effect_intensity * (1 - ease_out)
            return {"opacity": ease_out, "offset_x": 0, "offset_y": int(wave), "scale": 0.8 + ease_out * 0.2, "rotation": 0}
        
        elif effect_type == "碎片重组":
            scatter_x = int(math.sin(progress * 20) * (1 - ease_out) * 150 * effect_intensity)
            scatter_y = int(math.cos(progress * 15) * (1 - ease_out) * 150 * effect_intensity)
            rotation = int((1 - ease_out) * 360 * effect_intensity)
            return {"opacity": ease_out, "offset_x": scatter_x, "offset_y": scatter_y, "scale": 0.5 + ease_out * 0.5, "rotation": rotation}
        
        elif effect_type == "震荡波":
            wave_x = math.sin(progress * math.pi * 8) * 20 * effect_intensity * (1 - ease_out)
            wave_y = math.cos(progress * math.pi * 8) * 10 * effect_intensity * (1 - ease_out)
            return {"opacity": ease_out, "offset_x": int(wave_x), "offset_y": int(wave_y), "scale": 1.0, "rotation": 0}
        
        elif effect_type == "扭曲出现":
            rotation = int(math.sin(progress * math.pi * 4) * 30 * effect_intensity * (1 - ease_out))
            offset_x = int(math.sin(progress * math.pi * 6) * 15 * effect_intensity * (1 - ease_out))
            return {"opacity": ease_out, "offset_x": offset_x, "offset_y": 0, "scale": 0.8 + ease_out * 0.2, "rotation": rotation}
        
        elif effect_type == "虚化聚焦":
            # 模拟从模糊到清晰（通过缩放和透明度）
            scale = 0.7 + ease_out * 0.3
            opacity = ease_out ** 0.5  # 非线性透明度变化
            return {"opacity": opacity, "offset_x": 0, "offset_y": 0, "scale": scale, "rotation": 0}
        
        elif effect_type == "彩虹渐变":
            # 通过位置抖动模拟彩虹效果
            rainbow_offset = math.sin(progress * math.pi * 2) * 2 * effect_intensity
            return {"opacity": ease_out, "offset_x": int(rainbow_offset), "offset_y": 0, "scale": 1.0, "rotation": 0}
        
        # 默认返回
        return {"opacity": 1.0, "offset_x": 0, "offset_y": 0, "scale": 1.0, "rotation": 0}
    
    def create_gradient_colors(self, colors: List[Tuple[int, int, int]], num_steps: int) -> List[Tuple[int, int, int]]:
        """创建多色渐变色列表（优化的LRU缓存）
        
        Args:
            colors: 颜色列表
            num_steps: 渐变步数
        
        Returns:
            渐变色列表
        """
        # 生成缓存键
        cache_key = (tuple(colors), num_steps)
        
        # LRU缓存：如果存在，移到末尾
        if cache_key in self._gradient_cache:
            self._gradient_cache.move_to_end(cache_key)
            return self._gradient_cache[cache_key]
        
        if len(colors) < 2:
            result = [colors[0]] * num_steps
        else:
            # 使用NumPy向量化计算，大幅提升性能
            num_colors = len(colors)
            steps_per_segment = num_steps // (num_colors - 1)
            
            # 预分配数组，减少内存分配次数
            result = []
            colors_array = np.array(colors)
            
            for i in range(num_colors - 1):
                start_color = colors_array[i]
                end_color = colors_array[i + 1]
                
                # 向量化计算整个段落的颜色
                ratios = np.linspace(0, 1, steps_per_segment, endpoint=False)
                # 修复广播错误：start_color也需要转为列向量
                segment_colors = start_color[:, np.newaxis] + (end_color - start_color)[:, np.newaxis] * ratios
                result.extend([tuple(c.astype(int)) for c in segment_colors.T])
            
            # 添加最后一个颜色
            result.append(tuple(colors[-1]))
            
            # 确保数量正确
            if len(result) < num_steps:
                result.extend([tuple(colors[-1])] * (num_steps - len(result)))
            result = result[:num_steps]
        
        # LRU缓存管理：超过限制时移除最旧的
        if len(self._gradient_cache) >= self._max_gradient_cache:
            self._gradient_cache.popitem(last=False)
        
        self._gradient_cache[cache_key] = result
        return result
    
    @classmethod
    def clear_gradient_cache(cls):
        """清空渐变色缓存，释放内存"""
        cls._gradient_cache.clear()
        gc.collect()
        print(f"[性能优化] 渐变色缓存已清空")
    
    def create_bold_text(self, draw: ImageDraw.ImageDraw, position: Tuple[int, int], 
                        text: str, font: ImageFont.FreeTypeFont, 
                        fill, bold_level: str, anchor: str = "mm", align: str = "left"):
        """创建加粗文字（优化版）"""
        x, y = position
        
        if bold_level == "常规":
            draw.text((x, y), text, font=font, fill=fill, anchor=anchor, align=align)
        elif bold_level == "粗体":
            offsets = [(0, 0), (1, 0), (0, 1), (1, 1)]
            for dx, dy in offsets:
                draw.text((x + dx, y + dy), text, font=font, fill=fill, anchor=anchor, align=align)
        elif bold_level == "特粗":
            offsets = [(0, 0), (1, 0), (2, 0), (0, 1), (1, 1), (2, 1), (0, 2), (1, 2)]
            for dx, dy in offsets:
                draw.text((x + dx, y + dy), text, font=font, fill=fill, anchor=anchor, align=align)
        elif bold_level == "超粗":
            offsets = [(dx, dy) for dx in range(-1, 3) for dy in range(-1, 3)]
            for dx, dy in offsets:
                draw.text((x + dx, y + dy), text, font=font, fill=fill, anchor=anchor, align=align)
    
    def create_projection(self, text_img: Image.Image, angle: int, 
                         distance: int, intensity: float, blur: int) -> Image.Image:
        """创建投影（阴影效果）
        
        Args:
            text_img: 文字图像
            angle: 投影角度（0-360度）
            distance: 投影距离（像素）
            intensity: 投影强度（0.0-1.0）
            blur: 投影模糊半径（像素）
        
        Returns:
            投影图像
        """
        if distance == 0 or intensity == 0:
            return Image.new('RGBA', text_img.size, (0, 0, 0, 0))
        
        # 计算投影偏移量
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
    
    def create_gradient_text(self, text: str, font: ImageFont.FreeTypeFont,
                            gradient_colors: List[Tuple[int, int, int]], direction: str,
                            stroke_color: Tuple[int, int, int], stroke_size: int,
                            width: int, height: int, align: str = "居中", 
                            x_percent: float = 50.0, bold_level: str = "常规",
                            visible_chars: int = -1) -> Image.Image:
        """创建渐变色文字（支持对齐方式和字体粗细，多行居中优化）"""
        text_layer = Image.new('RGBA', (width, height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(text_layer)
        
        # 映射对齐方式
        pil_align = "left"
        if align == "居中":
            pil_align = "center"
        elif align == "左对齐":
            pil_align = "left"
        elif align == "右对齐":
            pil_align = "right"
            
        # 预计算文字位置（统一使用 _calculate_multiline_metrics）
        char_positions, _, _ = self._calculate_multiline_metrics(draw, text, font, 0, pil_align, width, height)
        
        # 绘制描边
        if stroke_size > 0:
            stroke_rgba = stroke_color + (255,)
            
            # 智能采样策略
            if stroke_size <= 2:
                angle_step = 45
            elif stroke_size <= 5:
                angle_step = 30
            elif stroke_size <= 10:
                angle_step = 22.5
            else:
                angle_step = 15
            
            # 优化：预计算偏移量
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
            
            # 批量绘制描边
            for offset_x, offset_y in offsets:
                for i, (char, x, y) in enumerate(char_positions):
                    if visible_chars >= 0 and i >= visible_chars:
                        break
                    if bold_level == "常规":
                        draw.text((x + offset_x, y + offset_y), char, font=font, fill=stroke_rgba, anchor='mm')
                    else:
                        self.create_bold_text(draw, (x + offset_x, y + offset_y), char, font, stroke_rgba, bold_level, anchor='mm')
        
        # 创建渐变蒙版
        gradient_mask = Image.new('L', (width, height), 0)
        gradient_draw = ImageDraw.Draw(gradient_mask)
        
        # 绘制蒙版文字
        for i, (char, x, y) in enumerate(char_positions):
            if visible_chars >= 0 and i >= visible_chars:
                break
            if bold_level == "常规":
                gradient_draw.text((x, y), char, font=font, fill=255, anchor='mm')
            else:
                self.create_bold_text(gradient_draw, (x, y), char, font, 255, bold_level, anchor='mm')
        
        # 创建渐变图层
        gradient_layer = Image.new('RGB', (width, height))
        pixels = gradient_layer.load()
        
        num_colors = len(gradient_colors)
        
        for y in range(height):
            for x in range(width):
                if direction == "横向":
                    ratio = x / width
                elif direction == "竖向":
                    ratio = y / height
                else:  # 对角
                    ratio = (x + y) / (width + height)
                
                color_idx = int(ratio * (num_colors - 1))
                color_idx = max(0, min(num_colors - 1, color_idx))
                
                pixels[x, y] = gradient_colors[color_idx]
        
        # 应用蒙版
        text_layer.paste(gradient_layer, (0, 0), gradient_mask)
        
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

    def create_stroke_text(self, text: str, font: ImageFont.FreeTypeFont, 
                          text_color: Tuple[int, int, int], stroke_color: Tuple[int, int, int], 
                          stroke_size: int, width: int, height: int, 
                          align: str = "居中", x_percent: float = 50.0, bold_level: str = "常规",
                          visible_chars: int = -1) -> Image.Image:
        """创建描边文字（支持对齐方式和字体粗细，多行居中优化）"""
        text_layer = Image.new('RGBA', (width, height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(text_layer)
        
        # 映射对齐方式
        pil_align = "left"
        if align == "居中":
            pil_align = "center"
        elif align == "左对齐":
            pil_align = "left"
        elif align == "右对齐":
            pil_align = "right"
            
        if stroke_size == 0:
            # 无描边
            self._draw_multiline_text_with_spacing(draw, text, font, text_color + (255,), 
                                                 width, height, 0, pil_align, bold_level, visible_chars)
        else:
            # 有描边
            stroke_rgba = stroke_color + (255,)
            
            # 智能采样策略
            if stroke_size <= 2:
                angle_step = 45
            elif stroke_size <= 5:
                angle_step = 30
            elif stroke_size <= 10:
                angle_step = 22.5
            else:
                angle_step = 15
            
            # 优化：预计算偏移量
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
            
            # 计算文字位置
            char_positions, _, _ = self._calculate_multiline_metrics(draw, text, font, 0, pil_align, width, height)
            
            # 批量绘制描边
            for offset_x, offset_y in offsets:
                for i, (char, x, y) in enumerate(char_positions):
                    if visible_chars >= 0 and i >= visible_chars:
                        break
                    if bold_level == "常规":
                        draw.text((x + offset_x, y + offset_y), char, font=font, fill=stroke_rgba, anchor='mm')
                    else:
                        self.create_bold_text(draw, (x + offset_x, y + offset_y), char, font, stroke_rgba, bold_level, anchor='mm')
            
            # 绘制文字
            for i, (char, x, y) in enumerate(char_positions):
                if visible_chars >= 0 and i >= visible_chars:
                    break
                if bold_level == "常规":
                    draw.text((x, y), char, font=font, fill=text_color + (255,), anchor='mm')
                else:
                    self.create_bold_text(draw, (x, y), char, font, text_color + (255,), bold_level, anchor='mm')
        
        return text_layer
    
    def create_scrolling_credits(self, text: str, font: ImageFont.FreeTypeFont,
                                text_color: Tuple[int, int, int], stroke_color: Tuple[int, int, int],
                                stroke_size: int, width: int, height: int,
                                scroll_position: float, bold_level: str = "常规") -> Image.Image:
        """创建滚动字幕（电影片尾效果，支持字体粗细）
        
        Args:
            text: 字幕文本
            font: 字体对象
            text_color: 文字颜色
            stroke_color: 描边颜色
            stroke_size: 描边大小
            width: 画布宽度
            height: 画布高度
            scroll_position: 滚动位置
            bold_level: 字体粗细（常规/粗体/特粗/超粗）
        
        Returns:
            滚动字幕图像
        """
        # 创建足够大的画布来容纳所有文本
        lines = text.split('\n')
        line_height = font.size + 20  # 行间距
        total_height = len(lines) * line_height + height * 2
        
        # 创建滚动画布
        scroll_canvas = Image.new('RGBA', (width, total_height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(scroll_canvas)
        
        # 绘制每一行（居中对齐）
        y_offset = height  # 从底部开始
        for line in lines:
            if not line.strip():
                y_offset += line_height // 2
                continue
            
            # 测量文本宽度（用于调试）
            bbox = draw.textbbox((0, 0), line, font=font)
            text_width = bbox[2] - bbox[0]
            
            # 绘制描边（支持字体粗细）
            if stroke_size > 0:
                stroke_rgba = stroke_color + (255,)
                for angle in range(0, 360, 20):
                    for distance in range(1, stroke_size + 1):
                        offset_x = int(math.cos(math.radians(angle)) * distance)
                        offset_y = int(math.sin(math.radians(angle)) * distance)
                        if bold_level == "常规":
                            draw.text((width // 2 + offset_x, y_offset + offset_y), 
                                     line, font=font, fill=stroke_rgba, anchor='mm')
                        else:
                            self.create_bold_text(draw, (width // 2 + offset_x, y_offset + offset_y), 
                                                line, font, stroke_rgba, bold_level, 'mm')
            
            # 绘制文字（居中，支持字体粗细）
            if bold_level == "常规":
                draw.text((width // 2, y_offset), line, font=font, 
                         fill=text_color + (255,), anchor='mm')
            else:
                self.create_bold_text(draw, (width // 2, y_offset), line, font, 
                                    text_color + (255,), bold_level, 'mm')
            y_offset += line_height
        
        # 裁剪到可见区域
        visible_canvas = Image.new('RGBA', (width, height), (0, 0, 0, 0))
        
        # 计算滚动偏移
        scroll_y = int(scroll_position)
        
        # 裁剪并粘贴
        if 0 <= scroll_y < total_height - height:
            crop_box = (0, scroll_y, width, scroll_y + height)
            visible_canvas = scroll_canvas.crop(crop_box)
        
        return visible_canvas
    
    def calculate_optimal_font_size(self, text: str, font_name: str, initial_size: int,
                                    canvas_width: int, canvas_height: int, 
                                    stroke_size: int, align: str) -> int:
        """计算最适合画布的字号（单行文本）
        
        Args:
            text: 字幕文本
            font_name: 字体名称
            initial_size: 初始字号
            canvas_width: 画布宽度
            canvas_height: 画布高度
            stroke_size: 描边大小
            align: 对齐方式
        
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
            
            # 计算文本边界（包括描边）
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
    
    def calculate_optimal_font_size_for_scrolling(self, text: str, font_name: str, initial_size: int,
                                                   canvas_width: int, stroke_size: int) -> int:
        """计算滚动字幕的最优字号（检查所有行）
        
        Args:
            text: 字幕文本（多行）
            font_name: 字体名称
            initial_size: 初始字号
            canvas_width: 画布宽度
            stroke_size: 描边大小
        
        Returns:
            最适合的字号
        """
        # 留5%边距
        max_width = int(canvas_width * 0.95)
        
        # 分割成行
        lines = text.split('\n')
        
        # 从初始字号开始尝试
        test_size = initial_size
        
        for iteration in range(20):  # 最多尝试20次
            font = self.get_cached_font(font_name, test_size)
            if font is None:
                break
            
            # 创建临时图像测量尺寸
            temp_img = Image.new('RGBA', (1, 1))
            temp_draw = ImageDraw.Draw(temp_img)
            
            # 找出最宽的行
            max_line_width = 0
            for line in lines:
                if not line.strip():
                    continue
                bbox = temp_draw.textbbox((0, 0), line, font=font)
                line_width = bbox[2] - bbox[0] + stroke_size * 2
                max_line_width = max(max_line_width, line_width)
            
            # 检查是否适合
            if max_line_width <= max_width:
                # 适合，返回此字号
                if iteration == 0:
                    # 首次检查就适合，无需调整
                    return test_size
                else:
                    print(f"[滚动字幕] 自动调整字号: {initial_size}px → {test_size}px")
                    return test_size
            
            # 不适合，缩小字号
            scale = max_width / max_line_width
            new_test_size = max(12, int(test_size * scale * 0.95))  # 最小12px
            
            # 如果字号变化太小，结束循环
            if new_test_size >= test_size or abs(new_test_size - test_size) < 2:
                break
            
            test_size = new_test_size
        
        if test_size != initial_size:
            print(f"[滚动字幕] 自动调整字号: {initial_size}px → {test_size}px")
        
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
        """裁剪超出画布的字幕边缘（已废弃，保留用于兼容）"""
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

    def _build_srt_from_segments(self, segments: List[SubtitleSegment]) -> str:
        out_dir = folder_paths.get_output_directory()
        srt_path = os.path.join(out_dir, f"subtitle_{os.urandom(4).hex()}.srt")
        lines = []
        for seg in segments:
            lines.append(str(seg.index))
            lines.append(f"{self._seconds_to_srt(seg.start_time)} --> {self._seconds_to_srt(seg.end_time)}")
            lines.append(seg.text)
            lines.append("")
        with open(srt_path, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))
        return srt_path

    def _seconds_to_srt(self, t: float) -> str:
        t = max(0.0, t)
        h = int(t // 3600)
        m = int((t % 3600) // 60)
        s = int(t % 60)
        ms = int(round((t - int(t)) * 1000))
        return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"

    def _run_ffmpeg_burn(self, src_path: str, srt_path: str, container: str,
                         字体名称: str, 字体大小: int, 描边大小: int,
                         位置预设: str, y_percent: float, 视频质量: str):
        ffmpeg_path = shutil.which("ffmpeg")
        if not ffmpeg_path:
            raise RuntimeError("未找到 ffmpeg")
        out_dir = folder_paths.get_output_directory()
        base_name = os.path.splitext(os.path.basename(src_path))[0]
        out_ext = "mp4" if container == "mp4" else "mkv"
        out_path = os.path.join(out_dir, f"{base_name}_sub_{os.urandom(3).hex()}.{out_ext}")
        align_map = {
            "底部居中": "2",
            "顶部居中": "6",
            "左下角": "1",
            "右下角": "3",
            "左上角": "5",
            "右上角": "7",
            "正中央": "9",
            "底部三分之一": "2",
            "顶部三分之一": "6",
            "自定义": "2",
        }
        align_val = align_map.get(位置预设, "2")
        font_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "font")
        margin_v = 20
        if 位置预设 in ["底部居中", "底部三分之一", "自定义"]:
            margin_v = max(0, int((100.0 - y_percent) / 100.0 * 1080))
        elif 位置预设 in ["顶部居中", "顶部三分之一"]:
            margin_v = max(0, int(y_percent / 100.0 * 1080))
        quality_map = {"高": ("18", "fast"), "中": ("23", "medium"), "低": ("28", "slow")}
        crf, preset = quality_map.get(视频质量, ("23", "medium"))
        vf_arg = f"subtitles={srt_path}:fontsdir={font_dir}:force_style='FontName={字体名称},FontSize={字体大小},Outline={描边大小},Alignment={align_val},MarginV={margin_v}'"
        esc_srt = srt_path.replace("\\", "/").replace(":", "\\:").replace("'", "\\'")
        esc_font = font_dir.replace("\\", "/").replace(":", "\\:").replace("'", "\\'")
        vf_arg = f"subtitles={esc_srt}:fontsdir={esc_font}:force_style='FontName={字体名称},FontSize={字体大小},Outline={描边大小},Alignment={align_val},MarginV={margin_v}'"
        cmd = [
            ffmpeg_path, "-y",
            "-i", src_path,
            "-vf", vf_arg,
            "-c:v", "libx264",
            "-preset", preset,
            "-crf", crf,
            "-pix_fmt", "yuv420p",
            "-c:a", "aac",
            "-b:a", "192k",
            out_path
        ]
        result = subprocess.run(cmd, capture_output=True)
        try:
            os.remove(srt_path)
        except:
            pass
        if result.returncode != 0:
            stderr = result.stderr.decode("utf-8", errors="ignore") if isinstance(result.stderr, (bytes, bytearray)) else (result.stderr or "")
            if not stderr:
                stdout = result.stdout.decode("utf-8", errors="ignore") if isinstance(result.stdout, (bytes, bytearray)) else (result.stdout or "")
                stderr = stdout
            raise RuntimeError(f"FFmpeg执行失败: {stderr[-800:]}")
        return self._load_video_result(out_path)

    def _load_video_result(self, video_path: str):
        if cv2 is None:
            raise ImportError("需要 opencv-python")
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            raise Exception("无法打开生成的视频文件")
        frames = []
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frame = frame.astype(np.float32) / 255.0
            frames.append(frame)
        cap.release()
        if not frames:
            raise Exception("未读取到帧")
        images = torch.from_numpy(np.stack(frames, axis=0))
        return images
    
    def wrap_text_smart(self, text: str, font: ImageFont.FreeTypeFont, max_width: int, max_lines: int) -> str:
        """智能文本换行"""
        if max_lines <= 1 or not text or '\n' in text:
            return text
        
        try:
            draw = ImageDraw.Draw(Image.new('L', (1, 1)))
        except Exception:
            return text
        
        lines: List[str] = []
        current = ""
        
        for idx, ch in enumerate(text):
            next_current = current + ch
            try:
                bbox = draw.textbbox((0, 0), next_current, font=font)
                next_width = bbox[2] - bbox[0]
            except Exception:
                next_width = 0
            
            if current and next_width > max_width:
                lines.append(current)
                if len(lines) >= max_lines - 1:
                    remaining = text[idx:]
                    lines.append(remaining)
                    return "\n".join(lines)
                current = ch
            else:
                current = next_current
        
        if current:
            lines.append(current)
        
        if len(lines) <= 1:
            return text
        
        return "\n".join(lines)

    def add_subtitle_pro(self, images, 字幕格式, 字幕内容, 视频帧率,
                        开始时间, 结束时间, 每段显示时长, 字幕间隔,
                        字体选择, 字体大小, 最大行数, 字体粗细, 字体颜色, 
                        描边大小, 描边颜色, 不透明度,
                        投影角度, 投影距离, 投影强度, 投影模糊,
                        位置预设, 位置X百分比, 位置Y百分比, 对齐方式,
                        动画特效, 特效强度, 特效时长, 滚动速度, 去除符号, 限定在画布内,
                        渐变色数量="无",
                        渐变色1="#FFFFFF", 渐变色2="#FF0000", 渐变色3="#00FF00",
                        渐变方向="横向"):
        """添加专业字幕（支持丰富特效、渐变色、字体粗细和投影）"""
        
        batch_size = images.shape[0]
        height = images.shape[1]
        width = images.shape[2]
        video_duration = batch_size / 视频帧率
        
        # 解析字幕
        if 动画特效 == "滚动字幕":
            # 滚动字幕模式：不解析为段落，直接使用整个文本
            segments = []
        elif 字幕格式 == "SRT格式":
            segments = self.parse_srt_subtitles(字幕内容)
        elif 字幕格式 == "括号格式":
            segments = self.parse_parenthesis_subtitles(字幕内容)
        elif 字幕格式 == "无时间戳":
            segments = self.parse_notimestamp_subtitles(字幕内容, 每段显示时长, 字幕间隔, 开始时间, 结束时间)
        else:
            segments = self.parse_simple_subtitles(字幕内容)
        
        # 获取字体
        font = self.get_cached_font(字体选择, 字体大小)
        if font is None:
            print("错误: 字体加载失败")
            return (images, 开始时间, 结束时间)
            
        # 智能换行处理
        if 动画特效 != "滚动字幕" and 最大行数 > 1 and segments:
            # 留5%边距
            wrap_width = int(width * 0.9)
            print(f"[智能换行] 最大行数: {最大行数}, 限制宽度: {wrap_width}px")
            for seg in segments:
                seg.text = self.wrap_text_smart(seg.text, font, wrap_width, 最大行数)
        
        # 解析颜色
        text_color = self.parse_color(字体颜色)
        stroke_color = self.parse_color(描边颜色)
        
        # 渐变色处理
        gradient_colors_list = None
        if 渐变色数量 != "无":
            color_count = int(渐变色数量)
            gradient_color_inputs = [渐变色1, 渐变色2, 渐变色3]
            gradient_colors = [self.parse_color(gradient_color_inputs[i]) for i in range(color_count)]
            gradient_colors_list = self.create_gradient_colors(gradient_colors, width)
            print(f"[渐变色] 启用{color_count}色渐变，方向: {渐变方向}")
        
        # 获取位置
        if 位置预设 != "自定义":
            x_percent, y_percent = self.get_position_preset(位置预设, width, height)
        else:
            x_percent = 位置X百分比
            y_percent = 位置Y百分比
        
        output_images = []
        
        # 滚动字幕模式
        if 动画特效 == "滚动字幕":
            print(f"[专业字幕] 滚动字幕模式")
            
            # 应用符号去除
            processed_content = self.remove_punctuation(字幕内容, 去除符号)
            if 去除符号 != "不去除":
                print(f"[符号去除] 模式: {去除符号}")
            
            # 如果需要限定在画布内且是自动缩放模式，先计算合适的字号
            current_font_size = 字体大小
            if 限定在画布内 == "自动缩放":
                current_font_size = self.calculate_optimal_font_size_for_scrolling(
                    processed_content, 字体选择, 字体大小, width, 描边大小
                )
                # 如果调整了字号，重新获取字体
                if current_font_size != 字体大小:
                    font = self.get_cached_font(字体选择, current_font_size)
                    if font is None:
                        print(f"[滚动字幕] 警告: 无法加载字号{current_font_size}的字体，使用原字号")
                        font = self.get_cached_font(字体选择, 字体大小)
                        current_font_size = 字体大小
            
            # 进度日志间隔
            progress_interval = max(1, batch_size // 10)  # 每10%输出一次
            
            # GPU内存优化：批量处理前先移到CPU
            images_cpu = images.cpu()
            
            for i in range(batch_size):
                # 定期清理GPU显存（每100帧清理一次）
                if i > 0 and i % 100 == 0 and torch.cuda.is_available():
                    torch.cuda.empty_cache()
                
                # 进度提示（每10%或每50帧）
                if i % progress_interval == 0 and i > 0:
                    progress_pct = (i / batch_size) * 100
                    print(f"[滚动字幕] 进度: {i}/{batch_size} 帧 ({progress_pct:.1f}%)")
                
                img_array = images_cpu[i].numpy()
                img_array = (img_array * 255).astype(np.uint8)
                img_pil = Image.fromarray(img_array)
                
                # 计算滚动位置
                current_time = i / 视频帧率
                scroll_position = current_time * 滚动速度
                
                # 创建滚动字幕（支持字体粗细）
                text_img = self.create_scrolling_credits(
                    processed_content, font, text_color, stroke_color, 
                    描边大小, width, height, scroll_position, 字体粗细
                )
                
                # 应用透明度
                if 不透明度 < 1.0:
                    alpha_mask = text_img.split()[3].point(lambda p: int(p * 不透明度))
                    text_img.putalpha(alpha_mask)
                
                # 添加投影效果（滚动字幕）
                if 投影距离 > 0 and 投影强度 > 0:
                    final_layer = Image.new('RGBA', (width, height), (0, 0, 0, 0))
                    projection = self.create_projection(text_img, 投影角度, 投影距离, 投影强度, 投影模糊)
                    try:
                        final_layer = Image.alpha_composite(final_layer, projection)
                        final_layer = Image.alpha_composite(final_layer, text_img)
                        text_img = final_layer
                    except Exception as e:
                        print(f"警告: 滚动字幕投影合成失败 - {e}")
                
                # 合成
                img_pil = img_pil.convert('RGBA')
                result = Image.alpha_composite(img_pil, text_img)
                result = result.convert('RGB')
                
                result_array = np.array(result).astype(np.float32) / 255.0
                output_images.append(result_array)
            
            output_tensor = torch.from_numpy(np.stack(output_images))
            
            # 清理临时数据
            del output_images
            gc.collect()
            
            # 清理GPU显存
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
                torch.cuda.synchronize()
            
            print(f"[滚动字幕] ✓ 完成 {batch_size} 帧，字号: {current_font_size}px，时长: {video_duration:.2f}秒")
            return (output_tensor, 开始时间, video_duration)
        
        # 普通字幕模式
        if not segments:
            print("警告: 未解析到任何字幕段")
            return (images, 开始时间, 结束时间)
        
        # 应用符号去除到所有字幕段
        if 去除符号 != "不去除":
            for seg in segments:
                seg.text = self.remove_punctuation(seg.text, 去除符号)
            print(f"[符号去除] 模式: {去除符号}，已处理 {len(segments)} 段字幕")
        
        print(f"[专业字幕] 成功解析 {len(segments)} 段字幕, 特效: {动画特效}")
        
        # 如果启用自动缩放，预先计算所有段落的统一字号
        unified_font_size = 字体大小
        if 限定在画布内 == "自动缩放":
            print(f"[画布限定] 开始计算统一字号...")
            min_font_size = 字体大小
            
            # 遍历所有字幕段，找出最严格的字号限制
            for seg in segments:
                segment_font_size = self.calculate_optimal_font_size(
                    seg.text, 字体选择, 字体大小,
                    width, height, 描边大小, 对齐方式
                )
                min_font_size = min(min_font_size, segment_font_size)
            
            # 使用最小字号作为统一字号
            if min_font_size != 字体大小:
                unified_font_size = min_font_size
                font = self.get_cached_font(字体选择, unified_font_size)
                if font is None:
                    print(f"[画布限定] 警告: 无法加载字号{unified_font_size}的字体，使用原字号")
                    font = self.get_cached_font(字体选择, 字体大小)
                    unified_font_size = 字体大小
                else:
                    print(f"[画布限定] ✓ 统一字号: {字体大小}px → {unified_font_size}px（全视频一致）")
        
        segment_text_cache: Dict[int, Image.Image] = {}
        if 动画特效 != "打字机":
            for seg in segments:
                display_text_cache = seg.text
                if gradient_colors_list:
                    cached_img = self.create_gradient_text(
                        display_text_cache, font, gradient_colors_list, 渐变方向,
                        stroke_color, 描边大小, width * 2, height * 2, 对齐方式, x_percent, 字体粗细
                    )
                else:
                    cached_img = self.create_stroke_text(
                        display_text_cache, font, text_color, stroke_color, 
                        描边大小, width * 2, height * 2, 对齐方式, x_percent, 字体粗细
                    )
                segment_text_cache[seg.index] = cached_img
        
        # 生成时间轴
        timeline_info = []
        for seg in segments:
            timeline_info.append(f"[{seg.start_time:.2f}s-{seg.end_time:.2f}s] {seg.text[:50]}")
        timeline_str = "\n".join(timeline_info)
        
        # 进度日志间隔
        progress_interval = max(1, batch_size // 10)  # 每10%输出一次
        
        # GPU内存优化：批量处理前先移到CPU
        images_cpu = images.cpu()
        
        # 处理每一帧
        for i in range(batch_size):
            # 定期清理资源（每100帧清理一次）
            if i > 0 and i % 100 == 0:
                if torch.cuda.is_available():
                    torch.cuda.empty_cache()
                # 强制垃圾回收，防止内存累积
                gc.collect()
            
            # 进度提示（大量帧时）
            if batch_size > 100 and i % progress_interval == 0 and i > 0:
                progress_pct = (i / batch_size) * 100
                print(f"[专业字幕] 进度: {i}/{batch_size} 帧 ({progress_pct:.1f}%)")
            img_array = images_cpu[i].numpy()
            img_array = (img_array * 255).astype(np.uint8)
            img_pil = Image.fromarray(img_array)
            
            current_time = i / 视频帧率
            
            # 查找当前字幕
            current_segment = None
            for seg in segments:
                if seg.start_time <= current_time < seg.end_time:
                    current_segment = seg
                    break
            
            if current_segment is None:
                result = img_pil.convert('RGB')
                result_array = np.array(result).astype(np.float32) / 255.0
                output_images.append(result_array)
                del img_pil, result  # 清理PIL对象
                continue
            
            # 应用动画特效
            anim_params = self.apply_animation_effect(
                i, current_segment, current_time, 动画特效, 
                特效强度, 特效时长, 视频帧率, width
            )
            
            # 打字机效果特殊处理
            display_text = current_segment.text
            visible_chars = -1
            if 动画特效 == "打字机" and "char_reveal" in anim_params:
                # 计算需要显示的字符数（排除换行符，因为渲染时只计算可见字符）
                clean_text_len = len(current_segment.text.replace('\n', ''))
                visible_chars = int(clean_text_len * anim_params.get("char_reveal", 1.0))
                
                # 如果没有可见字符，输出空帧
                if visible_chars == 0:
                    result = img_pil.convert('RGB')
                    result_array = np.array(result).astype(np.float32) / 255.0
                    output_images.append(result_array)
                    del img_pil, result  # 清理PIL对象
                    continue
            
            # 使用统一字号（如果启用了自动缩放，已在前面计算）
            # 创建字幕图层（支持渐变色和字体粗细）
            if 动画特效 != "打字机" and current_segment.index in segment_text_cache:
                text_img = segment_text_cache[current_segment.index].copy()
            else:
                if gradient_colors_list:
                    text_img = self.create_gradient_text(
                        display_text, font, gradient_colors_list, 渐变方向,
                        stroke_color, 描边大小, width * 2, height * 2, 对齐方式, 50.0, 字体粗细,
                        visible_chars=visible_chars
                    )
                else:
                    text_img = self.create_stroke_text(
                        display_text, font, text_color, stroke_color, 
                        描边大小, width * 2, height * 2, 对齐方式, 50.0, 字体粗细,
                        visible_chars=visible_chars
                    )
            
            # 应用缩放
            if anim_params.get("scale", 1.0) != 1.0 and anim_params["scale"] > 0:
                new_size = (
                    max(1, int(text_img.width * anim_params["scale"])),
                    max(1, int(text_img.height * anim_params["scale"]))
                )
                text_img = text_img.resize(new_size, Image.LANCZOS)
            
            # 应用旋转
            if anim_params.get("rotation", 0) != 0:
                text_img = text_img.rotate(-anim_params["rotation"], expand=True, resample=Image.BICUBIC)
            
            # 应用透明度
            combined_opacity = 不透明度 * anim_params.get("opacity", 1.0)
            if combined_opacity < 1.0:
                alpha_mask = text_img.split()[3].point(lambda p: int(p * combined_opacity))
                text_img.putalpha(alpha_mask)
            
            # 创建最终图层
            final_layer = Image.new('RGBA', (width, height), (0, 0, 0, 0))
            
            # 计算位置
            text_x = int(width * x_percent / 100.0) + anim_params.get("offset_x", 0)
            text_y = int(height * y_percent / 100.0) + anim_params.get("offset_y", 0)
            
            paste_x = text_x - text_img.width // 2
            paste_y = text_y - text_img.height // 2
            
            # 限定在画布内处理（裁剪模式）
            if 限定在画布内 == "按字裁剪":
                text_img, paste_x, paste_y = self.constrain_to_canvas_by_char(
                    text_img, paste_x, paste_y, width, height
                )
            
            # 添加投影效果
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
            
            # 显式清理PIL对象，释放资源（防止Windows socket缓冲区耗尽）
            del img_pil, text_img, final_layer, result
            
            # 定期强制垃圾回收（每50帧）
            if i % 50 == 0:
                gc.collect()
        
        # 转换为tensor（使用stack直接从列表，更高效）
        output_tensor = torch.from_numpy(np.stack(output_images))
        
        # 清理临时数据，释放内存
        del output_images
        gc.collect()
        
        # 清理GPU显存
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
            torch.cuda.synchronize()
        
        # 计算实际的字幕时间范围
        actual_start_time = segments[0].start_time if segments else 开始时间
        actual_end_time = segments[-1].end_time if segments else 结束时间
        
        print(f"[专业字幕] 完成: 处理{batch_size}帧, 字幕{len(segments)}段")
        
        return (output_tensor, actual_start_time, actual_end_time)


# 节点已在 __init__.py 中统一注册，此处不再重复注册
