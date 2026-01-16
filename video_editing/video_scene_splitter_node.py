"""
分镜转接节点
根据场景识别结果，选择并输出多个场景片段
"""

import torch
import json
from typing import Tuple, Optional

class VideoSceneSplitterNode:
    """分镜转接节点 - 可选择输出多个场景片段"""
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "images": ("IMAGE",),
                "场景数据": ("STRING",),
                "输出1场景序号": ("INT", {
                    "default": 1,
                    "min": 1,
                    "max": 100,
                    "step": 1,
                    "tooltip": "输出端口1的场景序号（从1开始，0表示不输出）"
                }),
                "输出2场景序号": ("INT", {
                    "default": 0,
                    "min": 0,
                    "max": 100,
                    "step": 1,
                    "tooltip": "输出端口2的场景序号（从1开始，0表示不输出）"
                }),
                "输出3场景序号": ("INT", {
                    "default": 0,
                    "min": 0,
                    "max": 100,
                    "step": 1,
                    "tooltip": "输出端口3的场景序号（从1开始，0表示不输出）"
                }),
                "输出4场景序号": ("INT", {
                    "default": 0,
                    "min": 0,
                    "max": 100,
                    "step": 1,
                    "tooltip": "输出端口4的场景序号（从1开始，0表示不输出）"
                }),
                "输出5场景序号": ("INT", {
                    "default": 0,
                    "min": 0,
                    "max": 100,
                    "step": 1,
                    "tooltip": "输出端口5的场景序号（从1开始，0表示不输出）"
                }),
            },
        }
    
    RETURN_TYPES = ("IMAGE", "IMAGE", "IMAGE", "IMAGE", "IMAGE")
    RETURN_NAMES = ("场景1", "场景2", "场景3", "场景4", "场景5")
    FUNCTION = "split_scenes"
    CATEGORY = "HAIGC工具集/视频剪辑"
    
    def split_scenes(
        self,
        images: torch.Tensor,
        场景数据: str,
        输出1场景序号: int,
        输出2场景序号: int,
        输出3场景序号: int,
        输出4场景序号: int,
        输出5场景序号: int
    ) -> Tuple[torch.Tensor, torch.Tensor, torch.Tensor, torch.Tensor, torch.Tensor]:
        """
        根据场景数据分割视频并输出指定场景
        
        Args:
            images: 输入视频，形状 (B, H, W, C)
            场景数据: JSON格式的场景数据字符串
            输出1场景序号 ~ 输出5场景序号: 要输出的场景序号（1开始，0表示不输出）
            
        Returns:
            5个场景片段（如果序号为0或无效，返回空视频）
        """
        try:
            # 解析场景数据
            try:
                scene_data = json.loads(场景数据)
                scene_changes = scene_data.get("scene_changes", [])
                scene_count = scene_data.get("scene_count", 0)
                frame_rate = scene_data.get("frame_rate", 30.0)
                total_frames = scene_data.get("total_frames", images.shape[0])
            except (json.JSONDecodeError, KeyError) as e:
                print(f"[分镜转接] 错误: 无法解析场景数据 - {str(e)}")
                # 返回5个空视频（与输入视频尺寸一致的单帧黑色图像）
                _, height, width, channels = images.shape
                empty_video = torch.zeros((1, height, width, channels), device=images.device)
                return (empty_video, empty_video, empty_video, empty_video, empty_video)
            
            batch_size = images.shape[0]
            _, height, width, channels = images.shape
            device = images.device
            
            # 验证场景数据
            if scene_count == 0 or len(scene_changes) == 0:
                print(f"[分镜转接] 警告: 未检测到场景，返回空视频")
                empty_video = torch.zeros((1, height, width, channels), device=device)
                return (empty_video, empty_video, empty_video, empty_video, empty_video)
            
            # 调试信息：打印场景切换点
            print(f"[分镜转接] 场景数据解析成功:")
            print(f"  总场景数: {scene_count}")
            print(f"  场景切换点(帧): {scene_changes}")
            print(f"  输入视频总帧数: {batch_size}")
            print(f"  视频帧率: {frame_rate}")
            
            # 打印每个场景的帧范围
            for idx in range(scene_count):
                start_frame = scene_changes[idx]
                end_frame = scene_changes[idx + 1] if idx + 1 < len(scene_changes) else batch_size
                start_time = start_frame / frame_rate
                end_time = end_frame / frame_rate
                duration = end_time - start_time
                print(f"  场景{idx+1}: 帧{start_frame}-{end_frame} (时长{duration:.2f}s)")
            
            # 处理每个输出端口
            outputs = []
            output_indices = [
                输出1场景序号,
                输出2场景序号,
                输出3场景序号,
                输出4场景序号,
                输出5场景序号
            ]
            
            print(f"[分镜转接] 输出配置: {output_indices}")
            
            for port_idx, scene_idx in enumerate(output_indices, 1):
                if scene_idx == 0:
                    # 不输出，返回空视频（与输入视频尺寸一致的单帧黑色图像）
                    empty_video = torch.zeros((1, height, width, channels), device=device)
                    outputs.append(empty_video)
                    continue
                
                # 转换为0-based索引
                scene_idx_0based = scene_idx - 1
                
                # 验证场景索引范围
                if scene_idx_0based < 0:
                    print(f"[分镜转接] 警告: 输出端口{port_idx}的场景序号{scene_idx}无效，使用场景1")
                    scene_idx_0based = 0
                elif scene_idx_0based >= scene_count:
                    print(f"[分镜转接] 警告: 输出端口{port_idx}的场景序号{scene_idx}超出范围（共{scene_count}个场景），使用最后一个场景")
                    scene_idx_0based = scene_count - 1
                
                # 获取对应场景的起始和结束帧
                start_frame = scene_changes[scene_idx_0based]
                end_frame = scene_changes[scene_idx_0based + 1] if scene_idx_0based + 1 < len(scene_changes) else batch_size
                
                # 确保索引在有效范围内
                start_frame = max(0, min(start_frame, batch_size - 1))
                end_frame = max(start_frame + 1, min(end_frame, batch_size))
                
                # 调试信息：检查帧范围
                if start_frame >= end_frame:
                    print(f"[分镜转接] 错误: 输出端口{port_idx}的场景{scene_idx}帧范围无效 (start={start_frame}, end={end_frame})")
                    empty_video = torch.zeros((1, height, width, channels), device=device)
                    outputs.append(empty_video)
                    continue
                
                # 提取场景片段
                scene_clip = images[start_frame:end_frame].clone()
                
                # 调试信息：验证提取的片段
                print(f"[分镜转接] 输出端口{port_idx}: 提取场景{scene_idx} -> 帧{start_frame}-{end_frame}, 片段形状: {scene_clip.shape}")
                
                if scene_clip.shape[0] == 0:
                    print(f"[分镜转接] 警告: 输出端口{port_idx}的场景{scene_idx}片段为空")
                    empty_video = torch.zeros((1, height, width, channels), device=device)
                    outputs.append(empty_video)
                else:
                    outputs.append(scene_clip)
                    start_time = start_frame / frame_rate
                    end_time = end_frame / frame_rate
                    duration = end_time - start_time
                    print(f"[分镜转接] 输出端口{port_idx}: 场景{scene_idx} (帧{start_frame}-{end_frame}, 时长{duration:.2f}s, {scene_clip.shape[0]}帧)")
            
            return tuple(outputs)
            
        except Exception as e:
            print(f"[分镜转接] 错误: {str(e)}")
            import traceback
            traceback.print_exc()
            # 返回5个空视频（与输入视频尺寸一致的单帧黑色图像）
            try:
                _, height, width, channels = images.shape
                device = images.device
            except:
                height, width, channels = 64, 64, 3
                device = torch.device("cpu")
            empty_video = torch.zeros((1, height, width, channels), device=device)
            return (empty_video, empty_video, empty_video, empty_video, empty_video)
    
NODE_CLASS_MAPPINGS = {
    "VideoSceneSplitterNode": VideoSceneSplitterNode
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "VideoSceneSplitterNode": "分镜转接 🎬"
}

