# List Optimization

**React Compiler is on in this project.** It auto-memoizes components and inline closures, so the old "wrap every list item in `memo` and every callback in `useCallback`" advice is unnecessary noise here. Start without manual memoization; add it only when the React DevTools Profiler shows wasted renders, and leave a comment explaining why.

## Baseline FlatList (no manual memo)

```tsx
import { FlatList, Pressable, Text } from "react-native";

type Item = { id: string; title: string; subtitle: string };

function ListItem({ item, onPress }: { item: Item; onPress: (id: string) => void }) {
    return (
        <Pressable onPress={() => onPress(item.id)} className="border-b border-neutral-200 px-4 py-3">
            <Text className="text-base font-medium">{item.title}</Text>
            <Text className="text-sm text-neutral-500">{item.subtitle}</Text>
        </Pressable>
    );
}

const ITEM_HEIGHT = 72;

export function ItemList({ data }: { data: Item[] }) {
    const handlePress = (id: string) => {
        console.log("Selected:", id);
    };

    return (
        <FlatList
            data={data}
            renderItem={({ item }) => <ListItem item={item} onPress={handlePress} />}
            keyExtractor={(item) => item.id}
            getItemLayout={(_, index) => ({ length: ITEM_HEIGHT, offset: ITEM_HEIGHT * index, index })}
            removeClippedSubviews
            maxToRenderPerBatch={10}
            windowSize={5}
            initialNumToRender={10}
            updateCellsBatchingPeriod={50}
        />
    );
}
```

The Compiler memoizes `ListItem` and the inline `renderItem` closure. `getItemLayout` is still a real win for fixed-height rows because it skips measurement.

## SectionList

```tsx
import { SectionList, Text, View } from "react-native";

type Section = { title: string; data: Item[] };

export function GroupedList({ sections }: { sections: Section[] }) {
    return (
        <SectionList
            sections={sections}
            renderItem={({ item }) => <ListItem item={item} onPress={() => {}} />}
            renderSectionHeader={({ section }) => (
                <View className="bg-neutral-100 px-4 py-2">
                    <Text className="text-xs font-semibold uppercase text-neutral-500">{section.title}</Text>
                </View>
            )}
            keyExtractor={(item) => item.id}
            stickySectionHeadersEnabled
        />
    );
}
```

## Pull to refresh

```tsx
import { useState } from "react";
import { FlatList, RefreshControl } from "react-native";

export function RefreshableList({ data, onRefresh }: { data: Item[]; onRefresh: () => Promise<void> }) {
    const [refreshing, setRefreshing] = useState(false);

    const handleRefresh = async () => {
        setRefreshing(true);
        try {
            await onRefresh();
        } finally {
            setRefreshing(false);
        }
    };

    return (
        <FlatList
            data={data}
            renderItem={({ item }) => <ListItem item={item} onPress={() => {}} />}
            keyExtractor={(item) => item.id}
            refreshControl={<RefreshControl refreshing={refreshing} onRefresh={handleRefresh} />}
        />
    );
}
```

Prefer wiring `refetch` from a React Query hook directly rather than maintaining a parallel `refreshing` boolean:

```tsx
const { data = [], isRefetching, refetch } = useItemsQuery();
// ...
refreshControl={<RefreshControl refreshing={isRefetching} onRefresh={refetch} />}
```

## Infinite scroll with React Query

```tsx
import { useInfiniteQuery } from "@tanstack/react-query";
import { ActivityIndicator, FlatList } from "react-native";
import { fetchItems } from "@/services/items";

export function InfiniteItemList() {
    const { data, fetchNextPage, hasNextPage, isFetchingNextPage } = useInfiniteQuery({
        queryKey: ["items"],
        queryFn: ({ pageParam }) => fetchItems({ cursor: pageParam }),
        initialPageParam: undefined as string | undefined,
        getNextPageParam: (last) => last.nextCursor,
    });

    const items = data?.pages.flatMap((p) => p.items) ?? [];

    return (
        <FlatList
            data={items}
            renderItem={({ item }) => <ListItem item={item} onPress={() => {}} />}
            keyExtractor={(item) => item.id}
            onEndReached={() => hasNextPage && fetchNextPage()}
            onEndReachedThreshold={0.5}
            ListFooterComponent={isFetchingNextPage ? <ActivityIndicator className="py-4" /> : null}
        />
    );
}
```

## FlashList (large or heterogeneous data)

If you find yourself fighting FlatList performance on a long or visually variable list, install Shopify's `@shopify/flash-list`.

```tsx
import { FlashList } from "@shopify/flash-list";

export function FastList({ data }: { data: Item[] }) {
    return (
        <FlashList
            data={data}
            renderItem={({ item }) => <ListItem item={item} onPress={() => {}} />}
            estimatedItemSize={72}
            keyExtractor={(item) => item.id}
        />
    );
}
```

## When manual memoization is justified

The Compiler is good but not perfect. Reach for `memo` / `useMemo` / `useCallback` when:

- Profiling shows a measurable, repeated waste (not just a hunch).
- A list item receives a referentially-unstable prop produced **outside** the component the Compiler optimizes (e.g. coming from a non-React layer, a ref, or a third-party hook).
- A child component is intentionally not Compiler-eligible (e.g. a class component or library boundary).

In all three cases, leave a one-line comment explaining the decision so the next reader doesn't strip it.

## Quick Reference

| Prop                    | Purpose                          |
| ----------------------- | -------------------------------- |
| `removeClippedSubviews` | Unmount off-screen items         |
| `maxToRenderPerBatch`   | Items per render batch           |
| `windowSize`            | Render window multiplier         |
| `initialNumToRender`    | Items rendered on first paint    |
| `getItemLayout`         | Skip measurement (fixed height)  |

| Choice                          | When                                                       |
| ------------------------------- | ---------------------------------------------------------- |
| `FlatList` + `getItemLayout`    | Default, fixed row heights                                 |
| `SectionList`                   | Grouped data with sticky headers                           |
| `FlashList`                     | Very long or heterogeneous lists where FlatList struggles  |
| Manual `memo` / `useCallback`   | Profiler shows waste, or prop instability outside Compiler |
