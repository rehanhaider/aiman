# Theme axes — canonical diversification values for the 22 catalog themes

This file is the **canonical source** for each catalog theme's three diversification axes
(SKILL.md § theme-diversification rule). When Step 2.5 needs to compare a candidate theme
against the previous run, look the values up here — do not infer them from the theme name.

Axis definitions (from SKILL.md):

- **Paper band** — lightness of `--color-paper`: dark (L < 30%) · mid (30–85%) · light (> 85%)
- **Display style** — the display face family: italic-serif · roman-serif · geometric-sans ·
  mono · display-condensed-italic · display-heavy · system-native · risograph-bold
- **Accent hue** — warm (red/orange/amber 10–60°) · cool (blue/indigo/violet 200–300°) ·
  neutral (no chromatic accent) · chromatic-other (anything else: greens, teals, magentas)

| Theme     | Paper band | Display style            | Accent hue                        | Genre cluster  |
| --------- | ---------- | ------------------------ | --------------------------------- | -------------- |
| Specimen  | light      | italic-serif             | warm (red-orange)                 | editorial      |
| Atelier   | light      | italic-serif             | neutral (ink + muted gold)        | editorial      |
| Brutal    | light      | display-heavy            | warm (raw red)                    | editorial      |
| Salon     | light      | roman-serif              | warm (oxblood)                    | editorial      |
| Newsprint | light      | roman-serif              | neutral (ink-led)                 | editorial      |
| Linen     | light      | roman-serif              | warm (terracotta)                 | editorial      |
| Studio    | light      | italic-serif             | chromatic-other (forest green)    | editorial      |
| Manifesto | light      | geometric-sans           | warm (poster red)                 | editorial      |
| Terminal  | dark       | mono                     | chromatic-other (phosphor green)  | atmospheric    |
| Midnight  | dark       | geometric-sans           | cool (indigo)                     | atmospheric    |
| Almanac   | mid        | roman-serif              | warm (ochre)                      | editorial      |
| Garden    | light      | roman-serif              | chromatic-other (sage)            | editorial      |
| Quiet     | light      | system-native            | neutral                           | modern-minimal |
| Riso      | light      | risograph-bold           | warm (fluoro red-orange)          | editorial      |
| Sport     | light      | display-condensed-italic | warm (track red)                  | editorial      |
| Bloom     | dark       | italic-serif             | chromatic-other (magenta)         | atmospheric    |
| Coral     | light      | geometric-sans           | warm (coral)                      | editorial      |
| Violet    | mid        | geometric-sans           | cool (violet)                     | editorial      |
| Aurora    | dark       | geometric-sans           | chromatic-other (aurora teal)     | editorial      |
| Halo      | light      | geometric-sans           | cool (ice blue)                   | editorial      |
| Plume     | light      | geometric-sans           | cool (lilac)                      | playful        |
| Editorial | light      | roman-serif              | warm (editorial red)              | editorial      |

Notes:

- Some themes share all three axis values (e.g. Salon / Linen / Editorial). The
  diversification rule requires two **consecutive** picks to differ on at least one axis, so
  such pairs cannot follow each other — pick a more distant theme instead.
- Custom themes do not appear here. A custom run computes its own three axis values at build
  time and records them in `.hallmark/log.json` under `theme_axes` (see `custom-theme.md` § F).
- Studied-DNA builds suspend diversification entirely (SKILL.md § 2.6 Condition 0) and are
  not compared against this table.
