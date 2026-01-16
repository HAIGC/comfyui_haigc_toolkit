"""
视频预览节点
用于显示视频加载器的详细预览信息，包括当前帧数显示
支持裁剪和输出指定范围的视频帧
"""

import os
import torch
from .video_loader_node import VideoLoaderNode

class VideoPreviewNode:
    """视频预览节点"""
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "video_info": ("HAIGC_VIDEOINFO",),
                "起始帧": ("INT", {
                    "default": 0,
                    "min": 0,
                    "max": 100000,
                    "step": 1,
                    "display": "number",
                    "tooltip": "输出视频的起始帧"
                }),
                "结束帧": ("INT", {
                    "default": 0,
                    "min": 0,
                    "max": 100000,
                    "step": 1,
                    "display": "number",
                    "tooltip": "输出视频的结束帧，0表示直到视频结束"
                }),
                "剪辑模式": (["保留选中区域", "删除选中区域", "保留起始帧及之后", "保留起始帧及之前"],),
            },
        }
    
    RETURN_TYPES = ("IMAGE", "AUDIO", "HAIGC_VIDEOINFO")
    RETURN_NAMES = ("视频", "音频", "视频信息")
    OUTPUT_NODE = True
    FUNCTION = "preview_and_process_video"
    CATEGORY = "HAIGC工具集/视频剪辑"
    
    def preview_and_process_video(self, video_info, 起始帧, 结束帧, 剪辑模式="保留选中区域"):
        """预览并处理视频"""
        
        # 获取视频路径
        source_path = video_info.get("source_path", "")
        
        # 如果路径不存在，返回空数据但保留UI以显示错误（如果有的话）
        if not source_path or not os.path.exists(source_path):
            empty_img = torch.zeros((1, 64, 64, 3))
            empty_audio = {"waveform": torch.zeros((1, 2, 0)), "sample_rate": 44100}
            return {"ui": {"videos": []}, "result": (empty_img, empty_audio, video_info)}
            
        loader = VideoLoaderNode()
        
        # 1. 构建预览信息（直接使用传入的video_info中的参数，避免重新读取文件）
        width = video_info.get("width", 0)
        height = video_info.get("height", 0)
        fps = video_info.get("fps", 0)
        total_frames = video_info.get("total_frames", video_info.get("frame_count", 0))
        duration = video_info.get("duration", 0)
        
        # 尝试获取文件大小和比特率，用于预览显示
        try:
            file_size_mb = os.path.getsize(source_path) / (1024 * 1024)
        except:
            file_size_mb = video_info.get("file_size_mb", 0)
            
        video_bitrate_kbps = video_info.get("video_bitrate_kbps", 0)
        audio_bitrate_kbps = video_info.get("audio_bitrate_kbps", 0)
        has_audio = video_info.get("has_audio", False)
        
        # 重新构建预览UI信息
        ui_info = loader._build_video_preview(
            video_path=source_path,
            fps=fps,
            frame_count=total_frames,
            duration=duration,
            has_audio=has_audio,
            file_size_mb=round(file_size_mb, 2),
            width=width,
            height=height,
            video_bitrate_kbps=video_bitrate_kbps,
            audio_bitrate_kbps=audio_bitrate_kbps
        )
        
        # 确保将 video_info 中的所有键值对更新到 ui_info 的 videos[0] 中
        if ui_info and "videos" in ui_info and len(ui_info["videos"]) > 0:
            ui_info["videos"][0].update({
                "video_bitrate_kbps": video_bitrate_kbps,
                "audio_bitrate_kbps": audio_bitrate_kbps
            })

        # 2. 根据剪辑模式确定要加载的片段范围
        ranges_to_load = []
        
        start_f = 起始帧
        end_f = 结束帧
        
        if 剪辑模式 == "保留选中区域":
            # 标准模式：保留 start 到 end
            # 如果 end 为 0，表示直到结束
            if end_f == 0:
                ranges_to_load.append((start_f, 0))
            else:
                # 如果 start > end，自动交换 (用户体验优化)
                if start_f > end_f:
                    ranges_to_load.append((end_f, start_f))
                else:
                    ranges_to_load.append((start_f, end_f))
                    
        elif 剪辑模式 == "删除选中区域":
            # 删除模式：保留 [0, start) 和 (end, total]
            # 首先规范化 start 和 end
            s = start_f
            e = end_f
            
            # 处理 end=0 的情况 (表示到末尾)
            # 如果删除 "Start 到 End(末尾)"，则只保留 "0 到 Start"
            if e == 0:
                ranges_to_load.append((0, s))
            else:
                # 如果 start > end，交换它们以确定要删除的中间部分
                if s > e:
                    s, e = e, s
                
                # 添加第一段：0 到 s
                if s > 0:
                    ranges_to_load.append((0, s))
                
                # 添加第二段：e 到 结束
                # 注意：如果 e >= total_frames，则不需要添加
                if e < total_frames:
                    ranges_to_load.append((e, 0))
                    
        elif 剪辑模式 == "保留起始帧及之后":
            # 忽略结束帧参数
            ranges_to_load.append((start_f, 0))
            
        elif 剪辑模式 == "保留起始帧及之前":
            # 忽略结束帧参数，保留 0 到 start
            ranges_to_load.append((0, start_f))
            
        # 3. 加载并合并所有片段
        final_images = []
        final_audio_waveforms = []
        final_sample_rate = 44100
        
        total_loaded_frames = 0
        
        # 如果没有有效范围 (例如 start=0, mode=保留起始帧及之前 -> 范围 0-0 空)
        # 默认至少加载一帧或者处理为空的情况
        if not ranges_to_load:
             # 如果范围为空，可能是逻辑导致的，这里兜底处理，比如加载全部或返回空
             # 为了避免错误，我们假设至少加载一帧占位，或者什么都不做返回空
             pass

        for (s, e) in ranges_to_load:
            # 调用 VideoLoaderNode 的 load_video 方法
            load_result = loader.load_video(
                视频文件="", 
                起始帧=s,
                结束帧=e,
                帧率=0, 
                跳帧=1, 
                视频路径=source_path,
                目标宽度=0,
                目标高度=0
            )
            
            res_images, res_audio, res_info = load_result["result"]
            
            # 检查是否是错误占位符 (通过 info 中的 error 判断)
            if res_info and "error" in res_info:
                print(f"[VideoPreview] 加载片段 {s}-{e} 失败: {res_info['error']}")
                continue
                
            if res_images is not None and res_images.shape[0] > 0:
                final_images.append(res_images)
                total_loaded_frames += res_images.shape[0]
            
            if res_audio and "waveform" in res_audio:
                wav = res_audio["waveform"]
                # 确保是 tensor
                if not isinstance(wav, torch.Tensor):
                     wav = torch.tensor(wav)
                
                if wav.numel() > 0:
                    final_audio_waveforms.append(wav)
                    final_sample_rate = res_audio.get("sample_rate", 44100)
        
        # 合并结果
        if not final_images:
            # 如果没有加载到任何图像，返回空
            empty_img = torch.zeros((1, 64, 64, 3))
            empty_audio = {"waveform": torch.zeros((1, 2, 0)), "sample_rate": 44100}
            # 更新 info 为 0 帧
            out_info = video_info.copy()
            out_info["frame_count"] = 0
            out_info["duration"] = 0
            return {"ui": ui_info, "result": (empty_img, empty_audio, out_info)}
            
        # 拼接图像
        output_images = torch.cat(final_images, dim=0)
        
        # 拼接音频
        if final_audio_waveforms:
            # 音频 waveform 形状应该是 (batch, channels, samples) usually (1, 2, N)
            # 我们需要在最后一个维度拼接 (时间维度)
            # 检查维度
            valid_waveforms = []
            for w in final_audio_waveforms:
                if w.dim() == 3:
                    valid_waveforms.append(w)
                elif w.dim() == 2:
                    valid_waveforms.append(w.unsqueeze(0))
            
            if valid_waveforms:
                output_audio_waveform = torch.cat(valid_waveforms, dim=2)
                output_audio = {"waveform": output_audio_waveform, "sample_rate": final_sample_rate}
            else:
                output_audio = {"waveform": torch.zeros((1, 2, 0)), "sample_rate": 44100}
        else:
            output_audio = {"waveform": torch.zeros((1, 2, 0)), "sample_rate": 44100}
            
        # 更新视频信息
        output_info = video_info.copy()
        output_info["frame_count"] = output_images.shape[0]
        if fps > 0:
            output_info["duration"] = output_images.shape[0] / fps
        else:
            output_info["duration"] = 0
            
        return {"ui": ui_info, "result": (output_images, output_audio, output_info)}
