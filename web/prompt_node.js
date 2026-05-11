import { app } from "../../scripts/app.js";

app.registerExtension({
    name: "m4.prompt_node",
    async nodeCreated(node) {
        if (node.comfyClass === "M4PromptNode") {
            const jsonPathWidget = node.widgets.find((w) => w.name === "json_file_path");
            const promptSelectorWidget = node.widgets.find((w) => w.name === "prompt_selector");
            const text2Widget = node.widgets.find((w) => w.name === "text_2");
            
            let loadedJsonData = {};

            const updateSelector = async (path) => {
                if (!path) return;
                try {
                    const response = await fetch(`/m4/read_json?path=${encodeURIComponent(path)}`);
                    const result = await response.json();
                    
                    if (result.data) {
                        loadedJsonData = result.data;
                        const keys = Object.keys(loadedJsonData);
                        promptSelectorWidget.options.values = keys.length > 0 ? keys : [""];
                        if (keys.length > 0) {
                            promptSelectorWidget.value = keys[0];
                            // Initial selection triggers text update
                            text2Widget.value = loadedJsonData[keys[0]];
                        } else {
                            promptSelectorWidget.value = "";
                            text2Widget.value = "";
                        }
                    } else {
                        console.error("Error loading JSON:", result.error);
                    }
                    app.graph.setDirtyCanvas(true, true);
                } catch (e) {
                    console.error("Failed to fetch JSON:", e);
                }
            };

            // JSONパスが変更されたときの処理
            jsonPathWidget.callback = () => {
                updateSelector(jsonPathWidget.value);
            };

            // セレクタが変更されたときの処理
            promptSelectorWidget.callback = () => {
                const selectedKey = promptSelectorWidget.value;
                if (loadedJsonData && loadedJsonData[selectedKey] !== undefined) {
                    text2Widget.value = loadedJsonData[selectedKey];
                } else {
                    text2Widget.value = "";
                }
            };
            
            // 初回読み込み時にパスが設定されていれば読み込む
            if (jsonPathWidget.value) {
                updateSelector(jsonPathWidget.value);
            }
        }
    }
});
