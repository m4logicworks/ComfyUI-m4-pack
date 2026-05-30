import { app } from "../../scripts/app.js";

app.registerExtension({
    name: "m4.prompt_node",
    async nodeCreated(node) {
        if (node.comfyClass === "M4PromptNode") {
            const jsonPathWidget = node.widgets.find((w) => w.name === "json_file_path");
            const promptSelectorWidget = node.widgets.find((w) => w.name === "prompt_selector");
            const text2Widget = node.widgets.find((w) => w.name === "text_2");
            
            node.loadedJsonData = {};
            node.isJsonLoading = false;

            node.updateSelector = async function(path) {
                if (!path || this.isJsonLoading) return;
                this.isJsonLoading = true;
                try {
                    const response = await fetch(`/m4/read_json?path=${encodeURIComponent(path)}`);
                    const result = await response.json();
                    
                    if (result.data) {
                        this.loadedJsonData = result.data;
                        const keys = Object.keys(this.loadedJsonData);
                        
                        const selectorWidget = this.widgets.find((w) => w.name === "prompt_selector");
                        if (selectorWidget) {
                            selectorWidget.options.values = keys.length > 0 ? keys : [""];
                            
                            if (keys.length > 0) {
                                if (!keys.includes(selectorWidget.value)) {
                                    selectorWidget.value = keys[0];
                                }
                                this.updateText2(selectorWidget.value);
                            } else {
                                selectorWidget.value = "";
                                this.updateText2("");
                            }
                        }
                    } else {
                        console.error("Error loading JSON:", result.error);
                    }
                    app.graph.setDirtyCanvas(true, true);
                } catch (e) {
                    console.error("Failed to fetch JSON:", e);
                } finally {
                    this.isJsonLoading = false;
                }
            };

            node.updateText2 = function(selectedKey) {
                const text2Widget = this.widgets.find((w) => w.name === "text_2");
                if (text2Widget) {
                    if (this.loadedJsonData && this.loadedJsonData[selectedKey] !== undefined) {
                        text2Widget.value = this.loadedJsonData[selectedKey];
                    } else {
                        text2Widget.value = "";
                    }
                }
            };

            // JSONパスが変更されたときの処理
            if (jsonPathWidget) {
                jsonPathWidget.callback = () => {
                    node.updateSelector(jsonPathWidget.value);
                };
            }

            // セレクタが変更されたときの処理
            if (promptSelectorWidget) {
                promptSelectorWidget.callback = () => {
                    node.updateText2(promptSelectorWidget.value);
                };
            }
            
            // ノードの設定復元時（ワークフロー読み込み時）の初期化処理
            const onConfigure = node.onConfigure;
            node.onConfigure = function() {
                if (onConfigure) onConfigure.apply(this, arguments);
                if (jsonPathWidget && jsonPathWidget.value) {
                    node.updateSelector(jsonPathWidget.value);
                }
            };

            // 描画時にデータが未ロードでパスがある場合、自動ロードする（リフレッシュ時の復元対策）
            const onDrawBackground = node.onDrawBackground;
            node.onDrawBackground = function() {
                if (onDrawBackground) onDrawBackground.apply(this, arguments);
                
                const jsonPathWidget = this.widgets.find((w) => w.name === "json_file_path");
                const promptSelectorWidget = this.widgets.find((w) => w.name === "prompt_selector");
                
                if (jsonPathWidget && jsonPathWidget.value && promptSelectorWidget) {
                    const hasNoValues = !promptSelectorWidget.options.values || 
                                        promptSelectorWidget.options.values.length === 0 || 
                                        (promptSelectorWidget.options.values.length === 1 && promptSelectorWidget.options.values[0] === "");
                                        
                    const hasNoData = !this.loadedJsonData || Object.keys(this.loadedJsonData).length === 0;
                    
                    if ((hasNoValues || hasNoData) && !this.isJsonLoading) {
                        this.updateSelector(jsonPathWidget.value);
                    }
                }
            };
            
            // 初回読み込み時にパスが設定されていれば読み込む
            if (jsonPathWidget && jsonPathWidget.value) {
                node.updateSelector(jsonPathWidget.value);
            }
        }
    }
});
