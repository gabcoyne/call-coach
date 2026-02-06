# Call Recording Player Enhancements

## Overview

The CallRecordingPlayer and related components have been significantly enhanced with advanced features for better coaching insights visualization and call analysis.

## New Features

### 1. Timeline Annotation Markers

**Component**: `AnnotationMarker.tsx`

Visual markers appear on the timeline showing where coaching insights occur. Each marker:

- Color-coded by dimension (product_knowledge=blue, discovery=green, objection_handling=orange, engagement=purple)
- Displays insight on hover
- Clickable to jump to that moment in the recording
- Animated feedback for better UX

**Usage**:

```tsx
<AnnotationMarker
  annotation={annotation}
  duration={duration}
  isHovered={hoveredId === annotation.id}
  onHover={setHoveredId}
  onClick={handleJump}
/>
```

**Data Structure**:

```typescript
interface Annotation {
  id: string;
  timestamp: number; // in seconds
  dimension: "product_knowledge" | "discovery" | "objection_handling" | "engagement";
  title: string; // e.g., "Great discovery question"
  insight: string; // detailed coaching insight
  severity?: "positive" | "neutral" | "improvement";
}
```

### 2. Annotation Popover

**Component**: `AnnotationPopover.tsx`

Floating panel that displays detailed coaching insights with:

- Dimension icon and label
- Full insight text
- Expandable dimension description
- Close button
- Jump-to-moment action

Useful for detailed review of specific coaching moments.

### 3. Coaching Overlay

**Component**: `CoachingOverlay.tsx`

Floating panel that automatically appears when playing through a section with a coaching insight. Features:

- Smooth slide-in animation
- Contextual coaching suggestions
- Auto-dismiss or manual close
- Positioning options (bottom-right, bottom-left, top-right, top-left)

The overlay intelligently detects when the playback time is near an annotation and displays relevant coaching guidance.

### 4. Enhanced CallRecordingPlayer

**Component**: `CallRecordingPlayer.tsx`

Major upgrades:

- **Playback speed control**: 0.5x, 1x, 1.5x, 2x speeds
- **Annotation timeline**: Visual timeline with coaching insight markers
- **Timestamp sharing**: Copy a shareable link to specific moments
- **Better layout**: Improved UI with header, secondary controls
- **Performance**: Smooth animation and state management

**New Props**:

```typescript
interface CallRecordingPlayerProps {
  gongUrl?: string | null;
  recordingUrl?: string | null;
  duration: number;
  annotations?: Annotation[]; // NEW
  onTimestampClick?: (timestamp: number) => void; // NEW
}
```

### 5. Enhanced TranscriptSearch

**Component**: `TranscriptSearch.tsx`

Improvements:

- **Auto-scroll**: Automatically scrolls to current playback segment
- **Highlight current speaker**: Shows "Playing" indicator for active segment
- **Playback synchronization**: Receives `currentPlaybackTime` prop
- **Auto-expand long segments**: Expands current segment if it's lengthy
- **Better visual feedback**: Highlights with blue background when playing

**New Props**:

```typescript
interface TranscriptSearchProps {
  transcript: TranscriptSegment[];
  onTimestampClick?: (timestamp: number) => void;
  currentPlaybackTime?: number; // NEW
}
```

### 6. Clip Generator

**Component**: `ClipGenerator.tsx`

Enables sharing of specific coaching moments with:

- Automatic 30-second clip generation (15 seconds before/after insight)
- Copy shareable link with timestamp range
- Download functionality (backend integration ready)
- Visual timeline showing clip boundaries
- One-click sharing

**Usage**:

```tsx
<ClipGenerator annotation={annotation} duration={duration} onGenerate={handleGenerate} />
```

### 7. Enhanced Call Player Integration

**Component**: `EnhancedCallPlayer.tsx`

Comprehensive player combining all features:

- Tabbed interface: Transcript, Coaching Insights, Share Clip
- Synchronized playback across all components
- Coaching insight selection and display
- One-stop interface for call analysis

## Integration with CallAnalysisViewer

The `CallAnalysisViewer` has been updated to:

1. Generate annotations from dimension_details
2. Use `EnhancedCallPlayer` instead of basic player
3. Pass transcript and annotations to the player
4. Handle timestamp clicks to sync audio playback

Example annotation generation:

```typescript
const generateAnnotations = (): Annotation[] => {
  // Creates annotations from strengths/improvements
  // Maps to timeline positions
  // Assigns severity based on type
};
```

## Color Coding

Dimensions are color-coded for quick visual identification:

| Dimension          | Color            | Icon          |
| ------------------ | ---------------- | ------------- |
| Product Knowledge  | Blue (#3B82F6)   | AlertCircle   |
| Discovery          | Green (#22C55E)  | Search        |
| Objection Handling | Orange (#F97316) | MessageSquare |
| Engagement         | Purple (#A855F7) | TrendingUp    |

## Performance Considerations

1. **Memoization**: Components use useCallback and useMemo to prevent unnecessary re-renders
2. **Lazy updates**: Annotation detection only triggers when currentTime changes significantly
3. **DOM optimization**: Annotations are rendered efficiently on the timeline
4. **Audio sync**: Smooth playback without audio glitches

## Usage Example

### Basic Usage

```tsx
<CallRecordingPlayer
  gongUrl="https://gong.io/..."
  recordingUrl="https://example.com/call.mp3"
  duration={3600}
  annotations={coachingAnnotations}
/>
```

### With Transcript Sync

```tsx
<EnhancedCallPlayer
  recordingUrl="https://example.com/call.mp3"
  duration={3600}
  transcript={transcriptSegments}
  annotations={coachingAnnotations}
  onTimestampClick={handleJump}
/>
```

### Full Integration

```tsx
import { EnhancedCallPlayer } from "@/components/coaching/EnhancedCallPlayer";
import type { Annotation } from "@/components/coaching/AnnotationMarker";

export function CallPage() {
  const annotations: Annotation[] = [
    {
      id: "insight-1",
      timestamp: 120,
      dimension: "discovery",
      title: "Excellent discovery question",
      insight: "Asked about budget constraints early, showing good listening skills",
      severity: "positive",
    },
    // ... more annotations
  ];

  return (
    <EnhancedCallPlayer
      recordingUrl={recordingUrl}
      duration={duration}
      transcript={transcript}
      annotations={annotations}
    />
  );
}
```

## Accessibility

All components include:

- Semantic HTML
- ARIA labels where appropriate
- Keyboard-accessible controls
- Color + icon differentiation (not color-only)
- High contrast text

## Browser Support

- Chrome/Edge: Full support
- Firefox: Full support
- Safari: Full support (iOS audio playback may require user interaction)

## Future Enhancements

1. **Custom annotation timestamps**: Allow users to create bookmarks during playback
2. **Annotation filtering**: Show/hide annotations by dimension
3. **Speed-adjusted segment expansion**: Auto-scroll more accurately at different playback speeds
4. **Clip download**: Backend integration for actual audio clip generation
5. **Annotation export**: Export annotations as PDF or JSON
6. **Multi-speaker highlighting**: Different colors for different speakers in transcript

## API Integration Points

### Required Data Structure

For annotations to work, coaching analysis must provide:

```typescript
interface DimensionAnalysis {
  score: number | null;
  strengths?: string[]; // Used to generate positive annotations
  areas_for_improvement?: string[]; // Used to generate improvement annotations
  specific_examples?: SpecificExamples;
  action_items?: string[];
  error?: string;
}
```

The `CallAnalysisViewer.generateAnnotations()` function creates timeline annotations from these properties.

## Component Files Location

```
frontend/components/coaching/
├── CallRecordingPlayer.tsx           (enhanced)
├── TranscriptSearch.tsx              (enhanced)
├── AnnotationMarker.tsx              (new)
├── AnnotationPopover.tsx             (new)
├── CoachingOverlay.tsx               (new)
├── ClipGenerator.tsx                 (new)
├── EnhancedCallPlayer.tsx            (new)
└── index.ts                          (updated)
```

## Styling

Components use Tailwind CSS with:

- Blue accent color for primary actions
- Green for positive/strength indicators
- Orange for improvement opportunities
- Purple for engagement insights
- Responsive design that works on mobile, tablet, and desktop
