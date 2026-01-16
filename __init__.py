"""
HAIGC Toolkit - ComfyUI节点工具集
包含视频字幕、图片处理、视频处理等实用功能
"""

from .subtitle_node_enhanced import VideoSubtitleEnhancedNode
from .subtitle_timestamp_pro_node import VideoSubtitleTimestampProNode
from .image_accumulator_node import ImageAccumulatorNode
from .image_batch_duplicate_node import ImageBatchDuplicateNode
from .video_last_frame_node import VideoLastFrameNode
from .video_transition_node import VideoTransitionNode
from .timestamp_text_replace_node import TimestampTextReplaceNode

# 导入视频剪辑节点集合
from .video_editing import VIDEO_EDITING_NODE_CLASS_MAPPINGS, VIDEO_EDITING_NODE_DISPLAY_NAME_MAPPINGS

# 临时禁用文本替换节点进行测试
try:
    from .text_replace_pro_node import TextReplaceProNode
    text_replace_loaded = True
    print("[HAIGC] 文本替换节点加载成功")
except Exception as e:
    print(f"[HAIGC] 文本替换节点加载失败: {e}")
    TextReplaceProNode = None
    text_replace_loaded = False

from .version import __version__, print_version_info

# 打印版本信息
print_version_info()

# 节点类映射
NODE_CLASS_MAPPINGS = {
    "HAIGC_VideoSubtitleEnhanced": VideoSubtitleEnhancedNode,
    "HAIGC_VideoSubtitleTimestampPro": VideoSubtitleTimestampProNode,
    "HAIGC_ImageAccumulator": ImageAccumulatorNode,
    "HAIGC_ImageBatchDuplicate": ImageBatchDuplicateNode,
    "HAIGC_VideoLastFrame": VideoLastFrameNode,
    "HAIGC_VideoTransition": VideoTransitionNode,
    "HAIGC_TimestampTextReplace": TimestampTextReplaceNode,
}

# 添加视频剪辑节点
NODE_CLASS_MAPPINGS.update(VIDEO_EDITING_NODE_CLASS_MAPPINGS)

# 只在加载成功时添加文本替换节点
if text_replace_loaded and TextReplaceProNode is not None:
    NODE_CLASS_MAPPINGS["HAIGC_TextReplacePro"] = TextReplaceProNode

# 节点显示名称映射（中文）
NODE_DISPLAY_NAME_MAPPINGS = {
    "HAIGC_VideoSubtitleEnhanced": "视频字幕增强版(v2.6) 🎬",
    "HAIGC_VideoSubtitleTimestampPro": "视频字幕时间戳(专业版) ⚡",
    "HAIGC_ImageAccumulator": "图片批次累积 📦",
    "HAIGC_ImageBatchDuplicate": "图像批次复制 🔄",
    "HAIGC_VideoLastFrame": "获取视频尾帧 🎞️",
    "HAIGC_VideoTransition": "视频拼接过渡 🔗",
    "HAIGC_TimestampTextReplace": "时间戳文本替换(专业版) 📝",
}

# 添加视频剪辑节点显示名称
NODE_DISPLAY_NAME_MAPPINGS.update(VIDEO_EDITING_NODE_DISPLAY_NAME_MAPPINGS)

# 只在加载成功时添加文本替换节点的显示名称
if text_replace_loaded and TextReplaceProNode is not None:
    NODE_DISPLAY_NAME_MAPPINGS["HAIGC_TextReplacePro"] = "文本智能分段替换 🎯"

WEB_DIRECTORY = "./web"

__all__ = ['NODE_CLASS_MAPPINGS', 'NODE_DISPLAY_NAME_MAPPINGS', 'WEB_DIRECTORY']

