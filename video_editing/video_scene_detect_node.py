"""
分镜识别节点
自动检测视频中的场景切换点
"""

import torch
import torch.nn.functional as F
import json

class VideoSceneDetectNode:
    """分镜识别节点"""
    
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
                "检测灵敏度": (["低", "中", "高", "极高"], {
                    "default": "中"
                }),
                "最小场景时长": ("FLOAT", {
                    "default": 1.0,
                    "min": 0.1,
                    "max": 10.0,
                    "step": 0.1
                }),
                "输出模式": (["仅标记", "分割输出", "批量输出", "时间列表"], {
                    "default": "仅标记"
                }),
            },
            "optional": {
                "场景索引": ("INT", {
                    "default": 1,
                    "min": 1,
                    "max": 100,
                    "step": 1,
                    "tooltip": "选择输出第几个场景（仅在'分割输出'模式下有效，从1开始计数）"
                }),
            }
        }
    
    RETURN_TYPES = ("IMAGE", "STRING", "INT", "STRING")
    RETURN_NAMES = ("视频", "场景信息", "场景数量", "场景数据")
    FUNCTION = "detect_scenes"
    CATEGORY = "HAIGC工具集/视频剪辑"
    
    def detect_scenes(self, images, 视频帧率, 检测灵敏度, 最小场景时长, 输出模式, 场景索引=1):
        """分镜识别"""
        batch_size = images.shape[0]
        min_scene_frames = int(最小场景时长 * 视频帧率)
        
        # 灵敏度阈值（调整为更合理的值）
        # 对于归一化图像，帧间差异通常在0.01-0.1之间
        threshold_map = {
            "低": 0.15,      # 只检测非常明显的场景切换
            "中": 0.08,      # 检测明显的场景切换
            "高": 0.05,      # 检测较明显的场景切换
            "极高": 0.03     # 检测所有可能的场景切换
        }
        threshold = threshold_map[检测灵敏度]
        
        # 计算帧间差异（使用更鲁棒的方法）
        scene_changes = [0]  # 第一帧总是场景起始
        diffs = []  # 记录所有帧间差异，用于调试
        
        for i in range(1, batch_size):
            # 方法1: 转换为灰度图计算差异（更鲁棒）
            frame1 = images[i-1]
            frame2 = images[i]
            
            # 转换为灰度图 (H, W, C) -> (H, W)
            gray1 = 0.299 * frame1[:, :, 0] + 0.587 * frame1[:, :, 1] + 0.114 * frame1[:, :, 2]
            gray2 = 0.299 * frame2[:, :, 0] + 0.587 * frame2[:, :, 1] + 0.114 * frame2[:, :, 2]
            
            # 计算平均绝对差异
            diff_gray = torch.mean(torch.abs(gray2 - gray1)).item()
            
            # 方法2: 计算直方图差异（检测颜色分布变化）
            # 将图像分成小块，计算每块的直方图差异
            hist_diff = 0.0
            if frame1.shape[0] > 32 and frame1.shape[1] > 32:
                # 下采样到较小尺寸计算直方图
                h, w = frame1.shape[0], frame1.shape[1]
                sample_h, sample_w = min(64, h), min(64, w)
                
                # 计算RGB各通道的直方图
                for c in range(3):
                    hist1 = torch.histc(frame1[:, :, c].flatten(), bins=16, min=0.0, max=1.0)
                    hist2 = torch.histc(frame2[:, :, c].flatten(), bins=16, min=0.0, max=1.0)
                    hist1 = hist1 / (hist1.sum() + 1e-8)  # 归一化
                    hist2 = hist2 / (hist2.sum() + 1e-8)
                    hist_diff += torch.mean(torch.abs(hist1 - hist2)).item()
                hist_diff = hist_diff / 3.0
            
            # 综合差异（灰度差异 + 直方图差异）
            diff = diff_gray * 0.7 + hist_diff * 0.3
            diffs.append(diff)
            
            # 如果差异超过阈值，且距离上个场景足够远
            if diff > threshold and (i - scene_changes[-1]) >= min_scene_frames:
                scene_changes.append(i)
        
        scene_count = len(scene_changes)
        
        # 根据输出模式生成不同的输出
        if 输出模式 == "仅标记":
            # 在图像上标记场景切换点（可选，当前只返回原图）
            result_images = images
        elif 输出模式 == "分割输出":
            # 根据场景索引返回对应的场景片段
            if scene_count > 1:
                # 验证场景索引范围（转换为0-based索引）
                scene_idx = 场景索引 - 1  # 用户输入从1开始，转换为0-based
                
                if scene_idx < 0:
                    scene_idx = 0
                    print(f"[分镜识别] 警告: 场景索引{场景索引}无效，使用场景1")
                elif scene_idx >= scene_count:
                    scene_idx = scene_count - 1
                    print(f"[分镜识别] 警告: 场景索引{场景索引}超出范围（共{scene_count}个场景），使用最后一个场景")
                
                # 获取对应场景的起始和结束帧
                start_frame = scene_changes[scene_idx]
                end_frame = scene_changes[scene_idx + 1] if scene_idx + 1 < len(scene_changes) else batch_size
                result_images = images[start_frame:end_frame]
                
                start_time = start_frame / 视频帧率
                end_time = end_frame / 视频帧率
                duration = end_time - start_time
                print(f"[分镜识别] 分割输出: 返回场景{场景索引} (帧{start_frame}-{end_frame}, 时长{duration:.2f}s)")
            else:
                # 只有一个场景（未检测到切换），返回原视频
                result_images = images
                print(f"[分镜识别] 分割输出: 未检测到场景切换，返回原视频")
        elif 输出模式 == "批量输出":
            # 批量输出模式：视频保持原样，配合场景数据用于后续节点
            result_images = images
            if scene_count > 1:
                print(f"[分镜识别] 批量输出: 检测到 {scene_count} 个场景，可在分镜转接/批量保存节点中选择具体场景")
            else:
                print(f"[分镜识别] 批量输出: 未检测到场景切换，返回原视频")
        else:  # "时间列表"
            # 只返回时间信息，返回原视频
            result_images = images
        
        # 生成场景信息
        scene_info_list = []
        for idx, start in enumerate(scene_changes):
            end = scene_changes[idx + 1] if idx + 1 < len(scene_changes) else batch_size
            start_time = start / 视频帧率
            end_time = end / 视频帧率
            duration = end_time - start_time
            scene_info_list.append(
                f"场景{idx+1}: {start_time:.2f}s-{end_time:.2f}s (时长{duration:.2f}s, 帧{start}-{end})"
            )
        
        scene_info = "\n".join(scene_info_list) if scene_info_list else "未检测到场景切换"
        
        # 生成场景数据（JSON格式，用于转接节点）
        scene_data = {
            "scene_changes": scene_changes,  # 场景切换点（帧索引）
            "scene_count": scene_count,
            "frame_rate": 视频帧率,
            "total_frames": batch_size
        }
        scene_data_json = json.dumps(scene_data)
        
        # 输出调试信息
        if len(diffs) > 0:
            max_diff = max(diffs)
            avg_diff = sum(diffs) / len(diffs)
            print(f"[分镜识别] 检测到 {scene_count} 个场景, 灵敏度:{检测灵敏度}, 阈值:{threshold:.4f}")
            print(f"[分镜识别] 最大帧间差异: {max_diff:.4f}, 平均差异: {avg_diff:.4f}")
            print(f"[分镜识别] 场景切换点(帧): {scene_changes}")
            if scene_count > 1:
                print(f"[分镜识别] 场景信息:\n{scene_info}")
            else:
                print(f"[分镜识别] 警告: 未检测到场景切换，请尝试提高灵敏度或降低最小场景时长")
        
        return (result_images, scene_info, scene_count, scene_data_json)

