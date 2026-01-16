import { app } from "../../../scripts/app.js";
import { api } from "../../../scripts/api.js";

const WIDGET_ID = "haigc_loader_preview";

app.registerExtension({
    name: "haigc.VideoLoaderPreview",
    nodeCreated(node) {
        if (node.comfyClass === "HAIGC_VideoLoader") {
            // 移除节点的最小尺寸限制，允许任意调整大小到最小
            const removeMinSize = () => {
                // 移除节点的最小宽度和高度限制
                if (node.minWidth !== undefined) {
                    node.minWidth = 0;
                }
                if (node.minHeight !== undefined) {
                    node.minHeight = 0;
                }
                
                // 移除 DOM 元素的 CSS 最小尺寸限制
                const nodeEl = node.el || node;
                if (nodeEl) {
                    // 直接设置样式，使用 !important 覆盖所有可能的限制
                    nodeEl.style.setProperty("min-width", "0", "important");
                    nodeEl.style.setProperty("min-height", "0", "important");
                    nodeEl.style.setProperty("overflow", "hidden", "important");
                    nodeEl.style.setProperty("box-sizing", "border-box", "important");
                    
                    // 查找并移除所有子元素的最小尺寸限制
                    const allElements = nodeEl.querySelectorAll("*");
                    allElements.forEach(el => {
                        if (el.style) {
                            el.style.setProperty("min-width", "0", "important");
                            el.style.setProperty("min-height", "0", "important");
                            el.style.setProperty("box-sizing", "border-box", "important");
                        }
                    });
                    
                    // 检查并移除计算样式中的最小尺寸
                    const computedStyle = window.getComputedStyle(nodeEl);
                    if (computedStyle.minWidth && computedStyle.minWidth !== "0px" && computedStyle.minWidth !== "0") {
                        nodeEl.style.setProperty("min-width", "0", "important");
                    }
                    if (computedStyle.minHeight && computedStyle.minHeight !== "0px" && computedStyle.minHeight !== "0") {
                        nodeEl.style.setProperty("min-height", "0", "important");
                    }
                    
                    // 查找节点内容区域（通常有特定的类名）
                    const contentArea = nodeEl.querySelector(".content") || 
                                       nodeEl.querySelector("[class*='content']") ||
                                       nodeEl.querySelector(".node_content");
                    if (contentArea) {
                        contentArea.style.setProperty("min-width", "0", "important");
                        contentArea.style.setProperty("min-height", "0", "important");
                        contentArea.style.setProperty("overflow", "hidden", "important");
                        contentArea.style.setProperty("box-sizing", "border-box", "important");
                    }
                    
                    // 处理输入字段区域（可能阻止节点缩小）
                    const inputArea = nodeEl.querySelector(".inputs") || 
                                     nodeEl.querySelector("[class*='input']") ||
                                     nodeEl.querySelector(".node_inputs");
                    if (inputArea) {
                        inputArea.style.setProperty("min-width", "0", "important");
                        inputArea.style.setProperty("min-height", "0", "important");
                        inputArea.style.setProperty("overflow", "hidden", "important");
                        inputArea.style.setProperty("box-sizing", "border-box", "important");
                    }
                    
                    // 处理所有可能的固定宽度元素
                    const fixedWidthElements = nodeEl.querySelectorAll("[style*='min-width'], [style*='minWidth']");
                    fixedWidthElements.forEach(el => {
                        el.style.setProperty("min-width", "0", "important");
                    });

                    // 允许控件在容器变窄时收缩且不撑开容器
                    const widgetElements = nodeEl.querySelectorAll(".widget, [class*='widget'], input, select, textarea, label");
                    widgetElements.forEach(el => {
                        el.style.setProperty("min-width", "0", "important");
                        el.style.setProperty("max-width", "100%", "important");
                        el.style.setProperty("width", "auto", "important");
                        el.style.setProperty("overflow", "hidden", "important");
                        el.style.setProperty("white-space", "nowrap", "important");
                        el.style.setProperty("text-overflow", "ellipsis", "important");
                    });

                    // 压缩预览区域的尺寸以适配更小的节点宽度
                    const previewMedia = nodeEl.querySelectorAll("video, img, canvas");
                    previewMedia.forEach(el => {
                        el.style.setProperty("max-width", "100%", "important");
                        el.style.setProperty("height", "auto", "important");
                        el.style.setProperty("max-height", "140px", "important");
                        el.style.setProperty("object-fit", "contain", "important");
                    });

                    // 标题和文本区域允许换行或收缩
                    const titleEl = nodeEl.querySelector(".title, .node-title, [class*='title']");
                    if (titleEl) {
                        titleEl.style.setProperty("min-width", "0", "important");
                        titleEl.style.setProperty("white-space", "normal", "important");
                        titleEl.style.setProperty("word-break", "break-word", "important");
                    }
                }
            };
            
            // 立即移除最小尺寸限制
            removeMinSize();
            
            // 延迟多次移除，确保节点已完全初始化（包括所有可能的渲染阶段）
            setTimeout(removeMinSize, 50);
            setTimeout(removeMinSize, 100);
            setTimeout(removeMinSize, 200);
            setTimeout(removeMinSize, 300);
            setTimeout(removeMinSize, 500);
            setTimeout(removeMinSize, 1000);
            
            // 监听节点大小变化，持续移除限制
            const minSizeResizeObserver = new ResizeObserver(() => {
                removeMinSize();
            });
            
            setTimeout(() => {
                const nodeEl = node.el || node;
                if (nodeEl) {
                    minSizeResizeObserver.observe(nodeEl);
                }
            }, 100);
            
            // 监听节点的 UI 更新和大小变化，持续移除限制
            const originalOnResize = node.onResize;
            node.onResize = function() {
                const result = originalOnResize?.apply(this, arguments);
                // 在每次调整大小时移除最小尺寸限制
                removeMinSize();
                return result;
            };
            
            const originalOnRemoved = node.onRemoved;
            node.onRemoved = () => {
                minSizeResizeObserver.disconnect();
                return originalOnRemoved?.();
            };
        }
    },
});
