# TanStack Start scaffold

Use TanStack Start for the public site and authenticated product. Keep one app,
one router, one token system, and separate public/product shells.

## Folder shape

For a single application:

```text
src/
├── router.tsx
├── routeTree.gen.ts                 # generated; never edit
├── styles/
│   └── app.css
├── routes/
│   ├── __root.tsx
│   ├── index.tsx                    # public home
│   ├── pricing.tsx                  # public
│   ├── login.tsx
│   ├── app.tsx                      # auth guard + product shell
│   ├── app.index.tsx
│   └── app.widgets.index.tsx
├── components/
│   ├── AppShell.tsx
│   ├── ui-composites.tsx
│   ├── marketing/
│   │   ├── site.tsx                 # public shell and public composites
│   │   └── visuals.tsx
│   └── ui/                          # shadcn-owned local component source
├── lib/
│   ├── api.ts
│   ├── colors.ts
│   └── utils.ts
├── queries/                         # queryOptions and key factories
├── server/
│   └── fns.ts                       # server boundary
├── store/
│   └── ui.ts                        # one Zustand UI store by default
└── hooks/
    └── use-mobile.ts
```

In a monorepo, place the same shape under `apps/web`. Use the repository's
existing alias and naming rules. The bundled assets use `@/*`; adjust their
imports once if the project uses another alias.

Routes may contain route-specific page composition, as emcp does. Extract
reusable or hard-to-test behavior into components; do not create a `pages/`
mirror that only adds indirection.

There is no `index.html` and no `main.tsx`. TanStack Start owns the document
and entry points.

## Initialize shadcn/ui

Use the official shadcn CLI. For a new TanStack Start project:

```bash
pnpm dlx shadcn@latest init --template start --base base
```

For an existing TanStack Start project that does not yet have shadcn:

```bash
pnpm dlx shadcn@latest init --base base
```

Verify the detected framework, aliases, CSS file, and selected primitive base:

```bash
pnpm dlx shadcn@latest info
```

Install only components the product uses. A typical application shell starts
with:

```bash
pnpm dlx shadcn@latest add button input label card badge separator sheet sidebar dialog alert-dialog dropdown-menu tooltip sonner
```

Use `pnpm dlx shadcn@latest docs <component>` before adapting unfamiliar
components. Commit the generated `components.json` and local component source.
Do not manually add `@base-ui/react`; the chosen shadcn registry variant owns
that dependency. Do not replace generated components with bundled lookalikes.
Merge the tokens, font imports, theme selector, and house utilities from
`assets/styles.css` into the stylesheet created by shadcn. Preserve shadcn's
required imports and base layer instead of replacing the file wholesale.

## Dependencies

Baseline:

```jsonc
"@fontsource-variable/geist": "^5.2.9",
"@fontsource-variable/geist-mono": "^5.2.8",
"@tanstack/react-query": "^5.101.0",
"@tanstack/react-router": "^1.170.0",
"@tanstack/react-router-ssr-query": "^1.167.0",
"@tanstack/react-start": "^1.168.0",
"class-variance-authority": "^0.7.1",
"lucide-react": "^1.0.0",
"react": "^19.2.0",
"react-dom": "^19.2.0",
"srvx": "^0.11.0",
"tailwind-merge": "^3.6.0",
"zod": "^3.25.0",
"zustand": "^5.0.0"
```

Add as needed:

- `@tanstack/react-table` for reusable sorting, selection, visibility, or
  pagination;
- `@tanstack/react-form` for schema-backed or multi-field forms;
- `@tanstack/react-virtual` for genuinely large visible lists;
- `@tanstack/react-query-devtools` and router devtools in development only.

Development baseline:

```jsonc
"@tailwindcss/vite": "^4.3.0",
"@testing-library/dom": "^10.4.0",
"@testing-library/react": "^16.3.0",
"@types/node": "^22.0.0",
"@types/react": "^19.2.0",
"@types/react-dom": "^19.2.0",
"@vitejs/plugin-react": "^6.0.0",
"happy-dom": "^20.0.0",
"tailwindcss": "^4.3.0",
"typescript": "^5.9.0",
"vite": "^8.0.0",
"vitest": "^4.1.0"
```

Use versions already resolved by an existing workspace. Do not churn a lock
file merely to match these examples.

## Scripts

```jsonc
"dev": "vite dev --port 3000 --host",
"build": "vite build",
"start": "srvx serve --prod --dir . --entry dist/server/server.js --static dist/client --port 3000",
"typecheck": "tsc --noEmit",
"test": "vitest run --passWithNoTests"
```

The `srvx` flags matter: `--dir . --static dist/client` keeps static asset
resolution correct.

## Vite

```ts
import tailwindcss from "@tailwindcss/vite";
import { tanstackStart } from "@tanstack/react-start/plugin/vite";
import viteReact from "@vitejs/plugin-react";
import { defineConfig } from "vite";

export default defineConfig({
  server: { port: 3000 },
  resolve: { tsconfigPaths: true },
  plugins: [
    tailwindcss(),
    tanstackStart(),
    // Keep React after Start.
    viteReact(),
  ],
});
```

For a public-plus-product build, prerender only public paths:

```ts
const PUBLIC_PATHS = new Set(["/", "/pricing", "/blog", "/privacy", "/terms"]);
const isPublicPath = (path: string) =>
  PUBLIC_PATHS.has(path) || path.startsWith("/blog/");

tanstackStart({
  prerender: {
    enabled: true,
    crawlLinks: true,
    failOnError: true,
    filter: (page) => isPublicPath(page.path),
  },
});
```

Use SPA mode only for a truly serverless tool:

```ts
tanstackStart({ spa: { enabled: true } });
```

## Strict TypeScript

At minimum enable `strict`, `noUncheckedIndexedAccess`, bundler module
resolution, `isolatedModules`, `verbatimModuleSyntax`, and `noEmit`. Use one
source alias consistently.

## Root document

Import the bundled fonts from `styles/app.css`, then attach that stylesheet in
the root route. Set the theme before paint:

```tsx
import type { QueryClient } from "@tanstack/react-query";
import {
  HeadContent,
  Outlet,
  Scripts,
  createRootRouteWithContext,
} from "@tanstack/react-router";
import type { ReactNode } from "react";
import { Toaster } from "@/components/ui/sonner";
import appCss from "@/styles/app.css?url";

export interface RouterContext {
  queryClient: QueryClient;
}

export const Route = createRootRouteWithContext<RouterContext>()({
  head: () => ({
    meta: [
      { charSet: "utf-8" },
      { name: "viewport", content: "width=device-width, initial-scale=1" },
      { title: "App name" },
    ],
    links: [{ rel: "stylesheet", href: appCss }],
    scripts: [
      {
        children: `(function(){try{var m=localStorage.getItem("app:theme")||"system";var d=matchMedia("(prefers-color-scheme: dark)").matches;var t=m==="dark"||(m==="system"&&d)?"dark":"light";document.documentElement.dataset.theme=t;document.documentElement.style.colorScheme=t;}catch(e){}})();`,
      },
    ],
  }),
  component: Root,
});

function Root() {
  return (
    <Document>
      <Outlet />
      <Toaster />
    </Document>
  );
}

function Document({ children }: { children: ReactNode }) {
  return (
    <html lang="en" data-theme="dark" suppressHydrationWarning>
      <head>
        <HeadContent />
      </head>
      <body className="min-h-dvh bg-background text-foreground antialiased">
        {children}
        <Scripts />
      </body>
    </html>
  );
}
```

Rename `app:theme` and keep it identical in the boot script and Zustand store.

## Router and Query integration

Create one `QueryClient`, pass it in router context, and install
`setupRouterSsrQueryIntegration`. Let Query own freshness:

```ts
queries: {
  staleTime: 30_000,
  gcTime: 5 * 60_000,
  retry: 1,
  refetchOnWindowFocus: false,
}
```

Set Router `defaultPreload: "intent"`, `defaultPreloadStaleTime: 0`, and
`scrollRestoration: true`.

## First verification

Before page work, verify:

1. dev server renders the root route;
2. reload shows no theme flash;
3. `pnpm typecheck`, tests, and build pass;
4. public prerender output exists when enabled;
5. `routeTree.gen.ts` is generated, not edited by hand.
