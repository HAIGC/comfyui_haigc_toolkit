import { app } from "../../../scripts/app.js";
import { api } from "../../../scripts/api.js";

const WIDGET_ID = "haigc_video_preview";

function ensurePreviewWidget(node) {
    if (node.__haigcVideoPreview) {
        return node.__haigcVideoPreview;
    }

    const container = document.createElement("div");
    container.className = "haigc-video-preview";
    container.style.marginTop = "8px";
    container.style.padding = "6px";
    container.style.border = "1px solid #3a3a3a";
    container.style.borderRadius = "6px";
    container.style.background = "rgba(0, 0, 0, 0.15)";
    container.style.display = "block"; // 与视频加载器节点一致，默认显示
    container.style.width = "100%";
    container.style.boxSizing = "border-box";
    container.style.marginLeft = "0";
    container.style.marginRight = "0";
    container.style.overflow = "hidden"; // 防止内容溢出
    container.style.wordWrap = "break-word"; // 允许长单词换行
    container.style.overflowWrap = "break-word"; // 现代浏览器的换行属性

    const videoEl = document.createElement("video");
    videoEl.controls = true;
    videoEl.loop = true;
    videoEl.style.width = "100%";
    videoEl.style.maxHeight = "220px"; // 初始值，会被 updateVideoSize 更新
    videoEl.style.height = "auto"; // 自动高度，根据视频比例
    videoEl.style.borderRadius = "4px";
    videoEl.style.background = "transparent"; // 透明背景
    videoEl.style.display = "block";
    videoEl.style.objectFit = "contain"; // 显示完整视频，不裁剪
    container.appendChild(videoEl);

    const caption = document.createElement("div");
    caption.style.marginTop = "4px";
    caption.style.fontSize = "12px"; // 固定字体大小，不随节点缩放
    caption.style.textAlign = "left"; // 左对齐，铺满整行
    caption.style.color = "#cccccc"; // 确保文字颜色可见
    caption.style.opacity = "0.8";
    caption.style.wordWrap = "break-word"; // 允许长单词换行
    caption.style.wordBreak = "break-word"; // 更温和的换行方式，优先在单词边界换行
    caption.style.overflowWrap = "break-word"; // 现代浏览器的换行属性
    caption.style.lineHeight = "1.4";
    caption.style.minHeight = "16px";
    caption.style.maxWidth = "100%";
    caption.style.whiteSpace = "pre-wrap"; // 保留换行符，允许自动换行
    caption.style.width = "100%";
    caption.style.boxSizing = "border-box";
    caption.style.display = "block"; // 确保默认显示
    caption.style.visibility = "visible";
    caption.style.overflow = "hidden"; // 防止文字溢出
    caption.style.flexShrink = "1"; // 允许在空间不足时收缩
    caption.style.flexGrow = "0"; // 防止信息窗口被拉伸
    container.appendChild(caption);

    const widget = node.addDOMWidget(WIDGET_ID, "video_preview", container);

    // 先创建预览对象
    const preview = {
        container,
        videoEl,
        caption,
        widget,
        currentUrl: null,
    };

    // 监听节点缩放，调整视频预览大小（信息窗口保持固定）
    const updateVideoSize = () => {
        const nodeEl = node.el || node;
        if (!nodeEl) return;
        
        const nodeWidth = nodeEl.offsetWidth || node.size?.[0] || 300;
        const baseMaxHeight = 220;
        
        // 根据节点宽度调整视频高度，允许更大的缩放范围
        // 缩放因子：节点宽度 / 基准宽度(300px)
        const scaleFactor = nodeWidth / 300;
        
        // 计算缩放后的高度，范围更宽：最小120px，最大可以到节点宽度的80%（适应竖屏视频）
        const maxAllowedHeight = Math.floor(nodeWidth * 0.8);
        const scaledMaxHeight = Math.max(120, Math.min(maxAllowedHeight, baseMaxHeight * scaleFactor));
        
        // 设置最大高度，保持视频完整显示（contain模式，不裁剪）
        preview.videoEl.style.maxHeight = `${scaledMaxHeight}px`;
        preview.videoEl.style.height = "auto"; // 自动高度，保持视频比例，完整显示
        
        // 信息窗口保持固定字体大小，不随节点缩放
        // 确保字体大小始终为12px，不被修改
        preview.caption.style.fontSize = "12px";
    };
    
    // 添加 updateVideoSize 方法到预览对象
    preview.updateVideoSize = updateVideoSize;
    
    // 使用 ResizeObserver 监听节点大小变化
    const resizeObserver = new ResizeObserver(() => {
        updateVideoSize();
    });
    
    // 延迟观察，确保节点已渲染
    setTimeout(() => {
        const nodeEl = node.el || node;
        if (nodeEl) {
            resizeObserver.observe(nodeEl);
        }
    }, 100);
    
    // 初始更新
    updateVideoSize();

    node.__haigcVideoPreview = preview;

    const onRemoved = node.onRemoved;
    node.onRemoved = () => {
        resizeObserver.disconnect();
        node.__haigcVideoPreview = null;
        return onRemoved?.();
    };

    return node.__haigcVideoPreview;
}

function formatDuration(seconds) {
    if (typeof seconds !== "number" || !isFinite(seconds)) {
        return "";
    }
    const mins = Math.floor(seconds / 60);
    const secs = Math.round(seconds % 60);
    if (mins <= 0) {
        return `${secs}s`;
    }
    return `${mins}m${secs.toString().padStart(2, "0")}s`;
}

function updatePreview(node, message) {
    if (!node || node.comfyClass !== "HAIGC_VideoWriter") {
        return;
    }
    const preview = ensurePreviewWidget(node);
    
    // ComfyUI 的消息格式：message.ui.videos
    const videos = message?.ui?.videos || message?.videos;
    
    // 调试日志
    if (!videos || !Array.isArray(videos) || videos.length === 0) {
        console.log("[HAIGC_VideoWriter] 预览更新：无视频数据", {
            hasMessage: !!message,
            hasUI: !!message?.ui,
            hasVideos: !!message?.videos,
            hasUIVideos: !!message?.ui?.videos,
            messageKeys: message ? Object.keys(message) : []
        });
        preview.container.style.display = "none";
        preview.caption.textContent = ""; // 清空信息，与视频加载器节点一致
        return;
    }

    const info = videos[0];
    const params = new URLSearchParams({
        filename: info.filename ?? "",
        subfolder: info.subfolder ?? "",
        type: info.type ?? "output",
    });
    const url = api.apiURL(`/view?${params.toString()}`);
    if (preview.currentUrl !== url) {
        preview.videoEl.src = url;
        preview.currentUrl = url;
    }

    // 格式化格式文本（大写），与视频加载器节点一致
    const formatText = info.format ? info.format.toUpperCase() : (info.format_label ? info.format_label : "");
    const fpsText = info.fps ? `${info.fps}fps` : "";
    const durationText = formatDuration(info.duration);
    const sizeText = typeof info.file_size_mb === "number" ? `${info.file_size_mb.toFixed(2)}MB` : "";
    const resolutionText = info.width && info.height ? `${info.width}x${info.height}` : "";
    const frameCountText = info.frame_count ? `总帧数：${info.frame_count}帧` : "";
    
    // 构建比特率文本，与视频加载器节点一致（只显示有值的比特率）
    const bitrateParts = [];
    if (info.video_bitrate_kbps && info.video_bitrate_kbps > 0) {
        bitrateParts.push(`${info.video_bitrate_kbps}Kbps`);
    }
    if (info.audio_bitrate_kbps && info.audio_bitrate_kbps > 0) {
        bitrateParts.push(`音频${info.audio_bitrate_kbps}Kbps`);
    }
    const bitrateText = bitrateParts.length > 0 
        ? `比特率：${bitrateParts.join(" / ")}` 
        : "";
    
    const filename = info.filename || "视频";

    // 构建信息文本，使用换行符分隔不同类别的信息
    // 第一行：文件名
    // 第二行：格式、FPS、时长
    // 第三行：分辨率、文件大小、总帧数
    // 第四行：比特率信息
    const lines = [];
    
    // 第一行：文件名
    lines.push(filename);
    
    // 第二行：格式、FPS、时长
    const line2 = [formatText, fpsText, durationText].filter(Boolean);
    if (line2.length > 0) {
        lines.push(line2.join(" · "));
    }
    
    // 第三行：分辨率、文件大小、总帧数
    const line3 = [resolutionText, sizeText, frameCountText].filter(Boolean);
    if (line3.length > 0) {
        lines.push(line3.join(" · "));
    }
    
    // 第四行：比特率信息
    if (bitrateText) {
        lines.push(bitrateText);
    }
    
    const infoText = lines.join("\n");
    
    // 确保信息文本不为空时才显示，与视频加载器节点一致
    if (infoText && infoText.trim().length > 0) {
        preview.caption.textContent = infoText;
        preview.caption.style.display = "block";
        preview.caption.style.visibility = "visible";
        preview.caption.style.opacity = "0.8";
    } else {
        preview.caption.textContent = "";
        preview.caption.style.display = "none";
    }
    
    // 触发尺寸更新
    if (node.__haigcVideoPreview && node.__haigcVideoPreview.updateVideoSize) {
        node.__haigcVideoPreview.updateVideoSize();
    }

    // 确保容器可见，与视频加载器节点一致
    preview.container.style.display = "block";
    preview.container.style.visibility = "visible";
    node.setDirtyCanvas(true);
    
    console.log("[HAIGC_VideoWriter] 预览更新成功", {
        filename: info.filename,
        url: url,
        hasVideo: !!preview.videoEl.src
    });
}

app.registerExtension({
    name: "haigc.VideoPreview",
    nodeCreated(node) {
        if (node.comfyClass === "HAIGC_VideoWriter") {
            ensurePreviewWidget(node);
            
            // 监听节点的 UI 更新
            const originalOnResize = node.onResize;
            node.onResize = function() {
                const result = originalOnResize?.apply(this, arguments);
                // 尝试从节点的执行结果中获取 UI 数据
                if (this.lastExecutionResult) {
                    setTimeout(() => {
                        updatePreview(this, this.lastExecutionResult);
                    }, 50);
                }
                return result;
            };
        }
    },
    beforeRegisterNodeDef(nodeType, nodeData) {
        if (nodeData.name !== "HAIGC_VideoWriter") {
            return;
        }
        const originalExecuted = nodeType.prototype.onExecuted;
        nodeType.prototype.onExecuted = function (message) {
            const result = originalExecuted?.apply(this, arguments);
            
            // 保存执行结果
            this.lastExecutionResult = message;
            
            // 立即尝试更新预览
            updatePreview(this, message);
            
            // 延迟再次尝试，确保 UI 数据已完全更新
            setTimeout(() => {
                updatePreview(this, message);
            }, 200);
            
            return result;
        };
    },
});

