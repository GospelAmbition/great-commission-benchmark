# Great Commission Benchmark - Frontend

Next.js 14 frontend for the Great Commission Benchmark platform.

## Overview

The frontend provides:
- Public leaderboard and model comparison
- User dashboard for test management
- Test execution flow with payment integration
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

   The app will be available at `http://localhost:3000`

## Project Structure

```
frontend/
├── app/                      # Next.js app directory
│   ├── api/                 # API routes (Auth0)
│   │   └── auth/           # Auth0 handlers
│   ├── about/              # About/methodology page
│   ├── admin/              # Admin pages
│   ├── contribute/         # Contribute page
│   ├── dashboard/          # User dashboard
│   ├── moderator/          # Moderator interface
│   ├── privacy/            # Privacy policy
│   ├── profile/            # Public profiles
│   ├── research/           # Leaderboard and model pages
│   ├── terms/              # Terms of service
│   ├── tester-agreement/   # Tester agreement
│   ├── tests/              # Test flow pages
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
| `/research` | Full leaderboard with filters |
| `/research/models/[id]` | Model detail page |
| `/research/compare` | Model comparison |
| `/tests/new` | Start new test |
| `/tests/[id]/payment` | Payment step |
| `/tests/[id]/processing` | Test progress |
| `/tests/[id]/results` | Test results |
| `/dashboard` | User dashboard |
| `/moderator` | Moderator queue |
| `/admin` | Admin dashboard |

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
| `AUTH0_SECRET` | Session encryption (generate with `openssl rand -hex 32`) | Yes |
| `AUTH0_BASE_URL` | Base URL (e.g., `http://localhost:3000`) | Yes |
| `AUTH0_ISSUER_BASE_URL` | Auth0 tenant URL | Yes |
| `AUTH0_CLIENT_ID` | Auth0 client ID | Yes |
| `AUTH0_CLIENT_SECRET` | Auth0 client secret | Yes |
| `NEXT_PUBLIC_API_URL` | Backend API URL | Yes |
| `NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY` | Stripe key | Production |
| `NEXT_PUBLIC_UMAMI_SCRIPT_URL` | Analytics URL | Optional |
| `NEXT_PUBLIC_UMAMI_WEBSITE_ID` | Analytics ID | Optional |

## Auth0 Setup

1. Create an Auth0 tenant at https://auth0.com
2. Create a "Regular Web Application"
3. Configure:
   - **Allowed Callback URLs**: `http://localhost:3000/api/auth/callback`
   - **Allowed Logout URLs**: `http://localhost:3000`
   - **Allowed Web Origins**: `http://localhost:3000`
4. Copy credentials to `.env.local`

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
const profile = await apiClient.getProfile();
const tests = await apiClient.getUserTests();
```

## Deployment

### Railway

The frontend auto-deploys from the `frontend/` directory.

Configuration in `railway.json`:
```json
{
  "build": {
    "builder": "NIXPACKS"
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

### Auth0 Callback Errors

- Verify callback URLs match exactly
- Check `AUTH0_BASE_URL` matches your domain
- Ensure secrets are set correctly

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
