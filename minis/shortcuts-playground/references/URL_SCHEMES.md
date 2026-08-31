# Shortcuts URL Schemes and x-callback-url

Use only Apple-documented Shortcuts URL forms. Do not invent `shortcuts://` routes, import routes, or extra query parameters unless the user provides working evidence from their own shortcut library.

## Apple-Documented Shortcuts URLs

All query parameter values must be URL-encoded.

| Purpose | URL |
| --- | --- |
| Open Shortcuts | `shortcuts://` |
| Create a new shortcut editor draft | `shortcuts://create-shortcut` |
| Open an existing shortcut | `shortcuts://open-shortcut?name=<encoded shortcut name>` |
| Run a shortcut | `shortcuts://run-shortcut?name=<encoded shortcut name>` |
| Run with text input | `shortcuts://run-shortcut?name=<encoded shortcut name>&input=text&text=<encoded text>` |
| Run with clipboard input | `shortcuts://run-shortcut?name=<encoded shortcut name>&input=clipboard` |
| Open Gallery | `shortcuts://gallery` |
| Search Gallery | `shortcuts://gallery/search?query=<encoded search terms>` |

Use the **Run Shortcut** action instead of `shortcuts://run-shortcut` when one shortcut needs to run another shortcut. Use the URL scheme only for integration from outside Shortcuts, such as another app, a website, a command line, or a task manager URL field.

## x-callback-url

Shortcuts supports x-callback-url for running shortcuts and returning to the calling app:

```text
shortcuts://x-callback-url/run-shortcut?name=<encoded shortcut name>&input=text&text=<encoded text>&x-success=<encoded callback URL>&x-cancel=<encoded callback URL>&x-error=<encoded callback URL>
```

Callback parameters:

| Parameter | Behavior |
| --- | --- |
| `x-success` | Opened after successful completion. When a shortcut runs, Shortcuts appends `result=<text output>` to this callback URL. |
| `x-cancel` | Opened when the user cancels before completion. No shortcut output is provided. |
| `x-error` | Opened when Shortcuts fails to complete. Shortcuts appends `errorMessage=<description>` to this callback URL. |

Always URL-encode the callback URL itself. For example, `myapp://done` becomes `myapp%3A%2F%2Fdone` when placed in `x-success`.

## Building These in Shortcuts

- For a normal URL launch, use **URL** (`is.workflow.actions.url`) followed by **Open URL** (`is.workflow.actions.openurl`).
- For callback workflows, prefer **Open X-Callback URL** (`is.workflow.actions.openxcallbackurl`) when the shortcut must wait for or route callbacks.
- Do not hard-code unencoded user text into a URL. Assemble text first, then URL-encode user-supplied pieces.
- Do not use `input=text` without a non-empty `text` parameter.
- Do not include `text=` with `input=clipboard`; Shortcuts ignores it.

## Local Verification Notes

On macOS, `open -g -u <url>` verifies that LaunchServices accepts the Shortcuts URL and hands it to Shortcuts. In local testing on 2026-05-04, `shortcuts://`, `shortcuts://gallery`, `shortcuts://gallery/search?query=photos`, `shortcuts://open-shortcut?name=Shortcuts%20Playground`, and `shortcuts://create-shortcut` all returned success through `open -g -u`.

x-callback success/error routing requires a runnable shortcut and a real callback receiver. The bundled validator therefore verifies the documented URL shapes and required parameters, but it cannot prove a specific user-library shortcut exists.

## Sources

- Apple Shortcuts User Guide: Open and create a shortcut using a URL scheme
- Apple Shortcuts User Guide: Run a shortcut from a URL
- Apple Shortcuts User Guide: Open or search the Gallery from a URL
- Apple Shortcuts User Guide: Use x-callback-url
