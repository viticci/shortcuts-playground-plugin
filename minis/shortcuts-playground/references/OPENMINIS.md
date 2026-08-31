# OpenMinis Shortcut actions (optional third-party integration)

This reference documents actions from the public OpenMinis source repository, not guessed action
identifiers. Source: `https://github.com/OpenMinis/OpenMinis`, inspected at commit
`09fc199928de0f26685e766c34e6d541c7a69e5a`.

The observed iOS app bundle identifier is:

```text
com.openminis.app
```

## Registered App Shortcuts

The source `MinisShortcutsProvider` registers these actions:

- **Ask Minis** → `AskMinisIntent`
- **Quick Task** → `QuickTaskIntent`
- **Send Prompt** → `SendPromptIntent`
- **Get Session Status** → `GetSessionStatusIntent`
- **List Sessions** → `ListSessionsIntent`
- **Follow Up Session** → `FollowUpSessionIntent`
- **Open Session** → `OpenSessionIntent`

`RetryRunIntent` is implemented but intentionally not registered in the provider because of an
iOS 16 launch issue involving an intent parameter dependency. It may still be available under
Shortcuts → All Actions. `AudioTogglePlaybackIntent` is a Live Activity narration control, not a
normal chat automation action.

## Send Prompt

Source file: `src/ios/Agent/Intents/SendPromptIntent.swift`.

Parameters:

- `Prompt: String` — the text sent to the agent; accepts a previous Shortcut result.
- `Attachments: [IntentFile]?` — optional files, images or videos; supported UTIs include
  `public.image`, `public.movie` and `public.data`; accepts a previous action result.
- `Session: SessionEntity?` — optional existing session.
- `Model: ModelSelectionEntity?` — optional model/model-group selection.
- `Wait for Result: Bool` — default false. Set true when later Shortcut actions need the completed
  response; false starts asynchronously and returns session information.
- `Send Notifications: Bool` — default true.

`openAppWhenRun` is false. Its parameter summary is `Send <Prompt> to Minis`.

## Other chat/session actions

### Ask Minis

`Prompt: String` plus optional `Session: SessionEntity`. `openAppWhenRun` is true and the app
opens on the conversation.

### Follow Up Session

Required `Session: SessionEntity`, `Prompt: String`, optional attachments, `Wait for Result`
defaulting to false, and `Send Notifications` defaulting to true.

### Quick Task

`Task: QuickTask` plus optional attachments, model, wait and notifications. The current enum
cases are `analyzeSleep`, `healthReport`, `checkWeather`, `morningBriefing`, `checkCalendar`,
`takePhoto`, `setAlarm` and `controlHome`.

### Session management

- **Get Session Status** → `GetSessionStatusIntent`; `Session ID: String`; returns session ID,
  title, model, running state, latest message, latest tool and update time.
- **List Sessions** → `ListSessionsIntent`; no parameters; returns titles, relative age and opaque
  session IDs as text.
- **Open Session** → `OpenSessionIntent`; `Session: SessionEntity`; opens a selected session.
- **Retry Run** → `RetryRunIntent`; session, message, optional replacement attachments, wait and
  notifications; not registered in the provider as noted above.

## Serialized AppIntent descriptors

The OpenMinis source documents the intent types and parameters, but does not publish the signing
TeamIdentifier used in a serialized Shortcut plist. Do not invent that field. For an import-ready
plist, obtain an iOS-exported Shortcut containing the Minis action and mirror its complete
`AppIntentDescriptor`, or let the user connect the action manually in Shortcuts after import. The
bundle identifier alone is not sufficient evidence for a complete descriptor.

## Authoring guidance

- Treat these as optional third-party actions. The OpenMinis app must be installed on the target
  iPhone/iPad.
- Prefer **Send Prompt** for headless automations and **Ask Minis** when the app should open.
- Set **Wait for Result** deliberately when chaining a response into later actions.
- Keep attachments limited to the files required for the task and keep secrets out of prompts.
- macOS can validate/sign the plist, but that does not prove the iOS app action is installed or
  executable on the target device.
