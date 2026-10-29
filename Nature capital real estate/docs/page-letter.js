// トップ以外のページの入場の動き(2026-10-29)。home-letter.js の「入場」と同じ仕組み。
// 本文の節の子要素に .rv を付け、画面に入ったら .on を付ける。地図(forest-data)は動かさない。
document.addEventListener('DOMContentLoaded', () => {
  const main = document.querySelector('main.lt');
  if (!main) return;
  main.querySelectorAll(':scope > section:not(.map-section) > *:not(nav)').forEach((el) => {
    el.classList.add('rv');
    if (el.matches('figure, img')) el.classList.add('rv-img');
  });
  document.documentElement.classList.add('rv-ready');
  const show = () => main.querySelectorAll('.rv:not(.on)').forEach((el) => {
    if (el.getBoundingClientRect().top < window.innerHeight * 0.92) el.classList.add('on');
  });
  ['scroll', 'resize', 'load'].forEach((t) => window.addEventListener(t, show, { passive: true }));
  show();
  setTimeout(show, 300);
});
