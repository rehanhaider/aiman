---
name: react-native
description: Builds, optimizes, and debugs cross-platform mobile applications with React Native and Expo. Implements Expo Router navigation, configures native modules, optimizes lists, and handles platform-specific code for iOS and Android. Use when building a React Native or Expo mobile app, setting up navigation, integrating native modules, improving scroll performance, handling SafeArea or keyboard input, or configuring Expo SDK projects. Carries calibrated defaults for an Expo SDK 54 / Expo Router 6 / NativeWind stack and verifies the actual project before applying them.
license: MIT
metadata:
  version: "2.2.0"
  domain: frontend
  triggers: React Native, Expo, mobile app, iOS, Android, cross-platform, native module
  role: specialist
  scope: implementation
  output-format: code
  related-skills: react-expert
---

# React Native Expert

Senior mobile engineer building production-ready cross-platform applications with React Native and Expo. The stack below is a set of **calibrated defaults**, not facts about every repo — before relying on any of them, verify against the actual project: `AGENTS.md` (if present), `package.json`, and `app.json` are the source of truth, and when they disagree with this file, the project wins. Surface the difference rather than silently applying a default.

## Project stack (calibrated defaults — verify first)

- **Expo SDK 54**, React Native 0.81, React 19.1
- **New Architecture ON** (`newArchEnabled: true`)
- **React Compiler ON** (`experiments.reactCompiler: true`) — auto-memoizes; **do not** reach for `memo` / `useMemo` / `useCallback` reflexively
- **TypeScript strict**, path alias `@/*` → `mobile/src/*`
- **Expo Router 6** with `typedRoutes: true`
- **NativeWind v4** for styling (`className` on RN primitives)
- **React Query 5** for server state, **Zustand 5 + MMKV** for client state (no AsyncStorage)
- **Typography** — this stack's default sans family is **Montserrat** (`@expo-google-fonts/montserrat`), weights `_400Regular` / `_500Medium` / `_600SemiBold` / `_700Bold`, loaded via `useFonts` in the root `_layout.tsx`. If the project already has an established family, use that instead.
- Code under the app workspace's `src/{app,components,contexts,hooks,stores,services,styles,types}` (in this calibrated project: `mobile/src/*`)

If a constraint above conflicts with what the user asks or with the actual project, surface the conflict — don't silently violate either.

## Core Workflow

1. **Verify stack & env** — read `package.json` / `app.json` to confirm the defaults above, then `npx expo doctor` (run from the app workspace, e.g. `mobile/`); fix anything reported before coding.
2. **Place code by role** — routes in `src/app/`, hooks in `src/hooks/`, stores in `src/stores/`, network/platform clients in `src/services/`. Don't invent new top-level folders.
3. **Implement** — TypeScript-first, NativeWind for styling, React Query for fetching, Zustand for client state.
4. **Wire native modules** — after adding/upgrading anything that has native code (e.g. `react-native-mmkv`, `react-native-nitro-modules`, gesture-handler), run `npx expo run:android` (or `:ios`) to rebuild the dev client. Fast Refresh alone won't pick those up.
5. **Verify** — `npm run lint` (`expo lint`); manually exercise iOS + Android. No test runner is wired up.

### Error Recovery

- **Metro bundler errors** → `npx expo start --clear`, then restart.
- **iOS build fails** → check Xcode logs → resolve native dependency / provisioning → `npx expo run:ios`.
- **Android build fails** → check Gradle output or `adb logcat` → resolve SDK/NDK mismatch → `npx expo run:android`.
- **Native module not found / TurboModule errors** → `npx expo install <module>` for a compatible version, then rebuild the dev client.
- **Tailwind classes not applied** → check the workspace's `tailwind.config.js` `content` glob covers the file; Metro caches aggressively → restart with `--clear`.

## Reference Guide

Load detailed guidance based on context:

| Topic      | Reference                         | Load When                                                                |
| ---------- | --------------------------------- | ------------------------------------------------------------------------ |
| Navigation | `references/expo-router.md`       | Expo Router, tabs, stacks, deep linking                                  |
| App shell  | `references/app-shell.md`         | Root layout wiring, providers, fonts, splash gating, share target        |
| Platform   | `references/platform-handling.md` | iOS/Android splits, SafeArea, keyboard                                   |
| Theming    | `references/theming.md`           | CSS-variable tokens, dark mode, Tailwind + NativeWind color setup        |
| Lists      | `references/list-optimization.md` | FlatList / FlashList, large data sets                                    |
| Storage    | `references/storage-hooks.md`     | MMKV (`createMMKV`), Zustand persistence, secure tokens                  |
| Local DB   | `references/local-database.md`    | Project uses (or needs) SQLite — Drizzle, migrations, live queries       |
| Structure  | `references/project-structure.md` | Where new files go, alias / config layout                                |

## Constraints

### MUST DO

- Use `FlatList` / `SectionList` / `FlashList` for lists (never `ScrollView` for variable-length data).
- Set a stable `keyExtractor` and provide `getItemLayout` when row heights are fixed.
- Use `react-native-safe-area-context` (`SafeAreaView` or `useSafeAreaInsets`) for notch / home-indicator handling — it's already a dependency.
- Use `KeyboardAvoidingView` (with `behavior="padding"` on iOS, `"height"` on Android) for forms.
- Type Expo Router params with `useLocalSearchParams<{...}>()` and rely on `typedRoutes`.
- Persist Zustand stores via the MMKV `StateStorage` adapter (see `references/storage-hooks.md`).
- Use the project's established type family, gating render on `useFonts` resolving in `_layout.tsx`. When the project has none, default to **Montserrat** (install the relevant `@expo-google-fonts/montserrat` weight modules).

### MUST NOT DO

- Sprinkle `memo` / `useMemo` / `useCallback` "for performance" — React Compiler handles it. Add them only when a profiler shows a real win, and leave a comment explaining why.
- Add `@react-native-async-storage/async-storage`. MMKV is the persistence layer.
- Use `StyleSheet.create` for layout / spacing / typography / colors — use NativeWind `className`. Reserve inline `style` for dynamic values that can't be expressed as classes (animated values, computed insets, theme tokens).
- Hardcode pixel dimensions where flex / `Dimensions` / safe-area insets would do.
- Skip the dev-client rebuild after touching native dependencies.
- Use `waitFor` / `setTimeout` for animation timing — use Reanimated.

## Code Examples

### List with React Compiler ON

```tsx
import { FlatList, Pressable, Text, View } from "react-native";

type Item = { id: string; title: string };

function ListItem({ title, onPress }: { title: string; onPress: () => void }) {
    return (
        <Pressable onPress={onPress} className="border-b border-neutral-200 px-4 py-3">
            <Text className="text-base">{title}</Text>
        </Pressable>
    );
}

export function ItemList({ data }: { data: Item[] }) {
    const handlePress = (id: string) => {
        console.log("pressed", id);
    };

    return (
        <FlatList
            data={data}
            keyExtractor={(item) => item.id}
            renderItem={({ item }) => <ListItem title={item.title} onPress={() => handlePress(item.id)} />}
            removeClippedSubviews
            maxToRenderPerBatch={10}
            windowSize={5}
        />
    );
}
```

No `memo`, no `useCallback` — the compiler memoizes `ListItem` and the inline closures. If a profiler later shows wasted renders, add memoization with a comment.

### Form with KeyboardAvoidingView + NativeWind

```tsx
import { KeyboardAvoidingView, Platform, ScrollView, TextInput } from "react-native";
import { SafeAreaView } from "react-native-safe-area-context";

export function LoginForm() {
    return (
        <SafeAreaView className="flex-1">
            <KeyboardAvoidingView className="flex-1" behavior={Platform.OS === "ios" ? "padding" : "height"}>
                <ScrollView contentContainerClassName="gap-3 p-4" keyboardShouldPersistTaps="handled">
                    <TextInput className="rounded-lg border border-neutral-300 p-3 text-base" placeholder="Email" autoCapitalize="none" />
                    <TextInput className="rounded-lg border border-neutral-300 p-3 text-base" placeholder="Password" secureTextEntry />
                </ScrollView>
            </KeyboardAvoidingView>
        </SafeAreaView>
    );
}
```

### Platform-specific values

Prefer `Platform.select` inline over duplicate `.ios.tsx` / `.android.tsx` files unless the divergence is large.

```tsx
import { Platform, Pressable, Text, View } from "react-native";

export function StatusChip({ label }: { label: string }) {
    return (
        <View
            className="self-start rounded-full px-3 py-1"
            style={{
                backgroundColor: "#0a7ea4",
                ...Platform.select({
                    ios: { shadowColor: "#000", shadowOffset: { width: 0, height: 2 }, shadowOpacity: 0.2, shadowRadius: 4 },
                    android: { elevation: 3 },
                }),
            }}
        >
            <Text className="text-sm font-semibold text-white">{label}</Text>
        </View>
    );
}
```

## Output Format

When implementing React Native features, deliver:

1. **Component code** — TypeScript, NativeWind classes for styling, props typed.
2. **Route integration** — typed `useLocalSearchParams`, correct group / layout placement under `src/app/`.
3. **Data layer** — React Query hook in `src/hooks/`, query key factory co-located, mutation invalidations spelled out.
4. **State layer** — Zustand store in `src/stores/`, MMKV-persisted if it must survive restarts.
5. **Platform notes** — only if behavior diverges between iOS and Android.

## Knowledge Reference

Expo SDK 54, React Native 0.81, React 19.1 (Compiler), Expo Router 6 (typed routes), Reanimated 4, Gesture Handler 2, react-native-safe-area-context, NativeWind 4 + Tailwind 3, React Query 5, Zustand 5, react-native-mmkv 4 (Nitro), expo-image, @expo/vector-icons.
