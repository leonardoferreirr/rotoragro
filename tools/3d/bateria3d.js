// Bateria de drone agrícola em 3D: começa como desenho técnico (linhas verdes traçando a peça)
// e vira a bateria sólida conforme o scroll; no fim os indicadores de carga acendem um por um.
// Exporta montar(canvas, opcoes) e devolve { progresso(p), destruir() }.
import {
  WebGLRenderer, Scene, PerspectiveCamera, Group, Mesh, Shape, ExtrudeGeometry, BoxGeometry, TubeGeometry,
  CatmullRomCurve3, Vector3, MeshStandardMaterial, LineBasicMaterial, LineSegments, BufferGeometry,
  Float32BufferAttribute, EdgesGeometry, HemisphereLight, DirectionalLight, Color, SRGBColorSpace,
} from 'three';

const LIMA = new Color('#B9DE4F'), BEGE = new Color('#F0EADB');

function caixaArredondada(l, a, p, r) {
  const s = new Shape(), x = -l / 2, y = -a / 2;
  s.moveTo(x + r, y); s.lineTo(x + l - r, y); s.quadraticCurveTo(x + l, y, x + l, y + r);
  s.lineTo(x + l, y + a - r); s.quadraticCurveTo(x + l, y + a, x + l - r, y + a);
  s.lineTo(x + r, y + a); s.quadraticCurveTo(x, y + a, x, y + a - r);
  s.lineTo(x, y + r); s.quadraticCurveTo(x, y, x + r, y);
  const b = 0.05;
  const g = new ExtrudeGeometry(s, { depth: p - 2 * b, bevelEnabled: true, bevelSize: b, bevelThickness: b, bevelSegments: 2, curveSegments: 6 });
  g.translate(0, 0, -(p - 2 * b) / 2);
  return g;
}

export function montar(canvas, op = {}) {
  const dpr = Math.min(window.devicePixelRatio || 1, op.dprMax || 1.75);
  const r = new WebGLRenderer({ canvas, antialias: true, alpha: true, powerPreference: 'low-power' });
  r.setPixelRatio(dpr); r.outputColorSpace = SRGBColorSpace;
  const cena = new Scene();
  const cam = new PerspectiveCamera(28, 1, 0.1, 50); cam.position.set(0, 0.55, 7.4); cam.lookAt(0, 0.05, 0);
  cena.add(new HemisphereLight(0xf4f1ea, 0x2a2c2e, 1.5));
  const sol = new DirectionalLight(0xffe2b0, 2.8); sol.position.set(3, 4, 5); cena.add(sol);
  const recorte = new DirectionalLight(0xb9de4f, 0.6); recorte.position.set(-4, 1.5, -3); cena.add(recorte);

  const peca = new Group(); cena.add(peca);
  const corpoMat = new MeshStandardMaterial({ color: 0x4b4f55, roughness: 0.48, metalness: 0.22, transparent: true, opacity: 0 });
  const frenteMat = new MeshStandardMaterial({ color: 0x34383d, roughness: 0.6, metalness: 0.15, transparent: true, opacity: 0 });
  const metalMat = new MeshStandardMaterial({ color: 0x8c918e, roughness: 0.35, metalness: 0.8, transparent: true, opacity: 0 });
  const ledMat = [];
  const partes = [];
  function add(geo, mat, x = 0, y = 0, z = 0) { const m = new Mesh(geo, mat); m.position.set(x, y, z); peca.add(m); partes.push(m); return m; }

  const L = 1.7, A = 2.05, P = 1.15;
  add(caixaArredondada(L, A, P, 0.16), corpoMat);
  add(caixaArredondada(1.28, 1.42, 0.06, 0.08), frenteMat, 0, -0.08, P / 2 + 0.01);
  for (let i = -2; i <= 2; i++) add(new BoxGeometry(0.05, 1.5, 0.05), frenteMat, L / 2 + 0.01, -0.05, i * 0.16);   // frisos da lateral
  for (let i = -2; i <= 2; i++) add(new BoxGeometry(0.05, 1.5, 0.05), frenteMat, -L / 2 - 0.01, -0.05, i * 0.16);
  const alca = new CatmullRomCurve3([new Vector3(-0.5, A / 2 - 0.02, 0), new Vector3(-0.45, A / 2 + 0.3, 0), new Vector3(0, A / 2 + 0.42, 0), new Vector3(0.45, A / 2 + 0.3, 0), new Vector3(0.5, A / 2 - 0.02, 0)]);
  add(new TubeGeometry(alca, 40, 0.075, 10, false), corpoMat);
  add(new BoxGeometry(0.62, 0.2, 0.34), metalMat, 0, -A / 2 - 0.02, P / 2 - 0.12);   // conector
  add(new BoxGeometry(0.16, 0.16, 0.03), frenteMat, 0.42, 0.5, P / 2 + 0.05);       // botão
  for (let i = 0; i < 4; i++) {
    const m = new MeshStandardMaterial({ color: 0x1b211f, emissive: 0x000000, roughness: 0.4, transparent: true, opacity: 0 });
    ledMat.push(m); add(new BoxGeometry(0.13, 0.05, 0.03), m, -0.42 + i * 0.19, 0.5, P / 2 + 0.05);
  }

  // as linhas do desenho: todas as arestas juntas, ordenadas de cima para baixo, para "traçar" a peça
  peca.updateMatrixWorld(true);
  const segs = [];
  for (const m of partes) {
    const e = new EdgesGeometry(m.geometry, 28); const pos = e.attributes.position;
    for (let i = 0; i < pos.count; i += 2) {
      const a = new Vector3().fromBufferAttribute(pos, i).applyMatrix4(m.matrixWorld);
      const b = new Vector3().fromBufferAttribute(pos, i + 1).applyMatrix4(m.matrixWorld);
      segs.push([a, b, Math.max(a.y, b.y) + (a.x + b.x) * 0.04]);
    }
  }
  segs.sort((s, t) => t[2] - s[2]);
  const arr = new Float32Array(segs.length * 6);
  segs.forEach((s, i) => { arr.set([s[0].x, s[0].y, s[0].z, s[1].x, s[1].y, s[1].z], i * 6); });
  const linhasGeo = new BufferGeometry(); linhasGeo.setAttribute('position', new Float32BufferAttribute(arr, 3));
  const linhasMat = new LineBasicMaterial({ color: LIMA, transparent: true, opacity: 0.95 });
  const linhas = new LineSegments(linhasGeo, linhasMat); peca.add(linhas);

  // cotas, como num desenho técnico
  const cotaArr = [];
  const c = (x1, y1, z1, x2, y2, z2) => cotaArr.push(x1, y1, z1, x2, y2, z2);
  const yb = -A / 2 - 0.32, xd = L / 2 + 0.34;
  c(-L / 2, yb, P / 2, L / 2, yb, P / 2); c(-L / 2, yb - 0.07, P / 2, -L / 2, yb + 0.07, P / 2); c(L / 2, yb - 0.07, P / 2, L / 2, yb + 0.07, P / 2);
  c(xd, -A / 2, P / 2, xd, A / 2, P / 2); c(xd - 0.07, -A / 2, P / 2, xd + 0.07, -A / 2, P / 2); c(xd - 0.07, A / 2, P / 2, xd + 0.07, A / 2, P / 2);
  const cotaGeo = new BufferGeometry(); cotaGeo.setAttribute('position', new Float32BufferAttribute(cotaArr, 3));
  const cotaMat = new LineBasicMaterial({ color: BEGE, transparent: true, opacity: 0 });
  peca.add(new LineSegments(cotaGeo, cotaMat));

  // pontos que recebem os rótulos em HTML
  const ancoras = {
    leds: new Vector3(-0.13, 0.5, P / 2 + 0.06), celulas: new Vector3(0, -0.35, P / 2 + 0.02),
    conector: new Vector3(0.2, -A / 2 - 0.08, P / 2 + 0.02), carcaca: new Vector3(L / 2 + 0.02, 0.35, 0.2),
  };

  let p = 0, giro = 0, w = 0, h = 0, vivo = true;
  const est = (a, b, x) => Math.min(1, Math.max(0, (x - a) / (b - a)));
  function tamanho() {
    const nw = canvas.clientWidth, nh = canvas.clientHeight;
    if (nw !== w || nh !== h) { w = nw; h = nh; r.setSize(w, h, false); cam.aspect = w / h; cam.updateProjectionMatrix(); }
  }
  function desenha(dt = 0) {
    if (!vivo) return;
    tamanho();
    giro += dt * 0.12;
    const traco = est(0.02, 0.5, p), solido = est(0.42, 0.72, p), cargas = est(0.74, 0.96, p);
    linhasGeo.setDrawRange(0, Math.floor(segs.length * traco) * 2);
    linhasMat.opacity = 0.95 - 0.7 * solido;
    cotaMat.opacity = 0.6 * Math.min(traco * 1.5, 1) * (1 - solido);
    for (const m of [corpoMat, frenteMat, metalMat]) m.opacity = solido;
    ledMat.forEach((m, i) => {
      m.opacity = solido; const on = cargas > (i + 0.5) / 4;
      m.emissive.set(on ? 0x8fd14f : 0x000000); m.emissiveIntensity = on ? 1.6 : 0;
    });
    peca.rotation.y = -0.75 + p * 1.15 + Math.sin(giro) * 0.04;
    peca.rotation.x = 0.06;
    r.render(cena, cam);
  }
  function rotulos() {
    const out = {};
    for (const k in ancoras) {
      const v = ancoras[k].clone().applyMatrix4(peca.matrixWorld).project(cam);
      out[k] = [(v.x + 1) / 2 * w, (1 - v.y) / 2 * h];
    }
    return out;
  }
  return {
    progresso(np, dt) { p = np; desenha(dt); return rotulos(); },
    destruir() { vivo = false; r.dispose(); },
  };
}
