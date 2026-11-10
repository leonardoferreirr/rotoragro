import asyncio
from pathlib import Path
from playwright.async_api import async_playwright
chrome = sorted((Path.home() / "Library/Caches/ms-playwright").glob("chromium_headless_shell-*/*/chrome-headless-shell"))[-1]
OUT = Path(__file__).resolve().parent.parent / ".audit"
PASSOS = [("abertura", "0"), ("frase1", "AB*0.3"), ("frase2", "AB*0.7"), ("quadro", "AB*0.97"), ("servicos", "#servicos+120"), ("como", "#como+40"),
          ("bateria-linhas", "#baterias+P*0.35"), ("bateria-solida", "#baterias+P*1.05"), ("revisao", "#revisao"), ("modelos", "#modelos+40"), ("chamada", "#contato")]
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path=str(chrome), args=["--use-gl=swiftshader", "--enable-webgl", "--ignore-gpu-blocklist"])
        pg = await b.new_page(viewport={"width": 390, "height": 844}, is_mobile=True, has_touch=True, device_scale_factor=2)
        erros = []; pg.on("pageerror", lambda e: erros.append(str(e)))
        await pg.goto("http://localhost:4230/"); await pg.wait_for_load_state("load"); await pg.wait_for_timeout(1500)
        await pg.evaluate("document.querySelectorAll('img[loading=lazy]').forEach(i=>i.loading='eager')")
        for nome, alvo in PASSOS:
            y = await pg.evaluate(f"""(() => {{ const ab=document.querySelector('.abertura'), AB=ab.offsetHeight-innerHeight; const pal=document.querySelector('.b3d__palco'); const P = pal ? pal.offsetHeight : 0;
              const a = '{alvo}'; if (a.startsWith('#')) {{ const [id, extra] = a.slice(1).split('+'); return document.getElementById(id).offsetTop + (extra ? eval(extra) : 0); }} return eval(a); }})()""")
            await pg.evaluate(f"window.scrollTo(0,{y})"); await pg.wait_for_timeout(1300)
            await pg.screenshot(path=str(OUT / f"cel-{nome}.png"))
        print("erros:", erros); await b.close()
asyncio.run(main())
