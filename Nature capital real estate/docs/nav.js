(function () {
  "use strict";

  // Runs before the page is drawn, so styles.css hides the phone menu only when
  // the button below will exist; without this script the menu stays open.
  document.documentElement.classList.add("js-nav");

  document.addEventListener("DOMContentLoaded", function () {
    const header = document.querySelector("body > header");
    const nav = header && header.querySelector(".site-nav");
    if (!nav) return;

    const en = document.documentElement.lang === "en";
    const labels = en ? ["Menu", "Close"] : ["メニュー", "閉じる"];
    nav.id = nav.id || "site-nav";

    const button = document.createElement("button");
    button.type = "button";
    button.className = "nav-toggle";
    button.setAttribute("aria-controls", nav.id);
    button.setAttribute("aria-expanded", "false");
    button.textContent = labels[0];

    button.addEventListener("click", function () {
      const open = header.classList.toggle("nav-open");
      button.setAttribute("aria-expanded", String(open));
      button.textContent = labels[open ? 1 : 0];
    });

    header.insertBefore(button, nav);
  });
})();
