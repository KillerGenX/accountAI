---
title: Frontend Guidelines
version: 2.0.0
status: Approved
owner: Chief Architect
last_updated: 2026-07-18
---

# 25 — Frontend Guidelines

> **"The frontend is not just a UI. It is the user's perception of our product's quality. If it is slow, the AI is perceived as dumb. If it is buggy, the AI is perceived as broken."**

---

# Purpose

This document outlines the architectural patterns and best practices for the Next.js frontend application in PROJECT BRAIN. The frontend architecture must gracefully handle the asynchronous, sometimes slow, and highly dynamic nature of AI-generated content.

---

# 1. Architecture: Next.js App Router (RSC)

We strictly use the Next.js App Router (`/app` directory) and fully embrace React Server Components (RSC).

### The "Server-First" Mental Model
- **Server Components by Default:** All components are Server Components unless explicitly marked with `"use client"`. Server Components fetch data securely, execute on the server, and send zero JavaScript to the browser.
- **Pushing State Down:** Do not place `"use client"` at the top of a page layout. Push client interactivity to the leaf nodes of your component tree. 
  - *Example:* Instead of making the entire `AccountDashboard` a client component just to have a togglable sidebar, extract the sidebar toggle into a `SidebarButton` client component and leave the dashboard as a Server Component.

---

# 2. State Management Strategy

We use a tri-partite state management strategy. Never mix these up.

### 2.1. URL State (The Source of Truth)
If a piece of state dictates what the user is currently looking at (e.g., active tab, search query, pagination page, selected filter), **it belongs in the URL query parameters**, not in React state.
- ✅ *Why?* Users can bookmark, share links, and refresh the page without losing their place.

### 2.2. Server State (React Query / TanStack)
If a piece of state comes from the database via an API, it is Server State.
- Do not use `useEffect` and `useState` to fetch and store data.
- **Always use React Query (`useQuery`, `useMutation`).** It handles caching, background refetching, deduplication, and loading/error states out of the box.

### 2.3. Global Client State (Zustand)
If a piece of ephemeral UI state needs to be accessed by deeply nested components across different branches of the DOM (e.g., global theme, currently active modal, toast notification queue), use **Zustand**.
- Avoid React Context for frequently changing values to prevent unnecessary re-renders.

---

# 3. Styling & UI Primitives

### 3.1. Tailwind CSS
We use Tailwind CSS exclusively for styling.
- Do not write raw CSS or SCSS modules unless handling highly specific complex animations that Tailwind cannot support.
- Use a utility function like `cn()` (combining `clsx` and `tailwind-merge`) to conditionally merge classes without specificity conflicts.

```tsx
// ❌ BAD: Messy string interpolation, risk of conflicting classes
<div className={`p-4 bg-white ${isActive ? "bg-blue-500 text-white" : ""}`}>

// ✅ GOOD: Clean merging, later classes override earlier ones properly
<div className={cn("p-4 bg-white", isActive && "bg-blue-500 text-white")}>
```

### 3.2. shadcn/ui & Radix
We do not use bloated component libraries like Material-UI or Ant Design. We use `shadcn/ui` built on top of `Radix UI`.
- These are headless primitives that we copy into our codebase (`components/ui/`).
- They provide total control over styling while guaranteeing W3C accessibility (ARIA attributes, keyboard navigation).

---

# 4. Handling AI Latency (Optimistic UI)

AI operations are slow. We cannot make the user stare at a spinner for 45 seconds while an AI worker researches a company.

1. **Immediate Acknowledgment:** When a user triggers an AI task, immediately create a local placeholder record in the UI using React Query's `onMutate` (Optimistic Update) with a "Processing" status.
2. **Polling vs WebSockets:** To detect when the AI task finishes:
   - *Phase 1 (MVP):* Use React Query polling (refetch interval every 3 seconds) on the specific task status endpoint.
   - *Phase 2:* Implement Server-Sent Events (SSE) or WebSockets tied to the NATS event bus.
3. **Skeleton Loaders:** Do not use full-page loading spinners. Use skeleton UI components that match the shape of the content being loaded.

---

# 5. Directory Structure

```text
/app
  /api              # Next.js Route Handlers (BFF pattern)
  /(dashboard)      # Route group for authenticated layout
    /accounts       # Page route
  /login            # Public page route
/components
  /ui               # Generic, reusable primitives (shadcn)
  /forms            # Reusable form components (react-hook-form)
  /domain           # Domain-specific components (e.g., AccountProfileCard)
/lib
  /utils            # Helper functions (cn, formatters)
  /api              # Axios/Fetch clients calling the Python Backend
/hooks              # Custom React hooks
/store              # Zustand global state stores
/types              # Shared TypeScript definitions
```

---

# 6. Error Handling

- **Route Boundaries:** Every major route segment must have an `error.tsx` file to catch rendering errors gracefully without crashing the entire app.
- **Form Validation:** We use `react-hook-form` paired with `zod` for schema validation. Form validation rules must mirror the Pydantic schemas on the backend perfectly.
- **User Feedback:** Every mutation (POST/PUT/DELETE) must result in a Toast notification indicating success or failure.
