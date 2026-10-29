// トップの本文(2026-10-29、試作 v4 を本番化): ペン画の地図・相談票・入場の動き。
// 相談票の印は、申し込みの用紙で送信するまでどこにも送られない(consult-sheet.js)。
document.addEventListener('DOMContentLoaded', () => {
// ---- ペン画の地図(等高線の地面、ペン画の木、公図のような注記) ----
(function () {
  const svg = document.getElementById('map'), NS = 'http://www.w3.org/2000/svg';
  let seed = 11; const rnd = () => (seed = (seed * 9301 + 49297) % 233280) / 233280;
  const el = (n, a, p = svg) => { const e = document.createElementNS(NS, n); for (const k in a) e.setAttribute(k, a[k]); p.appendChild(e); return e; };
  // 等高線の地面(5 本ごとに太い計曲線)
  const cg = el('g', { fill: 'none', stroke: '#23211d', opacity: .5 });
  [[470, 250, 10], [990, 100, 6], [80, 580, 5]].forEach(([cx, cy, n]) => {
    for (let k = 1; k <= n; k++) {
      const pts = [];
      for (let a = 0; a < 72; a++) { const t = a / 72 * Math.PI * 2, r = k * 44 * (1 + .14 * Math.sin(3 * t + k * .7) + .07 * Math.sin(5 * t + cx));
        pts.push(`${(cx + Math.cos(t) * r * 1.4).toFixed(1)} ${(cy + Math.sin(t) * r).toFixed(1)}`); }
      el('path', { d: 'M' + pts.join(' L') + ' Z', 'stroke-width': k % 5 ? .6 : 1.2 }, cg);
    }
  });
  // 林道(白く抜く 2 本線)
  const road = 'M -20 470 C 180 420, 300 520, 470 470 S 760 330, 900 360 S 1060 430, 1130 400';
  el('path', { d: road, fill: 'none', stroke: '#f4f2eb', 'stroke-width': 34 });
  el('path', { d: road, fill: 'none', stroke: '#23211d', 'stroke-width': 36, 'stroke-opacity': 1, 'stroke-dasharray': 'none', style: 'mix-blend-mode:normal', opacity: 0 });
  const edge = (dy) => el('path', { d: road, fill: 'none', stroke: '#23211d', 'stroke-width': 1, transform: `translate(0 ${dy})` });
  edge(-17); edge(17);
  // 沢(点線)
  el('path', { d: 'M 640 0 C 620 90, 690 160, 650 250 S 600 360, 640 420', fill: 'none', stroke: '#23211d', 'stroke-width': 1, 'stroke-dasharray': '2 6' });
  // 境界(区画)
  const lot = 'M 330 90 L 600 70 L 640 250 L 610 400 L 360 420 L 300 260 Z';
  el('path', { d: lot, fill: '#f4f2eb', 'fill-opacity': .6, stroke: '#a8382a', 'stroke-width': 2.2 });
  el('path', { d: 'M 600 70 L 860 110 L 880 300 L 640 250', fill: 'none', stroke: '#23211d', 'stroke-width': 1, 'stroke-dasharray': '7 5' });
  el('path', { d: 'M 330 90 L 120 130 L 90 330 L 300 260', fill: 'none', stroke: '#23211d', 'stroke-width': 1, 'stroke-dasharray': '7 5' });
  // 境界杭
  [[330, 90], [600, 70], [640, 250], [610, 400], [360, 420], [300, 260]].forEach(([x, y]) => { el('rect', { x: x - 4, y: y - 4, width: 8, height: 8, fill: '#f4f2eb', stroke: '#23211d', 'stroke-width': 1 }); });
  // ペン画の杉
  const tree = (x, y, s) => { const g = el('g', { transform: `translate(${x} ${y}) scale(${s})`, stroke: '#23211d', 'stroke-width': 1.1, fill: 'none', 'stroke-linecap': 'round' });
    el('path', { d: 'M0 -62 V6' }, g);
    for (let i = 0; i < 13; i++) { const yy = -56 + i * 4.6, w = 3 + i * 1.25; el('path', { d: `M0 ${yy} l${-w} ${3 + i * .15} M0 ${yy} l${w} ${3 + i * .15}` }, g); } };
  const inside = (x, y) => x > 290 && x < 650 && y > 60 && y < 430;
  const onRoad = (x, y) => { const t = x / 1100; const ry = 470 - 120 * Math.sin(t * Math.PI * 1.1); return Math.abs(y - ry) < 70; };
  const pts = [];
  for (let i = 0; i < 400 && pts.length < 54; i++) { const x = 30 + rnd() * 1040, y = 70 + rnd() * 540;
    if (onRoad(x, y)) continue; if (pts.some(p => Math.hypot(p[0] - x, p[1] - y) < 62)) continue; pts.push([x, y]); }
  pts.sort((a, b) => a[1] - b[1]).forEach(([x, y]) => tree(x, y, inside(x, y) ? .95 : .8 + rnd() * .25));
  // 枠付きの地名
  const tag = (x, y, main, sub, cls = '') => { const g = el('g', { class: ('tag ' + cls).trim() });
    const t = el('text', { x: x + 10, y: y + 21, 'font-size': 17 }, g); t.textContent = main;
    if (sub) { const s = el('tspan', { 'font-size': 12, dx: 4 }, t); s.textContent = sub; }
    const w = t.getComputedTextLength ? t.getComputedTextLength() : main.length * 18; const r = el('rect', { x, y, width: w + 20, height: 30 }, g); g.insertBefore(r, t); };
  tag(390, 205, '1206-2', '(ご相談の山)', 'mine');
  tag(700, 160, '隣の山', '(所有者は別)');
  tag(110, 200, '隣の山', '');
  tag(820, 395, '林道', '(車で入れる所まで)');
  tag(600, 20, '沢', '');
  tag(250, 445, '境界杭', '(見つかっていない所も)');
})();

// ---- 相談票 ----
(function () {
  const form = document.getElementById('hl-sheet'), out = document.getElementById('hl-out');
  const d = new Date(); document.getElementById('hl-today').textContent = `${d.getFullYear()}年${d.getMonth() + 1}月${d.getDate()}日`;
  let prev = new Set();
  const apply = () => `<a class="apply" href="${window.ConsultSheet.url(form)}" target="_blank" rel="noopener noreferrer">無料相談を申し込む</a><small>申し込みの用紙が開きます。ここで付けた印は、用紙の「ご相談の内容」に写してあります。お名前とご連絡先を書いて送ってください。</small>`;
  function render() {
    document.getElementById('hl-count').textContent = form.querySelectorAll('input:checked').length;
    const v = n => form.querySelector(`[name=${n}]:checked`)?.value, all = n => [...form.querySelectorAll(`[name=${n}]:checked`)].map(e => e.value);
    const docs = all('doc'), worry = all('worry'), owner = v('owner'), place = v('place'), steps = [];
    if (!owner && !place && !docs.length && !worry.length) { out.innerHTML = '<p class="empty">相談票に印を付けると、ここに出ます。印を付けずに申し込んでも構いません。</p>' + apply(); prev = new Set(); return; }
    if (docs.includes('tax')) steps.push('納税通知書に書かれた地番から、山の場所と面積が分かります。まずはこれをお手元に。');
    else if (place !== 'known') steps.push('山の場所は、市町村で「名寄帳」を取ると一覧で分かることがあります。取り方はご相談の中でご案内します。');
    if (owner === 'dead') steps.push('名義が亡くなった方のままの場合、相続登記が必要です(義務化されています)。手続きは司法書士へおつなぎします。');
    if (owner === 'unknown' || (!docs.includes('touki') && owner !== 'self')) steps.push('登記簿を取ると、今の名義と共有者が分かります。法務局で誰でも取れます。');
    if (worry.includes('far') || worry.includes('tree')) steps.push('現地の様子は、私たちが確かめて写真でお伝えできます(費用は事前にお見積り)。');
    if (worry.includes('sell')) steps.push('売れるかどうかは場所と条件次第です。売る以外に、管理を頼む・隣の方に譲る、も一緒に比べます。');
    if (worry.includes('mixed')) steps.push('畑や空き家も、山と一緒に一覧にして整理します。');
    if (worry.includes('cost') || worry.includes('family')) steps.push('毎年の負担を土地ごとに一覧にすると、残すか手放すかを家族で話しやすくなります。');
    if (!steps.length) steps.push('分かる範囲のことを、そのままお聞かせください。');
    out.innerHTML = '<ol>' + steps.map(s => `<li${prev.has(s) ? '' : ' class="new"'}>${s}</li>`).join('') + '</ol>' + apply();
    prev = new Set(steps);
  }
  form.addEventListener('change', render); form.addEventListener('input', render); render();
})();

// ---- 入場 ----
// 画面に入ったら .on を付ける。IntersectionObserver に頼りきらず、スクロールのたびにも位置を確かめる。
(function () {
  document.documentElement.classList.add('rv-ready');
  const show = () => document.querySelectorAll('.rv:not(.on)').forEach(el => { if (el.getBoundingClientRect().top < window.innerHeight * 0.92) el.classList.add('on'); });
  ['scroll', 'resize', 'load'].forEach(t => window.addEventListener(t, show, { passive: true }));
  show();
  setTimeout(show, 300);
})();
});
