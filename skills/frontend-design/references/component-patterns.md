# Component Patterns

Reusable Astro + React component examples following the design language.

## Accessibility Defaults (Quick Rules)

- Prefer semantic controls: `<button>` for actions, `<a>` for navigation (avoid click handlers on `<div>`).
- Icon-only buttons must have an `aria-label`.
- Disclosures/menus: wire `aria-expanded` + `aria-controls`.
- Inputs must have an associated label (visible label preferred); use `aria-describedby` for helper/error text.
- Modals/dialogs must trap focus and restore focus on close (if you build a modal island, treat this as required).

## Navbar

```astro
---
import ThemeToggle from './ThemeToggle.astro';

const links = [
  { label: 'Home', href: '/' },
  { label: 'Services', href: '/services' },
  { label: 'About', href: '/about' },
  { label: 'Contact', href: '/contact' },
];
---
<header class="sticky top-0 z-50 border-b border-base-300 bg-base-100/80 backdrop-blur-md">
  <nav class="mx-auto flex h-16 max-w-7xl items-center justify-between px-4 sm:px-6 lg:px-8">
    <a href="/" class="text-xl font-bold text-base-content">Brand</a>
    <div class="hidden items-center gap-8 md:flex">
      {links.map(link => (
        <a
          href={link.href}
          class="text-sm font-medium text-base-content/70 transition-colors hover:text-primary"
        >
          {link.label}
        </a>
      ))}
    </div>
    <div class="flex items-center gap-2">
      <ThemeToggle />
      <a href="/contact" class="btn btn-primary btn-sm hidden md:inline-flex">Get Started</a>
    </div>
  </nav>
</header>
```

## ThemeToggle (Astro, No Island)

```astro
---
// src/components/ThemeToggle.astro
---
<button type="button" class="btn btn-ghost btn-circle" aria-label="Toggle theme" data-theme-toggle>
  <span aria-hidden="true">🌓</span>
</button>

<script is:inline>
  (function () {
    var LIGHT = 'brand-light';
    var DARK = 'brand-dark';

    function getCurrentTheme() {
      return document.documentElement.getAttribute('data-theme') || LIGHT;
    }

    function setTheme(theme) {
      localStorage.setItem('theme', theme);
      document.documentElement.setAttribute('data-theme', theme);
    }

    function toggleTheme() {
      var current = getCurrentTheme();
      setTheme(current === DARK ? LIGHT : DARK);
    }

    var buttons = document.querySelectorAll('[data-theme-toggle]');
    for (var i = 0; i < buttons.length; i++) {
      buttons[i].addEventListener('click', toggleTheme);
    }
  })();
</script>
```

## Mobile Menu (React Island)

Use `client:media="(max-width: 768px)"` so the JS is only loaded on mobile.

```tsx
// src/components/react/MobileMenu.tsx
import { useState } from 'react';

interface Link {
  label: string;
  href: string;
}

interface Props {
  links: Link[];
}

export default function MobileMenu({ links }: Props) {
  const [open, setOpen] = useState(false);

  return (
    <div className="md:hidden">
      <button
        onClick={() => setOpen(!open)}
        className="btn btn-ghost btn-square"
        aria-label="Toggle menu"
        aria-expanded={open}
      >
        <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          {open
            ? <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            : <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
          }
        </svg>
      </button>
      {open && (
        <div className="absolute left-0 right-0 top-16 z-40 border-b border-base-300 bg-base-100 px-4 py-4 shadow-lg">
          <ul className="space-y-2">
            {links.map(link => (
              <li key={link.href}>
                <a
                  href={link.href}
                  className="block rounded-lg px-3 py-2 text-base font-medium text-base-content/80 transition-colors hover:bg-base-200 hover:text-primary"
                >
                  {link.label}
                </a>
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}
```

## SectionHeading (Reusable)

```astro
---
interface Props {
  label?: string;
  heading: string;
  subtitle?: string;
  align?: 'center' | 'left';
}

const { label, heading, subtitle, align = 'center' } = Astro.props;
const alignClass = align === 'center' ? 'text-center' : 'text-left';
---
<div class={`mb-12 ${alignClass}`}>
  {label && (
    <p class="mb-4 text-sm font-medium uppercase tracking-wider text-primary">{label}</p>
  )}
  <h2 class="mb-4 text-3xl font-bold text-base-content md:text-4xl">{heading}</h2>
  {subtitle && (
    <p class={`text-lg text-base-content/70 ${align === 'center' ? 'mx-auto max-w-2xl' : 'max-w-2xl'}`}>
      {subtitle}
    </p>
  )}
</div>
```

## Feature Grid (3-column with icons)

```astro
---
import SectionHeading from './SectionHeading.astro';

interface Feature {
  icon: string;
  title: string;
  description: string;
}

interface Props {
  label?: string;
  heading: string;
  subtitle?: string;
  features: Feature[];
  bgAlt?: boolean;
}

const { label, heading, subtitle, features, bgAlt = false } = Astro.props;
---
<section class={`py-16 md:py-24 ${bgAlt ? 'bg-base-200' : 'bg-base-100'}`}>
  <div class="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
    <SectionHeading label={label} heading={heading} subtitle={subtitle} />
    <div class="grid grid-cols-1 gap-6 md:grid-cols-2 md:gap-8 lg:grid-cols-3">
      {features.map(f => (
        <div class="card border border-base-300 bg-base-100 shadow-sm transition-shadow hover:shadow-md">
          <div class="card-body">
            <div class="mb-3 text-3xl">{f.icon}</div>
            <h3 class="card-title text-lg font-semibold">{f.title}</h3>
            <p class="text-base-content/70">{f.description}</p>
          </div>
        </div>
      ))}
    </div>
  </div>
</section>
```

## Testimonial / Quote Block

```astro
---
interface Props {
  quote: string;
  author: string;
  role?: string;
}
const { quote, author, role } = Astro.props;
---
<blockquote class="mx-auto max-w-5xl py-12 text-center">
  <p class="mb-6 text-xl italic text-base-content/80 md:text-2xl">&ldquo;{quote}&rdquo;</p>
  <footer>
    <p class="font-semibold text-base-content">{author}</p>
    {role && <p class="text-sm text-base-content/60">{role}</p>}
  </footer>
</blockquote>
```

## Contact Form (React Island)

```tsx
// src/components/react/ContactForm.tsx
import { useState, type FormEvent } from 'react';

export default function ContactForm() {
  const [status, setStatus] = useState<'idle' | 'sending' | 'sent' | 'error'>('idle');

  async function handleSubmit(e: FormEvent<HTMLFormElement>) {
    e.preventDefault();
    setStatus('sending');
    try {
      const data = new FormData(e.currentTarget);
      await fetch('/api/contact', { method: 'POST', body: data });
      setStatus('sent');
    } catch {
      setStatus('error');
    }
  }

  if (status === 'sent') {
    return (
      <div className="alert alert-success">
        <span>Thank you! We'll be in touch shortly.</span>
      </div>
    );
  }

  return (
    <form onSubmit={handleSubmit} className="mx-auto max-w-lg space-y-4">
      <div className="form-control">
        <label className="label"><span className="label-text">Name</span></label>
        <input name="name" type="text" required className="input input-bordered w-full" />
      </div>
      <div className="form-control">
        <label className="label"><span className="label-text">Email</span></label>
        <input name="email" type="email" required className="input input-bordered w-full" />
      </div>
      <div className="form-control">
        <label className="label"><span className="label-text">Message</span></label>
        <textarea name="message" required rows={4} className="textarea textarea-bordered w-full" />
      </div>
      {status === 'error' && (
        <div className="alert alert-error">
          <span>Something went wrong. Please try again.</span>
        </div>
      )}
      <button type="submit" className="btn btn-primary w-full" disabled={status === 'sending'}>
        {status === 'sending' ? 'Sending\u2026' : 'Send Message'}
      </button>
    </form>
  );
}
```

Usage: `<ContactForm client:visible />`

## Loading Skeleton (DaisyUI)

```astro
<div class="space-y-3">
  <div class="skeleton h-6 w-48"></div>
  <div class="skeleton h-4 w-full"></div>
  <div class="skeleton h-4 w-5/6"></div>
</div>
```

## Empty State (Card)

```astro
<div class="card border border-base-300 bg-base-100">
  <div class="card-body items-center text-center">
    <div class="text-3xl" aria-hidden="true">🗂️</div>
    <h3 class="card-title">Nothing here yet</h3>
    <p class="text-base-content/70">Add your first item to get started.</p>
    <div class="card-actions mt-2">
      <button type="button" class="btn btn-primary btn-sm">Add item</button>
    </div>
  </div>
</div>
```

## Error State (Retry)

```astro
<div class="alert alert-error">
  <span>Unable to load data. Please try again.</span>
  <div class="ml-auto">
    <button type="button" class="btn btn-ghost btn-sm">Retry</button>
  </div>
</div>
```

## Async Island Pattern (Loading / Empty / Error)

```tsx
// src/components/react/ItemsWidget.tsx
import { useEffect, useState } from 'react';

type Item = { id: string; name: string };

export default function ItemsWidget() {
  const [status, setStatus] = useState<'loading' | 'ready' | 'error'>('loading');
  const [items, setItems] = useState<Item[]>([]);

  async function load() {
    setStatus('loading');
    try {
      const res = await fetch('/api/items');
      if (!res.ok) throw new Error('Request failed');
      const data = (await res.json()) as Item[];
      setItems(data);
      setStatus('ready');
    } catch {
      setStatus('error');
    }
  }

  useEffect(() => {
    void load();
  }, []);

  if (status === 'loading') {
    return (
      <div className="space-y-3">
        <div className="skeleton h-6 w-48" />
        <div className="skeleton h-4 w-full" />
        <div className="skeleton h-4 w-5/6" />
      </div>
    );
  }

  if (status === 'error') {
    return (
      <div className="alert alert-error">
        <span>Unable to load items.</span>
        <button type="button" className="btn btn-ghost btn-sm ml-auto" onClick={load}>
          Retry
        </button>
      </div>
    );
  }

  if (items.length === 0) {
    return <div className="alert"><span>No items yet.</span></div>;
  }

  return (
    <ul className="space-y-2">
      {items.map((it) => (
        <li key={it.id} className="rounded-lg border border-base-300 bg-base-100 px-3 py-2">
          {it.name}
        </li>
      ))}
    </ul>
  );
}
```

## Footer

```astro
---
const year = new Date().getFullYear();
const sections = {
  company: [
    { label: 'About', href: '/about' },
    { label: 'Services', href: '/services' },
    { label: 'Contact', href: '/contact' },
  ],
  legal: [
    { label: 'Privacy', href: '/privacy' },
    { label: 'Terms', href: '/terms' },
  ],
};
---
<footer class="border-t border-base-300 bg-base-200">
  <div class="mx-auto max-w-7xl px-4 py-12 sm:px-6 lg:px-8">
    <div class="grid grid-cols-1 gap-8 md:grid-cols-3">
      <div>
        <p class="mb-2 text-lg font-bold text-base-content">Brand</p>
        <p class="text-sm text-base-content/60">Short brand description.</p>
      </div>
      <div>
        <p class="mb-3 text-sm font-semibold text-base-content">Company</p>
        <ul class="space-y-2">
          {sections.company.map(l => (
            <li>
              <a href={l.href} class="text-sm text-base-content/60 transition-colors hover:text-primary">
                {l.label}
              </a>
            </li>
          ))}
        </ul>
      </div>
      <div>
        <p class="mb-3 text-sm font-semibold text-base-content">Legal</p>
        <ul class="space-y-2">
          {sections.legal.map(l => (
            <li>
              <a href={l.href} class="text-sm text-base-content/60 transition-colors hover:text-primary">
                {l.label}
              </a>
            </li>
          ))}
        </ul>
      </div>
    </div>
    <div class="mt-8 border-t border-base-300 pt-8 text-center">
      <p class="text-sm text-base-content/50">&copy; {year} Brand. All rights reserved.</p>
    </div>
  </div>
</footer>
```

## BaseLayout (Full Example)

```astro
---
import '@/styles/global.css';
import Header from '@/components/Header.astro';
import Footer from '@/components/Footer.astro';

interface Props {
  title: string;
  description?: string;
}

const { title, description = '' } = Astro.props;
---
<!doctype html>
<html lang="en" class="h-full">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <meta name="description" content={description} />
    <link rel="icon" href="/favicon.ico" />
    <meta name="generator" content={Astro.generator} />
    <script is:inline>
      (function() {
        var t = localStorage.getItem('theme');
        if (!t) t = window.matchMedia('(prefers-color-scheme: dark)').matches ? 'brand-dark' : 'brand-light';
        document.documentElement.setAttribute('data-theme', t);
      })();
    </script>
    <title>{title}</title>
  </head>
  <body class="flex min-h-svh flex-col bg-base-100 text-base-content">
    <Header />
    <main class="flex-1">
      <slot />
    </main>
    <Footer />
  </body>
</html>
```
