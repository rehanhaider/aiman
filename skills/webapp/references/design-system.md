# Design system

Use one token system across the public site and the product. Change scale and
composition by surface; do not fork colors, fonts, or primitive behavior.

## Reference character

The target combines:

- Mizanic's measured public presentation: warm or neutral surfaces, wider
  composition, larger headings, 48px hero actions, restrained texture, and
  deliberate visual anchors.
- emcp's product clarity: near-monochrome surfaces, one accent, compact app
  controls, strong borders, simple elevation, and direct information layout.

Do not describe this as a generic Linear/Vercel aesthetic. Derive the visual
direction from the product, its content, and any reference the user provides.

## Tokens

Define light and dark values for:

1. Page, card, popover, muted, secondary, and accent surfaces plus their
   foregrounds.
2. Primary, destructive, border, input, and focus ring.
3. Sidebar surface, foreground, accent, border, and primary.
4. Semantic data tones for info, success, warning, violet, and cyan.

Use the CSS variable names created by shadcn so registry components and
ordinary Tailwind markup share the same language. Keep raw values in
`styles/app.css`; expose them
through `@theme inline`.

Use a single brand accent for product chrome. Data colors communicate status,
not a second brand palette. Choose neutrals deliberately:

- warm paper/off-black for editorial, advisory, or premium service brands;
- clean neutral gray for product-first SaaS;
- a faintly cool neutral only when the brand or content calls for it.

Do not default every project to navy.

## Typography

Bundle and import `@fontsource-variable/geist` and
`@fontsource-variable/geist-mono`; do not depend on Google Fonts at runtime.

- Product: `text-sm` body, `text-xs` metadata, `text-xl` page titles.
- Public: `text-base` or `text-lg` body, `text-4xl` through `text-7xl` hero,
  `text-3xl` through `text-5xl` section headings.
- Mono: identifiers, amounts, commands, measurements, and short eyebrows.
- Keep prose line length near 60–72 characters. A wide container does not
  mean wide paragraphs.

## Two spacing scales

### Product scale

| Element              | Default                             |
| -------------------- | ----------------------------------- |
| Top bar              | `h-12 px-4 sm:px-6`                 |
| Page frame           | `px-4 py-4 sm:px-6 sm:py-5`         |
| Page section gap     | `gap-4` to `gap-6`                  |
| Card content         | `p-4`; `p-5` for substantial panels |
| Table cell           | `px-3 py-2`                         |
| Default control      | `h-8`                               |
| Prominent app action | `h-9`                               |

Compact does not mean tiny. On mobile or coarse pointers, give interactive
targets a 44px hit area even when the visible control remains compact.

### Public scale

| Element              | Default                                                                |
| -------------------- | ---------------------------------------------------------------------- |
| Header               | `h-14` to `h-16`                                                       |
| Container            | `max-w-6xl` or `max-w-7xl`                                             |
| Side padding         | `px-5 sm:px-6 lg:px-8`                                                 |
| Hero padding         | `pt-20 pb-16 sm:pt-28 sm:pb-20`                                        |
| Section padding      | `py-20 md:py-24`                                                       |
| Card padding         | `p-5` for compact SaaS cards; `p-7 md:p-9` for editorial feature cards |
| Hero CTA             | `h-12 px-5 text-base`                                                  |
| Secondary public CTA | `h-10 px-5 text-sm`                                                    |

Never use the product button's `h-9` large variant for a hero CTA.

## Radius and elevation

Use approximately 8px for fields and app controls, 12px for app cards, and
14–16px for large public cards. Pills are reserved for chips, segmented
controls, and intentionally pill-shaped public navigation.

Use borders and surface changes for static separation. Use shadows for menus,
dialogs, floating navigation, and genuinely lifted public cards. Avoid a
uniform shadow on every card.

## Color transitions, gradients, and texture

Inside the product UI, keep surfaces flat. Avoid decorative gradients on
buttons, cards, tables, charts, and shell chrome.

On public pages, a controlled gradient or image wash is allowed when it has a
clear composition job: make text readable over imagery, separate a major
section, or create a restrained atmosphere. Keep it token-derived and local.
Do not use gradients as decoration on every section or CTA.

Grid, dot, and drafting-line textures may support a brand concept at low
contrast. Each page gets at most one or two such motifs. Avoid the generic
"dark grid plus glowing blobs" look.

## Motion

- Product overlays: 100–200ms fade/scale/slide.
- Public reveal: about 400–550ms with small travel; content must remain
  visible if JavaScript fails.
- Button response: subtle color/elevation change; no bouncy spring by default.
- Respect `prefers-reduced-motion` and never hide important content behind a
  reveal state without a safe fallback.

## Brand adaptation

Before writing page components, decide:

1. primary hue and matching light/dark values;
2. neutral temperature;
3. public theme behavior (system-aware, user-toggle, or deliberately pinned);
4. image/illustration direction;
5. public container width (`6xl` text-led or `7xl` image-led).

Ask the user when these choices would materially change the result and the
references do not answer them.
