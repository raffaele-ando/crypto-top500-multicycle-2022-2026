/* ==========================================================================
   Pure Crypto Top 500 — Shared Hub Shell, Theme Engine & Italian FMT Helper
   ========================================================================== */
(function () {
  const THEME_KEY = "crypto_hub_theme";
  const REPO_URL = "https://github.com/raffaele-ando/crypto-top500-multicycle-2022-2026";

  // 1. Unified Italian Financial Number Formatter (useGrouping:'always' so 4-digit numbers ALWAYS get thousands dot!)
  const nfInt = new Intl.NumberFormat("it-IT", { maximumFractionDigits: 0, useGrouping: "always" });
  const nf1 = new Intl.NumberFormat("it-IT", { minimumFractionDigits: 1, maximumFractionDigits: 1, useGrouping: "always" });
  const nf2 = new Intl.NumberFormat("it-IT", { minimumFractionDigits: 2, maximumFractionDigits: 2, useGrouping: "always" });
  const nf4 = new Intl.NumberFormat("it-IT", { minimumFractionDigits: 4, maximumFractionDigits: 4, useGrouping: "always" });
  const nf6 = new Intl.NumberFormat("it-IT", { minimumFractionDigits: 6, maximumFractionDigits: 6, useGrouping: "always" });

  function cleanZero(n, decimals) {
    const eps = decimals === 1 ? 0.05 : 0.005;
    return Math.abs(n) < eps ? 0 : n;
  }

  window.FMT = {
    int: (v) => (v === null || v === undefined || v === "" || isNaN(v)) ? "N/D" : nfInt.format(Math.round(Number(v))),
    dec1: (v) => (v === null || v === undefined || v === "" || isNaN(v)) ? "N/D" : nf1.format(cleanZero(Number(v), 1)),
    dec2: (v) => (v === null || v === undefined || v === "" || isNaN(v)) ? "N/D" : nf2.format(cleanZero(Number(v), 2)),
    fx: (v) => (v === null || v === undefined || v === "" || isNaN(v)) ? "N/D" : nf4.format(Number(v)),
    eur: (v, withUnit = true) => {
      if (v === null || v === undefined || v === "" || isNaN(v)) return "N/D";
      return nf2.format(cleanZero(Number(v), 2)) + (withUnit ? "\u00A0EUR" : "");
    },
    eurSigned: (v) => {
      if (v === null || v === undefined || v === "" || isNaN(v)) return "N/D";
      const n = cleanZero(Number(v), 2);
      return (n > 0 ? "+" : "") + nf2.format(n) + "\u00A0EUR";
    },
    pct: (v, signed = true, decimals = 2) => {
      if (v === null || v === undefined || v === "" || isNaN(v)) return "N/D";
      const n = cleanZero(Number(v), decimals);
      const s = (signed && n > 0 ? "+" : "");
      return s + (decimals === 1 ? nf1.format(n) : nf2.format(n)) + "%";
    },
    pctClass: (v) => {
      if (v === null || v === undefined || v === "" || isNaN(v)) return "mut";
      const n = cleanZero(Number(v), 2);
      return n >= 0 ? "pos" : "neg";
    },
    price: (v, currencyPrefix = "") => {
      if (v === null || v === undefined || v === "" || isNaN(v)) return "N/Q";
      const n = Number(v);
      const a = Math.abs(n);
      let s;
      if (a >= 10) s = nf2.format(n);
      else if (a >= 0.01) s = nf4.format(n);
      else if (a >= 0.0001) s = nf6.format(n);
      else if (a === 0) s = "0,00";
      else {
        const fixed = n.toFixed(10).replace(/0+$/, "");
        const dec = fixed.split(".")[1] || "00";
        const trimmed = dec.length > 8 ? dec.slice(0, Math.min(dec.length, Math.max(8, dec.search(/[1-9]/) + 3))) : dec;
        s = (n < 0 ? "-" : "") + "0," + trimmed;
      }
      return currencyPrefix + s;
    },
    compact: (v, prefix = "") => {
      if (v === null || v === undefined || v === "" || isNaN(v)) return "N/D";
      const n = Number(v), a = Math.abs(n);
      if (a >= 1e12) return prefix + nf2.format(n / 1e12) + "\u00A0T";
      if (a >= 1e9) return prefix + nf2.format(n / 1e9) + "\u00A0B";
      if (a >= 1e6) return prefix + nf2.format(n / 1e6) + "\u00A0M";
      if (a >= 1e3) return prefix + nf1.format(n / 1e3) + "\u00A0K";
      return prefix + nfInt.format(Math.round(n));
    }
  };

  const SUN_SVG = '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><circle cx="12" cy="12" r="4"/><path d="M12 2v2M12 20v2M4.93 4.93l1.41 1.41M17.66 17.66l1.41 1.41M2 12h2M20 12h2M6.34 17.66l-1.41 1.41M19.07 4.93l-1.41 1.41"/></svg>';
  const MOON_SVG = '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/></svg>';
  const GH_SVG = '<svg width="14" height="14" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M12 2C6.48 2 2 6.58 2 12.26c0 4.54 2.87 8.39 6.84 9.75.5.09.68-.22.68-.49 0-.24-.01-.88-.01-1.73-2.78.62-3.37-1.37-3.37-1.37-.45-1.18-1.11-1.5-1.11-1.5-.91-.64.07-.63.07-.63 1 .07 1.53 1.06 1.53 1.06.89 1.57 2.34 1.12 2.91.85.09-.66.35-1.12.63-1.38-2.22-.26-4.56-1.14-4.56-5.08 0-1.12.39-2.04 1.03-2.76-.1-.26-.45-1.31.1-2.72 0 0 .84-.28 2.75 1.05A9.35 9.35 0 0 1 12 6.84c.85 0 1.71.12 2.51.35 1.91-1.33 2.75-1.05 2.75-1.05.55 1.41.2 2.46.1 2.72.64.72 1.03 1.64 1.03 2.76 0 3.95-2.34 4.82-4.57 5.07.36.32.68.94.68 1.9 0 1.37-.01 2.48-.01 2.82 0 .27.18.59.69.49A10.27 10.27 0 0 0 22 12.26C22 6.58 17.52 2 12 2z"/></svg>';

  // 2. Theme Engine (persisted across all 7 pages + reacts to external data-theme changes!)
  function syncThemeUI(theme) {
    const btn = document.getElementById("agyThemeToggle");
    if (btn) {
      btn.setAttribute("aria-pressed", theme === "light" ? "true" : "false");
      btn.setAttribute("aria-label", theme === "dark" ? "Passa alla modalità chiara" : "Passa alla modalità scura OLED");
      btn.title = theme === "dark" ? "Passa alla modalità chiara" : "Passa alla modalità scura OLED";
      btn.innerHTML = theme === "dark"
        ? `${SUN_SVG}<span class="theme-lbl">Chiara</span>`
        : `${MOON_SVG}<span class="theme-lbl">Scura</span>`;
    }
  }
  function applyTheme(t) {
    const theme = t === "light" ? "light" : "dark";
    document.documentElement.setAttribute("data-theme", theme);
    try { localStorage.setItem(THEME_KEY, theme); } catch (_) {}
    syncThemeUI(theme);
    window.dispatchEvent(new CustomEvent("agy-theme-change", { detail: { theme } }));
  }
  window.agyToggleTheme = function () {
    const cur = document.documentElement.getAttribute("data-theme") || "dark";
    applyTheme(cur === "dark" ? "light" : "dark");
  };
  let _lastTheme = document.documentElement.getAttribute("data-theme") || "dark";
  new MutationObserver(() => {
    const cur = document.documentElement.getAttribute("data-theme") || "dark";
    if (cur !== _lastTheme) {
      _lastTheme = cur;
      syncThemeUI(cur);
      window.dispatchEvent(new CustomEvent("agy-theme-change", { detail: { theme: cur } }));
    }
  }).observe(document.documentElement, { attributes: true, attributeFilter: ["data-theme"] });

  // 3. Unified Single-Row Hub Navbar Renderer (with Bilateral Scroll Fade & Compact Tablet/Mobile Ergonomics)
  window.agyInitHubNav = function (activeId, basePrefix) {
    const pref = basePrefix || "./";
    const pages = [
      { id: "home", href: pref + "index.html", label: "Home", cls: "hub-home" },
      { id: "flagship15", href: pref + "multidate_15_2022_2026/dashboard_15date_ciclo_2022_2026.html", label: "15 Date (2022–2026)" },
      { id: "storico3", href: pref + "dashboard_storico_3date_500.html", label: "Storico 3 Date" },
      { id: "tokenomics", href: pref + "dashboard_tokenomics_holders_500.html", label: "Tokenomics & Whale" },
      { id: "curva", href: pref + "curva_rendimento_N1_to_N500.html", label: "Curva N=1..500" },
      { id: "pure500", href: pref + "dashboard_pure500_crypto_2026.html", label: "Pure 500 Q3" },
      { id: "raw500", href: pref + "dashboard_top500_crypto_2026.html", label: "Raw Top 500" },
    ];
    let nav = document.querySelector("nav.agy-hub-nav");
    if (!nav) {
      nav = document.createElement("nav");
      nav.className = "agy-hub-nav";
      nav.setAttribute("aria-label", "Navigazione principale suite");
      document.body.insertBefore(nav, document.body.firstChild);
    }
    const linksHtml = pages.map(p => {
      const active = p.id === activeId ? " hub-active" : "";
      const extra = p.cls ? " " + p.cls : "";
      const aria = p.id === activeId ? ' aria-current="page"' : "";
      return `<a href="${p.href}" class="hub-pill${extra}${active}"${aria}>${p.label}</a>`;
    }).join("");
    nav.innerHTML =
      `<div class="agy-hub-rail">${linksHtml}</div>` +
      `<div class="agy-hub-actions">` +
        `<button type="button" id="agyThemeToggle" class="hub-pill hub-theme" onclick="agyToggleTheme()"></button>` +
        `<a href="${REPO_URL}" target="_blank" rel="noopener" class="hub-pill hub-gh" aria-label="Apri repository su GitHub" title="Apri repository su GitHub">${GH_SVG}<span class="gh-txt">GitHub<span class="gh-lbl"> Repo</span> &nearr;</span></a>` +
      `</div>`;

    let saved = "dark";
    try { saved = localStorage.getItem(THEME_KEY) || document.documentElement.getAttribute("data-theme") || "dark"; } catch (_) {}
    applyTheme(saved);

    const rail = nav.querySelector(".agy-hub-rail");
    const act = nav.querySelector(".hub-active");
    function syncRailFade() {
      if (!rail) return;
      const canScroll = rail.scrollWidth > rail.clientWidth + 4;
      const hasLeft = canScroll && rail.scrollLeft > 2;
      const hasRight = canScroll && (rail.scrollLeft + rail.clientWidth < rail.scrollWidth - 4);
      rail.classList.toggle("has-left-fade", hasLeft);
      rail.classList.toggle("has-right-fade", hasRight);
      nav.classList.toggle("rail-overflows", canScroll);
    }
    if (act && rail) {
      requestAnimationFrame(() => {
        if (rail.scrollWidth > rail.clientWidth + 4) {
          try { act.scrollIntoView({ inline: "center", block: "nearest", behavior: "instant" }); } catch (_) {}
        }
        syncRailFade();
      });
    }
    if (rail) {
      rail.addEventListener("scroll", syncRailFade, { passive: true });
      window.addEventListener("resize", syncRailFade);
      syncRailFade();
      setTimeout(syncRailFade, 80);
      setTimeout(syncRailFade, 220);
    }

    window.agyRefreshScrollHints();
    window.addEventListener("resize", window.agyRefreshScrollHints);
  };

  function ensureTableShell(wrap) {
    if (!wrap) return null;
    if (wrap.parentElement && wrap.parentElement.classList.contains("tbl-shell")) return wrap.parentElement;
    // Only wrap horizontal-scroll containers (skip desktop overflow:visible heatmap)
    const shell = document.createElement("div");
    shell.className = "tbl-shell";
    wrap.parentNode.insertBefore(shell, wrap);
    shell.appendChild(wrap);
    return shell;
  }

  function bindTableShadow(wrap) {
    if (!wrap || wrap.dataset.shadowBound) return;
    wrap.dataset.shadowBound = "1";
    const sync = () => {
      const shell = wrap.parentElement && wrap.parentElement.classList.contains("tbl-shell") ? wrap.parentElement : null;
      const cs = getComputedStyle(wrap);
      const isScrollableBox = cs.overflowX !== "visible";
      const hasRight = isScrollableBox && wrap.scrollWidth > wrap.clientWidth + 6 && (wrap.scrollLeft + wrap.clientWidth < wrap.scrollWidth - 4);
      if (shell) shell.classList.toggle("can-scroll-right", hasRight);
    };
    wrap.addEventListener("scroll", sync, { passive: true });
    sync();
  }

  window.agyRefreshScrollHints = function () {
    document.querySelectorAll("[data-scroll-hint]").forEach(hint => {
      const targetId = hint.getAttribute("data-scroll-hint");
      const wrap = document.getElementById(targetId);
      if (!wrap) return;
      const cs = getComputedStyle(wrap);
      const isScrollableBox = cs.overflowX !== "visible";
      const hasX = isScrollableBox && wrap.scrollWidth > wrap.clientWidth + 6;
      hint.classList.toggle("visible", hasX);
      if (hasX) ensureTableShell(wrap);
      bindTableShadow(wrap);
      const shell = wrap.parentElement && wrap.parentElement.classList.contains("tbl-shell") ? wrap.parentElement : null;
      if (shell) {
        const hasRight = hasX && (wrap.scrollLeft + wrap.clientWidth < wrap.scrollWidth - 4);
        shell.classList.toggle("can-scroll-right", hasRight);
      }
    });
  };

  window.agyBindSearchClear = function (inputId, onClear) {
    const inp = document.getElementById(inputId);
    if (!inp) return;
    const box = inp.closest(".search-box");
    const clr = box ? box.querySelector(".s-clr") : null;
    const sync = () => { if (box) box.classList.toggle("has-val", inp.value.length > 0); };
    inp.addEventListener("input", sync);
    if (clr) {
      clr.addEventListener("click", () => {
        inp.value = "";
        sync();
        inp.focus();
        if (onClear) onClear();
        else inp.dispatchEvent(new Event("input", { bubbles: true }));
      });
    }
    sync();
  };
})();
