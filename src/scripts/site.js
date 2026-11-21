const reduceMotion = () =>
  window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;

let scrollBound = false;

function updateHeader() {
  const header = document.querySelector("[data-header]");
  if (header) header.classList.toggle("is-scrolled", window.scrollY > 80);
}

function bindHeaderScroll() {
  if (scrollBound) return;
  scrollBound = true;
  window.addEventListener("scroll", updateHeader, { passive: true });
  updateHeader();
}

function bindMenu() {
  const toggle = document.querySelector("[data-menu-toggle]");
  const nav = document.querySelector("[data-site-nav]");
  if (!toggle || !nav || toggle.dataset.bound === "1") return;
  toggle.dataset.bound = "1";
  const setOpen = (open) => {
    nav.classList.toggle("is-open", open);
    toggle.setAttribute("aria-expanded", String(open));
    document.body.classList.toggle("menu-open", open);
  };
  toggle.addEventListener("click", () => setOpen(!nav.classList.contains("is-open")));
  nav.querySelectorAll("a").forEach((link) => link.addEventListener("click", () => setOpen(false)));
}

function activeNav(id) {
  document.querySelectorAll("[data-nav]").forEach((link) => {
    link.classList.toggle("is-active", link.dataset.nav === id);
  });
  requestAnimationFrame(positionNavIndicator);
}

function positionNavIndicator() {
  const nav = document.querySelector("[data-site-nav]");
  const indicator = nav?.querySelector("[data-nav-indicator]");
  if (!nav || !indicator) return;
  if (getComputedStyle(nav).display === "none") {
    indicator.style.opacity = "0";
    return;
  }
  const active = nav.querySelector(".site-nav__link.is-active");
  if (!active) {
    indicator.style.opacity = "0";
    return;
  }
  indicator.style.opacity = "1";
  indicator.style.left = `${active.offsetLeft}px`;
  indicator.style.top = `${active.offsetTop + active.offsetHeight - 1}px`;
  indicator.style.width = `${active.offsetWidth}px`;
}

function positionWorksIndicator() {
  const indicator = document.querySelector("[data-works-indicator]");
  const tabs = indicator?.parentElement;
  if (!indicator || !tabs) return;
  const active = tabs.querySelector(".works-tab.is-active");
  if (!active) {
    indicator.style.opacity = "0";
    return;
  }
  indicator.style.opacity = "1";
  indicator.style.left = `${active.offsetLeft}px`;
  indicator.style.top = `${active.offsetTop + active.offsetHeight - 1}px`;
  indicator.style.width = `${active.offsetWidth}px`;
}

let resizeBound = false;
function bindResize() {
  if (resizeBound) return;
  resizeBound = true;
  window.addEventListener("resize", () => {
    positionNavIndicator();
    positionWorksIndicator();
  });
}

function bindNavObserver() {
  if (window.__ripNavObserver) window.__ripNavObserver.disconnect();
  const page = document.querySelector("[data-header]")?.dataset.page;
  if (page === "detail") {
    activeNav("works");
    return;
  }
  const sections = [...document.querySelectorAll("main section[id]")];
  if (!sections.length) return;
  const observer = new IntersectionObserver(
    (entries) => {
      const visible = entries
        .filter((entry) => entry.isIntersecting)
        .sort((a, b) => b.intersectionRatio - a.intersectionRatio);
      if (!visible.length) return;
      const id = visible[0].target.id;
      activeNav(id);
      if (id !== "top" && location.hash !== `#${id}`) {
        history.replaceState(null, "", `${location.pathname}${location.search}#${id}`);
      }
    },
    { rootMargin: "-42% 0px -52% 0px", threshold: [0, 0.1, 0.5] }
  );
  sections.forEach((section) => observer.observe(section));
  window.__ripNavObserver = observer;
}

function bindReveal() {
  const elements = [...document.querySelectorAll("[data-reveal]")].filter(
    (el) => el.dataset.revealBound !== "1"
  );
  if (!elements.length) return;
  elements.forEach((el) => {
    el.dataset.revealBound = "1";
  });
  if (reduceMotion() || !("IntersectionObserver" in window)) {
    elements.forEach((el) => {
      el.classList.add("is-visible");
    });
    return;
  }
  const observer = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        if (!entry.isIntersecting) return;
        entry.target.classList.add("is-visible");
        observer.unobserve(entry.target);
      });
    },
    { rootMargin: "0px 0px -12% 0px", threshold: 0.08 }
  );
  elements.forEach((el) => observer.observe(el));
}

function bindWorks() {
  const explorer = document.querySelector("[data-works-explorer]");
  if (!explorer || explorer.dataset.bound === "1") return;
  explorer.dataset.bound = "1";
  const cards = [...explorer.querySelectorAll("[data-work-card]")];
  const tabs = [...explorer.querySelectorAll("[data-filter]")];
  const participation = explorer.querySelector("[data-participation-filter]");
  const divider = explorer.querySelector("[data-works-divider]");
  const empty = explorer.querySelector("[data-works-empty]");
  let category = "ALL";

  const apply = () => {
    let shown = 0;
    for (const card of cards) {
      const catOk = category === "ALL" || card.dataset.category === category;
      const partOk =
        !participation ||
        participation.value === "ALL" ||
        card.dataset.participation === participation.value;
      const visible = catOk && partOk;
      card.hidden = !visible;
      if (visible) shown += 1;
    }
    const visibleCards = cards.filter((card) => !card.hidden);
    const hasFeatured = visibleCards.some((card) => card.dataset.featured === "true");
    const firstNormal = visibleCards.find((card) => card.dataset.featured !== "true");
    if (divider) {
      if (hasFeatured && firstNormal) {
        firstNormal.before(divider);
        divider.hidden = false;
      } else {
        divider.hidden = true;
      }
    }
    if (empty) empty.hidden = shown > 0;
    positionWorksIndicator();
  };

  tabs.forEach((tab) => {
    tab.addEventListener("click", () => {
      category = tab.dataset.filter || "ALL";
      tabs.forEach((item) => {
        const active = item === tab;
        item.classList.toggle("is-active", active);
        item.setAttribute("aria-pressed", String(active));
      });
      apply();
    });
  });
  participation?.addEventListener("change", apply);
  cards.forEach((card) => {
    card.addEventListener("click", () => {
      sessionStorage.setItem("rip-works-scroll", String(window.scrollY));
    });
  });
  apply();
}

function bindHomeWorkLinks() {
  if (!document.body.classList.contains("page-home")) return;
  document.querySelectorAll('a[href*="/works/"]').forEach((link) => {
    if (link.dataset.boundScroll === "1") return;
    link.dataset.boundScroll = "1";
    link.addEventListener("click", () => {
      sessionStorage.setItem("rip-works-scroll", String(window.scrollY));
    });
  });
}

function bindBackWorks() {
  const back = document.querySelector("[data-back-works]");
  if (!back || back.dataset.bound === "1") return;
  back.dataset.bound = "1";
  back.addEventListener("click", () => {
    sessionStorage.setItem("rip-return-works", "1");
  });
}

function restoreWorksScroll() {
  if (sessionStorage.getItem("rip-return-works") !== "1") return;
  if (location.hash !== "#works") return;
  const target = Number(sessionStorage.getItem("rip-works-scroll") || "0");
  sessionStorage.removeItem("rip-return-works");
  window.setTimeout(() => {
    window.scrollTo({ top: target, behavior: "instant" });
  }, 80);
}

function langHref(lang) {
  const base = document.documentElement.dataset.base || "/";
  const normalizedBase = base.endsWith("/") ? base : `${base}/`;
  const match = location.pathname.match(/\/works\/([^/]+)\/?$/);
  if (match) {
    return `${normalizedBase}${lang === "ja" ? "" : `${lang}/`}works/${match[1]}/`;
  }
  return `${normalizedBase}${lang === "ja" ? "" : `${lang}/`}${location.hash || ""}`;
}

function bindLanguageLinks() {
  document.querySelectorAll("[data-lang-link]").forEach((link) => {
    const lang = link.dataset.langLink;
    if (!lang || link.dataset.bound === "1") return;
    link.dataset.bound = "1";
    const update = () => {
      link.setAttribute("href", langHref(lang));
    };
    update();
    link.addEventListener("pointerenter", update);
    link.addEventListener("focus", update);
    link.addEventListener("click", update);
  });
}

function fallbackCopy(text) {
  const textarea = document.createElement("textarea");
  textarea.value = text;
  textarea.setAttribute("readonly", "");
  textarea.style.position = "fixed";
  textarea.style.opacity = "0";
  document.body.appendChild(textarea);
  textarea.select();
  try {
    document.execCommand("copy");
  } finally {
    textarea.remove();
  }
}

function bindCopyMail() {
  document.querySelectorAll("[data-copy-mail]").forEach((button) => {
    if (button.dataset.bound === "1") return;
    button.dataset.bound = "1";
    button.addEventListener("click", async () => {
      const mail = button.dataset.mail || "";
      const copiedLabel = button.dataset.copied || "COPIED";
      const original = button.textContent;
      try {
        if (navigator.clipboard?.writeText) await navigator.clipboard.writeText(mail);
        else fallbackCopy(mail);
        button.textContent = copiedLabel;
      } catch {
        fallbackCopy(mail);
        button.textContent = copiedLabel;
      }
      window.setTimeout(() => {
        button.textContent = original;
      }, 1600);
    });
  });
}

function bindLightbox() {
  const dialog = document.querySelector("[data-lightbox-dialog]");
  if (!dialog || dialog.dataset.bound === "1") return;
  const image = dialog.querySelector("[data-lightbox-image]");
  const caption = dialog.querySelector("[data-lightbox-caption]");
  const triggers = [...document.querySelectorAll("[data-lightbox]")];
  if (!image || !triggers.length) return;
  dialog.dataset.bound = "1";
  let index = 0;
  const show = (nextIndex) => {
    index = (nextIndex + triggers.length) % triggers.length;
    const trigger = triggers[index];
    image.src = trigger.dataset.src || "";
    image.alt = trigger.dataset.alt || "";
    if (caption) caption.textContent = trigger.dataset.alt || "";
  };
  const open = (nextIndex) => {
    show(nextIndex);
    if (!dialog.open) dialog.showModal();
    document.body.classList.add("lightbox-open");
  };
  triggers.forEach((trigger, i) => {
    trigger.addEventListener("click", () => open(i));
  });
  dialog.querySelector("[data-lightbox-close]")?.addEventListener("click", () => dialog.close());
  dialog.querySelector("[data-lightbox-prev]")?.addEventListener("click", () => show(index - 1));
  dialog.querySelector("[data-lightbox-next]")?.addEventListener("click", () => show(index + 1));
  dialog.addEventListener("click", (event) => {
    if (event.target === dialog) dialog.close();
  });
  dialog.addEventListener("close", () => document.body.classList.remove("lightbox-open"));
  dialog.addEventListener("keydown", (event) => {
    if (event.key === "ArrowLeft") show(index - 1);
    if (event.key === "ArrowRight") show(index + 1);
  });
}

function bindMiniPlayer() {
  const root = document.querySelector("[data-mini-player]");
  if (!root || root.dataset.bound === "1") return;
  root.dataset.bound = "1";
  const toggle = root.querySelector("[data-mini-toggle]");
  const panel = root.querySelector("[data-mini-panel]");
  if (!toggle || !panel) return;
  const setOpen = (open) => {
    root.classList.toggle("is-open", open);
    toggle.setAttribute("aria-expanded", String(open));
    panel.setAttribute("aria-hidden", String(!open));
  };
  toggle.addEventListener("click", () => setOpen(!root.classList.contains("is-open")));
  root.querySelector("[data-mini-close]")?.addEventListener("click", () => setOpen(false));
  document.addEventListener("click", (event) => {
    if (!root.classList.contains("is-open")) return;
    if (!root.contains(event.target)) setOpen(false);
  });
  document.addEventListener("keydown", (event) => {
    if (event.key === "Escape") setOpen(false);
  });
}

function bindArchiveColors() {
  document.querySelectorAll("[data-hex]").forEach((card) => {
    if (card.dataset.bound === "1") return;
    card.dataset.bound = "1";
    card.addEventListener("click", () => card.classList.toggle("is-revealed"));
  });
}

let cursorStarted = false;
function bindCursor() {
  if (cursorStarted) return;
  if (!window.matchMedia) return;
  if (!document.querySelector("[data-cursor]")) return;
  if (window.matchMedia("(pointer: coarse)").matches) return;
  if (window.matchMedia("(prefers-reduced-motion: reduce)").matches) return;
  cursorStarted = true;
  let x = window.innerWidth / 2;
  let y = window.innerHeight / 2;
  let tx = x;
  let ty = y;

  const cursor = () => document.querySelector("[data-cursor]");

  window.addEventListener(
    "pointermove",
    (event) => {
      const el = cursor();
      if (!el) return;
      tx = event.clientX;
      ty = event.clientY;
      el.classList.add("is-active");
    },
    { passive: true }
  );

  document.addEventListener("mouseleave", () => cursor()?.classList.remove("is-active"));
  document.addEventListener("mouseenter", () => cursor()?.classList.add("is-active"));

  document.addEventListener("pointerover", (event) => {
    const target = event.target;
    if (!(target instanceof Element)) return;
    if (target.closest("a,button,[data-hex]")) cursor()?.classList.add("is-hover");
  });
  document.addEventListener("pointerout", (event) => {
    const target = event.target;
    if (!(target instanceof Element)) return;
    if (target.closest("a,button,[data-hex]")) cursor()?.classList.remove("is-hover");
  });

  const tick = () => {
    x += (tx - x) * 0.18;
    y += (ty - y) * 0.18;
    const el = cursor();
    if (el) el.style.transform = `translate3d(${x}px, ${y}px, 0)`;
    requestAnimationFrame(tick);
  };
  requestAnimationFrame(tick);
}

function initPage() {
  document.body.classList.remove("menu-open");
  bindHeaderScroll();
  bindMenu();
  bindNavObserver();
  positionNavIndicator();
  positionWorksIndicator();
  bindResize();
  bindCursor();
  bindReveal();
  bindWorks();
  bindHomeWorkLinks();
  bindBackWorks();
  restoreWorksScroll();
  bindLanguageLinks();
  bindCopyMail();
  bindLightbox();
  bindMiniPlayer();
  bindArchiveColors();

  if (document.fonts?.ready) {
    document.fonts.ready.then(() => {
      positionNavIndicator();
      positionWorksIndicator();
    });
  }
}

document.addEventListener("astro:page-load", initPage);
if (document.readyState === "loading") {
  document.addEventListener("DOMContentLoaded", initPage);
} else {
  initPage();
}
