// Tabs: each `.tabs[data-sec]` bar controls the `.panel[data-sec]` with the
// same key. Videos load only when their panel is first shown, and hidden
// panels pause theirs.
function activate(sec: string, i: number) {
  document.querySelectorAll<HTMLButtonElement>(`.tabs[data-sec="${sec}"] .tab`).forEach((t) => {
    const on = Number(t.dataset.i) === i;
    t.setAttribute("aria-selected", String(on));
    t.tabIndex = on ? 0 : -1;
  });
  document.querySelectorAll<HTMLElement>(`.panel[data-sec="${sec}"] .panel-item`).forEach((p) => {
    const on = Number(p.dataset.i) === i;
    p.hidden = !on;
    p.querySelectorAll("video").forEach((v) => {
      if (on) {
        if (!v.getAttribute("src") && v.dataset.src) v.src = v.dataset.src;
        v.play().catch(() => {});
      } else {
        v.pause();
      }
    });
  });
}

document.querySelectorAll<HTMLElement>(".tabs").forEach((bar) => {
  const sec = bar.dataset.sec!;
  bar.addEventListener("click", (e) => {
    const b = (e.target as Element).closest<HTMLButtonElement>(".tab");
    if (b) activate(sec, Number(b.dataset.i));
  });
  bar.addEventListener("keydown", (e) => {
    const tabs = [...bar.querySelectorAll<HTMLButtonElement>(".tab")];
    const cur = tabs.findIndex((t) => t.getAttribute("aria-selected") === "true");
    const step = { ArrowRight: 1, ArrowLeft: -1 }[e.key];
    const next = step === undefined ? -1 : cur + step;
    if (next >= 0 && next < tabs.length) {
      e.preventDefault();
      tabs[next].focus();
      activate(sec, Number(tabs[next].dataset.i));
    }
  });
});

// Start a section's first video only once it scrolls near the viewport.
const panels = document.querySelectorAll<HTMLElement>(".panel[data-sec]");
if ("IntersectionObserver" in window) {
  const io = new IntersectionObserver(
    (entries) => {
      for (const en of entries) {
        if (!en.isIntersecting) continue;
        const el = en.target as HTMLElement;
        const sel = document.querySelector<HTMLElement>(`.tabs[data-sec="${el.dataset.sec}"] .tab[aria-selected="true"]`);
        activate(el.dataset.sec!, sel ? Number(sel.dataset.i) : 0);
        io.unobserve(el);
      }
    },
    { rootMargin: "250px" },
  );
  panels.forEach((p) => io.observe(p));
} else {
  panels.forEach((p) => activate(p.dataset.sec!, 0));
}

// Bar charts grow in when they scroll into view (CSS handles the motion).
const charts = document.querySelectorAll<HTMLElement>(".qchart");
if ("IntersectionObserver" in window) {
  const io = new IntersectionObserver(
    (entries) => {
      for (const en of entries) {
        if (!en.isIntersecting) continue;
        en.target.classList.add("in");
        io.unobserve(en.target);
      }
    },
    { threshold: 0.35 },
  );
  charts.forEach((c) => io.observe(c));
} else {
  charts.forEach((c) => c.classList.add("in"));
}

const tip = document.getElementById("qtip");
if (tip) {
  document.querySelectorAll<SVGRectElement>(".qchart rect.bar").forEach((r) => {
    r.addEventListener("mousemove", (e) => {
      tip.textContent = r.dataset.tip ?? "";
      tip.style.left = `${e.clientX + 12}px`;
      tip.style.top = `${e.clientY - 34}px`;
      tip.style.opacity = "1";
    });
    r.addEventListener("mouseleave", () => {
      tip.style.opacity = "0";
    });
  });
}

const copy = document.getElementById("copy-bibtex");
const bib = document.getElementById("bibtex");
copy?.addEventListener("click", async () => {
  try {
    await navigator.clipboard.writeText(bib?.textContent ?? "");
    copy.textContent = "copied";
  } catch {
    // Clipboard API unavailable (e.g. plain http): select the entry instead.
    if (bib) window.getSelection()?.selectAllChildren(bib);
    copy.textContent = "selected";
  }
  setTimeout(() => (copy.textContent = "copy"), 1600);
});
