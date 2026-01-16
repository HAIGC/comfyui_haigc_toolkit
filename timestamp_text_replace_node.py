"""
时间戳文本替换节点(专业版) - v1.0.1
用于智能替换和编辑时间戳字幕文本的专业工具

核心功能:
1. 批量文本替换 - 按时间排序或索引排序一一对应替换
2. 智能匹配替换 - 按关键字、正则表达式精准替换
3. 文本增强 - 添加前缀/后缀、文本转换
4. 段落管理 - 删除、合并、拆分指定段落
5. 批量操作 - 支持多种时间戳格式(SRT/括号/简单格式)
6. 🆕 智能跳过 - 替换文本为空时自动保持原文不变

更新日志:
v1.0.1 (2025-11-06)
  - 新增: 替换文本为空时智能跳过,保持原文不变
  - 优化: 避免误操作清空所有文本内容
  - 改进: 详细日志提示跳过替换的原因

v1.0.0 (2025-11-06)
  - 初始版本发布

作者: HAIGC Toolkit
日期: 2025-11-06
"""

import re
from typing import List, Tuple, Dict, Optional
from dataclasses import dataclass

@dataclass
class TimestampSegment:
    """时间戳段落数据结构"""
    index: int
    start_time: float
    end_time: float
    text: str
    original_format: str  # 保存原始格式(srt/bracket/simple)
    
    def __repr__(self):
        return f"[{self.index}] {self.start_time:.2f}s-{self.end_time:.2f}s: {self.text[:20]}"


class TimestampTextReplaceNode:
    """时间戳文本替换节点 - 专业文本编辑工具"""
    
    def __init__(self):
        self.type = "HAIGC_TimestampTextReplace"
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                # === 📝 输入数据 ===
                "时间戳文本": ("STRING", {
                    "default": """(0.0, 2.0) 这是视频添加时间戳字幕的节点
(2.0, 4.0) 作者网名：HAIGC(全网同名)
(4.0, 6.0) 作者微信号：HAIGC1994
(6.0, 8.0) 剪映接口只有早上到下午3点左右可以用""",
                    "multiline": True,
                    "forceInput": False  # 允许从其他节点输入
                }),
                
                "时间戳格式": (["自动检测", "SRT格式", "括号格式", "简单格式"], {
                    "default": "自动检测"
                }),
                
                # === 🔄 替换模式 ===
                "替换模式": ([
                    "批量替换(按时间排序)",
                    "批量替换(按索引排序)", 
                    "关键字替换",
                    "正则表达式替换",
                    "指定段落替换",
                    "文本增强",
                    "无(仅格式转换)"
                ], {
                    "default": "批量替换(按时间排序)"
                }),
                
                # === 📄 替换内容 ===
                "替换文本": ("STRING", {
                    "default": "",
                    "multiline": True
                }),
                
                # === 🔍 高级选项 ===
                "关键字_正则": ("STRING", {
                    "default": "",
                    "multiline": False
                }),
                
                "指定段落索引": ("STRING", {
                    "default": "1,2,3",
                    "multiline": False
                }),
                
                "文本增强选项": ([
                    "无",
                    "添加前缀",
                    "添加后缀",
                    "首字母大写",
                    "全部大写",
                    "全部小写",
                    "删除空格",
                    "删除换行"
                ], {
                    "default": "无"
                }),
                
                "前缀_后缀内容": ("STRING", {
                    "default": "",
                    "multiline": False
                }),
                
                # === ⚙️ 处理选项 ===
                "智能分段策略": ([
                    "按行分段",
                    "按字数均分",
                    "按标点分段",
                    "严格按字数"
                ], {
                    "default": "按行分段"
                }),
                
                "保留空行": (["是", "否"], {
                    "default": "否"
                }),
                
                "自动去除多余空格": (["是", "否"], {
                    "default": "是"
                }),
                
                # === 📤 输出格式 ===
                "输出格式": (["保持原格式", "SRT格式", "括号格式", "简单格式", "纯文本"], {
                    "default": "保持原格式"
                }),
                
                # === 🐛 调试选项 ===
                "显示详细日志": (["否", "是"], {
                    "default": "否"
                }),
            }
        }
    
    RETURN_TYPES = ("STRING", "STRING", "INT")
    RETURN_NAMES = ("处理后的时间戳文本", "处理报告", "段落数")
    FUNCTION = "replace_timestamp_text"
    CATEGORY = "haigc_toolkit/subtitle"
    
    def replace_timestamp_text(
        self,
        时间戳文本: str,
        时间戳格式: str,
        替换模式: str,
        替换文本: str,
        关键字_正则: str,
        指定段落索引: str,
        文本增强选项: str,
        前缀_后缀内容: str,
        智能分段策略: str,
        保留空行: str,
        自动去除多余空格: str,
        输出格式: str,
        显示详细日志: str
    ) -> Tuple[str, str, int]:
        """主处理函数"""
        
        if 显示详细日志 == "是":
            print("\n" + "="*60)
            print("🔄 时间戳文本替换节点 v1.0.0")
            print("="*60)
        
        # 步骤1: 解析时间戳文本
        if 显示详细日志 == "是":
            print(f"\n[步骤1] 📝 解析时间戳文本...")
            print(f"  格式: {时间戳格式}")
        
        segments = self.parse_timestamp_text(时间戳文本, 时间戳格式)
        
        if not segments:
            return ("", "❌ 错误: 无法解析时间戳文本", 0)
        
        if 显示详细日志 == "是":
            print(f"✅ 成功解析 {len(segments)} 段字幕")
            for seg in segments[:3]:
                print(f"  {seg}")
            if len(segments) > 3:
                print(f"  ... 还有 {len(segments) - 3} 段")
        
        # 步骤2: 根据模式执行替换
        if 显示详细日志 == "是":
            print(f"\n[步骤2] 🔄 执行替换...")
            print(f"  模式: {替换模式}")
        
        original_texts = [seg.text for seg in segments]
        
        # 智能判断：替换文本为空时，跳过批量替换模式（保持原文）
        should_skip_replace = False
        if 替换模式 in ["批量替换(按时间排序)", "批量替换(按索引排序)", "指定段落替换"]:
            if not 替换文本 or not 替换文本.strip():
                should_skip_replace = True
                if 显示详细日志 == "是":
                    print(f"⚠️  替换文本为空，跳过替换（保持原文不变）")
        
        if not should_skip_replace:
            if 替换模式 == "批量替换(按时间排序)":
                segments = self.batch_replace_by_time(segments, 替换文本, 智能分段策略, 保留空行 == "是")
            
            elif 替换模式 == "批量替换(按索引排序)":
                segments = self.batch_replace_by_index(segments, 替换文本, 智能分段策略, 保留空行 == "是")
            
            elif 替换模式 == "关键字替换":
                segments = self.keyword_replace(segments, 关键字_正则, 替换文本)
            
            elif 替换模式 == "正则表达式替换":
                segments = self.regex_replace(segments, 关键字_正则, 替换文本)
            
            elif 替换模式 == "指定段落替换":
                segments = self.specific_segment_replace(segments, 指定段落索引, 替换文本, 智能分段策略)
            
            elif 替换模式 == "文本增强":
                segments = self.text_enhancement(segments, 文本增强选项, 前缀_后缀内容)
        
        # 步骤3: 文本清理
        if 自动去除多余空格 == "是":
            for seg in segments:
                seg.text = ' '.join(seg.text.split())
        
        # 步骤4: 生成输出
        if 显示详细日志 == "是":
            print(f"\n[步骤3] 📤 生成输出...")
            print(f"  输出格式: {输出格式}")
        
        output_text = self.generate_output(segments, 输出格式)
        
        # 生成报告
        report = self.generate_report(
            segments, original_texts, 替换模式, 
            时间戳格式, 输出格式
        )
        
        if 显示详细日志 == "是":
            print("\n" + "="*60)
            print("✅ 处理完成")
            print("="*60 + "\n")
        
        return (output_text, report, len(segments))
    
    # ========== 解析函数 ==========
    
    def parse_timestamp_text(self, content: str, format_type: str) -> List[TimestampSegment]:
        """解析时间戳文本"""
        if format_type == "自动检测":
            format_type = self.detect_format(content)
        
        if format_type == "SRT格式":
            return self.parse_srt_format(content)
        elif format_type == "括号格式":
            return self.parse_bracket_format(content)
        elif format_type == "简单格式":
            return self.parse_simple_format(content)
        else:
            return []
    
    def detect_format(self, content: str) -> str:
        """自动检测时间戳格式"""
        if '-->' in content and re.search(r'\d{2}:\d{2}:\d{2}', content):
            return "SRT格式"
        elif re.search(r'\([\d\.]+\s*,\s*[\d\.]+\)', content):
            return "括号格式"
        elif re.search(r'[\d\.]+\s*-\s*[\d\.]+', content):
            return "简单格式"
        return "未知格式"
    
    def parse_srt_format(self, content: str) -> List[TimestampSegment]:
        """解析SRT格式: 
        1
        00:00:00,000 --> 00:00:01,000
        文本内容
        """
        segments = []
        blocks = re.split(r'\n\s*\n', content.strip())
        
        for block in blocks:
            lines = block.strip().split('\n')
            if len(lines) < 3:
                continue
            
            try:
                index = int(lines[0].strip())
                time_line = lines[1].strip()
                
                # 解析时间
                match = re.match(r'(\d{2}:\d{2}:\d{2}[,\.]\d{3})\s*-->\s*(\d{2}:\d{2}:\d{2}[,\.]\d{3})', time_line)
                if not match:
                    continue
                
                start_time = self.srt_time_to_seconds(match.group(1))
                end_time = self.srt_time_to_seconds(match.group(2))
                text = '\n'.join(lines[2:])
                
                segments.append(TimestampSegment(
                    index=index,
                    start_time=start_time,
                    end_time=end_time,
                    text=text,
                    original_format="srt"
                ))
            except Exception as e:
                print(f"[警告] SRT段落解析失败: {e}")
                continue
        
        return segments
    
    def parse_bracket_format(self, content: str) -> List[TimestampSegment]:
        """解析括号格式: (0.0, 1.5) 文本"""
        segments = []
        lines = content.strip().split('\n')
        
        index = 1
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            try:
                match = re.match(r'\(([\d\.]+)\s*,\s*([\d\.]+)\)\s*(.+)', line)
                if not match:
                    continue
                
                start_time = float(match.group(1))
                end_time = float(match.group(2))
                text = match.group(3)
                
                segments.append(TimestampSegment(
                    index=index,
                    start_time=start_time,
                    end_time=end_time,
                    text=text,
                    original_format="bracket"
                ))
                index += 1
            except Exception as e:
                print(f"[警告] 括号格式解析失败: {e}")
                continue
        
        return segments
    
    def parse_simple_format(self, content: str) -> List[TimestampSegment]:
        """解析简单格式: 0.0-1.5 文本"""
        segments = []
        lines = content.strip().split('\n')
        
        index = 1
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            try:
                match = re.match(r'([\d\.]+)\s*-\s*([\d\.]+)\s+(.+)', line)
                if not match:
                    continue
                
                start_time = float(match.group(1))
                end_time = float(match.group(2))
                text = match.group(3)
                
                segments.append(TimestampSegment(
                    index=index,
                    start_time=start_time,
                    end_time=end_time,
                    text=text,
                    original_format="simple"
                ))
                index += 1
            except Exception as e:
                print(f"[警告] 简单格式解析失败: {e}")
                continue
        
        return segments
    
    def srt_time_to_seconds(self, time_str: str) -> float:
        """SRT时间转秒"""
        time_str = time_str.replace(',', '.')
        parts = time_str.split(':')
        hours = int(parts[0])
        minutes = int(parts[1])
        seconds = float(parts[2])
        return hours * 3600 + minutes * 60 + seconds
    
    def seconds_to_srt_time(self, seconds: float) -> str:
        """秒转SRT时间"""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = seconds % 60
        milliseconds = int((secs - int(secs)) * 1000)
        secs = int(secs)
        return f"{hours:02d}:{minutes:02d}:{secs:02d},{milliseconds:03d}"
    
    # ========== 替换模式函数 ==========
    
    def batch_replace_by_time(self, segments: List[TimestampSegment], 
                               replace_text: str, strategy: str, keep_empty: bool) -> List[TimestampSegment]:
        """批量替换(按时间排序)"""
        # 按开始时间排序
        sorted_segments = sorted(segments, key=lambda x: x.start_time)
        
        # 分段替换文本
        split_texts = self.split_text(replace_text, len(sorted_segments), strategy, keep_empty)
        
        # 替换
        for i, seg in enumerate(sorted_segments):
            if i < len(split_texts):
                seg.text = split_texts[i]
        
        return sorted_segments
    
    def batch_replace_by_index(self, segments: List[TimestampSegment], 
                                replace_text: str, strategy: str, keep_empty: bool) -> List[TimestampSegment]:
        """批量替换(按索引排序)"""
        # 按索引排序
        sorted_segments = sorted(segments, key=lambda x: x.index)
        
        # 分段替换文本
        split_texts = self.split_text(replace_text, len(sorted_segments), strategy, keep_empty)
        
        # 替换
        for i, seg in enumerate(sorted_segments):
            if i < len(split_texts):
                seg.text = split_texts[i]
        
        return sorted_segments
    
    def keyword_replace(self, segments: List[TimestampSegment], 
                        keyword: str, replace_text: str) -> List[TimestampSegment]:
        """关键字替换"""
        if not keyword:
            return segments
        
        for seg in segments:
            if keyword in seg.text:
                seg.text = seg.text.replace(keyword, replace_text)
        
        return segments
    
    def regex_replace(self, segments: List[TimestampSegment], 
                      pattern: str, replace_text: str) -> List[TimestampSegment]:
        """正则表达式替换"""
        if not pattern:
            return segments
        
        try:
            regex = re.compile(pattern)
            for seg in segments:
                seg.text = regex.sub(replace_text, seg.text)
        except Exception as e:
            print(f"[错误] 正则表达式错误: {e}")
        
        return segments
    
    def specific_segment_replace(self, segments: List[TimestampSegment], 
                                  indices: str, replace_text: str, strategy: str) -> List[TimestampSegment]:
        """指定段落替换"""
        # 解析索引
        try:
            index_list = []
            for part in indices.split(','):
                part = part.strip()
                if '-' in part:
                    # 范围: 1-5
                    start, end = map(int, part.split('-'))
                    index_list.extend(range(start, end + 1))
                else:
                    # 单个: 3
                    index_list.append(int(part))
            
            # 分段替换文本
            split_texts = self.split_text(replace_text, len(index_list), strategy, False)
            
            # 创建索引到文本的映射
            index_to_text = {}
            for i, idx in enumerate(index_list):
                if i < len(split_texts):
                    index_to_text[idx] = split_texts[i]
            
            # 替换指定段落
            for seg in segments:
                if seg.index in index_to_text:
                    seg.text = index_to_text[seg.index]
            
        except Exception as e:
            print(f"[错误] 段落索引解析失败: {e}")
        
        return segments
    
    def text_enhancement(self, segments: List[TimestampSegment], 
                        option: str, content: str) -> List[TimestampSegment]:
        """文本增强"""
        for seg in segments:
            if option == "添加前缀":
                seg.text = content + seg.text
            elif option == "添加后缀":
                seg.text = seg.text + content
            elif option == "首字母大写":
                seg.text = seg.text.capitalize()
            elif option == "全部大写":
                seg.text = seg.text.upper()
            elif option == "全部小写":
                seg.text = seg.text.lower()
            elif option == "删除空格":
                seg.text = seg.text.replace(' ', '')
            elif option == "删除换行":
                seg.text = seg.text.replace('\n', ' ')
        
        return segments
    
    # ========== 文本分段函数 ==========
    
    def split_text(self, text: str, count: int, strategy: str, keep_empty: bool) -> List[str]:
        """智能分段文本"""
        if not text:
            return [""] * count
        
        if strategy == "按行分段":
            return self.split_by_lines(text, count, keep_empty)
        elif strategy == "按字数均分":
            return self.split_by_chars(text, count)
        elif strategy == "按标点分段":
            return self.split_by_punctuation(text, count)
        elif strategy == "严格按字数":
            return self.split_by_chars_strict(text, count)
        else:
            return [text] * count
    
    def split_by_lines(self, text: str, count: int, keep_empty: bool) -> List[str]:
        """按行分段"""
        lines = text.split('\n')
        
        if not keep_empty:
            lines = [line for line in lines if line.strip()]
        
        # 如果行数等于段数,直接返回
        if len(lines) == count:
            return lines
        
        # 如果行数少于段数,填充空字符串
        if len(lines) < count:
            lines.extend([''] * (count - len(lines)))
            return lines[:count]
        
        # 如果行数多于段数,合并行
        lines_per_segment = len(lines) / count
        result = []
        
        for i in range(count):
            start_idx = int(i * lines_per_segment)
            end_idx = int((i + 1) * lines_per_segment) if i < count - 1 else len(lines)
            result.append('\n'.join(lines[start_idx:end_idx]))
        
        return result
    
    def split_by_chars(self, text: str, count: int) -> List[str]:
        """按字数均分(在标点处断开)"""
        if count == 1:
            return [text]
        
        chars_per_segment = len(text) / count
        result = []
        current_pos = 0
        
        for i in range(count):
            if i == count - 1:
                result.append(text[current_pos:].strip())
            else:
                target_pos = int((i + 1) * chars_per_segment)
                break_pos = self.find_break_point(text, target_pos, current_pos)
                result.append(text[current_pos:break_pos].strip())
                current_pos = break_pos
        
        return result
    
    def split_by_chars_strict(self, text: str, count: int) -> List[str]:
        """严格按字数均分"""
        if count == 1:
            return [text]
        
        chars_per_segment = len(text) / count
        result = []
        
        for i in range(count):
            start = int(i * chars_per_segment)
            end = int((i + 1) * chars_per_segment) if i < count - 1 else len(text)
            result.append(text[start:end])
        
        return result
    
    def split_by_punctuation(self, text: str, count: int) -> List[str]:
        """按标点分段"""
        delimiters = '。！？；.!?;\n'
        sentences = []
        current = ""
        
        for char in text:
            current += char
            if char in delimiters:
                if current.strip():
                    sentences.append(current.strip())
                current = ""
        
        if current.strip():
            sentences.append(current.strip())
        
        if len(sentences) >= count:
            # 合并句子
            sentences_per_seg = len(sentences) / count
            result = []
            
            for i in range(count):
                start_idx = int(i * sentences_per_seg)
                end_idx = int((i + 1) * sentences_per_seg) if i < count - 1 else len(sentences)
                result.append(' '.join(sentences[start_idx:end_idx]))
            
            return result
        else:
            # 句子不够,按字数分
            return self.split_by_chars(text, count)
    
    def find_break_point(self, text: str, target: int, min_pos: int) -> int:
        """寻找合适的断句点"""
        search_range = 10
        
        # 优先在逗号处断开
        for offset in range(search_range):
            for pos in [target + offset, target - offset]:
                if min_pos < pos < len(text) and text[pos] in '，,':
                    return pos + 1
        
        # 其次句号
        for offset in range(search_range):
            for pos in [target + offset, target - offset]:
                if min_pos < pos < len(text) and text[pos] in '。！？；.!?;':
                    return pos + 1
        
        return target
    
    # ========== 输出生成函数 ==========
    
    def generate_output(self, segments: List[TimestampSegment], output_format: str) -> str:
        """生成输出文本"""
        if output_format == "保持原格式":
            # 根据第一个段落的原始格式决定
            if not segments:
                return ""
            
            original_format = segments[0].original_format
            if original_format == "srt":
                return self.to_srt_format(segments)
            elif original_format == "bracket":
                return self.to_bracket_format(segments)
            elif original_format == "simple":
                return self.to_simple_format(segments)
            else:
                return self.to_bracket_format(segments)
        
        elif output_format == "SRT格式":
            return self.to_srt_format(segments)
        
        elif output_format == "括号格式":
            return self.to_bracket_format(segments)
        
        elif output_format == "简单格式":
            return self.to_simple_format(segments)
        
        elif output_format == "纯文本":
            return self.to_plain_text(segments)
        
        return ""
    
    def to_srt_format(self, segments: List[TimestampSegment]) -> str:
        """转换为SRT格式"""
        output_lines = []
        
        for seg in segments:
            output_lines.append(str(seg.index))
            start_time = self.seconds_to_srt_time(seg.start_time)
            end_time = self.seconds_to_srt_time(seg.end_time)
            output_lines.append(f"{start_time} --> {end_time}")
            output_lines.append(seg.text)
            output_lines.append("")  # 空行分隔
        
        return '\n'.join(output_lines)
    
    def to_bracket_format(self, segments: List[TimestampSegment]) -> str:
        """转换为括号格式"""
        output_lines = []
        
        for seg in segments:
            output_lines.append(f"({seg.start_time}, {seg.end_time}) {seg.text}")
        
        return '\n'.join(output_lines)
    
    def to_simple_format(self, segments: List[TimestampSegment]) -> str:
        """转换为简单格式"""
        output_lines = []
        
        for seg in segments:
            output_lines.append(f"{seg.start_time}-{seg.end_time} {seg.text}")
        
        return '\n'.join(output_lines)
    
    def to_plain_text(self, segments: List[TimestampSegment]) -> str:
        """转换为纯文本"""
        return '\n'.join([seg.text for seg in segments])
    
    # ========== 报告生成 ==========
    
    def generate_report(self, segments: List[TimestampSegment], 
                       original_texts: List[str], mode: str,
                       input_format: str, output_format: str) -> str:
        """生成处理报告"""
        report = "📊 时间戳文本替换报告\n"
        report += "="*50 + "\n"
        report += f"处理模式: {mode}\n"
        report += f"输入格式: {input_format}\n"
        report += f"输出格式: {output_format}\n"
        report += f"段落总数: {len(segments)}\n"
        
        # 统计修改数量
        modified_count = sum(1 for i, seg in enumerate(segments) 
                            if i < len(original_texts) and seg.text != original_texts[i])
        
        report += f"修改段数: {modified_count}/{len(segments)}\n"
        report += "\n"
        
        # 显示前3个修改示例
        report += "修改示例:\n"
        shown = 0
        for i, seg in enumerate(segments):
            if i < len(original_texts) and seg.text != original_texts[i]:
                report += f"\n段落 {seg.index}:\n"
                report += f"  原文: {original_texts[i][:30]}...\n"
                report += f"  新文: {seg.text[:30]}...\n"
                shown += 1
                if shown >= 3:
                    break
        
        if modified_count > 3:
            report += f"\n... 还有 {modified_count - 3} 处修改\n"
        
        report += "\n" + "="*50
        
        return report


# 节点注册
NODE_CLASS_MAPPINGS = {
    "TimestampTextReplaceNode": TimestampTextReplaceNode
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "TimestampTextReplaceNode": "时间戳文本替换(专业版) 📝"
}

