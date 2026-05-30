# m4-ComfyUI

ComfyUI用のカスタムノード群です。主にLora学習のキャプション作成ワークフローなどを効率化するためのノードを提供します。

## インストール方法

1. ComfyUIの `custom_nodes` ディレクトリに移動します。
2. このリポジトリをクローンします。
   ```bash
   git clone https://github.com/m4logicworks/m4-ComfyUI.git
   ```
3. ComfyUIを再起動します。

## ノード一覧

### 1. M4 Sequence Image Loader
指定したフォルダ内の画像を、ファイル名順（昇順）に順番に読み込むことができるノードです。ComfyUIのバッチ処理と組み合わせて、フォルダ内の画像を1枚ずつ連続して処理する際に便利です。

- **カテゴリ**: `M4/loaders`
- **入力項目**:
  - `folder_path` (STRING): 画像が保存されているフォルダの絶対パス。
  - `image_index` (INT): 読み込む画像のインデックス番号（0始まり）。`Primitive` ノードを繋ぎ `increment` に設定することで順番に読み込むことができます。
- **出力項目**:
  - `IMAGE`: 読み込んだ画像データ（スマホなどのExif回転情報も自動補正されます）。
  - `STRING`: 拡張子を除いたファイル名（例: `001.png` なら `001`）。
  - `INT`: 画像の幅 (Width)。
  - `INT`: 画像の高さ (Height)。

### 2. M4 Save Text
テキストデータ（LLMで生成されたキャプションなど）を、指定したフォルダにテキストファイル（`.txt`）として保存するノードです。

- **カテゴリ**: `M4/savers`
- **入力項目**:
  - `text` (STRING): 保存したいテキストデータ。他のノードからの出力を繋いで使用します。
  - `folder_path` (STRING): テキストファイルを保存するフォルダの絶対パス。
  - `filename` (STRING): 保存するファイル名（`.txt` の拡張子は自動で付与されます）。
  - `collision_behavior` (COMBO): 同名のファイルが既に存在した場合の動作を選択します。
    - `replace`: 既存のファイルを上書きします（デフォルト）。
    - `rename`: ファイル名の末尾に連番を付けて別名保存します（例: `output_1.txt`）。
- **出力項目**:
  - `STRING`: 実際に保存されたファイルの絶対パス。

### 3. M4 Prompt Node
テキスト入力の管理、および指定したJSONファイルからのプロンプトの動的な選択と自動読み込みを行うノードです。

- **カテゴリ**: `M4/text`
- **入力項目**:
  - `text_1` (STRING, 複数行): 任意のテキストを入力できます。
  - `json_file_path` (STRING): 読み込みたいプロンプトデータ（JSON形式）のファイルパス。
  - `prompt_selector` (COMBO): JSONファイルからロードされたキー（プロンプト名）のリストから選択します。
  - `text_2` (STRING, 複数行): `prompt_selector` で選択されたプロンプトテキストが自動的にここにロードされます。手動で編集することも可能です。
  - `output_choice` (COMBO): 出力するソースを選択します。`Text 1` または `Text 2` から選択します。
- **出力項目**:
  - `text` (STRING): `output_choice` で選択されたテキストデータを出力します。

### 4. M4 Resolution Preset Node
一般的な画像生成や動画配信の解像度プリセットをプルダウンから選択し、幅 (Width) と高さ (Height) を出力するノードです。

- **カテゴリ**: `M4/utils`
- **入力項目**:
  - `preset` (COMBO): 1024, 1536, 2048 などの正方形、SDXL/Flux系、2K解像度、HD/FHD動画規格などから解像度を選択します。`Custom` を選ぶと任意の数値を指定可能です。
  - `custom_width` (INT): `preset` に `Custom` を選んだ際に出力する任意の幅（デフォルト 1024）。
  - `custom_height` (INT): `preset` に `Custom` を選んだ際に出力する任意の高さ（デフォルト 1024）。
  - `invert_aspect` (BOOLEAN): `True` に設定すると、選択された解像度の幅と高さを入れ替えて出力します（縦横の切り替えに便利です）。
  - `batch_size` (INT): バッチサイズ（`Empty Latent Image` 等に直接接続できるように出力します。デフォルト 1）。
- **出力項目**:
  - `width` (INT): 出力する幅のピクセル数。
  - `height` (INT): 出力する高さのピクセル数。
  - `batch_size` (INT): 設定されたバッチサイズ。

### 5. M4 Texture Generator
画像生成（i2iのノイズインジェクションなど）にベース素材として使用できる様々なテクスチャやノイズ画像を生成するノードです。

- **カテゴリ**: `M4/image`
- **入力項目**:
  - `width` (INT): 生成するテクスチャの幅（デフォルト 1024）。
  - `height` (INT): 生成するテクスチャの高さ（デフォルト 1024）。
  - `batch_size` (INT): 生成するバッチサイズ（デフォルト 1）。
  - `texture_type` (COMBO): 生成するテクスチャの種類（12種類）。
    - `White Noise`, `Gaussian Noise`, `Film Grain`, `Perlin Noise (Smooth)`, `Fractal Noise (High Detail)`, `Canvas Texture`, `Paper Texture`, `Horizontal Brush`, `Vertical Brush`, `Diagonal Hatching`, `Vignette`, `Color Cloud`
  - `scale` (FLOAT): ノイズやテクスチャのスケール値（デフォルト 1.0）。
  - `strength` (FLOAT): ベースカラーに対するテクスチャ効果の適用強度。0.0で単色、1.0でテクスチャ全開となります（デフォルト 0.5）。
  - `color_preset` (COMBO): ベースとなる背景色のプリセット（White, Black, Gray, Red, Green, Blue, Sepia, Warm, Cool, Custom HEX）。
  - `custom_hex` (STRING): `color_preset` で `Custom HEX` を選んだ際に反映される任意のHEXカラーコード（デフォルト `#FFFFFF`）。
- **出力項目**:
  - `IMAGE`: 生成されたRGB画像。

### 6. M4 Wildcard Loader
YAML形式のワイルドカードファイルからテキストデータを読み込み、ランダム、シーケンシャル（順番）、または固定インデックスで1項目を抽出して出力するノードです。

- **カテゴリ**: `M4/text`
- **入力項目**:
  - `wildcard_dir` (STRING): ワイルドカードファイルを保存しているフォルダの絶対パス。
  - `wildcard_selector` (COMBO): フォルダ内のYAMLファイルから自動スキャンされたワイルドカードキー（例: `sample/gravure_pose/basic_pose` や上位の `sample/gravure_pose` など）を選択します。
  - `preview_text` (STRING, 複数行): `wildcard_selector` で選択されたワイルドカードに含まれるテキスト候補の一覧が自動的に改行区切りでプレビュー表示されます（読み取り専用）。
  - `mode` (COMBO): テキストデータの選択モードを選択します。
    - `random`: `seed` に基づいた再現性のあるランダムな項目抽出。
    - `sequential`: 実行（Queue Prompt）ごとに上から順に抽出し、最後まで到達すると最初に戻ります（別のワイルドカードキーを選択した場合はインデックスが自動リセットされます）。
    - `fixed`: `fixed_index` で指定されたインデックスの項目を抽出します。
  - `fixed_index` (INT): `fixed` モードの際に抽出する項目のインデックス（0始まり）。
  - `seed` (INT): `random` モードの際に使用する乱数シード。シード値を固定すると同じ項目が抽出され、変更すると異なる項目がランダム抽出されます。
- **出力項目**:
  - `text` (STRING): 選択されたテキストデータを出力します。

#### ワイルドカードYAMLの形式について
以下のような階層構造（辞書およびリスト）を持つ `.yaml` / `.yml` 形式に対応しています。

```yaml
gravure_pose:
  basic_pose:
    - standing, cowboy shot, looking at viewer
    - standing, cowboy shot, arms behind head
  lying_pose:
    - lying on stomach, looking at viewer
    - lying on side, looking at viewer
```

本ノードでは、最下層のリスト項目（例: `basic_pose`）だけでなく、中間カテゴリ（例: `gravure_pose`）やファイル名レベルの上位キーを選択することも可能です。上位のカテゴリを選択した場合は、その配下にあるすべてのリスト項目が自動的に結合（マージ）されて抽出対象となります。

## ライセンス
このプロジェクトのライセンスについては `LICENSE` ファイルをご参照ください。