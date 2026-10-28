(function () {
  "use strict";

  // 相談フォームの「流入元」質問の ID(例: "entry.123456789")。
  // 空のあいだは何もしない。決め方は maintenance/consult-source.md を参照。
  var FORM_ENTRY = "";

  var STORAGE_KEY = "nature-capital-src";
  var FORM_PREFIX = "https://docs.google.com/forms/";

  // チラシの QR などに付けた ?src=flyer-a を、そのタブを閉じるまで覚えておく
  var src = new URLSearchParams(window.location.search).get("src");
  if (src && /^[a-z0-9-]{1,40}$/.test(src)) {
    try {
      sessionStorage.setItem(STORAGE_KEY, src);
    } catch (e) {}
  }

  // このファイルの置き場所をサイトの起点とみなし、ページの位置を相対パスで出す
  var script = document.currentScript;
  var base = script ? script.src.replace(/consult-source\.js.*$/, "") : "";

  document.addEventListener("DOMContentLoaded", function () {
    if (!FORM_ENTRY) return;

    var stored = null;
    try {
      stored = sessionStorage.getItem(STORAGE_KEY);
    } catch (e) {}

    var here = window.location.href.split(/[?#]/)[0];
    var page = base && here.indexOf(base) === 0 ? here.slice(base.length) : window.location.pathname;
    var value = (stored || "web") + " / " + (page || "top");

    var links = document.querySelectorAll('a[href^="' + FORM_PREFIX + '"]');
    Array.prototype.forEach.call(links, function (link) {
      var url = new URL(link.href);
      url.searchParams.set("usp", "pp_url");
      url.searchParams.set(FORM_ENTRY, value);
      link.href = url.toString();
    });
  });
})();
