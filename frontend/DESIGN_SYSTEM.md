# Prefect Design System for Call Coaching

This design system provides a comprehensive set of UI components and design tokens for the Gong Call Coaching frontend, built on Prefect brand guidelines.

## Setup

### Installation

After cloning the repository, install dependencies:

```bash
npm install
```

This will install:
- Tailwind CSS v3.4+
- Shadcn/ui components
- Radix UI primitives
- Class Variance Authority (CVA)
- Tailwind Merge

### Development

To see the design system in action:

```bash
npm run dev
```

Then navigate to `http://localhost:3000/design-system` to view all components.

## Brand Colors

### Primary Colors

- **Prefect Pink** (`#FF4BBD`) - Primary brand color, used for CTAs and highlights
- **Sunrise 1** (`#FE9655`) - Orange accent, used for warnings and secondary CTAs
- **Sunrise 2** (`#FEB255`) - Yellow accent, used for success states

### Extended Palette

- **Blue Scale** - `prefect-blue-50` through `prefect-blue-900`
- **Purple Scale** - `prefect-purple-50` through `prefect-purple-900`
- **Gray Scale** - `prefect-gray-50` through `prefect-gray-900`

### Semantic Colors

The design system uses Shadcn/ui's semantic color system with CSS variables:

- `--background` / `--foreground` - Base colors
- `--primary` / `--primary-foreground` - Primary actions (mapped to Prefect Pink)
- `--secondary` / `--secondary-foreground` - Secondary actions (mapped to Prefect Blue)
- `--accent` / `--accent-foreground` - Accents (mapped to Sunrise Orange)
- `--muted` / `--muted-foreground` - Muted backgrounds and text
- `--destructive` / `--destructive-foreground` - Error states
- `--border` / `--input` / `--ring` - Form elements

## Typography

### Font Families

- **Sans-serif**: Inter (fallback: system-ui, sans-serif)
- **Monospace**: JetBrains Mono (fallback: monospace)

Add font imports to your layout:

```tsx
import { Inter } from 'next/font/google';

const inter = Inter({ subsets: ['latin'] });
```

### Type Scale

- `text-xs` - 0.75rem (12px)
- `text-sm` - 0.875rem (14px)
- `text-base` - 1rem (16px)
- `text-lg` - 1.125rem (18px)
- `text-xl` - 1.25rem (20px)
- `text-2xl` - 1.5rem (24px)
- `text-3xl` - 1.875rem (30px)
- `text-4xl` - 2.25rem (36px)
- And larger sizes up to `text-9xl`

### Font Weights

- `font-normal` - 400
- `font-medium` - 500
- `font-semibold` - 600
- `font-bold` - 700

## Spacing

Tailwind's default spacing scale is extended with:

- `128` - 32rem (512px)
- `144` - 36rem (576px)

Use standard Tailwind spacing utilities: `p-4`, `m-8`, `gap-6`, etc.

## Responsive Breakpoints

- `xs`: 475px
- `sm`: 640px
- `md`: 768px
- `lg`: 1024px
- `xl`: 1280px
- `2xl`: 1536px

Example usage:

```tsx
<div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3">
  {/* Responsive grid */}
</div>
```

## Components

### Button

Multiple variants available:

```tsx
import { Button } from "@/components/ui/button";

<Button variant="default">Default</Button>
<Button variant="prefect">Prefect</Button>
<Button variant="sunrise">Sunrise</Button>
<Button variant="gradient">Gradient</Button>
<Button variant="outline">Outline</Button>
<Button variant="ghost">Ghost</Button>

// Sizes
<Button size="sm">Small</Button>
<Button size="default">Default</Button>
<Button size="lg">Large</Button>
<Button size="icon">+</Button>
```

### Card

Composable card components:

```tsx
import {
  Card,
  CardHeader,
  CardTitle,
  CardDescription,
  CardContent,
  CardFooter,
} from "@/components/ui/card";

<Card>
  <CardHeader>
    <CardTitle>Title</CardTitle>
    <CardDescription>Description</CardDescription>
  </CardHeader>
  <CardContent>
    Content goes here
  </CardContent>
  <CardFooter>
    <Button>Action</Button>
  </CardFooter>
</Card>
```

### Input

Standard text input:

```tsx
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";

<div className="space-y-2">
  <Label htmlFor="email">Email</Label>
  <Input id="email" type="email" placeholder="you@example.com" />
</div>
```

### Select

Dropdown select component:

```tsx
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";

<Select>
  <SelectTrigger>
    <SelectValue placeholder="Select option" />
  </SelectTrigger>
  <SelectContent>
    <SelectItem value="1">Option 1</SelectItem>
    <SelectItem value="2">Option 2</SelectItem>
  </SelectContent>
</Select>
```

### Badge

Status and label badges:

```tsx
import { Badge } from "@/components/ui/badge";

<Badge variant="default">Default</Badge>
<Badge variant="success">Success</Badge>
<Badge variant="warning">Warning</Badge>
<Badge variant="info">Info</Badge>
<Badge variant="prefect">Prefect</Badge>
```

## Custom Variants

The design system includes Prefect-specific variants:

### Button Variants
- `prefect` - Solid pink background
- `sunrise` - Solid orange background
- `gradient` - Pink to orange gradient

### Badge Variants
- `prefect` - Pink badge
- `sunrise` - Orange badge
- `success` - Green badge
- `warning` - Yellow badge
- `info` - Blue badge

## Utilities

### cn() Function

Merge Tailwind classes with proper precedence:

```tsx
import { cn } from "@/lib/utils";

<div className={cn("base-class", conditionalClass && "conditional-class")} />
```

## Dark Mode

The design system includes full dark mode support via CSS variables. Dark mode is automatically detected via the `prefers-color-scheme` media query.

To manually toggle dark mode, add the `dark` class to your root element:

```tsx
<html className="dark">
```

## Logo Assets

Official Prefect logos should be placed in `/public/logos/`:

- `prefect-logo.svg` - Primary logo
- `prefect-logo-white.svg` - White version for dark backgrounds
- `prefect-wordmark.svg` - Wordmark only
- `prefect-icon.svg` - Icon only

Download from: https://prefect.io/newsroom/logos

### Usage

```tsx
import Image from "next/image";

<Image
  src="/logos/prefect-logo.svg"
  alt="Prefect"
  width={120}
  height={32}
  priority
/>
```

## Best Practices

1. **Use semantic colors** - Prefer `bg-primary` over `bg-prefect-pink` for consistency
2. **Responsive first** - Design mobile-first, then add larger breakpoints
3. **Component composition** - Build complex UIs from small, reusable components
4. **Accessibility** - All components include proper ARIA attributes
5. **Type safety** - Leverage TypeScript for component props

## Adding New Components

To add new Shadcn/ui components:

```bash
npx shadcn-ui@latest add [component-name]
```

This will automatically:
- Install required dependencies
- Add the component to `components/ui/`
- Configure with your theme

## Resources

- [Shadcn/ui Documentation](https://ui.shadcn.com/)
- [Tailwind CSS Documentation](https://tailwindcss.com/docs)
- [Radix UI Documentation](https://www.radix-ui.com/)
- [Prefect Brand Assets](https://prefect.io/newsroom/logos)
