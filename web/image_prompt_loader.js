import { app } from "../../scripts/app.js";

app.registerExtension({
    name: "m4.image_prompt_loader",
    async nodeCreated(node) {
        if (node.comfyClass === "M4FolderImagePromptLoader") {
            const pathWidget = node.widgets.find((w) => w.name === "folder_path");
            const selectWidget = node.widgets.find((w) => w.name === "image_select");
            
            // プロンプトプレビュー用テキストウィジェットの追加（フロント専用）
            const previewWidget = node.addWidget(
                "text", 
                "prompt_preview", 
                "", 
                () => {}, 
                { multiline: true, serialize: false }
            );
            
            // 読込専用にし、デザインを少し調整
            if (previewWidget) {
                Object.defineProperty(previewWidget, "inputEl", {
                    configurable: true,
                    enumerable: true,
                    get() {
                        return this._inputEl;
                    },
                    set(val) {
                        this._inputEl = val;
                        if (val) {
                            val.readOnly = true;
                            val.style.opacity = 0.8;
                            val.style.backgroundColor = "#1a1a1a";
                            val.style.color = "#00ffcc";
                            val.style.fontFamily = "monospace";
                        }
                    }
                });
            }

            node.isImagesLoading = false;

            // 画像リストをスキャンしてドロップダウンを更新
            node.updateImagesList = async function(path, selectValueToRestore) {
                if (!path || this.isImagesLoading) return;
                this.isImagesLoading = true;
                
                try {
                    const response = await fetch(`/m4/get_images?path=${encodeURIComponent(path)}`);
                    const result = await response.json();
                    
                    if (result.files) {
                        const files = result.files;
                        const selectWidget = this.widgets.find((w) => w.name === "image_select");
                        if (selectWidget) {
                            selectWidget.options.values = files.length > 0 ? files : [""];
                            
                            if (files.length > 0) {
                                if (selectValueToRestore && files.includes(selectValueToRestore)) {
                                    selectWidget.value = selectValueToRestore;
                                } else if (!files.includes(selectWidget.value)) {
                                    selectWidget.value = files[0];
                                }
                                this.updatePreview(selectWidget.value);
                            } else {
                                selectWidget.value = "";
                                this.updatePreview("");
                            }
                        }
                    } else {
                        console.error("Error loading images list:", result.error);
                    }
                    app.graph.setDirtyCanvas(true, true);
                } catch (e) {
                    console.error("Failed to fetch images list:", e);
                } finally {
                    this.isImagesLoading = false;
                }
            };

            // プレビューの更新 (画像 & 同名テキスト)
            node.updatePreview = async function(filename) {
                const pathWidget = this.widgets.find((w) => w.name === "folder_path");
                if (!pathWidget || !pathWidget.value || !filename) {
                    this.imgs = null;
                    if (previewWidget) previewWidget.value = "";
                    app.graph.setDirtyCanvas(true, true);
                    return;
                }

                const folderPath = pathWidget.value;

                // 1. テキスト（プロンプト）のロード
                try {
                    const txtRes = await fetch(`/m4/get_text_preview?folder_path=${encodeURIComponent(folderPath)}&filename=${encodeURIComponent(filename)}`);
                    const txtData = await txtRes.json();
                    if (previewWidget) {
                        previewWidget.value = txtData.text || "";
                    }
                } catch (e) {
                    console.error("Failed to fetch text preview:", e);
                }

                // 2. 画像プレビューのロードと描画
                const img = new Image();
                img.src = `/m4/get_image_preview?folder_path=${encodeURIComponent(folderPath)}&filename=${encodeURIComponent(filename)}`;
                img.onload = () => {
                    this.imgs = [img];
                    
                    // ノードサイズの自動調整
                    const nodeWidth = this.size[0] || 260;
                    const imgAspect = img.height / img.width;
                    const imgHeight = nodeWidth * imgAspect;
                    
                    // 各ウィジェットの高さを合算
                    let widgetsHeight = 0;
                    if (this.widgets) {
                        for (const w of this.widgets) {
                            if (w.computeSize) {
                                widgetsHeight += w.computeSize(nodeWidth)[1] || 32;
                            } else {
                                widgetsHeight += w.type === "text" && w.options.multiline ? 80 : 32;
                            }
                            widgetsHeight += 6; // マージン
                        }
                    }
                    
                    // 画像の高さと余白を足してサイズを設定
                    this.size = [nodeWidth, widgetsHeight + imgHeight + 30];
                    app.graph.setDirtyCanvas(true, true);
                };
                img.onerror = () => {
                    this.imgs = null;
                    app.graph.setDirtyCanvas(true, true);
                };
            };

            // コールバック登録
            if (pathWidget) {
                const origCallback = pathWidget.callback;
                pathWidget.callback = function() {
                    if (origCallback) origCallback.apply(this, arguments);
                    node.updateImagesList(pathWidget.value);
                };
            }

            if (selectWidget) {
                const origCallback = selectWidget.callback;
                selectWidget.callback = function() {
                    if (origCallback) origCallback.apply(this, arguments);
                    node.updatePreview(selectWidget.value);
                };
            }

            // ワークフロー読込時の初期化
            const onConfigure = node.onConfigure;
            node.onConfigure = function() {
                if (onConfigure) onConfigure.apply(this, arguments);
                const pathWidget = this.widgets.find((w) => w.name === "folder_path");
                const selectWidget = this.widgets.find((w) => w.name === "image_select");
                if (pathWidget && pathWidget.value) {
                    node.updateImagesList(pathWidget.value, selectWidget ? selectWidget.value : null);
                }
            };

            // 描画時にスキャン（リフレッシュ対策）
            const onDrawBackground = node.onDrawBackground;
            node.onDrawBackground = function() {
                if (onDrawBackground) onDrawBackground.apply(this, arguments);
                
                const pathWidget = this.widgets.find((w) => w.name === "folder_path");
                const selectWidget = this.widgets.find((w) => w.name === "image_select");
                
                if (pathWidget && pathWidget.value && selectWidget) {
                    const hasNoValues = !selectWidget.options.values || 
                                        selectWidget.options.values.length === 0 || 
                                        (selectWidget.options.values.length === 1 && selectWidget.options.values[0] === "");
                    
                    if (hasNoValues && !this.isImagesLoading) {
                        this.updateImagesList(pathWidget.value, selectWidget.value);
                    }
                }
            };

            // 初回起動時のロード
            if (pathWidget && pathWidget.value) {
                node.updateImagesList(pathWidget.value, selectWidget ? selectWidget.value : null);
            }
        }
    }
});
