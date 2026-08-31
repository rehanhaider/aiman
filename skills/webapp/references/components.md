# Components

Install official shadcn/ui components with the Base UI option. Keep product and
marketing composition outside `components/ui`.

## Primitive rules

- Run `shadcn add <component>` instead of writing a primitive from memory.
- Use `shadcn docs <component>` when the component API is unfamiliar.
- Preserve the generated component API, slots, accessibility, and state
  handling when applying house styles.
- Compose classes with `cn()`; use CVA only for meaningful variants.
- Keep semantic token classes in components; never use raw Tailwind palette
  colors for shared UI.
- Import one component by its file path. Avoid a barrel for the primitive set.
- Never import `@base-ui/react` from routes, feature components, or composites.
  Such imports belong only inside shadcn-generated component source.

Do not maintain a parallel bundled primitive library. Install only what the
current application uses.

## Button scale

The Button component deliberately contains two scales:

| Size      | Height | Use                        |
| --------- | ------ | -------------------------- |
| `xs`      | 24px   | rare dense inline actions  |
| `sm`      | 28px   | compact table/tool actions |
| `default` | 32px   | ordinary product controls  |
| `lg`      | 36px   | prominent product actions  |
| `cta`     | 40px   | normal public actions      |
| `cta-lg`  | 48px   | hero/final primary CTA     |

Use corresponding icon-only sizes. Keep mobile hit targets at least 44px via
the control itself or a larger interactive wrapper.

Do not reinterpret `lg` as a marketing size. SnapNews looked undersized
because a 36px app button was used as a hero CTA.

After installing `button` with the CLI, extend its generated CVA size map with
`cta: "h-10 px-5"` and `cta-lg: "h-12 px-6"`. This is a house-style change to
shadcn-owned local source, not a replacement Button implementation.

## Inputs and selects

Product inputs default to 32px. Public signup/contact forms normally use
40–44px fields. Keep text at 16px on narrow screens to avoid browser zoom;
reduce to `text-sm` on desktop when appropriate.

Always render a visible label. Use description and error slots when a field
needs them; do not rely on placeholder text as the label.

Use the shadcn Select for rich option content or controlled popups. A styled
native `<select>` is acceptable for a short ordinary list when native mobile
behavior is preferable.

## Cards and repeated structure

Use three composition levels:

1. Primitive `Card`: surface, border/ring, radius, internal slots.
2. Product composites: `PageHeader`, `SectionCard`, `EmptyState`, `Field`,
   and table shells from `assets/components/ui.tsx`.
3. Public composites: `MarketingContainer`, `MarketingSection`,
   `MarketingEyebrow`, and `MarketingSectionHeading` from
   `assets/components/marketing.tsx`.

Do not make every public section a grid of identical icon cards. Change the
composition when the information changes: split layout, proof strip, stat
rules, screenshot, comparison, timeline, editorial feature, or CTA band.

## Dialogs and destructive actions

- Confirmation and destructive decisions: Alert Dialog.
- Forms and ordinary overlays: Dialog.
- Mobile navigation or side panels: Sheet.
- Keep open state controlled by the owning composite.
- Let form content unmount after close when state should reset.
- Constrain tall bodies and keep actions visible.

Use a token surface, border, and strong overlay shadow. Backdrop opacity must
preserve context without competing with the dialog.

## Tables

Use semantic `<table>` markup for simple read-only grids. Use TanStack Table
when columns, sorting, selection, pagination, or visibility become stateful.

Create one shared DataTable per app family, not a bespoke table per route.
Column definitions live near the domain route. The shared shell owns header
rendering, empty state, loading rows, pagination chrome, and selection hooks.

## Status and badges

Use `chipClass()` and `dotClass()` from `lib/colors.ts` for domain state. Keep
their class maps literal so Tailwind detects them. Use Badge for interface
labels such as Beta, count, or role.

Do not use the primary brand color for every status.

## Loading, empty, and error

- Content loading: skeleton rows or blocks that match final layout.
- Button submission: small inline spinner.
- Empty: specific title, one helpful sentence, optional next action.
- Error: plain-language cause when known, retry where useful, and preserve
  already-entered form state.

Avoid a page-level spinner for content that can show a stable shell.

## Icons

Use Lucide by default and one consistent stroke weight. Product icons are
normally 14–16px; public feature icons may be 20–40px when they carry real
hierarchy. Icon-only controls need an accessible label and usually a tooltip.

## Motion and states

Use the state attributes exposed by the installed shadcn component. Keep
overlay transitions 100–200ms. Public components may use longer reveal motion,
but never start as permanently invisible before JavaScript initializes.

Every shared component must be checked in hover, focus, active, disabled,
invalid, loading, dark, light, mobile, and reduced-motion states where those
states apply.
