# Authentication Quick Start

**5-minute setup guide for Clerk authentication**

## 1. Install Dependencies

```bash
cd frontend
npm install
```

## 2. Get Clerk Keys

1. Go to https://dashboard.clerk.com/sign-up
2. Create account and new application
3. Copy your API keys

## 3. Configure Environment

```bash
cd frontend
cp .env.example .env.local
```

Edit `.env.local` and add your keys:
```env
NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=pk_test_YOUR_KEY
CLERK_SECRET_KEY=sk_test_YOUR_KEY
```

## 4. Start Development Server

```bash
npm run dev
```

Visit http://localhost:3000

## 5. Create Test Users

1. Sign up at http://localhost:3000/sign-up
2. Go to Clerk Dashboard → Users
3. Click on user → Metadata tab
4. Add to Public metadata:

**For Manager:**
```json
{"role": "manager"}
```

**For Rep:**
```json
{"role": "rep"}
```

## Done!

You now have:
- ✅ Working sign-in/sign-up
- ✅ Protected routes
- ✅ Role-based access control

## Using RBAC in Code

```typescript
import { isManager, canViewRepData } from "@/lib/auth";

// Check if user is manager
const hasManagerAccess = await isManager();

// Check if user can view specific rep's data
const canView = await canViewRepData("rep@example.com");
```

## Next Steps

- See [CLERK_SETUP.md](./CLERK_SETUP.md) for detailed documentation
- See [AUTH_IMPLEMENTATION_SUMMARY.md](./AUTH_IMPLEMENTATION_SUMMARY.md) for complete implementation details
- See [README.md](./README.md) for project structure and development guide

## Troubleshooting

**Problem**: "Clerk: Missing publishableKey"
**Solution**: Check `.env.local` exists and has correct keys, restart dev server

**Problem**: Can't access protected routes
**Solution**: Sign in at `/sign-in`

**Problem**: Role not working
**Solution**: Set `publicMetadata.role` in Clerk Dashboard

For more help, see [CLERK_SETUP.md#troubleshooting](./CLERK_SETUP.md#troubleshooting)
