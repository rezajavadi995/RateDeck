# Card Engine Contract

## Goal

RateDeck cards must feel significantly more polished than a generic market-card template while remaining lightweight and scalable to hundreds or thousands of assets.

The design system must avoid two failures:

1. every asset looks identical except for a logo/color;
2. every asset requires a hand-maintained custom layout.

## Composition model

A card is produced from layered configuration:

```text
Design System
    ×
Asset Family
    ×
Layout
    ×
Theme
    ×
Chart Style
    ×
Density/Decoration
    ×
Optional Asset Override
    ×
Runtime Market Snapshot
```

Not every cross-product combination must be allowed. A compatibility matrix/registry can exclude visually poor combinations.

## Default canvas

Primary square card:

- final output: 1080x1080;
- internal render: 2160x2160 (2x) where feasible;
- downsample using a high-quality filter;
- RGB/RGBA output with deterministic compression/export.

Optional future aspect ratios can include 1080x1350 or story formats, but Phase 2 must first make the square card excellent.

## Renderer

Default renderer is Pillow-based. Do not require Chromium, browser automation or a web rendering stack.

Renderer responsibilities:

- compose backgrounds/shapes/gradients;
- place logos/icons;
- render text with robust bounds/alignment;
- render badges/chips;
- render charts/range widgets;
- apply opacity/layers/clipping;
- deterministic export;
- safe fallback when an asset logo/font/history is absent.

## Card elements

Elements are data-driven records/objects. Typical built-ins:

- brand logo;
- asset logo;
- asset name;
- symbol/pair pill;
- main local price;
- USD/global price;
- 24h change badge;
- high/low widget;
- volume;
- market state;
- chart;
- provider/source line;
- updated time;
- stale badge;
- custom text layer 1..N;
- decorative accent/icon layer;
- footer/watermark.

Element configuration should support where relevant:

- `x`, `y`;
- width/height/max bounds;
- anchor/alignment;
- font family/size/weight;
- opacity;
- visibility;
- z-index/layer;
- text style;
- padding/radius;
- family/theme token references.

Avoid storing arbitrary Python expressions in layout data.

## Design tokens

Central design system tokens include:

- spacing scale;
- typography scale;
- radius scale;
- shadows;
- stroke widths;
- glass/surface opacity;
- badge sizes;
- chip/pill style;
- chart grid density;
- card margins;
- safe zones;
- accent strength.

Themes override tokens rather than duplicating entire rendering logic.

## Asset families

Initial families may include:

- `major_crypto`
- `crypto`
- `stablecoin`
- `tokenized_metal`
- `tokenized_equity`
- `fiat`
- `manual_stars`
- `generic`

Unknown assets always render using `generic` safely.

Family assignment is data/registry driven and admin-overridable. Do not build a massive `if symbol == ...` renderer.

## Auto theming

Asset metadata may provide accent/color hints. Use them as accents, not as an excuse to make every surface a single saturated brand color.

Examples of design intent:

- stablecoin: restrained mint/green accents, calm surface;
- major crypto: premium high-contrast market look;
- tokenized metal: warm/cool luxury material treatment depending on metal identity;
- fiat: clean neutral card with currency/region cue;
- generic: elegant neutral card with generated accent.

Accessibility/readability always wins over brand-color fidelity.

## Theme/layout registry

Example Phase 2 names (names may change; concepts should remain):

Themes:

- Soft Glass
- Dark Pro
- Crystal
- Clean Light
- Luxury
- Ice

Layouts:

- Hero
- Trading
- Compact
- Wide Chart
- Minimal

Chart styles:

- Smooth Area
- Clean Line
- Range Focus
- Minimal Sparkline

All are implementations behind registries. Admin configuration stores stable IDs, not localized display names.

## Charts

### Truthfulness rule

Never invent chart points.

Sources:

- local history recorded from validated market snapshots;
- provider historical endpoint only if explicitly added with its own rate budget.

If history is insufficient:

- show a truthful high/low range widget;
- show day open/current/high/low markers when provider data supports them;
- show “history building” state;
- or choose a layout that does not require a line chart.

Do not draw a fake smooth trend using random/interpolated points that imply observed history.

### Chart quality

For sufficient history:

- adaptive y-range with sensible padding;
- smooth but data-faithful line interpolation;
- subtle grid;
- area gradient where theme allows;
- high/low markers;
- current point marker;
- optional baseline/open marker;
- no misleading exaggerated slope caused by pathological scaling;
- legibility at Telegram image size.

### Local history windows

At minimum Phase 2 should support recent windows that are defensible from stored history, such as 1h/6h/12h/24h once enough points exist. 7d is optional if retention supports it.

## Typography

Persian labels must render correctly, but all numeric glyphs generated by RateDeck remain ASCII digits.

Fonts are configured by family/role. Do not bundle proprietary fonts without proper licensing.

Font fallback must be deterministic and validated at startup/preview time.

## Logos/assets

Admin can upload/replace brand logo. Asset logo support may use:

- configured local asset icon;
- safely cached provider/icon source only if terms permit;
- generated fallback badge from symbol.

Uploaded assets must be validated for:

- type;
- dimensions;
- file size;
- decode success;
- safe destination path.

No user-controlled filesystem paths.

## Admin card editing

Admin flow is preview-first and inline-first.

### Element position editor

Conceptual controls:

```text
        ↑
    ←   •   →
        ↓

Step: 1 | 5 | 10 | 25 px
```

Controls for an element may include:

- move;
- size;
- font;
- alignment;
- opacity;
- visibility;
- layer;
- reset to family/layout default.

### Custom text layers

Admin may add a small bounded number of custom text layers. Each layer has text/rich style + position/appearance config. The renderer must validate bounds and avoid unbounded resource consumption.

### Override hierarchy

Resolution order:

```text
design-system defaults
< theme
< asset family
< layout
< instance/global admin settings
< specific asset override
```

A “Reset override” action returns the asset to family behavior.

## Card cache

Rendered cards may be cached by a deterministic key including:

- asset;
- market snapshot version/timestamp;
- layout/theme/card config revision;
- language/format settings;
- card size.

Do not rerender identical cards for repeated user requests during the same snapshot/config revision.

Cache invalidates when relevant card/template/branding config changes.

## Rendering safety

- constrain text lengths;
- bound font sizes and coordinates;
- reject impossible image dimensions;
- use time/resource limits where reasonable;
- never load remote URLs directly during per-user render;
- sanitize uploaded filenames;
- prevent path traversal;
- handle missing asset/logo/font gracefully.

## Card tests

Tests should cover:

- deterministic output dimensions/mode;
- no crash with generic unknown asset;
- very long names/symbols;
- very large/small prices;
- negative/positive/zero change;
- stale badge;
- missing history fallback;
- sufficient-history chart;
- family/theme/layout resolution;
- override/reset hierarchy;
- uploaded logo validation;
- no Persian numeric glyphs in generated numeric text inputs;
- representative visual golden images or structural pixel assertions where stable.

Golden tests must be used carefully: do not update expected images merely to make CI green without reviewing the visual diff.
