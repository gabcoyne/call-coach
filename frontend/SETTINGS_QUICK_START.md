# Settings Pages - Quick Start Guide

## Overview

User settings pages allow users to manage their profile, notifications, preferences, and data.

## Access Points

- **Main Sidebar:** Settings item (gear icon)
- **Direct URLs:**
  - `/settings` → redirects to profile
  - `/settings/profile` → user profile
  - `/settings/notifications` → notification preferences
  - `/settings/preferences` → user preferences (theme, layout, etc.)
  - `/settings/data` → data export and privacy

## Architecture

### Pages

```
/frontend/app/settings/
├── layout.tsx              # Settings layout with sidebar
├── page.tsx               # Redirect to profile
├── profile/
│   └── page.tsx          # Profile management
├── notifications/
│   └── page.tsx          # Notification preferences
├── preferences/
│   └── page.tsx          # User preferences
└── data/
    └── page.tsx          # Data export & privacy
```

### Components

```
/frontend/components/settings/
└── settings-nav.tsx       # Settings navigation sidebar
```

### APIs

```
/frontend/app/api/user/
├── preferences/route.ts   # GET/PUT user preferences
├── avatar/route.ts        # POST avatar upload
└── data/
    └── export/route.ts    # POST data export
```

## Using the APIs

### Get User Preferences

```typescript
const response = await fetch("/api/user/preferences");
const preferences = await response.json();
```

### Update User Preferences

```typescript
const response = await fetch("/api/user/preferences", {
  method: "PUT",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({
    theme: "dark",
    notificationFrequency: "daily",
    defaultCoachingDimensions: ["opening", "discovery"],
  }),
});
```

### Export Data

```typescript
const response = await fetch("/api/user/data/export", {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({
    format: "csv",
    includeTranscripts: true,
    includeCoachingFeedback: true,
    includeCallRecordings: false,
  }),
});
const blob = await response.blob();
// Create download link...
```

### Upload Avatar

```typescript
const formData = new FormData();
formData.append("file", file);

const response = await fetch("/api/user/avatar", {
  method: "POST",
  body: formData,
});
const { url } = await response.json();
```

## Component Usage

### SettingsNav Component

```tsx
import { SettingsNav } from "@/components/settings/settings-nav";

export default function SettingsSidebar() {
  return (
    <Card>
      <SettingsNav />
    </Card>
  );
}
```

## Customization

### Add New Setting

1. Create new page in `/settings/[new-section]/page.tsx`
2. Add to `settingsNavigation` in `settings-nav.tsx`:

   ```tsx
   {
     name: "New Section",
     href: "/settings/new-section",
     icon: IconName,
     description: "Description of section",
   }
   ```

### Update API Defaults

In `api/user/preferences/route.ts`:

```typescript
const validatedPreferences = {
  // Add your new preference here
  newPreference: body.newPreference || defaultValue,
};
```

## Database Integration Checklist

When connecting to database:

- [ ] Create `user_preferences` table
- [ ] Create `user_avatars` table
- [ ] Create audit log table for data exports
- [ ] Implement `save_user_preferences()` function
- [ ] Implement `get_user_preferences()` function
- [ ] Connect avatar upload to cloud storage
- [ ] Add data retention cleanup job

## Testing Settings

### Test Profile Page

- [ ] Avatar upload (valid and invalid files)
- [ ] Display name editing
- [ ] Email display
- [ ] Form validation

### Test Notifications Page

- [ ] Toggle each notification type
- [ ] Change notification frequency
- [ ] Enable/disable Slack
- [ ] Save and reload preferences

### Test Preferences Page

- [ ] Switch theme (light/dark/system)
- [ ] Toggle compact mode
- [ ] Change dashboard layout
- [ ] Select coaching dimensions
- [ ] Validate at least one dimension selected

### Test Data Page

- [ ] Export as CSV
- [ ] Export as JSON
- [ ] Select items to export
- [ ] Change retention policy
- [ ] Download file

## Styling

All pages use:

- Tailwind CSS
- shadcn/ui components
- Prefect design tokens (colors in tailwind config)
- Lucide React icons

## Colors Available

```css
.bg-prefect-pink     /* Brand pink */
.bg-prefect-sunrise1 /* Brand orange/sunrise */
.text-foreground     /* Primary text */
.text-muted-foreground /* Secondary text */
.bg-muted            /* Muted backgrounds */
.bg-card             /* Card backgrounds */
```

## Icons Used

From lucide-react:

- User (profile)
- Bell (notifications)
- Sliders (preferences)
- Lock (data)
- Upload (file upload)
- Download (data export)
- Loader (loading state)
- Sun/Moon (theme)
- LayoutGrid (layout)
- Slack (slack integration)
- AlertCircle (errors)
- CheckCircle (success)

## Common Patterns

### Form with API Submission

```tsx
const [saving, setSaving] = useState(false);
const [message, setMessage] = useState(null);

const handleSave = async () => {
  setSaving(true);
  try {
    const response = await fetch("/api/endpoint", {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(data),
    });
    if (!response.ok) throw new Error("Failed");
    setMessage({ type: "success", text: "Saved!" });
  } catch (error) {
    setMessage({ type: "error", text: error.message });
  } finally {
    setSaving(false);
  }
};
```

### Loading and Error States

```tsx
if (loading) return <Loader className="h-8 w-8 animate-spin" />;
if (error) return <div className="bg-red-50 p-4 rounded">{error}</div>;
```

### Responsive Layout

```tsx
<div className="grid grid-cols-1 md:grid-cols-4 gap-6">
  <div className="md:col-span-1">Sidebar</div>
  <div className="md:col-span-3">Content</div>
</div>
```

## Troubleshooting

### Settings Not Loading

- Check Clerk authentication
- Verify API endpoint is accessible
- Check browser console for errors
- Verify localStorage permissions

### Avatar Upload Fails

- Check file size (max 5MB)
- Verify file type (JPEG, PNG, GIF, WebP)
- Check permissions on file input
- Verify API endpoint accessibility

### Data Not Persisting

- Verify API response is successful
- Check localStorage fallback
- Verify database connection (future)
- Check network requests in DevTools

## Resources

- [Clerk Documentation](https://clerk.com/docs)
- [Tailwind CSS](https://tailwindcss.com)
- [shadcn/ui Components](https://ui.shadcn.com)
- [Lucide Icons](https://lucide.dev)
- [Next.js API Routes](https://nextjs.org/docs/api-routes/introduction)

## Support

For issues or questions:

1. Check this guide first
2. Review SETTINGS_IMPLEMENTATION.md for detailed architecture
3. Check API endpoints implementation
4. Review Clerk authentication setup
