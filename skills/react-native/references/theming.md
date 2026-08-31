# Theming & Dark Mode

Load this when wiring (or extending) the design-token system, adding a color, or building a dark-mode toggle. The pattern below is the project's standard: **CSS variables drive Tailwind/NativeWind classes**, a small **JS palette mirrors the same tokens** for color-string props that don't accept `className`, and **NativeWind's `setColorScheme()`** flips between light and dark from React state.

## The three-layer model

1. **`mobile/src/styles/global.css`** — the source of truth for color values. Defines RGB-triplet CSS variables under `:root` (light) and `.dark:root, :root.dark` (dark). NativeWind compiles your `className`s against these variables.
2. **`tailwind.config.js`** — maps each Tailwind utility (`bg-ink`, `text-paper`, `border-rule`) to a CSS variable via two small helpers. This is what makes `bg-ink/50` work: Tailwind takes the RGB triplet and composes the alpha at use site.
3. **`mobile/src/theme/tokens.ts`** + **`ThemeProvider`** — a JS palette mirror, exposed via `useTheme()`, for the cases where you can't apply a class: `Icon` `color` props, `StatusBar` `backgroundColor`, animated `style.backgroundColor`, `tabBarActiveTintColor`, etc.

The layers are *parallel*, not chained — you maintain both `global.css` and `tokens.ts` by hand. The cost is a 2-place edit on color changes; the win is that the same token name works in *both* a `className="bg-ink"` and an `<Icon color={tokens.ink} />`. If maintaining two parallel palettes feels wrong, see "Single-source alternative" at the bottom.

## Tailwind config — `rgbVar` / `rawVar`

```js
// mobile/tailwind.config.js
// Expose a CSS variable as an alpha-aware Tailwind color. Lets utilities like
// `bg-ink/50` work — Tailwind substitutes its `<alpha-value>` template into the
// rgb() call at use site.
const rgbVar = (name) => `rgb(var(${name}) / <alpha-value>)`;

// For tokens that already encode their own alpha (rgba strings, scrims),
// expose `var(...)` raw — Tailwind's alpha template would corrupt the rgba.
const rawVar = (name) => `var(${name})`;

module.exports = {
    content: ["./src/**/*.{js,jsx,ts,tsx}"],
    presets: [require("nativewind/preset")],
    darkMode: "class",
    theme: {
        extend: {
            colors: {
                ink: rgbVar("--color-ink"),
                "ink-mute": rgbVar("--color-ink-mute"),
                paper: rgbVar("--color-paper"),
                accent: rgbVar("--color-accent"),

                // Tokens that carry their own alpha — passed through raw.
                rule: rawVar("--color-rule"),
                "sheet-scrim": rawVar("--color-sheet-scrim"),
            },
        },
    },
};
```

**Why the split**: alpha composition (`bg-ink/50`) requires Tailwind to *interpolate* its `<alpha-value>` into the `rgb(...)` call. That only works if the CSS variable holds a space-separated triplet (`8 30 50`), not a complete `rgba(...)` string. For tokens that *do* need their own alpha — borders, scrims, hover-soft overlays — bypass the template with `rawVar`.

## CSS variables in `global.css`

```css
@tailwind base;
@tailwind components;
@tailwind utilities;

@layer base {
    :root {
        /* Triplet form — Tailwind's `<alpha-value>` composes against these. */
        --color-ink: 8 30 50;
        --color-paper: 245 239 227;
        --color-accent: 213 183 124;

        /* Baked alpha — read raw via `rawVar`. */
        --color-rule: rgba(8, 30, 50, 0.12);
        --color-sheet-scrim: rgba(22, 21, 19, 0.32);
    }

    .dark:root,
    :root.dark {
        --color-ink: 240 232 214;
        --color-paper: 13 36 56;
        --color-accent: 230 201 146;

        --color-rule: rgba(240, 232, 214, 0.10);
        --color-sheet-scrim: rgba(0, 0, 0, 0.55);
    }
}
```

The dual selector `.dark:root, :root.dark` covers both directions of class application — some tools toggle `<html class="dark">`, NativeWind toggles `:root.dark`. Including both keeps the file portable.

Don't put non-token CSS here — keep it tokens-only. The file gets imported once (from `src/app/_layout.tsx`) and that import is the only Tailwind entry.

## ThemeProvider — coupling NativeWind to your settings store

NativeWind exposes `useColorScheme()` which controls the `:root.dark` class toggle. Drive it from your persisted theme preference so a stored `"dark"` choice flips the whole tree:

```tsx
// mobile/src/theme/ThemeProvider.tsx
import { createContext, useContext, useEffect } from "react";
import { useColorScheme as useSystemColorScheme } from "react-native";
import { useColorScheme } from "nativewind";

import { useSettings } from "@/stores/settings";
import { PALETTES, type ResolvedThemeMode, type Tokens } from "./tokens";

interface ThemeContextValue {
    resolvedMode: ResolvedThemeMode;
    tokens: Tokens;
}

const ThemeContext = createContext<ThemeContextValue | null>(null);

export const ThemeProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
    const mode = useSettings((s) => s.theme); // "light" | "dark" | "system"
    const systemScheme = useSystemColorScheme(); // null until platform reports
    const resolvedMode: ResolvedThemeMode = mode === "system" ? (systemScheme ?? "light") : mode;

    // Drive NativeWind's class-based dark-mode toggle so `dark:` variants flip
    // in lockstep with the JS palette below.
    const { setColorScheme } = useColorScheme();
    useEffect(() => {
        setColorScheme(resolvedMode);
    }, [resolvedMode, setColorScheme]);

    return (
        <ThemeContext.Provider value={{ resolvedMode, tokens: PALETTES[resolvedMode] }}>
            {children}
        </ThemeContext.Provider>
    );
};

export const useTheme = () => {
    const ctx = useContext(ThemeContext);
    if (!ctx) throw new Error("useTheme must be used within a ThemeProvider");
    return ctx;
};
```

Two `useColorScheme` imports show up: `react-native`'s reads the OS preference (read-only); `nativewind`'s drives the `:root.dark` class (read + write). That's intentional — one is the *input* (what the OS reports), the other is the *output* (what the document class becomes).

`tokens.ts` exposes a parallel palette as plain strings:

```ts
// mobile/src/theme/tokens.ts
export type ResolvedThemeMode = "light" | "dark";

export const PALETTES = {
    light: {
        ink: "#081e32",
        paper: "#F5EFE3",
        accent: "#d5b77c",
        rule: "rgba(8, 30, 50, 0.12)",
    },
    dark: {
        ink: "#F0E8D6",
        paper: "#0d2438",
        accent: "#e6c992",
        rule: "rgba(240, 232, 214, 0.10)",
    },
} as const;

export type Tokens = (typeof PALETTES)[ResolvedThemeMode];
```

Use the same token names as the CSS variables so a code reader can find both ends. If you add `ink-soft` to one, add it to the other in the same commit.

## When to reach for JS tokens vs `className`

| Context                                          | Use                          |
| ------------------------------------------------ | ---------------------------- |
| Static styling on RN primitives (`<View>`, etc.) | `className="bg-ink"`         |
| `Icon` / vector `color` prop                     | `tokens.ink`                 |
| `StatusBar` `backgroundColor` / `style`          | `tokens.paper` + `resolvedMode` |
| Animated `useSharedValue` driving a color        | `tokens.*` interpolated in the worklet |
| `tabBarActiveTintColor`, `headerTintColor`       | `tokens.accent`              |
| `react-native-svg` `fill` / `stroke`             | `tokens.ink`                 |

Default to `className`; only drop to `tokens` when the API simply doesn't take a class.

## Caveats

- **Don't redeclare token names in `extend.fontFamily` or `extend.colors`** — adding a key shadows the global one. Extend, don't replace.
- **Class-based dark mode doesn't propagate across Modal/Portals on Android in some RN versions.** If a portal renders in light mode while the rest is dark, mount a `<View className="dark">` shell inside the portal to force re-evaluation.
- **`useColorScheme()` from `react-native` returns `null` on first render** until the platform reports a value. The `?? "light"` fallback in `ThemeProvider` matters — without it you'll see a one-frame flash.
- **Don't put Tailwind colors directly in `tokens.ts`** like `bg-ink`. Tokens hold values; class names belong in JSX.

## Single-source alternative

If the two-place edit becomes a real pain, NativeWind v4's `vars()` helper lets you define theme variables in JS and apply them via a parent `View`'s `style` prop:

```tsx
import { vars } from "nativewind";

const lightTheme = vars({ "--color-ink": "8 30 50", "--color-paper": "245 239 227" });
const darkTheme  = vars({ "--color-ink": "240 232 214", "--color-paper": "13 36 56" });

<View style={resolvedMode === "dark" ? darkTheme : lightTheme} className="flex-1">
    <App />
</View>
```

This collapses `global.css` and `tokens.ts` into one map. The trade-offs: the JS map can't use the `rgb(... / <alpha-value>)` composition trick (you still get alpha via `bg-ink/50` because Tailwind's compiler handles that part), but theme variables now live inside a React tree rather than at `:root`, so portals/modals may need a re-wrap. Pick this only if you find the dual-source maintenance is causing actual drift.

## Quick Reference

| Pattern                                         | Where it lives                          |
| ----------------------------------------------- | --------------------------------------- |
| Color token definition                          | `src/styles/global.css`                 |
| Tailwind utility binding                        | `tailwind.config.js` (`rgbVar`/`rawVar`)|
| JS palette mirror                               | `src/theme/tokens.ts`                   |
| Light/dark resolution + class toggle            | `src/theme/ThemeProvider.tsx`           |
| Persisted user preference (`light`/`dark`/`system`) | `src/stores/settings.ts`            |
