# Authenticated application shell

Use the emcp shell pattern for products with several destinations: persistent
sidebar, compact top bar, command/search affordance when useful, theme control,
and account menu.

## Structure

```tsx
<SidebarProvider
  open={sidebarOpen || preview}
  onOpenChange={setSidebarOpen}
  data-hover-preview={!sidebarOpen && preview ? "true" : undefined}
>
  <Sidebar
    collapsible="icon"
    onMouseEnter={() => setPreview(true)}
    onMouseLeave={() => setPreview(false)}
    onFocusCapture={() => setPreview(true)}
    onBlurCapture={handleBlur}
  >
    <SidebarHeader>{/* brand + pin control */}</SidebarHeader>
    <SidebarContent>{/* navigation groups */}</SidebarContent>
    <SidebarFooter>{/* account menu */}</SidebarFooter>
    <SidebarRail />
  </Sidebar>
  <SidebarInset>
    <TopBar />
    <main className="min-w-0 w-full flex-1 px-4 py-4 sm:px-6 sm:py-5">
      <Outlet />
    </main>
  </SidebarInset>
</SidebarProvider>
```

The sidebar pin, palette state, and theme preference normally come from the
single Zustand UI store. Use the shadcn Sonner component for transient
notifications rather than duplicating a toast queue in Zustand.

## Sidebar

- Expanded width: about 256px; icon rail: about 48px.
- Row: 32px high, 16px icon, `text-sm`, quiet active surface plus a thin
  primary indicator.
- Persist pinned open/collapsed state.
- `Ctrl/Cmd+B` toggles the pin.
- When collapsed, hover/focus may preview the full panel as an overlay without
  moving the page content.
- On mobile, render the same navigation in a shadcn Sheet.
- Add group labels only when groups are real and useful.

Do not create a second mobile navigation model with different destinations.

## Top bar

Use a 48px bar for the product:

```tsx
<header className="sticky top-0 z-10 flex h-12 shrink-0 items-center gap-2 border-b bg-background/85 px-4 backdrop-blur-sm sm:px-6">
  <SidebarTrigger />
  <Separator orientation="vertical" className="mr-1 data-vertical:h-5" />
  {/* context, breadcrumbs, or command search */}
  <div className="ml-auto flex items-center gap-2">...</div>
</header>
```

Global navigation/search/theme/account belong here. Route-specific create,
edit, export, and destructive actions belong in the page header.

## Command palette

Add it only when there are several destinations or meaningful cross-domain
search. Open with `Ctrl/Cmd+K`, close with Escape, and show the shortcut in
the top bar. Use a shadcn Dialog or a small accessible combobox/dialog
composition; do not add a library only for a short static list.

## Theme control

Use the behavior chosen for the project:

- two-state light/dark for a deliberately dark-first product, as emcp does;
- three-state system/light/dark when respecting OS preference is part of the
  product contract.

The boot script and Zustand persistence key must match. Always update
`color-scheme` with `data-theme`.

## Account menu

Show identity and role in the sidebar footer. Put profile/security/sign-out
actions in a shadcn Dropdown Menu. Keep destructive account actions visually distinct
and confirm actions with irreversible consequences.

## Accessibility and responsive behavior

- Preserve visible focus rings.
- Give icon-only controls accessible names and tooltips.
- Ensure sidebar hover preview also works through focus.
- Make mobile targets at least 44px even though desktop shell rows are compact.
- Close mobile navigation after route changes.
- Verify keyboard navigation through sidebar, palette, account menu, and
  dialogs.
