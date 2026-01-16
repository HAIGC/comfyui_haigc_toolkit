"""
图像批次复制节点
支持按顺序复制图像和按批次复制图像
同时支持音频复制，根据图像复制模式自动对齐音频
"""

import torch
import numpy as np

class ImageBatchDuplicateNode:
    """图像批次复制节点"""
    
    def __init__(self):
        self.type = "HAIGC_ImageBatchDuplicate"
        
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "images": ("IMAGE",),
                "复制次数": ("INT", {
                    "default": 1,
                    "min": 0,
                    "max": 100,
                    "step": 1,
                    "display": "number"
                }),
                "复制模式": (["按顺序复制", "按批次复制"], {
                    "default": "按顺序复制"
                }),
            },
            "optional": {
                "audio": ("AUDIO",),
            }
        }
    
    RETURN_TYPES = ("IMAGE", "AUDIO", "INT", "INT")
    RETURN_NAMES = ("图像批次", "音频", "原始数量", "输出数量")
    FUNCTION = "duplicate_images"
    CATEGORY = "HAIGC工具集/图片处理"
    OUTPUT_NODE = False
    
    def duplicate_images(self, images, 复制次数=1, 复制模式="按顺序复制", audio=None):
        """复制图像批次和音频"""
        
        if images is None or images.shape[0] == 0:
            print("图像批次复制：没有输入图像")
            empty_audio = {"waveform": torch.zeros((1, 2, 0)), "sample_rate": 44100}
            return (images, empty_audio, 0, 0)
        
        original_count = images.shape[0]
        
        # 如果复制次数小于1，直接返回原图和原音频
        if 复制次数 < 1:
            print(f"图像批次复制：复制次数 {复制次数} < 1，返回原图")
            if audio is None:
                audio = {"waveform": torch.zeros((1, 2, 0)), "sample_rate": 44100}
            return (images, audio, original_count, original_count)
        
        if 复制模式 == "按顺序复制":
            # 按顺序复制：每张图片连续重复N次
            # 例如：[A, B, C] 复制2次 -> [A, A, B, B, C, C]
            duplicated_list = []
            for i in range(original_count):
                for _ in range(复制次数):
                    duplicated_list.append(images[i:i+1])
            
            output_images = torch.cat(duplicated_list, dim=0)
            output_count = original_count * 复制次数
            
            print(f"图像批次复制：按顺序复制 {复制次数} 次")
            print(f"  原始数量: {original_count}, 输出数量: {output_count}")
            
            # 复制音频（按顺序）
            output_audio = self._duplicate_audio_sequential(audio, original_count, 复制次数)
            
        else:  # 按批次复制
            # 按批次复制：整个批次重复N次
            # 例如：[A, B, C] 复制2次 -> [A, B, C, A, B, C]
            repeated_batches = [images] * 复制次数
            output_images = torch.cat(repeated_batches, dim=0)
            output_count = original_count * 复制次数
            
            print(f"图像批次复制：按批次复制 {复制次数} 次")
            print(f"  原始数量: {original_count}, 输出数量: {output_count}")
            
            # 复制音频（按批次）
            output_audio = self._duplicate_audio_batch(audio, 复制次数)
        
        return (output_images, output_audio, original_count, output_count)
    
    def _duplicate_audio_sequential(self, audio, frame_count, duplicate_count):
        """按顺序复制音频（每帧音频重复N次）"""
        if audio is None or audio.get("waveform") is None:
            return {"waveform": torch.zeros((1, 2, 0)), "sample_rate": 44100}
        
        waveform = audio["waveform"]
        sample_rate = audio["sample_rate"]
        
        # 如果音频为空
        if waveform.shape[2] == 0:
            return {"waveform": torch.zeros((1, 2, 0)), "sample_rate": sample_rate}
        
        # 计算每帧对应的音频采样数
        total_samples = waveform.shape[2]
        samples_per_frame = total_samples // frame_count
        
        # 按顺序复制音频片段
        duplicated_segments = []
        for i in range(frame_count):
            start_idx = i * samples_per_frame
            end_idx = start_idx + samples_per_frame if i < frame_count - 1 else total_samples
            
            # 提取该帧对应的音频片段
            segment = waveform[:, :, start_idx:end_idx]
            
            # 重复该片段N次
            for _ in range(duplicate_count):
                duplicated_segments.append(segment)
        
        # 合并所有片段
        output_waveform = torch.cat(duplicated_segments, dim=2)
        
        print(f"  音频按顺序复制: {waveform.shape[2]} -> {output_waveform.shape[2]} samples")
        
        return {"waveform": output_waveform, "sample_rate": sample_rate}
    
    def _duplicate_audio_batch(self, audio, duplicate_count):
        """按批次复制音频（整个音频重复N次）"""
        if audio is None or audio.get("waveform") is None:
            return {"waveform": torch.zeros((1, 2, 0)), "sample_rate": 44100}
        
        waveform = audio["waveform"]
        sample_rate = audio["sample_rate"]
        
        # 如果音频为空
        if waveform.shape[2] == 0:
            return {"waveform": torch.zeros((1, 2, 0)), "sample_rate": sample_rate}
        
        # 重复整个音频
        repeated_waveforms = [waveform] * duplicate_count
        output_waveform = torch.cat(repeated_waveforms, dim=2)
        
        print(f"  音频按批次复制: {waveform.shape[2]} -> {output_waveform.shape[2]} samples")
        
        return {"waveform": output_waveform, "sample_rate": sample_rate}
    
    @classmethod
    def IS_CHANGED(cls, **kwargs):
        # 参数变化时重新计算
        return float("nan")
