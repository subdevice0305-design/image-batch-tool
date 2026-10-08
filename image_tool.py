import argparse
from pathlib import Path
from PIL import Image, ImageOps

EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp"}
FORMATS = {"png": "PNG", "jpg": "JPEG", "webp": "WEBP"}


def parse_color(value):
    """'#ffffff' / 'fff' / 'ffffff' を (R, G, B) に変換"""
    h = value.lstrip("#")
    if len(h) == 3:
        h = "".join(c * 2 for c in h)
    try:
        if len(h) != 6:
            raise ValueError
        return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))
    except ValueError:
        raise argparse.ArgumentTypeError(f"色は #rrggbb 形式で指定してください: {value}")


def parse_ratio(value):
    """'16:9' / '16x9' / '1.91:1' を (幅, 高さ) に変換"""
    try:
        a, b = value.lower().replace("x", ":").split(":")
        a, b = float(a), float(b)
        if a <= 0 or b <= 0:
            raise ValueError
        return a, b
    except ValueError:
        raise argparse.ArgumentTypeError(f"比率は 16:9 のように指定してください: {value}")


def parse_args():
    p = argparse.ArgumentParser(description="画像の一括リサイズ・形式変換ツール(Pillowのみ)")
    p.add_argument("-i", "--input", type=Path, default=Path("input"), help="入力フォルダ (default: input)")
    p.add_argument("-o", "--output", type=Path, default=Path("output"), help="出力フォルダ (default: output)")
    p.add_argument("-s", "--sizes", type=int, nargs="+", default=[800, 400],
                   help="長辺のサイズ。複数可。サイズごとにフォルダ分け (default: 800 400)")
    p.add_argument("-f", "--format", choices=list(FORMATS), default=None,
                   help="出力形式 (default: 元の形式のまま)")
    p.add_argument("--ratio", type=parse_ratio, default=None,
                   help="縦横比。例: 16:9 / 4:5 / 3:2 (default: 元の比率のまま)")
    p.add_argument("--square", action="store_true", help="正方形にする (--ratio 1:1 と同じ)")
    p.add_argument("--crop", action="store_true",
                   help="余白を足さず、はみ出た部分を切り取って比率に合わせる (--ratio か --square と一緒に使う)")
    p.add_argument("--bg", type=parse_color, default=(255, 255, 255),
                   help="余白・塗りつぶしの色 (default: #ffffff)")
    p.add_argument("--flatten", action="store_true", help="透過部分を --bg の色で塗りつぶす (jpgは常に塗りつぶし)")
    p.add_argument("--delete", action="store_true", help="成功した元画像を input から削除")
    args = p.parse_args()
    if any(s <= 0 for s in args.sizes):
        p.error("サイズは1以上の整数で指定してください")
    if args.square:
        args.ratio = (1, 1)
    if args.crop and args.ratio is None:
        p.error("--crop は --ratio か --square と一緒に使ってください")
    return args


def flatten(img, bg):
    """透過部分を bg で塗りつぶして RGB にする"""
    base = Image.new("RGBA", img.size, bg + (255,))
    base.alpha_composite(img)
    return base.convert("RGB")


def is_opaque(img):
    return img.getchannel("A").getextrema() == (255, 255)


def canvas_size(size, ratio):
    """長辺が size になるキャンバスの (幅, 高さ)"""
    rw, rh = ratio
    if rw >= rh:
        return size, max(1, round(size * rh / rw))
    return max(1, round(size * rw / rh)), size


def process(src, args):
    with Image.open(src) as img:
        img = ImageOps.exif_transpose(img).convert("RGBA")
        ext = (args.format or src.suffix.lstrip(".")).lower()
        if ext == "jpeg":
            ext = "jpg"

        for size in args.sizes:
            if args.ratio and args.crop:
                out = ImageOps.fit(img, canvas_size(size, args.ratio), Image.LANCZOS)
            else:
                out = img.copy()
                out.thumbnail((size, size))  # 縦横比を保って縮小
                if args.ratio:
                    cw, ch = canvas_size(size, args.ratio)
                    out.thumbnail((cw, ch))
                    canvas = Image.new("RGBA", (cw, ch), args.bg + (255,))
                    pos = ((cw - out.width) // 2, (ch - out.height) // 2)
                    canvas.paste(out, pos, out)
                    out = canvas

            if ext == "jpg" or args.flatten:
                out = flatten(out, args.bg)
            elif is_opaque(out):
                out = out.convert("RGB")  # 透過なしなら軽くする

            folder = args.output / str(size)
            folder.mkdir(parents=True, exist_ok=True)
            out.save(folder / f"{src.stem}.{ext}", FORMATS[ext])


def main():
    args = parse_args()
    if not args.input.is_dir():
        print(f"入力フォルダが見つかりません: {args.input}")
        return
    args.output.mkdir(exist_ok=True)

    files = [p for p in sorted(args.input.iterdir()) if p.suffix.lower() in EXTENSIONS]
    if not files:
        print(f"{args.input} フォルダに画像を入れてね")
        return

    ok = 0
    for src in files:
        try:
            process(src, args)
            if args.delete:
                src.unlink()
            ok += 1
            print(f"done: {src.name}")
        except Exception as e:
            print(f"skip: {src.name} ({e})")

    print(f"{ok}/{len(files)} 枚処理した")


if __name__ == "__main__":
    main()
