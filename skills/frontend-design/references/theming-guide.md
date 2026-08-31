# Theming Guide

## Color Philosophy

The design system uses DaisyUI v5 semantic tokens declared via `@plugin "daisyui/theme"` in CSS. Colors use the oklch color space for perceptual uniformity. Never use raw Tailwind color utilities.

## DaisyUI v5 Theme Declaration

Themes live in `src/styles/global.css`, not in `tailwind.config.mjs`:

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
  /* ... remaining tokens ... */
}

@plugin "daisyui/theme" {
  name: "brand-dark";
  prefersdark: true;
  color-scheme: "dark";
  --color-base-100: oklch(20% 0.02 250);
  /* ... remaining tokens ... */
}
```

### Required Theme Tokens

Every theme must define all of these:

| Token                       | Purpose                               |
| --------------------------- | ------------------------------------- |
| `--color-base-100`          | Primary background                    |
| `--color-base-200`          | Alternating section / card background |
| `--color-base-300`          | Borders, dividers                     |
| `--color-base-content`      | Primary text                          |
| `--color-primary`           | Brand accent, CTAs, links             |
| `--color-primary-content`   | Text on primary background            |
| `--color-secondary`         | Secondary accent                      |
| `--color-secondary-content` | Text on secondary background          |
| `--color-accent`            | Tertiary accent                       |
| `--color-accent-content`    | Text on accent background             |
| `--color-neutral`           | Neutral tone                          |
| `--color-neutral-content`   | Text on neutral background            |
| `--color-info`              | Informational alerts                  |
| `--color-success`           | Success states                        |
| `--color-warning`           | Warning states                        |
| `--color-error`             | Error states                          |

### Shape Tokens

```css
--radius-selector: 1rem;    /* pill-shaped toggles, chips */
--radius-field: 0.5rem;     /* inputs, textareas */
--radius-box: 0.25rem;      /* cards, containers */
--border: 1px;               /* default border width */
--depth: 1;                  /* shadow intensity (0-2) */
--noise: 0;                  /* texture noise (0 = clean) */
```

## oklch Primer

Format: `oklch(Lightness% Chroma Hue)`

| Parameter | Range  | Notes                         |
| --------- | ------ | ----------------------------- |
| Lightness | 0-100% | 0 = black, 100 = white        |
| Chroma    | 0-0.4  | 0 = gray, higher = more vivid |
| Hue       | 0-360  | Color wheel angle             |

### Light vs Dark Theme Strategy

| Token          | Light Theme                 | Dark Theme                            |
| -------------- | --------------------------- | ------------------------------------- |
| `base-100`     | High lightness (95-98%)     | Low lightness (18-22%)                |
| `base-200`     | Slightly lower (92-95%)     | Slightly higher (24-28%)              |
| `base-300`     | Lower still (88-92%)        | Higher still (30-35%)                 |
| `base-content` | Very low lightness (20-25%) | Very high lightness (90-95%)          |
| `primary`      | Medium lightness (45-55%)   | Slightly higher (58-65%) for contrast |

Keep the hue and chroma similar between light/dark variants of the same token — only shift lightness.

## Text Opacity Conventions

| Class                  | Purpose                  | Example                  |
| ---------------------- | ------------------------ | ------------------------ |
| `text-base-content`    | Headings, primary text   | Page titles, card titles |
| `text-base-content/80` | Body paragraphs          | Main content text        |
| `text-base-content/70` | Subtitles, descriptions  | Section subtitles        |
| `text-base-content/60` | Captions, secondary info | Footer links, metadata   |
| `text-base-content/50` | Fine print               | Copyright notices        |

## Contrast Requirements

Follow WCAG AA minimum contrast ratios:
- **Normal text** (< 18px): 4.5:1 against background
- **Large text** (>= 18px bold or >= 24px): 3:1 against background
- **UI components** (borders, icons): 3:1 against background

When defining a dark theme, bump `primary` lightness up ~10-15% to maintain contrast against the dark base.

## Rebranding Workflow

To rebrand for a new project:

1. Pick a primary hue (0-360) that represents the brand
2. Copy the theme template from SKILL.md
3. Set the hue angle on all color tokens (keep chroma/lightness patterns)
4. Adjust `primary` and `secondary` chroma for vibrancy
5. Create both light and dark variants
6. Test with DaisyUI's component preview or the live site
7. Verify contrast ratios

### Hue Reference

| Hue Range | Color Family  | Associations                   |
| --------- | ------------- | ------------------------------ |
| 0-30      | Red           | Energy, urgency, health        |
| 30-70     | Orange/Gold   | Warmth, friendliness           |
| 70-110    | Yellow/Green  | Optimism, growth               |
| 110-170   | Green         | Nature, health, success        |
| 170-210   | Cyan/Teal     | Trust, calm, technology        |
| 210-260   | Blue          | Professional, trust, stability |
| 260-310   | Purple/Violet | Creativity, luxury             |
| 310-360   | Magenta/Pink  | Playful, feminine              |

## Anti-Flash Script

Prevents the wrong theme from showing during page load. Place in `<head>` before any stylesheet:

```html
<script is:inline>
  (function() {
    var t = localStorage.getItem('theme');
    if (!t) t = window.matchMedia('(prefers-color-scheme: dark)').matches ? 'brand-dark' : 'brand-light';
    document.documentElement.setAttribute('data-theme', t);
  })();
</script>
```

Update the theme names (`brand-dark`, `brand-light`) to match your `@plugin "daisyui/theme"` `name` values.

## Global Transitions

Add to `global.css` for smooth theme switching:

```css
* {
  transition:
    background-color 0.2s ease,
    color 0.2s ease,
    border-color 0.2s ease;
}
```

## Spacing Rhythm

Maintain consistent vertical rhythm:

| Context                       | Spacing                     |
| ----------------------------- | --------------------------- |
| Between major sections        | `py-16 md:py-24`            |
| Section heading to content    | `mb-12`                     |
| Between card grid items       | `gap-6 md:gap-8`            |
| Between stacked text elements | `mb-4` to `mb-6`            |
| Inner card padding            | DaisyUI `card-body` default |
| Container max width           | `max-w-7xl`                 |
| Container horizontal padding  | `px-4 sm:px-6 lg:px-8`      |
