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

## ライセンス
このプロジェクトのライセンスについては `LICENSE` ファイルをご参照ください。