#!/usr/bin/env python3
"""Capturas de página inteira (computador e celular) e erros de console. Uso: python3 tools/auditar.py [rota ...]"""
import asyncio, sys
from pathlib import Path
from playwright.async_api import async_playwright
chrome = sorted((Path.home() / "Library/Caches/ms-playwright").glob("chromium_headless_shell-*/*/chrome-headless-shell"))[-1]
OUT = Path(__file__).resolve().parent.parent / ".audit"; OUT.mkdir(exist_ok=True)
rotas = sys.argv[1:] or ["/"]
async def main():
    async with async_playwright() as p:
        nav = await p.chromium.launch(executable_path=str(chrome))
        for nome, vp, mob in (("pc", {"width": 1440, "height": 900}, False), ("cel", {"width": 390, "height": 844}, True)):
            ctx = await nav.new_context(viewport=vp, device_scale_factor=1, is_mobile=mob, has_touch=mob)
            pg = await ctx.new_page(); erros = []
            pg.on("console", lambda m: erros.append(m.text) if m.type == "error" else None)
            pg.on("pageerror", lambda e: erros.append(str(e)))
            for r in rotas:
                await pg.goto("http://localhost:4230" + r); await pg.wait_for_load_state("load"); await pg.wait_for_timeout(400)
                altura = await pg.evaluate("document.body.scrollHeight")
                for y in range(0, altura, 500):
                    await pg.evaluate(f"window.scrollTo(0,{y})"); await pg.wait_for_timeout(60)
                await pg.evaluate("document.querySelectorAll('.rv').forEach(e=>e.classList.add('vis')); window.scrollTo(0,0)"); await pg.wait_for_timeout(500)
                arq = OUT / f"{nome}{r.replace('/', '_') or '_'}.png"
                await pg.screenshot(path=str(arq), full_page=True)
                larg = await pg.evaluate("[document.documentElement.scrollWidth, innerWidth]")
                print(nome, r, "altura", altura, "largura", larg, "erros", erros[:3])
            await ctx.close()
        await nav.close()
asyncio.run(main())
