# Date and Time Recipes

Use these patterns when a shortcut handles API dates, timestamps, filenames, or user-facing dates. Keep a raw Date value for calculations and use **Format Date** only when a string is needed.

## Built-In Date and Time Styles

Format Date supports date styles:

- `Short`: numeric date.
- `Medium`: abbreviated month date.
- `Long`: full month date.
- `None`: omit the date component.

Format Date also supports time styles:

- `Short`: hours and minutes.
- `Medium`: hours, minutes, and seconds.
- `Long`: hours, minutes, seconds, and time zone.
- `None`: omit the time component.

These styles are locale-sensitive. Do not rely on them for API parameters unless the API explicitly accepts locale-formatted dates.

## UNIX / Epoch Timestamp Conversion

Apple's documented UNIX timestamp pattern is:

1. Create a **Date** value set to `1970-01-01 00:00:00 UTC`.
2. Use **Adjust Date** to add the UNIX timestamp value as seconds.
3. Use **Format Date** only after the adjusted raw Date exists.

UNIX time is seconds since `1970-01-01 00:00:00 UTC`. If an API returns milliseconds, divide by `1000` only when that API's documentation confirms milliseconds.

## API Standards

Prefer explicit technical standards for APIs:

| Standard | Use | Pattern |
| --- | --- | --- |
| ISO 8601 date | Sortable date-only values, filenames, simple API date fields | `yyyy-MM-dd` |
| ISO 8601 date-time | API date-time values with timezone offset | `yyyy-MM-dd'T'HH:mm:ssXXXXX` |
| RFC 2822 | HTTP/email-style dates when explicitly required | `EEE, dd MMM yyyy HH:mm:ss Z` |

ISO 8601 date strings sort chronologically when sorted alphabetically. RFC 2822 is specialized for internet message formats; do not choose it unless the API requires it.

## Custom Format Strings

Custom Format Date strings use Unicode Technical Standard #35 date patterns. Pattern characters are case-sensitive:

- `yyyy` = calendar year.
- `MM` = month number.
- `MMM` / `MMMM` = abbreviated/full month name.
- `dd` = day of month.
- `HH` = 24-hour hour.
- `hh` = 12-hour hour.
- `mm` = minutes.
- `ss` = seconds.
- `XXXXX` = ISO 8601 timezone offset with a colon.
- `Z` = RFC-style numeric timezone offset.

Wrap literal text in single quotes, including the ISO separator `T`: `yyyy-MM-dd'T'HH:mm:ssXXXXX`.

## Plist Notes

For `is.workflow.actions.format.date`:

- Always set `WFDate` to the source Date as an editor-visible token string.
- For custom formats, set `WFDateFormatStyle` to `Custom`, set `WFDateFormat` to `Custom`, and put the custom pattern in `WFDateFormatString`.
- Keep the unformatted Date value available for later **Adjust Date**, **Get Time Between Dates**, or comparison actions.

## Sources

- Apple Shortcuts User Guide: Handling timestamps using Format Date
- Apple Shortcuts User Guide: Date and time formats
- Apple Shortcuts User Guide: Technical standards
- Apple Shortcuts User Guide: Custom date formats
