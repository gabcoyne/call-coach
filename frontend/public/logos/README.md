# Prefect Brand Assets

This directory contains Prefect brand assets including logos and wordmarks.

## Logo Files (To be added)

Download official Prefect logos from: <https://prefect.io/newsroom/logos>

Required files:

- `prefect-logo.svg` - Primary Prefect logo
- `prefect-logo-white.svg` - White version for dark backgrounds
- `prefect-wordmark.svg` - Prefect wordmark
- `prefect-icon.svg` - Prefect icon only (no text)
- `prefect-logo.png` - PNG fallback (transparent background)

## Usage

Import logos in Next.js components:

```tsx
import Image from "next/image";

<Image src="/logos/prefect-logo.svg" alt="Prefect" width={120} height={32} />;
```

## Brand Colors

- Highlight Pink: #FF4BBD
- Sunrise 1 (Orange): #FE9655
- Sunrise 2 (Yellow): #FEB255
- Blue: #1A94FF
- Purple: #8F47FF

See `tailwind.config.ts` for complete color palette.
