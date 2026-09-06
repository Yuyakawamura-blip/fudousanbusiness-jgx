(() => {
  'use strict';
  const $ = (id) => document.getElementById(id);
  const source = 'https://www.geospatial.jp/ckan/dataset/layer';
  function external(url, text, className) {
    const a = document.createElement('a');
    const parsed = new URL(url);
    if (parsed.protocol !== 'https:') throw new Error('Invalid source URL');
    a.href = parsed.href;
    a.textContent = text;
    a.target = '_blank';
    a.rel = 'noopener noreferrer';
    if (className) a.className = className;
    return a;
  }
  function dateTime(value) {
    const date = new Date(value);
    if (!Number.isFinite(date.getTime())) return '未確認';
    return new Intl.DateTimeFormat('ja-JP', { timeZone: 'Asia/Tokyo', dateStyle: 'medium', timeStyle: 'short' }).format(date) + '（日本時間）';
  }
  function drawCatalog(resources) {
    const downloads = resources.filter((r) => r.kind === 'download');
    const query = $('prefecture-search').value.trim().normalize('NFKC');
    const rows = downloads.filter((r) => r.prefecture.includes(query));
    const fragment = document.createDocumentFragment();
    rows.forEach((r) => {
      const article = document.createElement('article');
      article.className = 'prefecture-card';
      article.append(external(r.url, r.prefecture + ' ↗', 'download-link'));
      const meta = document.createElement('small');
      meta.textContent = `${r.format.toUpperCase() || 'ファイル'} / ${r.name}`;
      article.append(meta, external(r.page, '詳細・ファイル情報', 'detail-link'));
      fragment.append(article);
    });
    $('prefecture-list').replaceChildren(fragment);
    $('resource-count').textContent = `${rows.length} 件表示 / ${new Set(downloads.map((r) => r.prefecture)).size} 都道府県`;
    $('empty-result').hidden = rows.length > 0;
  }
  function drawConnections(resources) {
    resources.filter((r) => ['tile', 'style'].includes(r.kind)).forEach((r, i) => {
      const row = document.createElement('div'); row.className = 'connection-row';
      const label = document.createElement('label'); label.htmlFor = `connection-${i}`; label.textContent = r.name;
      const controls = document.createElement('div'); controls.className = 'connection-controls';
      const input = document.createElement('input'); input.id = label.htmlFor; input.value = r.url; input.readOnly = true;
      const button = document.createElement('button'); button.type = 'button'; button.className = 'outline-button'; button.textContent = 'URLをコピー';
      button.addEventListener('click', async () => {
        try { await navigator.clipboard.writeText(r.url); $('copy-status').textContent = `${r.name}のURLをコピーしました。`; }
        catch { input.focus(); input.select(); $('copy-status').textContent = 'URLを選択しました。コピー操作で取得してください。'; }
      });
      controls.append(input, button); row.append(label, controls); $('connection-list').append(row);
    });
    resources.filter((r) => r.kind === 'document').forEach((r) => {
      $('document-list').append(external(r.url, `${r.name} ↗`));
    });
  }
  function drawMap(resources) {
    const raster = resources.find((r) => r.kind === 'tile' && /\.(webp|png|jpg)(\?|$)/i.test(r.url));
    if (!raster || !window.L) {
      $('map-status').textContent = '地図を表示できません。公式データのリンクをご利用ください。';
      return;
    }
    // Limits follow the forest layer data dictionary. Vector styles are offered unmodified.
    const map = L.map('forest-map', { minZoom: 5, maxZoom: 16, scrollWheelZoom: false, zoomControl: true }).setView([37.2, 137.8], 5);
    L.tileLayer('https://cyberjapandata.gsi.go.jp/xyz/pale/{z}/{x}/{y}.png', {
      maxZoom: 16, attribution: '<a href="https://maps.gsi.go.jp/development/ichiran.html">地理院タイル</a>'
    }).on('tileerror', () => { $('map-status').textContent = '背景地図の一部を取得できません。'; }).addTo(map);
    const forest = L.tileLayer(raster.url, {
      minZoom: 5, maxZoom: 16, opacity: 0.75, bounds: [[20.4, 122.9], [45.6, 154]],
      attribution: '<a href="' + source + '">林野庁</a> / <a href="https://www.digital.go.jp/resources/open_data/public_data_license_v1.0">PDL1.0</a>'
    });
    let loaded = 0; let errors = 0;
    forest.on('loading', () => { loaded = 0; errors = 0; $('map-status').textContent = '森林レイヤを読み込み中…'; });
    forest.on('tileload', () => { loaded += 1; });
    forest.on('tileerror', () => { errors += 1; });
    forest.on('load', () => {
      $('map-status').textContent = errors ? (loaded ? '一部の森林タイルを取得できません。未表示部分は公式データでご確認ください。' : '森林レイヤを取得できません。公式データをご確認ください。') : '';
    });
    forest.addTo(map);
    L.control.scale({ imperial: false, position: 'bottomleft' }).addTo(map);
    ['forest-toggle', 'opacity', 'reset-map'].forEach((id) => { $(id).disabled = false; });
    $('forest-toggle').addEventListener('change', (e) => {
      if (e.target.checked) forest.addTo(map);
      else { map.removeLayer(forest); $('map-status').textContent = '森林レイヤを非表示にしています。'; }
    });
    $('opacity').addEventListener('input', (e) => { forest.setOpacity(Number(e.target.value) / 100); $('opacity-value').value = e.target.value + '%'; });
    $('reset-map').addEventListener('click', () => map.setView([37.2, 137.8], 5));
  }
  async function start() {
    try {
      const response = await fetch('./catalog.json', { cache: 'no-cache' });
      if (!response.ok) throw new Error('Catalog unavailable');
      const data = await response.json();
      if (data.schema_version !== 1 || !Array.isArray(data.resources) || !data.resources.length) throw new Error('Invalid catalog');
      $('checked-at').textContent = '最終取得：' + dateTime(data.checked_at);
      $('last-success').textContent = dateTime(data.checked_at);
      // CKAN timestamps have no timezone marker; retain their published calendar date.
      $('source-modified').textContent = data.source_modified.slice(0, 10) + '（提供元表記）';
      $('content-changed').textContent = dateTime(data.changed_at);
      const stale = Date.now() - new Date(data.checked_at).getTime() > 72 * 60 * 60 * 1000;
      $('freshness').textContent = stale ? '最終取得から3日以上経過しています。最新情報は提供元でご確認ください。' : '前回の正常な取得内容を表示しています。';
      $('source-notes').textContent = data.notes;
      $('prefecture-search').disabled = false;
      drawCatalog(data.resources);
      $('prefecture-search').addEventListener('input', () => drawCatalog(data.resources));
      drawConnections(data.resources);
      drawMap(data.resources);
    } catch {
      $('checked-at').textContent = '更新情報を取得できませんでした';
      $('resource-count').textContent = 'データ一覧を取得できません。';
      $('prefecture-list').append(external(source, '公式データ一覧を開く ↗'));
      $('map-status').textContent = 'データを読み込めません。公式データのリンクをご利用ください。';
      $('source-notes').textContent = '提供元のページをご確認ください。';
      ['last-success', 'source-modified', 'content-changed'].forEach((id) => { $(id).textContent = '未確認'; });
    }
  }
  start();
})();
