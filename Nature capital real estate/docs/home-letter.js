(function () {
  "use strict";

  // トップの相談票: 印に応じて「最初にすること」を出し、申し込みボタンに相談票の内容を付ける。
  // 印の内容はこのページの中だけで扱い、送るのは利用者がフォームで送信したときだけ。
  document.addEventListener("DOMContentLoaded", function () {
    var form = document.getElementById("hl-sheet");
    var out = document.getElementById("hl-out");
    if (!form || !out) return;

    var today = new Date();
    document.getElementById("hl-today").textContent =
      today.getFullYear() + "年" + (today.getMonth() + 1) + "月" + today.getDate() + "日";

    var prev = {};

    function checked(name) {
      return Array.prototype.map.call(form.querySelectorAll('[name="' + name + '"]:checked'), function (input) {
        return input.value;
      });
    }
    function has(list, value) {
      return list.indexOf(value) !== -1;
    }
    function escape(text) {
      return text.replace(/[&<>"]/g, function (c) {
        return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c];
      });
    }
    function button() {
      var href = window.ConsultSheet ? window.ConsultSheet.url(form) : form.getAttribute("data-form-url");
      return (
        '<a class="hl-btn" href="' + escape(href) + '" target="_blank" rel="noopener noreferrer">無料相談を申し込む</a>' +
        "<small>申し込みの用紙が開きます。ここで付けた印は、用紙の「ご相談の内容」に写してあります。お名前とご連絡先を書いて送ってください。3 営業日以内にご連絡します。</small>"
      );
    }

    function render() {
      document.getElementById("hl-count").textContent = form.querySelectorAll("input:checked").length;

      var owner = checked("owner")[0];
      var place = checked("place")[0];
      var docs = checked("doc");
      var worry = checked("worry");
      var steps = [];

      if (!owner && !place && !docs.length && !worry.length) {
        out.innerHTML = '<p class="empty">相談票に印を付けると、ここに出ます。印を付けずに申し込んでも構いません。</p>' + button();
        prev = {};
        return;
      }
      if (has(docs, "tax")) steps.push("納税通知書に書かれた地番から、山の場所と面積が分かります。まずはこれをお手元に。");
      else if (place !== "known") steps.push("山の場所は、市町村で「名寄帳」を取ると一覧で分かることがあります。取り方はご相談の中でご案内します。");
      if (owner === "dead") steps.push("名義が亡くなった方のままの場合、相続登記が必要です(義務化されています)。手続きは司法書士へおつなぎします。");
      if (owner === "unknown" || (!has(docs, "touki") && owner !== "self")) steps.push("登記簿を取ると、今の名義と共有者が分かります。法務局で誰でも取れます。");
      if (has(worry, "far") || has(worry, "tree")) steps.push("現地の様子は、私たちが確かめて写真でお伝えできます(費用は事前にお見積り)。");
      if (has(worry, "sell")) steps.push("売れるかどうかは場所と条件次第です。売る以外に、管理を頼む・隣の方に譲る、も一緒に比べます。");
      if (has(worry, "mixed")) steps.push("畑や空き家も、山と一緒に一覧にして整理します。");
      if (has(worry, "cost") || has(worry, "family")) steps.push("毎年の負担を土地ごとに一覧にすると、残すか手放すかを家族で話しやすくなります。");
      if (!steps.length) steps.push("分かる範囲のことを、そのままお聞かせください。");

      var next = {};
      out.innerHTML =
        "<ul>" +
        steps
          .map(function (step) {
            next[step] = true;
            return "<li" + (prev[step] ? "" : ' class="new"') + ">" + step + "</li>";
          })
          .join("") +
        "</ul>" +
        button();
      prev = next;
    }

    form.addEventListener("submit", function (event) {
      event.preventDefault();
    });
    form.addEventListener("change", render);
    form.addEventListener("input", render);
    render();
  });
})();
