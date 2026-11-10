/* Rotor Agro: topo, entradas no scroll, fita de modelos e a abertura do drone */
(function () {
  var d = document, reduz = window.matchMedia && matchMedia('(prefers-reduced-motion: reduce)').matches;

  var topo = d.querySelector('.topo'), zapf = d.querySelector('.zapf'), ab = d.querySelector('.abertura');
  function rolou() {
    var y = window.scrollY || 0;
    if (topo) topo.classList.toggle('rolou', y > 10);
    if (zapf) zapf.classList.toggle('mostra', y > (ab ? ab.offsetHeight - innerHeight * 0.4 : innerHeight * 0.8));
  }
  addEventListener('scroll', rolou, { passive: true }); rolou();

  if ('IntersectionObserver' in window) {
    var io = new IntersectionObserver(function (es) {
      es.forEach(function (en) { if (en.isIntersecting) { en.target.classList.add('vis'); io.unobserve(en.target); } });
    }, { rootMargin: '0px 0px -8% 0px' });
    d.querySelectorAll('.rv').forEach(function (el) { io.observe(el); });
    var fo = new IntersectionObserver(function (es) { es.forEach(function (en) { en.target.classList.toggle('vis', en.isIntersecting); }); });
    d.querySelectorAll('.fita').forEach(function (el) { fo.observe(el); });
  } else {
    d.querySelectorAll('.rv,.fita').forEach(function (el) { el.classList.add('vis'); });
  }

  // abertura: os braços abrem conforme o scroll e as hélices aceleram
  if (!ab) return;
  var svg = ab.querySelector('svg.drone');
  var B = [].slice.call(svg.querySelectorAll('.d-braco')).map(function (el) {
    return { el: el, px: +el.getAttribute('data-px'), py: +el.getAttribute('data-py'), a0: +el.getAttribute('data-a0'), a1: +el.getAttribute('data-a1'), dob: el.querySelector('.d-dobrada') };
  });
  var H = [].slice.call(svg.querySelectorAll('.d-helice')).map(function (el) {
    return { el: el, gira: el.querySelector('.d-gira'), rastro: el.querySelector('.d-rastro') };
  });
  var COMP = 300, sentido = [1, -1, -1, 1], ang = [0, 45, 90, 135];
  var alvo = 0, p = 0, visivel = true, ult = 0, rodando = false;
  function ease(t) { return t < 0.5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2; }
  function medir() {
    var total = ab.offsetHeight - innerHeight;
    alvo = total > 0 ? Math.min(1, Math.max(0, -ab.getBoundingClientRect().top / (total * 0.72))) : 1;
  }
  function desenha(dt) {
    p += (alvo - p) * Math.min(1, dt * 7);
    var e = ease(p);
    for (var i = 0; i < B.length; i++) {
      var b = B[i], h = H[i], a = b.a0 + (b.a1 - b.a0) * e, r = a * Math.PI / 180;
      b.el.setAttribute('transform', 'translate(' + b.px + ' ' + b.py + ') rotate(' + a.toFixed(2) + ')');
      var x = b.px + COMP * Math.cos(r), y = b.py + COMP * Math.sin(r), s = 0.3 + 0.7 * e;
      h.el.setAttribute('transform', 'translate(' + x.toFixed(1) + ' ' + y.toFixed(1) + ') scale(' + s.toFixed(3) + ')');
      ang[i] = (ang[i] + sentido[i] * (50 + 1150 * e) * dt) % 360;
      h.gira.setAttribute('transform', 'rotate(' + ang[i].toFixed(1) + ')');
      b.dob.style.opacity = Math.max(0, 1 - e * 3).toFixed(2);
      h.rastro.style.strokeOpacity = Math.max(0, (e - 0.55) * 0.8).toFixed(2);
    }
  }
  function quadro(t) {
    var dt = ult ? Math.min(0.05, (t - ult) / 1000) : 0.016; ult = t;
    desenha(dt);
    if (visivel) requestAnimationFrame(quadro); else { rodando = false; ult = 0; }
  }
  function liga() { if (!rodando) { rodando = true; requestAnimationFrame(quadro); } }
  if (reduz) { alvo = 1; p = 1; desenha(0); return; }
  function comeca() {
    addEventListener('scroll', medir, { passive: true }); addEventListener('resize', medir); medir();
    if ('IntersectionObserver' in window) new IntersectionObserver(function (es) { visivel = es[0].isIntersecting; if (visivel) liga(); }).observe(ab);
    liga();
  }
  // o giro só começa depois do load, para não disputar com a primeira pintura
  if (d.readyState === 'complete') comeca(); else addEventListener('load', comeca);
})();
