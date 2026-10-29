(function () {
  "use strict";

  // 相談票(ページ内の記入式の票)で付けた印を、相談フォームに事前入力する。
  // 送るのは利用者がフォームで「送信」を押したときだけ。このファイル自体はどこにも送らない。
  // 質問 ID の調べ方は maintenance/consult-source.md を参照。
  var FORM_URL = "https://docs.google.com/forms/d/e/1FAIpQLSf-ocdeAe1K4wWujFNSnc8Av1y8yW-3cLAVppjavB2UJwqELg/viewform";
  var ENTRY_CONTENT = "entry.2021287330"; // 山林の場所、相続の状況、お困りのことなど
  var ENTRY_PLACE = "entry.1159922948"; // 山林の所在地
  var MAX_LENGTH = 600;

  function clean(text) {
    return text.replace(/\s+/g, " ").trim();
  }

  // <fieldset data-label="名義"> ごとに「名義：選んだもの、選んだもの」を 1 行ずつ作る
  function summary(form) {
    var parts = [];
    Array.prototype.forEach.call(form.querySelectorAll("fieldset[data-label]"), function (set) {
      var values = [];
      Array.prototype.forEach.call(set.querySelectorAll("input:checked"), function (input) {
        var label = input.closest("label");
        if (label) values.push(clean(label.textContent));
      });
      Array.prototype.forEach.call(set.querySelectorAll('input[type="text"]:not([data-prefill])'), function (input) {
        if (clean(input.value)) values.push(clean(input.value));
      });
      if (values.length) parts.push(set.getAttribute("data-label") + "：" + values.join("、"));
    });
    var text = parts.length ? "【相談票より】\n" + parts.join("\n") : "";
    return text.length > MAX_LENGTH ? text.slice(0, MAX_LENGTH) + "…" : text;
  }

  function url(form) {
    var u = new URL(FORM_URL);
    var content = summary(form);
    var place = form.querySelector('[data-prefill="place"]');
    if (content || (place && clean(place.value))) u.searchParams.set("usp", "pp_url");
    if (content) u.searchParams.set(ENTRY_CONTENT, content);
    if (place && clean(place.value)) u.searchParams.set(ENTRY_PLACE, clean(place.value).slice(0, 100));
    return u.toString();
  }

  window.ConsultSheet = { url: url, summary: summary };
})();
