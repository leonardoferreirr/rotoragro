#!/usr/bin/env python3
"""Imagem de compartilhamento (1200x630) com a marca."""
import asyncio, re
from pathlib import Path
from playwright.async_api import async_playwright
RAIZ = Path(__file__).resolve().parent.parent
chrome = sorted((Path.home() / "Library/Caches/ms-playwright").glob("chromium_headless_shell-*/*/chrome-headless-shell"))[-1]
s = (RAIZ / "assets/img/logo-simbolo-sobre-escuro.svg").read_text()
vb, d = re.search(r'viewBox="([^"]+)"', s)[1], re.search(r' d="([^"]+)"', s)[1]
H = f'''<style>@font-face{{font-family:T;src:url({(RAIZ/"assets/fonts/archivo-400.woff2").as_uri()})}}body{{margin:0}}.c{{width:1200px;height:630px;background:#0F3226;position:relative;overflow:hidden;font-family:T}}</style>
<div class=c><svg viewBox="{vb}" style="position:absolute;width:760px;left:640px;top:20px;opacity:.36"><path fill="#1F7A4D" d="{d}"/></svg>
<img src="{(RAIZ/"assets/img/logo-horizontal-sobre-escuro.svg").as_uri()}" style="position:absolute;left:90px;top:250px;width:620px">
<div style="position:absolute;left:92px;top:340px;color:#F0EADB;font-size:30px;opacity:.85">Manutenção de drones agrícolas e baterias</div></div>'''
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path=str(chrome)); pg = await b.new_page(viewport={"width": 1200, "height": 630})
        await pg.set_content(H); await pg.wait_for_timeout(400)
        await pg.screenshot(path=str(RAIZ / "assets/img/og-image.jpg"), type="jpeg", quality=88); await b.close()
asyncio.run(main()); print("ok")
