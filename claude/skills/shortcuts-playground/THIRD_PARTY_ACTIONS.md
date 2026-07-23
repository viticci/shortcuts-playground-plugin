# Third-Party Actions Reference

This file lists third-party actions discovered from:
- macOS Shortcuts ToolKit database (installed apps)
- Local shortcut backup exports

Installed third-party actions (ToolKit): 11

## Third-Party Actions (ToolKit)
- `io.tailscale.ipn.macsys.ConnectIntent`
- `io.tailscale.ipn.macsys.DeviceAppEntity`
- `io.tailscale.ipn.macsys.DisconnectIntent`
- `io.tailscale.ipn.macsys.PingAppIntent`
- `io.tailscale.ipn.macsys.ProfileAppEntity`
- `io.tailscale.ipn.macsys.SetDNSAppIntent`
- `io.tailscale.ipn.macsys.StopUsingExitNodeIntent`
- `io.tailscale.ipn.macsys.SwitchProfileIntent`
- `io.tailscale.ipn.macsys.TaildropAppIntent`
- `io.tailscale.ipn.macsys.ToggleAppIntent`
- `is.workflow.actions.lightroom.import`

Third-party actions referenced in backups: 49

## Third-Party Actions (Backups)
- `betamagic.News-Explorer.mobile.ArticleBySelection`
- `betamagic.News-Explorer.mobile.ArticleEntity`
- `co.montanafloss.Shareshot.FrameScreenshotsIntent`
- `co.zottmann.ActionsForObsidian.CreateNote`
- `co.zottmann.ActionsForObsidian.GetNoteLink`
- `co.zottmann.ActionsForObsidian.SetNoteProperties`
- `com.agiletortoise.Drafts-OSX.CaptureIntent`
- `com.alexhay.ToolboxProForShortcuts.FindAlbumsIntent`
- `com.alexhay.ToolboxProForShortcuts.FindSongsIntent`
- `com.alexhay.ToolboxProForShortcuts.PlayMusicIntent`
- `com.alexhay.nautomate.AddValuesToDatabaseIntent`
- `com.alexhay.nautomate.CreateBookmarkBlockIntent`
- `com.alexhay.nautomate.CreateDividerBlockIntent`
- `com.alexhay.nautomate.CreateListBlockIntent`
- `com.alexhay.nautomate.CreateSmartBlocksFromTextIntent`
- `com.alexhay.nautomate.CreateTextBlockIntent`
- `com.culturedcode.ThingsMac.TAIAddTodo2`
- `com.culturedcode.ThingsMac.TAIItemEntity`
- `com.finnvoorhees.ShortcutButtons.NewButtonForShortcutIntent`
- `com.google.gemini.TypeToGeminiIntent`
- `com.gtrigonakis.TextWorkflow.TransformTextIntent`
- `com.gtrigonakis.TextWorkflowIOS.TransformTextIntent`
- `com.joehribar.toggl.StopTimeEntryIntent`
- `com.lireapp.smilingAlpaca.LIREGetArticleIdentifiersIntent`
- `com.lireapp.smilingAlpaca.LIREGetArticlePropertyIntent`
- `com.lireapp.smilingAlpaca.LIREGetCurrentArticleIdentifierIntent`
- `com.ngocluu.goodlinks.AddLinkIntent`
- `com.ngocluu.goodlinks.AddTags`
- `com.ngocluu.goodlinks.GetCurrentLink`
- `com.ngocluu.goodlinks.GetCurrentSelection`
- `com.ngocluu.goodlinks.GetTagsIntent`
- `com.ngocluu.goodlinks.HighlightEntity`
- `com.ngocluu.goodlinks.LinkEntity`
- `com.ngocluu.goodlinks.OpenHighlight`
- `com.ngocluu.goodlinks.OpenLinkIntent`
- `com.openai.chat.OpenVoiceModeIntent`
- `com.sindresorhus.AI-Actions.AskClaudeIntent`
- `com.sindresorhus.Actions.GenerateUUIDIntent`
- `com.sindresorhus.Actions.GetAudioPlaybackDestinationIntent`
- `com.sindresorhus.Actions.GetFilePathIntent`
- `com.sindresorhus.Actions.GetTitleOfURLIntent`
- `com.sindresorhus.Actions.TruncateNumber`
- `com.sindresorhus.Shortcutie.SetDefaultSoundDevice`
- `com.todoist.ios.OpenRambleAppIntent`
- `dk.simonbs.Jayson.ViewJSONIntent`
- `net.matrixteo.app.Collections.IntentsAddArrayValue`
- `net.matrixteo.app.Collections.IntentsAddDocument`
- `net.matrixteo.app.Collections.IntentsDocumentEntity`
- `net.matrixteo.app.Collections.IntentsUpdateValue`

Notes:
- Backup-only entries may come from apps not installed on this Mac.
- WF-style third-party actions can still use the `is.workflow.actions.*` prefix (e.g., Lightroom).

## Parameter-level ground truth (opt-in)

The lists above name *which* third-party actions exist, but not how to *call* them: the exact parameter keys, their types, and whether they are required. Naming an action is not enough to encode it — a wrong parameter key silently produces a broken action, and that ground truth cannot live in a static snapshot because it depends on the third-party apps a given user has installed.

Fill it in on demand with the bundled extractor. It is **opt-in and local**: it reads each installed app's declared App Intents schema at `<App>.app/Contents/Resources/Metadata.appintents/extract.actionsdata`, makes no network calls, and is not part of the normal validation path.

```bash
# Print a catalog for every installed third-party app…
"$CLAUDE_PLUGIN_ROOT/bin/extract-appintents"
# …or capture one app's actions:
"$CLAUDE_PLUGIN_ROOT/bin/extract-appintents" --app /Applications/PastePal.app --out /tmp/appintents.json
```

Each entry is keyed by the fully-qualified action identifier — the exact string that goes in `WFWorkflowActionIdentifier` — and carries what an `AppIntentDescriptor` needs:

```jsonc
"com.onmyway133.PastePal.AddItemIntent": {
  "bundleId": "com.onmyway133.PastePal",
  "teamId":   "T78DK947F2",
  "appName":  "PastePal",
  "intentId": "AddItemIntent",
  "parameters": [
    { "name": "text",      "optional": false, "type": "string" },
    { "name": "imageFile", "optional": true,  "type": "file" },
    { "name": "folder",    "optional": true,  "type": "entity:Folder" },
    { "name": "name",      "optional": true,  "type": "string" }
  ]
}
```

When building a call to a third-party action, prefer a schema from this catalog over guessing: emit only the listed `name` keys, respect `optional` (a required parameter left empty stops the shortcut with an "ask" prompt), and route by `type` — `string`/number primitives go in text-style parameters, `file` takes an image/file variable, `entity:*` expects one of the app's entities. The generated catalog is per-user, so it is git-ignored rather than committed.
