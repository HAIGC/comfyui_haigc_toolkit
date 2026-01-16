import { app } from "../../../scripts/app.js";
import { api } from "../../../scripts/api.js";

const WIDGET_ID = "haigc_info_preview";

function baseName(p) {
    try {
        if (!p || typeof p !== "string") return "";
        const parts = p.split(/[\\/]/);
        return parts[parts.length - 1] || "";
    } catch {
        return "";
    }
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

function ensurePreviewWidget(node) {
    if (node.__haigcInfoPreview) {
        return node.__haigcInfoPreview;
    }

    const container = document.createElement("div");
    container.className = "haigc-info-preview";
    container.style.marginTop = "8px";
    container.style.padding = "6px";
    container.style.border = "1px solid #3a3a3a";
    container.style.borderRadius = "6px";
    container.style.background = "rgba(0, 0, 0, 0.15)";
    container.style.display = "block";
    container.style.width = "100%";
    container.style.boxSizing = "border-box";
    
    // 移除视频预览元素
    // const videoEl = document.createElement("video");
    // ...

    const caption = document.createElement("div");
    caption.style.fontSize = "12px";
    caption.style.textAlign = "left";
    caption.style.color = "#cccccc";
    caption.style.lineHeight = "1.5";
    caption.style.whiteSpace = "pre-wrap";
    caption.style.wordBreak = "break-all";
    container.appendChild(caption);

    const widget = node.addDOMWidget(WIDGET_ID, "info_preview", container);

    const preview = {
        container,
        // videoEl,
        caption,
        widget,
        currentUrl: null,
    };

    node.__haigcInfoPreview = preview;

    const onRemoved = node.onRemoved;
    node.onRemoved = () => {
        node.__haigcInfoPreview = null;
        return onRemoved?.();
    };

    return node.__haigcInfoPreview;
}

function updatePreview(node, message) {
    if (!node || node.comfyClass !== "HAIGC_VideoInfoPreview") {
        return;
    }
    const preview = ensurePreviewWidget(node);
    
    const videos = message?.ui?.videos || message?.videos;
    let info = null;
    if (Array.isArray(videos) && videos.length > 0) {
        info = videos[0];
    } else {
        const vi = message?.result?.[0];
        if (vi && typeof vi === "object") {
            info = {
                filename: vi.filename ?? "",
                subfolder: "",
                type: "input",
                format: (vi.format ?? "").toLowerCase(),
                fps: vi.fps ?? 0,
                frame_count: (vi.total_frames ?? vi.frame_count ?? 0),
                duration: vi.duration ?? 0,
                absolute_path: vi.source_path ?? "",
                has_audio: !!vi.has_audio,
                file_size_mb: typeof vi.file_size_mb === "number" ? vi.file_size_mb : 0,
                width: vi.width ?? 0,
                height: vi.height ?? 0,
                video_bitrate_kbps: vi.video_bitrate_kbps ?? 0,
                audio_bitrate_kbps: vi.audio_bitrate_kbps ?? 0,
            };
        }
    }
    
    if (!info) {
        preview.container.style.display = "none";
        return;
    }
    
    // 设置视频源（已禁用视频预览）
    // const params = new URLSearchParams({
    //     filename: info.filename ?? "",
    //     subfolder: info.subfolder ?? "",
    //     type: info.type ?? "input",
    // });
    // const url = api.apiURL(`/view?${params.toString()}`);
    // if (preview.currentUrl !== url) {
    //     preview.videoEl.src = url;
    //     preview.currentUrl = url;
    // }

    // 格式化信息
    const formatText = info.format ? info.format.toUpperCase() : "";
    const fpsText = info.fps ? `${info.fps}fps` : "";
    const durationText = formatDuration(info.duration);
    const sizeText = typeof info.file_size_mb === "number" ? `${info.file_size_mb.toFixed(2)}MB` : "";
    const resolutionText = info.width && info.height ? `${info.width}x${info.height}` : "";
    const frameCountText = info.frame_count ? `总帧数：${info.frame_count}帧` : "";
    
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
    
    const filename = info.filename || baseName(info.absolute_path) || "视频";

    const lines = [];
    lines.push(`文件名: ${filename}`);
    
    // 如果时长缺失但有帧数和帧率，回退计算
    const durationOrFallback = durationText || (
        info.frame_count && info.fps
            ? formatDuration((info.frame_count / info.fps) || 0)
            : ""
    );
    const line2 = [formatText, fpsText, durationOrFallback].filter(Boolean);
    if (line2.length > 0) lines.push(line2.join(" · "));
    
    const line3 = [resolutionText, sizeText, frameCountText].filter(Boolean);
    if (line3.length > 0) lines.push(line3.join(" · "));
    
    if (bitrateText) lines.push(bitrateText);
    
    if (info.absolute_path) {
        // lines.push(`路径: ${info.absolute_path}`);
    }
    
    preview.caption.textContent = lines.join("\n");
    preview.container.style.display = "block";
    
    node.setDirtyCanvas(true);
}

app.registerExtension({
    name: "haigc.VideoInfoPreview",
    beforeRegisterNodeDef(nodeType, nodeData) {
        if (nodeData.name !== "HAIGC_VideoInfoPreview") {
            return;
        }
        const originalExecuted = nodeType.prototype.onExecuted;
        nodeType.prototype.onExecuted = function (message) {
            const result = originalExecuted?.apply(this, arguments);
            updatePreview(this, message);
            return result;
        };
    },
    nodeCreated(node) {
        if (node.comfyClass === "HAIGC_VideoInfoPreview") {
            ensurePreviewWidget(node);
            const originalOnResize = node.onResize;
            node.onResize = function() {
                const r = originalOnResize?.apply(this, arguments);
                if (this.lastExecutionResult) {
                    setTimeout(() => {
                        updatePreview(this, this.lastExecutionResult);
                    }, 50);
                }
                return r;
            };
        }
    },
});
