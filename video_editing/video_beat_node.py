"""
卡点效果节点
节奏卡点、闪白、缩放等特效
"""

import torch
import torch.nn.functional as F
import math

class VideoBeatNode:
    """卡点效果节点"""
    
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
                "卡点效果": (["闪白", "闪黑", "缩放", "旋转", "抖动", "色彩爆炸", "模糊", "像素化", "故障效果", "波纹", "径向模糊", "负片", "老电影", "边缘发光", "冲击波", "粒子爆炸", "能量脉冲", "时间扭曲", "镜头震动", "色彩分离", "光晕扩散", "速度线", "镜头拉近", "镜头拉远"], {
                    "default": "闪白"
                }),
                "卡点间隔": ("FLOAT", {
                    "default": 0.5,
                    "min": 0.1,
                    "max": 5.0,
                    "step": 0.1
                }),
                "效果强度": ("FLOAT", {
                    "default": 1.0,
                    "min": 0.1,
                    "max": 3.0,
                    "step": 0.1
                }),
                "效果时长": ("FLOAT", {
                    "default": 0.1,
                    "min": 0.03,
                    "max": 3.0,
                    "step": 0.01
                }),
            },
        }
    
    RETURN_TYPES = ("IMAGE", "INT", "FLOAT")
    RETURN_NAMES = ("视频", "输出帧数", "输出时长")
    FUNCTION = "apply_beat_effect"
    CATEGORY = "HAIGC工具集/视频剪辑"
    
    def apply_beat_effect(self, images, 视频帧率, 卡点效果, 卡点间隔, 效果强度, 效果时长):
        """应用卡点效果"""
        batch_size, height, width, channels = images.shape
        result = images.clone()
        
        beat_interval_frames = int(卡点间隔 * 视频帧率)
        effect_duration_frames = int(效果时长 * 视频帧率)
        
        beat_count = 0
        
        for i in range(0, batch_size, beat_interval_frames):
            # 在卡点位置应用效果
            beat_start = i
            beat_end = min(i + effect_duration_frames, batch_size)
            
            if beat_start >= batch_size:
                break
            
            beat_count += 1
            
            for j in range(beat_start, beat_end):
                # 计算效果衰减（从强到弱）
                progress = (j - beat_start) / max(effect_duration_frames, 1)
                fade = 1.0 - progress  # 线性衰减
                relative_frame = j - beat_start  # 相对帧索引（用于动画效果）
                
                if 卡点效果 == "闪白":
                    # 闪白效果
                    white = torch.ones_like(result[j])
                    result[j] = result[j] + white * 效果强度 * fade * 0.5
                    result[j] = torch.clamp(result[j], 0, 1)
                
                elif 卡点效果 == "闪黑":
                    # 闪黑效果
                    result[j] = result[j] * (1 - 效果强度 * fade * 0.5)
                
                elif 卡点效果 == "缩放":
                    # 缩放效果：从中心放大（scale > 1.0）或缩小（scale < 1.0）
                    # 效果强度越大，缩放越明显
                    # fade 从 1.0 衰减到 0.0，实现从强到弱的缩放效果
                    scale = 1.0 + 效果强度 * 0.2 * fade  # 放大效果，强度越大放大越多
                    
                    if scale != 1.0:
                        # 计算缩放后的尺寸（从中心裁剪）
                        new_h = max(1, int(height / scale))
                        new_w = max(1, int(width / scale))
                        
                        center_y, center_x = height // 2, width // 2
                        y1 = max(0, center_y - new_h // 2)
                        y2 = min(height, center_y + new_h // 2)
                        x1 = max(0, center_x - new_w // 2)
                        x2 = min(width, center_x + new_w // 2)
                        
                        # 裁剪中心区域 (H, W, C)
                        cropped = result[j, y1:y2, x1:x2, :]
                        
                        # 转换为 (1, C, H, W) 格式进行插值
                        cropped_nchw = cropped.unsqueeze(0).permute(0, 3, 1, 2)
                        
                        # 缩放回原尺寸
                        scaled = F.interpolate(
                            cropped_nchw,
                            size=(height, width),
                            mode='bilinear',
                            align_corners=False
                        )
                        
                        # 转换回 (H, W, C) 格式
                        result[j] = scaled.squeeze(0).permute(1, 2, 0)
                
                elif 卡点效果 == "旋转":
                    # 旋转效果：从中心旋转
                    max_angle = 效果强度 * 20.0 * fade  # 最大旋转角度（度），强度越大角度越大
                    
                    if abs(max_angle) > 0.1:  # 只有角度足够大时才旋转
                        angle_rad = math.radians(max_angle)
                        
                        # 获取当前帧 (H, W, C)
                        frame = result[j]
                        
                        # 转换为 (1, C, H, W) 格式
                        frame_nchw = frame.unsqueeze(0).permute(0, 3, 1, 2)
                        
                        # 计算旋转矩阵（仿射变换）
                        # 旋转中心为图像中心
                        center_x = width / 2.0
                        center_y = height / 2.0
                        
                        # 构建旋转矩阵
                        cos_a = math.cos(angle_rad)
                        sin_a = math.sin(angle_rad)
                        
                        # 仿射变换矩阵 [2x3]
                        theta = torch.tensor([
                            [cos_a, -sin_a, (1 - cos_a) * center_x + sin_a * center_y],
                            [sin_a, cos_a, -sin_a * center_x + (1 - cos_a) * center_y]
                        ], dtype=torch.float32, device=frame.device).unsqueeze(0)
                        
                        # 生成采样网格
                        grid = F.affine_grid(theta, frame_nchw.size(), align_corners=False)
                        
                        # 应用旋转（使用双线性插值）
                        rotated = F.grid_sample(
                            frame_nchw,
                            grid,
                            mode='bilinear',
                            padding_mode='border',
                            align_corners=False
                        )
                        
                        # 转换回 (H, W, C) 格式
                        result[j] = rotated.squeeze(0).permute(1, 2, 0)
                
                elif 卡点效果 == "抖动":
                    # 抖动效果：快速随机位移，模拟震动
                    jitter_intensity = 效果强度 * fade
                    
                    if jitter_intensity > 0.01:
                        # 使用相对帧索引生成抖动位移（高频振动）
                        freq_x = 20.0 + relative_frame * 0.3  # X方向频率
                        freq_y = 25.0 + relative_frame * 0.4  # Y方向频率
                        
                        # 计算抖动偏移量（像素）
                        offset_x = int(math.sin(freq_x) * jitter_intensity * 15.0)
                        offset_y = int(math.cos(freq_y) * jitter_intensity * 15.0)
                        
                        # 获取当前帧
                        frame = result[j]
                        
                        # 应用位移（通过滚动实现）
                        if offset_x != 0 or offset_y != 0:
                            frame = torch.roll(frame, shifts=(offset_y, offset_x), dims=(0, 1))
                        
                        # 添加轻微的噪声增强抖动感
                        if jitter_intensity > 0.3:
                            noise = torch.randn_like(frame) * 0.01 * jitter_intensity
                            frame = frame + noise
                            frame = torch.clamp(frame, 0.0, 1.0)
                        
                        result[j] = frame
                
                elif 卡点效果 == "色彩爆炸":
                    # 色彩爆炸（饱和度瞬间提升）
                    gray = 0.299 * result[j, ..., 0:1] + 0.587 * result[j, ..., 1:2] + 0.114 * result[j, ..., 2:3]
                    gray_rgb = gray.repeat(1, 1, 3)
                    saturated = result[j] + (result[j] - gray_rgb) * 效果强度 * fade
                    result[j] = torch.clamp(saturated, 0, 1)
                
                elif 卡点效果 == "模糊":
                    # 模糊效果：高斯模糊
                    blur_intensity = 效果强度 * fade
                    if blur_intensity > 0.01:
                        frame = result[j]
                        # 转换为 (1, C, H, W) 格式
                        frame_nchw = frame.unsqueeze(0).permute(0, 3, 1, 2)
                        
                        # 计算模糊核大小（必须是奇数）
                        kernel_size = int(blur_intensity * 15) * 2 + 1
                        kernel_size = min(kernel_size, 21)  # 限制最大核大小
                        
                        if kernel_size > 1:
                            # 创建高斯模糊核
                            device = frame.device
                            sigma = kernel_size / 6.0
                            kernel_1d = torch.exp(-torch.arange(kernel_size, dtype=torch.float32, device=device).sub(kernel_size // 2).pow(2) / (2 * sigma * sigma))
                            kernel_1d = kernel_1d / kernel_1d.sum()
                            kernel_2d = kernel_1d[:, None] * kernel_1d[None, :]
                            kernel_2d = kernel_2d.view(1, 1, kernel_size, kernel_size).repeat(channels, 1, 1, 1).to(device)
                            
                            # 应用卷积模糊
                            blurred = F.conv2d(frame_nchw, kernel_2d, padding=kernel_size//2, groups=channels)
                            result[j] = blurred.squeeze(0).permute(1, 2, 0)
                
                elif 卡点效果 == "像素化":
                    # 像素化效果：降低分辨率再放大
                    pixel_intensity = 效果强度 * fade
                    if pixel_intensity > 0.01:
                        # 转换为 (1, C, H, W) 格式
                        frame_nchw = result[j].unsqueeze(0).permute(0, 3, 1, 2)
                        
                        # 计算像素化后的尺寸
                        pixel_size = max(2, int(20 / (1 + pixel_intensity * 10)))
                        new_h = max(1, height // pixel_size)
                        new_w = max(1, width // pixel_size)
                        
                        # 缩小
                        pixelated = F.interpolate(frame_nchw, size=(new_h, new_w), mode='nearest', align_corners=False)
                        # 放大回原尺寸
                        result[j] = F.interpolate(pixelated, size=(height, width), mode='nearest', align_corners=False).squeeze(0).permute(1, 2, 0)
                
                elif 卡点效果 == "故障效果":
                    # 故障效果：RGB通道分离 + 扫描线
                    glitch_intensity = 效果强度 * fade
                    if glitch_intensity > 0.01:
                        frame = result[j].clone()
                        
                        # RGB通道分离
                        offset = int(glitch_intensity * 10)
                        if offset > 0:
                            # R通道向右偏移
                            frame[:, :, 0] = torch.roll(frame[:, :, 0], shifts=offset, dims=1)
                            # B通道向左偏移
                            frame[:, :, 2] = torch.roll(frame[:, :, 2], shifts=-offset, dims=1)
                        
                        # 添加扫描线
                        scan_line_count = int(glitch_intensity * 5)
                        for _ in range(scan_line_count):
                            line_y = torch.randint(0, height, (1,)).item()
                            line_width = torch.randint(1, 3, (1,)).item()
                            frame[line_y:line_y+line_width, :, :] = torch.rand_like(frame[line_y:line_y+line_width, :, :])
                        
                        result[j] = frame
                
                elif 卡点效果 == "波纹":
                    # 波纹效果：水波涟漪
                    wave_intensity = 效果强度 * fade
                    if wave_intensity > 0.01:
                        frame = result[j]
                        frame_nchw = frame.unsqueeze(0).permute(0, 3, 1, 2)
                        
                        # 创建波纹网格
                        y_coords = torch.arange(height, dtype=torch.float32, device=frame.device)
                        x_coords = torch.arange(width, dtype=torch.float32, device=frame.device)
                        y_grid, x_grid = torch.meshgrid(y_coords, x_coords, indexing='ij')
                        
                        # 计算到中心的距离
                        center_y, center_x = height / 2.0, width / 2.0
                        dist = torch.sqrt((x_grid - center_x) ** 2 + (y_grid - center_y) ** 2)
                        
                        # 波纹偏移（使用相对帧索引）
                        wave_offset = wave_intensity * 5.0 * torch.sin(dist * 0.1 + relative_frame * 0.5)
                        x_offset = wave_offset * (x_grid - center_x) / (dist + 1e-8)
                        y_offset = wave_offset * (y_grid - center_y) / (dist + 1e-8)
                        
                        # 归一化到[-1, 1]
                        x_normalized = ((x_grid + x_offset) / (width - 1)) * 2.0 - 1.0
                        y_normalized = ((y_grid + y_offset) / (height - 1)) * 2.0 - 1.0
                        
                        # 创建采样网格
                        sample_grid = torch.stack([x_normalized, y_normalized], dim=-1).unsqueeze(0)
                        
                        # 应用波纹
                        waved = F.grid_sample(frame_nchw, sample_grid, mode='bilinear', padding_mode='border', align_corners=False)
                        result[j] = waved.squeeze(0).permute(1, 2, 0)
                
                elif 卡点效果 == "径向模糊":
                    # 径向模糊：从中心向外模糊
                    radial_intensity = 效果强度 * fade
                    if radial_intensity > 0.01:
                        frame = result[j]
                        frame_nchw = frame.unsqueeze(0).permute(0, 3, 1, 2)
                        
                        # 创建径向采样网格
                        y_coords = torch.arange(height, dtype=torch.float32, device=frame.device)
                        x_coords = torch.arange(width, dtype=torch.float32, device=frame.device)
                        y_grid, x_grid = torch.meshgrid(y_coords, x_coords, indexing='ij')
                        
                        center_y, center_x = height / 2.0, width / 2.0
                        dist = torch.sqrt((x_grid - center_x) ** 2 + (y_grid - center_y) ** 2)
                        max_dist = math.sqrt(center_x ** 2 + center_y ** 2)
                        
                        # 径向偏移
                        radial_offset = radial_intensity * 10.0 * (dist / max_dist)
                        angle = torch.atan2(y_grid - center_y, x_grid - center_x)
                        x_offset = radial_offset * torch.cos(angle)
                        y_offset = radial_offset * torch.sin(angle)
                        
                        # 归一化
                        x_normalized = ((x_grid + x_offset) / (width - 1)) * 2.0 - 1.0
                        y_normalized = ((y_grid + y_offset) / (height - 1)) * 2.0 - 1.0
                        
                        sample_grid = torch.stack([x_normalized, y_normalized], dim=-1).unsqueeze(0)
                        blurred = F.grid_sample(frame_nchw, sample_grid, mode='bilinear', padding_mode='border', align_corners=False)
                        result[j] = blurred.squeeze(0).permute(1, 2, 0)
                
                elif 卡点效果 == "负片":
                    # 负片效果：颜色反转
                    negative_intensity = 效果强度 * fade
                    if negative_intensity > 0.01:
                        result[j] = 1.0 - result[j] * negative_intensity + result[j] * (1.0 - negative_intensity)
                
                elif 卡点效果 == "老电影":
                    # 老电影效果：噪点 + 闪烁 + 色偏
                    film_intensity = 效果强度 * fade
                    if film_intensity > 0.01:
                        frame = result[j]
                        
                        # 添加噪点
                        noise = torch.randn_like(frame) * film_intensity * 0.1
                        frame = frame + noise
                        
                        # 色偏（偏黄）
                        frame[:, :, 0] = frame[:, :, 0] * (1.0 + film_intensity * 0.2)  # 增强红色
                        frame[:, :, 2] = frame[:, :, 2] * (1.0 - film_intensity * 0.1)  # 减弱蓝色
                        
                        # 闪烁
                        flicker = 1.0 - film_intensity * 0.1 * (torch.rand(1, device=frame.device).item() - 0.5)
                        frame = frame * flicker
                        
                        result[j] = torch.clamp(frame, 0.0, 1.0)
                
                elif 卡点效果 == "边缘发光":
                    # 边缘发光效果：边缘高光
                    glow_intensity = 效果强度 * fade
                    if glow_intensity > 0.01:
                        frame = result[j]
                        frame_nchw = frame.unsqueeze(0).permute(0, 3, 1, 2)
                        
                        # 使用Sobel算子检测边缘
                        device = frame.device
                        sobel_x = torch.tensor([[-1, 0, 1], [-2, 0, 2], [-1, 0, 1]], dtype=torch.float32, device=device).view(1, 1, 3, 3)
                        sobel_y = torch.tensor([[-1, -2, -1], [0, 0, 0], [1, 2, 1]], dtype=torch.float32, device=device).view(1, 1, 3, 3)
                        
                        # 转换为灰度
                        gray = 0.299 * frame_nchw[:, 0:1, :, :] + 0.587 * frame_nchw[:, 1:2, :, :] + 0.114 * frame_nchw[:, 2:3, :, :]
                        
                        # 检测边缘
                        edge_x = F.conv2d(gray, sobel_x, padding=1)
                        edge_y = F.conv2d(gray, sobel_y, padding=1)
                        edges = torch.sqrt(edge_x ** 2 + edge_y ** 2)
                        edges = edges / (edges.max() + 1e-8)  # 归一化
                        
                        # 应用发光
                        glow = edges * glow_intensity * 0.5
                        glow_rgb = glow.repeat(1, channels, 1, 1)
                        frame_nchw = frame_nchw + glow_rgb
                        
                        result[j] = torch.clamp(frame_nchw.squeeze(0).permute(1, 2, 0), 0.0, 1.0)
                
                elif 卡点效果 == "冲击波":
                    # 冲击波效果：从中心向外扩散的冲击波
                    shock_intensity = 效果强度 * fade
                    if shock_intensity > 0.01:
                        frame = result[j]
                        frame_nchw = frame.unsqueeze(0).permute(0, 3, 1, 2)
                        
                        # 创建坐标网格
                        y_coords = torch.arange(height, dtype=torch.float32, device=frame.device)
                        x_coords = torch.arange(width, dtype=torch.float32, device=frame.device)
                        y_grid, x_grid = torch.meshgrid(y_coords, x_coords, indexing='ij')
                        
                        center_y, center_x = height / 2.0, width / 2.0
                        dist = torch.sqrt((x_grid - center_x) ** 2 + (y_grid - center_y) ** 2)
                        max_dist = math.sqrt(center_x ** 2 + center_y ** 2)
                        
                        # 冲击波：径向向外推拉
                        wave_radius = relative_frame * 0.3 * max_dist
                        wave_width = max_dist * 0.1
                        wave_strength = shock_intensity * 8.0 * torch.exp(-((dist - wave_radius) ** 2) / (2 * wave_width ** 2))
                        
                        angle = torch.atan2(y_grid - center_y, x_grid - center_x)
                        x_offset = wave_strength * torch.cos(angle)
                        y_offset = wave_strength * torch.sin(angle)
                        
                        # 归一化
                        x_normalized = ((x_grid + x_offset) / (width - 1)) * 2.0 - 1.0
                        y_normalized = ((y_grid + y_offset) / (height - 1)) * 2.0 - 1.0
                        
                        sample_grid = torch.stack([x_normalized, y_normalized], dim=-1).unsqueeze(0)
                        shocked = F.grid_sample(frame_nchw, sample_grid, mode='bilinear', padding_mode='reflection', align_corners=False)
                        result[j] = shocked.squeeze(0).permute(1, 2, 0)
                
                elif 卡点效果 == "粒子爆炸":
                    # 粒子爆炸效果：径向缩放 + 亮度爆炸 + 色散
                    explosion_intensity = 效果强度 * fade
                    if explosion_intensity > 0.01:
                        frame = result[j]
                        frame_nchw = frame.unsqueeze(0).permute(0, 3, 1, 2)
                        
                        # 径向缩放
                        scale = 1.0 + explosion_intensity * 0.4 * (1.0 - progress)
                        new_h = max(1, int(height * scale))
                        new_w = max(1, int(width * scale))
                        
                        if new_h != height or new_w != width:
                            scaled = F.interpolate(frame_nchw, size=(new_h, new_w), mode='bilinear', align_corners=False)
                            y_start = (new_h - height) // 2
                            x_start = (new_w - width) // 2
                            result[j] = scaled[0, :, y_start:y_start+height, x_start:x_start+width].permute(1, 2, 0)
                        
                        # 亮度爆炸（中心强，边缘弱）
                        y_coords = torch.arange(height, dtype=torch.float32, device=frame.device)
                        x_coords = torch.arange(width, dtype=torch.float32, device=frame.device)
                        y_grid, x_grid = torch.meshgrid(y_coords, x_coords, indexing='ij')
                        center_y, center_x = height / 2.0, width / 2.0
                        dist = torch.sqrt((x_grid - center_x) ** 2 + (y_grid - center_y) ** 2)
                        max_dist = math.sqrt(center_x ** 2 + center_y ** 2)
                        brightness = 1.0 + explosion_intensity * 0.8 * (1.0 - dist / max_dist)
                        result[j] = result[j] * brightness.unsqueeze(-1)
                        
                        # RGB通道分离（色散效果）
                        offset = int(explosion_intensity * 8)
                        if offset > 0:
                            result[j, :, :, 0] = torch.roll(result[j, :, :, 0], shifts=offset, dims=1)
                            result[j, :, :, 2] = torch.roll(result[j, :, :, 2], shifts=-offset, dims=1)
                        
                        result[j] = torch.clamp(result[j], 0.0, 1.0)
                
                elif 卡点效果 == "能量脉冲":
                    # 能量脉冲效果：中心向外扩散的能量波
                    pulse_intensity = 效果强度 * fade
                    if pulse_intensity > 0.01:
                        frame = result[j]
                        frame_nchw = frame.unsqueeze(0).permute(0, 3, 1, 2)
                        
                        # 创建坐标网格
                        y_coords = torch.arange(height, dtype=torch.float32, device=frame.device)
                        x_coords = torch.arange(width, dtype=torch.float32, device=frame.device)
                        y_grid, x_grid = torch.meshgrid(y_coords, x_coords, indexing='ij')
                        
                        center_y, center_x = height / 2.0, width / 2.0
                        dist = torch.sqrt((x_grid - center_x) ** 2 + (y_grid - center_y) ** 2)
                        max_dist = math.sqrt(center_x ** 2 + center_y ** 2)
                        
                        # 能量波：多个同心圆脉冲
                        pulse_phase = relative_frame * 0.5
                        pulse_radius = (pulse_phase % 1.0) * max_dist
                        pulse_width = max_dist * 0.15
                        pulse_strength = pulse_intensity * 6.0 * torch.exp(-((dist - pulse_radius) ** 2) / (2 * pulse_width ** 2))
                        
                        # 径向推拉
                        angle = torch.atan2(y_grid - center_y, x_grid - center_x)
                        x_offset = pulse_strength * torch.cos(angle)
                        y_offset = pulse_strength * torch.sin(angle)
                        
                        # 归一化
                        x_normalized = ((x_grid + x_offset) / (width - 1)) * 2.0 - 1.0
                        y_normalized = ((y_grid + y_offset) / (height - 1)) * 2.0 - 1.0
                        
                        sample_grid = torch.stack([x_normalized, y_normalized], dim=-1).unsqueeze(0)
                        pulsed = F.grid_sample(frame_nchw, sample_grid, mode='bilinear', padding_mode='reflection', align_corners=False)
                        
                        # 添加发光效果
                        glow = pulse_strength.unsqueeze(0).unsqueeze(0) * 0.3
                        glow_rgb = glow.repeat(1, channels, 1, 1)
                        frame_nchw = pulsed + glow_rgb
                        
                        result[j] = torch.clamp(frame_nchw.squeeze(0).permute(1, 2, 0), 0.0, 1.0)
                
                elif 卡点效果 == "时间扭曲":
                    # 时间扭曲效果：径向扭曲 + 模糊
                    twist_intensity = 效果强度 * fade
                    if twist_intensity > 0.01:
                        frame = result[j]
                        frame_nchw = frame.unsqueeze(0).permute(0, 3, 1, 2)
                        
                        # 创建坐标网格
                        y_coords = torch.arange(height, dtype=torch.float32, device=frame.device)
                        x_coords = torch.arange(width, dtype=torch.float32, device=frame.device)
                        y_grid, x_grid = torch.meshgrid(y_coords, x_coords, indexing='ij')
                        
                        center_y, center_x = height / 2.0, width / 2.0
                        dist = torch.sqrt((x_grid - center_x) ** 2 + (y_grid - center_y) ** 2)
                        angle = torch.atan2(y_grid - center_y, x_grid - center_x)
                        
                        # 螺旋扭曲
                        twist_amount = twist_intensity * 0.5 * (1.0 - dist / math.sqrt(center_x ** 2 + center_y ** 2))
                        new_angle = angle + twist_amount * relative_frame * 0.1
                        
                        # 径向压缩
                        radial_scale = 1.0 - twist_intensity * 0.2 * (1.0 - dist / math.sqrt(center_x ** 2 + center_y ** 2))
                        new_dist = dist * radial_scale
                        
                        x_new = center_x + new_dist * torch.cos(new_angle)
                        y_new = center_y + new_dist * torch.sin(new_angle)
                        
                        # 归一化
                        x_normalized = (x_new / (width - 1)) * 2.0 - 1.0
                        y_normalized = (y_new / (height - 1)) * 2.0 - 1.0
                        
                        sample_grid = torch.stack([x_normalized, y_normalized], dim=-1).unsqueeze(0)
                        twisted = F.grid_sample(frame_nchw, sample_grid, mode='bilinear', padding_mode='reflection', align_corners=False)
                        result[j] = twisted.squeeze(0).permute(1, 2, 0)
                
                elif 卡点效果 == "镜头震动":
                    # 镜头震动效果：多方向随机震动
                    shake_intensity = 效果强度 * fade
                    if shake_intensity > 0.01:
                        frame = result[j]
                        frame_nchw = frame.unsqueeze(0).permute(0, 3, 1, 2)
                        
                        # 高频震动（使用相对帧索引）
                        freq = 30.0 + relative_frame * 0.5
                        offset_x = math.sin(freq * 1.3) * shake_intensity * 20.0
                        offset_y = math.cos(freq * 1.7) * shake_intensity * 20.0
                        offset_rot = math.sin(freq * 0.9) * shake_intensity * 5.0
                        
                        # 创建坐标网格
                        y_coords = torch.arange(height, dtype=torch.float32, device=frame.device)
                        x_coords = torch.arange(width, dtype=torch.float32, device=frame.device)
                        y_grid, x_grid = torch.meshgrid(y_coords, x_coords, indexing='ij')
                        
                        center_y, center_x = height / 2.0, width / 2.0
                        
                        # 应用位移和旋转
                        x_centered = x_grid - center_x
                        y_centered = y_grid - center_y
                        
                        angle_rad = math.radians(offset_rot)
                        cos_a = math.cos(angle_rad)
                        sin_a = math.sin(angle_rad)
                        
                        x_rotated = x_centered * cos_a - y_centered * sin_a
                        y_rotated = x_centered * sin_a + y_centered * cos_a
                        
                        x_new = x_rotated + center_x + offset_x
                        y_new = y_rotated + center_y + offset_y
                        
                        # 归一化
                        x_normalized = (x_new / (width - 1)) * 2.0 - 1.0
                        y_normalized = (y_new / (height - 1)) * 2.0 - 1.0
                        
                        sample_grid = torch.stack([x_normalized, y_normalized], dim=-1).unsqueeze(0)
                        shaken = F.grid_sample(frame_nchw, sample_grid, mode='bilinear', padding_mode='reflection', align_corners=False)
                        result[j] = shaken.squeeze(0).permute(1, 2, 0)
                
                elif 卡点效果 == "色彩分离":
                    # 色彩分离效果：RGB通道大幅分离 + 色差
                    separation_intensity = 效果强度 * fade
                    if separation_intensity > 0.01:
                        frame = result[j].clone()
                        
                        # RGB通道大幅分离
                        offset = int(separation_intensity * 15)
                        if offset > 0:
                            # R通道向右上偏移
                            frame[:, :, 0] = torch.roll(frame[:, :, 0], shifts=(offset, offset), dims=(0, 1))
                            # G通道保持
                            # B通道向左下偏移
                            frame[:, :, 2] = torch.roll(frame[:, :, 2], shifts=(-offset, -offset), dims=(0, 1))
                        
                        # 增强对比度和饱和度
                        gray = 0.299 * frame[:, :, 0:1] + 0.587 * frame[:, :, 1:2] + 0.114 * frame[:, :, 2:3]
                        saturated = frame + (frame - gray.repeat(1, 1, 3)) * separation_intensity * 0.5
                        
                        result[j] = torch.clamp(saturated, 0.0, 1.0)
                
                elif 卡点效果 == "光晕扩散":
                    # 光晕扩散效果：中心向外扩散的光晕
                    glow_intensity = 效果强度 * fade
                    if glow_intensity > 0.01:
                        frame = result[j]
                        
                        # 创建坐标网格
                        y_coords = torch.arange(height, dtype=torch.float32, device=frame.device)
                        x_coords = torch.arange(width, dtype=torch.float32, device=frame.device)
                        y_grid, x_grid = torch.meshgrid(y_coords, x_coords, indexing='ij')
                        
                        center_y, center_x = height / 2.0, width / 2.0
                        dist = torch.sqrt((x_grid - center_x) ** 2 + (y_grid - center_y) ** 2)
                        max_dist = math.sqrt(center_x ** 2 + center_y ** 2)
                        
                        # 光晕强度（中心强，向外衰减）
                        glow_radius = relative_frame * 0.4 * max_dist
                        glow_width = max_dist * 0.2
                        glow_strength = glow_intensity * 0.6 * torch.exp(-((dist - glow_radius) ** 2) / (2 * glow_width ** 2))
                        
                        # 应用光晕（增强亮度）
                        glow_mask = glow_strength.unsqueeze(-1)
                        result[j] = result[j] + glow_mask * 0.5
                        result[j] = torch.clamp(result[j], 0.0, 1.0)
                
                elif 卡点效果 == "速度线":
                    # 速度线效果：径向运动模糊
                    speed_intensity = 效果强度 * fade
                    if speed_intensity > 0.01:
                        frame = result[j]
                        frame_nchw = frame.unsqueeze(0).permute(0, 3, 1, 2)
                        
                        # 创建坐标网格
                        y_coords = torch.arange(height, dtype=torch.float32, device=frame.device)
                        x_coords = torch.arange(width, dtype=torch.float32, device=frame.device)
                        y_grid, x_grid = torch.meshgrid(y_coords, x_coords, indexing='ij')
                        
                        center_y, center_x = height / 2.0, width / 2.0
                        angle = torch.atan2(y_grid - center_y, x_grid - center_x)
                        
                        # 径向运动模糊（从中心向外）
                        blur_amount = speed_intensity * 10.0
                        x_offset = blur_amount * torch.cos(angle) * (1.0 - progress)
                        y_offset = blur_amount * torch.sin(angle) * (1.0 - progress)
                        
                        # 归一化
                        x_normalized = ((x_grid + x_offset) / (width - 1)) * 2.0 - 1.0
                        y_normalized = ((y_grid + y_offset) / (height - 1)) * 2.0 - 1.0
                        
                        sample_grid = torch.stack([x_normalized, y_normalized], dim=-1).unsqueeze(0)
                        speeded = F.grid_sample(frame_nchw, sample_grid, mode='bilinear', padding_mode='reflection', align_corners=False)
                        result[j] = speeded.squeeze(0).permute(1, 2, 0)
                
                elif 卡点效果 == "镜头拉近":
                    # 镜头拉近效果：快速放大 + 轻微模糊
                    zoom_intensity = 效果强度 * fade
                    if zoom_intensity > 0.01:
                        frame = result[j]
                        frame_nchw = frame.unsqueeze(0).permute(0, 3, 1, 2)
                        
                        # 快速放大（从1.0到1.5）
                        zoom_scale = 1.0 + zoom_intensity * 0.5 * (1.0 - progress)
                        new_h = max(1, int(height * zoom_scale))
                        new_w = max(1, int(width * zoom_scale))
                        
                        if new_h != height or new_w != width:
                            scaled = F.interpolate(frame_nchw, size=(new_h, new_w), mode='bilinear', align_corners=False)
                            # 裁剪中心
                            y_start = (new_h - height) // 2
                            x_start = (new_w - width) // 2
                            result[j] = scaled[0, :, y_start:y_start+height, x_start:x_start+width].permute(1, 2, 0)
                
                elif 卡点效果 == "镜头拉远":
                    # 镜头拉远效果：快速缩小 + 填充
                    zoom_intensity = 效果强度 * fade
                    if zoom_intensity > 0.01:
                        frame = result[j]
                        frame_nchw = frame.unsqueeze(0).permute(0, 3, 1, 2)
                        
                        # 快速缩小（从1.0到0.7）
                        zoom_scale = 1.0 - zoom_intensity * 0.3 * (1.0 - progress)
                        new_h = max(1, int(height * zoom_scale))
                        new_w = max(1, int(width * zoom_scale))
                        
                        if new_h != height or new_w != width:
                            scaled = F.interpolate(frame_nchw, size=(new_h, new_w), mode='bilinear', align_corners=False)
                            # 填充到原尺寸（黑色背景）
                            padded = torch.zeros(1, channels, height, width, device=frame.device)
                            y_start = (height - new_h) // 2
                            x_start = (width - new_w) // 2
                            padded[0, :, y_start:y_start+new_h, x_start:x_start+new_w] = scaled[0]
                            result[j] = padded.squeeze(0).permute(1, 2, 0)
        
        output_frames = result.shape[0]
        output_duration = output_frames / 视频帧率
        
        print(f"[卡点效果] 类型:{卡点效果}, 间隔:{卡点间隔}s, 共{beat_count}个卡点")
        
        return (result, output_frames, output_duration)

