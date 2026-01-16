import { app } from "../../../scripts/app.js";
import { api } from "../../../scripts/api.js";

const WIDGET_ID = "haigc_video_preview_enhanced";

function formatDuration(seconds) {
    if (typeof seconds !== "number" || !isFinite(seconds)) {
        return "";
    }
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    const ms = Math.round((seconds % 1) * 100); // 百分位毫秒
    
    const msStr = ms.toString().padStart(2, "0");
    
    if (mins <= 0) {
        return `${secs}.${msStr}s`;
    }
    return `${mins}m${secs.toString().padStart(2, "0")}.${msStr}s`;
}

function createVideoSection(title, onSetFrame) {
    const container = document.createElement("div");
    container.className = "haigc-video-section"; // 添加类名以便应用样式
    container.style.position = "relative";
    // container.style.marginBottom = "8px"; // 移除下边距，改用 flex gap 控制
    container.style.padding = "6px";
    container.style.border = "1px solid #3a3a3a";
    container.style.borderRadius = "6px";
    container.style.background = "rgba(0, 0, 0, 0.2)";
    container.style.flex = "1"; // 允许伸缩
    
    // 移除原有的标题部分
    // if (title) {
    //     const header = document.createElement("div");
    //     header.textContent = title;
    //     // ...
    //     container.appendChild(header);
    // }

    const videoWrapper = document.createElement("div");
    videoWrapper.className = "haigc-video-wrapper"; // 使用 CSS 类
    // 移除内联样式，改用 CSS 类控制
    // videoWrapper.style.position = "relative";
    // videoWrapper.style.width = "100%";
    // videoWrapper.style.flex = "1"; 
    // videoWrapper.style.display = "flex";
    // videoWrapper.style.alignItems = "center";
    // videoWrapper.style.justifyContent = "center";
    // videoWrapper.style.overflow = "hidden";
    container.appendChild(videoWrapper);

    const videoEl = document.createElement("video");
    videoEl.controls = true;
    videoEl.loop = true;
    videoEl.style.width = "100%";
    videoEl.style.height = "auto"; // 改为 auto，让视频按比例显示
    videoEl.style.maxHeight = "none"; // 移除最大高度限制，允许无限放大
    videoEl.style.borderRadius = "4px";
    videoEl.style.background = "transparent";
    videoEl.style.display = "block";
    videoEl.style.objectFit = "contain";
    videoWrapper.appendChild(videoEl);

    const frameCounter = document.createElement("div");
    // 改为相对于 haigc-video-section 绝对定位，而不是 haigc-video-wrapper
    frameCounter.style.position = "absolute";
    frameCounter.style.top = "0"; // 顶部对齐
    frameCounter.style.left = "0"; // 左侧对齐
    frameCounter.style.width = "100%"; // 占满宽度
    frameCounter.style.padding = "2px 4px";
    frameCounter.style.background = "rgba(0, 0, 0, 0.0)"; // 透明背景
    frameCounter.style.color = "#aaa"; // 浅灰色文字
    frameCounter.style.fontSize = "11px";
    frameCounter.style.pointerEvents = "none";
    frameCounter.style.zIndex = "10";
    frameCounter.textContent = title;
    
    // 将 frameCounter 添加到 container 而不是 videoWrapper
    // 这样它就会显示在视频上方，不遮挡视频内容
    container.insertBefore(frameCounter, videoWrapper);

    if (onSetFrame) {
        const btnContainer = document.createElement("div");
        btnContainer.style.marginTop = "6px";
        btnContainer.style.display = "flex";
        btnContainer.style.justifyContent = "flex-end";
        container.appendChild(btnContainer);

        const btn = document.createElement("button");
        btn.textContent = title === "起始帧预览" ? "📌 设为起始帧" : "🏁 设为结束帧";
        btn.style.fontSize = "11px";
        btn.style.padding = "4px 8px";
        btn.style.cursor = "pointer";
        btn.style.backgroundColor = "#444";
        btn.style.color = "#fff";
        btn.style.border = "none";
        btn.style.borderRadius = "4px";
        
        btn.onmouseover = () => btn.style.backgroundColor = "#555";
        btn.onmouseout = () => btn.style.backgroundColor = "#444";
        
        btn.onclick = () => {
            onSetFrame(videoEl.currentTime);
        };
        btnContainer.appendChild(btn);
    }

    return { container, videoEl, frameCounter };
}

function ensurePreviewWidget(node) {
    if (node.__haigcVideoPreviewEnhanced) {
        return node.__haigcVideoPreviewEnhanced;
    }

    const mainContainer = document.createElement("div");
    mainContainer.className = "haigc-video-preview-enhanced";
    mainContainer.dataset.haigcPreview = "true";
    mainContainer.style.width = "100%";
    mainContainer.style.boxSizing = "border-box";
    // 允许主容器调整大小
    mainContainer.style.resize = "vertical"; 
    mainContainer.style.overflow = "hidden";
    mainContainer.style.minHeight = "300px"; // 设置一个合理的最小高度
    
    const style = document.createElement("style");
    style.textContent = `
        .haigc-video-preview-enhanced {
            display: flex;
            flex-direction: column;
            gap: 8px;
            width: 100% !important;
            height: 100% !important; /* 关键修改：确保父容器不超高 */
            min-height: 0;
            overflow: hidden; /* 防止内容溢出父容器 */
            padding-bottom: 10px; /* 增加底部padding防止内容贴边 */
        }
        .haigc-video-row {
            display: flex;
            flex-direction: row;
            flex: 1;
            gap: 8px;
            min-height: 0;
            width: 100%;
            overflow: hidden; /* 防止水平溢出 */
        }
        .haigc-video-preview-enhanced video {
            width: 100% !important;
            height: 100% !important; 
            max-height: none !important;
            object-fit: contain !important;
        }
        .haigc-video-section {
            display: flex;
            flex-direction: column;
            flex: 1;
            min-width: 0;
            overflow: hidden;
            box-sizing: border-box;
            height: 100%;
            padding-top: 20px !important; /* 为标题留出空间 */
        }
        .haigc-video-wrapper {
            position: relative;
            width: 100%;
            flex: 1;
            display: flex;
            align-items: center;
            justify-content: center;
            overflow: hidden;
            min-height: 0;
            background: rgba(0, 0, 0, 0.3);
            border-radius: 4px;
        }
        .haigc-info-caption {
             font-size: 12px;
             text-align: left;
             color: #cccccc;
             opacity: 0.8;
             word-wrap: break-word;
             word-break: break-all;
             line-height: 1.4;
             white-space: pre-wrap;
             flex-shrink: 0;
             max-height: 100px;
             overflow-y: auto;
             margin-bottom: 4px; /* 稍微增加与视频的间距 */
        }
    `;
    mainContainer.appendChild(style);

    // 1. 视频信息 (置顶)
    const caption = document.createElement("div");
    caption.className = "haigc-info-caption"; 
    mainContainer.appendChild(caption);

    // 2. 视频容器行 (左右布局)
    const videoRow = document.createElement("div");
    videoRow.className = "haigc-video-row";
    mainContainer.appendChild(videoRow);

    // Start Frame Section - 包裹在可调整大小的容器中
    const startSection = createVideoSection("起始帧预览", (time) => {
        if (!preview.fps) return;
        const frame = Math.floor(time * preview.fps);
        
        const widget = node.widgets?.find(w => w.name === "起始帧");
        if (widget) {
            widget.value = frame;
            // Optionally trigger a callback or node update if needed
            if (widget.callback) widget.callback(frame);
            app.graph.setDirtyCanvas(true);
        }
    });
    videoRow.appendChild(startSection.container);

    // End Frame Section
    const endSection = createVideoSection("结束帧预览", (time) => {
        if (!preview.fps) return;
        const frame = Math.floor(time * preview.fps);
        
        const widget = node.widgets?.find(w => w.name === "结束帧");
        if (widget) {
            widget.value = frame;
            if (widget.callback) widget.callback(frame);
            app.graph.setDirtyCanvas(true);
        }
    });
    videoRow.appendChild(endSection.container);

    const widget = node.addDOMWidget(WIDGET_ID, "video_preview", mainContainer);

    const preview = {
        container: mainContainer,
        startVideo: startSection.videoEl,
        endVideo: endSection.videoEl,
        startCounter: startSection.frameCounter,
        endCounter: endSection.frameCounter,
        caption,
        widget,
        currentUrl: null,
        fps: 0
    };

    // Update logic for counters
    const setupCounter = (video, counter, title) => {
        const update = () => {
            if (preview.fps) {
                const frame = Math.floor(video.currentTime * preview.fps);
                // 修改显示内容：标题 + 当前帧 + 时间
                counter.textContent = `${title}: ${frame} (${formatDuration(video.currentTime)})`; 
                counter.style.display = "block";
            } else {
                // 如果没有fps信息，至少显示标题
                counter.textContent = title;
                counter.style.display = "block";
            }
        };
        video.addEventListener("timeupdate", update);
        video.addEventListener("loadedmetadata", update);
    };

    setupCounter(startSection.videoEl, startSection.frameCounter, "起始帧预览");
    setupCounter(endSection.videoEl, endSection.frameCounter, "结束帧预览");

    const updateVideoSize = () => {
        if (preview.caption) {
            preview.caption.style.fontSize = "12px";
        }
    };
    
    preview.updateVideoSize = updateVideoSize;
    
    // Native preview hiding logic
    const hideNativePreview = () => {
        const nodeEl = node.el || node;
        if (!nodeEl) return;
        
        const elementsToHide = nodeEl.querySelectorAll('video, img, canvas, .preview, [class*="preview"]');
        elementsToHide.forEach(el => {
            if (el === mainContainer || mainContainer.contains(el)) return;
            
            if (el.style.display !== "none") {
                el.style.setProperty("display", "none", "important");
                el.style.setProperty("height", "0", "important");
                el.style.setProperty("min-height", "0", "important");
                el.style.setProperty("margin", "0", "important");
                el.style.setProperty("padding", "0", "important");
            }
        });
    };
    
    const resizeObserver = new ResizeObserver(() => {
        updateVideoSize();
    });

    const mutationObserver = new MutationObserver(() => {
        hideNativePreview();
    });
    
    setTimeout(() => {
        const nodeEl = node.el || node;
        if (nodeEl) {
            resizeObserver.observe(nodeEl);
            mutationObserver.observe(nodeEl, { childList: true, subtree: true });
            hideNativePreview();
        }
    }, 100);
    
    updateVideoSize();

    node.__haigcVideoPreviewEnhanced = preview;

    const onRemoved = node.onRemoved;
    node.onRemoved = () => {
        resizeObserver.disconnect();
        mutationObserver.disconnect();
        node.__haigcVideoPreviewEnhanced = null;
        return onRemoved?.();
    };

    return node.__haigcVideoPreviewEnhanced;
}

function updatePreview(node, message) {
    if (!node || node.comfyClass !== "HAIGC_VideoPreview") {
        return;
    }
    const preview = ensurePreviewWidget(node);
    
    const videos = message?.ui?.videos || message?.videos;
    
    if (!videos || !Array.isArray(videos) || videos.length === 0) {
        preview.container.style.display = "none";
        preview.caption.textContent = "";
        return;
    }

    const info = videos[0];
    
    const params = new URLSearchParams({
        filename: info.filename ?? "",
        subfolder: info.subfolder ?? "",
        type: info.type ?? "input",
    });
    const url = api.apiURL(`/view?${params.toString()}`);
    
    if (preview.currentUrl !== url) {
        preview.startVideo.src = url;
        preview.endVideo.src = url;
        preview.currentUrl = url;
    }
    
    if (info.fps) {
        preview.fps = info.fps;
    }

    const formatText = info.format ? info.format.toUpperCase() : "";
    const fpsText = info.fps ? `${info.fps}fps` : "";
    const durationText = formatDuration(info.duration);
    const sizeText = typeof info.file_size_mb === "number" ? `${info.file_size_mb.toFixed(2)}MB` : "";
    const resolutionText = info.width && info.height ? `${info.width}x${info.height}` : "";
    const frameCountText = info.frame_count ? `总帧数：${info.frame_count}帧` : "";
    
    const bitrateParts = [];
    // 强制转换为数字并检查
    const videoBitrate = Number(info.video_bitrate_kbps);
    const audioBitrate = Number(info.audio_bitrate_kbps);

    if (!isNaN(videoBitrate) && videoBitrate > 0) {
        bitrateParts.push(`视频${videoBitrate}Kbps`);
    }
    if (!isNaN(audioBitrate) && audioBitrate > 0) {
        bitrateParts.push(`音频${audioBitrate}Kbps`);
    }
    
    // 调试日志
    // console.log("Video Info:", info);
    // console.log("Bitrate Parts:", bitrateParts);

    const bitrateText = bitrateParts.length > 0 
        ? `比特率：${bitrateParts.join(" / ")}` 
        : "";
    
    const filename = info.filename || "视频";

    const lines = [];
    lines.push(filename);
    
    const line2 = [formatText, fpsText, durationText].filter(Boolean);
    if (line2.length > 0) {
        lines.push(line2.join(" · "));
    }
    
    const line3 = [resolutionText, sizeText, frameCountText].filter(Boolean);
    if (line3.length > 0) {
        lines.push(line3.join(" · "));
    }
    
    if (bitrateText) {
        lines.push(bitrateText);
    }
    
    const infoText = lines.join("\n");
    
    if (infoText && infoText.trim().length > 0) {
        preview.caption.textContent = infoText;
        preview.caption.style.display = "block";
        preview.caption.style.visibility = "visible";
        preview.caption.style.opacity = "0.8";
    } else {
        preview.caption.textContent = "";
        preview.caption.style.display = "none";
    }
    
    if (preview.updateVideoSize) {
        preview.updateVideoSize();
    }

    preview.container.style.display = "block";
    preview.container.style.visibility = "visible";
    
    node.setDirtyCanvas(true);
}

app.registerExtension({
    name: "haigc.VideoPreviewEnhanced",
    nodeCreated(node) {
        if (node.comfyClass === "HAIGC_VideoPreview") {
            // 设置最小尺寸限制
            const MIN_WIDTH = 450;
            const MIN_HEIGHT = 500;

            node.minWidth = MIN_WIDTH;
            node.minHeight = MIN_HEIGHT;
            
            // 如果当前尺寸小于最小尺寸，则调整
            if (node.size[0] < MIN_WIDTH) node.size[0] = MIN_WIDTH;
            if (node.size[1] < MIN_HEIGHT) node.size[1] = MIN_HEIGHT;

            ensurePreviewWidget(node);
            
            const originalOnResize = node.onResize;
            node.onResize = function() {
                 // 确保最小尺寸
                 if (this.size[0] < MIN_WIDTH) this.size[0] = MIN_WIDTH;
                 if (this.size[1] < MIN_HEIGHT) this.size[1] = MIN_HEIGHT;
                 return originalOnResize?.apply(this, arguments);
            };
        }
    },
    beforeRegisterNodeDef(nodeType, nodeData) {
        if (nodeData.name !== "HAIGC_VideoPreview") {
            return;
        }
        const originalExecuted = nodeType.prototype.onExecuted;
        nodeType.prototype.onExecuted = function (message) {
            // 拦截并移除 message.ui.videos
            let videoData = null;
            
            if (message && message.ui && message.ui.videos) {
                videoData = [...message.ui.videos];
                delete message.ui.videos;
            }
            
            if (message && message.videos) {
                if (!videoData) videoData = [...message.videos];
                delete message.videos;
            }
            
            const result = originalExecuted?.apply(this, arguments);
            
            if (videoData) {
                const tempMessage = {
                    ui: { videos: videoData },
                    videos: videoData
                };
                
                this.lastExecutionResult = tempMessage;
                updatePreview(this, tempMessage);
                
                setTimeout(() => {
                    updatePreview(this, tempMessage);
                }, 200);
            }
            
            return result;
        };
    },
});
