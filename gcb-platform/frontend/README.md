# Great Commission Benchmark - Frontend

Next.js frontend for the Great Commission Benchmark platform.

## Setup

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

## Environment Variables

See `.env.example` for required environment variables.

### Auth0 Setup

1. Create an Auth0 tenant at https://auth0.com
2. Create a "Regular Web Application"
3. Configure:
   - Allowed Callback URLs: `http://localhost:3000/api/auth/callback`
   - Allowed Logout URLs: `http://localhost:3000`
   - Allowed Web Origins: `http://localhost:3000`
4. Copy the Client ID and Client Secret to `.env.local`
5. Set `AUTH0_ISSUER_BASE_URL` to your tenant URL (e.g., `https://your-tenant.auth0.com`)

## Project Structure

```
frontend/
├── app/                  # Next.js app directory
│   ├── api/             # API routes (Auth0 handlers)
│   ├── layout.tsx       # Root layout
│   └── page.tsx        # Homepage
├── components/          # React components
│   └── ui/             # shadcn/ui components
├── lib/                 # Utility functions
└── public/             # Static assets
```

## Components

This project uses [shadcn/ui](https://ui.shadcn.com/) for UI components.

To add a new component:
```bash
npx shadcn@latest add [component-name]
```

## Testing

Run tests:
```bash
npm test
```

## Building for Production

```bash
npm run build
npm start
```
