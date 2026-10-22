(function () {
  "use strict";

  document.addEventListener("DOMContentLoaded", function () {
    var header = document.querySelector("body > header");
    var nav = header && header.querySelector(".site-nav");
    if (!nav) return;

    var en = document.documentElement.lang === "en";
    var labels = en ? ["Menu", "Close"] : ["メニュー", "閉じる"];
    nav.id = nav.id || "site-nav";

    var button = document.createElement("button");
    button.type = "button";
    button.className = "nav-toggle";
    button.setAttribute("aria-controls", nav.id);
    button.setAttribute("aria-expanded", "false");
    button.textContent = labels[0];

    button.addEventListener("click", function () {
      var open = header.classList.toggle("nav-open");
      button.setAttribute("aria-expanded", String(open));
      button.textContent = labels[open ? 1 : 0];
    });

    header.insertBefore(button, nav);
  });
})();
