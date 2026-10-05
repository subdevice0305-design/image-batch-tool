from pathlib import Path
from PIL import Image, ImageOps

INPUT_DIR = Path("input")
OUTPUT_DIR = Path("output")
MAX_SIZE = (800, 800)
EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp"}
DELETE_ORIGINAL = True  # True: 縮小に成功した元画像を input から削除


def main():
    OUTPUT_DIR.mkdir(exist_ok=True)
    files = [p for p in sorted(INPUT_DIR.iterdir()) if p.suffix.lower() in EXTENSIONS]
    if not files:
        print("input フォルダに画像を入れてね")
        return

    ok = 0
    for src in files:
        try:
            with Image.open(src) as img:
                img = ImageOps.exif_transpose(img)  # スマホ写真の向きを正す
                img.thumbnail(MAX_SIZE)  # 縦横比を保ったまま縮小
                img.save(OUTPUT_DIR / src.name)
            if DELETE_ORIGINAL:
                src.unlink()
            ok += 1
            print(f"done: {src.name}")
        except Exception as e:
            print(f"skip: {src.name} ({e})")

    print(f"{ok}/{len(files)} 枚処理した")


if __name__ == "__main__":
    main()
