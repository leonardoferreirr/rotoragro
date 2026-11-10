/* Rotor Agro: topo, entradas no scroll, vídeos, abertura em fases, bateria 3D e vitrine dos drones */
(function () {
  var d = document, raiz = d.documentElement;
  var reduz = window.matchMedia && matchMedia('(prefers-reduced-motion: reduce)').matches;
  var celular = window.matchMedia && matchMedia('(max-width:700px)').matches;
  var est = function (a, b, x) { return Math.min(1, Math.max(0, (x - a) / (b - a))); };

  var topo = d.querySelector('.topo'), zapf = d.querySelector('.zapf'), ab = d.querySelector('.abertura');
  function rolou() {
    var y = window.scrollY || 0, limite = ab ? (ab.offsetHeight - innerHeight) * 0.84 : 10;
    if (topo) topo.classList.toggle('solido', y > limite);
    if (zapf) zapf.classList.toggle('mostra', y > (ab ? ab.offsetHeight - innerHeight * 0.6 : innerHeight * 0.8));
  }
  addEventListener('scroll', rolou, { passive: true }); rolou();

  var temIO = 'IntersectionObserver' in window;
  if (temIO) {
    var io = new IntersectionObserver(function (es) {
      es.forEach(function (en) { if (en.isIntersecting) { en.target.classList.add('vis'); io.unobserve(en.target); } });
    }, { rootMargin: '0px 0px -8% 0px' });
    d.querySelectorAll('.rv').forEach(function (el) { io.observe(el); });
    var vo = new IntersectionObserver(function (es) { es.forEach(function (en) { en.target.classList.toggle('vis', en.isIntersecting); }); });
    d.querySelectorAll('.vitrine').forEach(function (el) { vo.observe(el); });
  } else {
    d.querySelectorAll('.rv,.vitrine').forEach(function (el) { el.classList.add('vis'); });
  }

  // vídeos: a capa já está na tela; o vídeo só entra depois do load e quando a área aparece
  function ligaVideos() {
    if (reduz) return;
    d.querySelectorAll('.vf').forEach(function (vf) {
      var v = vf.querySelector('video'), carregado = false;
      v.addEventListener('playing', function () { vf.classList.add('tocando'); });
      function toca(sim) {
        if (sim) {
          if (!carregado) { v.src = celular ? vf.getAttribute('data-video-cel') : vf.getAttribute('data-video-desk'); carregado = true; }
          var pr = v.play(); if (pr && pr.catch) pr.catch(function () {});
        } else if (carregado) v.pause();
      }
      if (temIO) new IntersectionObserver(function (es) { toca(es[0].isIntersecting); }, { rootMargin: '200px 0px' }).observe(vf);
      else toca(true);
    });
  }

  // abertura em fases: título, primeira frase, segunda frase com os fatos, e o vídeo vira um quadro
  function ligaAbertura() {
    if (!ab || reduz) return;
    var pendente = false;
    function fases() {
      pendente = false;
      var total = ab.offsetHeight - innerHeight, p = total > 0 ? Math.min(1, Math.max(0, -ab.getBoundingClientRect().top / total)) : 0;
      var s = ab.style;
      s.setProperty('--s1', est(0.02, 0.16, p).toFixed(3));
      s.setProperty('--f2', (est(0.17, 0.27, p) * (1 - est(0.42, 0.5, p))).toFixed(3));
      s.setProperty('--f3', (est(0.5, 0.62, p) * (1 - est(0.84, 0.9, p))).toFixed(3));
      s.setProperty('--m', est(0.86, 1, p).toFixed(3));
      s.setProperty('--z', (1.06 - 0.06 * p).toFixed(4));
    }
    addEventListener('scroll', function () { if (!pendente) { pendente = true; requestAnimationFrame(fases); } }, { passive: true });
    addEventListener('resize', fases); fases();
  }

  // bateria 3D: o módulo (three.js) só baixa quando a seção chega perto
  function ligaBateria() {
    var sec = d.querySelector('.b3d'); if (!sec) return;
    var palco = sec.querySelector('.b3d__palco'), tela = sec.querySelector('.b3d__tela');
    var rot = [].slice.call(sec.querySelectorAll('.b3d__rot'));
    var api = null, visivel = false, rodando = false, ult = 0, pedido = false;
    function progresso() {
      var r;
      if (getComputedStyle(palco).position === 'sticky') {
        r = sec.getBoundingClientRect();
        return Math.min(1, Math.max(0, (innerHeight * 0.15 - r.top) / (r.height - innerHeight)));
      }
      r = palco.getBoundingClientRect();
      return Math.min(1, Math.max(0, (innerHeight * 0.9 - r.top) / (innerHeight * 0.9 + r.height * 0.45)));
    }
    function quadro(t) {
      var dt = ult ? Math.min(0.05, (t - ult) / 1000) : 0.016; ult = t;
      var p = reduz ? 1 : progresso(), pos = api.progresso(p, dt), mostra = p > 0.8;
      rot.forEach(function (el) {
        var k = el.getAttribute('data-k'), xy = pos[k]; if (!xy) return;
        var dir = k === 'carcaca', dy = k === 'leds' ? -34 : (k === 'conector' ? 30 : 0);
        el.style.transform = 'translate(' + Math.round(dir ? xy[0] + 16 : xy[0] - el.offsetWidth - 16) + 'px,' + Math.round(xy[1] - el.offsetHeight / 2 + dy) + 'px)';
        el.style.opacity = mostra ? 1 : 0;
      });
      if (visivel) requestAnimationFrame(quadro); else { rodando = false; ult = 0; }
    }
    function liga() { if (api && !rodando) { rodando = true; requestAnimationFrame(quadro); } }
    function carrega() {
      if (pedido) return; pedido = true;
      import(sec.getAttribute('data-modulo') || d.body.getAttribute('data-b3d')).then(function (m) {
        try { api = m.montar(tela, { dprMax: celular ? 1.5 : 1.75 }); liga(); }
        catch (e) { sec.classList.add('sem3d'); }
      }).catch(function () { sec.classList.add('sem3d'); });
    }
    if (!temIO) { carrega(); visivel = true; return; }
    new IntersectionObserver(function (es) { if (es[0].isIntersecting) carrega(); }, { rootMargin: '120% 0px' }).observe(sec);
    new IntersectionObserver(function (es) { visivel = es[0].isIntersecting; if (visivel) liga(); }).observe(palco);
  }

  function comeca() { ligaVideos(); ligaBateria(); }
  ligaAbertura();
  if (d.readyState === 'complete') comeca(); else addEventListener('load', comeca);
})();
