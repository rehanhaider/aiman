---
name: react-expert
description: Use when building React 18/19 applications in .jsx or .tsx files, Next.js App Router projects, or Vite setups. Creates components, implements custom hooks, debugs rendering issues, migrates class components to functional, and implements state management. Invoke for Server Components, Suspense boundaries, useActionState forms, React Compiler adoption, performance optimization, or React 19 features.
license: MIT
metadata:
  author: https://github.com/Jeffallan
  version: "1.1.0"
  domain: frontend
  triggers: React, JSX, hooks, useState, useEffect, useContext, Server Components, React 19, Suspense, TanStack Query, Redux, Zustand, component, frontend
  role: specialist
  scope: implementation
  output-format: code
  related-skills: playwright-expert, frontend-design
---

# React Expert

Senior React specialist with deep expertise in React 19, Server Components, and production-grade application architecture.

## When to Use This Skill

- Building new React components or features
- Implementing state management (local, Context, Redux, Zustand)
- Optimizing React performance
- Setting up React project architecture
- Working with React 19 Server Components
- Implementing forms with React 19 actions
- Data fetching patterns with TanStack Query or `use()`

## Core Workflow

1. **Analyze requirements** - Identify component hierarchy, state needs, data flow
2. **Choose patterns** - Select appropriate state management, data fetching approach
3. **Implement** - Write TypeScript components with proper types
4. **Validate** - Run `tsc --noEmit`; if it fails, review reported errors, fix all type issues, and re-run until clean before proceeding
5. **Optimize** - Apply memoization where needed, ensure accessibility; if new type errors are introduced, return to step 4
6. **Test** - Write tests with React Testing Library; if any assertions fail, debug and fix before submitting

## Reference Guide

Load detailed guidance based on context:

| Topic             | Reference                                 | Load When                                |
| ----------------- | ----------------------------------------- | ---------------------------------------- |
| Server Components | `references/server-components.md`         | RSC patterns, Next.js App Router         |
| React 19          | `references/react-19-features.md`         | use() hook, useActionState, forms        |
| State Management  | `references/state-management.md`          | Context, Zustand, Redux, TanStack        |
| Hooks             | `references/hooks-patterns.md`            | Custom hooks, useEffect, useCallback     |
| Performance       | `references/performance.md`               | memo, lazy, virtualization               |
| Testing           | `references/testing-react.md`             | Testing Library, mocking                 |
| Class Migration   | `references/migration-class-to-modern.md` | Converting class components to hooks/RSC |

## Key Patterns

### Server Component (Next.js App Router)
```tsx
// app/users/page.tsx — Server Component, no "use client"
import { db } from '@/lib/db';

interface User {
  id: string;
  name: string;
}

export default async function UsersPage() {
  const users: User[] = await db.user.findMany();

  return (
    <ul>
      {users.map((user) => (
        <li key={user.id}>{user.name}</li>
      ))}
    </ul>
  );
}
```

### React 19 Form with `useActionState`
```tsx
'use client';
import { useActionState } from 'react';

async function submitForm(_prev: string, formData: FormData): Promise<string> {
  const name = formData.get('name') as string;
  // perform server action or fetch
  return `Hello, ${name}!`;
}

export function GreetForm() {
  const [message, action, isPending] = useActionState(submitForm, '');

  return (
    <form action={action}>
      <input name="name" required />
      <button type="submit" disabled={isPending}>
        {isPending ? 'Submitting…' : 'Submit'}
      </button>
      {message && <p>{message}</p>}
    </form>
  );
}
```

### Memoization and the React Compiler

Check whether the project has the React Compiler enabled (`babel-plugin-react-compiler` / `reactCompiler: true` in Next.js) before writing memoization code:

- **Compiler enabled:** don't hand-write `useCallback`/`useMemo`/`memo` — the compiler memoizes automatically, and manual wrappers are noise it has to work around.
- **No compiler:** memoize *selectively*. An inline function in JSX is fine by itself — new function identity only matters when it's passed to a `memo`-wrapped child or used in a dependency array. Profile with React DevTools before adding memoization; reflexive `useCallback` everywhere makes code harder to read for zero measured gain.

### Custom Hook with Cleanup
```tsx
import { useState, useEffect } from 'react';

function useWindowWidth(): number {
  const [width, setWidth] = useState(() => window.innerWidth);

  useEffect(() => {
    const handler = () => setWidth(window.innerWidth);
    window.addEventListener('resize', handler);
    return () => window.removeEventListener('resize', handler); // cleanup
  }, []);

  return width;
}
```

## Constraints

### MUST DO
- Use TypeScript with strict mode
- Implement error boundaries for graceful failures
- Use `key` props correctly (stable, unique identifiers)
- Clean up effects (return cleanup function)
- Use semantic HTML and ARIA for accessibility
- Memoize callbacks/objects passed to memoized children (skip when the React Compiler is enabled — it does this automatically)
- Use Suspense boundaries for async operations

### MUST NOT DO
- Mutate state directly
- Use array index as key for dynamic lists
- Add `useCallback`/`useMemo` by reflex — inline functions in JSX are fine unless the receiver is memoized; measure first
- Forget useEffect cleanup (memory leaks)
- Ignore React strict mode warnings
- Skip error boundaries in production

## Output Templates

When implementing React features, provide:
1. Component file with TypeScript types
2. Test file if non-trivial logic
3. Brief explanation of key decisions

## Knowledge Reference

React 19, React Compiler, Server Components, use() hook, Suspense, TypeScript, TanStack Query, Zustand, Redux Toolkit, React Router, React Testing Library, Vitest/Jest, Next.js App Router, Vite, accessibility (WCAG)