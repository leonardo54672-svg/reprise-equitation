from PIL import Image, ImageDraw
import math, os

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "icons")
os.makedirs(OUT, exist_ok=True)

BG_TOP = (46, 90, 70)      # #2E5A46
BG_BOTTOM = (25, 54, 41)   # #193629
FG = (244, 240, 228)       # ivoire


def draw_icon(size, padding_ratio=0.0):
    S = 1024
    img = Image.new("RGB", (S, S), BG_TOP)
    d = ImageDraw.Draw(img)

    # dégradé vertical
    for y in range(S):
        t = y / (S - 1)
        c = tuple(int(BG_TOP[i] + (BG_BOTTOM[i] - BG_TOP[i]) * t) for i in range(3))
        d.line([(0, y), (S, y)], fill=c)

    cx = cy = S / 2
    scale = 1.0 - padding_ratio
    r = 300 * scale          # rayon moyen du fer
    w = int(88 * scale)      # épaisseur
    cy = cy - 20 * scale

    bbox = [cx - r, cy - r, cx + r, cy + r]
    # arc ouvert vers le bas : 160° -> 380°
    d.arc(bbox, 160, 380, fill=FG, width=w)

    # PIL épaissit l'arc vers l'intérieur : la fibre neutre est à r - w/2
    rm = r - w / 2

    # extrémités arrondies
    for ang in (160, 20):
        a = math.radians(ang)
        px = cx + rm * math.cos(a)
        py = cy + rm * math.sin(a)
        d.ellipse([px - w / 2, py - w / 2, px + w / 2, py + w / 2], fill=FG)

    # trous de clous
    hole = int(20 * scale)
    for ang in (200, 230, 260, 290, 320, 350):
        a = math.radians(ang)
        px = cx + rm * math.cos(a)
        py = cy + rm * math.sin(a)
        d.ellipse([px - hole, py - hole, px + hole, py + hole], fill=BG_BOTTOM)

    return img.resize((size, size), Image.LANCZOS)


draw_icon(180).save(os.path.join(OUT, "apple-touch-icon.png"))
draw_icon(192).save(os.path.join(OUT, "icon-192.png"))
draw_icon(512).save(os.path.join(OUT, "icon-512.png"))
# version "maskable" : marge de sécurité pour le rognage Android
draw_icon(512, padding_ratio=0.22).save(os.path.join(OUT, "icon-512-maskable.png"))
print("icons ok")
