# Site Colors Documentation

This document provides a comprehensive reference for all colors used across the Great Commission Benchmark website and platform.

## Overview

The Great Commission Benchmark uses a consistent color palette across three main areas:
1. **Marketing Website** (`website/`) - Public-facing marketing site
2. **Platform Application** (`gcb-platform/`) - Main application interface
3. **Design System** - Reference colors for wireframes and design documentation

---

## Marketing Website Colors

The marketing website uses a red-based color scheme derived from the brand logo.

### Primary Brand Colors

| Variable | Hex Code | RGB | Usage |
|----------|----------|-----|-------|
| `--ga-red` | `#a11824` | `rgb(161, 24, 36)` | Primary dark red from logo for strong brand presence |
| `--ga-dark-red` | `#7a1219` | `rgb(122, 18, 25)` | Even darker red for hover states and deep accents |
| `--ga-light-red` | `#e84545` | `rgb(232, 69, 69)` | Lighter red for hyperlinks, buttons, and secondary elements |
| `--ga-accent-red` | `#fee9e8` | `rgb(254, 233, 232)` | Very light red for backgrounds and subtle highlights |

### Neutral Colors

| Variable | Hex Code | RGB | Usage |
|----------|----------|-----|-------|
| `--ga-black` | `#232323` | `rgb(35, 35, 35)` | Deep black for high contrast text, header, and footer |
| `--ga-white` | `#ffffff` | `rgb(255, 255, 255)` | Clean white for background and refreshing space |
| `--ga-gray` | `#f5f5f7` | `rgb(245, 245, 247)` | Soft gray for panels, subtle backgrounds |
| `--ga-medium-gray` | `#999999` | `rgb(153, 153, 153)` | Medium neutral for secondary text or icons |

### Usage Examples

- **Hero Section**: Gradient background using `--ga-red` to `--ga-dark-red`
- **Primary Buttons**: White background with `--ga-red` text
- **Hover States**: `--ga-dark-red` for buttons, `--ga-light-red` for links
- **Accent Sections**: `--ga-accent-red` background for highlighted content areas
- **Text**: `--ga-black` for primary text, `--ga-medium-gray` for secondary text

---

## Platform Application Colors

The platform application uses a semantic color system with light and dark mode support.

### Light Mode Colors

#### Base Colors

| Variable | Hex Code | RGB | Usage |
|----------|----------|-----|-------|
| `--background` | `#fafafa` | `rgb(250, 250, 250)` | Main page background |
| `--foreground` | `#0f172a` | `rgb(15, 23, 42)` | Primary text color |

#### Primary Colors

| Variable | Hex Code | RGB | Usage |
|----------|----------|-----|-------|
| `--primary` | `#b91c1c` | `rgb(185, 28, 28)` | Primary brand color (red) |
| `--primary-foreground` | `#ffffff` | `rgb(255, 255, 255)` | Text on primary backgrounds |

#### Secondary Colors

| Variable | Hex Code | RGB | Usage |
|----------|----------|-----|-------|
| `--secondary` | `#f1f5f9` | `rgb(241, 245, 249)` | Secondary background |
| `--secondary-foreground` | `#0f172a` | `rgb(15, 23, 42)` | Text on secondary backgrounds |

#### Accent Colors

| Variable | Hex Code | RGB | Usage |
|----------|----------|-----|-------|
| `--accent` | `#fef2f2` | `rgb(254, 242, 242)` | Accent background (light red) |
| `--accent-foreground` | `#991b1b` | `rgb(153, 27, 27)` | Text on accent backgrounds |

#### Muted Colors

| Variable | Hex Code | RGB | Usage |
|----------|----------|-----|-------|
| `--muted` | `#f1f5f9` | `rgb(241, 245, 249)` | Muted background |
| `--muted-foreground` | `#64748b` | `rgb(100, 116, 139)` | Muted text color |

#### Semantic Colors

| Variable | Hex Code | RGB | Usage |
|----------|----------|-----|-------|
| `--destructive` | `#dc2626` | `rgb(220, 38, 38)` | Error/destructive actions |
| `--border` | `#e2e8f0` | `rgb(226, 232, 240)` | Border color |
| `--input` | `#e2e8f0` | `rgb(226, 232, 240)` | Input border color |
| `--ring` | `#b91c1c` | `rgb(185, 28, 28)` | Focus ring color |

#### Card Colors

| Variable | Hex Code | RGB | Usage |
|----------|----------|-----|-------|
| `--card` | `#ffffff` | `rgb(255, 255, 255)` | Card background |
| `--card-foreground` | `#0f172a` | `rgb(15, 23, 42)` | Card text color |
| `--popover` | `#ffffff` | `rgb(255, 255, 255)` | Popover background |
| `--popover-foreground` | `#0f172a` | `rgb(15, 23, 42)` | Popover text color |

#### Info Bar Colors

| Variable | Hex Code | RGB | Usage |
|----------|----------|-----|-------|
| `--info` | `#6b7280` | `rgb(107, 114, 128)` | Info bar background (light gray) |
| `--info-foreground` | `#ffffff` | `rgb(255, 255, 255)` | Info bar text |
| `--info-muted` | `#e5e7eb` | `rgb(229, 231, 235)` | Info bar muted background |
| `--info-border` | `#9ca3af` | `rgb(156, 163, 175)` | Info bar border |

#### Sidebar Colors

| Variable | Hex Code | RGB | Usage |
|----------|----------|-----|-------|
| `--sidebar` | `#ffffff` | `rgb(255, 255, 255)` | Sidebar background |
| `--sidebar-foreground` | `#0f172a` | `rgb(15, 23, 42)` | Sidebar text |
| `--sidebar-primary` | `#b91c1c` | `rgb(185, 28, 28)` | Sidebar primary accent |
| `--sidebar-primary-foreground` | `#ffffff` | `rgb(255, 255, 255)` | Text on sidebar primary |
| `--sidebar-accent` | `#fef2f2` | `rgb(254, 242, 242)` | Sidebar accent background |
| `--sidebar-accent-foreground` | `#991b1b` | `rgb(153, 27, 27)` | Text on sidebar accent |
| `--sidebar-border` | `#e2e8f0` | `rgb(226, 232, 240)` | Sidebar border |
| `--sidebar-ring` | `#b91c1c` | `rgb(185, 28, 28)` | Sidebar focus ring |

#### Chart Colors

| Variable | Hex Code | RGB | Usage |
|----------|----------|-----|-------|
| `--chart-1` | `#b91c1c` | `rgb(185, 28, 28)` | Primary chart color |
| `--chart-2` | `#ef4444` | `rgb(239, 68, 68)` | Secondary chart color |
| `--chart-3` | `#0f172a` | `rgb(15, 23, 42)` | Tertiary chart color |
| `--chart-4` | `#64748b` | `rgb(100, 116, 139)` | Quaternary chart color |
| `--chart-5` | `#94a3b8` | `rgb(148, 163, 184)` | Quinary chart color |

### Dark Mode Colors

#### Base Colors

| Variable | Hex Code | RGB | Usage |
|----------|----------|-----|-------|
| `--background` | `#0f172a` | `rgb(15, 23, 42)` | Main page background (dark) |
| `--foreground` | `#f8fafc` | `rgb(248, 250, 252)` | Primary text color (light) |

#### Primary Colors

| Variable | Hex Code | RGB | Usage |
|----------|----------|-----|-------|
| `--primary` | `#ef4444` | `rgb(239, 68, 68)` | Primary brand color (lighter red for dark mode) |
| `--primary-foreground` | `#ffffff` | `rgb(255, 255, 255)` | Text on primary backgrounds |

#### Secondary Colors

| Variable | Hex Code | RGB | Usage |
|----------|----------|-----|-------|
| `--secondary` | `#334155` | `rgb(51, 65, 85)` | Secondary background (dark) |
| `--secondary-foreground` | `#f8fafc` | `rgb(248, 250, 252)` | Text on secondary backgrounds |

#### Accent Colors

| Variable | Hex Code | RGB | Usage |
|----------|----------|-----|-------|
| `--accent` | `rgba(239, 68, 68, 0.1)` | `rgba(239, 68, 68, 0.1)` | Accent background (transparent red) |
| `--accent-foreground` | `#ef4444` | `rgb(239, 68, 68)` | Text on accent backgrounds |

#### Muted Colors

| Variable | Hex Code | RGB | Usage |
|----------|----------|-----|-------|
| `--muted` | `#334155` | `rgb(51, 65, 85)` | Muted background (dark) |
| `--muted-foreground` | `#94a3b8` | `rgb(148, 163, 184)` | Muted text color (light gray) |

#### Semantic Colors

| Variable | Hex Code | RGB | Usage |
|----------|----------|-----|-------|
| `--destructive` | `#ef4444` | `rgb(239, 68, 68)` | Error/destructive actions |
| `--border` | `rgba(255, 255, 255, 0.1)` | `rgba(255, 255, 255, 0.1)` | Border color (transparent white) |
| `--input` | `rgba(255, 255, 255, 0.1)` | `rgba(255, 255, 255, 0.1)` | Input border color |
| `--ring` | `#ef4444` | `rgb(239, 68, 68)` | Focus ring color |

#### Card Colors

| Variable | Hex Code | RGB | Usage |
|----------|----------|-----|-------|
| `--card` | `#1e293b` | `rgb(30, 41, 59)` | Card background (dark slate) |
| `--card-foreground` | `#f8fafc` | `rgb(248, 250, 252)` | Card text color |
| `--popover` | `#1e293b` | `rgb(30, 41, 59)` | Popover background |
| `--popover-foreground` | `#f8fafc` | `rgb(248, 250, 252)` | Popover text color |

#### Sidebar Colors

| Variable | Hex Code | RGB | Usage |
|----------|----------|-----|-------|
| `--sidebar` | `#1e293b` | `rgb(30, 41, 59)` | Sidebar background (dark) |
| `--sidebar-foreground` | `#f8fafc` | `rgb(248, 250, 252)` | Sidebar text |
| `--sidebar-primary` | `#ef4444` | `rgb(239, 68, 68)` | Sidebar primary accent |
| `--sidebar-primary-foreground` | `#ffffff` | `rgb(255, 255, 255)` | Text on sidebar primary |
| `--sidebar-accent` | `rgba(239, 68, 68, 0.1)` | `rgba(239, 68, 68, 0.1)` | Sidebar accent background |
| `--sidebar-accent-foreground` | `#ef4444` | `rgb(239, 68, 68)` | Text on sidebar accent |
| `--sidebar-border` | `rgba(255, 255, 255, 0.1)` | `rgba(255, 255, 255, 0.1)` | Sidebar border |
| `--sidebar-ring` | `#ef4444` | `rgb(239, 68, 68)` | Sidebar focus ring |

#### Chart Colors (Dark Mode)

| Variable | Hex Code | RGB | Usage |
|----------|----------|-----|-------|
| `--chart-1` | `#ef4444` | `rgb(239, 68, 68)` | Primary chart color |
| `--chart-2` | `#b91c1c` | `rgb(185, 28, 28)` | Secondary chart color |
| `--chart-3` | `#f8fafc` | `rgb(248, 250, 252)` | Tertiary chart color |
| `--chart-4` | `#94a3b8` | `rgb(148, 163, 184)` | Quaternary chart color |
| `--chart-5` | `#64748b` | `rgb(100, 116, 139)` | Quinary chart color |

---

## Design System Reference Colors

These colors are used in wireframes and design documentation as reference standards.

### Semantic Status Colors

| Color | Hex Code | RGB | Usage |
|-------|----------|-----|-------|
| Success | `#28a745` | `rgb(40, 167, 69)` | Green for pass/success states |
| Warning | `#ffc107` | `rgb(255, 193, 7)` | Yellow for pending/caution states |
| Error | `#dc3545` | `rgb(220, 53, 69)` | Red for fail/error states |
| Info | `#17a2b8` | `rgb(23, 162, 184)` | Blue for informational messages |

---

## Color Usage Guidelines

### Accessibility

- All text colors meet WCAG AA standards (4.5:1 minimum contrast ratio)
- Primary text (`--foreground`) on background (`--background`) maintains sufficient contrast
- Interactive elements have visible focus states using `--ring` color

### Color Relationships

1. **Primary Red**: Used for brand identity, primary actions, and key highlights
   - Light mode: `#b91c1c`
   - Dark mode: `#ef4444`

2. **Accent Red**: Used for subtle backgrounds and hover states
   - Light mode: `#fef2f2`
   - Dark mode: `rgba(239, 68, 68, 0.1)`

3. **Neutral Grays**: Used for borders, muted content, and secondary elements
   - Light mode: Various shades from `#f1f5f9` to `#64748b`
   - Dark mode: Various shades from `#334155` to `#94a3b8`

### Selection Colors

Text selection uses the accent color scheme:
- Background: `#fef2f2` (light red)
- Text: `#991b1b` (dark red)

---

## Implementation Notes

### CSS Variables

All colors are defined as CSS custom properties (variables) in:
- **Marketing Website**: `website/index.html` (inline styles)
- **Platform Application**: `gcb-platform/frontend/app/globals.css`

### Theme Switching

The platform supports automatic dark mode detection. Dark mode colors are defined in the `.dark` class selector in `globals.css`.

### Color Updates

When updating colors:
1. Update the CSS variable definitions in the appropriate file
2. Update this documentation
3. Test both light and dark modes (if applicable)
4. Verify accessibility contrast ratios

---

## Quick Reference

### Most Used Colors

**Marketing Website:**
- Primary: `#a11824` (--ga-red)
- Text: `#232323` (--ga-black)
- Background: `#ffffff` (--ga-white)

**Platform (Light Mode):**
- Primary: `#b91c1c` (--primary)
- Text: `#0f172a` (--foreground)
- Background: `#fafafa` (--background)

**Platform (Dark Mode):**
- Primary: `#ef4444` (--primary)
- Text: `#f8fafc` (--foreground)
- Background: `#0f172a` (--background)

---

*Last Updated: 2025*