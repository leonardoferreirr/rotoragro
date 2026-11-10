#!/usr/bin/env python3
"""Fotos geradas (em _src/fotos) e capa do vídeo em WebP nos tamanhos usados pelo site."""
from pathlib import Path
from PIL import Image
RAIZ = Path(__file__).resolve().parent.parent
F, O = RAIZ / "_src/fotos", RAIZ / "assets/img/fotos"; O.mkdir(parents=True, exist_ok=True)

def corta(im, r):
    """Recorte centralizado na proporção r (largura/altura)."""
    if im.width / im.height > r:
        nw = int(im.height * r); x = (im.width - nw) // 2; return im.crop((x, 0, x + nw, im.height))
    nh = int(im.width / r); y = (im.height - nh) // 2; return im.crop((0, y, im.width, y + nh))

def salva(im, nome, larg, q=72):
    out = O / f"{nome}-{larg}.webp"; im.resize((larg, round(im.height * larg / im.width)), Image.LANCZOS).save(out, "WEBP", quality=q, method=6)
    return out.stat().st_size // 1024

for arq in sorted(F.glob("*.png")):
    nome = arq.stem; im = Image.open(arq).convert("RGB")
    # cartão dos serviços: 4:5; faixa larga: 16:9 (só para as que vão em faixa)
    c = corta(im, 4 / 5); k = [salva(c, f"{nome}-card", w) for w in (480, 720)]
    l = corta(im, 16 / 10); k += [salva(l, f"{nome}-largo", w) for w in (900, 1600)]
    print(nome, im.size, "KB:", k)
cap = Image.open(RAIZ / "_src/video/capa.png").convert("RGB")
print("capa-card", [salva(corta(cap, 4 / 5), "capa-card", w) for w in (480, 720)])
