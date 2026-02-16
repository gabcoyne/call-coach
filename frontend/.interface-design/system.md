# Call Coach Design System

## Intent

**Who:** Sales managers and reps at Prefect. Managers review team performance mid-morning with coffee, looking for coaching opportunities. Reps check their own progress, often after calls, wanting to improve.

**What they do:** Find coaching moments, track skill progression, identify patterns in call performance, celebrate growth.

**Feel:** Like a supportive mentor reviewing film with an athlete. Focused, constructive, growth-oriented. Never surveillance. Scores are feedback, not judgment.

---

## Direction

Coaching-focused interface that emphasizes growth and progress over raw metrics. Data serves development, not monitoring.

**Signature:** Progress-oriented score presentation. Scores show trajectory, not just current state. The journey matters.

---

## Colors

### Brand Foundation

- **Primary:** Prefect Blue `#0052FF` (hsl 220 100% 50%) — confidence, trust, technical credibility
- **Accent:** Prefect Pink `#FF4BBD` (hsl 322 100% 65%) — highlights, action items, attention
- **Growth:** Sunrise Orange `#FE9655` / Yellow `#FEB255` — achievement, progress, warmth

### Semantic

- **Success:** Green for improvement, goals met
- **Warning:** Orange for attention needed, declining trends
- **Destructive:** Red for critical issues only (not for low scores — low scores are opportunities, not failures)

### Surfaces

Light mode: Near-white background (99% lightness), white cards
Dark mode: Deep navy (#090422 base), subtle purple undertones

---

## Depth Strategy

**Borders-only.** Clean, technical, professional.

- Standard borders: `rgba(border, 0.5)` — whisper-quiet separation
- Emphasis borders: `rgba(border, 0.8)` — section divisions
- Focus rings: Prefect Blue with 2px offset

No drop shadows on cards. Elevation through subtle background shifts only.

**Why:** Coaching data is dense. Shadows add visual noise. Borders provide structure without weight.

---

## Spacing

**Base unit:** 4px

- `space-1`: 4px — micro gaps (icon to text)
- `space-2`: 8px — tight component spacing
- `space-3`: 12px — within components
- `space-4`: 16px — between related elements
- `space-6`: 24px — section padding
- `space-8`: 32px — major sections

**Card padding:** 24px (space-6)
**Section gaps:** 32px (space-8)

---

## Typography

**Font:** Inter — approachable but professional, excellent for data

### Hierarchy

- **Page title:** 30px/2.25rem, font-bold, tight tracking (-0.02em)
- **Section title:** 24px/1.5rem, font-semibold
- **Card title:** 18px/1.125rem, font-semibold
- **Body:** 14px/0.875rem, font-normal
- **Label:** 12px/0.75rem, font-medium, uppercase tracking (0.05em)
- **Data/Numbers:** JetBrains Mono, tabular nums

### Text Colors

- Primary: foreground (near-black in light, near-white in dark)
- Secondary: muted-foreground (for supporting text)
- Tertiary: muted-foreground at 70% opacity (metadata)
- Muted: muted-foreground at 50% (disabled, placeholder)

---

## Border Radius

**Base:** 10px (0.625rem)

- Buttons, inputs: 8px (base - 2px)
- Cards: 10px (base)
- Modals, large surfaces: 14px (base + 4px)
- Pills, badges: full rounded

**Why:** Slightly rounded feels approachable without being childish. Coaching tools should feel human.

---

## Components

### Score Display

Scores are coaching feedback, not grades. Present them as:

- Progress rings for overall scores (shows fullness, not emptiness)
- Trend indicators alongside raw numbers (↑ ↓ →)
- Color based on trajectory, not just current value:
  - Improving: Success green tint
  - Stable: Neutral
  - Declining: Warning orange (not red — opportunity, not failure)

### Cards

- White/card background
- 1px border, subtle
- 24px padding
- No shadow
- Optional header with border-bottom separator

### Tables

- Header: Muted background, medium weight text
- Rows: Hover state with subtle background shift
- Borders: Only horizontal, very subtle
- Clickable rows: Cursor pointer, hover reveals action

### Navigation (Sidebar)

- Same background as main content (not different color)
- Separated by 1px border
- Active state: Primary background, white text
- Hover: Accent background at low opacity

---

## States

### Interactive Elements

- **Default:** Standard appearance
- **Hover:** Subtle background shift or border emphasis
- **Active/Pressed:** Slightly darker
- **Focus:** Blue ring, 2px offset
- **Disabled:** 50% opacity, no interaction

### Data States

- **Loading:** Skeleton with subtle shimmer
- **Empty:** Helpful message, not just blank
- **Error:** Red border, clear message, retry action

---

## Animation

- **Duration:** 150ms for micro-interactions, 200ms for transitions
- **Easing:** ease-out for entering, ease-in for exiting
- **No bounce or spring** — this is professional software

---

## Patterns to Avoid

- Heavy drop shadows
- Bright colors for low scores (low = opportunity, not failure)
- Dense data tables without hierarchy
- Score badges that feel like report cards
- Different background colors for sidebar vs content
- Multiple accent colors competing for attention

---

## UI Update Specifications

### When Updating Components

Before modifying any UI component, verify:

1. **Intent alignment** — Does this change support coaching (growth-focused) or does it drift toward surveillance (judgment-focused)?
2. **Color usage** — Is color motivated? Blue for trust/action, orange/yellow for growth, pink for highlights only
3. **Spacing** — All values must be multiples of 4px
4. **Depth** — Borders only, no shadows on cards

### Score Components

**ScoreBadge / ScoreCard updates:**

```
- Score 0-49: muted gray background, "needs attention" not "failing"
- Score 50-69: subtle yellow/amber tint, "developing"
- Score 70-84: subtle blue tint, "proficient"
- Score 85-100: subtle green tint, "strong"
- Always show trend indicator when data available (↑ ↓ →)
- Never use red for scores — red is for errors only
```

**Progress indicators:**

```
- Use circular progress for overall scores (shows fullness)
- Use horizontal bars for dimension breakdowns
- Include benchmark/target lines where relevant
- Animate on load: 300ms ease-out
```

### Card Updates

**Standard card structure:**

```tsx
<Card className="border border-border bg-card">
  <CardHeader className="border-b border-border/50 pb-4">
    <CardTitle className="text-lg font-semibold">{title}</CardTitle>
    <CardDescription className="text-sm text-muted-foreground">{description}</CardDescription>
  </CardHeader>
  <CardContent className="pt-6">{content}</CardContent>
</Card>
```

**Metric cards (dashboard):**

```
- Icon: 20x20px, muted-foreground color, left-aligned
- Value: text-3xl font-bold, primary foreground
- Label: text-sm text-muted-foreground
- Trend: inline with value, colored by direction
- Padding: 24px all sides
```

### Table Updates

**Data tables:**

```
- Header: bg-muted/50, text-sm font-medium, py-3 px-4
- Rows: hover:bg-muted/30 transition-colors
- Borders: border-b border-border/50 (horizontal only)
- Clickable rows: cursor-pointer, group for hover effects
- Actions column: right-aligned, ghost buttons
```

**Score columns in tables:**

```
- Center-aligned
- Use ScoreBadge component (pill style)
- Include micro trend indicator when available
```

### Form Updates

**Input fields:**

```
- Height: 40px (h-10)
- Border: border-input (use CSS var)
- Focus: ring-2 ring-ring ring-offset-2
- Placeholder: text-muted-foreground
- Error: border-destructive, no red background
```

**Select dropdowns:**

```
- Match input styling
- Custom trigger (not native select)
- Dropdown: bg-popover, border, rounded-md
- Options: hover:bg-accent, py-2 px-3
```

### Navigation Updates

**Sidebar:**

```
- Width: 256px (w-64)
- Background: bg-card (same as content area)
- Border: border-r border-border
- Logo area: py-5 px-6, border-b
- Nav items: px-3 py-2, rounded-md
- Active: bg-primary text-primary-foreground
- Hover: bg-accent/50
- Section dividers: border-t border-border my-4
```

**Breadcrumbs:**

```
- Separator: / or chevron, text-muted-foreground
- Current page: font-medium, no link
- Previous pages: text-muted-foreground hover:text-foreground
```

### Chart Updates

**All charts (Recharts):**

```
- Use CSS variables for colors: hsl(var(--chart-1)) etc.
- Grid lines: stroke-muted, strokeDasharray="3 3"
- Axis labels: text-xs text-muted-foreground
- Tooltips: bg-popover border rounded-lg shadow-sm p-3
- Legend: below chart, horizontal, text-sm
```

**Score trend charts:**

```
- Primary line: chart-1 (Prefect blue)
- Target/benchmark: dashed, muted-foreground
- Area fill: primary at 10% opacity
- Animate on load: 500ms
```

### Loading States

**Skeletons:**

```
- Background: bg-muted animate-pulse
- Border radius: match component being loaded
- Height: match expected content height
- Duration: 1.5s pulse cycle
```

**Spinners:**

```
- Use only for actions (not page loads)
- Size: 16px for buttons, 24px standalone
- Color: currentColor (inherits)
```

### Empty States

**Structure:**

```tsx
<div className="flex flex-col items-center justify-center py-12 text-center">
  <Icon className="h-12 w-12 text-muted-foreground/50 mb-4" />
  <h3 className="text-lg font-medium mb-2">{title}</h3>
  <p className="text-sm text-muted-foreground max-w-sm mb-4">{description}</p>
  <Button variant="outline">{action}</Button>
</div>
```

**Tone:** Helpful, not apologetic. "No calls analyzed yet" not "Sorry, no data"

### Responsive Breakpoints

```
xs: 475px   — mobile landscape
sm: 640px   — tablet portrait
md: 768px   — tablet landscape
lg: 1024px  — desktop
xl: 1280px  — large desktop
2xl: 1536px — wide screens
```

**Mobile adaptations:**

- Sidebar: hidden, replaced by bottom nav or hamburger
- Cards: full width, stack vertically
- Tables: horizontal scroll or card view
- Charts: simplified, fewer data points

### Accessibility

**Required on all interactive elements:**

- Visible focus states (ring)
- ARIA labels on icon-only buttons
- Sufficient color contrast (4.5:1 minimum)
- Keyboard navigation support

**Score colors must not be sole indicator:**

- Always include text label or icon alongside color
- Trend arrows provide redundant information to color
