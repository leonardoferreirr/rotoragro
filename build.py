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


def rodape():
    regiao = (f"Oficina em {CIDADE}, com atendimento em {ABRANGENCIA}." if CIDADE else f"Atendimento em {ABRANGENCIA}, para produtores, prestadores de serviço de pulverização e cooperativas.")
    return f'''<footer class="rodape"><div class="wrap">
<div class="rodape__grade">
<div><img class="rodape__logo" src="/assets/img/logo-horizontal-sobre-escuro.svg" width="240" height="25" alt="Rotor Agro" loading="lazy"><p>Manutenção de drones agrícolas e baterias. {regiao}</p></div>
<div><p class="rodape__tit">Serviços</p><ul><li><a href="/manutencao-de-drones-agricolas">Manutenção de drones agrícolas</a></li><li><a href="/conserto-de-bateria-de-drone">Teste e conserto de bateria</a></li><li><a href="/#revisao">Revisão antes da safra</a></li><li><a href="/#perguntas">Perguntas frequentes</a></li></ul></div>
<div><p class="rodape__tit">Contato</p><ul><li><a href="{zap_link("rodape")}">WhatsApp{" " + TEL_VER if TEL_VER else ""}</a></li><li><a href="{INSTAGRAM}" target="_blank" rel="noopener">Instagram @rotoragro</a></li></ul></div>
</div>
<div class="rodape__base"><span>© {date.today().year} Rotor Agro</span>{sequencia(8, "seq seq--rodape", False)}</div>
</div></footer>
<a class="zapf" href="{zap_link("flutuante")}" aria-label="Falar no WhatsApp">{ZAP}</a>'''


FONTES = [("Tit", "archivo-exp-620", 620), ("Txt", "archivo-400", 400), ("Txt", "archivo-600", 600)]


def pagina(titulo, desc, corpo, rota="/", extra_ld="", robots=None, casca=True, classe=""):
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
<link rel="preload" href="/assets/fonts/archivo-exp-620.woff2" as="font" type="font/woff2" crossorigin>
<link rel="preload" href="/assets/fonts/archivo-400.woff2" as="font" type="font/woff2" crossorigin>
<script>document.documentElement.classList.add('js')</script>
{gtm_head()}
<style>{css}</style>
{ld(org_schema())}{extra_ld}
</head>
<body class="{classe}">
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


def perguntas_html(faq, titulo="Perguntas frequentes"):
    itens = "".join(f'<details class="pg"><summary><h3>{q}</h3><span class="pg__mais" aria-hidden="true"></span></summary><div class="pg__r"><p>{r}</p></div></details>' for q, r in faq)
    return f'<section class="secao secao--branca" id="perguntas"><div class="wrap estreito"><h2 class="tit">{titulo}</h2><div class="pgs">{itens}</div></div></section>'


def chamada(titulo, texto, contexto):
    return f'''<section class="chamada" id="contato"><div class="wrap chamada__in">{o_marca("chamada__o")}
<h2 class="tit">{titulo}</h2><p>{texto}</p>
<div class="ctas">{btn("Chamar no WhatsApp", zap_link(contexto), "lima", "zap")}</div></div></section>'''


# ------------------------------------------------------------------ conteúdo
REVENDA = "de qualquer revenda" if ATENDE_QUALQUER_REVENDA else ""
SERVICOS = [
    ("drone", "Drone que não liga ou não voa direito", "Motores, controladores, placas, GPS, radar e braços. Primeiro a gente acha a causa, depois troca a peça.", "/manutencao-de-drones-agricolas"),
    ("bateria", "Bateria que dura pouco", "Teste de saúde, equilíbrio entre as células e avaliação de bateria estufada ou com erro no aplicativo.", "/conserto-de-bateria-de-drone"),
    ("bico", "Pulverização falhando", "Bicos, bomba, mangueiras, medidor de vazão e calibração para a calda cair na dose certa.", "/manutencao-de-drones-agricolas"),
    ("helice", "Hélices e peças quebradas", "Troca de hélices, braços, trem de pouso e peças danificadas em queda ou no transporte.", "/manutencao-de-drones-agricolas"),
    ("revisao", "Revisão antes da safra", "Checagem completa na entressafra, para o drone não parar no meio da aplicação.", "/#revisao"),
    ("diagnostico", "Diagnóstico antes do conserto", "Você recebe o que foi encontrado e o orçamento antes de autorizar qualquer serviço.", "/#como"),
]
PASSOS = [
    ("Você chama no WhatsApp", "Conte o modelo do drone e o que está acontecendo. Se puder, mande um vídeo ou a foto do erro no aplicativo."),
    ("Diagnóstico e orçamento", "A gente encontra o defeito e envia o orçamento. Nada é consertado sem a sua aprovação."),
    ("Conserto e teste", "Trocamos o que precisa e testamos o drone e as baterias antes de devolver."),
    ("Entrega com selo de revisão", "O drone volta com o selo de revisão e o número da ordem de serviço, para você saber o que foi feito e quando."),
]
SINAIS = [("A autonomia cai.", "O drone cobre menos hectares com a mesma carga."),
          ("A bateria estufa.", "Carcaça inchada ou com trinca não volta para o campo."),
          ("As células desequilibram.", "O aplicativo mostra diferença de tensão entre elas ou avisa erro de bateria.")]

FAQ_HOME = [
    ("Vocês atendem drone comprado em qualquer revenda?", "Sim. A Rotor Agro faz a manutenção de drones agrícolas de qualquer revenda. O que importa é o modelo, não onde ele foi comprado."),
    ("Quais drones vocês consertam?", "Drones de pulverização da DJI, da linha Agras, e da XAG, além das baterias e dos carregadores desses modelos."),
    ("O orçamento sai antes do conserto?", "Sim. Primeiro vem o diagnóstico, depois o orçamento. O conserto só começa com a sua aprovação."),
    ("Quanto tempo demora?", "Depende do defeito e da peça. O prazo é informado junto com o orçamento, antes de você aprovar o serviço."),
    ("Vocês consertam bateria de drone agrícola?", "Sim. Testamos a saúde da bateria, o equilíbrio entre as células e o histórico de ciclos, e dizemos se o reparo compensa ou se é hora de trocar."),
    ("Quando é melhor fazer a revisão do drone?", "Na entressafra, antes de começarem as aplicações. Drone que voa muitas horas por dia também pede uma revisão no meio da safra."),
    ("Vocês atendem drones de outros estados?", "Sim. A Rotor Agro atende todo o Brasil. Chame no WhatsApp para combinar como o drone e as baterias chegam até a oficina e voltam para você."),
]


def abertura():
    return f'''<section class="abertura" aria-labelledby="h1"><div class="palco">
<div class="wrap palco__in">
<div class="abertura__txt">
<h1 id="h1" class="h1">Manutenção de drones agrícolas e baterias</h1>
<p class="lead">Drone de pulverização parado no meio da safra custa caro. A Rotor Agro atende todo o Brasil: encontra o defeito, passa o orçamento antes de mexer e devolve o drone pronto para voar.</p>
<div class="ctas">{btn("Chamar no WhatsApp", zap_link("abertura"), "lima", "zap")}{btn("Ver os serviços", "#servicos", "linha")}</div>
</div>
<div class="abertura__drone">{drone.svg()}</div>
</div></div></section>'''


def servicos():
    cards = "".join(f'''<a class="card" href="{u}" style="--i:{i}"><span class="card__ic">{icone(n)}</span><h3>{t}</h3><p>{d}</p><span class="card__seta">{SETA}</span></a>''' for i, (n, t, d, u) in enumerate(SERVICOS))
    return f'''<section class="secao" id="servicos"><div class="wrap servicos">
<div class="servicos__tit"><h2 class="tit">O que a gente conserta</h2><p class="sub">Drone, bateria e sistema de pulverização{", " + REVENDA if REVENDA else ""}. Você manda o problema e a gente diz o que é.</p>{btn("Falar com a oficina", zap_link("servicos"), "escuro", "zap")}</div>
<div class="pilha">{cards}</div></div></section>'''


def como():
    itens = "".join(f'''<li class="passo rv"><div class="passo__o">{o_helice(-i * 45, "passo__svg")}</div><span class="passo__n">0{i + 1}</span><h3>{t}</h3><p>{d}</p></li>''' for i, (t, d) in enumerate(PASSOS))
    return f'''<section class="secao secao--branca" id="como"><div class="wrap">
<h2 class="tit tit--centro">Do chamado à entrega</h2>
<ol class="passos">{itens}</ol>
<div class="selo rv"><img src="/assets/img/selo-revisao-320.webp" srcset="/assets/img/selo-revisao-320.webp 320w, /assets/img/selo-revisao-520.webp 520w" sizes="(max-width:700px) 200px, 260px" width="260" height="260" alt="Selo de revisão da Rotor Agro, com data e número da ordem de serviço" loading="lazy">
<p>O selo fica no drone. Na hora de revisar de novo, o número leva direto à ordem de serviço anterior.</p></div>
</div></section>'''


def baterias():
    lis = "".join(f'<li><span>0{i + 1}</span><div><b>{t}</b> {d}</div></li>' for i, (t, d) in enumerate(SINAIS))
    return f'''<section class="secao secao--escura" id="baterias"><div class="wrap bat">
<div class="bat__txt"><h2 class="tit">Bateria é a peça que mais se gasta no drone</h2>
<p class="sub">Cada carga consome um pouco das células. Antes de comprar uma bateria nova, vale testar a que você tem. Três sinais de que ela está no fim:</p>
<ul class="sinais">{lis}</ul>
<div class="ctas">{btn("Testar minhas baterias", zap_link("baterias"), "lima", "zap")}{btn("Como é o teste", "/conserto-de-bateria-de-drone", "linha-clara")}</div></div>
<div class="bat__img rv"><img src="/assets/img/etiqueta-bateria-600.webp" srcset="/assets/img/etiqueta-bateria-600.webp 600w, /assets/img/etiqueta-bateria-900.webp 900w" sizes="(max-width:900px) 90vw, 520px" width="600" height="213" alt="Etiqueta de bateria testada da Rotor Agro, com ciclos, saúde e data" loading="lazy"><p>Cada bateria testada sai com a etiqueta: ciclos, saúde em porcentagem, data e ordem de serviço.</p></div>
</div></section>'''


def revisao():
    return f'''<section class="faixa" id="revisao"><div class="wrap faixa__in">
{sequencia(8, "seq seq--faixa")}
<h2 class="tit">Revisão antes da safra</h2>
<p class="sub">Na entressafra o drone está parado e a revisão não atrapalha o trabalho. É a hora de trocar o que está gasto, calibrar a pulverização e testar as baterias.</p>
<div class="ctas">{btn("Agendar a revisão", zap_link("revisao"), "escuro", "zap")}</div></div></section>'''


def modelos():
    fita = "".join(f'<span>{e(m)}</span>{o_helice(80, "fita__o")}' for m in MODELOS)
    return f'''<section class="secao" id="modelos"><div class="wrap"><h2 class="tit tit--centro">Drones que a gente atende</h2>
<p class="sub sub--centro">Drones de pulverização da DJI e da XAG{", " + REVENDA if REVENDA else ""}, com as baterias e os carregadores de cada modelo.</p></div>
<div class="fita" aria-label="Modelos atendidos: {e(", ".join(MODELOS))}"><div class="fita__trilho"><div class="fita__grupo">{fita}</div><div class="fita__grupo" aria-hidden="true">{fita}</div></div></div></section>'''


def home():
    corpo = abertura() + servicos() + como() + baterias() + revisao() + modelos() + perguntas_html(FAQ_HOME) + chamada(
        "Drone parado é prejuízo todo dia", "Mande o modelo e o problema no WhatsApp. A gente responde com o próximo passo.", "final")
    lds = ld(site_ld()) + ld(faq_ld(FAQ_HOME)) + ld(servico_ld("Manutenção de drones agrícolas e baterias", "/", DESC_ORG))
    return pagina("Manutenção de drones agrícolas e baterias | Rotor Agro",
                  "Conserto de drones agrícolas de pulverização e de baterias, com atendimento em todo o Brasil: diagnóstico, orçamento antes do serviço, teste de bateria e revisão antes da safra.",
                  corpo, "/", lds, classe="home")


# ------------------------------------------------------------------ páginas de serviço
def cabeca(h1, lead, contexto, migalha):
    return f'''<section class="cabeca"><div class="wrap cabeca__in">{o_marca("cabeca__o")}
<nav class="migalha" aria-label="Você está em"><a href="/">Início</a><span aria-hidden="true">/</span><span>{migalha}</span></nav>
<h1 class="h1">{h1}</h1><p class="lead">{lead}</p>
<div class="ctas">{btn("Chamar no WhatsApp", zap_link(contexto), "lima", "zap")}</div></div></section>'''


def lista_blocos(itens, cls="blocos"):
    return f'<div class="{cls}">' + "".join(f'<div class="bloco rv" style="--i:{n}"><span class="bloco__ic">{icone(i)}</span><h3>{t}</h3><p>{d}</p></div>' for n, (i, t, d) in enumerate(itens)) + "</div>"


DEFEITOS_DRONE = [
    ("drone", "Drone que não arma ou não decola", "Erro de motor, de controlador ou de sensor que impede a decolagem."),
    ("motor", "Motor com barulho ou vibração", "Rolamento gasto, eixo empenado ou hélice desbalanceada."),
    ("placa", "Erro de placa ou de comunicação", "Falha de controlador, de cabo ou de conector depois de chuva, poeira ou queda."),
    ("campo", "GPS, RTK ou radar com erro", "Drone que perde posição, não segue o terreno ou avisa falha de sensor."),
    ("bico", "Aplicação irregular", "Bico entupido, bomba fraca, vazamento ou medidor de vazão fora de calibração."),
    ("helice", "Peças quebradas", "Braço, hélice, trem de pouso e carenagem danificados em queda ou no transporte."),
]
FAQ_DRONE = [
    ("Vocês consertam drone que caiu?", "Sim. Depois de uma queda a gente avalia estrutura, braços, motores, placas e sensores e passa o orçamento antes de consertar."),
    ("O drone precisa ir até a oficina?", "Para o diagnóstico completo, sim. Atendemos todo o Brasil: chame no WhatsApp para combinar como o drone chega até a oficina e volta para você."),
    FAQ_HOME[0], FAQ_HOME[2], FAQ_HOME[3],
]


def pag_drone():
    corpo = cabeca("Manutenção de drones agrícolas", f"Conserto de drones de pulverização DJI Agras e XAG{', ' + REVENDA if REVENDA else ''}, com atendimento em todo o Brasil. Diagnóstico primeiro, orçamento antes de mexer e teste antes de devolver.", "pagina-drone", "Manutenção de drones agrícolas")
    corpo += f'''<section class="secao"><div class="wrap"><h2 class="tit">Os defeitos que mais chegam na oficina</h2>{lista_blocos(DEFEITOS_DRONE)}</div></section>'''
    passos = "".join(f'<li><span class="passo__n">0{i + 1}</span><div><h3>{t}</h3><p>{d}</p></div></li>' for i, (t, d) in enumerate(PASSOS))
    corpo += f'''<section class="secao secao--branca"><div class="wrap duas"><div><h2 class="tit">Como é o serviço</h2><p class="sub">O mesmo caminho para qualquer defeito, com o orçamento aprovado por você antes do conserto.</p></div><ol class="passos-lista">{passos}</ol></div></section>'''
    corpo += revisao() + perguntas_html(FAQ_DRONE) + chamada("Seu drone está parado?", "Mande o modelo e o que está acontecendo. Um vídeo do erro já ajuda no diagnóstico.", "pagina-drone-final")
    desc = "Conserto de drones agrícolas de pulverização DJI Agras e XAG para todo o Brasil: motores, placas, GPS, radar, bicos e peças. Diagnóstico e orçamento antes do serviço."
    lds = ld(servico_ld("Manutenção de drones agrícolas", "/manutencao-de-drones-agricolas", desc)) + ld(faq_ld(FAQ_DRONE)) + ld(migalhas_ld([("Início", "/"), ("Manutenção de drones agrícolas", "/manutencao-de-drones-agricolas")]))
    return pagina("Manutenção de drones agrícolas DJI Agras e XAG | Rotor Agro", desc, corpo, "/manutencao-de-drones-agricolas", lds)


TESTE_BATERIA = [
    ("bateria", "Saúde da bateria", "Quanto da capacidade original ela ainda guarda, medido e anotado na etiqueta."),
    ("placa", "Equilíbrio entre as células", "Diferença de tensão entre as células, que é o que costuma gerar erro no aplicativo."),
    ("diagnostico", "Histórico de ciclos", "Quantas cargas ela já fez, para saber quanto ainda falta para o fim da vida útil."),
    ("garantia", "Carcaça e conectores", "Inchaço, trinca, conector queimado ou com folga, que são riscos no campo."),
]
FAQ_BATERIA = [
    ("Bateria estufada tem conserto?", "Na maioria dos casos, não vale o risco. A bateria estufada deve sair de uso. A gente avalia e orienta o descarte correto."),
    ("Quanto dura uma bateria de drone agrícola?", "Depende do modelo e do uso. O fabricante informa o número de ciclos esperado, e o teste mostra quanto da vida útil ainda resta."),
    ("Vocês testam o carregador também?", "Sim. Carregador com defeito encurta a vida da bateria, então ele entra no teste quando você manda junto."),
    FAQ_HOME[4], FAQ_HOME[2],
]


def pag_bateria():
    corpo = cabeca("Teste e conserto de bateria de drone agrícola", "Antes de comprar uma bateria nova, descubra quanto ainda resta da que você tem. Teste de saúde, equilíbrio das células e avaliação de bateria com erro.", "pagina-bateria", "Bateria de drone")
    corpo += f'''<section class="secao"><div class="wrap"><h2 class="tit">O que o teste mostra</h2>{lista_blocos(TESTE_BATERIA, "blocos blocos--4")}</div></section>'''
    lis = "".join(f'<li><span>0{i + 1}</span><div><b>{t}</b> {d}</div></li>' for i, (t, d) in enumerate(SINAIS))
    corpo += f'''<section class="secao secao--escura"><div class="wrap bat"><div class="bat__txt"><h2 class="tit">Três sinais de que a bateria está no fim</h2><ul class="sinais">{lis}</ul>
<div class="ctas">{btn("Testar minhas baterias", zap_link("pagina-bateria-sinais"), "lima", "zap")}</div></div>
<div class="bat__img rv"><img src="/assets/img/etiqueta-bateria-600.webp" srcset="/assets/img/etiqueta-bateria-600.webp 600w, /assets/img/etiqueta-bateria-900.webp 900w" sizes="(max-width:900px) 90vw, 520px" width="600" height="213" alt="Etiqueta de bateria testada da Rotor Agro" loading="lazy"><p>A etiqueta fica na bateria, com o resultado do teste e o número da ordem de serviço.</p></div></div></section>'''
    corpo += perguntas_html(FAQ_BATERIA) + chamada("Baterias durando pouco?", "Mande quantas baterias são e o modelo do drone. A gente combina o teste.", "pagina-bateria-final")
    desc = "Teste e conserto de bateria de drone agrícola DJI Agras e XAG, com atendimento em todo o Brasil: saúde, equilíbrio das células, ciclos, carregador e bateria com erro."
    lds = ld(servico_ld("Teste e conserto de bateria de drone agrícola", "/conserto-de-bateria-de-drone", desc)) + ld(faq_ld(FAQ_BATERIA)) + ld(migalhas_ld([("Início", "/"), ("Bateria de drone", "/conserto-de-bateria-de-drone")]))
    return pagina("Teste e conserto de bateria de drone agrícola | Rotor Agro", desc, corpo, "/conserto-de-bateria-de-drone", lds)


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
             "Como funciona: contato pelo WhatsApp, diagnóstico, orçamento aprovado pelo cliente, conserto, teste e entrega com selo de revisão e número da ordem de serviço.",
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
    JS.write_text(JS_FONTE.read_text())
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
