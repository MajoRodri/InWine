/* ============================================================
   InWine — main.js
   Interactividad del frontend / Frontend interactivity
   ============================================================ */

"use strict";

/* ── Theme toggle ───────────────────────────────────────────── */
(function initTheme() {
  const btn  = document.getElementById("themeToggle");
  const root = document.documentElement;

  function applyTheme(dark) {
    root.setAttribute("data-theme", dark ? "dark" : "light");
    localStorage.setItem("inwine-theme", dark ? "dark" : "light");
  }

  // Initialize from localStorage (anti-flash script in <head> already set attribute)
  const saved = localStorage.getItem("inwine-theme");
  if (!saved) applyTheme(true); // default: dark

  btn?.addEventListener("click", () => {
    applyTheme(root.getAttribute("data-theme") !== "dark");
  });
})();

/* ── Navbar: oscurece al hacer scroll / Darkens on scroll ── */
(function initNavbar() {
  const nav = document.getElementById("navbar");
  if (!nav) return;

  const toggle = () => nav.classList.toggle("scrolled", window.scrollY > 50);
  window.addEventListener("scroll", toggle, { passive: true });
  toggle(); // estado inicial
})();

/* ── Menú hamburger (móvil) / Hamburger menu (mobile) ─────── */
(function initHamburger() {
  const btn   = document.getElementById("hamburger");
  const links = document.getElementById("navLinks");
  if (!btn || !links) return;

  btn.addEventListener("click", () => {
    const open = links.classList.toggle("open");
    // Animación de las 3 líneas / 3-line animation
    const [a, b, c] = btn.querySelectorAll("span");
    a.style.transform = open ? "rotate(45deg) translate(5px, 6px)" : "";
    b.style.opacity   = open ? "0" : "";
    c.style.transform = open ? "rotate(-45deg) translate(5px, -6px)" : "";
  });
})();

/* ── Formulario multi-paso / Multi-step form ───────────────── */
(function initMultiStep() {
  const form  = document.getElementById("recommendForm");
  if (!form) return;

  const steps     = form.querySelectorAll(".form-step");
  const dots      = document.querySelectorAll(".step-dot");
  const lines     = document.querySelectorAll(".step-line");
  let   current   = 0;

  function goTo(idx) {
    steps.forEach((s, i) => s.classList.toggle("active", i === idx));
    dots.forEach((d, i) => {
      d.classList.remove("active", "done");
      if (i < idx) d.classList.add("done");
      if (i === idx) d.classList.add("active");
    });
    lines.forEach((l, i) => l.classList.toggle("done", i < idx));
    current = idx;
  }

  // Botones siguiente/anterior / Next/prev buttons
  form.querySelectorAll(".btn-next").forEach(btn =>
    btn.addEventListener("click", () => { if (current < steps.length - 1) goTo(current + 1); })
  );
  form.querySelectorAll(".btn-prev").forEach(btn =>
    btn.addEventListener("click", () => { if (current > 0) goTo(current - 1); })
  );

  goTo(0);
})();

/* ── Slider de presupuesto / Budget slider ─────────────────── */
(function initBudgetSlider() {
  const range   = document.getElementById("budget");
  const display = document.getElementById("budgetDisplay");
  if (!range || !display) return;

  const update = () => { display.textContent = range.value + "€"; };
  range.addEventListener("input", update);
  update();
})();

/* ── Quiz de perfil / Profile quiz ─────────────────────────── */
(function initQuiz() {
  const steps    = document.querySelectorAll(".quiz-step");
  const fill     = document.querySelector(".quiz-progress-fill");
  const counter  = document.querySelector(".quiz-counter");
  const result   = document.querySelector(".profile-result");
  const quizForm = document.getElementById("quizForm");
  if (!steps.length) return;

  let current = 0;
  const answers = {};

  function showStep(idx) {
    steps.forEach((s, i) => s.classList.toggle("active", i === idx));
    if (fill)    fill.style.width = `${(idx / steps.length) * 100}%`;
    if (counter) counter.textContent = `${idx + 1} / ${steps.length}`;
    current = idx;
  }

  // Jerarquía de compatibilidad entre preguntas
  // step indices: Q1=0, Q2=1, Q3=2, Q4=3, Q5=4, Q6=5, Q7=6, Q8=7
  const FILTERS = [
    // Q1 (sabores) → Q2 (cuerpo)
    { trigger: 0, target: 1, map: {
      frutas_frescas: null,
      frutas_secas:   ["estructura", "cremoso"],
      especias:       ["estructura", "cremoso"],
      hierbas:        ["ligero", "estructura", "burbujas"],  // solo quita cremoso
      maderas:        ["estructura", "cremoso"],
    }},
    // Q2 (cuerpo) → Q6 (tipo de vino)
    { trigger: 1, target: 5, map: {
      ligero:     ["pref_blanco", "pref_tinto", "pref_espumoso"],
      estructura: ["pref_tinto", "pref_blanco", "pref_generoso"],
      cremoso:    ["pref_tinto", "pref_blanco", "pref_generoso"],
      burbujas:   ["pref_espumoso"],
    }},
    // Q5 (cocina) → Q6 (tipo de vino): solo mariscos oculta tinto
    { trigger: 4, target: 5, map: {
      mediterranea: null,
      carnes:       null,
      mariscos:     ["pref_blanco", "pref_espumoso", "pref_generoso"],
      variada:      null,
    }},
    // Q6 (tipo de vino) → Q7 (carácter)
    { trigger: 5, target: 6, map: {
      pref_tinto:    ["car_joven", "car_barrica", "car_reserva"],
      pref_blanco:   null,
      pref_espumoso: ["car_espumoso"],
      pref_generoso: ["car_reserva"],
    }},
  ];

  // Calcula la intersección de todos los filtros activos para un paso destino
  function computeAllowed(targetIdx) {
    let result = null;
    FILTERS.forEach(f => {
      if (f.target !== targetIdx) return;
      const triggerAnswer = answers[f.trigger];
      if (triggerAnswer == null) return;
      const allowed = f.map[triggerAnswer];
      if (!allowed) return;
      result = result
        ? new Set([...result].filter(v => allowed.includes(v)))
        : new Set(allowed);
    });
    return result; // null = todas permitidas
  }

  function applyAllFilters(targetIdx) {
    const allowed = computeAllowed(targetIdx);
    const targetStep = steps[targetIdx];
    if (!targetStep) return;

    let invalidated = false;
    targetStep.querySelectorAll(".quiz-option").forEach(opt => {
      const isAllowed = !allowed || allowed.has(opt.dataset.value);
      opt.classList.toggle("quiz-option--disabled", !isAllowed);
      if (!isAllowed && opt.classList.contains("selected")) {
        opt.classList.remove("selected");
        invalidated = true;
      }
    });

    if (invalidated) {
      delete answers[targetIdx];
      const first = targetStep.querySelector(".quiz-option:not(.quiz-option--disabled)");
      if (first && quizForm) {
        const input = quizForm.querySelector(`[name="q${targetIdx + 1}"]`);
        if (input) input.value = first.dataset.value;
      }
      const downstream = new Set(FILTERS.filter(f => f.trigger === targetIdx).map(f => f.target));
      downstream.forEach(t => applyAllFilters(t));
    }
  }

  function applyFilter(triggerStep) {
    const targets = new Set(FILTERS.filter(f => f.trigger === triggerStep).map(f => f.target));
    targets.forEach(t => applyAllFilters(t));
  }

  // Al hacer clic en una opción / On option click
  document.querySelectorAll(".quiz-option").forEach(opt => {
    opt.addEventListener("click", () => {
      if (opt.classList.contains("quiz-option--disabled")) return;
      // Marcar seleccionado visualmente / Mark selected visually
      const parent = opt.closest(".quiz-step");
      parent.querySelectorAll(".quiz-option").forEach(o => o.classList.remove("selected"));
      opt.classList.add("selected");
      answers[current] = opt.dataset.value;
      applyFilter(current);

      // Avanzar tras una breve pausa / Advance after short pause
      setTimeout(() => {
        if (current < steps.length - 1) {
          showStep(current + 1);
        } else {
          // Último paso: enviar formulario / Last step: submit form
          if (quizForm) {
            // Rellenar inputs ocultos con las respuestas / Fill hidden inputs with answers
            Object.entries(answers).forEach(([step, val]) => {
              const input = quizForm.querySelector(`[name="q${parseInt(step) + 1}"]`);
              if (input) input.value = val;
            });
            quizForm.submit();
          }
          // Mostrar resultado si no hay form (vista previa) / Show result if no form
          if (!quizForm && result) {
            steps.forEach(s => s.classList.remove("active"));
            result.classList.add("show");
            if (fill) fill.style.width = "100%";
          }
        }
      }, 350);
    });
  });

  showStep(0);
})();

/* ── Selección de comida / Food selection ─────────────────── */
(function initFoodSelection() {
  const cards   = document.querySelectorAll(".food-card[data-food]");
  const hiddenInput = document.getElementById("selectedFood");
  const foodForm    = document.getElementById("foodForm");
  if (!cards.length) return;

  cards.forEach(card => {
    card.addEventListener("click", e => {
      e.preventDefault();
      cards.forEach(c => c.classList.remove("active"));
      card.classList.add("active");

      if (hiddenInput) hiddenInput.value = card.dataset.food;
      if (foodForm) foodForm.submit();
    });
  });
})();

/* ── Filtros de calidad-precio / Value page filters ────────── */
(function initValueFilters() {
  const range   = document.getElementById("maxBudget");
  const display = document.getElementById("maxBudgetDisplay");
  if (!range || !display) return;

  range.addEventListener("input", () => { display.textContent = range.value + "€"; });
})();

/* ── Scroll suave a anclas / Smooth scroll to anchors ──────── */
document.querySelectorAll('a[href^="#"]').forEach(a => {
  a.addEventListener("click", e => {
    const target = document.querySelector(a.getAttribute("href"));
    if (target) { e.preventDefault(); target.scrollIntoView({ behavior: "smooth" }); }
  });
});

/* ── Animación de entrada con IntersectionObserver ─────────── */
(function initFadeIn() {
  const elements = document.querySelectorAll(
    ".wine-card, .feature-card, .cluster-card, .card, .timeline-item, .food-card"
  );
  if (!elements.length) return;

  const obs = new IntersectionObserver(entries => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.style.opacity = "1";
        entry.target.style.transform = "translateY(0)";
      } else {
        entry.target.style.opacity = "0";
        entry.target.style.transform = "translateY(18px)";
      }
    });
  }, { threshold: 0.08 });

  elements.forEach(el => {
    el.style.opacity    = "0";
    el.style.transform  = "translateY(18px)";
    el.style.transition = "opacity 0.45s ease, transform 0.45s ease";
    obs.observe(el);
  });
})();

/* ── Reveal al hacer scroll — homepage sections ────────────── */
(function initScrollReveal() {
  const EASE = "cubic-bezier(0.25, 0.46, 0.45, 0.94)";
  const DUR  = "0.65s";

  // Oculta un elemento antes de animarlo / Hides element before animating
  function prepare(el, delayMs = 0) {
    el.style.opacity    = "0";
    el.style.transform  = "translateY(22px)";
    el.style.transition = `opacity ${DUR} ${EASE} ${delayMs}ms, transform ${DUR} ${EASE} ${delayMs}ms`;
  }

  // Revela el elemento / Reveals the element
  function reveal(el) {
    el.style.opacity   = "1";
    el.style.transform = "translateY(0)";
  }

  const obs = new IntersectionObserver(entries => {
    entries.forEach(e => {
      if (e.isIntersecting) { reveal(e.target); }
      else { prepare(e.target); }
    });
  }, { threshold: 0.07, rootMargin: "0px 0px -40px 0px" });

  // Elementos individuales / Individual elements
  document.querySelectorAll(
    ".section-header, .about-intro, .guide-tip-banner, .guide-phase, .guide-grape-group"
  ).forEach(el => { prepare(el); obs.observe(el); });

  // Tarjetas de tipos de vino — escalonadas / Wine type cards — staggered
  document.querySelectorAll(".guide-types .guide-type-card").forEach((el, i) => {
    prepare(el, i * 90);
    obs.observe(el);
  });

  // Pasos del "cómo funciona" — escalonados / How-it-works steps — staggered
  document.querySelectorAll(".how-steps .how-step").forEach((el, i) => {
    prepare(el, i * 90);
    obs.observe(el);
  });

  // Píldoras de uvas — escalonadas por grupo / Grape pills — staggered per group
  document.querySelectorAll(".guide-grape-pills").forEach(group => {
    group.querySelectorAll(".guide-grape-pill").forEach((el, i) => {
      prepare(el, i * 65);
      obs.observe(el);
    });
  });
})();

/* ── About — Donut SVG interactivo ─────────────────────────── */
(function initDonut() {
  const segs    = document.querySelectorAll(".donut-seg");
  const nEl     = document.getElementById("donut-center-n");
  const lblEl   = document.getElementById("donut-center-lbl");
  const legend  = document.querySelectorAll(".vine-donut-legend li");
  if (!segs.length || !nEl) return;

  const defaultN   = nEl.textContent;
  const defaultLbl = lblEl.textContent;

  segs.forEach((seg, i) => {
    seg.addEventListener("mouseenter", () => {
      nEl.textContent      = seg.dataset.count;
      nEl.setAttribute("fill", seg.getAttribute("fill"));
      lblEl.textContent    = seg.dataset.label;
      // Dim all other segments / Atenúa los demás segmentos
      segs.forEach((s, j) => { s.style.opacity = j === i ? "1" : "0.35"; });
      legend.forEach((li, j) => li.classList.toggle("active", j === i));
    });
    seg.addEventListener("mouseleave", () => {
      nEl.textContent = defaultN;
      nEl.setAttribute("fill", "var(--cream-raw, #F0E4CC)");
      lblEl.textContent = defaultLbl;
      segs.forEach(s  => { s.style.opacity = ""; });
      legend.forEach(li => li.classList.remove("active"));
    });
  });

  // Hover inverso desde la leyenda
  legend.forEach((li, i) => {
    li.addEventListener("mouseenter", () => segs[i]?.dispatchEvent(new Event("mouseenter")));
    li.addEventListener("mouseleave", () => segs[i]?.dispatchEvent(new Event("mouseleave")));
  });
})();

/* ── About — Curvas SVG: animación entrada ──────────────────── */
(function initPriceSvg() {
  const panels = document.querySelectorAll(".price-svg-panel");
  if (!panels.length) return;

  const obs = new IntersectionObserver(entries => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.querySelector(".price-svg")?.classList.add("animated");
        obs.unobserve(entry.target);
      }
    });
  }, { threshold: 0.3 });

  panels.forEach(p => obs.observe(p));
})();

/* ── Rueda de perfiles vinícolas / Profile wheel ────────────── */
(function initProfileWheel() {
  const wheel = document.getElementById("profilesWheel");
  if (!wheel) return;

  const btns   = wheel.querySelectorAll(".profile-circle-btn");
  const panels = document.querySelectorAll(".profile-panel");

  function activate(pid) {
    btns.forEach(b   => b.classList.toggle("active", b.dataset.pid === pid));
    panels.forEach(p => p.classList.toggle("active", p.id === "pp-" + pid));
  }

  btns.forEach(btn => btn.addEventListener("click", () => activate(btn.dataset.pid)));

  // Hover en desktop con pequeña latencia para evitar parpadeos
  let hoverTimer;
  btns.forEach(btn => {
    btn.addEventListener("mouseenter", () => {
      if (window.innerWidth > 700) {
        clearTimeout(hoverTimer);
        hoverTimer = setTimeout(() => activate(btn.dataset.pid), 170);
      }
    });
    btn.addEventListener("mouseleave", () => clearTimeout(hoverTimer));
  });

  // Activa automáticamente el perfil del usuario al cargar
  const matched = wheel.querySelector(".profile-circle-btn.is-match");
  if (matched) activate(matched.dataset.pid);
})();
