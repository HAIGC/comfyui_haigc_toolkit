"""
蒙版功能节点 - 增强版
区域遮罩处理 + 动画效果 + 位置移动
"""

import torch
import torch.nn.functional as F
import math

class VideoMaskNode:
    """蒙版功能节点 - 增强版"""
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "video1": ("IMAGE",),
                "视频帧率": ("FLOAT", {
                    "default": 30.0,
                    "min": 1.0,
                    "max": 120.0,
                    "step": 0.1
                }),
                "多视频模式": (["单视频", "双视频叠加", "三视频叠加", "视频拼接"], {
                    "default": "单视频"
                }),
                "蒙版类型": ([
                    "矩形", "圆形", "椭圆", 
                    "心形", "星形", "菱形", "六边形", "八边形",
                    "渐变-上下", "渐变-左右", "渐变-对角", "渐变-径向",
                    "边角暗角", "中心光晕", "扫光",
                    "斑马条纹", "棋盘格", "圆点"
                ], {
                    "default": "矩形"
                }),
                "蒙版模式": ([
                    "保留内部", "保留外部", 
                    "模糊外部", "模糊内部",
                    "黑色填充", "白色填充", "彩色填充",
                    "叠加混合", "颜色混合"
                ], {
                    "default": "保留内部"
                }),
                
                # === 位置和大小 ===
                "起始中心X": ("FLOAT", {
                    "default": 0.5,
                    "min": -0.5,
                    "max": 1.5,
                    "step": 0.01
                }),
                "起始中心Y": ("FLOAT", {
                    "default": 0.5,
                    "min": -0.5,
                    "max": 1.5,
                    "step": 0.01
                }),
                "结束中心X": ("FLOAT", {
                    "default": 0.5,
                    "min": -0.5,
                    "max": 1.5,
                    "step": 0.01
                }),
                "结束中心Y": ("FLOAT", {
                    "default": 0.5,
                    "min": -0.5,
                    "max": 1.5,
                    "step": 0.01
                }),
                
                # === 尺寸动画 ===
                "起始宽度": ("FLOAT", {
                    "default": 0.5,
                    "min": 0.0,
                    "max": 2.0,
                    "step": 0.01
                }),
                "起始高度": ("FLOAT", {
                    "default": 0.5,
                    "min": 0.0,
                    "max": 2.0,
                    "step": 0.01
                }),
                "结束宽度": ("FLOAT", {
                    "default": 0.5,
                    "min": 0.0,
                    "max": 2.0,
                    "step": 0.01
                }),
                "结束高度": ("FLOAT", {
                    "default": 0.5,
                    "min": 0.0,
                    "max": 2.0,
                    "step": 0.01
                }),
                
                # === 旋转动画 ===
                "起始旋转角度": ("FLOAT", {
                    "default": 0.0,
                    "min": -360.0,
                    "max": 360.0,
                    "step": 1.0
                }),
                "结束旋转角度": ("FLOAT", {
                    "default": 0.0,
                    "min": -360.0,
                    "max": 360.0,
                    "step": 1.0
                }),
                
                # === 羽化和效果 ===
                "羽化": ("INT", {
                    "default": 20,
                    "min": 0,
                    "max": 200,
                    "step": 5
                }),
                "不透明度": ("FLOAT", {
                    "default": 1.0,
                    "min": 0.0,
                    "max": 1.0,
                    "step": 0.05
                }),
                
                # === 动画设置 ===
                "启用动画": (["否", "是"], {
                    "default": "否"
                }),
                "缓动方式": (["线性", "缓入", "缓出", "缓入缓出", "弹性", "回弹"], {
                    "default": "线性"
                }),
                
                # === 特殊参数 ===
                "星形角数": ("INT", {
                    "default": 5,
                    "min": 3,
                    "max": 12,
                    "step": 1
                }),
                "条纹数量": ("INT", {
                    "default": 10,
                    "min": 2,
                    "max": 50,
                    "step": 1
                }),
                "填充颜色R": ("FLOAT", {
                    "default": 1.0,
                    "min": 0.0,
                    "max": 1.0,
                    "step": 0.01
                }),
                "填充颜色G": ("FLOAT", {
                    "default": 0.0,
                    "min": 0.0,
                    "max": 1.0,
                    "step": 0.01
                }),
                "填充颜色B": ("FLOAT", {
                    "default": 0.0,
                    "min": 0.0,
                    "max": 1.0,
                    "step": 0.01
                }),
                
                # === 多视频叠加参数 ===
                "叠加方式": (["正常叠加", "蒙版混合", "交替显示", "渐变过渡"], {
                    "default": "正常叠加"
                }),
                "video2权重": ("FLOAT", {
                    "default": 0.5,
                    "min": 0.0,
                    "max": 1.0,
                    "step": 0.05
                }),
                "video3权重": ("FLOAT", {
                    "default": 0.33,
                    "min": 0.0,
                    "max": 1.0,
                    "step": 0.05
                }),
                
                # === 视频拼接参数 ===
                "拼接方向": (["横向拼接", "纵向拼接", "九宫格", "画中画"], {
                    "default": "横向拼接"
                }),
                "拼接间隔": ("INT", {
                    "default": 0,
                    "min": 0,
                    "max": 50,
                    "step": 1
                }),
            },
            "optional": {
                "video2": ("IMAGE",),
                "video3": ("IMAGE",),
            }
        }
    
    RETURN_TYPES = ("IMAGE", "INT", "FLOAT")
    RETURN_NAMES = ("视频", "输出帧数", "输出时长")
    FUNCTION = "apply_mask"
    CATEGORY = "HAIGC工具集/视频剪辑"
    
    def ease_function(self, t, 缓动方式):
        """缓动函数"""
        if 缓动方式 == "线性":
            return t
        elif 缓动方式 == "缓入":
            return t * t * t
        elif 缓动方式 == "缓出":
            return 1 - (1 - t) ** 3
        elif 缓动方式 == "缓入缓出":
            if t < 0.5:
                return 4 * t * t * t
            else:
                return 1 - (-2 * t + 2) ** 3 / 2
        elif 缓动方式 == "弹性":
            c4 = (2 * math.pi) / 3
            if t == 0 or t == 1:
                return t
            return math.pow(2, -10 * t) * math.sin((t * 10 - 0.75) * c4) + 1
        elif 缓动方式 == "回弹":
            c1 = 1.70158
            c3 = c1 + 1
            return 1 + c3 * math.pow(t - 1, 3) + c1 * math.pow(t - 1, 2)
        return t
    
    def apply_mask(self, video1, 视频帧率, 多视频模式, 蒙版类型, 蒙版模式,
                   起始中心X, 起始中心Y, 结束中心X, 结束中心Y,
                   起始宽度, 起始高度, 结束宽度, 结束高度,
                   起始旋转角度, 结束旋转角度,
                   羽化, 不透明度, 启用动画, 缓动方式,
                   星形角数, 条纹数量, 填充颜色R, 填充颜色G, 填充颜色B,
                   叠加方式, video2权重, video3权重, 拼接方向, 拼接间隔,
                   video2=None, video3=None):
        """应用蒙版 - 增强版（支持多视频）"""
        
        # 收集所有视频
        videos = [video1]
        if video2 is not None and 多视频模式 != "单视频":
            videos.append(video2)
        if video3 is not None and 多视频模式 == "三视频叠加":
            videos.append(video3)
        
        # 处理多视频模式
        if 多视频模式 == "视频拼接" and len(videos) > 1:
            # 视频拼接模式
            images = self.splice_videos(videos, 拼接方向, 拼接间隔)
            batch_size, img_height, img_width, channels = images.shape
            result = images.clone()
        elif 多视频模式 in ["双视频叠加", "三视频叠加"] and len(videos) > 1:
            # 多视频叠加，先处理第一个视频
            images = video1
            batch_size, img_height, img_width, channels = images.shape
            result = images.clone()
        else:
            # 单视频模式
            images = video1
            batch_size, img_height, img_width, channels = images.shape
            result = images.clone()
        
        # 填充颜色
        fill_color = torch.tensor([填充颜色R, 填充颜色G, 填充颜色B], device=images.device)
        
        # 遍历每一帧
        for frame_idx in range(batch_size):
            # 计算当前帧的插值比例
            t = frame_idx / max(batch_size - 1, 1)
            
            if 启用动画 == "是":
                t_eased = self.ease_function(t, 缓动方式)
                # 插值位置
                current_center_x = 起始中心X + (结束中心X - 起始中心X) * t_eased
                current_center_y = 起始中心Y + (结束中心Y - 起始中心Y) * t_eased
                # 插值尺寸
                current_width = 起始宽度 + (结束宽度 - 起始宽度) * t_eased
                current_height = 起始高度 + (结束高度 - 起始高度) * t_eased
                # 插值旋转
                current_rotation = 起始旋转角度 + (结束旋转角度 - 起始旋转角度) * t_eased
            else:
                current_center_x = 起始中心X
                current_center_y = 起始中心Y
                current_width = 起始宽度
                current_height = 起始高度
                current_rotation = 起始旋转角度
            
            # 转换为像素坐标
            center_x = current_center_x * img_width
            center_y = current_center_y * img_height
            mask_w = current_width * img_width
            mask_h = current_height * img_height
            
            # 创建坐标网格
            y_coords = torch.arange(img_height, device=images.device).view(-1, 1).float()
            x_coords = torch.arange(img_width, device=images.device).view(1, -1).float()
            
            # 旋转坐标（如果需要）
            if current_rotation != 0:
                angle_rad = math.radians(current_rotation)
                cos_a = math.cos(angle_rad)
                sin_a = math.sin(angle_rad)
                
                # 平移到中心
                x_centered = x_coords - center_x
                y_centered = y_coords - center_y
                
                # 旋转
                x_rotated = x_centered * cos_a - y_centered * sin_a
                y_rotated = x_centered * sin_a + y_centered * cos_a
                
                # 平移回来
                x_coords = x_rotated + center_x
                y_coords = y_rotated + center_y
            
            # 根据蒙版类型创建蒙版
            mask = self.create_mask_shape(
                蒙版类型, x_coords, y_coords, center_x, center_y,
                mask_w, mask_h, 羽化, 星形角数, 条纹数量,
                img_width, img_height, frame_idx, batch_size
            )
            
            # 应用不透明度
            mask = mask * 不透明度
            
            # 应用蒙版模式
            result[frame_idx] = self.apply_mask_mode(
                images[frame_idx], mask, 蒙版模式, fill_color
            )
        
        # 处理多视频叠加
        if 多视频模式 in ["双视频叠加", "三视频叠加"] and len(videos) > 1:
            result = self.overlay_videos(
                result, videos, mask, 叠加方式, 
                video2权重, video3权重, 多视频模式
            )
        
        output_frames = result.shape[0]
        output_duration = output_frames / 视频帧率
        
        mode_desc = f"{多视频模式}" if 多视频模式 != "单视频" else "单视频"
        print(f"[蒙版增强] 类型:{蒙版类型}, 模式:{蒙版模式}, {mode_desc}, 动画:{'启用' if 启用动画=='是' else '禁用'}")
        
        return (result, output_frames, output_duration)
    
    def create_mask_shape(self, 蒙版类型, x_coords, y_coords, center_x, center_y,
                          mask_w, mask_h, 羽化, 星形角数, 条纹数量,
                          img_width, img_height, frame_idx, batch_size):
        """创建各种形状的蒙版"""
        
        if 蒙版类型 == "矩形":
            # 矩形蒙版
            x1 = center_x - mask_w / 2
            x2 = center_x + mask_w / 2
            y1 = center_y - mask_h / 2
            y2 = center_y + mask_h / 2
            
            dx = torch.minimum(x_coords - x1, x2 - x_coords)
            dy = torch.minimum(y_coords - y1, y2 - y_coords)
            distance = torch.minimum(dx, dy)
            
            if 羽化 > 0:
                mask = torch.clamp(distance / 羽化, 0, 1)
            else:
                mask = (distance > 0).float()
        
        elif 蒙版类型 == "圆形":
            # 圆形蒙版
            radius = min(mask_w, mask_h) / 2
            distance = torch.sqrt((x_coords - center_x) ** 2 + (y_coords - center_y) ** 2)
            
            if 羽化 > 0:
                mask = torch.clamp((radius + 羽化 - distance) / 羽化, 0, 1)
            else:
                mask = (distance <= radius).float()
        
        elif 蒙版类型 == "椭圆":
            # 椭圆蒙版
            x_norm = (x_coords - center_x) / (mask_w / 2 + 1e-6)
            y_norm = (y_coords - center_y) / (mask_h / 2 + 1e-6)
            distance = torch.sqrt(x_norm ** 2 + y_norm ** 2)
            
            if 羽化 > 0:
                feather_factor = 羽化 / (min(mask_w, mask_h) + 1e-6)
                mask = torch.clamp((1 + feather_factor - distance) / feather_factor, 0, 1)
            else:
                mask = (distance <= 1.0).float()
        
        elif 蒙版类型 == "心形":
            # 心形蒙版
            x_norm = (x_coords - center_x) / (mask_w / 2 + 1e-6)
            y_norm = -(y_coords - center_y) / (mask_h / 2 + 1e-6)  # 翻转Y轴
            
            # 心形方程
            heart = (x_norm ** 2 + y_norm ** 2 - 1) ** 3 - x_norm ** 2 * y_norm ** 3
            mask = (heart < 0).float()
            
            if 羽化 > 0:
                distance = torch.abs(heart)
                mask = torch.clamp(1 - distance * 2 / 羽化, 0, 1)
        
        elif 蒙版类型 == "星形":
            # 星形蒙版
            x_norm = (x_coords - center_x) / (mask_w / 2 + 1e-6)
            y_norm = (y_coords - center_y) / (mask_h / 2 + 1e-6)
            
            angle = torch.atan2(y_norm, x_norm)
            distance = torch.sqrt(x_norm ** 2 + y_norm ** 2)
            
            # 星形半径调制
            star_radius = 0.5 + 0.5 * torch.cos(星形角数 * angle)
            
            if 羽化 > 0:
                mask = torch.clamp((star_radius + 羽化 / 100 - distance) * 100 / 羽化, 0, 1)
            else:
                mask = (distance <= star_radius).float()
        
        elif 蒙版类型 == "菱形":
            # 菱形蒙版
            x_dist = torch.abs(x_coords - center_x) / (mask_w / 2 + 1e-6)
            y_dist = torch.abs(y_coords - center_y) / (mask_h / 2 + 1e-6)
            distance = x_dist + y_dist
            
            if 羽化 > 0:
                mask = torch.clamp((1 + 羽化 / 100 - distance) * 100 / 羽化, 0, 1)
            else:
                mask = (distance <= 1.0).float()
        
        elif 蒙版类型 == "六边形":
            # 六边形蒙版
            x_norm = (x_coords - center_x) / (mask_w / 2 + 1e-6)
            y_norm = (y_coords - center_y) / (mask_h / 2 + 1e-6)
            
            angle = torch.atan2(y_norm, x_norm)
            hex_radius = 1.0 / torch.cos((angle % (math.pi / 3)) - math.pi / 6)
            distance = torch.sqrt(x_norm ** 2 + y_norm ** 2)
            
            if 羽化 > 0:
                mask = torch.clamp((hex_radius + 羽化 / 100 - distance) * 100 / 羽化, 0, 1)
            else:
                mask = (distance <= hex_radius).float()
        
        elif 蒙版类型 == "八边形":
            # 八边形蒙版
            x_norm = (x_coords - center_x) / (mask_w / 2 + 1e-6)
            y_norm = (y_coords - center_y) / (mask_h / 2 + 1e-6)
            
            angle = torch.atan2(y_norm, x_norm)
            oct_radius = 1.0 / torch.cos((angle % (math.pi / 4)) - math.pi / 8)
            distance = torch.sqrt(x_norm ** 2 + y_norm ** 2)
            
            if 羽化 > 0:
                mask = torch.clamp((oct_radius + 羽化 / 100 - distance) * 100 / 羽化, 0, 1)
            else:
                mask = (distance <= oct_radius).float()
        
        elif 蒙版类型 == "渐变-上下":
            # 线性渐变（从上到下）
            mask = (img_height - y_coords) / img_height
        
        elif 蒙版类型 == "渐变-左右":
            # 线性渐变（从左到右）
            mask = x_coords / img_width
        
        elif 蒙版类型 == "渐变-对角":
            # 对角渐变
            mask = ((x_coords / img_width) + (y_coords / img_height)) / 2
        
        elif 蒙版类型 == "渐变-径向":
            # 径向渐变（从中心向外）
            distance = torch.sqrt((x_coords - center_x) ** 2 + (y_coords - center_y) ** 2)
            max_dist = torch.sqrt(torch.tensor(img_width ** 2 + img_height ** 2, device=x_coords.device)) / 2
            mask = 1 - torch.clamp(distance / max_dist, 0, 1)
        
        elif 蒙版类型 == "边角暗角":
            # 四角暗角效果
            x_edge = torch.minimum(x_coords, img_width - x_coords) / (img_width / 2)
            y_edge = torch.minimum(y_coords, img_height - y_coords) / (img_height / 2)
            mask = torch.minimum(x_edge, y_edge)
            mask = torch.clamp(mask * 2, 0, 1)
        
        elif 蒙版类型 == "中心光晕":
            # 中心光晕效果
            distance = torch.sqrt((x_coords - center_x) ** 2 + (y_coords - center_y) ** 2)
            max_dist = torch.sqrt(torch.tensor(img_width ** 2 + img_height ** 2, device=x_coords.device)) / 2
            mask = torch.exp(-distance ** 2 / (max_dist ** 2 / 4))
        
        elif 蒙版类型 == "扫光":
            # 扫光效果（动画）
            progress = frame_idx / max(batch_size - 1, 1)
            sweep_angle = progress * 2 * math.pi
            
            angle = torch.atan2(y_coords - center_y, x_coords - center_x)
            angle_diff = (angle - sweep_angle) % (2 * math.pi)
            
            mask = torch.clamp(1 - angle_diff / (math.pi / 4), 0, 1)
        
        elif 蒙版类型 == "斑马条纹":
            # 斑马条纹
            stripe = torch.sin(y_coords * 条纹数量 * math.pi / img_height)
            mask = (stripe > 0).float()
            
            if 羽化 > 0:
                mask = torch.clamp((stripe + 1) / 2, 0, 1)
        
        elif 蒙版类型 == "棋盘格":
            # 棋盘格
            cell_size = img_width / 条纹数量
            x_cell = (x_coords / cell_size).long()
            y_cell = (y_coords / cell_size).long()
            mask = ((x_cell + y_cell) % 2).float()
        
        elif 蒙版类型 == "圆点":
            # 圆点图案
            cell_size = img_width / 条纹数量
            x_mod = (x_coords % cell_size) - cell_size / 2
            y_mod = (y_coords % cell_size) - cell_size / 2
            distance = torch.sqrt(x_mod ** 2 + y_mod ** 2)
            mask = (distance < cell_size / 4).float()
        
        else:
            mask = torch.ones(img_height, img_width, device=x_coords.device)
        
        return mask
    
    def apply_mask_mode(self, image, mask, 蒙版模式, fill_color):
        """应用蒙版模式"""
        # 扩展蒙版维度以匹配图像
        mask_3d = mask.unsqueeze(-1).expand_as(image)
        
        if 蒙版模式 == "保留内部":
            # 保留蒙版内部，外部变黑
            result = image * mask_3d
        
        elif 蒙版模式 == "保留外部":
            # 保留蒙版外部，内部变黑
            result = image * (1 - mask_3d)
        
        elif 蒙版模式 == "模糊外部":
            # 蒙版内部清晰，外部模糊
            blur_kernel = 15
            image_permuted = image.unsqueeze(0).permute(0, 3, 1, 2)
            blurred = F.avg_pool2d(image_permuted, kernel_size=blur_kernel, 
                                  stride=1, padding=blur_kernel//2)
            blurred = blurred.permute(0, 2, 3, 1).squeeze(0)
            result = image * mask_3d + blurred * (1 - mask_3d)
        
        elif 蒙版模式 == "模糊内部":
            # 蒙版外部清晰，内部模糊
            blur_kernel = 15
            image_permuted = image.unsqueeze(0).permute(0, 3, 1, 2)
            blurred = F.avg_pool2d(image_permuted, kernel_size=blur_kernel, 
                                  stride=1, padding=blur_kernel//2)
            blurred = blurred.permute(0, 2, 3, 1).squeeze(0)
            result = blurred * mask_3d + image * (1 - mask_3d)
        
        elif 蒙版模式 == "黑色填充":
            # 蒙版区域填充黑色
            result = image * (1 - mask_3d)
        
        elif 蒙版模式 == "白色填充":
            # 蒙版区域填充白色
            result = image * (1 - mask_3d) + mask_3d
        
        elif 蒙版模式 == "彩色填充":
            # 蒙版区域填充自定义颜色
            fill = fill_color.view(1, 1, 3).expand_as(image)
            result = image * (1 - mask_3d) + fill * mask_3d
        
        elif 蒙版模式 == "叠加混合":
            # 叠加混合模式
            result = image * (1 + mask_3d * 0.5)
            result = torch.clamp(result, 0, 1)
        
        elif 蒙版模式 == "颜色混合":
            # 与填充颜色混合
            fill = fill_color.view(1, 1, 3).expand_as(image)
            result = image * (1 - mask_3d * 0.5) + fill * (mask_3d * 0.5)
        
        else:
            result = image
        
        return result
    
    def splice_videos(self, videos, 拼接方向, 拼接间隔):
        """视频拼接功能"""
        if len(videos) == 1:
            return videos[0]
        
        # 获取所有视频的尺寸
        batch_sizes = [v.shape[0] for v in videos]
        heights = [v.shape[1] for v in videos]
        widths = [v.shape[2] for v in videos]
        channels = videos[0].shape[3]
        device = videos[0].device
        
        # 统一批次大小（取最小值）
        min_batch = min(batch_sizes)
        videos = [v[:min_batch] for v in videos]
        
        if 拼接方向 == "横向拼接":
            # 横向拼接：统一高度，宽度累加
            target_height = max(heights)
            total_width = sum(widths) + 拼接间隔 * (len(videos) - 1)
            
            # 创建结果张量
            result = torch.zeros(min_batch, target_height, total_width, channels, device=device)
            
            # 拼接每个视频
            x_offset = 0
            for i, video in enumerate(videos):
                h, w = video.shape[1], video.shape[2]
                y_offset = (target_height - h) // 2  # 居中对齐
                result[:, y_offset:y_offset+h, x_offset:x_offset+w, :] = video
                x_offset += w + 拼接间隔
            
            print(f"[视频拼接] 横向拼接{len(videos)}个视频, 尺寸:{total_width}x{target_height}")
        
        elif 拼接方向 == "纵向拼接":
            # 纵向拼接：统一宽度，高度累加
            target_width = max(widths)
            total_height = sum(heights) + 拼接间隔 * (len(videos) - 1)
            
            # 创建结果张量
            result = torch.zeros(min_batch, total_height, target_width, channels, device=device)
            
            # 拼接每个视频
            y_offset = 0
            for i, video in enumerate(videos):
                h, w = video.shape[1], video.shape[2]
                x_offset = (target_width - w) // 2  # 居中对齐
                result[:, y_offset:y_offset+h, x_offset:x_offset+w, :] = video
                y_offset += h + 拼接间隔
            
            print(f"[视频拼接] 纵向拼接{len(videos)}个视频, 尺寸:{target_width}x{total_height}")
        
        elif 拼接方向 == "九宫格":
            # 九宫格布局
            num_videos = len(videos)
            grid_size = int(math.ceil(math.sqrt(num_videos)))
            
            # 计算每个格子的尺寸
            cell_height = max(heights)
            cell_width = max(widths)
            total_height = cell_height * grid_size + 拼接间隔 * (grid_size - 1)
            total_width = cell_width * grid_size + 拼接间隔 * (grid_size - 1)
            
            # 创建结果张量
            result = torch.zeros(min_batch, total_height, total_width, channels, device=device)
            
            # 放置每个视频
            for idx, video in enumerate(videos):
                row = idx // grid_size
                col = idx % grid_size
                h, w = video.shape[1], video.shape[2]
                
                y_pos = row * (cell_height + 拼接间隔) + (cell_height - h) // 2
                x_pos = col * (cell_width + 拼接间隔) + (cell_width - w) // 2
                
                result[:, y_pos:y_pos+h, x_pos:x_pos+w, :] = video
            
            print(f"[视频拼接] {grid_size}x{grid_size}九宫格, {len(videos)}个视频")
        
        elif 拼接方向 == "画中画":
            # 画中画模式：第一个视频作为背景，其他视频叠加
            result = videos[0].clone()
            base_h, base_w = result.shape[1], result.shape[2]
            
            # 叠加其他视频
            for i in range(1, len(videos)):
                video = videos[i]
                v_h, v_w = video.shape[1], video.shape[2]
                
                # 缩放到背景的1/4大小
                scale = 0.25
                new_h = int(v_h * scale)
                new_w = int(v_w * scale)
                
                # 使用插值缩放
                video_permuted = video.permute(0, 3, 1, 2)
                scaled = F.interpolate(video_permuted, size=(new_h, new_w), 
                                     mode='bilinear', align_corners=False)
                scaled = scaled.permute(0, 2, 3, 1)
                
                # 计算位置（右下角，依次向上）
                margin = 20
                y_pos = base_h - new_h - margin - (i-1) * (new_h + margin)
                x_pos = base_w - new_w - margin
                
                if y_pos >= 0:  # 确保不超出边界
                    result[:, y_pos:y_pos+new_h, x_pos:x_pos+new_w, :] = scaled
            
            print(f"[视频拼接] 画中画模式, {len(videos)}个视频")
        
        else:
            result = videos[0]
        
        return result
    
    def overlay_videos(self, base_result, videos, mask, 叠加方式, 
                      video2权重, video3权重, 多视频模式):
        """多视频叠加功能"""
        batch_size = base_result.shape[0]
        
        # 统一所有视频的尺寸和帧数
        target_h, target_w = base_result.shape[1], base_result.shape[2]
        
        # 处理video2
        if len(videos) > 1:
            video2 = videos[1]
            # 统一尺寸
            if video2.shape[1] != target_h or video2.shape[2] != target_w:
                video2_permuted = video2.permute(0, 3, 1, 2)
                video2_resized = F.interpolate(video2_permuted, size=(target_h, target_w),
                                             mode='bilinear', align_corners=False)
                video2 = video2_resized.permute(0, 2, 3, 1)
            
            # 统一帧数
            min_batch = min(batch_size, video2.shape[0])
            video2 = video2[:min_batch]
            base_result = base_result[:min_batch]
        
        # 处理video3
        video3 = None
        if len(videos) > 2:
            video3 = videos[2]
            # 统一尺寸
            if video3.shape[1] != target_h or video3.shape[2] != target_w:
                video3_permuted = video3.permute(0, 3, 1, 2)
                video3_resized = F.interpolate(video3_permuted, size=(target_h, target_w),
                                             mode='bilinear', align_corners=False)
                video3 = video3_resized.permute(0, 2, 3, 1)
            
            # 统一帧数
            min_batch = min(base_result.shape[0], video3.shape[0])
            video3 = video3[:min_batch]
            base_result = base_result[:min_batch]
            video2 = video2[:min_batch]
        
        result = base_result.clone()
        
        if 叠加方式 == "正常叠加":
            # 加权叠加
            if len(videos) == 2:
                # 双视频：video1 * (1-权重) + video2 * 权重
                result = base_result * (1 - video2权重) + video2 * video2权重
            elif len(videos) == 3:
                # 三视频：归一化权重
                w1 = 1 - video2权重 - video3权重
                w1 = max(0, w1)
                total = w1 + video2权重 + video3权重
                w1, w2, w3 = w1/total, video2权重/total, video3权重/total
                result = base_result * w1 + video2 * w2 + video3 * w3
            
            print(f"[视频叠加] 正常叠加, {len(videos)}个视频")
        
        elif 叠加方式 == "蒙版混合":
            # 使用蒙版控制混合
            # 这里可以重新计算蒙版或使用现有蒙版
            # 简化版：根据亮度创建混合蒙版
            if len(videos) == 2:
                # 基于video1亮度的蒙版
                brightness = 0.299 * base_result[..., 0] + 0.587 * base_result[..., 1] + 0.114 * base_result[..., 2]
                mask_weight = brightness.unsqueeze(-1).expand_as(base_result)
                result = base_result * mask_weight + video2 * (1 - mask_weight)
            elif len(videos) == 3:
                brightness = 0.299 * base_result[..., 0] + 0.587 * base_result[..., 1] + 0.114 * base_result[..., 2]
                mask1 = (brightness > 0.66).float().unsqueeze(-1).expand_as(base_result)
                mask2 = ((brightness > 0.33) & (brightness <= 0.66)).float().unsqueeze(-1).expand_as(base_result)
                mask3 = (brightness <= 0.33).float().unsqueeze(-1).expand_as(base_result)
                result = base_result * mask1 + video2 * mask2 + video3 * mask3
            
            print(f"[视频叠加] 蒙版混合, {len(videos)}个视频")
        
        elif 叠加方式 == "交替显示":
            # 按帧交替显示
            for i in range(result.shape[0]):
                if len(videos) == 2:
                    result[i] = base_result[i] if i % 2 == 0 else video2[i]
                elif len(videos) == 3:
                    idx = i % 3
                    if idx == 0:
                        result[i] = base_result[i]
                    elif idx == 1:
                        result[i] = video2[i]
                    else:
                        result[i] = video3[i]
            
            print(f"[视频叠加] 交替显示, {len(videos)}个视频")
        
        elif 叠加方式 == "渐变过渡":
            # 随时间渐变过渡
            total_frames = result.shape[0]
            for i in range(total_frames):
                t = i / max(total_frames - 1, 1)
                
                if len(videos) == 2:
                    # video1 → video2
                    result[i] = base_result[i] * (1 - t) + video2[i] * t
                elif len(videos) == 3:
                    # video1 → video2 → video3
                    if t < 0.5:
                        # 前半段：video1 → video2
                        t2 = t * 2
                        result[i] = base_result[i] * (1 - t2) + video2[i] * t2
                    else:
                        # 后半段：video2 → video3
                        t2 = (t - 0.5) * 2
                        result[i] = video2[i] * (1 - t2) + video3[i] * t2
            
            print(f"[视频叠加] 渐变过渡, {len(videos)}个视频")
        
        return result

