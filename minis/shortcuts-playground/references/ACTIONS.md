# Shortcuts Actions Reference

Complete catalog of all 365 WF*Action identifiers from the original macOS ToolKit v63 snapshot plus bundled iOS HealthKit backups. OS 27 ToolKit v78 snapshots add additional identifiers to the packaged allowlist; only the v78 actions with inspected metadata are summarized here.

> Note: In ToolKit SQLite `Tools`, four control-flow actions are not represented as normal tools:
> `is.workflow.actions.conditional`, `is.workflow.actions.repeat.count`,
> `is.workflow.actions.repeat.each`, and `is.workflow.actions.choosefrommenu`.
> They are still valid and are handled explicitly by this skill/validator.

## Identifier Mapping Rules

### Standard Mapping
Class `WF<Name>Action` maps to `is.workflow.actions.<lowercasename>`

Example: `WFShowResultAction` → `is.workflow.actions.showresult`

### Irregular Mappings

Some actions have non-standard mappings:

| Class Name | Identifier |
|------------|-----------|
| `WFRepeatAction` | `is.workflow.actions.repeat.count` |
| `WFForEachRepeatAction` | `is.workflow.actions.repeat.each` |
| `WFFiniteRepeatAction` | `is.workflow.actions.repeat.count` |
| `WFAskForInputAction` | `is.workflow.actions.ask` |
| `WFTextAction` | `is.workflow.actions.gettext` |
| `WFConditionalAction` | `is.workflow.actions.conditional` |
| `WFChooseFromMenuAction` | `is.workflow.actions.choosefrommenu` |
| `WFGetFileAction` | `is.workflow.actions.documentpicker.open` |
| `WFSelectFilesAction` | `is.workflow.actions.documentpicker.open` |
| `WFSaveFileAction` | `is.workflow.actions.documentpicker.save` |
| `WFGetCurrentWeatherConditionsAction` | `is.workflow.actions.weather.currentconditions` |
| `WFGetWeatherForecastAction` | `is.workflow.actions.weather.forecast` |
| `WFContentItemFilterAction` | `is.workflow.actions.filter.contentitems` |
| `WFGetUpcomingCalendarItemsAction` | `is.workflow.actions.getupcomingevents` |
| `WFAppendFileAction` | `is.workflow.actions.file.append` (was `appendfile` in older versions) |

---

## Actions by Category

### OS 27 ToolKit v78 Additions

These classic/WF-namespace identifiers are present in local OS 27 ToolKit v78 databases. They are allowlisted for validation only when targeting OS 27+ or `latest`. `Add Item to List` serialization is verified from Federico's macOS 27 sample; Stored Content, Get What's On Screen, and VPN fields have targeted ToolKit-derived validation. Picker-backed values such as VPN selection and iOS workout type/goal payloads still need exported samples before relying on rich generated payloads.

| Identifier | Display Name | Observed Parameter Keys |
|------------|--------------|-------------------------|
| `is.workflow.actions.additemtolist` | Add Item to List | `WFListVariable`, `WFListItem`, `WFInsertPosition`, `WFItemIndex` |
| `is.workflow.actions.deletestoredcontent` | Delete Stored Content | `WFStoredContentGlobalValue`, `WFStoredContentKey` |
| `is.workflow.actions.filter.vpns` | Find VPNs | `WFContentItemFilter`, `WFCompoundType`, `WFContentItemInputParameter`, `WFContentItemSortProperty`, `WFContentItemSortOrder`, `WFContentItemLimitEnabled`, `WFContentItemLimitNumber` |
| `is.workflow.actions.getonscreencontext` | Get What's On Screen | `WFOnScreenContextScope`, `WFOnScreenContextResultType`, `WFOnScreenContextLimitEnabled`, `WFOnScreenContextLimit` |
| `is.workflow.actions.getonscreencontent` | Get What's On Screen | Deprecated in v78; use `is.workflow.actions.getonscreencontext` |
| `is.workflow.actions.getselectedtext` | Get Selected Text | none |
| `is.workflow.actions.getstoredcontent` | Get Stored Content | `WFStoredContentGlobalValue`, `WFStoredContentKey` |
| `is.workflow.actions.setstoredcontent` | Store Content | `WFInput`, `WFStoredContentGlobalValue`, `WFStoredContentKey` |
| `is.workflow.actions.vpn.get` | Get Current VPN | none |
| `is.workflow.actions.vpn.set` | Set VPN | `WFVPNOperation`, `WFOnDemandValue`, `WFVPN` |
| `is.workflow.actions.workout.end` | End Workout | `IntentAppDefinition` (iOS/iPadOS 27 only) |
| `is.workflow.actions.workout.start` | Start Workout | `IntentAppDefinition`, `workoutName`, `isOpenEnded`, `WorkoutGoal` (iOS/iPadOS 27 only) |

#### Add Item to List

`is.workflow.actions.additemtolist` appends to the end of a list by default when `WFInsertPosition` is omitted.

| Behavior | Required Parameters |
|----------|---------------------|
| Add to end | `WFListVariable`, `WFListItem` |
| Add to beginning | `WFListVariable`, `WFListItem`, `WFInsertPosition = "Beginning"` |
| Add at index | `WFListVariable`, `WFListItem`, `WFInsertPosition = "Index"`, `WFItemIndex` |

`WFListVariable` is a `WFTextTokenAttachment` pointing at a list output or named variable. `WFListItem` can be a literal value or `WFTextTokenString`.

`WFInsertPosition` accepts exactly `Beginning`, `End`, or `Index`. Include `WFItemIndex` only when `WFInsertPosition = "Index"`, and use a 1-based integer (`1` or greater).

#### Stored Content

`Store Content`, `Get Stored Content`, and `Delete Stored Content` share a string key in `WFStoredContentKey`. The key must be non-empty. `WFStoredContentGlobalValue` is a boolean; omit it or set it to `false` for shortcut-scoped content, and set it to `true` only when intentionally using the global/iCloud stored-content namespace. This boolean is unrelated to editor rendering; it does not fix an empty `Content` field.

`Store Content` also requires explicit `WFInput` pointing at the content to save. Apple saves a manually connected Store Content input as `WFTextTokenString` with a single `￼` placeholder and an `attachmentsByRange` entry for the source output. Do **not** use a bare `WFTextTokenAttachment` or a wrapped `Type = Variable` attachment for this field; those sign and import, but render as an empty `Content` placeholder in Shortcuts. If `shortcuts sign` rejects this correct XML shape with a format error, use `plutil -convert binary1` on the final `.shortcut` copy and sign that; the bundled signer wrapper retries this automatically.

| Action | Required Parameters |
|--------|---------------------|
| `is.workflow.actions.setstoredcontent` | `WFInput`, `WFStoredContentKey` |
| `is.workflow.actions.getstoredcontent` | `WFStoredContentKey` |
| `is.workflow.actions.deletestoredcontent` | `WFStoredContentKey` |

#### VPN Actions

`is.workflow.actions.vpn.get` returns the current VPN and takes no parameters. Prefer this classic WF action for "Get Current VPN" output. The similarly named AppIntent entity row `com.apple.systempreferences.CurrentlyConnectedVPN` is filter/query metadata, not the no-parameter current-VPN action. `is.workflow.actions.filter.vpns` and `is.workflow.actions.vpn.set` are OS 27 ToolKit v78 rows available on macOS and iOS/iPadOS targets.

For `Find VPNs`, ToolKit exposes VPN content item properties `Name`, `Server Address`, `App`, `Is Connected`, and `Is On Demand Enabled`. The verified sort properties are `Name`, `Server Address`, and `Random`. Prefer ToolKit enum IDs for `WFCompoundType`: `0` means **Any** and `1` means **All**. The validator accepts the display labels `Any`/`All` as compatibility aliases, but generated shortcuts should use `0`/`1`. If `WFContentItemLimitEnabled` is `true`, include a positive numeric `WFContentItemLimitNumber`.

| Action | Required/Important Parameters |
|--------|-------------------------------|
| `is.workflow.actions.filter.vpns` | `WFContentItemFilter` for predicates, optional `WFContentItemSortProperty`, `WFContentItemSortOrder`, `WFContentItemLimitEnabled`, `WFContentItemLimitNumber`, `WFCompoundType`, `WFContentItemInputParameter = "Library"` |
| `is.workflow.actions.vpn.get` | none |
| `is.workflow.actions.vpn.set` | `WFVPNOperation`, `WFVPN`; `WFOnDemandValue` is required when `WFVPNOperation = "Set On Demand"` |

`WFVPNOperation` accepts exactly `Connect`, `Disconnect`, `Toggle`, `Set On Demand`, or `Toggle On Demand`. `WFOnDemandValue`, when present, must be a boolean. Treat `WFVPN` as a picker/token state for the selected VPN configuration; do not leave it empty.

#### iOS Workout Controls

`is.workflow.actions.workout.start` and `is.workflow.actions.workout.end` are present only in the iOS/iPadOS 27 Simulator ToolKit snapshot. Validate them with `--target-platform ios`; the default macOS target intentionally rejects them. Treat the listed ToolKit keys as metadata until an exported iPhone/iPad shortcut confirms picker value serialization for `workoutName` and `WorkoutGoal`.

#### Get What's On Screen

Use the OS 27 ToolKit v78 parameterized row `is.workflow.actions.getonscreencontext` for new shortcuts. `is.workflow.actions.getonscreencontent` is still present in the ToolKit snapshot but is deprecated by v78 and has no observed parameter schema in the current catalog.

| Parameter | Requirement |
|-----------|-------------|
| `WFOnScreenContextScope` | Optional. If present, use exactly `All Visible` or `Focused App Only`. |
| `WFOnScreenContextResultType` | Optional string. Leave omitted unless matching an exported sample or a known Shortcuts UI value. |
| `WFOnScreenContextLimitEnabled` | Optional boolean. Use `true` only when intentionally limiting the number of returned items. |
| `WFOnScreenContextLimit` | Required when `WFOnScreenContextLimitEnabled` is `true`; must be a positive number. Omit when limit is disabled. |

#### OS 26 to 27 Updated Parameters

These parameter additions were cross-checked against the Automators OS 26 to 27 thread and local ToolKit v78 metadata. Treat AppIntent-style WF-namespace actions (`appendnote`, `scanbarcode`, `extracttextfromimage`) as ToolKit-backed AppIntents even though their identifiers begin with `is.workflow.actions.`. The validator rejects these parameter keys when targeting macOS 26 or older even if the action identifier itself is available on that target.

| Identifier | Display Name | New/Updated Parameters | Notes |
|------------|--------------|------------------------|-------|
| `is.workflow.actions.addnewreminder` | New Reminder | `WFUrgent` | Boolean urgent flag reported in the OS 26.4 delta and present in ToolKit v78. |
| `is.workflow.actions.appendnote` | Append to Note | `section` (**Section**), `ignoreWhitespace` (**Ignore Whitespace**), `interpretAsMarkdown` (**Interpret as Markdown**); important existing key: `operation` | `section` is the section title/heading; `operation` accepts `append` or `prepend`; the booleans are `On`/`Off` UI toggles. |
| `com.apple.mobilenotes.SharingExtension` | Create Note | `interpretAsMarkdown` (**Interpret as Markdown**) | This ToolKit row uses `contents` for the note body; `com.apple.Notes.CreateNoteIntent` did not expose the markdown toggle in local macOS 27 v78. |
| `is.workflow.actions.askllm` | Use Model | `WFAllowWebSearch`, `FollowUp` | `WFAllowWebSearch` is the **Use Broad World Knowledge** toggle; `FollowUp` is the **Follow Up** toggle. Both are plist booleans. |
| `is.workflow.actions.searchlocalbusinesses` | Find Places | `WFSearchSortOrder` | ToolKit enum values: `Distance` or `Relevance`. |
| `is.workflow.actions.getdirections` | Open Directions | `WFDestination` | ToolKit notes that multi-stop trips are only supported by Apple Maps; exported multi-stop samples are still needed before generating complex destination lists. |
| `is.workflow.actions.getdistance` | Get Distance | `WFAvoidTolls` (**Avoid Tolls**), `WFAvoidHighways` (**Avoid Highways**), `WFDistanceUnit`, `Accuracy` | Boolean route options. Route modes: `Driving`, `Walking`, `Biking`, `Direct`. Distance units: `Miles` or `Kilometers`. Accuracy values: `Best`, `NearestTenMeters`, `HundredMeters`, `Kilometer`, `ThreeKilometers`. |
| `is.workflow.actions.gettraveltime` | Get Travel Time | `WFAvoidTolls` (**Avoid Tolls**), `WFAvoidHighways` (**Avoid Highways**) | Boolean route options. Route modes: `Driving`, `Walking`, `Biking`, `Transit`. |
| `is.workflow.actions.hide.app` | Hide App | `WFAppsExcept` | Used when `WFHideAppMode = "All Apps"` to keep listed apps open. |
| `is.workflow.actions.quit.app` | Quit App | `WFAppsExcept`, `WFAskToSaveChanges` | `WFAppsExcept` is used when `WFQuitAppMode = "All Apps"` to keep listed apps open. `WFAskToSaveChanges`, when present, must be a boolean. |
| `is.workflow.actions.scanbarcode` | Scan QR or Barcode | `imageFile` | ToolKit-backed AppIntent parameter displayed as **Image** for scanning an input image file. |
| `is.workflow.actions.extracttextfromimage` | Extract from Image | `imageFile` | ToolKit v78 exposes this as the primary image input. Older exported shortcuts may still use `WFImage` or `WFInput`. |
| `com.apple.Safari.CreateNewTabGroup` / `com.apple.mobilesafari.CreateNewTabGroup` | Create Tab Group | `contents` | Use `com.apple.Safari.*` on macOS and `com.apple.mobilesafari.*` on iOS/iPadOS. Accepts URLs or existing Safari tab entities to seed the new tab group. |

OS 27 boolean toggles must be real plist booleans, not strings: `ignoreWhitespace`, `interpretAsMarkdown`, `WFAllowWebSearch`, `FollowUp`, `WFAvoidTolls`, and `WFAvoidHighways`. `WFGetDirectionsActionMode` accepts `Driving`, `Walking`, `Biking`, or `Direct` for Get Distance, and `Driving`, `Walking`, `Biking`, or `Transit` for Get Travel Time. `WFDistanceUnit` accepts `Miles` or `Kilometers`; `Accuracy` accepts `Best`, `NearestTenMeters`, `HundredMeters`, `Kilometer`, or `ThreeKilometers`. For Hide/Quit App, `WFHideAppMode` / `WFQuitAppMode` accept `App` or `All Apps`; `WFApp` is required when the mode is `App`, `WFAppsExcept` should be omitted unless it contains at least one app to keep open, and `WFAskToSaveChanges` must be boolean when present. `Scan QR or Barcode` requires `imageFile` as a non-empty token attachment to an image/file output. `Create Tab Group` `contents` must be omitted or non-empty.

#### OS 26 to 27 Display Name Changes

| Identifier | Old Name | New Name |
|------------|----------|----------|
| `is.workflow.actions.extracttextfromimage` | Extract Text from Image | Extract from Image (`imageFile` in ToolKit v78) |
| `com.apple.Photos.PhotosSearchAssistantIntent` | Search Photos | Search |
| `com.apple.TVRemoteUIService.ToggleSystemAppearanceIntent` | Set Light/Dark Mode | Set Appearance on Apple TV |

#### OS 26.4 Choose from List Compatibility

The linked Automators OS 26.2 to 26.4 delta notes that **Choose from List** works again with more input types, including dictionaries and named text. Prefer direct Dictionary/List/Text inputs over vCard/VCF workarounds unless the user explicitly asks for contact-card formatting. Contact email and phone-number list values remain macOS-only in the reported behavior.

`WFChooseFromListActionSelectMultiple` and `WFChooseFromListActionSelectAll` must be plist booleans. Only set **Select All Initially** when **Select Multiple** is also enabled.

#### OS 18 to 26.1 Automators Follow-up

The earlier Automators iOS 18 to OS 26.1 thread lists a few rows that are also visible in the local ToolKit v78 metadata. Treat these as OS 27-era authoring metadata in this package unless you have an exported shortcut from the older OS that proves the same plist shape.

| Action | Identifier | Confirmed Metadata |
|--------|------------|--------------------|
| Open App | `is.workflow.actions.openapp` | New `WFWindowingFormat` parameter for **Window Location & Size**. Valid values: `Full Screen`, `Left`, `Right`, `Top`, `Bottom`, `Top Leading`, `Top Trailing`, `Bottom Leading`, `Bottom Trailing`, `Left Third`, `Middle Third`, `Right Third`. |
| Search in Files (iOS) | unresolved | The thread describes "Search for a file or folder", but no literal `Search in Files` row appears in the local macOS 27 or hydrated iOS 27 Simulator v78 ToolKit databases. The closest current classic row is `is.workflow.actions.filter.files` (`Filter Files`) with `WFContentItemFilter`, sort, limit, compound, and file input parameters. Do not invent a separate Search in Files payload until an exported iPhone/iPad shortcut identifies it. |

`WFWindowingFormat` is optional. If present, it must use one of the exact ToolKit enum values above; typoed values now fail validation.

### Text & Input

| Identifier | Class | Description |
|------------|-------|-------------|
| `gettext` | WFTextAction | Create a text value |
| `ask` | WFAskForInputAction | Ask user for input |
| `askllm` | WFAskLLMAction | Use AI model (Apple Intelligence) |
| `comment` | WFCommentAction | Add a comment (no effect) |
| `dictatetext` | WFDictateTextAction | Dictate text |
| `showresult` | WFShowResultAction | Display result to user |
| `alert` | WFAlertAction | Show alert dialog |
| `notification` | WFNotificationAction | Send notification |
| `speaktext` | WFSpeakTextAction | Speak text aloud |
| `detectlanguage` | WFDetectLanguageAction | Detect language |

### Variables

| Identifier | Class | Description |
|------------|-------|-------------|
| `setvariable` | WFSetVariableAction | Set a variable |
| `getvariable` | WFGetVariableAction | Get a variable |
| `appendvariable` | WFAppendVariableAction | Append to variable |
| `nothing` | WFNothingAction | Do nothing (pass-through) |

### Control Flow

| Identifier | Class | Description |
|------------|-------|-------------|
| `repeat.count` | WFRepeatAction | Repeat N times |
| `repeat.each` | WFForEachRepeatAction | Repeat for each item |
| `conditional` | WFConditionalAction | If/Otherwise/Otherwise If |
| `choosefrommenu` | WFChooseFromMenuAction | Menu with cases |
| `choosefromlist` | WFChooseFromListAction | Choose from list |
| `exit` | WFExitAction | Exit shortcut |
| `output` | WFOutputAction | Set output |

### Files & Documents

| Identifier | Class | Description |
|------------|-------|-------------|
| `file` | WFFileAction | Create file reference |
| `documentpicker.open` | WFSelectFilesAction | Open file picker |
| `documentpicker.save` | WFSaveFileAction | Save file |
| `setitemname` | WFSetItemNameAction | Set Name; produces a renamed item object |
| `file.rename` | WFRenameFileAction | Rename File; mutates the original file in place |
| `file.append` | WFAppendFileAction | Append to text file (was `appendfile` in older versions) |

### Web & URLs

| Identifier | Class | Description |
|------------|-------|-------------|
| `url` | WFURLAction | Create URL |
| `downloadurl` | WFDownloadURLAction | Get contents of URL |
| `openurl` | WFOpenURLAction | Open URL |
| `openxcallbackurl` | WFOpenXCallbackURLAction | Open x-callback-url (see `URL_SCHEMES.md`) |
| `urlencode` | WFURLEncodeAction | URL encode |
| `searchweb` | WFSearchWebAction | Search web |

### Apps & System

| Identifier | Class | Description |
|------------|-------|-------------|
| `openapp` | WFOpenAppAction | Open app |
| `getcurrentapp` | WFGetCurrentAppAction | Get current app |
| `runworkflow` | WFRunWorkflowAction | Run another shortcut |
| `runshellscript` | WFRunShellScriptAction | Run shell script |
| `getdevicedetails` | WFGetDeviceDetailsAction | Get device info |
| `getclipboard` | WFGetClipboardAction | Get clipboard |
| `setclipboard` | WFSetClipboardAction | Set clipboard |

### Lists & Data

| Identifier | Class | Description |
|------------|-------|-------------|
| `list` | WFListAction | Create list |
| `dictionary` | WFDictionaryAction | Create dictionary |
| `getitemfromlist` | WFGetItemFromListAction | Get item from list |
| `count` | WFCountAction | Count items |

### Numbers & Math

| Identifier | Class | Description |
|------------|-------|-------------|
| `number` | WFNumberAction | Create number |

### Date & Time

| Identifier | Class | Description |
|------------|-------|-------------|
| `date` | WFDateAction | Create date |
| `adjustdate` | WFAdjustDateAction | Adjust date |
| `converttimezone` | WFConvertTimeZoneAction | Convert timezone |
| `gettimebetweendates` | WFTimeUntilAction | Get time between dates |
| `delay` | WFDelayAction | Wait |
| `waittoreturn` | WFWaitToReturnAction | Wait to return |

#### Get Time Between Dates (`is.workflow.actions.gettimebetweendates`)

- Set `WFInput` to the target/end date as a `WFTextTokenString` placeholder.
- Set exactly one date operand: usually `WFTimeUntilFromDate`, also as a `WFTextTokenString` placeholder.
- To compare an event start date with now, add a **Date** action set to **Current Date** and reference that action output from `WFTimeUntilFromDate`. Do not put a `CurrentDate` magic token directly in `WFTimeUntilFromDate`; it imports as an empty/default date field.
- Do not use bare `WFTextTokenAttachment` for either date input. It can validate structurally but import as "First Date" / "Second Date" placeholders in Shortcuts.

### Calendar & Reminders

| Identifier | Class | Description |
|------------|-------|-------------|
| `addnewevent` | WFAddNewEventAction | Create event |
| `getupcomingevents` | WFGetUpcomingCalendarItemsAction | Get upcoming events |
| `addnewreminder` | WFAddNewReminderAction | Create reminder |

### Weather & Location

| Identifier | Class | Description |
|------------|-------|-------------|
| `weather.currentconditions` | WFGetCurrentWeatherConditionsAction | Current weather |
| `weather.forecast` | WFGetWeatherForecastAction | Weather forecast |
| `getcurrentlocation` | WFGetCurrentLocationAction | Current location |
| `location` | WFLocationAction | Create location |
| `getdirections` | WFGetDirectionsAction | Get directions |
| `getdistance` | WFGetDistanceAction | Get distance |
| `searchmaps` | WFSearchMapsAction | Search maps |

### Health

These actions are iOS/iPadOS Health actions. macOS Shortcuts can sync their plist XML, but cannot fully configure or run the Health UI. Use [HEALTHKIT.md](HEALTHKIT.md) for the verified parameter schemas.

| Identifier | Class | Description |
|------------|-------|-------------|
| `filter.health.quantity` | WFFindHealthSamplesAction | Find Health Samples |
| `properties.health.quantity` | WFGetDetailsOfHealthSampleAction | Get Details of Health Sample |
| `health.quantity.log` | WFLogHealthSampleAction | Log Health Sample |
| `health.workout.log` | WFLogWorkoutAction | Log Workout |

### Media

| Identifier | Class | Description |
|------------|-------|-------------|
| `takephoto` | WFTakePhotoAction | Take photo |
| `takevideo` | WFTakeVideoAction | Take video |
| `selectphoto` | WFSelectPhotoAction | Select photos |
| `filter.photos` | WFContentItemFilterAction | Find/filter photos (see FILTERS.md) |
| `savetocameraroll` | WFSaveToCameraRollAction | Save to camera roll |
| `deletephotos` | WFDeletePhotosAction | Delete photos (**uses `photos` param, not `WFInput`**) |
| `playmusic` | WFPlayMusicAction | Play music |
| `recordaudio` | WFRecordAudioAction | Record audio |
| `playsound` | WFPlaySoundAction | Play sound |

### Images

| Identifier | Class | Description |
|------------|-------|-------------|
| `overlaytext` | WFOverlayTextAction | Overlay text |
| `extracttextfromimage` | WFExtractTextFromImageAction | OCR |

### PDF

| Identifier | Class | Description |
|------------|-------|-------------|
| `makepdf` | WFMakePDFAction | Create PDF |
| `splitpdf` | WFSplitPDFAction | Split PDF |
| `compresspdf` | WFCompressPDFAction | Compress PDF |
| `gettextfrompdf` | WFGetTextFromPDFAction | Extract text from PDF |
| `makeimagefrompdfpage` | WFMakeImageFromPDFPageAction | PDF page to image |

### Sharing & Communication

| Identifier | Class | Description |
|------------|-------|-------------|
| `share` | WFShareAction | Share |
| `sendmessage` | WFSendMessageAction | Send message |
| `sendemail` | WFSendEmailAction | Send email |
| `contacts` | WFContactsAction | Get contacts |
| `selectcontacts` | WFSelectContactsAction | Select contacts |

### Settings

| Identifier | Class | Description |
|------------|-------|-------------|
| `setvolume` | WFSetVolumeAction | Set volume |

---
## Complete Identifier List

All 365 action identifiers (prefix `is.workflow.actions.` omitted):

```
addframetogif, addmusictoupnext, addnewcalendar, addnewcontact, addnewevent
addnewreminder, addquickreminder, address, addtoplaylist, adjustdate
airdropdocument, airplanemode.set, alert, announcenotifications.set, appearance
appendnote, appendvariable, ask, askllm, avairyeditphoto
base64encode, bluetooth.set, calculateexpression, cellulardata.set, choosefromlist
choosefrommenu, clearupnext, comment, compresspdf, conditional
connecttoservers, contacts, converttimezone, correctspelling, count
createplaylist, date, delay, deletephotos, deskconnect.send
detect.address, detect.contacts, detect.date, detect.dictionary, detect.emailaddress
detect.images, detect.link, detect.number, detect.phonenumber, detect.text
detectlanguage, dictatetext, dictionary, dismisssiri, display.always-on.set
displaysleep, dnd.getfocus, dnd.set, documentpicker.open, documentpicker.save
downloadurl, dropbox.appendfile, dropbox.open, dropbox.savefile, ejectdisk
email, encodemedia, evernote.append, evernote.delete, evernote.get
evernote.getlink, evernote.new, exit, exportsong, extracttextfromimage
file, file.append, file.createfolder, file.delete, file.getfoldercontents
file.getlink, file.label, file.move, file.rename, file.reveal
file.select, filter.apps, filter.articles, filter.calendarevents, filter.contacts
filter.displays, filter.eventattendees, filter.files, filter.health.quantity
filter.images, filter.locations, filter.music, filter.notes, filter.photos
filter.reminders, filter.windows
finder.getselectedfiles, flashlight, format.date, format.filesize, format.number
generatebarcode, get.playlist, getarticle, getbatterylevel, getclassaction
getclipboard, getcurrentapp, getcurrentlocation, getcurrentsong, getdevicedetails
getdirections, getdistance, getepisodesforpodcast, getframesfromimage, gethalfwaypoint
gethomeaccessorystate, gethtmlfromrichtext, getipaddress, getitemfromlist, getitemname
getitemtype, getlastphoto, getlastscreenshot, getlastvideo, getlatestbursts
getlatestlivephotos, getlatestphotoimport, getmapslink, getmarkdownfromrichtext, getmyworkflows
getnameofemoji, getonscreencontent, getparentdirectory, getparkedcarlocation, getpodcastsfromlibrary
getrichtextfromhtml, getrichtextfrommarkdown, gettext, gettextfrompdf, gettimebetweendates
gettraveltime, gettypeaction, getupcomingevents, getupcomingreminders, geturlcomponent
getvalueforkey, getvariable, getwebpagecontents, getwifi, giphy
goodreader.open, handoff, handoffplayback, hash, health.quantity.log
health.workout.log, hide.app, homeaccessory, image.combine, image.convert
image.convert.finder, image.crop, image.flip, image.mask, image.removebackground
image.resize, image.rotate, imgur.upload, importaudiofiles, input
instapaper.add, instapaper.get, intercom, list, listeningmode.set
location, lock.app, lockscreen, logout, lowpowermode.set
makediskimage, makegif, makeimagefrompdfpage, makeimagefromrichtext, makepdf
makespokenaudiofromtext, makevideofromgif, makezip, math, measurement.convert
measurement.create, mountdiskimage, movewindow, nightshift.set, nothing
notification, number, number.random, openapp, openin
openpasswords, openurl, openxcallbackurl, orientationlock.set, output
overlayimageonimage, overlaytext, pausemusic, personalhotspot.password.get, personalhotspot.password.set
personalhotspot.set, phonenumber, photos.createalbum, pinboard.add, pinboard.get
playmusic, playpodcast, playsound, pocket.add, pocket.get
podcasts.subscribe, posters.get, posters.switch, postonfacebook, previewdocument
print, properties.appearance, properties.appstore, properties.articles, properties.calendarevents
properties.contacts, properties.eventattendees, properties.files, properties.health.quantity
properties.images, properties.itunesartist, properties.itunesstore, properties.locations
properties.music, properties.parkedcar, properties.podcast, properties.podcastshow
properties.reminders, properties.ridestatus, properties.safariwebpage, properties.shazam
properties.trello, properties.ulysses.sheet, properties.weather.conditions, properties.workflow, quit.app
readinglist, reboot, recordaudio, reminders.showlist, removeevents
removefromalbum, removereminders, repeat.count, repeat.each, resizewindow
returntohomescreen, ride.requestride, round, rss, rss.extract
runapplescript, runextension, runjavascriptforautomation, runjavascriptonwebpage, runshellscript
runsshscript, runworkflow, safari.geturl, savetocameraroll, scanbarcode
searchappstore, searchitunes, searchlocalbusinesses, searchmaps, searchpodcasts
searchweb, seek, selectcontacts, selectemail, selectphone
selectphoto, sendemail, sendmessage, setairdropreceiving, setbrightness
setclipboard, setitemname, setparkedcar, setplaybackdestination, setters.calendarevents
setters.contacts, setters.reminders, setvalueforkey, setvariable, setvolume
share, shazamMedia, showdefinition, showinblindsquare, showincalendar
showinstore, shownote, showresult, showwebpage, silenceunknowncallers.set
skipback, skipforward, sleep, speaktext, splitpdf
splitscreen, spotlightsearch, stagemanager.set, startscreensaver, statistics
takephoto, takescreenshot, takevideo, text.changecase, text.combine
text.match, text.match.getgroup, text.replace, text.split, text.translate
text.trimwhitespace, timer.start, todoist.add, trello.add.board, trello.add.card
trello.add.list, trello.get, trimvideo, truetone.set, tumblr.post
tweet, unzip, url, url.expand, url.getheaders
urlencode, venmo.pay, venmo.request, vibrate, viewresult
vpn.set, waittoreturn, wallpaper.set, watchmedo, weather.currentconditions
weather.forecast, wifi.set, wordpress.post
```

---

## Common Parameter Patterns

### Text Parameters
```xml
<key>WFTextActionText</key>
<string>Your text here</string>
```

### Variable Reference Parameters
```xml
<key>Text</key>
<dict>
    <key>Value</key>
    <dict>
        <key>attachmentsByRange</key>
        <dict>
            <key>{0, 1}</key>
            <dict>
                <key>OutputUUID</key>
                <string>SOURCE-UUID</string>
                <key>OutputName</key>
                <string>Text</string>
                <key>Type</key>
                <string>ActionOutput</string>
            </dict>
        </dict>
        <key>string</key>
        <string>￼</string>
    </dict>
    <key>WFSerializationType</key>
    <string>WFTextTokenString</string>
</dict>
```

### Boolean Parameters
```xml
<key>WFSomeOption</key>
<true/>
```

### Number Parameters
```xml
<key>WFRepeatCount</key>
<integer>5</integer>
```

### Enum Parameters
```xml
<key>WFHTTPMethod</key>
<string>GET</string>
```

---

## Action-Specific Parameters

### Get Contents of URL (`is.workflow.actions.downloadurl`)

The `downloadurl` action (WFDownloadURLAction) makes HTTP requests. It supports various methods, headers, and body types.

#### Basic Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `UUID` | String | Unique identifier for variable references |
| `WFURL` | Variable ref or string | The URL to request |
| `WFHTTPMethod` | String | HTTP method: `GET`, `POST`, `PUT`, `PATCH`, `DELETE` |
| `WFHTTPBodyType` | String | Body type: `JSON`, `Form`, `File` |

#### Headers (`WFHTTPHeaders`)

Headers use `WFDictionaryFieldValue` serialization with key-value items:

```xml
<key>WFHTTPHeaders</key>
<dict>
    <key>Value</key>
    <dict>
        <key>WFDictionaryFieldValueItems</key>
        <array>
            <dict>
                <key>WFItemType</key>
                <integer>0</integer>
                <key>WFKey</key>
                <dict>
                    <key>Value</key>
                    <dict>
                        <key>string</key>
                        <string>Content-Type</string>
                    </dict>
                    <key>WFSerializationType</key>
                    <string>WFTextTokenString</string>
                </dict>
                <key>WFValue</key>
                <dict>
                    <key>Value</key>
                    <dict>
                        <key>string</key>
                        <string>application/json</string>
                    </dict>
                    <key>WFSerializationType</key>
                    <string>WFTextTokenString</string>
                </dict>
            </dict>
        </array>
    </dict>
    <key>WFSerializationType</key>
    <string>WFDictionaryFieldValue</string>
</dict>
```

#### JSON Body (`WFJSONValues`)

When `WFHTTPBodyType` is `JSON`, use `WFJSONValues` for key-value pairs:

```xml
<key>WFJSONValues</key>
<dict>
    <key>Value</key>
    <dict>
        <key>WFDictionaryFieldValueItems</key>
        <array>
            <dict>
                <key>WFItemType</key>
                <integer>0</integer>
                <key>WFKey</key>
                <dict>
                    <key>Value</key>
                    <dict>
                        <key>string</key>
                        <string>prompt</string>
                    </dict>
                    <key>WFSerializationType</key>
                    <string>WFTextTokenString</string>
                </dict>
                <key>WFValue</key>
                <!-- Can be a static string or variable reference -->
                <dict>
                    <key>Value</key>
                    <dict>
                        <key>attachmentsByRange</key>
                        <dict>
                            <key>{0, 1}</key>
                            <dict>
                                <key>OutputUUID</key>
                                <string>ASK-ACTION-UUID</string>
                                <key>OutputName</key>
                                <string>Provided Input</string>
                                <key>Type</key>
                                <string>ActionOutput</string>
                            </dict>
                        </dict>
                        <key>string</key>
                        <string>￼</string>
                    </dict>
                    <key>WFSerializationType</key>
                    <string>WFTextTokenString</string>
                </dict>
            </dict>
        </array>
    </dict>
    <key>WFSerializationType</key>
    <string>WFDictionaryFieldValue</string>
</dict>
```

#### Form Body (`WFFormValues`)

When `WFHTTPBodyType` is `Form`, use `WFFormValues` (same structure as `WFJSONValues`).

#### File Body (`WFRequestVariable`)

When `WFHTTPBodyType` is `File`, use `WFRequestVariable` to reference file data:

```xml
<key>WFRequestVariable</key>
<dict>
    <key>Value</key>
    <dict>
        <key>attachmentsByRange</key>
        <dict>
            <key>{0, 1}</key>
            <dict>
                <key>OutputUUID</key>
                <string>FILE-SOURCE-UUID</string>
                <key>OutputName</key>
                <string>File</string>
                <key>Type</key>
                <string>ActionOutput</string>
            </dict>
        </dict>
        <key>string</key>
        <string>￼</string>
    </dict>
    <key>WFSerializationType</key>
    <string>WFTextTokenString</string>
</dict>
```

#### WFItemType Values

The `WFItemType` field in dictionary items indicates the value type:

| Value | Type |
|-------|------|
| 0 | Text/String |
| 1 | Number |
| 2 | Array |
| 3 | Dictionary |
| 4 | Boolean |

---

### Find Photos (`is.workflow.actions.filter.photos`)

Searches the photo library with filters. See [FILTERS.md](./FILTERS.md) for complete filter documentation.

#### Key Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `UUID` | String | Action identifier for output reference |
| `WFContentItemFilter` | Dict | Filter conditions (see FILTERS.md) |
| `WFContentItemSortProperty` | String | Sort by: `Date Taken`, `Creation Date`, etc. |
| `WFContentItemSortOrder` | String | `Latest First` or `Oldest First` |
| `WFContentItemLimitEnabled` | Boolean | Enable result limit |
| `WFContentItemLimitNumber` | Integer | Max results to return |

#### Filter Properties for Photos

| Property | Type | Notes |
|----------|------|-------|
| `Is a Screenshot` | Boolean | Use this for screenshots, NOT media_type |
| `Media Type` | Enum | ONLY: `Image`, `Video`, `Live Photo` |
| `Date Taken` | Date | Use operators 1002 (is today), 1001 (is in the last) |
| `Album` | String | Album name |
| `Is Favorite` | Boolean | Favorited photos |
| `Is Hidden` | Boolean | Hidden photos |

#### Common Mistake: Screenshot Filtering

**WRONG:** Using `Media Type` = `Screenshot` - This value is invalid!

**CORRECT:** Use `Is a Screenshot` = `true` (boolean filter)

---

### Delete Photos (`is.workflow.actions.deletephotos`)

Deletes photos from the library.

#### Critical: Parameter Key

**The parameter key is `photos` (lowercase), NOT `WFInput`!**

This is an exception to the normal pattern where most actions use `WFInput`.

#### Correct Structure

```xml
<dict>
    <key>WFWorkflowActionIdentifier</key>
    <string>is.workflow.actions.deletephotos</string>
    <key>WFWorkflowActionParameters</key>
    <dict>
        <key>UUID</key>
        <string>DELETE-UUID</string>
        <key>photos</key>  <!-- NOT WFInput! -->
        <dict>
            <key>Value</key>
            <dict>
                <key>OutputName</key>
                <string>Photos</string>
                <key>OutputUUID</key>
                <string>FIND-PHOTOS-UUID</string>
                <key>Type</key>
                <string>ActionOutput</string>
            </dict>
            <key>WFSerializationType</key>
            <string>WFTextTokenAttachment</string>
        </dict>
    </dict>
</dict>
```
