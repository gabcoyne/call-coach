# Navigation and Layout Documentation

## Overview

The Gong Call Coaching frontend uses a responsive navigation system with a desktop sidebar and mobile hamburger menu. The layout is built using Next.js 15 App Router conventions.

## Components

### 1. Sidebar (`components/navigation/sidebar.tsx`)

Desktop navigation sidebar that appears on screens larger than 1024px (lg breakpoint).

**Features:**

- Logo and branding at the top
- Navigation links for main routes (Dashboard, Search, Feed, Calls, Profile)
- Active state highlighting using Prefect pink
- Version info in footer
- Fixed width of 256px (w-64)

**Navigation Links:**

- Dashboard (`/dashboard`) - LayoutDashboard icon
- Search (`/search`) - Search icon
- Feed (`/feed`) - Rss icon
- Calls (`/calls`) - Phone icon
- Profile (`/profile`) - User icon

### 2. Mobile Navigation (`components/navigation/mobile-nav.tsx`)

Mobile-first navigation that appears on screens smaller than 1024px.

**Features:**

- Fixed header with logo and hamburger menu
- Full-screen overlay menu when opened
- User avatar (Clerk UserButton) in header
- Same navigation links as desktop
- Closes automatically when a link is clicked

### 3. User Navigation (`components/navigation/user-nav.tsx`)

User profile component that displays at the bottom of the desktop sidebar.

**Features:**

- Clerk UserButton for authentication
- User name and email display
- Loading skeleton while user data loads
- Sign-out functionality
- Redirects to `/sign-in` after sign-out

### 4. Breadcrumb (`components/navigation/breadcrumb.tsx`)

Dynamic breadcrumb navigation for deep pages.

**Features:**

- Automatically generates breadcrumbs from URL path
- Home icon for root
- ChevronRight separators
- Active page is non-clickable and highlighted
- Hides on home page and single-level routes

**Special handling:**

- Formats path segments (capitalizes, removes hyphens)
- Known routes get proper labels (dashboard, search, feed, etc.)

## Layout Structure

### Root Layout (`app/layout.tsx`)

The main layout file that wraps all pages.

**Structure:**

```
<ClerkProvider>
  <html>
    <body>
      <div className="flex h-screen">
        {/* Desktop Sidebar + User Nav */}
        <Sidebar />
        <UserNav />

        {/* Main Content Area */}
        <div className="flex-1">
          <MobileNav />
          <Breadcrumb />
          <main>{children}</main>
        </div>
      </div>
    </body>
  </html>
</ClerkProvider>
```

**Key Features:**

- Clerk authentication wrapper
- Full-height layout with flex
- Responsive sidebar visibility
- Breadcrumb navigation
- Scrollable main content area

## Special Pages

### 1. Loading State (`app/loading.tsx`)

Global loading UI using React Suspense and Next.js loading.tsx convention.

**Features:**

- Skeleton components for header and content
- Grid layout matching typical page structure
- Automatically shown during route transitions

### 2. Error Boundary (`app/error.tsx`)

Client-side error boundary for handling runtime errors.

**Features:**

- Error message display
- Error digest for tracking
- "Try again" button to reset error
- "Go home" button for navigation
- Centered card layout
- Logs errors to console (integrate with error tracking service)

### 3. Not Found (`app/not-found.tsx`)

Custom 404 page for missing routes.

**Features:**

- Large 404 display
- Helpful messaging
- Navigation buttons to home and dashboard
- Consistent styling with design system

## Responsive Breakpoints

Based on Tailwind config (`tailwind.config.ts`):

- `xs`: 475px
- `sm`: 640px
- `md`: 768px
- `lg`: 1024px (sidebar breakpoint)
- `xl`: 1280px
- `2xl`: 1536px

## Styling

### Colors

Using Prefect brand colors from the design system:

- **Primary (Active state)**: Prefect Pink (`#FF4BBD`)
- **Background**: White (light mode) / Dark gray (dark mode)
- **Muted**: Subtle grays for inactive states
- **Accent**: Prefect Sunrise Orange for hover states

### Components Used

From the design system (`components/ui/*`):

- `Button` - Navigation toggle, action buttons
- `Card` - Error and 404 pages
- `Skeleton` - Loading states

### Icons

Using `lucide-react` for all icons:

- LayoutDashboard, Search, Rss, Phone, User (navigation)
- Menu, X (mobile menu toggle)
- ChevronRight, Home (breadcrumbs)
- AlertCircle, FileQuestion (error states)

## Integration Points

### Clerk Authentication

- `ClerkProvider` wraps entire app
- `UserButton` in navigation components
- `useUser()` hook for user data
- `afterSignOutUrl` configured to `/sign-in`

### Next.js Features

- App Router for file-based routing
- `usePathname()` for active state detection
- Server Components by default
- Client Components marked with "use client"
- `redirect()` from next/navigation

## Route Protection

Navigation assumes all routes are protected by middleware. Ensure the following in `middleware.ts`:

- All routes except `/sign-in` and `/sign-up` require authentication
- Public routes configured in Clerk middleware

## Future Enhancements

Potential improvements for future phases:

1. **Search bar** in navigation header
2. **Notifications** dropdown
3. **Theme toggle** (light/dark mode)
4. **Keyboard shortcuts** for navigation
5. **Recently viewed** calls section
6. **Team switcher** for managers
7. **Quick actions** menu
8. **Help/documentation** links

## Testing Checklist

- [ ] Desktop sidebar navigation works
- [ ] Mobile menu opens and closes
- [ ] Active states highlight correctly
- [ ] Breadcrumbs generate properly
- [ ] UserButton logs out correctly
- [ ] Loading states appear during navigation
- [ ] Error boundary catches errors
- [ ] 404 page appears for invalid routes
- [ ] Responsive at all breakpoints
- [ ] Navigation persists across route changes

## File Structure

```
frontend/
├── app/
│   ├── layout.tsx              # Root layout with navigation
│   ├── loading.tsx             # Global loading UI
│   ├── error.tsx               # Global error boundary
│   ├── not-found.tsx           # 404 page
│   ├── page.tsx                # Home (redirects to dashboard)
│   ├── dashboard/page.tsx      # Dashboard route
│   ├── search/page.tsx         # Search route
│   ├── feed/page.tsx           # Feed route
│   ├── calls/page.tsx          # Calls route
│   └── profile/page.tsx        # Profile route
├── components/
│   ├── navigation/
│   │   ├── sidebar.tsx         # Desktop sidebar
│   │   ├── mobile-nav.tsx      # Mobile navigation
│   │   ├── user-nav.tsx        # User profile dropdown
│   │   ├── breadcrumb.tsx      # Breadcrumb navigation
│   │   └── index.ts            # Export barrel
│   └── ui/
│       ├── button.tsx          # Button component
│       ├── card.tsx            # Card components
│       └── skeleton.tsx        # Skeleton loader
└── NAVIGATION.md               # This file
```
