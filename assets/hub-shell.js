/* ==========================================================================
   Pure Crypto Top 500 — Shared Hub Shell, Theme Engine & Italian FMT Helper
   ========================================================================== */
(function () {
  const THEME_KEY = "crypto_hub_theme";
  const REPO_URL = "https://github.com/raffaele-ando/crypto-top500-multicycle-2022-2026";

  // 1. Unified Italian Financial Number Formatter (useGrouping:'always' for 4-digit thousands dots!)
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
      return nf2.format(cleanZero(Number(v), 2)) + (withUnit ? "\u00A0\u20AC" : "");
    },
    eurInt: (v) => {
      if (v === null || v === undefined || v === "" || isNaN(v)) return "N/D";
      return nfInt.format(Math.round(Number(v))) + "\u00A0\u20AC";
    },
    eurSigned: (v) => {
      if (v === null || v === undefined || v === "" || isNaN(v)) return "N/D";
      const n = cleanZero(Number(v), 2);
      return (n > 0 ? "+" : "") + nf2.format(n) + "\u00A0\u20AC";
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
    price: (v, withUsd = false) => {
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
      return withUsd ? (s + "\u00A0USD") : s;
    },
    // Pure Italian compact scale: mld (miliardi), mln (milioni), mila — ZERO English T/B/M ambiguity!
    compact: (v, suffix = "") => {
      if (v === null || v === undefined || v === "" || isNaN(v)) return "N/D";
      const n = Number(v), a = Math.abs(n);
      if (a >= 1e11) return nf1.format(n / 1e9) + "\u00A0mld" + suffix;
      if (a >= 1e9) return nf2.format(n / 1e9) + "\u00A0mld" + suffix;
      if (a >= 1e8) return nf1.format(n / 1e6) + "\u00A0mln" + suffix;
      if (a >= 1e6) return nf2.format(n / 1e6) + "\u00A0mln" + suffix;
      if (a >= 1e3) return nf1.format(n / 1e3) + "\u00A0mila" + suffix;
      return nfInt.format(Math.round(n)) + suffix;
    },
    dateIt: (iso) => {
      if (!iso) return "—";
      const mNames = ["gen","feb","mar","apr","mag","giu","lug","ago","set","ott","nov","dic"];
      const parts = String(iso).slice(0, 10).split("-");
      if (parts.length !== 3) return iso;
      const d = parseInt(parts[2], 10);
      const m = mNames[parseInt(parts[1], 10) - 1] || parts[1];
      return `${d === 1 ? "1°" : d} ${m} ${parts[0]}`;
    },
    dateShort: (iso) => {
      if (!iso) return "—";
      const mNames = ["Gen","Feb","Mar","Apr","Mag","Giu","Lug","Ago","Set","Ott","Nov","Dic"];
      const parts = String(iso).slice(0, 10).split("-");
      if (parts.length !== 3) return iso;
      const m = mNames[parseInt(parts[1], 10) - 1] || parts[1];
      return `${m} ${parts[0].slice(2)}`;
    },
    durationIt: (isoStart, isoEnd) => {
      if (!isoStart || !isoEnd) return "";
      const d1 = new Date(String(isoStart).slice(0, 10) + "T00:00:00Z");
      const d2 = new Date(String(isoEnd).slice(0, 10) + "T00:00:00Z");
      const days = Math.max(1, Math.round((d2 - d1) / 86400000));
      const months = Math.round(days / 30.4375);
      if (months < 2) return `${days} giorni`;
      if (months < 12) return `${months} mesi (${days} giorni)`;
      const yrs = Math.floor(months / 12);
      const rem = months % 12;
      const yStr = yrs === 1 ? "1 anno" : `${yrs} anni`;
      if (rem === 0) return `${yStr} (${months} mesi)`;
      const mStr = rem === 1 ? "1 mese" : `${rem} mesi`;
      return `${yStr} e ${mStr} (${months} mesi)`;
    }
  };

  const SUN_SVG = '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><circle cx="12" cy="12" r="4"/><path d="M12 2v2M12 20v2M4.93 4.93l1.41 1.41M17.66 17.66l1.41 1.41M2 12h2M20 12h2M6.34 17.66l-1.41 1.41M19.07 4.93l-1.41 1.41"/></svg>';
  const MOON_SVG = '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/></svg>';
  const GH_SVG = '<svg width="14" height="14" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M12 2C6.48 2 2 6.58 2 12.26c0 4.54 2.87 8.39 6.84 9.75.5.09.68-.22.68-.49 0-.24-.01-.88-.01-1.73-2.78.62-3.37-1.37-3.37-1.37-.45-1.18-1.11-1.5-1.11-1.5-.91-.64.07-.63.07-.63 1 .07 1.53 1.06 1.53 1.06.89 1.57 2.34 1.12 2.91.85.09-.66.35-1.12.63-1.38-2.22-.26-4.56-1.14-4.56-5.08 0-1.12.39-2.04 1.03-2.76-.1-.26-.45-1.31.1-2.72 0 0 .84-.28 2.75 1.05A9.35 9.35 0 0 1 12 6.84c.85 0 1.71.12 2.51.35 1.91-1.33 2.75-1.05 2.75-1.05.55 1.41.2 2.46.1 2.72.64.72 1.03 1.64 1.03 2.76 0 3.95-2.34 4.82-4.57 5.07.36.32.68.94.68 1.9 0 1.37-.01 2.48-.01 2.82 0 .27.18.59.69.49A10.27 10.27 0 0 0 22 12.26C22 6.58 17.52 2 12 2z"/></svg>';
  const MENU_SVG = '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.1" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><line x1="4" y1="7" x2="20" y2="7"/><line x1="4" y1="12" x2="20" y2="12"/><line x1="4" y1="17" x2="20" y2="17"/></svg>';

  // 2. Theme Engine (persisted across all pages + reacts to external data-theme changes!)
  function syncThemeUI(theme) {
    const btn = document.getElementById("agyThemeToggle");
    if (btn) {
      btn.setAttribute("aria-pressed", theme === "light" ? "true" : "false");
      btn.setAttribute("aria-label", theme === "dark" ? "Attiva tema chiaro" : "Attiva tema scuro OLED");
      btn.title = theme === "dark" ? "Attiva tema chiaro" : "Attiva tema scuro OLED";
      btn.innerHTML = theme === "dark"
        ? `${SUN_SVG}<span class="theme-lbl">Tema chiaro</span>`
        : `${MOON_SVG}<span class="theme-lbl">Tema scuro</span>`;
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

  // 3. Task-Oriented 6-Item Hub Navbar — ZERO mid-word truncation from 1440px down to 320px!
  window.agyInitHubNav = function (activeId, basePrefix) {
    const pref = basePrefix || "./";
    const normActive = (activeId === "raw500" || activeId === "pure500") ? "dataset2026" : activeId;
    const pages = [
      { id: "home", href: pref + "index.html", label: "Panoramica", shortLabel: "Panoramica", desc: "Sintesi dei risultati sul ciclo 2022–2026", cls: "hub-home" },
      { id: "flagship15", href: pref + "multidate_15_2022_2026/dashboard_15date_ciclo_2022_2026.html", label: "Backtest 2022–2026", shortLabel: "Backtest 22–26", desc: "15 date, 105 finestre, fasce Top N e correlazioni" },
      { id: "storico3", href: pref + "dashboard_storico_3date_500.html", label: "Evoluzione 2026", shortLabel: "Evoluzione 2026", desc: "Confronto su 3 date (lug, ott, nov 2026)" },
      { id: "tokenomics", href: pref + "dashboard_tokenomics_holders_500.html", label: "Tokenomics e Balene", shortLabel: "Tokenomics", desc: "Registro on-chain, wallet e fonti dei 500 asset" },
      { id: "curva", href: pref + "curva_rendimento_N1_to_N500.html", label: "Curva Top 1–500", shortLabel: "Curva Top N", desc: "Diversificazione da 1 a 500 asset (lug–ott 2026)" },
      { id: "dataset2026", href: pref + "dashboard_pure500_crypto_2026.html", label: "Prezzi e Filtro CMC", shortLabel: "Prezzi e Filtro", desc: "Prezzi USD 2026 e confronto Pure vs Originali CMC" },
    ];
    const activePage = pages.find(p => p.id === normActive) || pages[0];

    let nav = document.querySelector("nav.agy-hub-nav");
    if (!nav) {
      nav = document.createElement("nav");
      nav.className = "agy-hub-nav";
      nav.setAttribute("aria-label", "Navigazione principale");
      document.body.insertBefore(nav, document.body.firstChild);
    }
    const linksHtml = pages.map(p => {
      const active = p.id === normActive ? " hub-active" : "";
      const extra = p.cls ? " " + p.cls : "";
      const aria = p.id === normActive ? ' aria-current="page"' : "";
      return `<a href="${p.href}" class="hub-pill${extra}${active}"${aria}><span class="nav-full">${p.label}</span><span class="nav-short">${p.shortLabel}</span></a>`;
    }).join("");

    const drawerLinksHtml = pages.map(p => {
      const active = p.id === normActive ? " is-active" : "";
      const aria = p.id === normActive ? ' aria-current="page"' : "";
      return `<a href="${p.href}" class="hub-drawer-item${active}"${aria}><span class="hub-drawer-title">${p.label}${p.id === normActive ? ' <span class="hub-drawer-cur">Corrente</span>' : ""}</span><span class="hub-drawer-desc">${p.desc}</span></a>`;
    }).join("");

    nav.innerHTML =
      `<div class="agy-hub-rail">${linksHtml}</div>` +
      `<div class="agy-mob-bar">` +
        `<a href="${activePage.href}" class="hub-pill hub-active agy-mob-cur" aria-current="page">${activePage.shortLabel}</a>` +
        `<button type="button" id="agyMenuToggle" class="hub-pill hub-menu-btn" aria-expanded="false" aria-controls="agyNavDrawer">${MENU_SVG}<span>Sezioni (6) &#9662;</span></button>` +
      `</div>` +
      `<div class="agy-hub-actions">` +
        `<button type="button" id="agyThemeToggle" class="hub-pill hub-theme" onclick="agyToggleTheme()"></button>` +
        `<a href="${REPO_URL}" target="_blank" rel="noopener" class="hub-pill hub-gh" aria-label="Apri codice sorgente su GitHub" title="Apri codice sorgente su GitHub">${GH_SVG}<span class="gh-txt"><span class="gh-lbl">Codice </span>GitHub &nearr;</span></a>` +
      `</div>` +
      `<div id="agyNavDrawer" class="agy-nav-drawer" hidden role="region" aria-label="Tutte le 6 sezioni del portale">${drawerLinksHtml}</div>`;

    const menuBtn = document.getElementById("agyMenuToggle");
    const drawer = document.getElementById("agyNavDrawer");
    if (menuBtn && drawer) {
      const setOpen = (open) => {
        drawer.hidden = !open;
        menuBtn.setAttribute("aria-expanded", open ? "true" : "false");
        nav.classList.toggle("drawer-open", open);
      };
      menuBtn.addEventListener("click", (e) => {
        e.stopPropagation();
        setOpen(drawer.hidden);
      });
      document.addEventListener("click", (e) => {
        if (!drawer.hidden && !nav.contains(e.target)) setOpen(false);
      });
      document.addEventListener("keydown", (e) => {
        if (e.key === "Escape" && !drawer.hidden) { setOpen(false); menuBtn.focus(); }
      });
    }

    let saved = "dark";
    try { saved = localStorage.getItem(THEME_KEY) || document.documentElement.getAttribute("data-theme") || "dark"; } catch (_) {}
    applyTheme(saved);

    const rail = nav.querySelector(".agy-hub-rail");
    const act = nav.querySelector(".agy-hub-rail .hub-active");
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
