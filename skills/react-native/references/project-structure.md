# Project Structure

This project is a single Expo workspace at `mobile/`. All app code lives under `mobile/src/` and is reachable via the `@/*` TypeScript path alias.

## Directory layout (`mobile/src/`)

```
mobile/
├── app.json                  # Expo config (newArch + React Compiler ON)
├── babel.config.js           # babel-preset-expo with jsxImportSource: nativewind
├── metro.config.js           # withNativeWind wrapper
├── tailwind.config.js        # content: ./src/**/*.{js,jsx,ts,tsx}
├── tsconfig.json             # strict, paths: { "@/*": ["./src/*"] }
├── eslint.config.js          # flat config, extends eslint-config-expo
└── src/
    ├── app/                  # Expo Router routes (file = route)
    │   ├── _layout.tsx       # Root layout — mount providers here
    │   ├── index.tsx         # Home (/)
    │   ├── +not-found.tsx    # 404
    │   ├── (tabs)/           # Tab group (no URL segment)
    │   │   ├── _layout.tsx
    │   │   ├── index.tsx
    │   │   └── profile.tsx
    │   ├── (auth)/           # Auth group (no tabs)
    │   │   ├── _layout.tsx
    │   │   ├── login.tsx
    │   │   └── signup.tsx
    │   └── details/[id].tsx  # Dynamic route
    ├── components/           # Reusable presentational components
    ├── contexts/             # React context providers
    ├── hooks/                # Reusable hooks (incl. React Query useFooQuery / useFooMutation)
    ├── stores/               # Zustand stores (one file per store)
    ├── services/             # HTTP / auth / platform clients (no React imports)
    ├── styles/
    │   └── global.css        # Tailwind entry — imported once from app/_layout.tsx
    └── types/                # Shared TS types and ambient declarations
```

Don't add a top-level folder unless none of the existing roles fit. If you'd be tempted by `utils/`, prefer co-locating with the consumer or putting it under `services/` if it's a side-effecting client.

## tsconfig.json

```json
{
    "extends": "expo/tsconfig.base",
    "compilerOptions": {
        "strict": true,
        "resolveJsonModule": true,
        "jsx": "react-jsx",
        "paths": {
            "@/*": ["./src/*"]
        }
    },
    "include": ["**/*.ts", "**/*.tsx", ".expo/types/**/*.ts", "expo-env.d.ts", "nativewind-env.d.ts"]
}
```

A single `@/*` alias points at `mobile/src/*`. Use it for every intra-`src` import: `import { useAuth } from "@/hooks/useAuth"`.

## babel.config.js

```js
module.exports = function (api) {
    api.cache(true);
    return {
        presets: [["babel-preset-expo", { jsxImportSource: "nativewind" }], "nativewind/babel"],
    };
};
```

`jsxImportSource: "nativewind"` is what makes `className` work on RN primitives. No `react-native-reanimated/plugin` line — RN 0.81 + Reanimated 4 + the new arch handle it via the worklets package.

## metro.config.js

```js
const { getDefaultConfig } = require("expo/metro-config");
const { withNativeWind } = require("nativewind/metro");

const config = getDefaultConfig(__dirname);

module.exports = withNativeWind(config, { input: "./src/styles/global.css" });
```

## app.json (key fields)

```json
{
    "expo": {
        "name": "downloader",
        "slug": "downloader",
        "scheme": "downloader",
        "newArchEnabled": true,
        "experiments": {
            "typedRoutes": true,
            "reactCompiler": true
        },
        "plugins": ["expo-router", ["expo-splash-screen", { /* ... */ }]]
    }
}
```

`newArchEnabled` and `reactCompiler` are both load-bearing — see `SKILL.md` constraints for what that implies.

**Don't hand-edit `version`** — `make mobile-build` rewrites it as `<base>.<YYYYMMDD>.<patch>`.

## Installed packages (Expo SDK 54 era)

What's available without an install step — group by role:

- **Routing**: `expo-router` (file-based, with `typedRoutes`)
- **Server state**: `@tanstack/react-query`
- **Client state**: `zustand`
- **Persistence**: `react-native-mmkv` (Nitro-based; no AsyncStorage)
- **Styling**: `nativewind` + `tailwindcss`
- **Native UI**: `react-native-safe-area-context`, `react-native-screens`, `react-native-gesture-handler`, `react-native-reanimated` (+ `react-native-worklets`)
- **Expo modules**: `expo-image`, `expo-haptics`, `expo-linking`, `expo-splash-screen`, `expo-status-bar`, `expo-system-ui`, `expo-web-browser`, `expo-symbols`, `expo-font`, `expo-constants`
- **Icons**: `@expo/vector-icons`
- **Navigation primitives** (transitively, via expo-router): `@react-navigation/native`, `@react-navigation/bottom-tabs`, `@react-navigation/elements`

See `mobile/package.json` for exact versions — that file is the source of truth, don't duplicate version numbers in docs. To add or upgrade a package, prefer `npx expo install <pkg>` over `npm install <pkg>` — it picks the version matched to the installed Expo SDK.

## Quick Reference

| Directory     | Purpose                                                       |
| ------------- | ------------------------------------------------------------- |
| `app/`        | Expo Router file-based routes                                 |
| `components/` | Reusable presentational components (no fetching)              |
| `contexts/`   | React context providers                                       |
| `hooks/`      | Custom hooks, including React Query queries/mutations         |
| `stores/`     | Zustand stores (MMKV-persisted when needed)                   |
| `services/`   | HTTP / auth / platform clients (pure, no React)               |
| `styles/`     | Tailwind entry + theme tokens                                 |
| `types/`      | Shared TS types and ambient declarations                      |
