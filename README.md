# image-batch-tool

画像を一括でリサイズ・形式変換するPythonツールです。Pillowのみ使用。

- 複数サイズの同時書き出し(サイズごとにフォルダ分け)
- 形式変換(png / jpg / webp)
- 正方形への余白追加
- 透過部分の塗りつぶし

## セットアップ

```bash
pip install pillow
```

## 基本の使い方

1. 画像を `input` フォルダに入れる
2. 実行する
3. `output` フォルダに結果が出る

```bash
python image_tool.py
```

何も付けないと、長辺800pxと400pxの2サイズで、元の形式のまま保存されます。

## オプション


| 引数               | 意味                     | 初期値     |
| ---------------- | ---------------------- | ------- |
| `-i`, `--input`  | 入力フォルダ                 | input   |
| `-o`, `--output` | 出力フォルダ                 | output  |
| `-s`, `--sizes`  | 長辺のサイズ(複数可)            | 800 400 |
| `-f`, `--format` | 出力形式(png / jpg / webp) | 元の形式    |
| `--square`       | 正方形になるよう余白を足す          | OFF     |
| `--bg`           | 余白・塗りつぶしの色             | #ffffff |
| `--flatten`      | 透過部分を `--bg` の色で塗りつぶす  | OFF     |
| `--delete`       | 処理に成功した元画像を削除          | OFF     |


jpg に変換するときは、透過部分が自動で塗りつぶされる

## 使用例

```bash
# 1200pxのwebpにする
python image_tool.py -s 1200 -f webp

# 1080px正方形、黒い余白
python image_tool.py -s 1080 --square --bg "#000000"

# jpgに変換、透過部分はクリーム色
python image_tool.py -f jpg --bg "#f5f0e6"

# 1200px・600px、正方形、webp、透過をクリーム色で塗りつぶし
python image_tool.py -o out_test -s 1200 600 --square -f webp --flatten --bg "#f5f0e6"
```



## 出力のしくみ

```
output/
├── 800/
│   ├── photo1.jpg
│   └── photo2.png
└── 400/
    ├── photo1.jpg
    └── photo2.png
```



## 注意

- 同じ名前のファイルは上書きされます。出力先を分けたいときは `-o` を使う。
- `--delete` は元画像が消えます。最初はコピーした画像で試してください。
- 対応する入力形式は png / jpg / jpeg / webp です。それ以外のファイルは無視されます。
- 写真の向きは自動で補正されます。



## ファイル構成

- `image_tool.py` : 本体(v2。複数サイズ・形式変換・余白・引数対応)
- `resize_all.py` : 最初の版(v1。縮小のみ。成功すると元画像を削除するので注意)

