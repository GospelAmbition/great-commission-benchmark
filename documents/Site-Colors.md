# Site Colors Documentation

This document provides a comprehensive reference for all colors used across the Great Commission Benchmark website and platform.

## Overview

The Great Commission Benchmark uses a **dark-first design system** inspired by modern leaderboard sites like Vellum and Scale. The color palette prioritizes:

1. **Dark backgrounds** with subtle depth layers
2. **Red accent color** for brand identity and CTAs
3. **High contrast** for readability
4. **Semantic status colors** (green/amber/red) for scores and verdicts

---

## Platform Application Colors (Dark Theme - Default)

### Base Colors

| Variable | Hex Code | RGB | Usage |
|----------|----------|-----|-------|
| `--background` | `#09090b` | `rgb(9, 9, 11)` | Main page background (near-black) |
| `--foreground` | `#fafafa` | `rgb(250, 250, 250)` | Primary text color (off-white) |
| `--surface` | `#0c0c0f` | `rgb(12, 12, 15)` | Surface layer for sections |
| `--surface-elevated` | `#18181b` | `rgb(24, 24, 27)` | Elevated surfaces |

### Card and Popover Colors

| Variable | Hex Code | RGB | Usage |
|----------|----------|-----|-------|
| `--card` | `#111113` | `rgb(17, 17, 19)` | Card background |
| `--card-foreground` | `#fafafa` | `rgb(250, 250, 250)` | Card text color |
| `--popover` | `#18181b` | `rgb(24, 24, 27)` | Popover/dropdown background |
| `--popover-foreground` | `#fafafa` | `rgb(250, 250, 250)` | Popover text color |

### Primary Colors (Red Accent)

| Variable | Hex Code | RGB | Usage |
|----------|----------|-----|-------|
| `--primary` | `#dc2626` | `rgb(220, 38, 38)` | Primary brand color (bright red) |
| `--primary-foreground` | `#ffffff` | `rgb(255, 255, 255)` | Text on primary backgrounds |
| `--glow-primary` | `rgba(220, 38, 38, 0.4)` | — | Red glow effect for CTAs |

### Secondary Colors

| Variable | Hex Code | RGB | Usage |
|----------|----------|-----|-------|
| `--secondary` | `#27272a` | `rgb(39, 39, 42)` | Secondary background |
| `--secondary-foreground` | `#fafafa` | `rgb(250, 250, 250)` | Text on secondary backgrounds |

### Muted Colors

| Variable | Hex Code | RGB | Usage |
|----------|----------|-----|-------|
| `--muted` | `#18181b` | `rgb(24, 24, 27)` | Muted background |
| `--muted-foreground` | `rgba(255, 255, 255, 0.9)` | — | Secondary text color (90% white) |

### Accent Colors

| Variable | Hex Code | RGB | Usage |
|----------|----------|-----|-------|
| `--accent` | `rgba(220, 38, 38, 0.15)` | — | Accent background (transparent red) |
| `--accent-foreground` | `#ef4444` | `rgb(239, 68, 68)` | Text on accent backgrounds |

### Borders and Inputs

| Variable | Hex Code | RGB | Usage |
|----------|----------|-----|-------|
| `--border` | `rgba(255, 255, 255, 0.08)` | — | Border color (8% white) |
| `--input` | `rgba(255, 255, 255, 0.08)` | — | Input border color |
| `--ring` | `#dc2626` | `rgb(220, 38, 38)` | Focus ring color |

### Chart Colors

| Variable | Hex Code | RGB | Usage |
|----------|----------|-----|-------|
| `--chart-1` | `#ef4444` | `rgb(239, 68, 68)` | Red - primary chart color |
| `--chart-2` | `#f97316` | `rgb(249, 115, 22)` | Orange |
| `--chart-3` | `#22c55e` | `rgb(34, 197, 94)` | Green |
| `--chart-4` | `#3b82f6` | `rgb(59, 130, 246)` | Blue |
| `--chart-5` | `#a855f7` | `rgb(168, 85, 247)` | Purple |

### Sidebar Colors

| Variable | Hex Code | RGB | Usage |
|----------|----------|-----|-------|
| `--sidebar` | `#0c0c0f` | `rgb(12, 12, 15)` | Sidebar background |
| `--sidebar-foreground` | `#fafafa` | `rgb(250, 250, 250)` | Sidebar text |
| `--sidebar-primary` | `#dc2626` | `rgb(220, 38, 38)` | Sidebar primary accent |
| `--sidebar-accent` | `rgba(220, 38, 38, 0.15)` | — | Sidebar accent background |
| `--sidebar-border` | `rgba(255, 255, 255, 0.08)` | — | Sidebar border |

---

## Semantic Status Colors

Used for score verdicts, badges, and status indicators:

### Verdict Colors

| Status | Background | Text | Usage |
|--------|------------|------|-------|
| Aligned (≥75) | `bg-emerald-500/20` | `text-emerald-400` | Excellent GCB scores |
| Caution (50-74) | `bg-amber-500/20` | `text-amber-400` | Moderate scores |
| Compromised (<50) | `bg-red-500/20` | `text-red-400` | Poor scores |

### Tier Colors

| Tier | Background | Text | Usage |
|------|------------|------|-------|
| Tier 1 (Task) | `bg-red-500/10` | `text-red-400` | 70% weight |
| Tier 2 (Doctrine) | `bg-amber-500/10` | `text-amber-400` | 20% weight |
| Tier 3 (Worldview) | `bg-blue-500/10` | `text-blue-400` | 10% weight |

---

## Light Mode Colors (Optional Override)

The `.light` class can be applied for light mode support:

| Variable | Light Value | Usage |
|----------|-------------|-------|
| `--background` | `#fafafa` | Light page background |
| `--foreground` | `#09090b` | Dark text |
| `--card` | `#ffffff` | White cards |
| `--border` | `#e4e4e7` | Visible borders |

---

## Utility Classes

### Gradient Utilities

```css
.gradient-hero       /* Dark gradient for hero sections */
.gradient-red-glow   /* Radial red glow effect */
.glass               /* Frosted glass effect with backdrop blur */
.border-glow         /* Hover glow effect on borders */
```

### Animation Utilities

```css
.animate-fade-in-up  /* Fade in with upward motion */
.animate-fade-in     /* Simple fade in */
.animate-glow        /* Pulsing glow effect */
.animate-shimmer     /* Loading shimmer effect */
.animate-pulse-glow  /* Subtle pulse opacity */
```

### Animation Delays

```css
.animate-delay-100   /* 100ms delay */
.animate-delay-200   /* 200ms delay */
.animate-delay-300   /* 300ms delay */
.animate-delay-400   /* 400ms delay */
.animate-delay-500   /* 500ms delay */
```

---

## Design Principles

### 1. Dark-First Design
The site defaults to dark mode for a modern, professional appearance that makes data visualizations pop.

### 2. Subtle Depth
Instead of heavy shadows, use:
- Semi-transparent borders (`border-white/[0.08]`)
- Subtle background variations
- Backdrop blur for elevated elements

### 3. Red as Accent
The brand red (`#dc2626`) is used sparingly for:
- Primary CTAs and buttons
- Active states
- Important highlights
- Logo and brand elements

### 4. Semantic Colors
Green, amber, and red consistently represent good, caution, and poor states respectively.

---

## Implementation Notes

### CSS Variables Location
All colors are defined in:
- `gcb-platform/frontend/app/globals.css`

### Theme Switching
The platform uses dark mode by default. Light mode is available via the `.light` class.

### Accessibility
- All text colors maintain WCAG AA contrast ratios
- Focus states use visible ring colors
- Interactive elements have clear hover/active states

---

*Last Updated: January 2026*
