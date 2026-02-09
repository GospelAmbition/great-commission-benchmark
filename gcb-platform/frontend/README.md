# Great Commission Benchmark - Frontend

Next.js 14 frontend for the Great Commission Benchmark platform.

## Overview

The frontend provides:
- Public leaderboard and model comparison
- User dashboard for submission management
- CLI submission review workflow
- Moderator review interface
- Admin management panels
- Responsive design for all devices

## Setup

### Prerequisites

- Node.js 18+
- npm or yarn

### Installation

1. **Install dependencies:**
   ```bash
   npm install
   ```

2. **Configure environment:**
   ```bash
   cp .env.example .env.local
   # Edit .env.local with your configuration
   ```

3. **Run development server:**
   ```bash
   npm run dev
   ```

   The app will be available at `http://localhost:3001`

## Project Structure

```
frontend/
├── app/                      # Next.js app directory
│   ├── api/                 # API routes
│   │   └── auth/           # NextAuth handlers
│   ├── about/              # About/methodology page
│   ├── admin/              # Admin pages
│   ├── api/                # API routes
│   │   ├── auth/          # NextAuth handlers
│   │   ├── admin/         # Admin API proxy
│   │   └── blog/          # Blog API proxy
│   ├── benchmark/         # Benchmark information
│   ├── blog-manager/      # Blog management interface
│   ├── categories/        # Category pages
│   ├── contact/           # Contact page
│   ├── contribute/        # Contribute page
│   ├── dashboard/         # User dashboard
│   ├── faq/               # FAQ page
│   ├── insights/          # Blog/insights pages
│   ├── leaderboard/       # Leaderboard and model pages
│   ├── moderator/         # Moderator interface
│   ├── newsletter/        # Newsletter page
│   ├── privacy/           # Privacy policy
│   ├── profile/           # Public profiles
│   ├── runner/            # Runner CLI information
│   ├── sponsor/           # Sponsorship page
│   ├── terms/             # Terms of service
│   ├── tester-agreement/  # Tester agreement
│   ├── layout.tsx          # Root layout
│   ├── page.tsx            # Homepage
│   ├── error.tsx           # Error boundary
│   ├── not-found.tsx       # 404 page
│   └── global-error.tsx    # Global error handler
├── components/
│   ├── analytics/          # Analytics components
│   ├── charts/             # Chart.js visualizations
│   ├── home/               # Homepage components
│   ├── layout/             # Header, Footer
│   ├── tester-agreement/   # Agreement modal
│   └── ui/                 # shadcn/ui components
├── lib/
│   └── api.ts              # API client
├── public/                  # Static assets
└── __tests__/              # Test files
```

## Key Pages

| Route | Description |
|-------|-------------|
| `/` | Homepage with top performers |
| `/about` | About page and methodology |
| `/leaderboard` | Full leaderboard with filters |
| `/leaderboard/models/[id]` | Model detail page |
| `/leaderboard/compare` | Model comparison |
| `/categories` | Category overview |
| `/categories/[id]` | Category detail page |
| `/dashboard` | User dashboard |
| `/dashboard/settings` | User settings |
| `/dashboard/submissions` | User's CLI submissions |
| `/dashboard/submissions/[id]` | Submission detail |
| `/dashboard/sponsorships/[id]` | Sponsorship request detail |
| `/moderator` | Moderator queue |
| `/moderator/community/[id]` | Community submission review |
| `/moderator/sponsorship/[id]` | Sponsorship request review |
| `/admin` | Admin dashboard |
| `/admin/users` | User management |
| `/admin/questions` | Question management |
| `/admin/payments` | Payment management |
| `/admin/volunteers` | Volunteer applications |
| `/admin/data` | Data management |
| `/blog-manager` | Blog post management |
| `/blog-manager/new` | Create new blog post |
| `/blog-manager/[id]` | Edit blog post |
| `/insights` | Blog/insights listing |
| `/insights/[slug]` | Blog post detail |
| `/contribute` | Contribute page |
| `/contribute/support` | Support page |
| `/sponsor` | Sponsorship page |
| `/newsletter` | Newsletter page |
| `/contact` | Contact page |
| `/faq` | FAQ page |
| `/runner` | Runner CLI information |
| `/profile/[id]` | Public user profile |
| `/terms` | Terms of service |
| `/privacy` | Privacy policy |
| `/tester-agreement` | Tester agreement |

## Components

### UI Components (shadcn/ui)

This project uses [shadcn/ui](https://ui.shadcn.com/) components:

```bash
# Add a new component
npx shadcn@latest add [component-name]

# Available components
npx shadcn@latest add button card table badge tabs dialog sheet form input select checkbox progress alert toast dropdown-menu navigation-menu avatar skeleton separator
```

### Chart Components

Located in `components/charts/`:
- `TopPerformersChart` - Horizontal bar chart
- `CategoryChart` - Category breakdown
- `RadarChart` - Model comparison radar
- `VerdictDistributionChart` - Stacked bar
- `VersionHistoryChart` - Line chart
- `CategoryHeatmap` - Performance heatmap

Charts use Chart.js with react-chartjs-2.

## Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `AUTH_URL` | Base URL of your app (e.g., `http://localhost:3001`) | Yes |
| `NEXTAUTH_SECRET` | Session encryption secret (generate with `openssl rand -base64 32`) | Yes |
| `GOOGLE_CLIENT_ID` | Google OAuth client ID | Yes |
| `GOOGLE_CLIENT_SECRET` | Google OAuth client secret | Yes |
| `NEXT_PUBLIC_API_URL` | Backend API URL | Yes |
| `NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY` | Stripe key (for payments and donations) | Production |
| `NEXT_PUBLIC_UMAMI_SCRIPT_URL` | Analytics URL | Optional |
| `NEXT_PUBLIC_UMAMI_WEBSITE_ID` | Analytics ID | Optional |

## Google OAuth Setup

1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Create a new project or select an existing one
3. Enable Google+ API
4. Create OAuth 2.0 credentials:
   - Go to **APIs & Services** → **Credentials**
   - Click **Create Credentials** → **OAuth client ID**
   - Application type: **Web application**
   - Authorized redirect URIs: `http://localhost:3001/api/auth/callback`
5. Copy the Client ID and Client Secret to `.env.local`
6. Generate `NEXTAUTH_SECRET`:
   ```bash
   openssl rand -base64 32
   ```

## Development

### Running Tests

```bash
npm test              # Run tests
npm run test:watch    # Watch mode
npm run test:coverage # With coverage
```

### Linting

```bash
npm run lint          # Check for issues
npm run lint:fix      # Auto-fix issues
```

### Type Checking

```bash
npm run type-check    # Run TypeScript compiler
```

## Building for Production

```bash
npm run build         # Create production build
npm start            # Start production server
```

## Accessibility

The frontend includes accessibility features:
- Skip to main content link
- Proper ARIA labels on navigation
- Keyboard navigation support
- Focus indicators
- Screen reader announcements
- Color contrast compliance

## Security

Security headers configured in `next.config.ts`:
- `X-Content-Type-Options`
- `X-Frame-Options`
- `X-XSS-Protection`
- `Referrer-Policy`
- `Permissions-Policy`
- `Strict-Transport-Security`

## Styling

### Tailwind CSS

Custom colors defined in `tailwind.config.js`:
```javascript
colors: {
  'ga-red': '#a11824',
  'ga-dark-red': '#7a1219',
  'ga-light-red': '#e84545',
  'ga-accent-red': '#fee9e8',
}
```

### CSS Variables

Global CSS variables in `app/globals.css`:
```css
:root {
  --ga-red: #a11824;
  --ga-dark-red: #7a1219;
  /* ... */
}
```

## API Client

The API client (`lib/api.ts`) handles:
- Request/response types
- Authentication token injection
- Error handling
- Backend endpoint mapping

Example usage:
```typescript
import { apiClient } from '@/lib/api';

// Public endpoints
const leaderboard = await apiClient.getLeaderboard({ limit: 10 });
const stats = await apiClient.getStats();

// Authenticated endpoints
const profile = await apiClient.getUserProfile();
const submissions = await apiClient.getUserSubmissions();
```

## Deployment

### Railway

The frontend auto-deploys from the `frontend/` directory.

Configuration in `railway.json`:
```json
{
  "build": {
    "builder": "RAILPACK"
  },
  "deploy": {
    "startCommand": "npm start"
  }
}
```

### Vercel

Alternatively, deploy to Vercel:
```bash
npx vercel
```

## Troubleshooting

### Authentication Errors

- Verify `AUTH_URL` matches your domain exactly
- Check Google OAuth callback URLs match
- Ensure `NEXTAUTH_SECRET` is set correctly
- Verify Google OAuth credentials are correct

### API Connection Issues

- Verify `NEXT_PUBLIC_API_URL` is correct
- Check CORS settings on backend
- Ensure backend is running

### Build Errors

- Clear `.next` directory: `rm -rf .next`
- Clear node_modules: `rm -rf node_modules && npm install`
- Check for TypeScript errors: `npm run type-check`

---

For more information, see the [main README](../README.md).
