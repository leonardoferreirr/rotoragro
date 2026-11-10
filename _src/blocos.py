# Conteúdo e seções do site. Lido pelo build.py (exec no mesmo espaço de nomes).

FONTES = [("Tit", "archivo-exp-620", 620), ("Leve", "archivo-exp-300", 300), ("Txt", "archivo-400", 400), ("Txt", "archivo-600", 600)]
DRONES = json.loads((RAIZ / "_src/drones.json").read_text())


def tit(forte, leve="", tag="h2", cls="tit"):
    """Título no desenho do logo: a parte forte em seminegrito e a leve na cor de destaque, como ROTOR e AGRO."""
    return f'<{tag} class="{cls}">{forte}{" <span class=leve>" + leve + "</span>" if leve else ""}</{tag}>'


def foto(nome, alt, sizes, larguras=(480, 720), tipo="card", cls="", lazy=True, w=720, h=900):
    src = ", ".join(f"/assets/img/fotos/{nome}-{tipo}-{l}.webp {l}w" for l in larguras)
    return (f'<img class="{cls}" src="/assets/img/fotos/{nome}-{tipo}-{larguras[-1]}.webp" srcset="{src}" sizes="{sizes}" '
            f'width="{w}" height="{h}" alt="{alt}"{" loading=lazy decoding=async" if lazy else ""}>')


def perguntas_html(faq, forte="Perguntas", leve="frequentes"):
    itens = "".join(f'<details class="pg"><summary><h3>{q}</h3><span class="pg__mais" aria-hidden="true"></span></summary><div class="pg__r"><p>{r}</p></div></details>' for q, r in faq)
    return f'<section class="secao secao--branca" id="perguntas"><div class="wrap estreito">{tit(forte, leve)}<div class="pgs">{itens}</div></div></section>'


def video_fundo(cls=""):
    """Vídeo da lavoura: a capa entra como imagem (é o que pinta primeiro) e o vídeo só carrega depois do load."""
    return f'''<div class="vf {cls}" data-video-desk="/assets/video/lavoura-1600.mp4" data-video-cel="/assets/video/lavoura-vertical.mp4">
<picture><source media="(max-width:700px)" srcset="/assets/img/lavoura-capa-vertical.webp"><img class="vf__capa" src="/assets/img/lavoura-capa-1600.webp" width="1600" height="900" alt="" {"fetchpriority=high" if cls == "vf--abertura" else "loading=lazy decoding=async"}></picture>
<video class="vf__video" muted playsinline loop preload="none" aria-hidden="true"></video></div>'''


def chamada(forte, leve, texto, contexto):
    return f'''<section class="chamada" id="contato">{video_fundo("vf--chamada")}<div class="chamada__veu"></div><div class="wrap chamada__in">
{tit(forte, leve)}<p>{texto}</p>
<div class="ctas">{btn("Chamar no WhatsApp", zap_link(contexto), "lima", "zap")}</div></div></section>'''


# ------------------------------------------------------------------ conteúdo
REVENDA = "de qualquer revenda" if ATENDE_QUALQUER_REVENDA else ""
SERVICOS = [
    ("oficina", "Drone que não liga ou não voa direito", "Motores, controladores, placas, GPS, radar e braços. Primeiro a gente acha a causa, depois troca a peça.", "/manutencao-de-drones-agricolas", "Técnico consertando o motor de um drone agrícola na bancada da oficina"),
    ("bateria", "Bateria que dura pouco", "Teste de saúde, equilíbrio entre as células e avaliação de bateria estufada ou com erro no aplicativo.", "/conserto-de-bateria-de-drone", "Bateria de drone agrícola sendo testada com multímetro"),
    ("bicos", "Pulverização falhando", "Bicos, bomba, mangueiras, medidor de vazão e calibração para a calda cair na dose certa.", "/manutencao-de-drones-agricolas", "Bicos de um drone agrícola pulverizando sobre a lavoura"),
    ("helice", "Hélices e peças quebradas", "Troca de hélices, braços, trem de pouso e peças danificadas em queda ou no transporte.", "/manutencao-de-drones-agricolas", "Técnico trocando a hélice de um drone agrícola"),
    ("diagnostico", "Diagnóstico antes do conserto", "Você recebe o que foi encontrado e o orçamento antes de autorizar qualquer serviço.", "/#como", "Diagnóstico de drone agrícola no computador da oficina"),
    ("capa", "Revisão antes da safra", "Checagem completa na entressafra, para o drone não parar no meio da aplicação.", "/#revisao", "Drone agrícola pulverizando a lavoura de soja"),
]
PASSOS = [
    ("Você chama no WhatsApp", "Conte o modelo do drone e o que está acontecendo. Se puder, mande um vídeo ou a foto do erro no aplicativo."),
    ("Diagnóstico e orçamento", "A gente encontra o defeito e envia o orçamento. Nada é consertado sem a sua aprovação."),
    ("Conserto e teste", "Trocamos o que precisa e testamos o drone e as baterias antes de devolver."),
    ("Volta para o campo", "O drone sai testado e pronto para aplicar, com a lista do que foi feito."),
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
    """O vídeo fica preso na tela e, no scroll, as frases aparecem por cima; no fim ele encolhe e vira um quadro."""
    return f'''<section class="abertura" aria-labelledby="h1"><div class="palco">
<div class="palco__quadro">{video_fundo("vf--abertura")}<div class="palco__veu"></div></div>
<div class="wrap fase fase--1">
{tit("Manutenção de drones agrícolas", "e baterias", "h1", "h1")}
<p class="lead">Drone de pulverização parado no meio da safra custa caro. A Rotor Agro atende todo o Brasil: encontra o defeito, passa o orçamento antes de mexer e devolve o drone pronto para voar.</p>
<div class="ctas">{btn("Chamar no WhatsApp", zap_link("abertura"), "lima", "zap")}{btn("Ver os serviços", "#servicos", "linha")}</div>
</div>
<div class="wrap fase fase--2" aria-hidden="true"><p class="frase">Drone parado na safra <span class="leve">é prejuízo todo dia.</span></p></div>
<div class="wrap fase fase--3" aria-hidden="true"><p class="frase frase--menor">Antes de trocar qualquer peça, <span class="leve">a gente descobre o defeito.</span></p>
<ul class="fatos"><li>Orçamento antes do conserto</li><li>Drone de qualquer revenda</li><li>Atendimento em todo o Brasil</li></ul></div>
<div class="rolar" aria-hidden="true">{o_helice(80, "rolar__o")}<span>role a página</span></div>
</div></section>'''


def servicos():
    cards = "".join(f'''<a class="card" href="{u}" style="--i:{i}"><div class="card__foto">{foto(n, alt, "(max-width:900px) 88vw, 300px")}</div>
<div class="card__txt"><h3>{t}</h3><p>{d}</p><span class="card__mais">Saber mais {SETA}</span></div></a>''' for i, (n, t, d, u, alt) in enumerate(SERVICOS))
    return f'''<section class="secao" id="servicos"><div class="wrap servicos">
<div class="servicos__tit">{tit("O que a gente", "conserta")}<p class="sub">Drone, bateria e sistema de pulverização{", " + REVENDA if REVENDA else ""}. Você manda o problema e a gente diz o que é.</p>{btn("Falar com a oficina", zap_link("servicos"), "escuro", "zap")}</div>
<div class="pilha">{cards}</div></div></section>'''


def como():
    itens = "".join(f'''<li class="passo rv" style="--i:{i}"><div class="passo__o">{o_helice(-i * 45, "passo__svg")}</div><div><span class="passo__n">0{i + 1}</span><h3>{t}</h3><p>{d}</p></div></li>''' for i, (t, d) in enumerate(PASSOS))
    return f'''<section class="secao secao--escura" id="como"><div class="wrap como">
<div class="como__foto rv">{foto("oficina", "Bancada da oficina com um drone agrícola em conserto", "(max-width:900px) 92vw, 560px", (900, 1600), "largo", w=1600, h=1000)}</div>
<div class="como__txt">{tit("Do chamado", "à entrega")}<ol class="passos">{itens}</ol></div>
</div></section>'''


def bateria3d(titulo=True):
    """A bateria em 3D: desenho técnico que vira peça sólida no scroll, com os rótulos do que o teste olha."""
    lis = "".join(f'<li class="rv" style="--i:{i}"><span>0{i + 1}</span><div><b>{t}</b> {d}</div></li>' for i, (t, d) in enumerate(SINAIS))
    rot = [("leds", "Indicadores de carga"), ("celulas", "Células"), ("conector", "Conector"), ("carcaca", "Carcaça")]
    return f'''<section class="b3d" id="baterias"><div class="wrap b3d__in">
<div class="b3d__palco"><canvas class="b3d__tela" aria-label="Bateria de drone agrícola em 3D, desenhada como projeto técnico e depois montada" role="img"></canvas>
{"".join(f'<span class="b3d__rot" data-k="{k}"><i></i>{t}</span>' for k, t in rot)}
<img class="b3d__reserva" src="/assets/img/fotos/bateria-card-720.webp" width="720" height="900" alt="Bateria de drone agrícola em teste na oficina" loading="lazy" decoding="async"></div>
<div class="b3d__txt">{tit("Bateria é a peça que", "mais se gasta") if titulo else ""}
<p class="sub">Cada carga consome um pouco das células. Antes de comprar uma bateria nova, vale testar a que você tem. Três sinais de que ela está no fim:</p>
<ul class="sinais">{lis}</ul>
<div class="ctas">{btn("Testar minhas baterias", zap_link("baterias"), "lima", "zap")}{btn("Como é o teste", "/conserto-de-bateria-de-drone", "linha")}</div></div>
</div></section>'''


def revisao():
    return f'''<section class="faixa" id="revisao"><div class="faixa__foto">{foto("bicos", "", "100vw", (900, 1600), "largo", w=1600, h=1000)}</div><div class="faixa__veu"></div>
<div class="wrap faixa__in">{tit("Revisão", "antes da safra")}
<p class="sub">Na entressafra o drone está parado e a revisão não atrapalha o trabalho. É a hora de trocar o que está gasto, calibrar a pulverização e testar as baterias.</p>
<div class="ctas">{btn("Agendar a revisão", zap_link("revisao"), "lima", "zap")}</div></div></section>'''


def modelos():
    cards = "".join(f'''<figure class="dr"><div class="dr__foto"><img src="/assets/img/drones/{d['slug']}.webp" width="720" height="540" alt="Drone {e(d['nome'])}" loading="lazy" decoding="async"></div>
<figcaption><b>{e(d['nome'].split(' ', 1)[1] if d['nome'].startswith('DJI') else d['nome'].split(' ', 1)[1])}</b><span>{'DJI' if d['nome'].startswith('DJI') else 'XAG'}</span></figcaption></figure>''' for d in DRONES if d["slug"] != "agras-t50-voo")
    outros = [m for m in MODELOS if not any(m.endswith(d["nome"].split(" ", 1)[1]) for d in DRONES)]
    return f'''<section class="secao" id="modelos"><div class="wrap">{tit("Drones que", "a gente atende", cls="tit tit--centro")}
<p class="sub sub--centro">Drones de pulverização da DJI e da XAG{", " + REVENDA if REVENDA else ""}, com as baterias e os carregadores de cada modelo. Também atendemos {", ".join(outros[:-1])} e {outros[-1]}.</p></div>
<div class="vitrine" aria-label="Fotos de alguns drones atendidos"><div class="vitrine__trilho"><div class="vitrine__grupo">{cards}</div><div class="vitrine__grupo" aria-hidden="true">{cards}</div></div></div></section>'''


def home():
    corpo = abertura() + servicos() + como() + bateria3d() + revisao() + modelos() + perguntas_html(FAQ_HOME) + chamada(
        "Mande o modelo", "e o problema", "No WhatsApp a gente responde com o próximo passo e o orçamento.", "final")
    lds = ld(site_ld()) + ld(faq_ld(FAQ_HOME)) + ld(servico_ld("Manutenção de drones agrícolas e baterias", "/", DESC_ORG))
    return pagina("Manutenção de drones agrícolas e baterias | Rotor Agro",
                  "Conserto de drones agrícolas de pulverização e de baterias, com atendimento em todo o Brasil: diagnóstico, orçamento antes do serviço, teste de bateria e revisão antes da safra.",
                  corpo, "/", lds, classe="home", preload='<link rel="preload" as="image" href="/assets/img/lavoura-capa-1600.webp" media="(min-width:701px)" fetchpriority="high"><link rel="preload" as="image" href="/assets/img/lavoura-capa-vertical.webp" media="(max-width:700px)" fetchpriority="high">')


# ------------------------------------------------------------------ páginas de serviço
def cabeca(forte, leve, lead, contexto, migalha, imagem, alt):
    return f'''<section class="cabeca"><div class="cabeca__foto">{foto(imagem, alt, "(max-width:900px) 100vw, 50vw", (900, 1600), "largo", lazy=False, w=1600, h=1000)}</div><div class="cabeca__veu"></div>
<div class="wrap cabeca__in"><nav class="migalha" aria-label="Você está em"><a href="/">Início</a><span aria-hidden="true">/</span><span>{migalha}</span></nav>
{tit(forte, leve, "h1", "h1")}<p class="lead">{lead}</p>
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
    corpo = cabeca("Manutenção de", "drones agrícolas", f"Conserto de drones de pulverização DJI Agras e XAG{', ' + REVENDA if REVENDA else ''}, com atendimento em todo o Brasil. Diagnóstico primeiro, orçamento antes de mexer e teste antes de devolver.", "pagina-drone", "Manutenção de drones agrícolas", "oficina", "Bancada da oficina com um drone agrícola em conserto")
    corpo += f'''<section class="secao"><div class="wrap">{tit("Os defeitos que mais", "chegam na oficina")}{lista_blocos(DEFEITOS_DRONE)}</div></section>'''
    corpo += como() + revisao() + perguntas_html(FAQ_DRONE) + chamada("Seu drone", "está parado?", "Mande o modelo e o que está acontecendo. Um vídeo do erro já ajuda no diagnóstico.", "pagina-drone-final")
    desc = "Conserto de drones agrícolas de pulverização DJI Agras e XAG para todo o Brasil: motores, placas, GPS, radar, bicos e peças. Diagnóstico e orçamento antes do serviço."
    lds = ld(servico_ld("Manutenção de drones agrícolas", "/manutencao-de-drones-agricolas", desc)) + ld(faq_ld(FAQ_DRONE)) + ld(migalhas_ld([("Início", "/"), ("Manutenção de drones agrícolas", "/manutencao-de-drones-agricolas")]))
    return pagina("Manutenção de drones agrícolas DJI Agras e XAG | Rotor Agro", desc, corpo, "/manutencao-de-drones-agricolas", lds)


TESTE_BATERIA = [
    ("bateria", "Saúde da bateria", "Quanto da capacidade original ela ainda guarda, em porcentagem."),
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
    corpo = cabeca("Teste e conserto de", "bateria de drone", "Antes de comprar uma bateria nova, descubra quanto ainda resta da que você tem. Teste de saúde, equilíbrio das células e avaliação de bateria com erro.", "pagina-bateria", "Bateria de drone", "bateria", "Bateria de drone agrícola sendo testada com multímetro")
    corpo += f'''<section class="secao"><div class="wrap">{tit("O que o teste", "mostra")}{lista_blocos(TESTE_BATERIA, "blocos blocos--4")}</div></section>'''
    corpo += bateria3d(titulo=True) + perguntas_html(FAQ_BATERIA) + chamada("Baterias", "durando pouco?", "Mande quantas baterias são e o modelo do drone. A gente combina o teste.", "pagina-bateria-final")
    desc = "Teste e conserto de bateria de drone agrícola DJI Agras e XAG, com atendimento em todo o Brasil: saúde, equilíbrio das células, ciclos, carregador e bateria com erro."
    lds = ld(servico_ld("Teste e conserto de bateria de drone agrícola", "/conserto-de-bateria-de-drone", desc)) + ld(faq_ld(FAQ_BATERIA)) + ld(migalhas_ld([("Início", "/"), ("Bateria de drone", "/conserto-de-bateria-de-drone")]))
    return pagina("Teste e conserto de bateria de drone agrícola | Rotor Agro", desc, corpo, "/conserto-de-bateria-de-drone", lds)
