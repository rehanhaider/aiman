# Product routes and page patterns

Keep authenticated product routes under one guarded layout (`/app/*` by
default). The layout owns auth and the app shell; child routes own domain page
composition.

## Route conventions

```text
routes/__root.tsx
routes/login.tsx
routes/app.tsx
routes/app.index.tsx
routes/app.widgets.index.tsx
routes/app.widgets.$id.tsx
routes/app.settings.tsx
```

Use `beforeLoad` for guards and redirects, `validateSearch` for URL state, and
`loader` with `ensureQueryData` for route-critical data. Route modules may
contain page-specific composition. Extract reusable behavior and large tested
units rather than creating a second file for every route automatically.

## Page frame

The app shell supplies the normal frame:

```tsx
<main className="min-w-0 w-full flex-1 px-4 py-4 sm:px-6 sm:py-5">
  {children}
</main>
```

Do not add another full page wrapper with duplicate padding inside every
route.

## List pages

Order:

1. PageHeader with title, short subtitle/count, and primary action.
2. Search/filter row, normally one wrapping line.
3. Table or domain-appropriate card/board view.
4. Empty or error state in the same content region.
5. Pagination and selection actions.

Use Router search params for filters, sort, page, and view. Debounce only text
input; update discrete filters immediately. Reset the page when filter or sort
changes.

Use TanStack Table when the list supports sorting, selection, server
pagination, reusable column definitions, or column visibility. Set
`manualSorting` and `manualPagination` when the server owns them. Keep row
navigation accessible; do not make interactive controls inside a row trigger
row navigation.

Product table baseline:

- header: `text-xs font-medium text-muted-foreground`;
- cells: `px-3 py-2 text-sm`;
- row hover: quiet muted surface;
- numeric/id/date data: mono or tabular numerals;
- shell: `overflow-x-auto rounded-xl border bg-card`.

## Detail pages

Header: back context, title, status, key metadata, primary action, and overflow
menu for secondary/destructive work.

Body: `grid gap-4` with SectionCard panels. Use a `2fr 1fr` split when there
is a clear primary record and supporting metadata; otherwise use one readable
column. Definition rows normally use a 120–160px label column.

Keep destructive actions behind a clear confirmation that names the affected
record and consequence.

## Forms

Use local state for one or two trivial fields. Prefer TanStack Form plus Zod
for larger or validated forms. Reuse field components for label, description,
control, and error placement.

- Disable duplicate submission.
- Keep entered values after a server error.
- Show field errors next to fields and non-field errors above actions.
- Use Query mutations and invalidate affected keys on success.
- In a dialog, close only after success.
- In a full page, support cancel/back without accidental data loss when the
  form is substantial.

Product form controls use the product scale; public contact/signup forms use
the public scale from `marketing.md`.

## Dashboard/home

Do not default to four meaningless stat cards. Choose the smallest set of
information that helps the user act:

- urgent work or approvals;
- recent activity;
- pipeline/list status;
- shortcuts to common actions;
- genuinely useful metrics.

Use cards, lists, or a compact chart only when the data relationship warrants
them. Values use tabular numerals. Avoid decorative percentage deltas without
context.

## Empty, loading, and error behavior

The shell should stay stable while route data changes. Use skeletons in the
final layout, a specific EmptyState when there are no records, and an inline
error state with retry when a query fails. Preserve stale data during refetch
when it remains safe to show.

## Full-screen workbenches

For editors and complex workbenches, render one component in a fixed
`inset-0` product surface, close on Escape, trap focus when appropriate, and
avoid duplicating the editor markup for embedded and full-screen modes.
