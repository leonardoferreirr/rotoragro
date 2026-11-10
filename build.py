#!/usr/bin/env python3
"""Gera o site estático da Rotor Agro: páginas, dados estruturados, sitemap, robots e arquivos para as IAs.

Rodar: python3 build.py
"""
import hashlib, json, re, sys
from datetime import date
from html import escape as e, unescape
from pathlib import Path

RAIZ = Path(__file__).parent
sys.path.insert(0, str(RAIZ / "tools"))
import drone

# ------------------------------------------------------------------ dados do cliente
# Tudo que depende do cliente fica aqui. Enquanto INDEXAR for False, o site fica fora do Google.
DOMINIO = "https://www.rotoragro.com.br"
INDEXAR = False            # ligar quando entrarem cidade, WhatsApp e as confirmações abaixo
WHATSAPP = ""             # [A PREENCHER] só números, com 55 e DDD; vazio, os botões levam a uma página que aponta para o Instagram
TEL_VER = ""               # como o número aparece escrito, ex.: "(34) 99999-9999"
INSTAGRAM = "https://www.instagram.com/rotoragro"
CIDADE = ""                # opcional: cidade da oficina, ex.: "Uberlândia, MG"
ABRANGENCIA = "todo o Brasil"   # o atendimento é nacional: o drone vem até a oficina
GTM_ID = ""
# [A CONFIRMAR] com o cliente: cada uma dessas afirmações aparece no site
ATENDE_QUALQUER_REVENDA = True
MODELOS = ["DJI Agras T10", "DJI Agras T16", "DJI Agras T20", "DJI Agras T20P", "DJI Agras T25", "DJI Agras T30",
           "DJI Agras T40", "DJI Agras T50", "DJI Agras T100", "XAG P100", "XAG V40"]

VE, VM, LI, AM, BE, BR = "#0F3226", "#1F7A4D", "#B9DE4F", "#F5E58A", "#F0EADB", "#FFFFFF"
CSS = RAIZ / "_src/site.css"
JS_FONTE = RAIZ / "_src/site.js"
JS = RAIZ / "assets/js/site.js"
JS3D = RAIZ / "assets/js/bateria3d.js"
ESBUILD = RAIZ / "tools/3d/node_modules/.bin/esbuild"
ICONES = Path.home() / "kit-piloto-automatico/06_OUTPUTS/rotor-agro/marca/icones"


def minificar(css):
    css = re.sub(r"/\*.*?\*/", "", css, flags=re.S)
    css = re.sub(r"\s+", " ", css)
    css = re.sub(r"\s*([{};:,>])\s*", r"\1", css)
    return css.replace(";}", "}").strip()


def hash_de(p):
    return hashlib.sha1(p.read_bytes()).hexdigest()[:10]


def icone(nome, tema="claro", px=48):
    s = (ICONES / f"{nome}-{tema}.svg").read_text()
    return s.replace("<svg ", f'<svg width="{px}" height="{px}" aria-hidden="true" focusable="false" ', 1)


SETA = '<svg viewBox="0 0 16 16" fill="none" aria-hidden="true"><path d="M2 8h11M9 4l4 4-4 4" stroke="currentColor" stroke-width="1.6"/></svg>'
ZAP = ('<svg class="zap" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M12 2a10 10 0 0 0-8.6 15.1L2 22l5-1.3A10 10 0 1 0 12 2zm0 18.2a8.2 8.2 0 0 1-4.2-1.1l-.3-.2-3 .8.8-2.9-.2-.3A8.2 8.2 0 1 1 12 20.2zm4.5-6.1c-.2-.1-1.5-.7-1.7-.8s-.4-.1-.6.1-.7.8-.8 1-.3.2-.5.1a6.7 6.7 0 0 1-3.3-2.9c-.2-.4.2-.4.7-1.3.1-.2 0-.3 0-.4l-.8-1.8c-.2-.5-.4-.4-.6-.4h-.5a1 1 0 0 0-.7.3 3 3 0 0 0-.9 2.2 5.2 5.2 0 0 0 1.1 2.7 11.8 11.8 0 0 0 4.5 4c1.7.7 2.4.8 3.2.6a2.8 2.8 0 0 0 1.8-1.3 2.3 2.3 0 0 0 .2-1.3c-.1-.1-.3-.2-.6-.3z"/></svg>')


def zap_link(contexto):
    return f"/obrigado?c={contexto}"


def btn(txt, href, tipo="lima", icone_="seta"):
    if icone_ == "zap":
        return f'<a class="btn btn--{tipo}" href="{href}">{ZAP}<span>{txt}</span></a>'
    return f'<a class="btn btn--{tipo}" href="{href}"><span>{txt}</span>{SETA}</a>'


# O da marca para grafismo (o mesmo do logo, oval) e a sequência do giro
O_MARCA = re.search(r'd="([^"]+)"', (RAIZ / "assets/img/logo-simbolo-sobre-escuro.svg").read_text())[1]
VB_O = re.search(r'viewBox="([^"]+)"', (RAIZ / "assets/img/logo-simbolo-sobre-escuro.svg").read_text())[1]


# os dois desenhos do O entram uma vez só na página, como símbolos, e cada uso aponta para eles
SPRITE = (f'<svg width="0" height="0" style="position:absolute" aria-hidden="true" focusable="false"><defs>'
          f'<path id="o-helice" d="{drone.O_HELICE}"/><path id="o-marca" d="{O_MARCA}"/></defs></svg>')


def o_marca(cls, cor="currentColor"):
    return f'<svg class="{cls}" viewBox="{VB_O}" aria-hidden="true" focusable="false"><use href="#o-marca" fill="{cor}"/></svg>'


def o_helice(rot, cls="", cor="currentColor"):
    return f'<svg class="{cls}" viewBox="-104 -104 208 208" aria-hidden="true" focusable="false"><use href="#o-helice" fill="{cor}" transform="rotate({rot})"/></svg>'


def sequencia(n=8, cls="seq", destaque=True):
    return f'<div class="{cls}" aria-hidden="true">' + "".join(o_helice(-i * 180 / n, "seq__o" + (" seq__o--fim" if destaque and i == n - 1 else "")) for i in range(n)) + "</div>"


# ------------------------------------------------------------------ dados estruturados
def ld(obj):
    return f'<script type="application/ld+json">{json.dumps(obj, ensure_ascii=False, separators=(",", ":"))}</script>'


ORG_ID = DOMINIO + "/#empresa"
DESC_ORG = "Oficina de manutenção de drones agrícolas de pulverização e de baterias de drone: diagnóstico, conserto, teste de bateria e revisão antes da safra."


def org_schema():
    d = {"@context": "https://schema.org", "@type": "LocalBusiness", "@id": ORG_ID, "name": "Rotor Agro", "alternateName": ["Rotoragro", "rotoragro"],
         "url": DOMINIO + "/", "logo": DOMINIO + "/assets/img/icone-180.png", "image": DOMINIO + "/assets/img/og-image.jpg",
         "description": DESC_ORG, "sameAs": [INSTAGRAM], "priceRange": "Sob orçamento",
         "knowsAbout": ["Manutenção de drones agrícolas", "Conserto de drone de pulverização", "Teste e conserto de bateria de drone", "Revisão de drone antes da safra", "DJI Agras", "XAG"]}
    if WHATSAPP:
        d["telephone"] = "+" + WHATSAPP
    d["areaServed"] = {"@type": "Country", "name": "Brasil"}
    if CIDADE:
        cid, uf = [x.strip() for x in CIDADE.split(",")]
        d["address"] = {"@type": "PostalAddress", "addressLocality": cid, "addressRegion": uf, "addressCountry": "BR"}
    return d


def site_ld():
    return {"@context": "https://schema.org", "@type": "WebSite", "@id": DOMINIO + "/#site", "url": DOMINIO + "/", "name": "Rotor Agro",
            "alternateName": ["Rotoragro"], "inLanguage": "pt-BR", "publisher": {"@id": ORG_ID}}


def servico_ld(nome, rota, desc):
    return {"@context": "https://schema.org", "@type": "Service", "@id": DOMINIO + rota + "#servico", "name": nome, "serviceType": nome,
            "url": DOMINIO + rota, "description": desc, "provider": {"@id": ORG_ID}, "areaServed": {"@type": "Country", "name": "Brasil"}}


def faq_ld(faq):
    return {"@context": "https://schema.org", "@type": "FAQPage",
            "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": re.sub("<[^>]+>", "", r)}} for q, r in faq]}


def migalhas_ld(passos):
    return {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": i + 1, "name": n, "item": DOMINIO + u} for i, (n, u) in enumerate(passos)]}


def gtm_head():
    if not GTM_ID:
        return ""
    return ("<script>(function(w,d,s,l,i){w[l]=w[l]||[];w[l].push({'gtm.start':new Date().getTime(),event:'gtm.js'});"
            "var f=d.getElementsByTagName(s)[0],j=d.createElement(s),dl=l!='dataLayer'?'&l='+l:'';j.async=true;"
            f"j.src='https://www.googletagmanager.com/gtm.js?id='+i+dl;f.parentNode.insertBefore(j,f);}})(window,document,'script','dataLayer','{GTM_ID}');</script>")


# ------------------------------------------------------------------ casca
NAV = [("Serviços", "/#servicos"), ("Drones", "/manutencao-de-drones-agricolas"), ("Baterias", "/conserto-de-bateria-de-drone"), ("Perguntas", "/#perguntas")]


def topo(rota):
    links = "".join(f'<a href="{u}"{" aria-current=page" if u == rota else ""}>{n}</a>' for n, u in NAV)
    return f'''<header class="topo"><div class="wrap topo__in">
<a class="marca" href="/" aria-label="Rotor Agro, página inicial"><img src="/assets/img/logo-horizontal-sobre-escuro.svg" width="190" height="20" alt="Rotor Agro"></a>
<nav class="nav" aria-label="Principal">{links}</nav>
<a class="topo__zap" href="{zap_link("topo")}">{ZAP}<span>WhatsApp</span></a>
</div></header>'''


def creditos():
    """CC BY-SA pede autor, licença e link; o CC0 não pede, mas fica junto."""
    vistos, partes = set(), []
    for d in DRONES:
        if d["pagina"] in vistos: continue
        vistos.add(d["pagina"])
        partes.append(f'<a href="{d["pagina"]}" target="_blank" rel="noopener">{e(d["nome"])}</a>, {e(d["autor"])}, {e(d["licenca"])}')
    return "Fotos dos drones via Wikimedia Commons: " + "; ".join(partes) + ". As demais imagens são ilustrativas."


def rodape():
    regiao = (f"Oficina em {CIDADE}, com atendimento em {ABRANGENCIA}." if CIDADE else f"Atendimento em {ABRANGENCIA}, para produtores, prestadores de serviço de pulverização e cooperativas.")
    return f'''<footer class="rodape"><div class="wrap">
<div class="rodape__grade">
<div><img class="rodape__logo" src="/assets/img/logo-horizontal-sobre-escuro.svg" width="240" height="25" alt="Rotor Agro" loading="lazy"><p>Manutenção de drones agrícolas e baterias. {regiao}</p></div>
<div><p class="rodape__tit">Serviços</p><ul><li><a href="/manutencao-de-drones-agricolas">Manutenção de drones agrícolas</a></li><li><a href="/conserto-de-bateria-de-drone">Teste e conserto de bateria</a></li><li><a href="/#revisao">Revisão antes da safra</a></li><li><a href="/#perguntas">Perguntas frequentes</a></li></ul></div>
<div><p class="rodape__tit">Contato</p><ul><li><a href="{zap_link("rodape")}">WhatsApp{" " + TEL_VER if TEL_VER else ""}</a></li><li><a href="{INSTAGRAM}" target="_blank" rel="noopener">Instagram @rotoragro</a></li></ul></div>
</div>
<div class="rodape__base"><span>© {date.today().year} Rotor Agro</span>{sequencia(8, "seq seq--rodape", False)}</div>
<p class="creditos">{creditos()}</p>
</div></footer>
<a class="zapf" href="{zap_link("flutuante")}" aria-label="Falar no WhatsApp">{ZAP}</a>'''


def pagina(titulo, desc, corpo, rota="/", extra_ld="", robots=None, casca=True, classe="", preload=""):
    robots = robots or ("index,follow,max-image-preview:large" if INDEXAR else "noindex,nofollow")
    faces = "".join(f"@font-face{{font-family:{f};src:url(/assets/fonts/{a}.woff2) format('woff2');font-weight:{w};font-display:optional}}" for f, a, w in FONTES)
    css = faces + minificar(CSS.read_text())
    return f'''<!doctype html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<title>{e(titulo)}</title>
<meta name="description" content="{e(desc)}">
<meta name="robots" content="{robots}">
<link rel="canonical" href="{DOMINIO}{rota}">
<meta name="theme-color" content="{VE}">
<meta property="og:type" content="website"><meta property="og:locale" content="pt_BR"><meta property="og:site_name" content="Rotor Agro">
<meta property="og:title" content="{e(titulo)}"><meta property="og:description" content="{e(desc)}"><meta property="og:url" content="{DOMINIO}{rota}">
<meta property="og:image" content="{DOMINIO}/assets/img/og-image.jpg"><meta property="og:image:width" content="1200"><meta property="og:image:height" content="630"><meta name="twitter:card" content="summary_large_image">
<link rel="icon" href="/favicon.ico" sizes="48x48"><link rel="icon" type="image/svg+xml" href="/assets/img/icone.svg"><link rel="apple-touch-icon" href="/assets/img/icone-180.png">
<link rel="preload" href="/assets/fonts/archivo-exp-300.woff2" as="font" type="font/woff2" crossorigin>
<link rel="preload" href="/assets/fonts/archivo-300.woff2" as="font" type="font/woff2" crossorigin>
{preload}
<script>document.documentElement.classList.add('js')</script>
{gtm_head()}
<style>{css}</style>
{ld(org_schema())}{extra_ld}
</head>
<body class="{classe}" data-b3d="/assets/js/bateria3d.js?v={hash_de(JS3D)}">
{SPRITE}
{topo(rota) if casca else ""}
<main id="conteudo">
{corpo}
</main>
{rodape() if casca else ""}
<script src="/assets/js/site.js?v={hash_de(JS)}" defer></script>
</body>
</html>
'''


exec((RAIZ / "_src/blocos.py").read_text())


def obrigado():
    if not WHATSAPP:
        corpo = f'''<section class="ponte"><div>
<img src="/assets/img/logo-horizontal-sobre-escuro.svg" width="240" height="25" alt="Rotor Agro">
<h1>O WhatsApp da Rotor Agro entra aqui em breve</h1>
<p>Enquanto isso, fale com a gente pelo Instagram.</p>
<div class="ctas">{btn("Abrir o Instagram", INSTAGRAM, "lima")}{btn("Voltar ao site", "/", "linha-clara")}</div>
</div></section>'''
        return pagina("Fale com a Rotor Agro", "Fale com a Rotor Agro.", corpo, "/obrigado", robots="noindex,nofollow", casca=False, classe="escura")
    corpo = f'''<section class="ponte"><div>
<img src="/assets/img/logo-horizontal-sobre-escuro.svg" width="240" height="25" alt="Rotor Agro">
<div class="ponte__o">{o_helice(80, "ponte__gira")}</div>
<h1>Estamos abrindo o seu WhatsApp</h1>
<p>Se não abrir sozinho, toque no botão abaixo.</p>
<div class="ctas">{btn("Abrir o WhatsApp", "https://wa.me/" + WHATSAPP, "lima", "zap").replace('<a ', '<a id="vai" ', 1)}{btn("Voltar ao site", "/", "linha-clara")}</div>
</div></section>
<script>
(function(){{
  var W='{WHATSAPP}', q=new URLSearchParams(location.search), c=q.get('c')||'site';
  var msgs={{baterias:'Olá, Rotor Agro! Vim pelo site e quero testar as baterias do meu drone.','pagina-bateria':'Olá, Rotor Agro! Vim pelo site e quero testar as baterias do meu drone.','pagina-bateria-sinais':'Olá, Rotor Agro! Vim pelo site e quero testar as baterias do meu drone.','pagina-bateria-final':'Olá, Rotor Agro! Vim pelo site e quero testar as baterias do meu drone.',revisao:'Olá, Rotor Agro! Vim pelo site e quero agendar a revisão do meu drone antes da safra.'}};
  var msg=msgs[c]||'Olá, Rotor Agro! Vim pelo site e preciso de manutenção no meu drone.';
  var dest='https://wa.me/'+W+'?text='+encodeURIComponent(msg); document.getElementById('vai').href=dest;
  var t0=Date.now(), pronto=false, partiu=false;
  function vai(){{ if(partiu) return; partiu=true; location.replace(dest); }}
  function talvez(){{ if(pronto && Date.now()-t0>=900) vai(); }}
  window.dataLayer=window.dataLayer||[];
  window.dataLayer.push({{event:'conversao_whatsapp',contexto:c,eventCallback:function(){{pronto=true;talvez();}},eventTimeout:2000}});
  {"" if GTM_ID else "pronto=true;"}
  setTimeout(talvez,900); setTimeout(vai,2600);
}})();
</script>'''
    return pagina("Abrindo o WhatsApp | Rotor Agro", "Abrindo a conversa com a Rotor Agro no WhatsApp.", corpo, "/obrigado", robots="noindex,nofollow", casca=False, classe="escura")


def nao_achou():
    corpo = f'''<section class="ponte"><div>
<img src="/assets/img/logo-horizontal-sobre-escuro.svg" width="240" height="25" alt="Rotor Agro">
<h1>Esta página não existe</h1><p>Talvez o endereço tenha mudado. Os serviços estão todos na página inicial.</p>
<div class="ctas">{btn("Ir para a página inicial", "/", "lima")}</div></div></section>'''
    return pagina("Página não encontrada | Rotor Agro", "Página não encontrada.", corpo, "/404", robots="noindex,nofollow", casca=False, classe="escura")


def guia_ia(paginas, rotas):
    def dados(r):
        h = paginas["index.html" if r == "/" else r[1:] + ".html"]
        titulo = unescape(re.search(r"<title>(.*?)</title>", h)[1]).removesuffix(" | Rotor Agro")
        desc = unescape(re.search(r'<meta name="description" content="(.*?)"', h)[1])
        blocos = [json.loads(b) for b in re.findall(r'<script type="application/ld\+json">(.*?)</script>', h)]
        return titulo, desc, [(q["name"], q["acceptedAnswer"]["text"]) for b in blocos if b["@type"] == "FAQPage" for q in b["mainEntity"]]
    resumo = ("# Rotor Agro\n\n> A Rotor Agro é uma oficina de manutenção de drones agrícolas de pulverização e de baterias de drone. "
              "Faz diagnóstico, conserto, teste de bateria e revisão antes da safra, com orçamento antes do serviço e contato pelo WhatsApp.\n")
    fatos = [f"Drones atendidos: {', '.join(MODELOS)}." + (" Atende drones de qualquer revenda." if ATENDE_QUALQUER_REVENDA else ""),
             "Serviços: motores, controladores, placas, GPS, radar, braços, hélices, sistema de pulverização (bicos, bomba, mangueiras, medidor de vazão), teste e avaliação de baterias e carregadores.",
             "Como funciona: contato pelo WhatsApp, diagnóstico, orçamento aprovado pelo cliente, conserto, teste e entrega do drone pronto para o campo.",
             "Preço e prazo: informados no orçamento, depois do diagnóstico. O site não publica preços."]
    fatos.append(f"Área de atendimento: {ABRANGENCIA}." + (f" Oficina em {CIDADE}." if CIDADE else ""))
    contato = "\n## Contato\n\n" + (f"- WhatsApp: {TEL_VER}\n" if TEL_VER else "") + f"- Instagram: {INSTAGRAM}\n- Site: {DOMINIO}/\n"
    indice = [resumo, *[f"- {f}" for f in fatos], "\n## Páginas\n"] + [f"- [{dados(r)[0]}]({DOMINIO}{r}): {dados(r)[1]}" for r in rotas]
    indice += [f"\n## Detalhes\n\n- [Perguntas frequentes]({DOMINIO}/llms-full.txt)", contato]
    (RAIZ / "llms.txt").write_text("\n".join(indice))
    completo = [resumo, *[f"- {f}" for f in fatos]]
    for r in rotas:
        titulo, desc, faq = dados(r)
        completo.append(f"\n## {titulo}\n\n{DOMINIO}{r}\n\n{desc}")
        if faq:
            completo.append("\n### Perguntas frequentes\n\n" + "\n\n".join(f"**{q}**\n{a}" for q, a in faq))
    completo.append(contato)
    (RAIZ / "llms-full.txt").write_text("\n".join(completo))


def main():
    import subprocess
    JS.write_text(JS_FONTE.read_text())
    if ESBUILD.exists():
        subprocess.run([str(ESBUILD), str(RAIZ / "tools/3d/bateria3d.js"), "--bundle", "--format=esm", "--minify", "--target=es2019", "--legal-comments=none", f"--outfile={JS3D}"], check=True, capture_output=True)
    paginas = {"index.html": home(), "manutencao-de-drones-agricolas.html": pag_drone(), "conserto-de-bateria-de-drone.html": pag_bateria(),
               "obrigado.html": obrigado(), "404.html": nao_achou()}
    for nome, html in paginas.items():
        (RAIZ / nome).write_text(html)
    rotas = ["/", "/manutencao-de-drones-agricolas", "/conserto-de-bateria-de-drone"]
    hoje = date.today().isoformat()
    (RAIZ / "sitemap.xml").write_text('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
                                      + "".join(f"<url><loc>{DOMINIO}{r}</loc><lastmod>{hoje}</lastmod></url>" for r in rotas) + "</urlset>\n")
    (RAIZ / "robots.txt").write_text("User-agent: *\n" + ("Allow: /\n" if INDEXAR else "Disallow:\n") + f"\nSitemap: {DOMINIO}/sitemap.xml\n")
    guia_ia(paginas, rotas)
    print(f"  {len(paginas)} páginas  site.js v={hash_de(JS)}  indexar={INDEXAR}  home={len(paginas['index.html']) // 1024} KB")


if __name__ == "__main__":
    main()
