# Storage & Hooks

This project uses **MMKV** (`react-native-mmkv` v4, Nitro-based) as the only general-purpose persistence layer. Do **not** add `@react-native-async-storage/async-storage` — it's intentionally absent.

For sensitive material (auth tokens, refresh tokens), use `expo-secure-store` instead of MMKV.

## MMKV basics

v4 ships two equivalent ways to create an instance:

- **`createMMKV({ id })`** — the Nitro-based factory introduced in v4. This is the recommended path; it exercises the Nitro JSI bindings directly and is what new code should use.
- **`new MMKV({ id })`** — the v3-compatible class constructor. Still works, falls back to the JSI path. Use it only if you're carrying code over from v3 and don't want to churn.

```ts
import { createMMKV } from "react-native-mmkv";

// One instance per logical bucket; reuse it everywhere.
export const appStorage = createMMKV({ id: "app" });

appStorage.set("user.name", "John");
const name = appStorage.getString("user.name");

appStorage.set("user.age", 25);
const age = appStorage.getNumber("user.age");

appStorage.set("user.premium", true);
const isPremium = appStorage.getBoolean("user.premium");

appStorage.delete("user.name");
appStorage.clearAll();
```

Operations are **synchronous** — no `await`, no loading states needed for reads. That's the headline win over AsyncStorage, and it's what makes MMKV viable as a persistence backend for Zustand's `persist` middleware (which expects sync storage).

**Buckets.** Different `id` values produce isolated stores backed by separate files on disk. Use this to scope domains (`auth`, `settings`, `cache`) so `clearAll()` on one doesn't nuke the others.

## React hooks for MMKV

```ts
import { useMMKVString, useMMKVNumber, useMMKVBoolean, useMMKVObject } from "react-native-mmkv";

function Settings() {
    const [theme, setTheme] = useMMKVString("theme");
    const [fontSize, setFontSize] = useMMKVNumber("fontSize");
    const [notifications, setNotifications] = useMMKVBoolean("notifications");
    const [profile, setProfile] = useMMKVObject<{ name: string; avatar?: string }>("profile");
    // ...
}
```

The hooks subscribe to the key and re-render on change — good for ad-hoc UI bindings. For app-wide state, prefer Zustand below.

## Zustand + MMKV (the canonical pattern)

This is how persisted client state should be wired. One file per store under `mobile/src/stores/`.

```ts
// mobile/src/stores/settings.ts
import { createMMKV } from "react-native-mmkv";
import { create } from "zustand";
import { createJSONStorage, persist, type StateStorage } from "zustand/middleware";

const mmkv = createMMKV({ id: "settings" });

const mmkvStorage: StateStorage = {
    getItem: (name) => mmkv.getString(name) ?? null,
    setItem: (name, value) => mmkv.set(name, value),
    removeItem: (name) => mmkv.delete(name),
};

interface SettingsState {
    theme: "light" | "dark" | "system";
    setTheme: (t: SettingsState["theme"]) => void;
}

export const useSettings = create<SettingsState>()(
    persist(
        (set) => ({
            theme: "system",
            setTheme: (theme) => set({ theme }),
        }),
        {
            name: "settings",
            version: 1,
            storage: createJSONStorage(() => mmkvStorage),
            migrate: (persisted) => persisted as SettingsState,
            // Optionally narrow what gets persisted:
            // partialize: (s) => ({ theme: s.theme }),
        },
    ),
);
```

The `StateStorage` adapter is three lines but they're load-bearing — Zustand's `persist` middleware expects an `AsyncStorage`-shaped interface (`getItem` returning a string-or-null, `setItem` taking a string), and `createJSONStorage` serializes/deserializes the slice for you.

**Always set `version` + `migrate`** on a new store, even if `migrate` is a no-op today:

```ts
{
    name: "auth",
    version: 1,
    storage: createJSONStorage(() => mmkvStorage),
    migrate: (persisted, version) => {
        if (version < 1) {
            // v0 stored email at top level; v1 nests it under `user`.
            return { ...persisted, user: { email: (persisted as any).email } } as AuthState;
        }
        return persisted as AuthState;
    },
}
```

Bumping `version` later is cheap; backfilling a `migrate` when users already have v0 data on disk is painful.

### Hydration gate

`persist` reads asynchronously on first mount. If you redirect based on persisted state (e.g. "if logged in → tabs, else → login"), you'll bounce the user for one frame on cold start. Gate behind a `hasHydrated` flag:

```tsx
const hydrated = useSettings.persist.hasHydrated();
const [, setHydrated] = useState(hydrated);

useEffect(() => {
    if (useSettings.persist.hasHydrated()) return;
    const unsub = useSettings.persist.onFinishHydration(() => setHydrated(true));
    return unsub;
}, []);

if (!hydrated) return null; // keep splash visible
```

## Selecting from a Zustand store

Always **select** with a selector — selecting the whole store re-renders the component on every change:

```tsx
import { useSettings } from "@/stores/settings";

function ThemeButton() {
    const theme = useSettings((s) => s.theme);
    const setTheme = useSettings((s) => s.setTheme);
    // ...
}
```

If you need multiple slices, two selectors is usually fine. Use `useShallow` from `zustand/shallow` only if you're returning a new object from one selector and re-renders are showing up in the profiler.

## Secure storage (tokens)

For credentials that shouldn't sit in a plain MMKV file, use `expo-secure-store`. Add it with `npx expo install expo-secure-store` first.

```ts
import * as SecureStore from "expo-secure-store";

await SecureStore.setItemAsync("refreshToken", token);
const token = await SecureStore.getItemAsync("refreshToken");
await SecureStore.deleteItemAsync("refreshToken");
```

Wrap `expo-secure-store` behind a function in `mobile/src/services/` so the storage choice is centralized and the rest of the app doesn't import the SDK directly.

## Server state — React Query, not MMKV

Don't cache server responses in MMKV "to make them faster." React Query already caches in memory and supports offline persistence via `@tanstack/query-async-storage-persister` (or a custom MMKV-backed persister). Use MMKV / Zustand for **client** state (UI prefs, auth session, drafts), not derivable server data.

## Quick Reference

| Storage                     | Speed  | Async | Use Case                       |
| --------------------------- | ------ | ----- | ------------------------------ |
| MMKV (`react-native-mmkv`)  | Fast   | No    | App state, prefs, large data   |
| `expo-secure-store`         | Medium | Yes   | Tokens, secrets                |
| React Query in-memory cache | Fast   | -     | Server responses               |

| Factory               | When to use                                       |
| --------------------- | ------------------------------------------------- |
| `createMMKV({ id })`  | New code (v4 Nitro factory — recommended)         |
| `new MMKV({ id })`    | Carrying over from v3, otherwise prefer the above |

| Hook                  | Returns                  |
| --------------------- | ------------------------ |
| `useMMKVString(k)`    | `[string?, setter]`      |
| `useMMKVNumber(k)`    | `[number?, setter]`      |
| `useMMKVBoolean(k)`   | `[boolean?, setter]`     |
| `useMMKVObject<T>(k)` | `[T?, setter]`           |
