"""O drone da abertura, visto de cima, em SVG. Os braços dobrados abrem com o scroll e cada hélice é o O da marca.

Coordenadas com o centro em (0, 0), frente para cima. Os ângulos dos braços ficam em data-*,
e o site.js só gira os grupos: nada é redesenhado durante o scroll.
"""
import math
import pathops

VE, VM, LI, BE = "#0F3226", "#1F7A4D", "#B9DE4F", "#F0EADB"


def _poly(conts):
    p = pathops.Path(); pen = p.getPen()
    for c in conts:
        pen.moveTo(c[0])
        for q in c[1:]: pen.lineTo(q)
        pen.closePath()
    return p


def _circ(r, n=180, sentido=1):
    return [(r * math.cos(sentido * 2 * math.pi * i / n), r * math.sin(sentido * 2 * math.pi * i / n)) for i in range(n)]


def _d(path):
    out = []
    for verb, pts in path.segments:
        if verb == "moveTo": out.append("M%.1f %.1f" % pts[0])
        elif verb == "lineTo": out.append("L%.1f %.1f" % pts[0])
        elif verb == "closePath": out.append("Z")
    return "".join(out)


def o_circular(r_ext=100, r_int=64, rot=80, curva=1.2, n=160):
    """O O da marca em versão circular (hélice vista de cima): por dentro a espessura cresce em volta do centro, em duas pás."""
    anel = pathops.simplify(_poly([_circ(r_ext), _circ(r_int, sentido=-1)]), fix_winding=True)
    for k in range(2):
        th0 = math.radians(rot) + k * math.pi
        vao = math.pi * 0.97
        pts = [(0.0, 0.0)]
        for i in range(n + 1):
            th = th0 + vao * i / n
            t = (i / n) ** curva
            r = r_int + (r_ext - r_int) * (1 - t) + 0.4 * (1 - t)
            pts.append((r * math.cos(th), -r * math.sin(th)))  # y para baixo no SVG
        anel = pathops.op(anel, _poly([pts]), pathops.PathOp.DIFFERENCE)
    return _d(pathops.simplify(anel))


O_HELICE = o_circular()

# braços: pivô, ângulo dobrado e ângulo aberto (graus, 0 = direita, sentido horário porque o y do SVG desce)
BRACOS = [
    ("fd", (96, -118), -80, -42),
    ("fe", (-96, -118), -100, -138),
    ("td", (96, 118), 80, 42),
    ("te", (-96, 118), 100, 138),
]
COMP = 300          # do pivô ao centro do motor
R_HELICE = 150      # raio da hélice aberta


def svg(classe="drone"):
    grade = "".join(f'<path d="M{x} -500V500"/>' for x in range(-450, 451, 50)) + "".join(f'<path d="M-500 {y}H500"/>' for y in range(-450, 451, 50))
    corpo = f'''<g class="d-corpo">
<rect x="-112" y="-172" width="224" height="344" rx="48" fill="{VE}" stroke="{BE}" stroke-width="3"/>
<rect x="-78" y="-124" width="156" height="176" rx="30" fill="none" stroke="{BE}" stroke-opacity=".55" stroke-width="2.5"/>
<path d="M-50 -124V52M0 -124V52M50 -124V52" stroke="{BE}" stroke-opacity=".18" stroke-width="2"/>
<rect x="-58" y="82" width="116" height="62" rx="12" fill="none" stroke="{BE}" stroke-opacity=".55" stroke-width="2.5"/>
<path d="M-24 113H24" stroke="{LI}" stroke-width="5" stroke-linecap="round"/>
<path d="M-46 -188Q0 -206 46 -188" fill="none" stroke="{BE}" stroke-width="3" stroke-linecap="round"/>
<circle r="7" cy="-150" fill="{LI}"/>
</g>'''
    bracos, helices = [], []
    for nome, (px, py), a0, a1 in BRACOS:
        bracos.append(f'''<g class="d-braco" data-px="{px}" data-py="{py}" data-a0="{a0}" data-a1="{a1}" transform="translate({px} {py}) rotate({a0})">
<rect x="-14" y="-15" width="{COMP + 14}" height="30" rx="15" fill="{VE}" stroke="{BE}" stroke-width="3"/>
<circle cx="0" cy="0" r="17" fill="{VE}" stroke="{BE}" stroke-width="3"/>
<circle cx="{COMP}" cy="0" r="30" fill="{VE}" stroke="{BE}" stroke-width="3"/>
<path class="d-dobrada" d="M{COMP - 6} -5L{COMP - 190} -15M{COMP - 6} 5L{COMP - 190} 15" stroke="{BE}" stroke-opacity=".8" stroke-width="5" stroke-linecap="round"/>
</g>''')
        x0 = px + COMP * math.cos(math.radians(a0)); y0 = py + COMP * math.sin(math.radians(a0))
        helices.append(f'''<g class="d-helice" transform="translate({x0:.1f} {y0:.1f}) scale(.3)"><circle r="{R_HELICE + 10}" class="d-rastro" fill="none" stroke="{BE}" stroke-opacity="0" stroke-width="2" stroke-dasharray="4 10"/><g class="d-gira"><use href="#o-helice" fill="{LI}" transform="scale(1.5)"/></g></g>''')
    return f'''<svg class="{classe}" viewBox="-500 -500 1000 1000" role="img" aria-label="Drone agrícola visto de cima, com os braços abrindo e as hélices girando">
<g class="d-grade" stroke="{BE}" stroke-opacity=".07" stroke-width="1">{grade}</g>
<path d="M0 -480V480M-480 0H480" stroke="{BE}" stroke-opacity=".14" stroke-width="1.5" stroke-dasharray="10 12"/>
{"".join(bracos)}{corpo}{"".join(helices)}
</svg>'''
