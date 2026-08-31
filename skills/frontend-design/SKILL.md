---
name: frontend-design
description: "Build production-grade frontend interfaces using Astro 6, React 19 islands, Tailwind CSS v4, and DaisyUI v5. Enforce strict theming (semantic tokens only, light/dark, anti-flash) and islands discipline, and apply design craft progressively via mode-based layers (Baseline, Design, Advanced) chosen by UI type. Also produces accompanying visuals: inline SVG state illustrations (empty, error, success, welcome) and JSON image-prompts for hero and marketing artwork. Default to Baseline when unsure. Use when the project runs on (or targets) this Astro + DaisyUI stack; for aesthetic-first standalone page builds with no stack constraint, prefer the hallmark skill."
---

# Frontend Design

Build production-quality web interfaces using Astro + React islands + Tailwind CSS v4 + DaisyUI v5. Every page and component must support light and dark themes.

**Routing vs. `hallmark`:** both skills can build landing pages. This skill owns work *inside* the Astro + DaisyUI system — repeatable, token-pure, team-maintainable UI. `hallmark` owns aesthetic-first, single-page editorial builds where the design direction is the deliverable and no stack constraint exists. If the user asks for a page in this repo's stack, stay here; if they ask for "a beautiful page" with no stack, hand to hallmark.

## Hybrid Goal (Keep Constraints, Add Craft)

Use the existing stack constraints and patterns as the **baseline**. Apply design craft **progressively** (Baseline/Design/Advanced) so outputs avoid generic template vibes while remaining maintainable, accessible, and fast.

### Hard Constraints (Do Not Violate)

- **Theming**: DaisyUI semantic tokens only (no raw Tailwind colors), **light + dark** themes, and the **anti-flash script** in layout `<head>`.
- **Astro first**: default to `.astro`; React islands only for interactivity with the most restrictive `client:*`.
- **Quality**: semantic HTML, keyboard/focus accessibility, and performance-safe effects.

## Tech Stack

| Layer     | Tool                       | Version | Role                                        |
| --------- | -------------------------- | ------- | ------------------------------------------- |
| Framework | Astro                      | 6.x     | Static pages, routing, layouts, SSG/SSR     |
| Islands   | React via `@astrojs/react` | 19.x    | Interactive components only                 |
| Styling   | Tailwind CSS               | 4.x     | Utility-first CSS (CSS-first config)        |
| Theme     | DaisyUI                    | 5.x     | Component classes, light/dark via `@plugin` |
| Icons     | Lucide React or Astro Icon | latest  | Consistent icon system                      |

### Version Verification (Required)

The versions above are **defaults for this skill**. Before generating code, verify the repo’s actual installed versions in `package.json` (and lockfile if needed). If they differ, follow the repo’s versions and adjust patterns accordingly (especially DaisyUI v5 CSS-first theming vs older approaches).

## When to Use React Islands

Default to **Astro components** (`.astro`). Only use React (`.tsx`) when the component needs:
- Client-side state (forms, toggles, modals, counters)
- Browser event handlers beyond simple links
- Third-party React libraries (charts, rich text editors)
- Real-time or frequently updating content

Always apply the most restrictive `client:*` directive:

| Directive        | Use when                                            |
| ---------------- | --------------------------------------------------- |
| `client:load`    | Immediately interactive (e.g., header nav dropdown) |
| `client:visible` | Below the fold (carousels, accordions)              |
| `client:idle`    | Non-critical (analytics widgets, chat)              |
| `client:media`   | Device-conditional (mobile menu)                    |

## Design Craft Layer (Mode-Based)

The core stack + theming + islands rules in this skill are **enforceable** and stay mandatory. The “design craft” parts below are **mode-based** to avoid brittle, forced outputs.

### Mode Selection (Default: Baseline)

| UI type                                  | Default mode | Notes                                                           |
| ---------------------------------------- | ------------ | --------------------------------------------------------------- |
| Marketing / landing / hero sections      | **Design**   | Add 1 safe anchor; motion is allowed but sparse                 |
| App UI (settings, forms, workflows)      | **Baseline** | Favor clarity; keep craft subtle and repeatable                 |
| Dashboards / tables / data-heavy screens | **Baseline** | Prioritize density, readability, states; no visual experiments  |
| Visual refresh / brand moment            | **Advanced** | Use a risk-scan + calibrated anchors; still respect constraints |

“Visual refresh / brand moment” means you’re explicitly changing the **aesthetic system** (theme tokens, hero identity, distinctive components). If you’re just assembling a standard marketing page with the existing system, prefer **Design** mode. If unsure, **Baseline**.

### Execution Gate (Enforced)

Before generating UI, you MUST:

1. **Identify the UI type** (marketing / app UI / dashboard-data / refresh).
2. **Select exactly one mode**: Baseline, Design, or Advanced (use the table above).
3. **State the choice explicitly** in one short line (UI type + mode).

If uncertain about UI type or the expected level of visual experimentation, **default to Baseline**.

### Baseline Mode (Always Safe)

- Use the existing **Design Language** patterns below.
- No risk scan. No “forced” differentiation.
- Optimize for clarity, scannability, and predictable reuse across a team.

Baseline mode MUST NOT:

- Introduce asymmetry/overlap/staggering beyond the existing patterns.
- Introduce custom motion beyond standard hover/focus transitions.
- Introduce decorative elements (textures, flourishes, “anchor” concepts) beyond the existing patterns.
- Use the custom-CSS escape hatch.

### Design Mode (Recommended for Marketing)

In Design mode, do these (briefly) before coding:

1. **Direction**: name a stance (e.g. *editorial minimal*, *industrial utilitarian*, *quiet luxury*, *retro-tech*).
2. **Purpose**: what action should the UI enable?
3. **One differentiation anchor** (pick 1 category below) with guardrails.
4. **Constraint check**: light/dark, semantic tokens, Astro-first + islands discipline, accessibility/performance.

#### Differentiation Anchors (Pick One, Keep It Safe)

If uncertain, default to **Typography anchor** (safest, most reusable).

- **Typography anchor**: a distinctive kicker/label system, numerals treatment (`tabular-nums`), or headline rhythm that stays within the existing scale.
- **Layout anchor**: a controlled asymmetry at `lg+` that collapses cleanly on mobile (no overlap that breaks reading order).
- **Interaction anchor**: one meaningful micro-interaction (state clarity, guided focus, crisp hover/focus affordances). CSS-first, `prefers-reduced-motion` respected.
- **Content anchor**: “editorial” section labeling, narrative dividers, or structured copy rhythm (no visual gimmicks required).
- **Component-shape anchor**: a consistent border/radius/divider motif that’s used across sections (theme-driven).

#### Anchor Guardrails (Prevent Gimmicks)

- **Max 1 anchor per page** (or per major screen). Call it out explicitly.
- **Max 1 entrance animation motif** per page. Prefer `opacity` + `transform` only.
- **Max 1 texture/depth motif** per page (often none). Avoid heavy gradients/glows.
- Must work in **light + dark** and with **keyboard/focus**.
- No new heavy client libraries to “make the anchor work.”

### Advanced Mode (Optional; Use for Big Visual Swings)

Advanced mode is for **new pages**, **hero redesigns**, or **brand refresh** work. It is explicitly optional because it’s subjective.

#### Advanced Risk Scan (Checklist, Not a Score)

Use this to **validate a proposed direction**, not to invent one. This is a checklist to avoid self-justifying “creative” decisions.

Optionally rate each 1–5, but **do not sum scores** and do not “optimize the number.” If anything feels forced or uncertain, **fall back** to Design or Baseline.

- **Impact**: will the direction be meaningfully distinctive, or is it just novelty?
- **Fit**: does it match audience + intent (trust vs play vs urgency)?
- **Feasibility**: can you implement it cleanly in Astro/Tailwind/DaisyUI without brittle hacks?
- **Performance safety**: will it stay fast and accessible (no heavy JS, no jank)?
- **Consistency risk**: can the pattern scale across screens without one-off snowflakes?

Rule of thumb: if **Feasibility ≤ 3** or **Performance ≤ 3** or **Consistency risk ≥ 4**, don’t do Advanced — reduce scope and use Baseline/Design patterns.

### Practical Guardrails (Actionable)

#### DaisyUI Tokens vs Distinctiveness (Escape Hatch)

- Stay “token-pure” in markup: use `bg-base-*`, `text-base-content`, `border-base-300`, `text-primary`, etc.
- If you need a new vibe, **change/extend the DaisyUI theme tokens in `global.css` (OKLCH)** rather than hardcoding colors in components.
- Custom CSS is allowed **only** in Design/Advanced mode to implement the chosen anchor, and must follow:
  - **Scoped root class**: all selectors must be prefixed by a single root class like `.anchor-*`
  - **Size limit**: keep it under ~50 lines
  - **No global selectors**: no `html`, `body`, `:root`, `*`, or unscoped element selectors
  - **Token-derived only**: no raw colors; reference DaisyUI theme variables/tokens only

#### Typography (Concrete Defaults)

- For long-form text blocks, use `max-w-prose` (≈ 65ch) and `leading-relaxed`.
- Keep the existing scale, but allow **one** repeatable signature move per page (e.g., kicker labels, numeric rhythm, or divider typography). Avoid stacking multiple flourishes.

#### Motion (Concrete Defaults)

- Hover/focus: **150–250ms**, `ease-out`/`ease-in-out` (`transition-colors`, `transition-shadow`, `transition-transform`).
- Entrances: **250–450ms**, `ease-out`, `opacity` + `transform` only.
- Always respect `prefers-reduced-motion` (use `motion-reduce:*` utilities).

#### Performance / Islands (Quantitative Defaults)

- Prefer **0–3 React islands per page**. More is OK if each island is small and justified; avoid many islands that each pull in heavy client JS.
- Prefer CSS-first interactions; avoid scroll-linked animations and layout-shifting transitions.
- Avoid adding large client-side libraries unless the user explicitly needs them.

Performance priority (highest → lowest):

1. Avoid unnecessary React islands
2. Avoid layout shifts and expensive reflows
3. Avoid heavy JS libraries
4. Keep animations simple and respectful of reduced motion

### Output Structure (Only in Design/Advanced Mode)

When in Design or Advanced mode, output:

1. **Direction summary**: aesthetic name + 1–2 sentence rationale (+ optional risk-scan notes in Advanced mode).
2. **System snapshot** (short): tokens/variables touched, spacing rhythm, motion philosophy.
3. **Implementation**: working code (Astro by default; React islands only where needed).
4. **Anchor callout**: “This avoids generic UI by doing X instead of Y.”

Baseline mode output:

- Still state the chosen **UI type + mode** (one short line).
- Then return **implementation only**.
- Do not include direction/risk-scan/anchor callouts in Baseline mode.

### Operator Checklist (Mode-Aware)

- [ ] Constraints satisfied (themes, tokens, anti-flash, islands discipline)
- [ ] Mode chosen appropriately for UI type
- [ ] If Design/Advanced: exactly one anchor category selected and guarded
- [ ] Accessibility (contrast, focus, keyboard) and performance-safe

## Design Language

A clean, professional marketing-site aesthetic: generous whitespace, card-driven structure, one strong headline per section, subtle depth over decoration.

### Patterns Are Defaults (Not Templates)

The patterns below are **default implementations** that make Baseline mode reliable and consistent.

- **Baseline mode**: treat these as the *defaults*. Only change content/copy and small spacing within the existing structure.
- **Design mode**: start from a default pattern, then diverge **intentionally** only to support the chosen anchor. State what you changed and why.
- **Advanced mode**: patterns are starting points; divergence must still respect constraints and should avoid bespoke CSS unless it meets the escape-hatch rules.

If a “layout anchor” conflicts with a default pattern, you may change the layout in Design/Advanced mode — but keep semantics, responsiveness, theming tokens, and accessibility intact.

### Core Principles

1. **Generous whitespace** — Sections breathe. Use `py-16 md:py-24` between sections minimum.
2. **Card-driven layouts** — Services, features, content blocks live in cards with subtle borders or shadows.
3. **Strong visual hierarchy** — One clear headline per section, supporting subtitle, then content.
4. **Purposeful CTAs** — Primary and secondary buttons with clear visual weight difference.
5. **Responsive grids** — 1 col mobile, 2 col tablet, 3 col desktop for card grids.
6. **Subtle depth** — Light shadows and borders, no heavy drop shadows or gradients.
7. **Consistent spacing** — Stick to Tailwind's spacing scale; avoid arbitrary values.

### Typography Scale

```
Headline (h1):   text-4xl md:text-5xl lg:text-6xl font-bold tracking-tight
Section (h2):    text-3xl md:text-4xl font-bold
Subsection (h3): text-xl md:text-2xl font-semibold
Minor (h4):      text-lg font-semibold
Micro (h5/h6):   text-base font-semibold
Body:            text-base md:text-lg text-base-content/80
Small/Caption:   text-sm text-base-content/60
```

### Semantic Heading Mapping (Operational)

- Use **one** `h1` per page (hero/title).
- Use `h2` for major sections, `h3` for subsection/card headings, `h4–h6` for nested headings.
- Never pick heading tags by size alone — keep the document outline correct.

### Long-Form Text Width (How to Use `max-w-prose`)

`max-w-prose` is for readable line length inside the normal `max-w-7xl` layout. Nest it:

```astro
<div class="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
  <div class="mx-auto max-w-prose">
    <!-- long-form content -->
  </div>
</div>
```

### Default Section Anatomy

Default purpose: **repeatable section hierarchy** (label → headline → subtitle → content) with low design risk.

Every major page section follows this pattern:

```astro
<section class="py-16 md:py-24 bg-base-100">
  <div class="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
    <p class="mb-4 text-center text-sm font-medium uppercase tracking-wider text-primary">
      Section Label
    </p>
    <h2 class="mb-4 text-center text-3xl font-bold text-base-content md:text-4xl">
      Section Headline
    </h2>
    <p class="mx-auto mb-12 max-w-2xl text-center text-lg text-base-content/70">
      Supporting description.
    </p>
    <div class="grid grid-cols-1 gap-6 md:grid-cols-2 md:gap-8 lg:grid-cols-3">
      <!-- cards / content -->
    </div>
  </div>
</section>
```

Alternate section backgrounds between `bg-base-100` and `bg-base-200` for visual rhythm.

Design/Advanced variations (pick one; keep the same hierarchy):

- Left-align the heading/subtitle on `lg+` and keep centered on mobile if it improves scanning.
- Use a split layout on `lg+` (heading column + content column) while keeping the same semantic structure.

### Default Card Pattern

```astro
<div class="card border border-base-300 bg-base-100 shadow-sm transition-shadow duration-200 hover:shadow-md">
  <div class="card-body">
    <div class="mb-4 flex h-12 w-12 items-center justify-center rounded-lg bg-primary/10">
      <!-- icon -->
    </div>
    <h3 class="card-title text-xl font-semibold text-base-content">Title</h3>
    <p class="text-base-content/70">Description text.</p>
    <div class="card-actions mt-4 justify-start">
      <a href="/learn-more" class="link link-primary font-medium">Learn more &rarr;</a>
    </div>
  </div>
</div>
```

Default purpose: **scannable feature/service blocks** with consistent hierarchy.

Design/Advanced variations (choose at most one):

- Remove the icon wrapper if content is the focus (keep hierarchy strong).
- Swap the bottom link for a secondary button (`btn btn-ghost btn-sm`) when the action matters.
- Make the whole card clickable only if it remains accessible (proper link semantics + focus ring).

### Hero Pattern

```astro
<section class="flex min-h-[80vh] items-center bg-base-100">
  <div class="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
    <div class="max-w-5xl">
      <h1 class="mb-6 text-4xl font-bold tracking-tight text-base-content md:text-5xl lg:text-6xl">
        Headline with <span class="text-primary">accent</span>
      </h1>
      <p class="mb-8 max-w-2xl text-lg text-base-content/70 md:text-xl">
        Value proposition paragraph.
      </p>
      <div class="flex flex-wrap gap-4">
        <a href="/cta" class="btn btn-primary btn-lg">Primary Action</a>
        <a href="/secondary" class="btn btn-outline btn-lg">Secondary Action</a>
      </div>
    </div>
  </div>
</section>
```

Default purpose: **establish hierarchy fast** (headline → value prop → CTA) with minimal visual risk.

Design/Advanced variations (pick one; keep mobile stacked):

- Convert to a two-column hero on `lg+` (copy + supporting media/illustration) while preserving the same hierarchy.
- Change alignment (`text-left` → `text-center`) only if it serves the direction and doesn’t reduce readability.
- Adjust the height target (`min-h-[70vh]` to `min-h-[85vh]`) based on content density; avoid empty “hero air.”

### Stats Row

```astro
<div class="grid grid-cols-2 gap-8 border-y border-base-300 py-12 md:grid-cols-4">
  <div class="text-center">
    <p class="text-3xl font-bold text-primary md:text-4xl">99.9%</p>
    <p class="mt-1 text-sm text-base-content/60">Uptime SLA</p>
  </div>
</div>
```

Default purpose: **credible proof** in a compact, skimmable row.

### CTA Section

```astro
<section class="bg-primary py-16 text-primary-content md:py-24">
  <div class="mx-auto max-w-7xl px-4 text-center">
    <h2 class="mb-4 text-3xl font-bold md:text-4xl">Ready to get started?</h2>
    <p class="mx-auto mb-8 max-w-xl text-lg opacity-90">Supporting text.</p>
    <div class="flex flex-wrap justify-center gap-4">
      <a href="/contact" class="btn btn-secondary btn-lg">Get in Touch</a>
      <a href="/learn" class="btn btn-ghost btn-lg border border-primary-content/20">Learn More</a>
    </div>
  </div>
</section>
```

Default purpose: **high-contrast close** that is readable in both themes.

### State Illustrations and Imagery

Empty, error, success, and welcome states usually need a visual to carry the moment. Hero and marketing surfaces sometimes need richer artwork. Two routes:

- **Inline SVG** for state illustrations and icons. Recolour via `currentColor` so DaisyUI semantic tokens (`text-primary`, `text-base-content`, `text-error`) drive the fill across both themes. Ready-made starters live in `assets/` (`empty-state.svg`, `error-state.svg`, `success-state.svg`, `welcome-state.svg`).
- **JSON image-prompt** for hero illustrations or photography. Lock palette, framing, and exclusions in a structured prompt rather than a freeform sentence. Pull palette values from the `global.css` theme tokens.

For the full schema, rules, and worked examples, see [references/graphics.md](references/graphics.md).

Mode notes: Baseline uses the bundled SVGs as-is. Design mode tailors a single on-brand SVG or generates one illustration. Advanced mode is where art-directed hero imagery belongs — confirm contrast against both themes before shipping.

## Theming & Dark Mode

### DaisyUI v5 Configuration (CSS-first)

Themes are declared in `global.css` using `@plugin` directives — **not** in `tailwind.config.mjs`:

```css
@import "tailwindcss";

@plugin "daisyui" {
  themes: brand-light --default, brand-dark;
}

@plugin "daisyui/theme" {
  name: "brand-light";
  prefersdark: false;
  color-scheme: "light";
  --color-base-100: oklch(98% 0.01 250);
  --color-base-200: oklch(95.5% 0.015 250);
  --color-base-300: oklch(90% 0.02 250);
  --color-base-content: oklch(22% 0.02 250);
  --color-primary: oklch(50% 0.18 250);
  --color-primary-content: oklch(98% 0.008 250);
  --color-secondary: oklch(55% 0.16 300);
  --color-secondary-content: oklch(98% 0.01 300);
  --color-accent: oklch(60% 0.14 180);
  --color-accent-content: oklch(98% 0.01 180);
  --color-neutral: oklch(35% 0.02 250);
  --color-neutral-content: oklch(98% 0.008 250);
  --color-info: oklch(60% 0.16 235);
  --color-success: oklch(64% 0.15 155);
  --color-warning: oklch(75% 0.16 70);
  --color-error: oklch(60% 0.2 25);
  --radius-selector: 1rem;
  --radius-field: 0.5rem;
  --radius-box: 0.25rem;
  --border: 1px;
  --depth: 1;
  --noise: 0;
}

@plugin "daisyui/theme" {
  name: "brand-dark";
  prefersdark: true;
  color-scheme: "dark";
  --color-base-100: oklch(20% 0.02 250);
  --color-base-200: oklch(25% 0.025 250);
  --color-base-300: oklch(32% 0.03 250);
  --color-base-content: oklch(92% 0.01 250);
  --color-primary: oklch(62% 0.2 250);
  --color-primary-content: oklch(98% 0.008 250);
  --color-secondary: oklch(65% 0.18 300);
  --color-secondary-content: oklch(98% 0.01 300);
  --color-accent: oklch(68% 0.14 180);
  --color-accent-content: oklch(98% 0.01 180);
  --color-neutral: oklch(35% 0.02 250);
  --color-neutral-content: oklch(98% 0.008 250);
  --color-info: oklch(65% 0.16 235);
  --color-success: oklch(68% 0.15 155);
  --color-warning: oklch(78% 0.16 70);
  --color-error: oklch(65% 0.2 25);
  --radius-selector: 1rem;
  --radius-field: 0.5rem;
  --radius-box: 0.25rem;
  --border: 1px;
  --depth: 1;
  --noise: 0;
}
```

### Theme Toggle (Prefer No Island)

Prefer an Astro component with an inline click handler so the global header stays fast and you avoid unnecessary hydration.

```astro
---
// src/components/ThemeToggle.astro
---
<button type="button" class="btn btn-ghost btn-circle" aria-label="Toggle theme" data-theme-toggle>
  <span aria-hidden="true">🌓</span>
</button>

<script is:inline>
  (function () {
    var LIGHT = 'brand-light';
    var DARK = 'brand-dark';

    function getCurrentTheme() {
      return document.documentElement.getAttribute('data-theme') || LIGHT;
    }

    function setTheme(theme) {
      localStorage.setItem('theme', theme);
      document.documentElement.setAttribute('data-theme', theme);
    }

    function toggleTheme() {
      var current = getCurrentTheme();
      setTheme(current === DARK ? LIGHT : DARK);
    }

    var buttons = document.querySelectorAll('[data-theme-toggle]');
    for (var i = 0; i < buttons.length; i++) {
      buttons[i].addEventListener('click', toggleTheme);
    }
  })();
</script>
```

If you must implement this as a React island (rare), only use `client:load` when it must be interactive immediately; otherwise prefer `client:idle`.

### Anti-Flash Script

Add as the **first script in `<head>`**, before any stylesheets or other scripts, to prevent theme flash on load:

```html
<script is:inline>
  (function() {
    var t = localStorage.getItem('theme');
    if (!t) t = window.matchMedia('(prefers-color-scheme: dark)').matches ? 'brand-dark' : 'brand-light';
    document.documentElement.setAttribute('data-theme', t);
  })();
</script>
```

### Color Usage Rules

- **Backgrounds**: `bg-base-100` (primary), `bg-base-200` (alt sections), `bg-base-300` (emphasis)
- **Text**: `text-base-content` (primary), `/80` (body), `/70` (subtitles), `/60` (captions), `/50` (fine print)
- **Borders**: `border-base-300` always
- **Accents**: `text-primary`, `bg-primary`, `btn-primary`
- **Never** use raw color classes like `text-gray-600` or `bg-white` — always use DaisyUI semantic tokens

## Project Structure

```
src/
├── layouts/
│   └── BaseLayout.astro       # html, head (anti-flash script), nav, footer
├── components/
│   ├── Header.astro            # Static nav, includes ThemeToggle (no island)
│   ├── Footer.astro
│   ├── Hero.astro
│   ├── SectionHeading.astro    # Reusable label + h2 + subtitle
│   ├── Card.astro
│   ├── ThemeToggle.astro       # Inline-script theme toggle (no island)
│   └── react/                  # React islands only (shared); co-locate feature-specific islands as needed
│       ├── ContactForm.tsx
│       └── MobileMenu.tsx
├── pages/
│   └── index.astro
└── styles/
    └── global.css              # @import "tailwindcss", @plugin themes
```

## Constraints

### MUST
- Use DaisyUI semantic color tokens exclusively (no raw Tailwind colors)
- Provide both light and dark theme definitions in `global.css`
- Include the anti-flash script as the **first script** in layout `<head>` (before stylesheets/other scripts)
- Default to Astro components; React only for interactivity
- Apply the most restrictive `client:*` directive for each island
- Use semantic HTML (`<section>`, `<nav>`, `<main>`, `<footer>`, `<article>`)
- Use `max-w-7xl` containers consistently
- Test appearance in both light and dark modes
- Use oklch color space in DaisyUI theme definitions

### MUST NOT
- Hardcode colors (`text-white`, `bg-gray-900`) — use semantic tokens
- Configure DaisyUI themes in `tailwind.config.mjs` (use CSS `@plugin` syntax)
- Wrap entire pages in React — isolate interactive pieces only
- Use `client:load` when `client:visible` or `client:idle` suffices
- Use arbitrary Tailwind values (`w-[347px]`) unless absolutely necessary
- Nest DaisyUI `data-theme` attributes inside each other

## Additional Resources

- For full component examples (navbar, footer, forms, grids), see [references/component-patterns.md](references/component-patterns.md)
- For detailed theming and color palette guidance, see [references/theming-guide.md](references/theming-guide.md)
- For state illustrations and image prompts (inline SVG, JSON prompts, ready-made assets), see [references/graphics.md](references/graphics.md)
- For Astro framework docs, use the Astro docs MCP: `search_astro_docs`