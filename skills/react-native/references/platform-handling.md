# Platform Handling

This project uses NativeWind for almost all styling. Reach for `StyleSheet` / inline `style` only when a value is dynamic (animated, computed from insets, theme tokens) or platform-specific (shadows, elevation).

## Platform.select

```tsx
import { Platform, View } from "react-native";

export function ShadowedCard({ children }: { children: React.ReactNode }) {
    return (
        <View
            className="rounded-xl bg-white p-4"
            style={Platform.select({
                ios: { shadowColor: "#000", shadowOffset: { width: 0, height: 2 }, shadowOpacity: 0.1, shadowRadius: 8 },
                android: { elevation: 4 },
            })}
        >
            {children}
        </View>
    );
}
```

Tailwind's `shadow-*` utilities don't translate well to native — for actual elevation, use the inline `style` + `Platform.select` shown above.

## Platform.OS

```tsx
import { Platform, Text, View } from "react-native";

export function PlatformBadge() {
    return (
        <View>
            {Platform.OS === "ios" && <IOSOnlyComponent />}
            <Text>{Platform.OS === "android" ? "Android" : "iOS"}</Text>
        </View>
    );
}
```

## Platform-specific files

```
components/
├── Button.tsx           # Shared logic
├── Button.ios.tsx       # iOS-specific
└── Button.android.tsx   # Android-specific
```

Metro resolves `import Button from "@/components/Button"` to the platform variant. Use this when the divergence is large enough that `Platform.select` inside one file becomes unreadable. For small differences, inline `Platform.select` wins.

## SafeArea

`react-native-safe-area-context` is already a dependency. Mount the provider once at the root (or rely on Expo Router doing it for you) and consume it via `SafeAreaView` or `useSafeAreaInsets`.

```tsx
// Method 1: SafeAreaView component
import { SafeAreaView } from "react-native-safe-area-context";

export function Screen({ children }: { children: React.ReactNode }) {
    return <SafeAreaView className="flex-1">{children}</SafeAreaView>;
}

// Method 2: useSafeAreaInsets — when you need a custom header / fine control
import { useSafeAreaInsets } from "react-native-safe-area-context";
import { View, Text } from "react-native";

export function CustomHeader() {
    const insets = useSafeAreaInsets();
    return (
        <View className="px-4 pb-3" style={{ paddingTop: insets.top }}>
            <Text className="text-lg font-semibold">Header</Text>
        </View>
    );
}
```

Don't use the deprecated `SafeAreaView` from `react-native` itself.

`app.json` has `"android.edgeToEdgeEnabled": true`, so on Android the system bars are transparent — you must respect `insets.top` and `insets.bottom` manually anywhere you don't use `SafeAreaView`.

## KeyboardAvoidingView

```tsx
import { KeyboardAvoidingView, Platform, ScrollView, TextInput } from "react-native";
import { SafeAreaView } from "react-native-safe-area-context";

export function FormScreen() {
    return (
        <SafeAreaView className="flex-1">
            <KeyboardAvoidingView
                className="flex-1"
                behavior={Platform.OS === "ios" ? "padding" : "height"}
                keyboardVerticalOffset={Platform.select({ ios: 88, android: 0 })}
            >
                <ScrollView contentContainerClassName="gap-3 p-4" keyboardShouldPersistTaps="handled">
                    <TextInput className="rounded-lg border border-neutral-300 p-3" placeholder="Name" />
                    <TextInput className="rounded-lg border border-neutral-300 p-3" placeholder="Email" />
                </ScrollView>
            </KeyboardAvoidingView>
        </SafeAreaView>
    );
}
```

## StatusBar

Prefer Expo's `expo-status-bar` (already a dependency) over `react-native`'s — it integrates with Expo Router transitions.

```tsx
import { StatusBar } from "expo-status-bar";

export function Screen() {
    return (
        <>
            <StatusBar style="auto" />
            <Content />
        </>
    );
}
```

`style="auto"` follows the device color scheme; pass `"light"` or `"dark"` to force.

## Android back button

```ts
// hooks/useBackHandler.ts
import { useEffect } from "react";
import { BackHandler, Platform } from "react-native";

export function useBackHandler(handler: () => boolean) {
    useEffect(() => {
        if (Platform.OS !== "android") return;
        const sub = BackHandler.addEventListener("hardwareBackPress", handler);
        return () => sub.remove();
    }, [handler]);
}
```

```tsx
useBackHandler(() => {
    if (hasUnsavedChanges) {
        showDiscardAlert();
        return true; // swallow back
    }
    return false; // let default happen
});
```

`app.json` sets `"android.predictiveBackGestureEnabled": false`, so on Android 14+ the predictive back gesture is disabled and `hardwareBackPress` fires on the back swipe as expected.

## Quick Reference

| API                         | Purpose                          |
| --------------------------- | -------------------------------- |
| `Platform.OS`               | `'ios'` / `'android'` / `'web'`  |
| `Platform.select()`         | Platform-specific values         |
| `Platform.Version`          | OS version number                |
| `.ios.tsx` / `.android.tsx` | Platform-specific files          |

| Component / API                          | Purpose                          |
| ---------------------------------------- | -------------------------------- |
| `SafeAreaView` (safe-area-context)       | Avoid notch / home indicator     |
| `useSafeAreaInsets` (safe-area-context)  | Custom headers, edge-to-edge UI  |
| `KeyboardAvoidingView`                   | Keyboard-aware scrolling forms   |
| `expo-status-bar`                        | Status bar styling               |
| `BackHandler`                            | Android hardware back button     |
