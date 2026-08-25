(function () {
  "use strict";

  var PASSWORD = "fnature";
  var SESSION_KEY = "nature-capital-site-unlocked";

  document.documentElement.classList.add("auth-locked");

  function createGate() {
    if (sessionStorage.getItem(SESSION_KEY) === "true") {
      document.documentElement.classList.remove("auth-locked");
      return;
    }

    var gate = document.createElement("div");
    gate.className = "password-gate";
    gate.setAttribute("role", "dialog");
    gate.setAttribute("aria-modal", "true");
    gate.setAttribute("aria-labelledby", "password-gate-title");
    gate.innerHTML =
      '<div class="password-gate-card">' +
      '<p class="password-gate-label">NATURE CAPITAL &amp; REAL ESTATE</p>' +
      '<h1 id="password-gate-title">サイトをご覧になるには<br>パスワードを入力してください</h1>' +
      '<form class="password-gate-form" novalidate>' +
      '<label for="site-password">パスワード</label>' +
      '<input id="site-password" name="password" type="password" autocomplete="current-password" required>' +
      '<p class="password-gate-error" role="alert" hidden>パスワードが正しくありません。</p>' +
      '<button type="submit">アクセスする <span aria-hidden="true">→</span></button>' +
      "</form></div>";

    document.body.appendChild(gate);
    var form = gate.querySelector("form");
    var input = gate.querySelector("input");
    var error = gate.querySelector(".password-gate-error");

    form.addEventListener("submit", function (event) {
      event.preventDefault();
      if (input.value === PASSWORD) {
        sessionStorage.setItem(SESSION_KEY, "true");
        document.documentElement.classList.remove("auth-locked");
        gate.remove();
        return;
      }
      error.hidden = false;
      input.select();
    });

    input.focus();
  }

  document.addEventListener("DOMContentLoaded", createGate);
})();
