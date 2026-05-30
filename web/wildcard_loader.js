import { app } from "../../scripts/app.js";

app.registerExtension({
    name: "m4.wildcard_loader",
    async nodeCreated(node) {
        if (node.comfyClass === "M4WildcardLoader") {
            const dirWidget = node.widgets.find((w) => w.name === "wildcard_dir");
            const selectorWidget = node.widgets.find((w) => w.name === "wildcard_selector");
            const previewWidget = node.widgets.find((w) => w.name === "preview_text");

            // preview_text を読込専用にする（DOM要素が生成された時点で適用）
            if (previewWidget) {
                if (previewWidget.inputEl) {
                    previewWidget.inputEl.readOnly = true;
                    previewWidget.inputEl.style.opacity = 0.7;
                } else {
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
                                val.style.opacity = 0.7;
                            }
                        }
                    });
                }
            }

            node.loadedWildcardsData = {};
            node.isWildcardsLoading = false;

            node.updateSelector = async function(path) {
                if (!path || this.isWildcardsLoading) return;
                this.isWildcardsLoading = true;
                try {
                    const response = await fetch(`/m4/get_wildcards?path=${encodeURIComponent(path)}`);
                    const result = await response.json();
                    
                    if (result.data) {
                        this.loadedWildcardsData = result.data.wildcards || {};
                        const keys = result.data.keys || [];
                        
                        const selectorWidget = this.widgets.find((w) => w.name === "wildcard_selector");
                        if (selectorWidget) {
                            selectorWidget.options.values = keys.length > 0 ? keys : [""];
                            
                            if (keys.length > 0) {
                                if (!keys.includes(selectorWidget.value)) {
                                    selectorWidget.value = keys[0];
                                }
                                this.updatePreview(selectorWidget.value);
                            } else {
                                selectorWidget.value = "";
                                this.updatePreview("");
                            }
                        }
                    } else {
                        console.error("Error loading wildcards:", result.error);
                    }
                    app.graph.setDirtyCanvas(true, true);
                } catch (e) {
                    console.error("Failed to fetch wildcards:", e);
                } finally {
                    this.isWildcardsLoading = false;
                }
            };

            node.updatePreview = function(selectedKey) {
                const previewWidget = this.widgets.find((w) => w.name === "preview_text");
                if (previewWidget) {
                    if (this.loadedWildcardsData && this.loadedWildcardsData[selectedKey]) {
                        const items = this.loadedWildcardsData[selectedKey];
                        previewWidget.value = items.join("\n");
                    } else {
                        previewWidget.value = "";
                    }
                }
            };

            // ディレクトリパス変更時の処理
            if (dirWidget) {
                dirWidget.callback = () => {
                    node.updateSelector(dirWidget.value);
                };
            }

            // セレクタ変更時の処理
            if (selectorWidget) {
                selectorWidget.callback = () => {
                    node.updatePreview(selectorWidget.value);
                };
            }
            
            // ノードの設定復元時（ワークフロー読み込み時）の初期化処理
            const onConfigure = node.onConfigure;
            node.onConfigure = function() {
                if (onConfigure) onConfigure.apply(this, arguments);
                if (dirWidget && dirWidget.value) {
                    node.updateSelector(dirWidget.value);
                }
            };

            // 描画時にデータが未ロードでパスがある場合、自動ロードする（リフレッシュ時の復元対策）
            const onDrawBackground = node.onDrawBackground;
            node.onDrawBackground = function() {
                if (onDrawBackground) onDrawBackground.apply(this, arguments);
                
                const dirWidget = this.widgets.find((w) => w.name === "wildcard_dir");
                const selectorWidget = this.widgets.find((w) => w.name === "wildcard_selector");
                
                if (dirWidget && dirWidget.value && selectorWidget) {
                    const hasNoValues = !selectorWidget.options.values || 
                                        selectorWidget.options.values.length === 0 || 
                                        (selectorWidget.options.values.length === 1 && selectorWidget.options.values[0] === "");
                                        
                    const hasNoData = !this.loadedWildcardsData || Object.keys(this.loadedWildcardsData).length === 0;
                    
                    if ((hasNoValues || hasNoData) && !this.isWildcardsLoading) {
                        this.updateSelector(dirWidget.value);
                    }
                }
            };

            // 初回読み込み時の初期化処理
            if (dirWidget && dirWidget.value) {
                node.updateSelector(dirWidget.value);
            }
        }
    }
});
