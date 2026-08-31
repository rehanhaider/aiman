# Expo Router

This project uses **Expo Router 6** with `typedRoutes: true`. Routes live under `mobile/src/app/`. The `package.json` `main` is `expo-router/entry`, so there is no `App.tsx` — `app/_layout.tsx` is the root.

## Project structure

```
mobile/src/app/
├── _layout.tsx           # Root layout — mount providers (QueryClient, SafeAreaProvider, etc.)
├── index.tsx             # Home (/)
├── +not-found.tsx        # 404
├── (tabs)/               # Tab group (no URL segment)
│   ├── _layout.tsx       # Tab bar config
│   ├── index.tsx         # First tab
│   └── profile.tsx       # Profile tab
├── (auth)/               # Auth group (no tabs)
│   ├── _layout.tsx
│   ├── login.tsx
│   └── signup.tsx
├── settings/
│   ├── _layout.tsx       # Stack layout
│   ├── index.tsx
│   └── notifications.tsx
└── details/[id].tsx      # Dynamic route
```

Parens groups (`(tabs)`, `(auth)`) don't appear in the URL — use them to scope a layout to a subset of screens.

## Root layout

Mount React Query, the safe-area provider, and any global context here.

```tsx
// mobile/src/app/_layout.tsx
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { Stack } from "expo-router";
import { SafeAreaProvider } from "react-native-safe-area-context";
import "@/styles/global.css";

const queryClient = new QueryClient();

export default function RootLayout() {
    return (
        <QueryClientProvider client={queryClient}>
            <SafeAreaProvider>
                <Stack screenOptions={{ headerShown: false }}>
                    <Stack.Screen name="(tabs)" />
                    <Stack.Screen name="(auth)" />
                    <Stack.Screen name="details/[id]" options={{ presentation: "modal" }} />
                </Stack>
            </SafeAreaProvider>
        </QueryClientProvider>
    );
}
```

`import "@/styles/global.css"` is what loads the Tailwind sheet — keep it in this file.

## Tab layout

```tsx
// mobile/src/app/(tabs)/_layout.tsx
import { Ionicons } from "@expo/vector-icons";
import { Tabs } from "expo-router";

export default function TabLayout() {
    return (
        <Tabs screenOptions={{ tabBarActiveTintColor: "#007AFF", headerShown: true }}>
            <Tabs.Screen
                name="index"
                options={{
                    title: "Home",
                    tabBarIcon: ({ color, size }) => <Ionicons name="home" color={color} size={size} />,
                }}
            />
            <Tabs.Screen
                name="profile"
                options={{
                    title: "Profile",
                    tabBarIcon: ({ color, size }) => <Ionicons name="person" color={color} size={size} />,
                }}
            />
        </Tabs>
    );
}
```

`@react-navigation/bottom-tabs` is already a transitive dependency of `expo-router`; you don't need to install it separately.

## Navigation

```ts
import { Link, router, useLocalSearchParams } from "expo-router";

// Programmatic
router.push("/details/123");                 // Add to stack
router.replace("/home");                     // Replace current
router.back();                                // Go back
router.canGoBack();

// With params (typedRoutes validates these at compile time)
router.push({ pathname: "/details/[id]", params: { id: "123" } });
```

```tsx
// Declarative
<Link href="/profile" asChild>
    <Pressable>
        <Text>Go to Profile</Text>
    </Pressable>
</Link>
```

```tsx
// Reading params — always type the generic
function DetailsScreen() {
    const { id } = useLocalSearchParams<{ id: string }>();
    return <Text>Details for {id}</Text>;
}
```

With `typedRoutes`, the `href` prop on `<Link>` and `pathname` on `router.push` are checked against the actual route tree — bad paths fail TypeScript, not runtime.

## Protected routes

```tsx
// mobile/src/app/(auth)/_layout.tsx
import { Redirect, Stack } from "expo-router";
import { useAuthStore } from "@/stores/authStore";

export default function AuthLayout() {
    const accessToken = useAuthStore((s) => s.accessToken);
    if (accessToken) return <Redirect href="/(tabs)" />;
    return <Stack screenOptions={{ headerShown: false }} />;
}
```

```tsx
// mobile/src/app/(tabs)/_layout.tsx
import { Redirect, Tabs } from "expo-router";
import { useAuthStore } from "@/stores/authStore";

export default function TabsLayout() {
    const accessToken = useAuthStore((s) => s.accessToken);
    if (!accessToken) return <Redirect href="/(auth)/login" />;
    return <Tabs>{/* ... */}</Tabs>;
}
```

Selecting a single field (`(s) => s.accessToken`) avoids re-rendering the layout on unrelated store changes.

If your auth state involves an async hydration step (e.g. waiting for MMKV to load on cold start), gate redirects behind a `hydrated` flag so you don't bounce the user to `/login` for one frame.

## Deep linking

```jsonc
// app.json
{
    "expo": {
        "scheme": "downloader"
    }
}
```

`downloader://details/123` resolves to `app/details/[id].tsx` automatically — no manual routing config needed.

## Quick Reference

| Component  | Purpose                |
| ---------- | ---------------------- |
| `<Stack>`  | Stack navigator        |
| `<Tabs>`   | Tab navigator          |
| `<Drawer>` | Drawer navigator       |
| `<Link>`   | Declarative navigation |

| router method  | Behavior        |
| -------------- | --------------- |
| `push()`       | Add to stack    |
| `replace()`    | Replace current |
| `back()`       | Go back         |
| `dismissAll()` | Dismiss modals  |

| Hook                     | Returns                        |
| ------------------------ | ------------------------------ |
| `useLocalSearchParams()` | Route params (type the generic) |
| `useGlobalSearchParams()`| Params from any active route   |
| `usePathname()`          | Current pathname               |
| `useSegments()`          | Current route segments         |
