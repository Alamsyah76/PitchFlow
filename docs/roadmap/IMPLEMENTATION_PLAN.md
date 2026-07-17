# Content Studio AI Implementation Plan

## Source Schema Summary

`UI.json` defines a light-mode dashboard application named **Content Studio AI**. The primary experience is a document-to-content workflow with these major regions:

- A fixed left sidebar with navigation, recent generations, and an upgrade card.
- A top header with page title, subtitle, credits, and user identity.
- A horizontal workflow stepper for five stages: upload PDF, generate topics, select topic, generate caption, generate image.
- A two-column upload/input area.
- A generated topics section with selectable scored topic cards.
- A caption studio split into a large editor and smaller performance insights panel.
- A sticky footer action bar for copy and image generation actions.

The schema is mostly presentational seed data, not a full data contract. It should be treated as a UI blueprint plus initial/mock state while keeping the existing backend integration points for upload, topic generation, caption generation, and carousel/image export.

## Current Repo Context

The frontend lives in `frontend/` and uses:

- Next.js pages router.
- React 18.
- TypeScript.
- Tailwind CSS.
- Tiptap rich text editor in `frontend/components/RichEditorTiptap.tsx`.
- `lucide-react` for icons.
- SWR is installed but not currently central to the page state.

The current working UI is concentrated in `frontend/pages/index.tsx`, with older layout components in `frontend/components/ColumnLeft.tsx`, `ColumnCenter.tsx`, and `ColumnRight.tsx`. The implementation should evolve the existing Next/Tailwind structure instead of introducing a separate app shell.

## Recommended Folder Structure

```text
frontend/
  components/
    app-shell/
      AppShell.tsx
      Sidebar.tsx
      SidebarNav.tsx
      RecentGenerations.tsx
      UpgradeCard.tsx
      HeaderBar.tsx
      MobileNav.tsx
    content-studio/
      ContentStudioPage.tsx
      WorkflowStepper.tsx
      UploadDocumentCard.tsx
      KeywordInputCard.tsx
      TopicCards.tsx
      TopicCard.tsx
      CaptionStudio.tsx
      CaptionEditorPanel.tsx
      PerformanceInsights.tsx
      FooterActionBar.tsx
      EmptyState.tsx
    ui/
      button.tsx
      card.tsx
      input.tsx
      label.tsx
      badge.tsx
      progress.tsx
      separator.tsx
      avatar.tsx
      tooltip.tsx
      sheet.tsx
      scroll-area.tsx
      dropdown-menu.tsx
  data/
    ui-config.ts
  hooks/
    useContentStudio.ts
    useIsMobile.ts
  lib/
    api.ts
    content-studio-types.ts
    utils.ts
  pages/
    index.tsx
    dashboard.tsx
    content-studio.tsx
    image-studio.tsx
    history.tsx
    saved.tsx
    templates.tsx
    settings.tsx
  styles/
    globals.css
```

Notes:

- `data/ui-config.ts` should hold a typed version of the static data from `UI.json`. Keep `UI.json` as the design source, but avoid importing raw JSON throughout the component tree.
- `content-studio-types.ts` should define `WorkflowStep`, `Topic`, `UploadedFileState`, `CaptionMetrics`, and `ContentStudioState`.
- `components/ui/` should contain shadcn/ui generated primitives, customized through Tailwind tokens and `cn`.
- Existing `RichEditorTiptap.tsx` can remain in `components/` initially, then be wrapped by `CaptionEditorPanel`.

## Page Hierarchy

### Primary Route

- `/content-studio`
  - Uses `AppShell`.
  - Renders `ContentStudioPage`.
  - This should become the canonical implementation of the schema because `sidebar.menu` marks Content Studio as active.

### Root Route

- `/`
  - Redirect to `/content-studio`, or render the same `ContentStudioPage`.
  - Redirect is cleaner once the full app shell exists.

### Sidebar Placeholder Routes

- `/dashboard`
- `/image-studio`
- `/history`
- `/saved`
- `/templates`
- `/settings`

These routes can initially render `AppShell` with a simple page title and empty/coming-soon content area. The sidebar should still navigate to them so the information architecture in `UI.json` is honored.

### Component Tree for `/content-studio`

```text
ContentStudioRoute
  AppShell
    Sidebar
      Logo
      SidebarNav
      RecentGenerations
      UpgradeCard
    HeaderBar
    MainContent
      WorkflowStepper
      UploadSection
        UploadDocumentCard
        KeywordInputCard
      TopicCards
      CaptionStudio
        CaptionEditorPanel
          RichEditorTiptap
        PerformanceInsights
      FooterActionBar
```

## Reusable Components

### App Shell

- `AppShell`
  - Owns the dashboard grid: fixed sidebar, sticky/top header, scrollable content area.
  - Accepts `children`, `activeRoute`, and optional page metadata.

- `Sidebar`
  - Consumes logo, menu, recent generation, and upgrade card data.
  - Uses `lucide-react` icons mapped from schema icon strings.
  - Desktop: fixed 260px width.
  - Mobile/tablet: collapses into `Sheet` navigation opened from header.

- `HeaderBar`
  - Displays title/subtitle from schema or current route metadata.
  - Shows credits badge and user avatar.
  - On smaller screens, includes menu trigger.

### Content Workflow

- `WorkflowStepper`
  - Renders the five horizontal steps.
  - Supports statuses: `complete`, `active`, `disabled`, `pending`.
  - Status should be derived from workflow state, not hard-coded to the JSON seed.

- `UploadDocumentCard`
  - Drag/drop and file picker for single PDF upload.
  - Shows uploaded file name, size, and success/error/loading state.
  - Maps to existing upload endpoint logic from `index.tsx`.

- `KeywordInputCard`
  - Keyword input plus optional audience/tone fields if needed later.
  - Shows schema tips as a compact helper list.
  - Owns the primary `Generate Topics` action.

- `TopicCards`
  - Section wrapper with title/subtitle.
  - Renders empty, loading, and populated states.

- `TopicCard`
  - Displays title, score, potential badge, and selected state.
  - Click selects a topic and can trigger caption generation.

- `CaptionStudio`
  - Two-column layout matching schema `70-30`.
  - Owns spacing between editor and insights.

- `CaptionEditorPanel`
  - Wraps existing `RichEditorTiptap`.
  - Provides toolbar affordances, copy action, and hashtag display.
  - Avoid duplicating editor state outside the central hook except for editor-local interactions.

- `PerformanceInsights`
  - Displays metrics as progress bars/rings.
  - Shows success badge for viral potential.

- `FooterActionBar`
  - Sticky bottom action bar.
  - Shows `Copy Caption` and `Generate Image`.
  - Should be hidden or simplified until a caption exists.

## shadcn/ui Dependencies

Install and configure shadcn/ui for the current Next.js pages-router project. Recommended components:

```text
button
card
input
label
badge
progress
separator
avatar
tooltip
sheet
scroll-area
dropdown-menu
```

Likely package additions from shadcn setup:

```text
class-variance-authority
clsx
tailwind-merge
tailwindcss-animate
@radix-ui/react-avatar
@radix-ui/react-dialog
@radix-ui/react-dropdown-menu
@radix-ui/react-label
@radix-ui/react-progress
@radix-ui/react-scroll-area
@radix-ui/react-separator
@radix-ui/react-slot
@radix-ui/react-tooltip
```

Existing dependencies to keep using:

- `lucide-react` for all schema icons.
- `@tiptap/*` for the caption editor.
- `jspdf` only for existing carousel/PDF export behavior.
- `swr` only if backend fetches are moved out of event handlers later.

Tailwind config updates needed:

- Add shadcn content paths for `components`, `pages`, `lib`, and any new folders.
- Add CSS variables for theme tokens.
- Add `tailwindcss-animate` plugin.
- Define radius using schema token, but consider using `0.5rem` to keep UI controls restrained. Use larger radius only where the design explicitly benefits from it.

## State Management Approach

Use local React state consolidated into a custom hook first. The workflow is page-scoped and does not justify a global store yet.

### `useContentStudio`

Own state:

- `apiHealthy`
- `apiError`
- `loading`
- `uploadState`
- `contentId`
- `keywords`
- `audience`
- `language`
- `topics`
- `selectedTopic`
- `captionHtml`
- `failedPropositions`
- `metrics`
- `pdfProgress`
- `toast`

Expose actions:

- `checkApiHealth`
- `uploadPdf(file)`
- `generateTopics()`
- `selectTopic(topic)`
- `generateCaption(topic)`
- `copyCaption()`
- `generateImageOrCarousel()`

Derived state:

- `currentStep`
- `canGenerateTopics`
- `canSelectTopic`
- `canCopyCaption`
- `canGenerateImage`
- `workflowSteps`

### Backend Integration

Reuse the current endpoint flow:

- `POST /api/v1/content/upload`
- `GET /api/v1/content/topics?document_id=...`
- caption generation through `generateCaption`
- carousel generation through `generateCarousel`

Normalize backend topics into the schema-style topic shape:

```text
{
  id,
  title,
  score,
  potential,
  selected
}
```

If the backend only returns topic text, compute temporary display scores client-side only for mock presentation, or omit scores until the backend provides them. Avoid treating generated fake scores as real analytics.

### Server State

Keep event-driven fetches in the hook for the first implementation. Introduce SWR only if the app adds:

- persisted history,
- saved items,
- templates,
- account credits,
- repeated polling,
- cache sharing between routes.

## Responsive Strategy

### Desktop, 1280px and Up

- Fixed 260px sidebar.
- Header height 80px.
- Main content max-width 1440px with 32px padding.
- Upload area uses two equal columns.
- Caption studio uses `70fr 30fr` or `minmax(0, 1fr) 360px`.
- Footer action bar spans the content area, not the sidebar.

### Tablet, 768px to 1279px

- Sidebar becomes a collapsible `Sheet` or compact rail.
- Header remains sticky.
- Upload area can remain two columns above 900px; below that, stack.
- Caption studio stacks editor above insights when the insight panel would become too narrow.
- Topic cards use a responsive grid: two columns when space allows.

### Mobile, Below 768px

- No fixed sidebar; use header menu button with `Sheet`.
- Content padding drops to 16px.
- Workflow stepper becomes horizontally scrollable, with fixed step item widths.
- Upload cards stack.
- Topic cards stack.
- Caption editor toolbar wraps cleanly and uses icon buttons with tooltips.
- Footer action bar remains sticky, but actions stack or use two equal-width buttons.
- Ensure the bottom sticky bar does not cover editor content by adding bottom padding to main content.

### Accessibility and Interaction

- All icon-only buttons need `aria-label` and tooltip text.
- Dropzone should support keyboard activation through a visible button/label.
- Selected topic state should be announced via visible selected badge and `aria-pressed` or equivalent.
- Progress metrics need text values, not color-only communication.
- Preserve focus states from shadcn primitives.

## Visual System

Map schema theme tokens into CSS variables:

- Primary: `#6D5DFC`
- Secondary: `#8B5CF6`
- Background: `#F8FAFC`
- Surface: `#FFFFFF`
- Border: `#E5E7EB`
- Text: `#0F172A`
- Muted: `#64748B`

Use gradients sparingly for primary calls to action only:

- `Generate Topics`
- `Generate Image`
- Upgrade CTA

The schema radius is `16px`, but shadcn cards and dashboard controls should stay visually disciplined. Recommended:

- Cards: 12px to 16px.
- Buttons/inputs: 8px to 10px.
- Badges: pill radius where appropriate.

## Implementation Phases

### Phase 1: Foundation

- Add shadcn/ui setup and required primitives.
- Add `lib/utils.ts` with `cn`.
- Update Tailwind theme tokens and content paths.
- Move static schema-derived constants into `data/ui-config.ts`.

### Phase 2: App Shell

- Build `AppShell`, `Sidebar`, `HeaderBar`, `RecentGenerations`, and `UpgradeCard`.
- Add routes for `/content-studio` and sidebar placeholders.
- Redirect or mirror `/` to `/content-studio`.

### Phase 3: Workflow Components

- Build `WorkflowStepper`.
- Build upload/input section.
- Build topic cards.
- Build caption studio and insights panel using existing Tiptap editor.
- Build sticky footer action bar.

### Phase 4: State and API Wiring

- Extract current `index.tsx` state and handlers into `useContentStudio`.
- Wire upload, topic generation, topic selection, caption generation, copy, and carousel/image export.
- Add clear loading, empty, success, and error states.

### Phase 5: Responsive QA

- Verify desktop, tablet, and mobile layouts.
- Check that sticky sidebar/header/footer do not overlap content.
- Check editor toolbar wrapping and topic card selection states.
- Confirm keyboard access for upload, sidebar nav, topic cards, and editor actions.

## Risks and Decisions

- The schema contains mock values for user, credits, recent generations, uploaded file, topics, and metrics. Decide which are backend-backed now versus static placeholders.
- `lucide-react` version is very old in `package.json`; some schema icons may not exist under the expected names. If icon imports fail, upgrade `lucide-react` or map to available alternatives.
- Existing text has some mojibake characters in the current page/components. Clean user-facing strings during implementation.
- Existing Tiptap toolbar overlaps above the editor using absolute positioning. The new caption panel should make toolbar layout part of normal document flow to avoid responsive overlap.
- shadcn/ui setup may require dependency installation and Tailwind config changes before components can be generated.

## Verification Checklist

- TypeScript build passes.
- Next.js dev page loads at `/content-studio`.
- Sidebar active state follows current route.
- Upload accepts only one PDF and shows selected file state.
- Generate topics is disabled or guarded before upload.
- Selecting a topic updates selected state and caption area.
- Copy action writes plain caption text and hashtags.
- Generate image/carousel action preserves existing export behavior.
- Layout works at 1440px, 1024px, 768px, and 390px widths.
- No content is hidden behind sticky header/sidebar/footer.
