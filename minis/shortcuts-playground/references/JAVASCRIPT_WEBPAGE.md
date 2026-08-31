# Run JavaScript on Webpage

`is.workflow.actions.runjavascriptonwebpage` is only appropriate for shortcuts that run from Safari or Safari-backed web views. It is not a general JavaScript runtime.

## Runtime Requirements

- The user must enable **Allow Running Scripts** in Shortcuts privacy/security settings. This is a user setting and cannot be encoded in the plist.
- The shortcut must be available from the share sheet: include `ActionExtension` in `WFWorkflowTypes`.
- Scope shortcut input to Safari webpages: include `WFSafariWebPageContentItem` in `WFWorkflowInputContentItemClasses`.
- To keep the shortcut from appearing in unrelated share sheets, do not include other input classes unless the shortcut has a separate non-JavaScript path for those inputs.
- The action input must be an active Safari webpage from Safari, SFSafariViewController, or ASWebAuthenticationSession.
- If a shortcut contains multiple Run JavaScript on Webpage actions, each one must receive the Safari webpage as input.

## Script Rules

- The script must call `completion(result)` or `completion()`; returning from the JavaScript function is not enough.
- Asynchronous completion is supported. Call `completion(...)` from the async callback or promise resolution path.
- The output must be JSON-compatible: string, number, boolean, array, dictionary/object, `null`, or `undefined`.
- Do not call `JSON.stringify` just to return data to Shortcuts; Shortcuts handles JSON encoding/decoding for supported values.
- Convert DOM nodes, functions, Maps/Sets, and other non-JSON values into arrays or dictionaries of plain values before calling `completion(...)`.

## Timeout and Error Rules

- Keep scripts short and fast. Safari JavaScript extension execution has a time limit.
- Avoid `window.alert()`, `window.prompt()`, and `window.confirm()`; synchronous UI functions can prevent the action from completing in time.
- Avoid multi-second timers and blocking loops. A long `setTimeout` can cause a JavaScript Timeout failure.
- Runtime exceptions are surfaced by Shortcuts. Do not reference `shortcuts.completion()` or any non-Apple completion API.

## Minimal Pattern

```javascript
const title = document.title;
const links = Array.from(document.querySelectorAll("a")).map((link) => ({
  text: link.textContent.trim(),
  href: link.href
}));

completion({ title, links });
```

For no output:

```javascript
document.body.style.fontSize = "120%";
completion();
```

## Sources

- Apple Shortcuts User Guide: Intro to the Run JavaScript on Webpage action
- Apple Shortcuts User Guide: Use the Run JavaScript on Webpage action
