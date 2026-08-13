# Content, Rich Text, Buttons and Telegram UI Safety

## Goal

RateDeck must let the admin deeply customize user-facing text, captions and designated buttons without scattering strings, placeholder rules, custom emoji IDs or Telegram-limit handling across routers.

The core design is:

**one Placeholder Registry + one template system + one rich-text compiler + one button/callback layer + one diagnostics layer.**

## Customizable content surface

At minimum the admin can edit/reset/preview:

- `/start` content;
- `/help` content;
- `/market` content;
- `/support` content;
- `/about` content and visibility where configured;
- price response text;
- conversion response text;
- market empty/stale/unavailable messages;
- card master caption (foundation Phase 1, fully used Phase 2);
- card field fragments;
- designated admin-facing helper/instruction texts where product-safe.

Handlers reference stable template keys; customizable prose is not embedded inside handler code.

## Template definition

Each editable template has:

- stable key;
- Persian admin title/description;
- scope/context;
- target surface (`message`, `caption`, etc.);
- default rich document;
- allowed placeholders;
- required placeholders where needed;
- enabled/visibility policy if applicable;
- revision/update/admin metadata;
- realistic sample preview context.

## Central Placeholder Registry

Every supported `{placeholder}` is registered centrally with metadata:

- stable key;
- valid scope(s);
- value type;
- Persian description;
- sample value;
- formatting/escape policy;
- optional/required/availability semantics where applicable.

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

Do not automatically allow every placeholder in every template.

## Admin placeholder browser

Every template editor has an inline action such as:

`🧩 آکولادهای این متن`

It shows only placeholders valid for that exact scope, paged if needed, with:

- literal syntax to type/copy, e.g. `{price_toman}`;
- Persian meaning;
- sample output;
- optional/required status when relevant.

The admin may mix placeholders with any normal text, punctuation, line breaks, ordinary emoji and captured custom emoji.

## Literal braces

The implementation must define and document a simple literal-brace escape rule so the admin can intentionally display `{` or `}` without invoking placeholder parsing.

Malformed or accidental brace syntax must be reported before save.

## Field-fragment model

Card captions and reusable market blocks use composable field fragments.

Examples:

```text
{field.asset_header}
{field.local_price}
{field.usd_price}
{field.change}
{field.high_low}
{field.source}
{field.updated_at}
```

A field itself is an editable rich template with its own allowed placeholders.

Example:

```text
{asset_emoji} {asset_name} ({asset_symbol})
```

Master caption example:

```text
{field.asset_header}

{field.local_price}
{field.usd_price}
{field.change}

{field.high_low}
{field.updated_at}
```

Rules:

- field reference must exist;
- direct/indirect cycles are rejected;
- expansion depth/size is bounded;
- optional missing data follows explicit field policy (usually empty fragment);
- unresolved `{field.*}` never reaches users.

## Save flow

For arbitrary text/rich-template editing:

1. capture input/entities;
2. parse rich document;
3. validate brace syntax;
4. validate placeholder names/scopes;
5. validate required fields;
6. validate field graph/cycles/bounds;
7. expand realistic sample context;
8. compile Telegram entities;
9. enforce target Telegram length;
10. show preview/current-vs-new summary;
11. save on explicit confirmation where appropriate.

Invalid templates never become active just because parsing partially succeeded.

## Rich-text internal representation

Do not store only raw HTML and call `.format()` on it.

Use one serializable rich-document representation that can contain:

- plain text;
- placeholder token;
- field token;
- custom emoji token (real Telegram ID + fallback);
- ordinary formatting supported by Telegram;
- validated links;
- line breaks.

Placeholder expansion happens before final Telegram entity offset compilation.

## Premium/custom emoji

There is **no standalone Premium Emoji manager**.

When admin input in any supported rich-text editor contains Telegram `custom_emoji` entities:

- read the actual custom emoji/document ID from Telegram update entities;
- preserve a fallback visible character;
- store it as a rich token;
- never guess the ID from Unicode appearance;
- compile it centrally at send/edit time.

Ordinary emoji remains ordinary text.

### UTF-16 offsets

Telegram entity offsets are UTF-16 based. One compiler calculates them after final placeholder/field expansion.

Tests include Persian text, surrogate-pair emoji, custom emoji before/after expanded values, links and mixed formatting.

## Asset caption emoji

Asset metadata includes an optional caption emoji token.

Admin edits it from the asset page, not a global emoji page.

Resolution order:

1. asset-specific configured emoji;
2. family/default emoji if configured;
3. no emoji.

## Button customization model

Every designated customizable button has a stable source-defined spec:

- stable key;
- default plain label;
- source-defined action semantic (callback action or URL type);
- allowed customization flags;
- default Telegram style;
- optional default custom emoji icon;
- owning menu/placement metadata.

Admin override may include, **only if permitted by that spec**:

- label text;
- style;
- custom emoji icon;
- enabled state;
- row/order inside a menu intentionally declared configurable.

Admin must not be able to replace built-in action semantics with arbitrary callback code/text.

## Button custom emoji auto-capture

Button text itself does not support normal message entities.

In a button-label edit flow, if admin sends a Telegram custom emoji with text:

- automatically capture a supported custom emoji as `icon_custom_emoji_id` according to the editor contract;
- preserve the remaining plain label text;
- preview the actual button representation.

No separate icon-ID typing is required for normal use.

## Telegram button styles

Expose only:

- default;
- primary;
- success;
- danger.

Do not expose fake HEX colors or unsupported styles.

## Menu customization

Not every menu is arbitrarily rearrangeable.

For menus explicitly marked configurable, admin may use inline controls to:

- enable/disable safe optional buttons;
- move button earlier/later;
- move row up/down where layout contract permits;
- preview resulting keyboard;
- reset layout.

Safety/navigation/destructive-confirmation buttons may keep fixed placement/semantics.

The system always validates practical keyboard size/row layout before activation.

## Callback codec

One central versioned codec:

- compact namespace/action/record ID;
- <=64 UTF-8 bytes;
- no API keys/templates/JSON/long asset labels/arbitrary user prose;
- unknown version/action fails safely;
- diagnostics can verify every source-defined button action resolves to a registered callback path.

## Current-value display and safe previews

When an admin edits something, the **full current value belongs in the admin message body** where possible.

Buttons display only a safe short preview.

Central preview formatter:

- normalizes whitespace/newlines;
- preserves useful start and optional end context;
- truncates on grapheme boundaries;
- does not split custom-emoji/fallback content;
- uses a conservative UI budget;
- adds ellipsis when shortened.

Examples:

- `✏️ ویرایش • 📊 بازارهای فعال…`
- `متن: شروع متن…آخر متن`

## Inline-first admin rule

Use inline buttons for finite choices:

- on/off;
- provider/mode;
- family;
- style;
- page/filter;
- menu ordering actions;
- position movement;
- step size;
- visibility;
- reset/confirm/cancel;
- favorite/recent selection;
- theme/layout/chart style in Phase 2.

Use free-form input only for arbitrary values:

- template body;
- API key;
- custom alias/search term;
- manual Stars package line;
- custom text layer;
- logo/image upload;
- numeric setting with no sensible bounded chooser.

## Pagination

Large collections require fixed page size + Previous/Next + page indicator + filters/search. Never generate hundreds of inline buttons at once.

## Edit-in-place

Prefer editing the current admin control message. One shared adapter handles Telegram cases where the existing media/content type cannot be edited and a replacement message is needed.

## Callback latency

Acknowledge callback queries immediately/early. Expensive preview/card work happens after callback acknowledgement.

## Dynamic data safety

Template structure is trusted after validation. Runtime placeholder values are escaped/typed and are not interpreted as markup unless the placeholder is explicitly declared a validated rich fragment.

Links supplied by admin are validated.

## Diagnostics

All template/placeholder/field/button/custom-emoji diagnostics are defined in `docs/DIAGNOSTICS.md` and must be available from Telegram admin.

## Required tests

- Placeholder Registry scopes/descriptions/samples;
- unknown/malformed/wrong-scope placeholder rejection;
- literal-brace behavior;
- required placeholder enforcement;
- field dependency/cycle/depth/size checks;
- optional empty field behavior;
- sample preview generation;
- custom emoji capture -> persistence -> render round trip;
- UTF-16 offsets after mixed Persian/placeholder/custom emoji content;
- ordinary emoji remains ordinary;
- button custom emoji extraction;
- supported style mapping only;
- callback 64-byte boundary/action registration;
- grapheme-safe label shortening;
- safe configurable-menu ordering;
- large pagination sets;
- edit-in-place fallback;
- dynamic placeholder escaping;
- final rendered Telegram length enforcement.