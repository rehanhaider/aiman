# Public and marketing routes

Public pages share the product's tokens and framework, but use their own
layout primitives and size scale.

## Route and build shape

Keep public routes at the root (`/`, `/pricing`, `/blog`, `/privacy`, etc.)
and the authenticated product under `/app/*` unless the product already has a
different established contract. Use TanStack Start prerendering for eligible
public routes; do not prerender authenticated or user-specific routes.

Create public composites under `src/components/marketing/`. Start with the
bundled `assets/components/marketing.tsx` layout primitives, then add
brand-specific header, footer, and visuals.

## Shell

- Sticky header: `h-14` to `h-16`, translucent or solid token surface,
  `max-w-6xl/7xl`, `px-5 sm:px-6 lg:px-8`.
- Desktop navigation: quiet text links; one clear primary action.
- Mobile navigation: shadcn Sheet or a simple controlled disclosure with
  full-width 44px targets.
- Footer: meaningful product/resource/legal groupings, not a repeated hero.

The public shell may follow the user's theme preference, use a system default,
or pin one deliberate theme. Decide explicitly; do not inherit product state
accidentally.

## Hero

Use this order when the content supports it:

1. optional mono eyebrow;
2. one clear H1;
3. short explanatory paragraph;
4. one primary and at most one secondary CTA;
5. proof or a product visual.

Baseline:

```tsx
<section className="relative overflow-hidden">
  <MarketingContainer className="pt-20 pb-16 sm:pt-28 sm:pb-20">
    <div className="max-w-3xl">
      <MarketingEyebrow>...</MarketingEyebrow>
      <h1 className="mt-5 text-4xl font-semibold leading-[1.05] tracking-tight text-balance sm:text-6xl lg:text-7xl">
        ...
      </h1>
      <p className="mt-5 max-w-2xl text-lg leading-relaxed text-muted-foreground">
        ...
      </p>
      <div className="mt-8 flex flex-wrap gap-3">
        <Button size="cta-lg">Primary action</Button>
        <Button size="cta" variant="outline">
          Secondary action
        </Button>
      </div>
    </div>
  </MarketingContainer>
</section>
```

Hero visuals must carry product meaning: real screenshots, a purposeful
diagram, a relevant illustration, or restrained brand imagery. Do not add a
generic dashboard mockup merely to fill the right column.

## Section rhythm

- Use `py-20 md:py-24` as the normal major-section interval.
- Use `max-w-2xl` for heading/lede blocks inside a wider container.
- Separate sections through surface, border, imagery, or composition; do not
  alternate backgrounds mechanically.
- Prefer two or three asymmetric, information-rich sections over six repeated
  three-card grids.

### Feature cards

Choose the card density by role:

- compact product proof: `rounded-xl border bg-card p-5`;
- editorial/capability feature: `rounded-2xl border bg-card/70 p-7 md:p-9`;
- stat: border rule plus large mono value, often no enclosing card.

Icon tiles are optional. If every card starts with the same tinted icon box,
the page is probably becoming generic.

## Public control scale

- hero primary: 48px (`h-12`) with generous horizontal padding;
- normal public CTA: 40px (`h-10`);
- header primary action: 32–36px is acceptable because the header is compact;
- mobile menu/action targets: at least 44px.

Do not pass `size="lg"` from the product Button into a hero; in the bundled
component it remains a 36px app action.

## Trust and evidence

Use real evidence only: actual screenshots, customer names with permission,
real metrics, genuine compatibility claims, or clearly labeled examples.
Avoid fabricated logos, metrics, testimonials, and product screens.

## Responsive review

At minimum inspect 375px, 768px, 1280px, and 1440px widths. Confirm:

- H1 wrapping is intentional;
- CTAs do not become tiny or overflow;
- visual and copy order remains clear;
- container padding grows at breakpoints;
- card padding and section gaps do not collapse into one undifferentiated
  column;
- sticky navigation does not hide anchored content.
