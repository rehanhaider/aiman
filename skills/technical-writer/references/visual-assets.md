# Visual Assets — SVG Diagrams and JSON Image Specifications

Every long-form technical article needs visuals. This skill produces them in two ways:

- **SVG inline** — for diagrams. Architecture, flow, sequence, state, comparison, charts.
- **JSON image specification** — for illustrations / hero images. Hand the spec to DALL-E, Midjourney, Imagen, Stable Diffusion, or paste it into Claude / ChatGPT / Gemini.

The decision rule (from SKILL.md):

> When in doubt, SVG. Use the JSON-spec path when the visual is *expressive* (mood, atmosphere, narrative), not *informational* (structure, flow, data).

---

## Part 1: SVG Diagrams

### Why SVG for technical diagrams

- **Text remains text.** Crawlers and screen readers can read it. Embedded labels become indexable content.
- **Editable.** A teammate can grep for a label and fix a typo without re-rendering an image.
- **Resolution-independent.** No "high-DPI version" or "retina version" needed.
- **Accessible.** `<title>` and `<desc>` elements pair cleanly with ARIA.
- **Themable.** CSS variables let the diagram match light/dark themes automatically.

### Standard structure

```svg
<svg
  xmlns="http://www.w3.org/2000/svg"
  viewBox="0 0 800 450"
  role="img"
  aria-labelledby="diagram-title diagram-desc"
>
  <title id="diagram-title">Three-stage data pipeline</title>
  <desc id="diagram-desc">Ingest, enrich, and publish stages connected with a feedback loop.</desc>

  <!-- definitions: gradients, markers, patterns -->
  <defs>
    <marker id="arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
      <path d="M 0 0 L 10 5 L 0 10 z" fill="currentColor" />
    </marker>
  </defs>

  <!-- background (transparent by default; explicit fill if needed) -->
  <!-- main content -->
</svg>
```

Always include `<title>` and `<desc>` — these are the SVG equivalent of `alt` and `longdesc`. `role="img"` and `aria-labelledby` link them.

Use `currentColor` for stroke / fill where possible — lets the page CSS recolor the diagram for theming.

### Architecture diagram pattern

Three-box pipeline with an arrow:

```svg
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 240" role="img" aria-labelledby="arch-title arch-desc">
  <title id="arch-title">Three-stage pipeline</title>
  <desc id="arch-desc">Ingest receives raw events, Enrich joins reference data, Publish writes to downstream sinks.</desc>

  <defs>
    <marker id="arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto">
      <path d="M 0 0 L 10 5 L 0 10 z" fill="#1d3557" />
    </marker>
  </defs>

  <!-- boxes -->
  <g font-family="ui-sans-serif, system-ui, sans-serif" font-size="16" text-anchor="middle">
    <g>
      <rect x="40"  y="80" width="180" height="80" rx="8" fill="#f1faee" stroke="#1d3557" stroke-width="2"/>
      <text x="130" y="115" font-weight="600" fill="#1d3557">Ingest</text>
      <text x="130" y="138" fill="#457b9d">raw events</text>
    </g>
    <g>
      <rect x="310" y="80" width="180" height="80" rx="8" fill="#f1faee" stroke="#1d3557" stroke-width="2"/>
      <text x="400" y="115" font-weight="600" fill="#1d3557">Enrich</text>
      <text x="400" y="138" fill="#457b9d">join reference data</text>
    </g>
    <g>
      <rect x="580" y="80" width="180" height="80" rx="8" fill="#f1faee" stroke="#1d3557" stroke-width="2"/>
      <text x="670" y="115" font-weight="600" fill="#1d3557">Publish</text>
      <text x="670" y="138" fill="#457b9d">write to sinks</text>
    </g>
  </g>

  <!-- arrows -->
  <g stroke="#1d3557" stroke-width="2" fill="none">
    <line x1="220" y1="120" x2="305" y2="120" marker-end="url(#arrow)"/>
    <line x1="490" y1="120" x2="575" y2="120" marker-end="url(#arrow)"/>
  </g>
</svg>
```

### Flowchart pattern

Decision diamond + branches. Use `<polygon>` for diamonds, `<rect>` for steps.

### Sequence diagram pattern

Two or three vertical lifelines with horizontal arrows annotated by label. Use `<line>` for lifelines (dashed), `<g>` for each interaction.

### State diagram pattern

Circles for states, arrows for transitions, double-bordered circle for terminal states.

### Comparison diagram pattern

Two columns side-by-side, mirroring structure, often with a vertical divider. Title each column.

### Box-and-arrow tips

- Pad rectangles by ≥20px from siblings; tight diagrams read as cramped.
- Use rounded corners (`rx="8"`) for a friendly feel, sharp corners for formal/technical contexts.
- Typography: 14–16px for labels, 18–20px for headers. Below 12px stops being readable on mobile.
- Color palette: use the article's existing palette if it has one. If not, default to a neutral palette like `#1d3557` (dark blue), `#457b9d` (slate), `#f1faee` (cream), `#e63946` (accent red).
- Stroke widths: 2px for primary lines, 1px for secondary, 3px for emphasis arrows.

### Color choices

Default palette (works on light backgrounds, AA-contrast safe):

```
Primary:    #1d3557  (dark blue — text, primary strokes)
Secondary:  #457b9d  (slate blue — secondary text, secondary strokes)
Tertiary:   #a8dadc  (pale teal — fills, backgrounds)
Surface:    #f1faee  (off-white — box fills)
Accent:     #e63946  (red — emphasis, alerts, "wrong" branches)
```

For dark-mode-friendly diagrams, include `prefers-color-scheme` media queries inside `<style>`:

```svg
<style>
  @media (prefers-color-scheme: dark) {
    .surface { fill: #1a1a1a; }
    .text { fill: #f1faee; }
    .stroke { stroke: #f1faee; }
  }
</style>
```

### When to ask the user before generating

If the user has an existing brand palette / typography / icon set, ask before producing a diagram. Mismatched diagrams stand out worse than no diagrams. A 30-second question saves a 30-minute redo.

### Sizing for article placement

| Placement                  | Recommended viewBox     |
| -------------------------- | ----------------------- |
| Inline diagram (full-width)| `0 0 800 450` (16:9)    |
| Inline diagram (tall)      | `0 0 600 800`           |
| Inline diagram (square)    | `0 0 600 600`           |
| Hero / lede                | `0 0 1200 630` (OG ratio)|
| Sidebar / margin           | `0 0 320 240`           |

Keep everything inside the viewBox; clipping at the edges is amateur-hour.

---

## Part 2: JSON image specifications

For visuals that aren't diagrams — hero images, section openers, conceptual illustrations — output a JSON specification the user can hand to an image generator. The spec is tool-agnostic; tools differ in their prompt format, but they all map cleanly from the same fields.

### Why JSON spec, not raw prompt

- **Shareable.** The user can iterate on the spec, swap tools, regenerate a year later.
- **Versionable.** Lives in the repo alongside the article markdown.
- **Tool-agnostic.** Same spec → DALL-E, Midjourney, Imagen, Stable Diffusion. The translation step is mechanical.
- **Reviewable.** Easier to spot "you forgot to specify aspect ratio" in JSON than in a freeform prompt.

### Schema

The canonical schema lives in `assets/image-spec.schema.json`. Required fields:

```jsonc
{
  "purpose": "string — what this image is for in the article",
  "context": "string — one sentence on the article's topic",
  "subject": "string — the literal subject in the frame",
  "style": "string — art-direction descriptor",
  "color_palette": ["#hex", "#hex", "..."],
  "aspect_ratio": "16:9 | 4:3 | 1:1 | 3:2 | etc.",
  "include": ["string", "..."],
  "exclude": ["string", "..."],
  "mood": "string — one or two adjectives",
  "alt_text": "string — accessibility description (≤125 chars)",
  "tools_supported": ["DALL-E 3", "Midjourney", "Imagen", "Stable Diffusion XL", "..."]
}
```

Optional fields:

```jsonc
{
  "lighting": "soft natural / dramatic / studio / etc.",
  "perspective": "isometric / front-facing / aerial / etc.",
  "composition": "rule of thirds / centered / asymmetric / etc.",
  "negative_prompt": "string — for SD / similar tools",
  "seed": 12345,
  "reference_images": ["url or path"],
  "iteration_notes": "what to tweak if the first generation doesn't land"
}
```

### Worked examples

#### Example 1 — Hero image for a deep-dive on caching

```json
{
  "purpose": "Hero image (lede + OG card) for a blog post titled 'Why caching at the agent harness beats caching at the model'",
  "context": "Technical deep-dive on agent infrastructure latency. The argument is that the harness layer is a better cache boundary than the model API.",
  "subject": "An isometric illustration of two parallel pipelines, one labelled 'harness' with a glowing cache layer, one labelled 'model' without. The harness pipeline has clearly faster particle flow.",
  "style": "minimal isometric tech illustration, clean line art with selective gradient fills",
  "color_palette": ["#0a7ea4", "#f1faee", "#1d3557", "#e63946"],
  "aspect_ratio": "16:9",
  "include": ["two parallel pipeline rows", "labelled cache layer with glow", "particle/data flow", "monospace labels"],
  "exclude": ["text-heavy diagrams", "stock-photo people", "literal robot or brain imagery", "Midjourney watermarks"],
  "mood": "calm, technical, confident",
  "alt_text": "Isometric illustration comparing two pipelines, with the cached harness pipeline showing faster data flow than the uncached model pipeline.",
  "tools_supported": ["DALL-E 3", "Midjourney", "Imagen", "Stable Diffusion XL"],
  "lighting": "soft, diffuse, low-contrast",
  "perspective": "30-degree isometric",
  "composition": "two horizontal bands, harness on top",
  "iteration_notes": "If the cache layer doesn't read as a 'box', swap for a glowing torus shape. If particle flow looks like rain, switch to a directional gradient streak."
}
```

#### Example 2 — Section opener for a postmortem

```json
{
  "purpose": "Section opener illustration for 'What we thought was happening' in a postmortem on a 3-hour deploy hang",
  "context": "Postmortem about misdiagnosing a deploy hang as a network issue when it was actually a config typo.",
  "subject": "A magnifying glass hovering over a tangle of network wires, with a single wire glowing red but partially hidden behind the others",
  "style": "editorial illustration, soft watercolor texture",
  "color_palette": ["#264653", "#2a9d8f", "#e9c46a", "#e76f51"],
  "aspect_ratio": "3:1",
  "include": ["magnifying glass", "tangled wires", "one wire glowing red", "soft shadow"],
  "exclude": ["screens", "people", "computers", "text", "logos"],
  "mood": "investigative, slightly wry",
  "alt_text": "Magnifying glass over a tangle of wires with one wire glowing red, illustrating misdiagnosed root cause.",
  "tools_supported": ["DALL-E 3", "Midjourney", "Imagen"],
  "lighting": "soft side-light from upper left",
  "composition": "magnifying glass centered, wires filling lower two-thirds",
  "iteration_notes": "If the metaphor reads as too literal (a real magnifying glass), shift toward a more abstract shape — a glowing circle or focus reticle."
}
```

#### Example 3 — Author headshot for E-E-A-T page

```json
{
  "purpose": "Author headshot illustration for the /author/<slug> page (used when a real photo isn't available)",
  "context": "Personal blog. The author writes about distributed systems and devrel.",
  "subject": "A stylized avatar — chest-up, friendly expression, neutral background",
  "style": "vector illustration with limited palette, similar to Notion / Slack avatar style",
  "color_palette": ["#1d3557", "#a8dadc", "#f1faee"],
  "aspect_ratio": "1:1",
  "include": ["avatar", "neutral background"],
  "exclude": ["realistic photo features", "logos", "branded clothing", "complex backgrounds"],
  "mood": "approachable, professional",
  "alt_text": "Stylized avatar illustration of [author name].",
  "tools_supported": ["DALL-E 3", "Midjourney"],
  "iteration_notes": "Real photo preferred when available — this spec is the fallback."
}
```

### Tool-translation notes

When the user wants to actually generate the image, the spec maps to each tool roughly like this:

- **DALL-E 3 (via ChatGPT or API):** Concatenate `subject + ", " + style + ", " + composition + ", " + mood`. Append "Color palette: ..." with hex codes. Append "Avoid: ..." with the `exclude` list.
- **Midjourney:** Same prose ordering, then append `--ar 16:9 --style raw --no people, text` (or the relevant exclude). Add `--seed 12345` for reproducibility.
- **Imagen / Vertex AI:** Use the spec almost verbatim — its prompt understanding is closest to plain English.
- **Stable Diffusion XL:** Use `subject + style + lighting + composition` as positive prompt; map `exclude` to negative prompt; set CFG to 7 and sampler to DPM++ 2M Karras as a sane default.

### Always include alt_text

Don't ship an image spec without it. Writing alt text *with* the spec, while the visual is fresh in your mind, is far easier than retrofitting it. The alt text is also a forcing function: if you can't describe what the image will show in 125 characters, your spec is probably too vague.

### Iteration

Image generation is rarely one-shot. The `iteration_notes` field captures *what to change if the first generation misses*. This is more useful than re-prompting from scratch — it preserves the parts of the spec that are working and points at the specific weak spot.

---

## Decision examples

| Article context                                                    | Choose       | Reason                                                              |
| ------------------------------------------------------------------ | ------------ | ------------------------------------------------------------------- |
| "Architecture of our pipeline"                                     | SVG          | Structural, labelled, needs to be editable.                         |
| Hero image for "Why caching at the harness wins"                   | JSON spec    | Expressive / mood; not a literal architecture diagram.              |
| Sequence diagram showing API call flow                             | SVG          | Structural; lifelines + arrows + labels.                            |
| Section opener illustration for a postmortem                       | JSON spec    | Mood / metaphor; not informational.                                 |
| Comparison table of two libraries                                  | SVG          | Structural; text remains searchable.                                |
| Author headshot                                                    | JSON spec or photo | Identity; SVG would feel cold.                                |
| State machine for a feature flag system                            | SVG          | Structural.                                                          |
| Lede image for a "Day in the life" post                            | JSON spec    | Mood; reader needs atmosphere, not data.                            |
| Benchmark chart                                                    | SVG          | Numerical; consider a real chart library, but inline SVG works.     |
| Concept illustration for "what AI agents really are"               | JSON spec    | Metaphor / atmosphere; SVG would be too literal.                    |

When both could work, ask: *would the reader benefit from being able to copy this image's text?* If yes, SVG. If no, JSON spec.
