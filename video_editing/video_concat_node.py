
import os
import shutil
import subprocess
import torch
import numpy as np
import sys
from pathlib import Path
import folder_paths

# 尝试导入 OpenCV
try:
    import cv2
except ImportError:
    cv2 = None

class VideoConcatNode:
    """
    多段视频拼接节点
    支持最多10段视频拼接，自动处理分辨率和帧率，智能补全音频
    """
    
    @classmethod
    def INPUT_TYPES(cls):
        # 定义10个视频输入
        inputs = {
            "required": {
                "video_1": ("HAIGC_VIDEOINFO",),  # 至少需要一个视频
                "目标宽度": ("INT", {
                    "default": 0,
                    "min": 0,
                    "max": 4096,
                    "step": 1,
                    "tooltip": "0 表示使用第一段视频的宽度"
                }),
                "目标高度": ("INT", {
                    "default": 0,
                    "min": 0,
                    "max": 4096,
                    "step": 1,
                    "tooltip": "0 表示使用第一段视频的高度"
                }),
                "目标帧率": ("FLOAT", {
                    "default": 0.0,
                    "min": 0.0,
                    "max": 120.0,
                    "step": 0.1,
                    "tooltip": "0 表示自动选择最高帧率"
                }),
                "缩放模式": (["contain", "cover", "stretch"], {
                    "default": "contain",
                    "tooltip": "contain: 保持比例黑边填充; cover: 保持比例裁剪; stretch: 拉伸"
                }),
            },
            "optional": {}
        }
        
        # 添加 video_2 到 video_10
        for i in range(2, 11):
            inputs["optional"][f"video_{i}"] = ("HAIGC_VIDEOINFO",)
            
        return inputs

    RETURN_TYPES = ("IMAGE", "AUDIO", "HAIGC_VIDEOINFO")
    RETURN_NAMES = ("拼接图像", "拼接音频", "video_info")
    FUNCTION = "concatenate_videos"
    CATEGORY = "HAIGC工具集/视频剪辑"

    def concatenate_videos(self, 
                         video_1, 
                         目标宽度, 
                         目标高度, 
                         目标帧率, 
                         缩放模式,
                         **kwargs):
        
        # 1. 收集有效视频输入
        # video_1 可能是 None (如果上游节点出错或未连接正确)
        video_inputs = [video_1]
        for i in range(2, 11):
            key = f"video_{i}"
            # 确保 kwargs 中存在该键且不为 None
            if key in kwargs:
                val = kwargs[key]
                if val is not None:
                    video_inputs.append(val)
        
        valid_videos = []
        for idx, v in enumerate(video_inputs):
            # 详细检查 v 是否为有效字典
            if v is None:
                print(f"[视频拼接] 警告: 输入视频 {idx+1} 为 None，已跳过")
                continue
                
            if not isinstance(v, dict):
                print(f"[视频拼接] 警告: 输入视频 {idx+1} 格式错误 (期望 dict, 实际 {type(v)})，已跳过")
                continue
                
            if "source_path" not in v:
                print(f"[视频拼接] 警告: 输入视频 {idx+1} 缺少 source_path，已跳过")
                continue
                
            if not os.path.exists(v["source_path"]):
                print(f"[视频拼接] 警告: 输入视频 {idx+1} 文件不存在: {v['source_path']}，已跳过")
                continue
                
            valid_videos.append(v)
                
        if not valid_videos:
            raise ValueError("没有有效的视频输入 (所有输入均无效或为空)")

        # 2. 确定目标参数
        # 如果未指定尺寸，使用第一个视频的尺寸
        target_w = 目标宽度 if 目标宽度 > 0 else valid_videos[0].get("width", 1920)
        target_h = 目标高度 if 目标高度 > 0 else valid_videos[0].get("height", 1080)
        
        # 确保尺寸是2的倍数 (yuv420p要求)
        target_w = (target_w // 2) * 2
        target_h = (target_h // 2) * 2
        
        # 如果未指定帧率，使用所有视频中的最大帧率
        if 目标帧率 <= 0:
            target_fps = max([float(v.get("fps", 30.0)) for v in valid_videos])
            target_fps = max(target_fps, 1.0) # 确保最小为1
        else:
            target_fps = 目标帧率

        print(f"[视频拼接] 目标参数: {target_w}x{target_h} @ {target_fps}fps")

        # 3. 构建 FFmpeg 滤镜图
        output_dir = folder_paths.get_output_directory()
        output_filename = f"concat_{os.urandom(4).hex()}.mp4"
        output_path = os.path.join(output_dir, output_filename)
        
        # 直接抛出异常而不是返回空帧，以便用户能看到报错
        self._run_ffmpeg_concat(
            valid_videos, 
            output_path, 
            target_w, 
            target_h, 
            target_fps, 
            缩放模式
        )

        # 4. 加载结果供后续节点使用
        return self._load_video_result(output_path)

    def _run_ffmpeg_concat(self, videos, output_path, width, height, fps, scale_mode):
        ffmpeg_path = shutil.which("ffmpeg")
        if not ffmpeg_path:
            raise RuntimeError("未找到 ffmpeg，请先安装 ffmpeg")

        filter_complex = []
        inputs = []
        
        print(f"[视频拼接] 开始构建命令，共 {len(videos)} 个视频片段")
        
        for i, video in enumerate(videos):
            path = video["source_path"]
            inputs.extend(["-i", path])
            
            # 视频处理滤镜
            # 1. 缩放
            if scale_mode == "contain":
                # 保持比例缩放，加黑边
                scale_filter = f"scale={width}:{height}:force_original_aspect_ratio=decrease,pad={width}:{height}:(ow-iw)/2:(oh-ih)/2"
            elif scale_mode == "cover":
                # 保持比例缩放，裁剪
                scale_filter = f"scale={width}:{height}:force_original_aspect_ratio=increase,crop={width}:{height}"
            else: # stretch
                scale_filter = f"scale={width}:{height}"
            
            # 检查是否有裁剪信息 (支持 VideoLoader 的 start_frame/end_frame 逻辑)
            # 注意：目前 VideoLoader 还没把这些放入 info，后续如果加上，这里可以直接支持
            trim_filter = ""
            # if "start_frame" in video: ... (暂时不实现，避免复杂度，先保证基础拼接可用)
                
            # 2. 统一帧率和SAR
            v_filter = f"[{i}:v]{scale_filter},fps={fps},setsar=1[v{i}]"
            filter_complex.append(v_filter)
            
            # 音频处理滤镜
            has_audio = self._check_audio_track(path)
            if has_audio:
                # 统一音频格式
                a_filter = f"[{i}:a]aformat=sample_rates=44100:channel_layouts=stereo[a{i}]"
                filter_complex.append(a_filter)
            else:
                # 生成静音
                # 关键修复：确保静音时长与视频完全一致
                v_frames = video.get("frame_count", 0)
                v_fps = video.get("fps", 0)
                
                if v_frames > 0 and v_fps > 0:
                    duration = v_frames / v_fps
                else:
                    duration = video.get("duration", 5.0)
                
                if duration <= 0: duration = 5.0
                
                # 增加一点点缓冲时长(0.1s)防止音频比视频短导致丢帧
                duration_cmd = f"{duration + 0.1:.4f}"
                
                # 使用 aformat 确保静音格式也匹配
                a_filter = f"anullsrc=r=44100:cl=stereo,atrim=duration={duration_cmd},aformat=sample_rates=44100:channel_layouts=stereo[a{i}]"
                filter_complex.append(a_filter)

        # 拼接滤镜
        # 关键修复：concat 滤镜要求输入顺序为 [v0][a0][v1][a1]... (即成对出现)
        concat_inputs = []
        for i in range(len(videos)):
            concat_inputs.append(f"[v{i}]")
            concat_inputs.append(f"[a{i}]")
        
        concat_str = "".join(concat_inputs)
        
        # 关键修复：unsafe=1 允许拼接不同格式的片段
        concat_filter = f"{concat_str}concat=n={len(videos)}:v=1:a=1:unsafe=1[outv][outa]"
        filter_complex.append(concat_filter)
        
        cmd = [
            ffmpeg_path,
            "-y",
        ] + inputs + [
            "-filter_complex", ";".join(filter_complex),
            "-map", "[outv]",
            "-map", "[outa]",
            "-c:v", "libx264",
            "-pix_fmt", "yuv420p",    # 指定像素格式
            "-movflags", "+faststart", # 优化 Web 播放
            "-preset", "ultrafast",
            "-crf", "23",
            "-c:a", "aac",
            "-b:a", "192k",
            output_path
        ]
        
        print(f"[视频拼接] 执行FFmpeg命令:\n{' '.join(cmd)}")
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode != 0:
            print(f"[视频拼接] FFmpeg错误输出:\n{result.stderr}")
            # 抛出异常，让 ComfyUI 显示错误
            raise RuntimeError(f"FFmpeg执行失败: {result.stderr[-500:]}")
        else:
            print(f"[视频拼接] 拼接成功: {output_path}")

    def _check_audio_track(self, video_path):
        try:
            ffprobe_path = shutil.which("ffprobe")
            if not ffprobe_path: return False
            
            cmd = [
                ffprobe_path, "-v", "error",
                "-select_streams", "a:0",
                "-show_entries", "stream=codec_type",
                "-of", "default=noprint_wrappers=1:nokey=1",
                str(video_path)
            ]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=5)
            return result.returncode == 0 and result.stdout.strip() == "audio"
        except:
            return False

    def _load_video_result(self, video_path):
        # 复用 VideoLoader 的部分逻辑来加载结果
        if cv2 is None:
            raise ImportError("需要 opencv-python")
            
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            raise Exception("无法打开生成的视频文件")
            
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        fps = cap.get(cv2.CAP_PROP_FPS)
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        
        frames = []
        # 限制最大加载帧数以防内存爆炸，例如最多加载300帧用于预览？
        # 但用户可能需要完整视频。这里我们全量加载，但打印警告。
        # 或者：如果超过一定大小，只加载部分？
        # 遵循"ComfyUI"习惯，通常是全量加载。
        
        print(f"[视频拼接] 正在加载结果视频到内存 (共{total_frames}帧)...")
        
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frame = frame.astype(np.float32) / 255.0
            frames.append(frame)
            
        cap.release()
        
        if not frames:
            raise Exception("未读取到帧")
            
        images = torch.from_numpy(np.stack(frames, axis=0))
        
        # 提取音频
        import shutil
        ffmpeg_path = shutil.which("ffmpeg")
        temp_audio = os.path.join(os.path.dirname(video_path), f"temp_audio_{os.urandom(4).hex()}.wav")
        if ffmpeg_path:
            subprocess.run([
                ffmpeg_path, "-y", "-i", video_path, 
                "-vn", "-acodec", "pcm_s16le", "-ar", "44100", "-ac", "2",
                temp_audio
            ], capture_output=True)
        if os.path.exists(temp_audio):
            try:
                import torchaudio
                waveform, sample_rate = torchaudio.load(temp_audio)
            except ImportError:
                import wave
                with wave.open(temp_audio, 'rb') as wf:
                    sample_rate = wf.getframerate()
                    channels = wf.getnchannels()
                    sampwidth = wf.getsampwidth()
                    frames = wf.getnframes()
                    audio_bytes = wf.readframes(frames)
                import numpy as np
                dtype = np.int16 if sampwidth == 2 else np.int8
                audio_np = np.frombuffer(audio_bytes, dtype=dtype)
                if channels > 1:
                    audio_np = audio_np.reshape(-1, channels).T
                else:
                    audio_np = audio_np.reshape(1, -1)
                audio_np = (audio_np.astype(np.float32) / 32768.0)
                import torch as _torch
                waveform = _torch.from_numpy(audio_np).unsqueeze(0)
            finally:
                try:
                    os.remove(temp_audio)
                except OSError:
                    pass
            if waveform.dim() == 2:
                waveform = waveform.unsqueeze(0)
            elif waveform.dim() == 1:
                waveform = waveform.view(1, 1, -1)
            if waveform.shape[1] == 1:
                waveform = waveform.repeat(1, 2, 1)
            audio_data = {"waveform": waveform, "sample_rate": int(sample_rate or 44100)}
        else:
            audio_data = {"waveform": torch.zeros((1, 2, 0)), "sample_rate": 44100}
            
        info = {
            "width": width,
            "height": height,
            "fps": fps,
            "frame_count": total_frames,
            "duration": total_frames / fps if fps > 0 else 0,
            "source_path": video_path,
            "filename": os.path.basename(video_path)
        }
        
        return (images, audio_data, info)
