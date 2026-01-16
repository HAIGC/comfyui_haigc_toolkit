"""
视频剪辑节点集合
包含29个独立的视频处理节点
"""

# 视频输入输出节点
from .video_loader_node import VideoLoaderNode
from .video_writer_node import VideoWriterNode
from .video_batch_writer_node import VideoBatchWriterNode
from .video_info_parser_node import VideoInfoParserNode
from .video_info_preview_node import VideoInfoPreviewNode
from .video_preview_node import VideoPreviewNode

# 基础剪辑节点
from .video_trim_node import VideoTrimNode
from .video_speed_node import VideoSpeedNode
from .video_reverse_node import VideoReverseNode
from .video_crop_node import VideoCropNode
from .video_rotate_node import VideoRotateNode
from .video_flip_node import VideoFlipNode
from .video_resize_node import VideoResizeNode
from .video_fade_node import VideoFadeNode
from .video_loop_node import VideoLoopNode

# 高级剪辑节点
from .video_concat_node import VideoConcatNode
from .video_montage_node import VideoMontageNode
from .video_scene_detect_node import VideoSceneDetectNode
from .video_scene_splitter_node import VideoSceneSplitterNode
from .video_scene_av_split_node import VideoSceneAVSplitNode
from .video_seamless_loop_node import VideoSeamlessLoopNode

# 调色和滤镜节点


# 特效节点
from .video_beat_node import VideoBeatNode
from .video_pip_node import VideoPiPNode

# 动画和蒙版节点
from .video_keyframe_node import VideoKeyframeNode
from .video_mask_node import VideoMaskNode

# 节点类映射
VIDEO_EDITING_NODE_CLASS_MAPPINGS = {
    # 视频输入输出
    "HAIGC_VideoLoader": VideoLoaderNode,
    "HAIGC_VideoWriter": VideoWriterNode,
    "HAIGC_VideoBatchWriter": VideoBatchWriterNode,
    "HAIGC_VideoInfoParser": VideoInfoParserNode,
    "HAIGC_VideoInfoPreview": VideoInfoPreviewNode,
    "HAIGC_VideoPreview": VideoPreviewNode,
    
    # 基础剪辑
    "HAIGC_VideoTrim": VideoTrimNode,
    "HAIGC_VideoSpeed": VideoSpeedNode,
    "HAIGC_VideoReverse": VideoReverseNode,
    "HAIGC_VideoCrop": VideoCropNode,
    "HAIGC_VideoRotate": VideoRotateNode,
    "HAIGC_VideoFlip": VideoFlipNode,
    "HAIGC_VideoResize": VideoResizeNode,
    "HAIGC_VideoFade": VideoFadeNode,
    "HAIGC_VideoLoop": VideoLoopNode,
    
    # 高级剪辑
    "HAIGC_VideoConcat": VideoConcatNode,
    "HAIGC_VideoMontage": VideoMontageNode,
    "HAIGC_VideoSceneDetect": VideoSceneDetectNode,
    "HAIGC_VideoSceneSplitter": VideoSceneSplitterNode,
    "HAIGC_VideoSceneAVSplit": VideoSceneAVSplitNode,
    "HAIGC_VideoSeamlessLoop": VideoSeamlessLoopNode,
    
    # 调色和滤镜
    
    # 特效
    "HAIGC_VideoBeat": VideoBeatNode,
    "HAIGC_VideoPiP": VideoPiPNode,
    
    # 动画和蒙版
    "HAIGC_VideoKeyframe": VideoKeyframeNode,
    "HAIGC_VideoMask": VideoMaskNode,
}

# 节点显示名称映射
VIDEO_EDITING_NODE_DISPLAY_NAME_MAPPINGS = {
    # 视频输入输出
    "HAIGC_VideoLoader": "视频加载器 📂",
    "HAIGC_VideoWriter": "视频保存 💾",
    "HAIGC_VideoBatchWriter": "批量视频保存 💾",
    "HAIGC_VideoInfoParser": "视频信息解析器 🔍",
    "HAIGC_VideoInfoPreview": "视频信息预览 📝",
    "HAIGC_VideoPreview": "视频剪辑预览 🎬",
    
    # 基础剪辑
    "HAIGC_VideoTrim": "视频时间裁剪 ⏱️",
    "HAIGC_VideoSpeed": "视频变速 🎬",
    "HAIGC_VideoReverse": "视频倒放 🔄",
    "HAIGC_VideoCrop": "画面裁切 ✂️",
    "HAIGC_VideoRotate": "视频旋转 🔄",
    "HAIGC_VideoFlip": "视频翻转 🔀",
    "HAIGC_VideoResize": "视频缩放 📐",
    "HAIGC_VideoFade": "淡入淡出 🌅",
    "HAIGC_VideoLoop": "视频循环 🔁",
    
    # 高级剪辑
    "HAIGC_VideoConcat": "视频拼接 🎞️",
    "HAIGC_VideoMontage": "视频混剪 🎞️",
    "HAIGC_VideoSceneDetect": "分镜识别 🎯",
    "HAIGC_VideoSceneSplitter": "分镜转接 🎬",
    "HAIGC_VideoSceneAVSplit": "分镜音视频裁剪 🎧",
    "HAIGC_VideoSeamlessLoop": "无限循环 ♾️",
    
    # 调色和滤镜
    
    # 特效
    "HAIGC_VideoBeat": "卡点效果 💥",
    "HAIGC_VideoPiP": "画中画 📺",
    
    # 动画和蒙版
    "HAIGC_VideoKeyframe": "关键帧动画 🎬",
    "HAIGC_VideoMask": "蒙版功能 🎭",
}

__all__ = ['VIDEO_EDITING_NODE_CLASS_MAPPINGS', 'VIDEO_EDITING_NODE_DISPLAY_NAME_MAPPINGS']

