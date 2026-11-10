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
      if (!v) return;
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
  // quadros do vídeo da abertura: baixam em passadas (primeiro espalhados, depois o resto) e o scroll escolhe qual desenhar
  var quadros = null;
  function ligaQuadros() {
    var vf = ab && ab.querySelector('.vf--abertura'); if (!vf || reduz) return;
    var tela = vf.querySelector('canvas'), cx = tela.getContext('2d'), n = +vf.getAttribute('data-n');
    var base = vf.getAttribute(celular ? 'data-quadros-m' : 'data-quadros-d'), img = new Array(n), ok = new Array(n), alvo = 0, atual = '', w = 0, h = 0;
    function mede() {
      var r = Math.min(window.devicePixelRatio || 1, celular ? 2 : 1.5), nw = Math.round(tela.clientWidth * r), nh = Math.round(tela.clientHeight * r);
      if (nw !== w || nh !== h) { w = tela.width = nw; h = tela.height = nh; atual = ''; }
    }
    function perto(i) { for (var dlt = 0; dlt < n; dlt++) { if (ok[i - dlt]) return i - dlt; if (ok[i + dlt]) return i + dlt; } return -1; }
    function pinta(im, alfa) {
      var e = Math.max(w / im.naturalWidth, h / im.naturalHeight), iw = im.naturalWidth * e, ih = im.naturalHeight * e;
      cx.globalAlpha = alfa; cx.drawImage(im, (w - iw) / 2, (h - ih) * 0.6, iw, ih);
    }
    // mistura o quadro de agora com o seguinte na proporção exata do scroll: sem degrau entre um quadro e outro
    function desenha() {
      var f = alvo * (n - 1), a = Math.floor(f), b = Math.min(n - 1, a + 1), t = f - a;
      if (!ok[a] || !ok[b]) { a = b = perto(Math.round(f)); t = 0; }
      if (a < 0) return;
      var chave = a + ':' + b + ':' + t.toFixed(3);
      if (chave === atual) return;
      mede(); pinta(img[a], 1); if (b !== a && t > 0.01) pinta(img[b], t); cx.globalAlpha = 1; atual = chave;
      if (!vf.classList.contains('pronto')) vf.classList.add('pronto');
    }
    var ordem = [], vistos = {};
    [16, 8, 4, 2, 1].forEach(function (passo) { for (var i = 0; i < n; i += passo) if (!vistos[i]) { vistos[i] = 1; ordem.push(i); } });
    if (!vistos[n - 1]) ordem.push(n - 1);
    var pos = 0, ativos = 0;
    function proximo() {
      while (ativos < 6 && pos < ordem.length) {
        (function (i) {
          ativos++; var im = new Image(); im.decoding = 'async';
          im.onload = function () { ok[i] = 1; img[i] = im; ativos--; atual = ''; requestAnimationFrame(desenha); proximo(); };
          im.onerror = function () { ativos--; proximo(); };
          im.src = base + ('00' + i).slice(-3) + '.webp';
        })(ordem[pos++]);
      }
    }
    addEventListener('resize', function () { w = 0; atual = ''; requestAnimationFrame(desenha); });
    quadros = { vai: function (t) { alvo = t; desenha(); }, comeca: proximo };
  }

  function ligaAbertura() {
    if (!ab || reduz) return;
    var alvoP = 0, p = -1, rodando = false, ult = 0;
    function lePosicao() {
      var total = ab.offsetHeight - innerHeight;
      alvoP = total > 0 ? Math.min(1, Math.max(0, -ab.getBoundingClientRect().top / total)) : 0;
    }
    function aplica() {
      var s = ab.style;
      s.setProperty('--s1', est(0.02, 0.15, p).toFixed(4));
      s.setProperty('--f2', (est(0.17, 0.27, p) * (1 - est(0.42, 0.5, p))).toFixed(4));
      s.setProperty('--f3', (est(0.5, 0.62, p) * (1 - est(0.84, 0.9, p))).toFixed(4));
      s.setProperty('--m', est(0.86, 1, p).toFixed(4));
      if (quadros) quadros.vai(est(0, 0.86, p));
    }
    function quadro(t) {
      var dt = ult ? Math.min(0.05, (t - ult) / 1000) : 0.016; ult = t;
      if (p < 0) p = alvoP;
      p += (alvoP - p) * (1 - Math.exp(-dt * 7.5));
      if (Math.abs(alvoP - p) < 0.0004) p = alvoP;
      aplica();
      if (p !== alvoP) requestAnimationFrame(quadro); else { rodando = false; ult = 0; }
    }
    function anda() { lePosicao(); if (!rodando) { rodando = true; requestAnimationFrame(quadro); } }
    addEventListener('scroll', anda, { passive: true });
    addEventListener('resize', anda);
    lePosicao(); p = alvoP; aplica();
  }

  // bateria 3D: o módulo (three.js) só baixa quando a seção chega perto
  function ligaBateria() {
    var sec = d.querySelector('.b3d'); if (!sec) return;
    var palco = sec.querySelector('.b3d__palco'), tela = sec.querySelector('.b3d__tela');
    var rot = [].slice.call(sec.querySelectorAll('.b3d__rot'));
    var api = null, visivel = false, rodando = false, ult = 0, pedido = false;
    function progresso() {
      var r = (getComputedStyle(palco).position === 'sticky' ? sec : palco).getBoundingClientRect();
      return Math.min(1, Math.max(0, (innerHeight * 0.9 - r.top) / (innerHeight * 1.15)));
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

  function comeca() { ligaVideos(); ligaBateria(); if (quadros) quadros.comeca(); }
  ligaQuadros(); ligaAbertura();
  if (d.readyState === 'complete') comeca(); else addEventListener('load', comeca);
})();
