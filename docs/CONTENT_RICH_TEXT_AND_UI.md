# Content, Rich Text, Buttons and Telegram UI Safety

## Goals

RateDeck lets the admin customize user-facing content deeply without scattering strings, placeholder rules, custom emoji IDs or callback behavior across handlers.

The core requirement is **central representation + central validation + central rendering**.

## Template system

Every editable text has a stable key, for example:

- `user.start`
- `user.help`
- `user.market`
- `user.support`
- `user.about`
- `market.price.text`
- `market.conversion.text`
- `card.caption.master`
- `card.field.asset_header`
- `card.field.local_price`
- `card.field.usd_price`
- `card.field.change`
- `card.field.high_low`
- `card.field.source`
- `card.field.updated_at`
- `admin.provider.health`
- `admin.error.generic`

Handlers reference keys; they do not contain the customizable prose.

## Template definition

Conceptual fields:

- key;
- title shown to admin;
- scope/context;
- default rich document;
- allowed placeholders;
- required placeholders;
- enabled state if applicable;
- revision;
- updated_at/admin ID;
- sample preview context.

## Placeholder contracts

Placeholders are explicit per scope.

Possible market placeholders include:

- `{asset}`
- `{asset_name}`
- `{asset_symbol}`
- `{asset_emoji}`
- `{amount}`
- `{source_amount}`
- `{target_amount}`
- `{source_asset}`
- `{target_asset}`
- `{price_toman}`
- `{price_usd}`
- `{change_24h}`
- `{high_24h}`
- `{low_24h}`
- `{volume_24h}`
- `{provider}`
- `{source}`
- `{updated_at}`
- `{market_status}`
- `{stale_label}`

Generic command scopes may include:

- `{user_first_name}`
- `{user_id}`
- `{bot_username}`
- `{support_username}`
- `{asset_count}`
- `{available_categories}`
- `{command_examples}`

Do not automatically allow every placeholder everywhere.

## Field-fragment model

Card captions use composable field fragments plus a master template.

Example field fragment:

```text
{asset_emoji} {asset_name} ({asset_symbol})
```

Example local-price fragment:

```text
💵 قیمت ایران: {price_toman} تومان
```

Example master:

```text
{field.asset_header}

{field.local_price}
{field.usd_price}
{field.change}

{field.high_low}
{field.updated_at}
```

Admin may add arbitrary fixed text around fields. Missing optional field data resolves through explicit field policy (usually empty fragment), not raw `{field.*}` leakage.

## Save-time validation

Before save:

1. parse rich document;
2. validate braces/placeholders;
3. reject unknown placeholders;
4. verify required placeholders;
5. estimate/render with sample context;
6. enforce Telegram length limits for the target surface;
7. display preview;
8. save only after explicit confirmation where the flow requires it.

Malformed templates never reach users as raw braces.

## Rich-text internal representation

Do not store only raw HTML and then perform arbitrary `.format()` over it.

Preferred internal model is a serializable rich document/AST with segments such as:

- plain text;
- placeholder token;
- custom emoji token with Telegram ID + fallback;
- bold/italic/underline/strikethrough/spoiler/code/pre where supported;
- link entity with validated URL;
- line breaks.

The exact type design is implementation-specific, but placeholder expansion must occur before final Telegram entity offset compilation.

## Custom/Premium Emoji capture

There is **no separate Premium Emoji Manager**.

When an admin sends/edit input containing Telegram `custom_emoji` entities:

- read the real entity/custom emoji ID from Telegram update data;
- preserve the visible fallback emoji/text;
- store a custom-emoji segment in the rich document;
- never guess an ID from Unicode appearance;
- render through the central compiler.

If the input contains only an ordinary Unicode emoji, store ordinary text.

### UTF-16 offsets

Telegram message entity offsets are UTF-16 based. The compiler must calculate offsets centrally after placeholder expansion. Tests must include surrogate-pair emoji, Persian text and mixed content.

## Asset caption emoji

Asset metadata includes an optional caption emoji rich token. Admin edits it from the asset page by sending/selecting an emoji.

This is distinct from a global emoji manager: the emoji belongs to that asset's metadata.

Resolution:

- asset-specific emoji if configured;
- family/default emoji if configured;
- no emoji otherwise.

## Button model

Stable button spec fields may include:

- key;
- localized text/rich-input source;
- callback action ID or URL action;
- Telegram style;
- optional `icon_custom_emoji_id`;
- enabled;
- row/order metadata where the owning menu permits customization.

Button text itself does not support normal message entities. If the admin supplies a custom emoji in a button-label edit flow, RateDeck should capture a supported custom emoji as the button icon and store remaining plain label text according to the editor contract.

Do not pretend multiple rich message entities can render inside button text.

## Telegram button styles

Admin may choose only:

- default;
- primary;
- success;
- danger.

Do not expose fake arbitrary HEX colors or unsupported “warning” styles as if Telegram would render them.

## Callback codec

Central callback codec requirements:

- versioned namespace;
- short action ID;
- compact integer/opaque record ID when needed;
- UTF-8 byte count <= 64;
- decode validation;
- unknown namespace/action fails safely;
- no secrets/user prose/JSON/templates in callback payload.

Example conceptual form:

`v1:a:asset:123`

Actual encoding may be more compact.

## Safe button labels/previews

Admin menus often need to show a current value. Never put the entire previous template/value into a button.

A central preview formatter should:

- normalize newlines/whitespace;
- preserve useful beginning and optionally ending context;
- truncate on grapheme boundaries;
- never split a custom emoji/fallback pair;
- enforce a conservative UI character budget below platform failure thresholds;
- add an ellipsis when shortened.

Examples:

- `✏️ ویرایش • 📊 بازارهای فعال…`
- `متن فعلی: شروع متن…آخر متن`

The full old value belongs in the admin message body, not the button.

## Inline-first admin rule

Use inline buttons whenever the value comes from a finite set:

- on/off;
- provider/mode;
- family;
- theme/layout/chart style;
- button style;
- page;
- position movement;
- step size;
- visibility;
- reset/confirm/cancel;
- recent/favorite asset;
- predefined font/size choices where practical.

Use typed/free-form input only for genuinely arbitrary values:

- template body;
- API key;
- custom alias/search query;
- custom text layer;
- logo/image upload;
- manual Stars price line;
- numeric setting that cannot be represented safely by bounded choices.

## Pagination

Large collections (hundreds of assets/templates) require:

- fixed page size;
- Previous/Next;
- current page indicator;
- Favorites;
- Recent;
- category/family filters;
- search fallback.

Do not generate keyboards with hundreds of buttons.

## Edit-in-place UX

Prefer `edit_message_text`, `edit_message_caption` or reply-markup edits for admin navigation when legal. If Telegram rejects the edit because media/content type requires replacement, use one central adapter that safely falls back to sending a new control message and optionally cleaning the previous one.

Do not duplicate this error handling in every router.

## Callback response latency

Callback queries are acknowledged immediately or as early as possible, while heavier work happens after acknowledgement. Card preview generation may send a temporary status/update if necessary; it must not leave Telegram's callback spinner hanging during expensive rendering.

## Admin language

All Telegram admin UI defaults to Persian. Numeric output policy remains ASCII digits.

## User template safety

Dynamic user values are never interpreted as markup merely because the template supports formatting. The rich-text compiler distinguishes trusted template structure from escaped dynamic placeholder data, except where a placeholder type explicitly returns a prevalidated rich fragment.

Links/URLs supplied by admin are validated before rendering.

## Required tests

- unknown/malformed placeholder rejection;
- required placeholder enforcement;
- optional empty field behavior;
- sample preview generation;
- custom emoji capture -> storage -> render round trip;
- UTF-16 offsets after Persian text + placeholder expansion + emoji;
- ordinary emoji remains ordinary;
- button custom emoji icon extraction;
- supported style mapping only;
- callback data 64-byte boundary;
- malicious/long callback rejection;
- grapheme-safe label shortening;
- large pagination sets;
- edit-in-place fallback adapter;
- dynamic placeholder escaping.
