"""
视频信息解析器节点
从HAIGC_VIDEOINFO中提取各种视频参数
"""

class VideoInfoParserNode:
    """视频信息解析器节点"""
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "video_info": ("HAIGC_VIDEOINFO",),
            },
        }
    
    RETURN_TYPES = ("INT", "INT", "FLOAT", "INT", "FLOAT")
    RETURN_NAMES = ("宽度", "高度", "帧率", "帧数", "时长")
    FUNCTION = "parse_info"
    CATEGORY = "HAIGC工具集/视频剪辑"
    
    def parse_info(self, video_info):
        """解析视频信息"""
        
        width = video_info.get("width", 0)
        height = video_info.get("height", 0)
        fps = video_info.get("fps", 0.0)
        frames = video_info.get("frame_count", 0)
        duration = video_info.get("duration", 0.0)
        
        print(f"[视频信息解析器] 解析结果:")
        print(f"  宽度: {width}, 高度: {height}")
        print(f"  帧率: {fps} FPS")
        print(f"  帧数: {frames}")
        print(f"  时长: {duration}秒")
        
        return (width, height, fps, frames, duration)

