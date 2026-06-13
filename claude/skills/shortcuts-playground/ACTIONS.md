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

These classic/WF-namespace identifiers are present in local OS 27 ToolKit v78 databases. They are allowlisted for validation only when targeting OS 27+ or `latest`. `Add Item to List` serialization is verified from Federico's macOS 27 sample; the remaining new actions still need dedicated authoring samples before relying on exact parameter structure.

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

#### Add Item to List

`is.workflow.actions.additemtolist` appends to the end of a list by default when `WFInsertPosition` is omitted.

| Behavior | Required Parameters |
|----------|---------------------|
| Add to end | `WFListVariable`, `WFListItem` |
| Add to beginning | `WFListVariable`, `WFListItem`, `WFInsertPosition = "Beginning"` |
| Add at index | `WFListVariable`, `WFListItem`, `WFInsertPosition = "Index"`, `WFItemIndex` |

`WFListVariable` is a `WFTextTokenAttachment` pointing at a list output or named variable. `WFListItem` can be a literal value or `WFTextTokenString`.

#### OS 26 to 27 Updated Parameters

These parameter additions were cross-checked against the Automators OS 26 to 27 thread and local ToolKit v78 metadata. Treat AppIntent-style WF-namespace actions (`appendnote`, `scanbarcode`, `extracttextfromimage`) as ToolKit-backed AppIntents even though their identifiers begin with `is.workflow.actions.`. The validator rejects these parameter keys when targeting macOS 26 or older even if the action identifier itself is available on that target.

| Identifier | New/Updated Parameters | Notes |
|------------|------------------------|-------|
| `is.workflow.actions.appendnote` | `section`, `ignoreWhitespace`, `interpretAsMarkdown` | `section` is the section title/heading; the booleans are `On`/`Off` UI toggles. |
| `com.apple.mobilenotes.SharingExtension` | `interpretAsMarkdown` | Displayed as **Create Note**. This ToolKit row uses `contents` for the note body; `com.apple.Notes.CreateNoteIntent` did not expose the markdown toggle in local macOS 27 v78. |
| `is.workflow.actions.askllm` | `WFAllowWebSearch` | Displayed as **Use Broad World Knowledge**. Boolean toggle for web-backed model knowledge. |
| `is.workflow.actions.getdistance` | `WFAvoidTolls`, `WFAvoidHighways` | Boolean route options. Route modes: `Driving`, `Walking`, `Biking`, `Direct`. |
| `is.workflow.actions.gettraveltime` | `WFAvoidTolls`, `WFAvoidHighways` | Boolean route options. Route modes: `Driving`, `Walking`, `Biking`, `Transit`. |
| `is.workflow.actions.hide.app` | `WFAppsExcept` | Used when `WFHideAppMode = "All Apps"` to keep listed apps open. |
| `is.workflow.actions.quit.app` | `WFAppsExcept` | Used when `WFQuitAppMode = "All Apps"` to keep listed apps open. |
| `is.workflow.actions.scanbarcode` | `imageFile` | ToolKit-backed AppIntent parameter for scanning an input image file. |
| `com.apple.Safari.CreateNewTabGroup` | `contents` | Displayed as **Create Tab Group**. Accepts URLs or existing Safari tab entities to seed the new tab group. |

#### OS 26 to 27 Display Name Changes

| Identifier | Old Name | New Name |
|------------|----------|----------|
| `is.workflow.actions.extracttextfromimage` | Extract Text from Image | Extract from Image |
| `com.apple.TVRemoteUIService.ToggleSystemAppearanceIntent` | Set Light/Dark Mode | Set Appearance on Apple TV |

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
