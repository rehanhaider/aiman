# Data and state ownership

Make ownership obvious from the type of state.

| State                                     | Owner                         |
| ----------------------------------------- | ----------------------------- |
| Remote/server-derived data                | TanStack Query                |
| Shareable filters, sort, pagination, view | TanStack Router search params |
| Cross-route UI preferences and chrome     | Zustand                       |
| Validated multi-field form state          | TanStack Form                 |
| Small transient interaction               | local React state             |

Do not mirror Query data into Zustand. Do not put ordinary form fields in the
global store. Do not use TanStack Store alongside Zustand.

## One server boundary

When the web app owns its backend, expose a small set of Start server
functions from `src/server/fns.ts`. Keep database drivers and secrets behind
that file or behind modules imported only from it.

```ts
import { createServerFn } from "@tanstack/react-start";
import { z } from "zod";

export const listWidgets = createServerFn({ method: "GET" })
  .validator(
    z.object({ q: z.string().optional(), page: z.number().int().min(0) }),
  )
  .handler(({ data }) => runtime.widgets.list(data));
```

When the backend is external, keep one typed HTTP boundary in `src/lib/api.ts`:

```ts
export class ApiError extends Error {
  constructor(
    public status: number,
    public code: string,
    message: string,
  ) {
    super(message);
  }
}

export async function apiFetch<T>(
  path: string,
  init: RequestInit = {},
): Promise<T> {
  const headers = new Headers(init.headers);
  headers.set("accept", "application/json");
  if (init.body && !headers.has("content-type"))
    headers.set("content-type", "application/json");

  const response = await fetch(path, { ...init, headers });
  const text = await response.text();
  const body = text ? JSON.parse(text) : {};
  if (!response.ok) {
    throw new ApiError(
      response.status,
      body.error ?? "request_failed",
      body.message ?? response.statusText,
    );
  }
  return body as T;
}
```

Centralize credentials, error normalization, and 401 handling at this
boundary. Prefer HttpOnly cookie sessions when the app controls the server;
do not put server session secrets in localStorage.

## Query conventions

Export `queryOptions` so routes and components use the same key and query
function:

```ts
export const widgetKeys = {
  all: ["widget"] as const,
  list: (filters: WidgetFilters) =>
    [...widgetKeys.all, "list", filters] as const,
  detail: (id: string) => [...widgetKeys.all, id] as const,
};

export const widgetListQuery = (filters: WidgetFilters) =>
  queryOptions({
    queryKey: widgetKeys.list(filters),
    queryFn: () => loadWidgets(filters),
    placeholderData: keepPreviousData,
  });
```

Prewarm route-critical data with `ensureQueryData` in the route loader.

After a mutation, invalidate the narrowest complete prefix. For related
domains, centralize the fan-out in one invalidation graph instead of scattering
extra invalidations across components. Prefer invalidation/refetch over
optimistic cache editing unless latency makes optimism materially better.

Every data surface needs loading, empty, error, and stale/refetch behavior.

## Router search state

Use `validateSearch` with Zod and a safe fallback for every field:

```ts
const searchSchema = z.object({
  q: z.string().optional().catch(undefined),
  status: z.enum(["all", "active", "archived"]).catch("all"),
  sort: z.enum(["updatedAt", "name"]).catch("updatedAt"),
  page: z.number().int().min(0).catch(0),
});
```

Feed the validated search object directly into the Query key. Reset the page
when filters or sort change. This keeps URL, cache, and fetch inputs aligned.

## Zustand

Default to one `src/store/ui.ts`, matching emcp's shape. It may own:

- sidebar pin state;
- command palette visibility;
- theme preference;
- other cross-route interface preferences.

Split a store only when a domain has a distinct lifecycle, persistence rule,
or ownership boundary. Do not create one file per boolean.

For code outside React, use the store's `getState()` directly or expose a
small facade. Keep persisted keys explicit and versioned when the stored shape
may migrate.

## Forms

Use local state for a tiny form with one or two fields and trivial checks.

Use TanStack Form when the form has any of these:

- a Zod schema or field-level validation;
- three or more related fields;
- nested/repeating values;
- dependent fields;
- reusable field components;
- server errors that map back to fields.

The server remains authoritative. Disable duplicate submission, show pending
state inside the action, focus the first invalid field, and keep labels visible.
Use Query mutations for submission and invalidate the correct keys on success.

## Auth

For cookie auth, define a `whoamiQuery`. Guard the product layout in
`beforeLoad`:

```ts
beforeLoad: async ({ context, location }) => {
  const auth = await context.queryClient.ensureQueryData(whoamiQuery);
  if (!auth) throw redirect({ to: "/login", search: { redirect: location.href } });
},
```

Keep "not signed in" separate from "signed in but not allowed". Redirect the
first to login and render a plain no-access route for the second.

## Errors and feedback

Use typed errors carrying a machine code and human message. Show mutation
failures through the shadcn Sonner component unless the user must read the
error next to a field.
Use inline error states for failed page queries with a retry action. Never turn
all errors into a generic "Something went wrong" toast.
