import asyncio
from pathlib import Path
from playwright.async_api import async_playwright
OUT = Path(__file__).resolve().parent.parent / ".audit"
JS_LINHAS = "(() => { const h = document.querySelector('.h1'); const lh = parseFloat(getComputedStyle(h).lineHeight); return Math.round(h.getBoundingClientRect().height / lh); })()"
async def main():
    async with async_playwright() as p:
        wk = await p.webkit.launch(executable_path=str(Path.home() / "Library/Caches/ms-playwright/webkit-2336/pw_run.sh"))
        pg = await wk.new_page(viewport={"width": 390, "height": 844}); erros = []
        pg.on("pageerror", lambda e: erros.append(str(e)))
        await pg.goto("http://localhost:4230/"); await pg.wait_for_load_state("load"); await pg.wait_for_timeout(500)
        await pg.evaluate("window.scrollTo(0, innerHeight*1.1)"); await pg.wait_for_timeout(1200)
        await pg.screenshot(path=str(OUT / "safari-abertura.png"))
        t = await pg.evaluate("document.querySelector('.d-braco').getAttribute('transform')")
        print("safari: erros", erros, "| braço", t)
        await wk.close()
        ch = await p.chromium.launch(executable_path=str(sorted((Path.home() / "Library/Caches/ms-playwright").glob("chromium_headless_shell-*/*/chrome-headless-shell"))[-1]))
        for w in (320, 360, 390, 414, 600, 768, 900, 1024, 1280, 1440):
            res = []
            for frio in (False, True):
                ctx = await ch.new_context(viewport={"width": w, "height": 900})
                if frio: await ctx.route("**/*.woff2", lambda r: r.abort())
                pg = await ctx.new_page(); await pg.goto("http://localhost:4230/"); await pg.wait_for_load_state("load"); await pg.wait_for_timeout(250)
                res.append(await pg.evaluate(JS_LINHAS)); await ctx.close()
            print(f"{w}px: título com a fonte {res[0]} linhas, sem a fonte {res[1]} linhas")
        await ch.close()
asyncio.run(main())
