#!/usr/bin/env python3
"""Prepara fontes e imagens do site a partir da marca. Rodar uma vez (ou quando a marca mudar)."""
import shutil, subprocess
from pathlib import Path
from fontTools.ttLib import TTFont
from fontTools.varLib import instancer
from fontTools import subset
from PIL import Image

RAIZ = Path(__file__).resolve().parent.parent
MARCA = Path.home() / "kit-piloto-automatico/06_OUTPUTS/rotor-agro/marca"
VAR = sorted((Path.home() / "Library/Fonts").glob("Archivo-VariableFont*"))[0]
UNI = "U+0020-007E,U+00A0-00FF,U+0131,U+0152-0153,U+02C6,U+02DA,U+02DC,U+2013-2014,U+2018-201A,U+201C-201E,U+2022,U+2026,U+20AC"

FONTES = {"archivo-exp-620": (620, 124), "archivo-400": (400, 100), "archivo-600": (600, 100)}
for nome, (w, wd) in FONTES.items():
    f = TTFont(VAR); instancer.instantiateVariableFont(f, {"wght": w, "wdth": wd}, inplace=True)
    tmp = RAIZ / f"tools/{nome}.ttf"; f.save(tmp)
    opts = subset.Options(); opts.flavor = "woff2"; opts.layout_features = ["kern", "liga", "calt"]; opts.name_IDs = ["*"]
    fs = TTFont(tmp); s = subset.Subsetter(opts); s.populate(unicodes=subset.parse_unicodes(UNI)); s.subset(fs)
    fs.flavor = "woff2"; fs.save(RAIZ / f"assets/fonts/{nome}.woff2"); tmp.unlink()
    print(nome, (RAIZ / f"assets/fonts/{nome}.woff2").stat().st_size // 1024, "KB")

for nome in ["rotoragro-horizontal-sobre-escuro", "rotoragro-horizontal-sobre-claro", "rotoragro-horizontal-branco", "rotoragro-simbolo-sobre-escuro"]:
    shutil.copy(MARCA / "svg" / f"{nome}.svg", RAIZ / "assets/img" / f"{nome.replace('rotoragro-', 'logo-')}.svg")

def webp(orig, dest, larg):
    im = Image.open(orig).convert("RGBA"); k = larg / im.width
    im.resize((larg, round(im.height * k)), Image.LANCZOS).save(dest, "WEBP", quality=86, method=6)
    print(dest.name, Image.open(dest).size, dest.stat().st_size // 1024, "KB")
webp(MARCA / "aplicacoes/etiqueta-bateria.png", RAIZ / "assets/img/etiqueta-bateria-900.webp", 900)
webp(MARCA / "aplicacoes/etiqueta-bateria.png", RAIZ / "assets/img/etiqueta-bateria-600.webp", 600)
webp(MARCA / "aplicacoes/selo-revisao.png", RAIZ / "assets/img/selo-revisao-520.webp", 520)
webp(MARCA / "aplicacoes/selo-revisao.png", RAIZ / "assets/img/selo-revisao-320.webp", 320)

av = Image.open(MARCA / "png/rotoragro-icone-app.png").convert("RGBA")
av.resize((180, 180), Image.LANCZOS).save(RAIZ / "assets/img/icone-180.png")
av.resize((32, 32), Image.LANCZOS).save(RAIZ / "assets/img/icone-32.png")
Image.open(MARCA / "png/rotoragro-avatar.png").convert("RGBA").resize((48, 48), Image.LANCZOS).save(RAIZ / "favicon.ico", sizes=[(48, 48), (32, 32), (16, 16)])
shutil.copy(MARCA / "svg/rotoragro-icone-app.svg", RAIZ / "assets/img/icone.svg")
print("ok")
