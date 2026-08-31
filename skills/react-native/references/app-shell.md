# App Shell — Root Layout, Providers, Fonts, Splash

Load this when wiring (or modifying) the app's root: `_layout.tsx`, the provider stack, font loading, splash-screen gating, or share-target integration. Most apps touch this once and forget it — but getting the order and the boot gates right is the difference between "splash hides cleanly" and "the app flashes the wrong color for one frame, then crashes because gestures didn't initialize."

## The provider stack

Order matters. Some providers must wrap others to function. Below is the canonical stack for this skill's assumed dependencies; add/remove based on what's actually installed.

```tsx
// mobile/src/app/_layout.tsx
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { GestureHandlerRootView } from "react-native-gesture-handler";
import { SafeAreaProvider } from "react-native-safe-area-context";

import { ThemeProvider } from "@/theme/ThemeProvider";
import "@/styles/global.css";

export default function RootLayout() {
    const [queryClient] = useState(() => new QueryClient());

    return (
        <GestureHandlerRootView style={{ flex: 1 }}>
            <QueryClientProvider client={queryClient}>
                <SafeAreaProvider>
                    <ThemeProvider>
                        <ThemedStack />
                    </ThemeProvider>
                </SafeAreaProvider>
            </QueryClientProvider>
        </GestureHandlerRootView>
    );
}
```

Why this order:

1. **`GestureHandlerRootView` outermost.** `react-native-gesture-handler` registers a native view that intercepts touches *above* the React tree. Anything inside it gets gesture support; anything outside doesn't. Make it the literal root and forget about it.
2. **`QueryClientProvider` before anything that might fetch.** React Query hooks crash without a client in context. Mount it high enough that no screen renders without it.
3. **`SafeAreaProvider` before anything that reads insets.** `useSafeAreaInsets()` returns zeros without a provider. Headers, modals, and `SafeAreaView` consumers all depend on it being above them.
4. **`ThemeProvider` close to the screens.** It only needs to wrap things that consume `useTheme()`; deeper is fine. Keep it inside the safe-area provider so a themed header can still see insets.
5. **`QueryClient` in `useState`, not a module-level constant.** A module-level client survives Fast Refresh but resets in dev with React 18's strict mode + double-mount in some configurations. Hoisting to `useState` makes the instance survive remounts cleanly.

If you add other providers, slot them by the same rule: *the consumer must be inside the provider*. A few common cases:

| Provider                                | Where it goes                                                    |
| --------------------------------------- | ---------------------------------------------------------------- |
| `BottomSheetModalProvider`              | Inside `GestureHandlerRootView`, outside screen content          |
| `KeyboardProvider` (react-native-keyboard-controller) | Inside `GestureHandlerRootView`                |
| Crash reporter (Sentry's `ErrorBoundary`)| Outermost (or inside `GestureHandlerRootView` if you want gestures inside the fallback) |
| Auth context                            | Inside `QueryClientProvider`, outside screens                    |

## Font loading

Use `useFonts` from `expo-font` and gate render on the result. With `react-native-splash-screen` (via `expo-splash-screen`) preventing auto-hide, the splash stays visible until fonts (and any other async deps) are ready.

```tsx
import * as SplashScreen from "expo-splash-screen";
import { useFonts } from "expo-font";
import {
    Montserrat_400Regular,
    Montserrat_500Medium,
    Montserrat_700Bold,
} from "@expo-google-fonts/montserrat";

// Module-level call — runs once, before any component mounts. The promise it
// returns is fire-and-forget; the splash stays visible until something calls
// `hideAsync()`.
SplashScreen.preventAutoHideAsync().catch(() => {});

export default function RootLayout() {
    const [fontsLoaded] = useFonts({
        Montserrat_400Regular,
        Montserrat_500Medium,
        Montserrat_700Bold,
    });

    useEffect(() => {
        if (fontsLoaded) SplashScreen.hideAsync().catch(() => {});
    }, [fontsLoaded]);

    if (!fontsLoaded) return null; // splash stays visible
    return <ProviderStack />;
}
```

Two things to know:

- **The `.catch(() => {})` on `preventAutoHideAsync` is load-bearing.** If the splash has already been hidden (e.g. on Fast Refresh, where the module is re-evaluated), this rejects. Swallowing is fine.
- **Don't render the tree before fonts resolve.** RN will render with the system default font, then re-render once the custom font loads — visible as a font flash. Returning `null` keeps the splash up instead.
- **Match the loaded `Montserrat_500Medium` to the Tailwind alias.** `tailwind.config.js` maps `font-sans-medium` → `Montserrat_500Medium`. Only weights you've loaded are usable; importing a weight you haven't loaded fails silently to system fallback.

## Multi-gate readiness — fonts + other async boot

Most non-trivial apps have more than just fonts to wait on: database migrations, a legacy data migration, a config fetch, etc. Combine them into a single ready flag instead of nesting `if (a) return null; if (b) return null;`:

```tsx
const [fontsLoaded] = useFonts({ /* ... */ });
const { success: schemaReady } = useMigrations(db, migrations);
const [legacyMigrated, setLegacyMigrated] = useState(false);

useEffect(() => {
    if (!schemaReady || legacyMigrated) return;
    migrateLegacyData()
        .catch((err) => __DEV__ && console.warn("[migrateLegacyData]", err))
        .finally(() => setLegacyMigrated(true));
}, [schemaReady, legacyMigrated]);

const ready = fontsLoaded && schemaReady && legacyMigrated;

useEffect(() => {
    if (ready) SplashScreen.hideAsync().catch(() => {});
}, [ready]);

if (!ready) return null;
```

Notes:

- **`legacyMigrated` flips even on error.** Use `.finally(() => setLegacyMigrated(true))` rather than `.then(...).catch(...)` — you don't want a broken migration to leave the splash up forever. Log to dev console, swallow in prod.
- **Order the gates by speed.** Cheap synchronous gates (in-memory) before slow async ones (network, disk migrations) so the loader resolves earlier on the happy path.
- **Don't pile gates into one big `Promise.all`.** Each gate has its own retry/error semantics and React Query/`useMigrations`-style hooks expose those individually. Keep them as separate `useEffect`s feeding one boolean.

## Share-target integration (conditional)

Load this section **only if the app accepts content via the OS share sheet** (a "download from share" / "save to library" UX). Otherwise skip — `expo-share-intent` is real native code that adds boot overhead.

### `app.json` plugin entry

```jsonc
{
    "expo": {
        "plugins": [
            "expo-router",
            ["expo-share-intent", {
                "iosActivationRules": {
                    "NSExtensionActivationSupportsText": true,
                    "NSExtensionActivationSupportsWebURLWithMaxCount": 1,
                    "NSExtensionActivationSupportsWebPageWithMaxCount": 1
                },
                "androidIntentFilters": ["text/*"]
            }]
        ]
    }
}
```

The iOS activation rules are *and*-not-*or* — declaring `SupportsText: true` and `SupportsWebURL: 1` means the share sheet shows your app for plain text *or* a single URL. Tune these to the exact content shape you handle; over-declaring shows your app in irrelevant share menus.

### Wiring in `_layout.tsx`

```tsx
import { ShareIntentProvider, useShareIntentContext } from "expo-share-intent";

const ShareIntentRouter: React.FC = () => {
    const router = useRouter();
    const { hasShareIntent, shareIntent, resetShareIntent } = useShareIntentContext();

    useEffect(() => {
        if (!hasShareIntent) return;
        const url =
            shareIntent.webUrl ??
            (shareIntent.text && /^https?:\/\//i.test(shareIntent.text.trim())
                ? shareIntent.text.trim()
                : null);
        if (url) router.push({ pathname: "/preview", params: { url } });
        resetShareIntent();
    }, [hasShareIntent, shareIntent, resetShareIntent, router]);

    return null;
};

// Mount inside ProviderStack:
<ShareIntentProvider>
    <ShareIntentRouter />
    <ThemedStack />
</ShareIntentProvider>
```

A few patterns worth noting:

- **The `ShareIntentRouter` returns `null`.** It's a side-effect-only component that listens for share events and navigates. Keeping it as a sibling of the stack (not as wrapper) means a share-triggered navigation doesn't re-mount the whole tree.
- **`resetShareIntent()` after handling.** Otherwise the same share replays on every re-render. The library's reset clears the buffered intent.
- **Validate the URL shape before navigating.** Shares come from arbitrary apps; assume the payload is hostile until proven a URL.
- **Decide what `/preview` does if the app was launched cold by the share.** Cold-launch shares fire before any auth gate — make sure the preview route doesn't crash if the user state isn't hydrated yet.

## Quick Reference

| Concern                       | Pattern                                                             |
| ----------------------------- | ------------------------------------------------------------------- |
| Gesture root                  | `<GestureHandlerRootView style={{ flex: 1 }}>` outermost            |
| React Query                   | `useState(() => new QueryClient())` + `<QueryClientProvider>`       |
| Safe area                     | `<SafeAreaProvider>` above anything reading insets                  |
| Theme                         | `<ThemeProvider>` inside SafeArea, above screens                    |
| Splash hold                   | `SplashScreen.preventAutoHideAsync()` at module load                |
| Splash release                | `SplashScreen.hideAsync()` in an effect gated on `ready`            |
| Fonts                         | `useFonts({...weights})` → returns `[loaded]` tuple                 |
| Multiple async gates          | One boolean `ready = a && b && c`, each fed by its own hook/effect  |
| Share target                  | `<ShareIntentProvider>` + `useShareIntentContext()` (conditional)   |
