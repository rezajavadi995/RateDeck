# Parser and Conversion Contract

## Purpose

RateDeck should feel natural for Persian Telegram users without becoming a chat keyword trap. The parser therefore optimizes for **high-confidence compact market intent**, not general natural-language understanding.

## Input normalization

Normalization is a dedicated layer and does not decide intent.

Required normalization:

- Persian digits `۰۱۲۳۴۵۶۷۸۹` -> ASCII digits;
- Arabic-Indic digits `٠١٢٣٤٥٦٧٨٩` -> ASCII digits;
- Persian decimal `٫` -> `.`;
- Persian grouping `٬` and common `,` grouping handled safely;
- Arabic `ي` -> Persian `ی`;
- Arabic `ك` -> Persian `ک`;
- zero-width non-joiner and repeated whitespace normalized where semantically safe;
- Unicode case folding for Latin aliases;
- punctuation around symbols/token names normalized without destroying `$` or decimal meaning.

Do not strip arbitrary characters until a malformed value accidentally becomes a valid number. Number parsing is strict.

## Numeric parser

Use Decimal from normalized string input.

Examples accepted:

- `1234`
- `1,234`
- `1_234` only if explicitly supported and tested;
- `۱۲۳۴`
- `۱٬۲۳۴`
- `١٢٣٤`
- `1.25`
- `۱٫۲۵`

Reject malformed forms such as multiple decimal separators, ambiguous mixed grouping, NaN/Infinity, exponent forms unless deliberately supported, and absurdly long numeric tokens.

## Output number formatter

Every bot-generated numeric character is ASCII.

Central formatter responsibilities:

- thousands grouping using comma;
- configurable/adaptive decimals;
- preserve useful precision for low-value tokens;
- trim meaningless trailing zeros where policy says auto;
- percent sign formatting;
- explicit positive sign for change when desired;
- avoid scientific notation in normal user-facing prices unless the value is too small for configured precision and scientific mode is explicitly selected;
- stable formatting in card and text output.

Examples:

- `125,450`
- `4,393.25`
- `0.00001274`
- `+2.43%`

## Alias index

Aliases are data, not a giant source-code conditional.

Sources:

1. core built-ins for common currency words (`تومان`, `ریال`, `دلار`, etc.);
2. runtime discovered symbols;
3. verified asset display names;
4. admin-added aliases;
5. curated safe Persian aliases for major assets.

Alias index rules:

- normalized alias -> one canonical asset where unambiguous;
- ambiguous aliases remain ambiguous and require clarification/search rather than silent selection;
- longest-match-first for multi-word aliases (`بیت کوین`, `the open network`);
- admin cannot create an alias collision without an explicit conflict-resolution step.

## Intent model

Typed intents should include at least:

- `PriceIntent(asset)`
- `ConversionIntent(amount, source, target?)`
- `MarketCommandIntent` for explicit command surfaces
- optional `StatusIntent(asset)` if status-rich rendering differs from normal price
- no-intent result with reason/debug metadata available in tests, not exposed noisily to users.

Avoid returning loosely structured dicts from parser internals.

## High-confidence parser examples

Should parse:

- `btc`
- `بیت کوین`
- `قیمت btc`
- `قیمت بیت کوین`
- `10 btc`
- `۱۰btc`
- `۱۰ بیت کوین`
- `10 btc toman`
- `10 btc به تومان`
- `۱۰ بیت کوین به تومان`
- `1200000 تومان تتر`
- `۱٬۲۰۰٬۰۰۰ تومان تتر`
- `100 usd trx`
- `$100 trx`
- `100$ trx`
- `btc to usdt`
- `btc به usdt`
- `2 paxg trx`
- dynamically discovered symbol-only queries such as a valid Nobitex symbol.

When a conversion has an amount/source but no explicit target, target resolution follows product settings, not parser guessing. Example: admin-configured default target could be IRT for Persian-local usage.

## False-positive examples

Must not parse as a market action by default:

- `من امروز بیت کوین خریدم`
- `این trx برای تست است`
- `please send dollar invoice`
- `فکر میکنی btc رشد میکنه؟`
- `من 10 تتر برای دوستم فرستادم`
- long general sentences containing a known asset.

A strict grammar/allowed-token model is preferred over an NLP guesser.

## Group safety

Group behavior is stricter than private chat.

Configurable modes:

- `compact`: accept only compact high-confidence intents;
- `mention_or_reply`: require bot mention/reply for non-command parser traffic;
- `disabled`: commands only.

The default should protect normal group conversation. Actual visibility also depends on Telegram bot privacy configuration outside the application.

## Parser limits

Do not copy Business Bot's fixed `len(words) <= 8` contract blindly. Instead:

- define reasonable maximum input length for parser work;
- tokenize safely;
- allow configured multi-word aliases;
- reject clearly conversational/long input using grammar confidence and token classes;
- keep worst-case parsing bounded.

The alias matcher should avoid O(number_of_aliases * input_words * alias_length) behavior that becomes expensive with thousands of aliases. Build an indexed structure/trie or equivalent efficient lookup when needed.

## Conversion graph

### Graph model

Assets are nodes. Valid rate relationships are directed edges.

Example:

```text
BTC ──Nobitex──> USDT
BTC ──CoinGecko──> USD
USD ──ExchangeRate──> EUR
USDT ──Nobitex──> IRT
```

The graph may create inverse edges from a validated positive direct edge.

### Route selection

Do not use a hard-coded conversion `if/elif` tree.

Use deterministic path search with policy/scoring. Constraints:

- prevent cycles;
- max hop count kept small;
- direct authoritative routes preferred;
- stale/weak edges penalized;
- ambiguous mappings excluded;
- domain-authoritative routing matters more than arbitrary shortest path.

### Domain preferences

Default preferences:

- target IRT/Toman: direct Nobitex local pair first;
- target USD for verified crypto: CoinGecko direct first;
- fiat-to-fiat: ExchangeRate graph first;
- Nobitex asset without CoinGecko mapping may use its USDT relationship for a clearly labeled derived route when policy allows;
- never use ExchangeRate IRR as an automatic substitute for Iranian free-market Toman.

### Provenance

Every result preserves all edge sources.

Example derived result metadata:

```text
source asset: TON
target asset: IRT
path:
  TON -> USD     CoinGecko
  USD -> USDT    derived via CoinGecko USDT/USD, if needed
  USDT -> IRT    Nobitex
```

The display source should summarize honestly, e.g. `CoinGecko + Nobitex`, not just the final edge provider.

## Price vs bid/ask/latest

Default informational cards may use `latest`/validated market reference prices. If bid/ask are shown, label them explicitly. Conversion policy must define which field it uses; do not silently mix bestBuy, bestSell and latest between assets.

The initial product is informational, not an execution quote engine, so avoid implying guaranteed executable price.

## Staleness

A conversion route is fresh only if all required edges meet their capability's freshness policy. A stale component makes the derived route stale.

If stale display is allowed, the response/card receives an explicit stale marker and old timestamp.

## Stars conversion behavior

Exact package query can return the package's Toman price.

Examples:

- `50 stars` -> exact configured package result if available;
- `50 stars toman` -> same;
- `75 stars` -> unavailable by default if 75 is not configured.

Do not silently interpolate between 50 and 100 packages.

## Parser/conversion test corpus

Maintain data-driven fixtures covering:

- Persian/Arabic/Latin digits;
- zero-width Persian spelling variants;
- punctuation/compact forms;
- dynamic asset symbols;
- alias collisions;
- multiple assets;
- default target behavior;
- direct conversion;
- multi-hop conversion;
- ambiguous/no-route;
- stale edge route;
- natural-language false positives;
- group strictness modes.

When a real user parser bug is discovered, add it to the corpus before/with the fix.
