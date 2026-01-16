"""
视频混剪节点
将多段视频按指定方式混合剪辑
"""

import torch
import random

class VideoMontageNode:
    """视频混剪节点"""
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "video1": ("IMAGE",),
                "video2": ("IMAGE",),
                "视频帧率": ("FLOAT", {
                    "default": 30.0,
                    "min": 1.0,
                    "max": 120.0,
                    "step": 0.1
                }),
                "混剪模式": (["顺序拼接", "交替切换", "随机混合", "A-B-A-B循环"], {
                    "default": "交替切换"
                }),
                "每段时长": ("FLOAT", {
                    "default": 1.0,
                    "min": 0.1,
                    "max": 10.0,
                    "step": 0.1
                }),
            },
            "optional": {
                "video3": ("IMAGE",),
                "video4": ("IMAGE",),
            }
        }
    
    RETURN_TYPES = ("IMAGE", "INT", "FLOAT")
    RETURN_NAMES = ("视频", "输出帧数", "输出时长")
    FUNCTION = "montage_videos"
    CATEGORY = "HAIGC工具集/视频剪辑"
    
    def montage_videos(self, video1, video2, 视频帧率, 混剪模式, 每段时长, video3=None, video4=None):
        """视频混剪"""
        # 收集所有视频
        videos = [video1, video2]
        if video3 is not None:
            videos.append(video3)
        if video4 is not None:
            videos.append(video4)
        
        segment_frames = int(每段时长 * 视频帧率)
        
        if 混剪模式 == "顺序拼接":
            # 简单顺序拼接
            result = torch.cat(videos, dim=0)
            method = "顺序拼接"
            
        elif 混剪模式 == "交替切换":
            # 交替切换各个视频的片段
            segments = []
            max_frames = max([v.shape[0] for v in videos])
            
            for i in range(0, max_frames, segment_frames):
                for video in videos:
                    if i < video.shape[0]:
                        end = min(i + segment_frames, video.shape[0])
                        segments.append(video[i:end])
            
            result = torch.cat(segments, dim=0)
            method = f"交替切换 (每段{每段时长}秒)"
            
        elif 混剪模式 == "随机混合":
            # 随机抽取各视频片段
            segments = []
            total_duration = min([v.shape[0] for v in videos])
            
            for i in range(0, total_duration, segment_frames):
                video = random.choice(videos)
                end = min(i + segment_frames, video.shape[0])
                if i < video.shape[0]:
                    segments.append(video[i:end])
            
            result = torch.cat(segments, dim=0)
            method = f"随机混合 (每段{每段时长}秒)"
            
        elif 混剪模式 == "A-B-A-B循环":
            # A-B交替循环
            segments = []
            min_frames = min([v.shape[0] for v in videos[:2]])
            
            a_segments = min_frames // segment_frames
            for i in range(a_segments):
                start = i * segment_frames
                end = min(start + segment_frames, videos[0].shape[0])
                segments.append(videos[0][start:end])
                
                end = min(start + segment_frames, videos[1].shape[0])
                segments.append(videos[1][start:end])
            
            result = torch.cat(segments, dim=0)
            method = f"A-B循环 (每段{每段时长}秒)"
        
        else:
            result = video1
            method = "默认"
        
        output_frames = result.shape[0]
        output_duration = output_frames / 视频帧率
        
        print(f"[视频混剪] {len(videos)}个视频, 模式:{method}, 输出:{output_frames}帧")
        
        return (result, output_frames, output_duration)

