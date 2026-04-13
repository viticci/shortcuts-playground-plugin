# AppIntents Reference

Complete catalog of all 1632 first-party AppIntent actions from macOS ToolKit v63 and backups.

## AppIntents vs WF*Actions

| Aspect | WF*Actions | AppIntents |
|--------|-----------|------------|
| Identifier format | `is.workflow.actions.*` | Full ID (e.g., `com.apple.systempreferences.OpenAboutSettingsStaticDeepLinks`) |
| Origin | Legacy Shortcuts (pre-iOS 16) | App Intents framework (iOS 16+) |
| Invocation | Direct identifier in action | Direct identifier in `WFWorkflowActionIdentifier` (with AppIntentDescriptor) |
| Scope | Core shortcut actions | System integrations, deep links, app extensions |

## How to Invoke AppIntents

AppIntents use their full identifier in `WFWorkflowActionIdentifier` and include an `AppIntentDescriptor`:

```
<dict>
    <key>WFWorkflowActionIdentifier</key>
    <string>com.apple.systempreferences.OpenAboutSettingsStaticDeepLinks</string>
    <key>WFWorkflowActionParameters</key>
    <dict>
        <key>AppIntentDescriptor</key>
        <dict>
            <key>BundleIdentifier</key>
            <string>com.apple.systempreferences</string>
            <key>Name</key>
            <string>About</string>
            <key>TeamIdentifier</key>
            <string>0000000000</string>
            <key>AppIntentIdentifier</key>
            <string>OpenAboutSettingsStaticDeepLinks</string>
        </dict>
        <!-- Additional parameters as needed -->
    </dict>
</dict>
```

---

## AppIntents by Category

### Settings Deep Links (23 actions)

Open specific Settings panes:

| Identifier | Title |
|------------|-------|
| `com.apple.Desktop-Settings.extension.OpenDesktopSettingsDeepLink` | Open Desktop & Dock Setting |
| `com.apple.GameCenter.Settings.DeviceExpertExtension.OpenGameCenterSettingsDeepLinks` | Open Game Center Settings |
| `com.apple.donotdisturb.DoNotDisturbAppIntents.OpenFocusSettingsDynamicDeepLinks` | Open Focus Settings |
| `com.apple.news.NewsSettingsAutomaticDownloadDynamicDeepLinks` | Find News Automatic Download Settings |
| `com.apple.news.NewsSettingsDynamicDeepLinks` | Find News Settings |
| `com.apple.systempreferences.AppearanceSettingsDeepLink` | Find Mouse setting |
| `com.apple.systempreferences.BatterySettingsPaneDynamicDeepLinks` | Find Battery Settings |
| `com.apple.systempreferences.FamilySettingsDeepLink` | Find FamilySettingsDeepLink |
| `com.apple.systempreferences.KeyboardSettingsDeepLink` | Find Keyboard Settings Deep Link |
| `com.apple.systempreferences.OpenAboutSettingsStaticDeepLinks` | Open About |
| `com.apple.systempreferences.OpenAppearanceSettingsDeepLink` | Open Appearance Settings |
| `com.apple.systempreferences.OpenBatterySettingsPaneDynamicDeepLinks` | Open Battery Settings |
| `com.apple.systempreferences.OpenBiometricsAndPasswordSettingsEntityDeepLinks` | OpenBiometricsAndPasswordSettingsEntityDeepLinks |
| `com.apple.systempreferences.OpenBluetoothSettingsDeepLinks` | Open Bluetooth Settings |
| `com.apple.systempreferences.OpenDesktopSettingsDeepLink` | Open Desktop & Dock Setting |
| `com.apple.systempreferences.OpenDisplaysSettingsDeepLinks` | Open Displays |
| `com.apple.systempreferences.OpenInternationalSettingsDeepLink` | Open Language & Region Settings |
| `com.apple.systempreferences.OpenKeyboardSettingsDeepLink` | Open Keyboard Settings |
| `com.apple.systempreferences.OpenNetworkSettingsDeepLinks` | Open Network |
| `com.apple.systempreferences.OpenSoundSettingsDeepLinks` | Open Sound |
| `com.apple.systempreferences.OpenSpotlightSettingsDeepLinks` | Open Search Settings |
| `com.apple.systempreferences.OpenTimeMachineSettingsStaticDeepLinks` | Open Time Machine Settings |
| `com.apple.systempreferences.SpotlightSettingsDeepLinks` | Find Search Settings |

### Accessibility (306 actions)

Accessibility settings and controls:

| Identifier Pattern | Description |
|-------------------|-------------|
| `OpenAccessibility*` | Open specific accessibility pane |
| `Ax*` | Accessibility entities and updatable values |
| `UpdateAx*` | Update accessibility setting value |
| `ToggleAx*` | Toggle accessibility feature |

Examples:
- `com.apple.systempreferences.OpenAccessibilityAudioDescriptionsStaticDeepLinks` - Open Accessibility Audio Descriptions Settings
- `com.apple.systempreferences.AxAdaptiveVoiceShortcutsEntity` - Get Vocal Shortcuts

### Clock & Alarms (18 actions)

| Identifier | Title |
|------------|-------|
| `com.apple.clock.AddWorldClockIntent` | Add City |
| `com.apple.clock.CancelTimerIntent` | Cancel Timer |
| `com.apple.clock.DeleteAlarmIntent` | Delete Alarms |
| `com.apple.clock.GetCurrentTimerDetailsIntent` | Get Current Timer |
| `com.apple.clock.GetTimeForCityIntent` | Get Time for City |
| `com.apple.clock.LapStopwatchIntent` | Lap Stopwatch |
| `com.apple.clock.OpenAlarmIntent` | Opens Alarm |
| `com.apple.clock.OpenTab` | Open Tab |
| `com.apple.clock.OpenTabIntent` | Open Clock Tab |
| `com.apple.clock.PauseTimerIntent` | Pause Timer |
| `com.apple.clock.RemoveWorldClockIntent` | Remove City |
| `com.apple.clock.ResetStopwatchIntent` | Reset Stopwatch |
| `com.apple.clock.ResumeTimerIntent` | Resume Timer |
| `com.apple.clock.StartStopwatchIntent` | Start Stopwatch |
| `com.apple.clock.StopStopwatchIntent` | Stop the Stopwatch |
| `com.apple.mobiletimer-framework.MobileTimerIntents.MTCreateAlarmIntent` | Add Alarm |
| `com.apple.mobiletimer-framework.MobileTimerIntents.MTGetAlarmsIntent` | Find Alarms |
| `com.apple.mobiletimer-framework.MobileTimerIntents.MTToggleAlarmIntent` | Toggle Alarm |

### Calendar (26 actions)

| Identifier | Title |
|------------|-------|
| `com.apple.iCal.CreateCalendarIntent` | Create Calendar |
| `com.apple.iCal.CreateEventIntent` | Create Event |
| `com.apple.iCal.CreateEventIntent_v0` | Create Event |
| `com.apple.iCal.DeleteCalendarsIntent` | Delete Calendars |
| `com.apple.iCal.DeleteEventIntent` | Delete Events |
| `com.apple.iCal.DeleteEventIntent_v0` | Delete Events |
| `com.apple.iCal.EditEventIntent` | Edit Event |
| `com.apple.iCal.EditEventIntent_v0` | Edit Event |
| `com.apple.iCal.EmailAttendeesIntent` | Email Attendees |
| `com.apple.iCal.EmailOrganizerIntent` | Email Organizer |
| `com.apple.iCal.EventEntity` | Find Event |
| `com.apple.iCal.FetchTransferableEventByURLIntent` | Fetch Transferable Event By URL Intent |
| `com.apple.iCal.FetchTransferableEventsInRangeIntent` | Fetch Transferable Events In Range Intent <no loc> |
| `com.apple.iCal.HighlightEventIntent` | Highlight Event |
| `com.apple.iCal.InboxItemEntity` | Find Inbox Item |
| `com.apple.iCal.JoinEventIntent` | Join Event |
| `com.apple.iCal.ListEventsIntent` | List Events Intent <no loc> |
| `com.apple.iCal.OpenCalendarEditorIntent` | Open Calendar Editor |
| `com.apple.iCal.OpenCalendarViewIntent` | Open Calendar View |
| `com.apple.iCal.OpenDateIntent` | Open Date |
| `com.apple.iCal.OpenEventDetailsIntent` | Open Event Details |
| `com.apple.iCal.OpenEventEditorIntent` | Open Event Editor |
| `com.apple.iCal.RespondToInboxItemIntent` | Respond to Inbox Item |
| `com.apple.iCal.SetCalendarFocusConfiguration` | Set Calendar Focus Filter |
| `com.apple.iCal.TransferableCalendarEntity` | Find TransferableCalendarEntity <no loc> |
| `com.apple.iCal.TransferableSourceEntity` | Find TransferableSourceEntity <no loc> |

### Reminders (36 actions)

| Identifier | Title |
|------------|-------|
| `com.apple.reminders.AddOrRemoveTagsAppIntent` | Add or Remove Tags |
| `com.apple.reminders.CompleteReminderAppIntent` | Set Reminder completion state |
| `com.apple.reminders.CompleteRemindersAppIntent` | Set Reminders completion state <no loc> |
| `com.apple.reminders.CreateCustomSmartListAppIntent` | Open New Custom Smart List |
| `com.apple.reminders.CreateGroupAppIntent` | Create Group |
| `com.apple.reminders.CreateSectionAppIntent` | Create Section |
| `com.apple.reminders.DeleteListsAppIntent` | Delete Lists |
| `com.apple.reminders.DeleteRemindersAppIntent` | Delete Reminders and Subtasks |
| `com.apple.reminders.DeleteRemindersListGroupsAppIntent` | Delete Groups |
| `com.apple.reminders.DeleteSectionsAppIntent` | Delete Sections |
| `com.apple.reminders.GroupEntity-UpdatableEntity` | Change Reminders Group Name |
| `com.apple.reminders.ListEntity-UpdatableEntity` | Edit Reminders List |
| `com.apple.reminders.MoveRemindersAppIntent` | Move Reminders |
| `com.apple.reminders.MoveRemindersToListAppIntent` | Move Reminders to a Reminders List <no loc> |
| `com.apple.reminders.MoveRemindersToParentReminderAppIntent` | Move Reminders to become Subtasks of a Parent Reminder <no loc> |
| `com.apple.reminders.MoveRemindersToSectionAppIntent` | Move Reminders to a Reminders List Section <no loc> |
| `com.apple.reminders.OpenGroupAppIntent` | Open Group |
| `com.apple.reminders.OpenReminderAppIntent` | Open Reminder In List |
| `com.apple.reminders.OpenSectionAppIntent` | Reveal Section In List |
| `com.apple.reminders.OpenSmartListAppIntent` | Open Smart List |
| `com.apple.reminders.OpenTagsAppIntent` | Open Tag Browser |
| `com.apple.reminders.RemotePreferencesEntity` | Get User Defaults Entity |
| `com.apple.reminders.SectionEntity-UpdatableEntity` | Edit Reminders List Section |
| `com.apple.reminders.SmartListEntity` | Find Smart List |
| `com.apple.reminders.TTRCreateListAppIntent` | Create List |
| `com.apple.reminders.TTRCreateReminderAppIntent` | Create Reminder |
| `com.apple.reminders.TTROpenListAppIntent` | Open List |
| `com.apple.reminders.TTROpenSmartListAppIntent` | Open List |
| `com.apple.reminders.TTRReminderSetCompletedIntent` | Toggle Reminder completion |
| `com.apple.reminders.TTRSearchRemindersAppIntent` | Search in Reminders |
| `com.apple.reminders.UpdateGroupAppIntent` | Update reminders group properties |
| `com.apple.reminders.UpdateListAppIntent` | Update reminders list properties |
| `com.apple.reminders.UpdateReminderAppIntent` | Update Reminder properties <no loc> |
| `com.apple.reminders.UpdateSectionAppIntent` | Update section properties |
| `com.apple.reminders.UpdateSmartListAppIntent` | Update reminders system smart list properties |
| `com.apple.reminders.UpdateSmartListIsHiddenAppIntent` | Show/Hide Reminders System Smart List |

### Notes (52 actions)

| Identifier | Title |
|------------|-------|
| `com.apple.Notes.AddFileAttachmentLinkAction` | Add File to Note |
| `com.apple.Notes.AddLinkAttachmentLinkAction` | Add Link |
| `com.apple.Notes.AddOrRemoveNoteLockLinkAction` | Add or Remove Note Lock |
| `com.apple.Notes.AddTagsToNotesLinkAction` | Add Tags to Notes |
| `com.apple.Notes.AppendMarkdownToNoteLinkAction` | Append Markdown to Note |
| `com.apple.Notes.ApplyFormattingLinkAction` | Apply Formatting to Selected Text |
| `com.apple.Notes.AttachmentEntity` | Find Attachment |
| `com.apple.Notes.ChangeFolderSettingLinkAction` | Change Folder View Setting |
| `com.apple.Notes.ChangeSettingLinkAction` | Change Notes Setting |
| `com.apple.Notes.ChangeTagSelectionIntent` | Change Tag Selection |
| `com.apple.Notes.CloseAppLocationLinkAction` | Close Notes View |
| `com.apple.Notes.CloseNoteLinkAction` | Close Note |
| `com.apple.Notes.CreateChecklistItemLinkAction` | Append Checklist Item |
| `com.apple.Notes.CreateFolderLinkAction` | Create Folder |
| `com.apple.Notes.CreateNoteFromMarkdownLinkAction` | Create Note from Markdown |
| `com.apple.Notes.CreateTableLinkAction` | Add Table to Note |
| `com.apple.Notes.CreateTagLinkAction` | Create Tag |
| `com.apple.Notes.DeleteAttachmentsLinkAction` | Delete Attachments |
| `com.apple.Notes.DeleteChecklistItemsLinkAction` | Delete Checklist Items |
| `com.apple.Notes.DeleteFoldersLinkAction` | Delete Folders |
| `com.apple.Notes.DeleteNotesLinkAction` | Delete Notes |
| `com.apple.Notes.DeleteTablesLinkAction` | Delete Tables |
| `com.apple.Notes.DeleteTagsLinkAction` | Delete Tags |
| `com.apple.Notes.GetLinkedNotesLinkAction` | Get Linked Notes |
| `com.apple.Notes.InsertAllMentionLinkAction` | Insert All Mention |
| `com.apple.Notes.InsertMentionLinkAction` | Insert Mention |
| `com.apple.Notes.InsertNoteLinkLinkAction` | Insert Note Link |
| `com.apple.Notes.MoveNotesToFolderLinkAction` | Move Notes to Folder |
| `com.apple.Notes.OpenAccountLinkAction` | Open Account |
| `com.apple.Notes.OpenAppLocationLinkAction` | Open Notes View |
| `com.apple.Notes.OpenAttachmentLinkAction` | Open Attachment |
| `com.apple.Notes.OpenChecklistItemLinkAction` | Reveal Checklist Item |
| `com.apple.Notes.OpenFolderLinkAction` | Open Folder |
| `com.apple.Notes.OpenTableLinkAction` | Reveal Table |
| `com.apple.Notes.OpenTagLinkAction` | Open Tag |
| `com.apple.Notes.OpenTopLevelFolderLinkAction` | Open Top-Level Folder |
| `com.apple.Notes.PinNotesLinkAction` | Pin Notes |
| `com.apple.Notes.QuickNoteIntent` | Quick Note |
| `com.apple.Notes.RemoveTagsFromNotesLinkAction` | Remove Tags from Notes |
| `com.apple.Notes.RenameFolderLinkAction` | Rename Folder |
| `com.apple.Notes.ReplaceSelectionLinkAction` | Replace Selected Text |
| `com.apple.Notes.SetAttachmentSizeLinkAction` | Set Attachment Size |
| `com.apple.Notes.SetChecklistItemCheckedLinkActionv2` | Set Checklist Items Checked |
| `com.apple.Notes.SetParagraphStyleLinkAction` | Set Paragraph Style |
| `com.apple.Notes.ShowNotesAppSearchResultsLinkAction` | Show Note and Attachment Search Result |
| `com.apple.Notes.ShowQuickNoteIntent` | Show Quick Note |
| `com.apple.Notes.StartRecordingLinkAction` | Start Audio Recording |
| `com.apple.Notes.TableEntity` | Find Table |
| `com.apple.mobilenotes.SharingExtension` | Create Note |
| `is.workflow.actions.appendnote` | Append to Note |
| `is.workflow.actions.filter.notes` | Find Notes |
| `is.workflow.actions.shownote` | Open Note |

### Safari (31 actions)

| Identifier | Title |
|------------|-------|
| `com.apple.Safari.BookmarkEntity` | Find Bookmarks |
| `com.apple.Safari.BookmarkTabIntent` | Bookmark Tab |
| `com.apple.Safari.BookmarkURLIntent` | Bookmark URL |
| `com.apple.Safari.CloseTab` | Close Tab |
| `com.apple.Safari.CloseTabsAssistantIntent` | Close Tabs |
| `com.apple.Safari.CloseView` | Close View |
| `com.apple.Safari.CloseWindowsIntent` | Close Windows |
| `com.apple.Safari.CreateNewBookmark` | Add Bookmark |
| `com.apple.Safari.CreateNewTab` | Create New Tab |
| `com.apple.Safari.CreateNewTabGroup` | Create Tab Group |
| `com.apple.Safari.CreateNewWindow` | Create Window |
| `com.apple.Safari.CreateTabAssistantIntent` | Create Tab |
| `com.apple.Safari.DeleteBookmarks` | Delete Bookmarks |
| `com.apple.Safari.DeleteTabGroups` | Delete Tab Groups |
| `com.apple.Safari.FindOnPage` | Find on Page |
| `com.apple.Safari.LoadURLInTab` | Open Link |
| `com.apple.Safari.MoveTabsToTabGroup` | Move Tabs to Tab Group |
| `com.apple.Safari.MoveTabsToWindowIntent` | Move Tabs to Window |
| `com.apple.Safari.OpenBookmark` | Open Bookmark |
| `com.apple.Safari.OpenBookmarkAssistantIntent` | Open Bookmark |
| `com.apple.Safari.OpenTab` | Switch Tab |
| `com.apple.Safari.OpenTabGroup` | Open Tab Group |
| `com.apple.Safari.OpenTabGroupForFocus` | Set Safari Focus Filter |
| `com.apple.Safari.OpenView` | Open View |
| `com.apple.Safari.QuickWebsiteSearchIntent` | Search Website |
| `com.apple.Safari.QuickWebsiteSearchProviderEntity` | Find browser_SearchableWebsiteEntity_1.0.0_entity_type_display_representation |
| `com.apple.Safari.SearchTabs` | Search Tabs |
| `com.apple.Safari.ShowWindowIntent` | Show Window |
| `com.apple.Safari.TabEntity` | Find Tabs |
| `com.apple.Safari.TabGroupEntity` | Find Tab Groups |
| `com.apple.Safari.WindowEntity` | Find Window |

### Home (32 actions)

| Identifier | Title |
|------------|-------|
| `com.apple.Home.ActivateSceneIntent` | Activate Scene |
| `com.apple.Home.AutomateAttributeValueIntent` | Automate Set Attribute Value |
| `com.apple.Home.AutomateSceneIntent` | Automate Scene |
| `com.apple.Home.CameraClipEntity` | Find  |
| `com.apple.Home.DeltaAttributeValueIntent` | Delta Attribute |
| `com.apple.Home.DeviceEntity` | Find Device |
| `com.apple.Home.ErrorIntent` | Error Intent |
| `com.apple.Home.ForecastWidgetConfiguration` | Show the Grid Forecast for a Home or your location. |
| `com.apple.Home.GetAttributeValueIntent` | Get Attribute |
| `com.apple.Home.GetDeviceInfoIntent` | Get Device Info |
| `com.apple.Home.HistoricalUsageWidgetConfiguration` | Select Home |
| `com.apple.Home.HomeAppIntentsExtensionTestAppIntent` | HomeAppIntentsExtensionTestAppIntent |
| `com.apple.Home.HomeEntity` | Find Selected Home |
| `com.apple.Home.HomeSingleTileConfigurationIntent` | Scene or Accessory |
| `com.apple.Home.HomeXLModuleConfigurationIntent` | Accessories |
| `com.apple.Home.OpenURLInHomeIntent` | Open Accessory or Scene in Home app |
| `com.apple.Home.RecommendedItemIntent` | Recommended Item |
| `com.apple.Home.RoomEntity` | Find Room |
| `com.apple.Home.SceneEntity` | Find Scene |
| `com.apple.Home.SecureToggleIntent` | Toggle Accessory or Scene |
| `com.apple.Home.SelectedHomeEntity` | Find Selected Home |
| `com.apple.Home.SetAttributeValueIntent` | Set Attribute |
| `com.apple.Home.ShowDeviceResultIntent` | Show Device Result |
| `com.apple.Home.ShowErrorIntent` | Show Error |
| `com.apple.Home.ShowNavigationIntent` | Show Navigation |
| `com.apple.Home.ShowSceneResultIntent` | Show Scene Result |
| `com.apple.Home.TileControlAction` | ToggleIntentTitle |
| `com.apple.Home.ToggleAttributeIntent` | Toggle Attribute |
| `com.apple.Home.ToggleControlConfigurationIntent` | Scene or Accessory |
| `com.apple.Home.ToggleIntent` | Toggle Accessory or Scene |
| `com.apple.Home.UtilityRateInfoWidgetConfiguration` | Select Home |
| `com.apple.Home.ZoneEntity` | Find Zone |

### Photos (69 actions)

| Identifier | Title |
|------------|-------|
| `com.apple.Photos.AddAssetsToAlbumIntent` | Add Photos To Album |
| `com.apple.Photos.ApplyFilterIntent` | Apply Filter |
| `com.apple.Photos.ApplyStyleIntent` | Apply Style |
| `com.apple.Photos.CleanupIntent` | Clean Up |
| `com.apple.Photos.CopyEditsIntent` | Copy Edits |
| `com.apple.Photos.CreateAlbumIntent` | Create Album |
| `com.apple.Photos.CreateAssetsIntent` | Save to Photos |
| `com.apple.Photos.CropIntent` | Crop |
| `com.apple.Photos.DeleteAlbumsIntent` | Delete Albums |
| `com.apple.Photos.DeleteAssetsIntent` | Delete Photos |
| `com.apple.Photos.DuplicateAssetsIntent` | Duplicate Photos |
| `com.apple.Photos.EditAssetIntent` | Edit Photo |
| `com.apple.Photos.EnableDepthIntent` | Portrait Mode |
| `com.apple.Photos.EnhanceIntent` | Auto Enhance |
| `com.apple.Photos.FavoriteAssetsIntent` | Favorite Photos |
| `com.apple.Photos.FavoriteMemoriesIntent` | Favorite Memories |
| `com.apple.Photos.FavoritePeopleIntent` | Favorite People or Pets |
| `com.apple.Photos.FilterLibraryIntent` | Set Library View |
| `com.apple.Photos.HideAssetsIntent` | Hide Photos |
| `com.apple.Photos.HidePeopleIntent` | Hide People or Pets |
| `com.apple.Photos.MarkupIntent` | Markup |
| `com.apple.Photos.MoveAssetsToPersonalLibraryIntent` | Move to Personal Library |
| `com.apple.Photos.MoveAssetsToSharedLibraryIntent` | Move to Shared Library |
| `com.apple.Photos.OpenAlbumIntent` | Open Album |
| `com.apple.Photos.OpenAssetIntent` | Open Photo |
| `com.apple.Photos.OpenDestinationIntent` | Open View |
| `com.apple.Photos.OpenMemoryCreationViewIntent` | Create Memory |
| `com.apple.Photos.OpenMemoryIntent` | Open Memory |
| `com.apple.Photos.OpenPersonIntent` | Open Person |
| `com.apple.Photos.PLPhotosReliveWidgetConfigurationIntent` | Photos Relive Widget Configuration |
| `com.apple.Photos.PasteEditsIntent` | Paste Edits |
| `com.apple.Photos.PhotosAddAssetsToAlbumAssistantIntent` | Add Photos to Album |
| `com.apple.Photos.PhotosCleanupPhotoAssistantIntent` | Cleanup |
| `com.apple.Photos.PhotosCopyEditsAssistantIntent` | Copy Edits |
| `com.apple.Photos.PhotosCreateAlbumAssistantIntent` | Create Album |
| `com.apple.Photos.PhotosCreateAssetsAssistantIntent` | Create Photos |
| `com.apple.Photos.PhotosCropAssistantIntent` | Crop Photo |
| `com.apple.Photos.PhotosDeleteAlbumsAssistantIntent` | Delete Albums |
| `com.apple.Photos.PhotosDeleteAssetsAssistantIntent` | Delete Photos |
| `com.apple.Photos.PhotosDuplicateAssetsAssistantIntent` | Duplicate Photos |
| `com.apple.Photos.PhotosPasteEditsAssistantIntent` | Paste Edits |
| `com.apple.Photos.PhotosReliveWidgetFeaturedConfiguration` | Photos Relive Featured Widget Configuration |
| `com.apple.Photos.PhotosRemoveAssetsFromAlbumAssistantIntent` | Remove Photos from Album |
| `com.apple.Photos.PhotosSearchAssistantIntent` | Search Photos |
| `com.apple.Photos.PhotosSetDepthAssistantIntent` | Set Depth |
| `com.apple.Photos.PhotosSetExposureAssistantIntent` | Set Exposure |
| `com.apple.Photos.PhotosSetFilterAssistantIntent` | Apply Filter |
| `com.apple.Photos.PhotosSetRotationAssistantIntent` | Rotate Photo |
| `com.apple.Photos.PhotosSetSaturationAssistantIntent` | Set Saturation |
| `com.apple.Photos.PhotosSetWarmthAssistantIntent` | Set Warmth |
| `com.apple.Photos.PhotosStraightenAssistantIntent` | Straighten Photo |
| `com.apple.Photos.PhotosToggleDepthAssistantIntent` | Toggle Depth |
| `com.apple.Photos.PhotosToggleSuggestedEditsAssistantIntent` | Enhance Photo |
| `com.apple.Photos.PhotosUpdateAlbumAssistantIntent` | Rename Album |
| `com.apple.Photos.PhotosUpdateAssetAssistantIntent` | Update Photo |
| `com.apple.Photos.PhotosUpdateRecognizedPersonAssistantIntent` | Update Person |
| `com.apple.Photos.RemoveAssetsFromAlbumIntent` | Remove Photos From Album |
| `com.apple.Photos.RenameAlbumIntent` | Rename Album |
| `com.apple.Photos.RenamePersonIntent` | Rename Person |
| `com.apple.Photos.RevealAlbumsIntent` | REVEAL_ALBUMS_INTENT_TITLE |
| `com.apple.Photos.RevealAssetsIntent` | REVEAL_ASSETS_INTENT_TITLE |
| `com.apple.Photos.RotateIntent` | Rotate |
| `com.apple.Photos.SetApertureIntent` | Set Aperture |
| `com.apple.Photos.SetAudioMixIntent` | Set Audio Mix |
| `com.apple.Photos.SetExposureIntent` | Set Exposure |
| `com.apple.Photos.SetPlaybackRateIntent` | Set Playback Speed |
| `com.apple.Photos.SetSaturationIntent` | Set Saturation |
| `com.apple.Photos.SetWarmthIntent` | Set Warmth |
| `com.apple.Photos.StraightenIntent` | Straighten |

### Music (1 actions)

| Identifier | Title |
|------------|-------|
| `com.apple.ShortcutsActions.PlayMusicTopHitAction` | Play Music |

### Writing Tools (3 actions)

| Identifier | Title |
|------------|-------|
| `com.apple.AppKit.WritingToolsComposeIntent` | Text Compose |
| `com.apple.AppKit.WritingToolsProofreadIntent` | Proofread |
| `com.apple.AppKit.WritingToolsRewriteIntent` | Rewrite |

### Voice Memos (24 actions)

| Identifier | Title |
|------------|-------|
| `com.apple.VoiceMemos.AudioQualityEntity` | Get Audio Quality |
| `com.apple.VoiceMemos.AudioQualityEntity-UpdatableEntity` | Edit Audio Quality |
| `com.apple.VoiceMemos.ChangeRecordingPlaybackSetting` | Change Recording Playback Setting |
| `com.apple.VoiceMemos.ClearDeletedEntity` | Get Clear Deleted |
| `com.apple.VoiceMemos.ClearDeletedEntity-UpdatableEntity` | Edit Clear Deleted |
| `com.apple.VoiceMemos.CreateFolder` | Create Folder |
| `com.apple.VoiceMemos.DeleteFolder` | Delete Folders |
| `com.apple.VoiceMemos.DeleteRecording` | Delete Recordings |
| `com.apple.VoiceMemos.LocationBasedNamingEntity` | Get Location-based Naming |
| `com.apple.VoiceMemos.LocationBasedNamingEntity-UpdatableEntity` | Edit Location-based Naming |
| `com.apple.VoiceMemos.OpenFolder` | Open Folder |
| `com.apple.VoiceMemos.OpenResetAnalyticsIdentifierEntity` | Open Reset Identifier |
| `com.apple.VoiceMemos.PlaybackVoiceMemoIntent` | Play Recording |
| `com.apple.VoiceMemos.RCCombineRecordings` | Combine Recordings |
| `com.apple.VoiceMemos.RCControlCenterToggleRecording` | CONTROL_CENTER_TOGGLE_RECORDING_INTENT_TITLE |
| `com.apple.VoiceMemos.RCImportRecording` | Import Recording |
| `com.apple.VoiceMemos.RCRecordingEntity` | Find Recordings |
| `com.apple.VoiceMemos.RecordVoiceMemoIntent` | Create Recording |
| `com.apple.VoiceMemos.ResetAnalyticsIdentifierEntity` | Get Reset Identifier |
| `com.apple.VoiceMemos.SearchRecordings` | Search in Voice Memos |
| `com.apple.VoiceMemos.SelectRecording` | Select Recording |
| `com.apple.VoiceMemos.StopRecording` | Stop Recording |
| `com.apple.VoiceMemos.ToggleRecording` | Voice Memo |
| `com.apple.VoiceMemos.WFAppSettingEntityUpdaterAction` | Change Voice Memos Settings |

### Shortcuts (23 actions)

| Identifier | Title |
|------------|-------|
| `com.apple.VoiceMemos.WFGetAppSettingAction` | Get Voice Memos Settings |
| `com.apple.news.WFGetAppSettingAction` | Get News Settings |
| `com.apple.shortcuts.AddShortcutToHomeScreenAction` | Add Shortcut to Home Screen |
| `com.apple.shortcuts.ChangeShortcutIconAction` | Change Shortcut Icon |
| `com.apple.shortcuts.CreateFolderAction` | Create Folder |
| `com.apple.shortcuts.CreateShortcutiCloudLinkAction` | Create iCloud Link for Shortcut |
| `com.apple.shortcuts.CreateWorkflowAction` | Create Shortcut |
| `com.apple.shortcuts.DeleteWorkflowAction` | Delete Shortcuts |
| `com.apple.shortcuts.GetShortcutAttributesAction` | Get Shortcut Attributes |
| `com.apple.shortcuts.MoveShortcutToFolderAction` | Move Shortcut |
| `com.apple.shortcuts.OpenAppIntent` | Open App |
| `com.apple.shortcuts.OpenNavigationDestinationAction` | Open Folder |
| `com.apple.shortcuts.OpenShortcutsStaticDeepLinks` | Open Shortcuts Settings |
| `com.apple.shortcuts.OpenWorkflowAction` | Open Shortcut |
| `com.apple.shortcuts.RenameShortcutAction` | Rename Shortcut |
| `com.apple.shortcuts.RunShortcutConfigurationIntent` | Shortcut |
| `com.apple.shortcuts.RunShortcutFromCollectionIntent` | Run Shortcut from Folder |
| `com.apple.shortcuts.RunShortcutIntent` | Run Shortcut |
| `com.apple.shortcuts.SearchActionDrawerAction` | Search Shortcuts Actions |
| `com.apple.shortcuts.SearchShortcutsAction` | Search in Shortcuts |
| `com.apple.shortcuts.SetShortcutAttributesAction` | Set Shortcut Attributes |
| `com.apple.shortcuts.ShortcutsFolderConfigurationIntent` | Shortcuts Folder |
| `com.apple.shortcuts.StopWorkflowAction` | Stop Shortcut |

### System Controls (52 actions)

Toggle and set system settings:

| Pattern | Description |
|---------|-------------|
| `Set*` | Set system setting |
| `Toggle*` | Toggle system setting |
| `Update*` | Update system setting value |

Examples:
- `com.apple.Home.SetAttributeValueIntent` - Set Attribute
- `com.apple.Home.ToggleAttributeIntent` - Toggle Attribute
- `com.apple.AddressBook.UpdateContactIntent` - Update Contact Details

### Data & Search (37 actions)

| Pattern | Description |
|---------|-------------|
| `Find*` | Find/search items |
| `Get*` | Get data |
| `Search*` | Search for content |

Examples:
- `com.apple.Safari.FindOnPage` - Find on Page
- `com.apple.Home.GetAttributeValueIntent` - Get Attribute
- `com.apple.AddressBook.SearchInContactsIntent` - Search in Contacts App

------------|-------|
| `com.apple.Desktop-Settings.extension.OpenDesktopSettingsDeepLink` | Open Desktop & Dock Setting |
| `com.apple.GameCenter.Settings.DeviceExpertExtension.OpenGameCenterSettingsDeepLinks` | Open Game Center Settings |
| `com.apple.donotdisturb.DoNotDisturbAppIntents.OpenFocusSettingsDynamicDeepLinks` | Open Focus Settings |
| `com.apple.news.NewsSettingsAutomaticDownloadDynamicDeepLinks` | Find News Automatic Download Settings |
| `com.apple.news.NewsSettingsDynamicDeepLinks` | Find News Settings |
| `com.apple.systempreferences.AppearanceSettingsDeepLink` | Find Mouse setting |
| `com.apple.systempreferences.BatterySettingsPaneDynamicDeepLinks` | Find Battery Settings |
| `com.apple.systempreferences.FamilySettingsDeepLink` | Find FamilySettingsDeepLink |
| `com.apple.systempreferences.KeyboardSettingsDeepLink` | Find Keyboard Settings Deep Link |
| `com.apple.systempreferences.OpenAboutSettingsStaticDeepLinks` | Open About |
| `com.apple.systempreferences.OpenAppearanceSettingsDeepLink` | Open Appearance Settings |
| `com.apple.systempreferences.OpenBatterySettingsPaneDynamicDeepLinks` | Open Battery Settings |
| `com.apple.systempreferences.OpenBiometricsAndPasswordSettingsEntityDeepLinks` | OpenBiometricsAndPasswordSettingsEntityDeepLinks |
| `com.apple.systempreferences.OpenBluetoothSettingsDeepLinks` | Open Bluetooth Settings |
| `com.apple.systempreferences.OpenDesktopSettingsDeepLink` | Open Desktop & Dock Setting |
| `com.apple.systempreferences.OpenDisplaysSettingsDeepLinks` | Open Displays |
| `com.apple.systempreferences.OpenInternationalSettingsDeepLink` | Open Language & Region Settings |
| `com.apple.systempreferences.OpenKeyboardSettingsDeepLink` | Open Keyboard Settings |
| `com.apple.systempreferences.OpenNetworkSettingsDeepLinks` | Open Network |
| `com.apple.systempreferences.OpenSoundSettingsDeepLinks` | Open Sound |
| `com.apple.systempreferences.OpenSpotlightSettingsDeepLinks` | Open Search Settings |
| `com.apple.systempreferences.OpenTimeMachineSettingsStaticDeepLinks` | Open Time Machine Settings |
| `com.apple.systempreferences.SpotlightSettingsDeepLinks` | Find Search Settings |

### Accessibility (306 actions)

Accessibility settings and controls:

| Identifier Pattern | Description |
|-------------------|-------------|
| `OpenAccessibility*` | Open specific accessibility pane |
| `Ax*` | Accessibility entities and updatable values |
| `UpdateAx*` | Update accessibility setting value |
| `ToggleAx*` | Toggle accessibility feature |

Examples:
- `com.apple.systempreferences.OpenAccessibilityAudioDescriptionsStaticDeepLinks` - Open Accessibility Audio Descriptions Settings
- `com.apple.systempreferences.AxAdaptiveVoiceShortcutsEntity` - Get Vocal Shortcuts

### Clock & Alarms (18 actions)



| Identifier | Title |
|------------|-------|
| `com.apple.clock.AddWorldClockIntent` | Add City |
| `com.apple.clock.CancelTimerIntent` | Cancel Timer |
| `com.apple.clock.DeleteAlarmIntent` | Delete Alarms |
| `com.apple.clock.GetCurrentTimerDetailsIntent` | Get Current Timer |
| `com.apple.clock.GetTimeForCityIntent` | Get Time for City |
| `com.apple.clock.LapStopwatchIntent` | Lap Stopwatch |
| `com.apple.clock.OpenAlarmIntent` | Opens Alarm |
| `com.apple.clock.OpenTab` | Open Tab |
| `com.apple.clock.OpenTabIntent` | Open Clock Tab |
| `com.apple.clock.PauseTimerIntent` | Pause Timer |
| `com.apple.clock.RemoveWorldClockIntent` | Remove City |
| `com.apple.clock.ResetStopwatchIntent` | Reset Stopwatch |
| `com.apple.clock.ResumeTimerIntent` | Resume Timer |
| `com.apple.clock.StartStopwatchIntent` | Start Stopwatch |
| `com.apple.clock.StopStopwatchIntent` | Stop the Stopwatch |
| `com.apple.mobiletimer-framework.MobileTimerIntents.MTCreateAlarmIntent` | Add Alarm |
| `com.apple.mobiletimer-framework.MobileTimerIntents.MTGetAlarmsIntent` | Find Alarms |
| `com.apple.mobiletimer-framework.MobileTimerIntents.MTToggleAlarmIntent` | Toggle Alarm |

### Calendar (26 actions)



| Identifier | Title |
|------------|-------|
| `com.apple.iCal.CreateCalendarIntent` | Create Calendar |
| `com.apple.iCal.CreateEventIntent` | Create Event |
| `com.apple.iCal.CreateEventIntent_v0` | Create Event |
| `com.apple.iCal.DeleteCalendarsIntent` | Delete Calendars |
| `com.apple.iCal.DeleteEventIntent` | Delete Events |
| `com.apple.iCal.DeleteEventIntent_v0` | Delete Events |
| `com.apple.iCal.EditEventIntent` | Edit Event |
| `com.apple.iCal.EditEventIntent_v0` | Edit Event |
| `com.apple.iCal.EmailAttendeesIntent` | Email Attendees |
| `com.apple.iCal.EmailOrganizerIntent` | Email Organizer |
| `com.apple.iCal.EventEntity` | Find Event |
| `com.apple.iCal.FetchTransferableEventByURLIntent` | Fetch Transferable Event By URL Intent |
| `com.apple.iCal.FetchTransferableEventsInRangeIntent` | Fetch Transferable Events In Range Intent <no loc> |
| `com.apple.iCal.HighlightEventIntent` | Highlight Event |
| `com.apple.iCal.InboxItemEntity` | Find Inbox Item |
| `com.apple.iCal.JoinEventIntent` | Join Event |
| `com.apple.iCal.ListEventsIntent` | List Events Intent <no loc> |
| `com.apple.iCal.OpenCalendarEditorIntent` | Open Calendar Editor |
| `com.apple.iCal.OpenCalendarViewIntent` | Open Calendar View |
| `com.apple.iCal.OpenDateIntent` | Open Date |
| `com.apple.iCal.OpenEventDetailsIntent` | Open Event Details |
| `com.apple.iCal.OpenEventEditorIntent` | Open Event Editor |
| `com.apple.iCal.RespondToInboxItemIntent` | Respond to Inbox Item |
| `com.apple.iCal.SetCalendarFocusConfiguration` | Set Calendar Focus Filter |
| `com.apple.iCal.TransferableCalendarEntity` | Find TransferableCalendarEntity <no loc> |
| `com.apple.iCal.TransferableSourceEntity` | Find TransferableSourceEntity <no loc> |

### Reminders (36 actions)



| Identifier | Title |
|------------|-------|
| `com.apple.reminders.AddOrRemoveTagsAppIntent` | Add or Remove Tags |
| `com.apple.reminders.CompleteReminderAppIntent` | Set Reminder completion state |
| `com.apple.reminders.CompleteRemindersAppIntent` | Set Reminders completion state <no loc> |
| `com.apple.reminders.CreateCustomSmartListAppIntent` | Open New Custom Smart List |
| `com.apple.reminders.CreateGroupAppIntent` | Create Group |
| `com.apple.reminders.CreateSectionAppIntent` | Create Section |
| `com.apple.reminders.DeleteListsAppIntent` | Delete Lists |
| `com.apple.reminders.DeleteRemindersAppIntent` | Delete Reminders and Subtasks |
| `com.apple.reminders.DeleteRemindersListGroupsAppIntent` | Delete Groups |
| `com.apple.reminders.DeleteSectionsAppIntent` | Delete Sections |
| `com.apple.reminders.GroupEntity-UpdatableEntity` | Change Reminders Group Name |
| `com.apple.reminders.ListEntity-UpdatableEntity` | Edit Reminders List |
| `com.apple.reminders.MoveRemindersAppIntent` | Move Reminders |
| `com.apple.reminders.MoveRemindersToListAppIntent` | Move Reminders to a Reminders List <no loc> |
| `com.apple.reminders.MoveRemindersToParentReminderAppIntent` | Move Reminders to become Subtasks of a Parent Reminder <no loc> |
| `com.apple.reminders.MoveRemindersToSectionAppIntent` | Move Reminders to a Reminders List Section <no loc> |
| `com.apple.reminders.OpenGroupAppIntent` | Open Group |
| `com.apple.reminders.OpenReminderAppIntent` | Open Reminder In List |
| `com.apple.reminders.OpenSectionAppIntent` | Reveal Section In List |
| `com.apple.reminders.OpenSmartListAppIntent` | Open Smart List |
| `com.apple.reminders.OpenTagsAppIntent` | Open Tag Browser |
| `com.apple.reminders.RemotePreferencesEntity` | Get User Defaults Entity |
| `com.apple.reminders.SectionEntity-UpdatableEntity` | Edit Reminders List Section |
| `com.apple.reminders.SmartListEntity` | Find Smart List |
| `com.apple.reminders.TTRCreateListAppIntent` | Create List |
| `com.apple.reminders.TTRCreateReminderAppIntent` | Create Reminder |
| `com.apple.reminders.TTROpenListAppIntent` | Open List |
| `com.apple.reminders.TTROpenSmartListAppIntent` | Open List |
| `com.apple.reminders.TTRReminderSetCompletedIntent` | Toggle Reminder completion |
| `com.apple.reminders.TTRSearchRemindersAppIntent` | Search in Reminders |
| `com.apple.reminders.UpdateGroupAppIntent` | Update reminders group properties |
| `com.apple.reminders.UpdateListAppIntent` | Update reminders list properties |
| `com.apple.reminders.UpdateReminderAppIntent` | Update Reminder properties <no loc> |
| `com.apple.reminders.UpdateSectionAppIntent` | Update section properties |
| `com.apple.reminders.UpdateSmartListAppIntent` | Update reminders system smart list properties |
| `com.apple.reminders.UpdateSmartListIsHiddenAppIntent` | Show/Hide Reminders System Smart List |

### Notes (52 actions)



| Identifier | Title |
|------------|-------|
| `com.apple.Notes.AddFileAttachmentLinkAction` | Add File to Note |
| `com.apple.Notes.AddLinkAttachmentLinkAction` | Add Link |
| `com.apple.Notes.AddOrRemoveNoteLockLinkAction` | Add or Remove Note Lock |
| `com.apple.Notes.AddTagsToNotesLinkAction` | Add Tags to Notes |
| `com.apple.Notes.AppendMarkdownToNoteLinkAction` | Append Markdown to Note |
| `com.apple.Notes.ApplyFormattingLinkAction` | Apply Formatting to Selected Text |
| `com.apple.Notes.AttachmentEntity` | Find Attachment |
| `com.apple.Notes.ChangeFolderSettingLinkAction` | Change Folder View Setting |
| `com.apple.Notes.ChangeSettingLinkAction` | Change Notes Setting |
| `com.apple.Notes.ChangeTagSelectionIntent` | Change Tag Selection |
| `com.apple.Notes.CloseAppLocationLinkAction` | Close Notes View |
| `com.apple.Notes.CloseNoteLinkAction` | Close Note |
| `com.apple.Notes.CreateChecklistItemLinkAction` | Append Checklist Item |
| `com.apple.Notes.CreateFolderLinkAction` | Create Folder |
| `com.apple.Notes.CreateNoteFromMarkdownLinkAction` | Create Note from Markdown |
| `com.apple.Notes.CreateTableLinkAction` | Add Table to Note |
| `com.apple.Notes.CreateTagLinkAction` | Create Tag |
| `com.apple.Notes.DeleteAttachmentsLinkAction` | Delete Attachments |
| `com.apple.Notes.DeleteChecklistItemsLinkAction` | Delete Checklist Items |
| `com.apple.Notes.DeleteFoldersLinkAction` | Delete Folders |
| `com.apple.Notes.DeleteNotesLinkAction` | Delete Notes |
| `com.apple.Notes.DeleteTablesLinkAction` | Delete Tables |
| `com.apple.Notes.DeleteTagsLinkAction` | Delete Tags |
| `com.apple.Notes.GetLinkedNotesLinkAction` | Get Linked Notes |
| `com.apple.Notes.InsertAllMentionLinkAction` | Insert All Mention |
| `com.apple.Notes.InsertMentionLinkAction` | Insert Mention |
| `com.apple.Notes.InsertNoteLinkLinkAction` | Insert Note Link |
| `com.apple.Notes.MoveNotesToFolderLinkAction` | Move Notes to Folder |
| `com.apple.Notes.OpenAccountLinkAction` | Open Account |
| `com.apple.Notes.OpenAppLocationLinkAction` | Open Notes View |
| `com.apple.Notes.OpenAttachmentLinkAction` | Open Attachment |
| `com.apple.Notes.OpenChecklistItemLinkAction` | Reveal Checklist Item |
| `com.apple.Notes.OpenFolderLinkAction` | Open Folder |
| `com.apple.Notes.OpenTableLinkAction` | Reveal Table |
| `com.apple.Notes.OpenTagLinkAction` | Open Tag |
| `com.apple.Notes.OpenTopLevelFolderLinkAction` | Open Top-Level Folder |
| `com.apple.Notes.PinNotesLinkAction` | Pin Notes |
| `com.apple.Notes.QuickNoteIntent` | Quick Note |
| `com.apple.Notes.RemoveTagsFromNotesLinkAction` | Remove Tags from Notes |
| `com.apple.Notes.RenameFolderLinkAction` | Rename Folder |
| `com.apple.Notes.ReplaceSelectionLinkAction` | Replace Selected Text |
| `com.apple.Notes.SetAttachmentSizeLinkAction` | Set Attachment Size |
| `com.apple.Notes.SetChecklistItemCheckedLinkActionv2` | Set Checklist Items Checked |
| `com.apple.Notes.SetParagraphStyleLinkAction` | Set Paragraph Style |
| `com.apple.Notes.ShowNotesAppSearchResultsLinkAction` | Show Note and Attachment Search Result |
| `com.apple.Notes.ShowQuickNoteIntent` | Show Quick Note |
| `com.apple.Notes.StartRecordingLinkAction` | Start Audio Recording |
| `com.apple.Notes.TableEntity` | Find Table |
| `com.apple.mobilenotes.SharingExtension` | Create Note |
| `is.workflow.actions.appendnote` | Append to Note |
| `is.workflow.actions.filter.notes` | Find Notes |
| `is.workflow.actions.shownote` | Open Note |

### Safari (31 actions)



| Identifier | Title |
|------------|-------|
| `com.apple.Safari.BookmarkEntity` | Find Bookmarks |
| `com.apple.Safari.BookmarkTabIntent` | Bookmark Tab |
| `com.apple.Safari.BookmarkURLIntent` | Bookmark URL |
| `com.apple.Safari.CloseTab` | Close Tab |
| `com.apple.Safari.CloseTabsAssistantIntent` | Close Tabs |
| `com.apple.Safari.CloseView` | Close View |
| `com.apple.Safari.CloseWindowsIntent` | Close Windows |
| `com.apple.Safari.CreateNewBookmark` | Add Bookmark |
| `com.apple.Safari.CreateNewTab` | Create New Tab |
| `com.apple.Safari.CreateNewTabGroup` | Create Tab Group |
| `com.apple.Safari.CreateNewWindow` | Create Window |
| `com.apple.Safari.CreateTabAssistantIntent` | Create Tab |
| `com.apple.Safari.DeleteBookmarks` | Delete Bookmarks |
| `com.apple.Safari.DeleteTabGroups` | Delete Tab Groups |
| `com.apple.Safari.FindOnPage` | Find on Page |
| `com.apple.Safari.LoadURLInTab` | Open Link |
| `com.apple.Safari.MoveTabsToTabGroup` | Move Tabs to Tab Group |
| `com.apple.Safari.MoveTabsToWindowIntent` | Move Tabs to Window |
| `com.apple.Safari.OpenBookmark` | Open Bookmark |
| `com.apple.Safari.OpenBookmarkAssistantIntent` | Open Bookmark |
| `com.apple.Safari.OpenTab` | Switch Tab |
| `com.apple.Safari.OpenTabGroup` | Open Tab Group |
| `com.apple.Safari.OpenTabGroupForFocus` | Set Safari Focus Filter |
| `com.apple.Safari.OpenView` | Open View |
| `com.apple.Safari.QuickWebsiteSearchIntent` | Search Website |
| `com.apple.Safari.QuickWebsiteSearchProviderEntity` | Find browser_SearchableWebsiteEntity_1.0.0_entity_type_display_representation |
| `com.apple.Safari.SearchTabs` | Search Tabs |
| `com.apple.Safari.ShowWindowIntent` | Show Window |
| `com.apple.Safari.TabEntity` | Find Tabs |
| `com.apple.Safari.TabGroupEntity` | Find Tab Groups |
| `com.apple.Safari.WindowEntity` | Find Window |

### Home (32 actions)



| Identifier | Title |
|------------|-------|
| `com.apple.Home.ActivateSceneIntent` | Activate Scene |
| `com.apple.Home.AutomateAttributeValueIntent` | Automate Set Attribute Value |
| `com.apple.Home.AutomateSceneIntent` | Automate Scene |
| `com.apple.Home.CameraClipEntity` | Find  |
| `com.apple.Home.DeltaAttributeValueIntent` | Delta Attribute |
| `com.apple.Home.DeviceEntity` | Find Device |
| `com.apple.Home.ErrorIntent` | Error Intent |
| `com.apple.Home.ForecastWidgetConfiguration` | Show the Grid Forecast for a Home or your location. |
| `com.apple.Home.GetAttributeValueIntent` | Get Attribute |
| `com.apple.Home.GetDeviceInfoIntent` | Get Device Info |
| `com.apple.Home.HistoricalUsageWidgetConfiguration` | Select Home |
| `com.apple.Home.HomeAppIntentsExtensionTestAppIntent` | HomeAppIntentsExtensionTestAppIntent |
| `com.apple.Home.HomeEntity` | Find Selected Home |
| `com.apple.Home.HomeSingleTileConfigurationIntent` | Scene or Accessory |
| `com.apple.Home.HomeXLModuleConfigurationIntent` | Accessories |
| `com.apple.Home.OpenURLInHomeIntent` | Open Accessory or Scene in Home app |
| `com.apple.Home.RecommendedItemIntent` | Recommended Item |
| `com.apple.Home.RoomEntity` | Find Room |
| `com.apple.Home.SceneEntity` | Find Scene |
| `com.apple.Home.SecureToggleIntent` | Toggle Accessory or Scene |
| `com.apple.Home.SelectedHomeEntity` | Find Selected Home |
| `com.apple.Home.SetAttributeValueIntent` | Set Attribute |
| `com.apple.Home.ShowDeviceResultIntent` | Show Device Result |
| `com.apple.Home.ShowErrorIntent` | Show Error |
| `com.apple.Home.ShowNavigationIntent` | Show Navigation |
| `com.apple.Home.ShowSceneResultIntent` | Show Scene Result |
| `com.apple.Home.TileControlAction` | ToggleIntentTitle |
| `com.apple.Home.ToggleAttributeIntent` | Toggle Attribute |
| `com.apple.Home.ToggleControlConfigurationIntent` | Scene or Accessory |
| `com.apple.Home.ToggleIntent` | Toggle Accessory or Scene |
| `com.apple.Home.UtilityRateInfoWidgetConfiguration` | Select Home |
| `com.apple.Home.ZoneEntity` | Find Zone |

### Photos (69 actions)



| Identifier | Title |
|------------|-------|
| `com.apple.Photos.AddAssetsToAlbumIntent` | Add Photos To Album |
| `com.apple.Photos.ApplyFilterIntent` | Apply Filter |
| `com.apple.Photos.ApplyStyleIntent` | Apply Style |
| `com.apple.Photos.CleanupIntent` | Clean Up |
| `com.apple.Photos.CopyEditsIntent` | Copy Edits |
| `com.apple.Photos.CreateAlbumIntent` | Create Album |
| `com.apple.Photos.CreateAssetsIntent` | Save to Photos |
| `com.apple.Photos.CropIntent` | Crop |
| `com.apple.Photos.DeleteAlbumsIntent` | Delete Albums |
| `com.apple.Photos.DeleteAssetsIntent` | Delete Photos |
| `com.apple.Photos.DuplicateAssetsIntent` | Duplicate Photos |
| `com.apple.Photos.EditAssetIntent` | Edit Photo |
| `com.apple.Photos.EnableDepthIntent` | Portrait Mode |
| `com.apple.Photos.EnhanceIntent` | Auto Enhance |
| `com.apple.Photos.FavoriteAssetsIntent` | Favorite Photos |
| `com.apple.Photos.FavoriteMemoriesIntent` | Favorite Memories |
| `com.apple.Photos.FavoritePeopleIntent` | Favorite People or Pets |
| `com.apple.Photos.FilterLibraryIntent` | Set Library View |
| `com.apple.Photos.HideAssetsIntent` | Hide Photos |
| `com.apple.Photos.HidePeopleIntent` | Hide People or Pets |
| `com.apple.Photos.MarkupIntent` | Markup |
| `com.apple.Photos.MoveAssetsToPersonalLibraryIntent` | Move to Personal Library |
| `com.apple.Photos.MoveAssetsToSharedLibraryIntent` | Move to Shared Library |
| `com.apple.Photos.OpenAlbumIntent` | Open Album |
| `com.apple.Photos.OpenAssetIntent` | Open Photo |
| `com.apple.Photos.OpenDestinationIntent` | Open View |
| `com.apple.Photos.OpenMemoryCreationViewIntent` | Create Memory |
| `com.apple.Photos.OpenMemoryIntent` | Open Memory |
| `com.apple.Photos.OpenPersonIntent` | Open Person |
| `com.apple.Photos.PLPhotosReliveWidgetConfigurationIntent` | Photos Relive Widget Configuration |
| `com.apple.Photos.PasteEditsIntent` | Paste Edits |
| `com.apple.Photos.PhotosAddAssetsToAlbumAssistantIntent` | Add Photos to Album |
| `com.apple.Photos.PhotosCleanupPhotoAssistantIntent` | Cleanup |
| `com.apple.Photos.PhotosCopyEditsAssistantIntent` | Copy Edits |
| `com.apple.Photos.PhotosCreateAlbumAssistantIntent` | Create Album |
| `com.apple.Photos.PhotosCreateAssetsAssistantIntent` | Create Photos |
| `com.apple.Photos.PhotosCropAssistantIntent` | Crop Photo |
| `com.apple.Photos.PhotosDeleteAlbumsAssistantIntent` | Delete Albums |
| `com.apple.Photos.PhotosDeleteAssetsAssistantIntent` | Delete Photos |
| `com.apple.Photos.PhotosDuplicateAssetsAssistantIntent` | Duplicate Photos |
| `com.apple.Photos.PhotosPasteEditsAssistantIntent` | Paste Edits |
| `com.apple.Photos.PhotosReliveWidgetFeaturedConfiguration` | Photos Relive Featured Widget Configuration |
| `com.apple.Photos.PhotosRemoveAssetsFromAlbumAssistantIntent` | Remove Photos from Album |
| `com.apple.Photos.PhotosSearchAssistantIntent` | Search Photos |
| `com.apple.Photos.PhotosSetDepthAssistantIntent` | Set Depth |
| `com.apple.Photos.PhotosSetExposureAssistantIntent` | Set Exposure |
| `com.apple.Photos.PhotosSetFilterAssistantIntent` | Apply Filter |
| `com.apple.Photos.PhotosSetRotationAssistantIntent` | Rotate Photo |
| `com.apple.Photos.PhotosSetSaturationAssistantIntent` | Set Saturation |
| `com.apple.Photos.PhotosSetWarmthAssistantIntent` | Set Warmth |
| `com.apple.Photos.PhotosStraightenAssistantIntent` | Straighten Photo |
| `com.apple.Photos.PhotosToggleDepthAssistantIntent` | Toggle Depth |
| `com.apple.Photos.PhotosToggleSuggestedEditsAssistantIntent` | Enhance Photo |
| `com.apple.Photos.PhotosUpdateAlbumAssistantIntent` | Rename Album |
| `com.apple.Photos.PhotosUpdateAssetAssistantIntent` | Update Photo |
| `com.apple.Photos.PhotosUpdateRecognizedPersonAssistantIntent` | Update Person |
| `com.apple.Photos.RemoveAssetsFromAlbumIntent` | Remove Photos From Album |
| `com.apple.Photos.RenameAlbumIntent` | Rename Album |
| `com.apple.Photos.RenamePersonIntent` | Rename Person |
| `com.apple.Photos.RevealAlbumsIntent` | REVEAL_ALBUMS_INTENT_TITLE |
| `com.apple.Photos.RevealAssetsIntent` | REVEAL_ASSETS_INTENT_TITLE |
| `com.apple.Photos.RotateIntent` | Rotate |
| `com.apple.Photos.SetApertureIntent` | Set Aperture |
| `com.apple.Photos.SetAudioMixIntent` | Set Audio Mix |
| `com.apple.Photos.SetExposureIntent` | Set Exposure |
| `com.apple.Photos.SetPlaybackRateIntent` | Set Playback Speed |
| `com.apple.Photos.SetSaturationIntent` | Set Saturation |
| `com.apple.Photos.SetWarmthIntent` | Set Warmth |
| `com.apple.Photos.StraightenIntent` | Straighten |

### Music (1 actions)



| Identifier | Title |
|------------|-------|
| `com.apple.ShortcutsActions.PlayMusicTopHitAction` | Play Music |

### Writing Tools (3 actions)



| Identifier | Title |
|------------|-------|
| `com.apple.AppKit.WritingToolsComposeIntent` | Text Compose |
| `com.apple.AppKit.WritingToolsProofreadIntent` | Proofread |
| `com.apple.AppKit.WritingToolsRewriteIntent` | Rewrite |

### Voice Memos (24 actions)



| Identifier | Title |
|------------|-------|
| `com.apple.VoiceMemos.AudioQualityEntity` | Get Audio Quality |
| `com.apple.VoiceMemos.AudioQualityEntity-UpdatableEntity` | Edit Audio Quality |
| `com.apple.VoiceMemos.ChangeRecordingPlaybackSetting` | Change Recording Playback Setting |
| `com.apple.VoiceMemos.ClearDeletedEntity` | Get Clear Deleted |
| `com.apple.VoiceMemos.ClearDeletedEntity-UpdatableEntity` | Edit Clear Deleted |
| `com.apple.VoiceMemos.CreateFolder` | Create Folder |
| `com.apple.VoiceMemos.DeleteFolder` | Delete Folders |
| `com.apple.VoiceMemos.DeleteRecording` | Delete Recordings |
| `com.apple.VoiceMemos.LocationBasedNamingEntity` | Get Location-based Naming |
| `com.apple.VoiceMemos.LocationBasedNamingEntity-UpdatableEntity` | Edit Location-based Naming |
| `com.apple.VoiceMemos.OpenFolder` | Open Folder |
| `com.apple.VoiceMemos.OpenResetAnalyticsIdentifierEntity` | Open Reset Identifier |
| `com.apple.VoiceMemos.PlaybackVoiceMemoIntent` | Play Recording |
| `com.apple.VoiceMemos.RCCombineRecordings` | Combine Recordings |
| `com.apple.VoiceMemos.RCControlCenterToggleRecording` | CONTROL_CENTER_TOGGLE_RECORDING_INTENT_TITLE |
| `com.apple.VoiceMemos.RCImportRecording` | Import Recording |
| `com.apple.VoiceMemos.RCRecordingEntity` | Find Recordings |
| `com.apple.VoiceMemos.RecordVoiceMemoIntent` | Create Recording |
| `com.apple.VoiceMemos.ResetAnalyticsIdentifierEntity` | Get Reset Identifier |
| `com.apple.VoiceMemos.SearchRecordings` | Search in Voice Memos |
| `com.apple.VoiceMemos.SelectRecording` | Select Recording |
| `com.apple.VoiceMemos.StopRecording` | Stop Recording |
| `com.apple.VoiceMemos.ToggleRecording` | Voice Memo |
| `com.apple.VoiceMemos.WFAppSettingEntityUpdaterAction` | Change Voice Memos Settings |

### Shortcuts (23 actions)



| Identifier | Title |
|------------|-------|
| `com.apple.VoiceMemos.WFGetAppSettingAction` | Get Voice Memos Settings |
| `com.apple.news.WFGetAppSettingAction` | Get News Settings |
| `com.apple.shortcuts.AddShortcutToHomeScreenAction` | Add Shortcut to Home Screen |
| `com.apple.shortcuts.ChangeShortcutIconAction` | Change Shortcut Icon |
| `com.apple.shortcuts.CreateFolderAction` | Create Folder |
| `com.apple.shortcuts.CreateShortcutiCloudLinkAction` | Create iCloud Link for Shortcut |
| `com.apple.shortcuts.CreateWorkflowAction` | Create Shortcut |
| `com.apple.shortcuts.DeleteWorkflowAction` | Delete Shortcuts |
| `com.apple.shortcuts.GetShortcutAttributesAction` | Get Shortcut Attributes |
| `com.apple.shortcuts.MoveShortcutToFolderAction` | Move Shortcut |
| `com.apple.shortcuts.OpenAppIntent` | Open App |
| `com.apple.shortcuts.OpenNavigationDestinationAction` | Open Folder |
| `com.apple.shortcuts.OpenShortcutsStaticDeepLinks` | Open Shortcuts Settings |
| `com.apple.shortcuts.OpenWorkflowAction` | Open Shortcut |
| `com.apple.shortcuts.RenameShortcutAction` | Rename Shortcut |
| `com.apple.shortcuts.RunShortcutConfigurationIntent` | Shortcut |
| `com.apple.shortcuts.RunShortcutFromCollectionIntent` | Run Shortcut from Folder |
| `com.apple.shortcuts.RunShortcutIntent` | Run Shortcut |
| `com.apple.shortcuts.SearchActionDrawerAction` | Search Shortcuts Actions |
| `com.apple.shortcuts.SearchShortcutsAction` | Search in Shortcuts |
| `com.apple.shortcuts.SetShortcutAttributesAction` | Set Shortcut Attributes |
| `com.apple.shortcuts.ShortcutsFolderConfigurationIntent` | Shortcuts Folder |
| `com.apple.shortcuts.StopWorkflowAction` | Stop Shortcut |

### System Controls (52 actions)

Toggle and set system settings:

| Pattern | Description |
|---------|-------------|
| `Set*` | Set system setting |
| `Toggle*` | Toggle system setting |
| `Update*` | Update system setting value |

Examples:
- `com.apple.Home.SetAttributeValueIntent` - Set Attribute
- `com.apple.Home.ToggleAttributeIntent` - Toggle Attribute
- `com.apple.AddressBook.UpdateContactIntent` - Update Contact Details

### Data & Search (37 actions)

| Pattern | Description |
|---------|-------------|
| `Find*` | Find/search items |
| `Get*` | Get data |
| `Search*` | Search for content |

Examples:
- `com.apple.Safari.FindOnPage` - Find on Page
- `com.apple.Home.GetAttributeValueIntent` - Get Attribute
- `com.apple.AddressBook.SearchInContactsIntent` - Search in Contacts App

------------|-------|
| `OpenAboutSettingsStaticDeepLinks` | Open About |
| `OpenAirDropSettingsStaticDeepLinks` | Open AirDrop |
| `OpenAppleIDSettingsStaticDeepLinks` | Open Apple ID |
| `OpenBatterySettingsStaticDeepLinks` | Open Battery |
| `OpenBluetoothSettingsStaticDeepLinks` | Open Bluetooth |
| `OpenDisplaySettingsStaticDeepLinks` | Open Display |
| `OpenFamilySettingsStaticDeepLinks` | Open Family |
| `OpenFocusSettingsStaticDeepLinks` | Open Focus |
| `OpenGeneralSettingsStaticDeepLinks` | Open General |
| `OpenInternetAccountsSettingsStaticDeepLinks` | Open Internet Accounts |
| `OpenKeyboardSettingsStaticDeepLinks` | Open Keyboard |
| `OpenLanguageSettingsStaticDeepLinks` | Open Language |
| `OpenNetworkSettingsStaticDeepLinks` | Open Network |
| `OpenNotificationSettingsStaticDeepLinks` | Open Notifications |
| `OpenPasswordsSettingsStaticDeepLinks` | Open Passwords |
| `OpenPrivacySettingsStaticDeepLinks` | Open Privacy |
| `OpenScreenTimeSettingsStaticDeepLinks` | Open Screen Time |
| `OpenSecuritySettingsStaticDeepLinks` | Open Security |
| `OpenSiriSettingsStaticDeepLinks` | Open Siri |
| `OpenSoftwareUpdateSettingsStaticDeepLinks` | Open Software Update |
| `OpenSoundSettingsStaticDeepLinks` | Open Sound |
| `OpenStorageSettingsStaticDeepLinks` | Open Storage |
| `OpenTrackpadSettingsStaticDeepLinks` | Open Trackpad |
| `OpenWalletSettingsStaticDeepLinks` | Open Wallet |
| `OpenWiFiSettingsStaticDeepLinks` | Open WiFi |

### Accessibility (164 actions)

Accessibility settings and controls:

| Identifier Pattern | Description |
|-------------------|-------------|
| `OpenAccessibility*StaticDeepLinks` | Open specific accessibility pane |
| `UpdateAx*EntityValueIntent` | Update accessibility setting value |
| `ToggleAx*` | Toggle accessibility feature |

Examples:
- `OpenAccessibilityVoiceOverStaticDeepLinks` - Open VoiceOver
- `OpenAccessibilityZoomStaticDeepLinks` - Open Zoom
- `OpenAccessibilitySwitchControlStaticDeepLinks` - Open Switch Control
- `UpdateAxVoiceOverSpeakingRateEntityValueIntent` - Update VoiceOver rate
- `ToggleAxVoiceOverIntent` - Toggle VoiceOver

### Clock & Alarms (23 actions)

| Identifier | Description |
|------------|-------------|
| `CreateAlarmIntent` | Create new alarm |
| `DeleteAlarmIntent` | Delete alarm |
| `ToggleAlarmIntent` | Toggle alarm on/off |
| `CreateTimerIntent` | Create timer |
| `PauseTimerIntent` | Pause timer |
| `ResumeTimerIntent` | Resume timer |
| `CancelTimerIntent` | Cancel timer |
| `StartStopwatchIntent` | Start stopwatch |
| `ResetStopwatchIntent` | Reset stopwatch |

### Calendar (5 actions)

| Identifier | Description |
|------------|-------------|
| `CreateCalendarIntent` | Create calendar |
| `DeleteCalendarIntent` | Delete calendar |
| `OpenCalendarScreenIntent` | Open calendar view |
| `CloseCalendarScreenIntent` | Close calendar |

### Reminders (12 actions)

| Identifier | Description |
|------------|-------------|
| `CreateReminderListIntent` | Create reminder list |
| `DeleteReminderListIntent` | Delete reminder list |
| `OpenReminderListIntent` | Open reminder list |
| `OpenSmartReminderListIntent` | Open smart list |
| `CompleteReminderIntent` | Complete reminder |

### Notes (8 actions)

| Identifier | Description |
|------------|-------------|
| `CreateNoteFolderIntent` | Create folder |
| `DeleteNoteFolderIntent` | Delete folder |
| `CreateNoteTagIntent` | Create tag |
| `DeleteNoteTagIntent` | Delete tag |
| `AddTagsToNotesIntent` | Add tags to notes |
| `RemoveTagsFromNotesIntent` | Remove tags |
| `PinNotesIntent` | Pin notes |
| `FindNotesIntent` | Find notes |

### Safari (18 actions)

| Identifier | Description |
|------------|-------------|
| `CreateTabIntent` | Create new tab |
| `CreatePrivateTabIntent` | Create private tab |
| `CloseTabIntent` | Close tab |
| `CreateTabGroupIntent` | Create tab group |
| `OpenTabIntent` | Open tab |
| `OpenTabGroupIntent` | Open tab group |
| `FindBookmarksIntent` | Find bookmarks |
| `FindReadingListItemsIntent` | Find reading list |
| `FindTabsIntent` | Find tabs |
| `FindTabGroupsIntent` | Find tab groups |
| `ChangeReaderModeStateIntent` | Toggle reader mode |

### Home (4 actions)

| Identifier | Description |
|------------|-------------|
| `FindHomeIntent` | Find home |
| `FindHomeDeviceIntent` | Find device |
| `FindHomeSceneIntent` | Find scene |
| `ToggleHomeAccessoryIntent` | Toggle accessory |

### Photos (24 actions)

| Identifier | Description |
|------------|-------------|
| `CreateMemoryIntent` | Create memory |
| `OpenCameraIntent` | Open camera |
| `FindPhotosIntent` | Find photos |
| `FindAlbumsIntent` | Find albums |
| `CreateAlbumIntent` | Create album |

### Music (2 actions)

| Identifier | Description |
|------------|-------------|
| `RecognizeMusicIntent` | Shazam recognition |
| `PlayMusicIntent` | Play music |

### Writing Tools (3 actions)

| Identifier | Description |
|------------|-------------|
| `ProofreadIntent` | Proofread text |
| `RewriteIntent` | Rewrite text |
| `SummarizeIntent` | Summarize text |

### Voice Memos (10 actions)

| Identifier | Description |
|------------|-------------|
| `CreateVoiceMemoFolderIntent` | Create folder |
| `DeleteVoiceMemoFolderIntent` | Delete folder |
| `OpenVoiceMemoFolderIntent` | Open folder |
| `FindVoiceMemosIntent` | Find recordings |
| `PlayVoiceMemoIntent` | Play recording |
| `DeleteVoiceMemosIntent` | Delete recordings |

### Shortcuts (8 actions)

| Identifier | Description |
|------------|-------------|
| `CreateWorkflowIntent` | Create shortcut |
| `DeleteWorkflowIntent` | Delete shortcut |
| `CreateiCloudLinkIntent` | Create iCloud link |
| `SearchShortcutsIntent` | Search shortcuts |
| `RunShortcutIntent` | Run shortcut |

### System Controls (154 actions)

Toggle and set system settings:

| Pattern | Description |
|---------|-------------|
| `Set*ModeIntent` | Set mode (silent, low power, etc.) |
| `Toggle*Intent` | Toggle setting |
| `Update*EntityValueIntent` | Update setting value |
| `Set*SettingIntent` | Set specific setting |

Examples:
- `SetLowPowerModeIntent` - Set low power mode
- `SetAirplaneModeIntent` - Set airplane mode
- `ToggleBluetoothIntent` - Toggle Bluetooth
- `SetBrightnessIntent` - Set brightness
- `SetVolumeIntent` - Set volume

### Data & Search (21 actions)

| Pattern | Description |
|---------|-------------|
| `Find*Intent` | Find/search items |
| `Get*Intent` | Get data |
| `Search*Intent` | Search for content |

Examples:
- `FindSportsEventsIntent` - Find sports events
- `GetPhysicalActivityIntent` - Get physical activity
- `SearchFilesIntent` - Search files

---

## Complete AppIntent Identifier List

All 1632 first-party AppIntent identifiers (full IDs):

### Open* (Settings Deep Links)
```
com.apple.AppStoreSettingsAppIntents.OpenAppStoreSettingsDeepLinkIntent, com.apple.Bridge.OpenAboutDeepLinks, com.apple.Bridge.OpenAccessibilityDeepLinks
com.apple.Bridge.OpenActionButtonDeepLinks, com.apple.Bridge.OpenAppViewDeepLinks, com.apple.Bridge.OpenAssistiveTouchDeepLinks
com.apple.Bridge.OpenCellularDeepLinks, com.apple.Bridge.OpenDisplayBrightnessDeepLinks, com.apple.Bridge.OpenEmergencySOSDeepLinks
com.apple.Bridge.OpenGeneralDeepLinks, com.apple.Bridge.OpenGesturesDeepLinks, com.apple.Bridge.OpenNotificationsDeepLinks
com.apple.Bridge.OpenPasscodeDeepLinks, com.apple.Bridge.OpenPrivacyDeepLinks, com.apple.Bridge.OpenSiriDeepLinks
com.apple.Bridge.OpenSmartStackDeepLinks, com.apple.Bridge.OpenSoundsAndHapticsDeepLinks, com.apple.Bridge.OpenVoiceOverDeepLinks
com.apple.Bridge.OpenZoomDeepLinks, com.apple.ClassKit.ClassKitAppIntents.OpenClassKitAppIntentsDeepLinks, com.apple.Desktop-Settings.extension.OpenDesktopSettingsDeepLink
com.apple.Fitness.OpenActivityRingIntent, com.apple.Fitness.OpenFitnessAppSettingsDeepLinksIntent, com.apple.Fitness.OpenFitnessPlusForYouIntent
com.apple.Fitness.OpenMindfulnessSessionIntent, com.apple.Fitness.OpenUnifiedWorkoutIntent, com.apple.GameCenter.Settings.DeviceExpertExtension.OpenGameCenterSettingsDeepLinks
com.apple.HealthStandaloneIntents.OpenHealthSettingsIntent, com.apple.Home.OpenURLInHomeIntent, com.apple.Maps.MapsSettingsAppIntents.OpenMapsSettingsDeepLink
com.apple.MobileSMS.OpenConversationIntent, com.apple.MobileSMS.OpenConversationListIntent, com.apple.MobileSMS.OpenMessageIntent
com.apple.Notes.OpenAccountLinkAction, com.apple.Notes.OpenAppLocationLinkAction, com.apple.Notes.OpenAttachmentLinkAction
com.apple.Notes.OpenChecklistItemLinkAction, com.apple.Notes.OpenFolderLinkAction, com.apple.Notes.OpenTableLinkAction
com.apple.Notes.OpenTagLinkAction, com.apple.Notes.OpenTopLevelFolderLinkAction, com.apple.Passbook.OpenOrdersIntent
com.apple.Passbook.OpenSavingsAccountEntity, com.apple.Passbook.OpenTransactionEntity, com.apple.Photos.OpenAlbumIntent
com.apple.Photos.OpenAssetIntent, com.apple.Photos.OpenDestinationIntent, com.apple.Photos.OpenMemoryCreationViewIntent
com.apple.Photos.OpenMemoryIntent, com.apple.Photos.OpenPersonIntent, com.apple.Preferences.OpenAirDropBringDevicesTogetherEntity
com.apple.Preferences.OpenAirDropReceivingModeEntity, com.apple.Preferences.OpenAirDropSettingsStaticLinks, com.apple.Preferences.OpenAirDropUseCellularDataEntity
com.apple.Preferences.OpenAmbientSettingsDeepLinks, com.apple.Preferences.OpenCameraSettingsDeepLinks, com.apple.Preferences.OpenContactsDynamicDeepLinks
com.apple.Preferences.OpenControlCenterDeepLinks, com.apple.Preferences.OpenDefaultAppsSettingsDeepLink, com.apple.Preferences.OpenDictionarySettingsDeepLinks
com.apple.Preferences.OpenDisplayAndBrightnessDeepLink, com.apple.Preferences.OpenFaceTimeSettingsDynamicDeepLinks, com.apple.Preferences.OpenFindMySettingsDeepLinks
com.apple.Preferences.OpenFocusSettingsDynamicDeepLinks, com.apple.Preferences.OpenFontSettingsStaticDeepLinks, com.apple.Preferences.OpenHomeScreenAndAppLibraryDeepLink
com.apple.Preferences.OpenMailSettingsDeepLink, com.apple.Preferences.OpenMobilePhoneSettingsDynamicDeepLinks, com.apple.Preferences.OpenMultitaskingAndGesturesDeepLink
com.apple.Preferences.OpenMusicSettingsDeepLink, com.apple.Preferences.OpenNotificationsSettingsDeepLinks, com.apple.Preferences.OpenPasswordManagerDeepLinks
com.apple.Preferences.OpenPasswordSettingsDeepLinks, com.apple.Preferences.OpenPhotosDeepLinks, com.apple.Preferences.OpenSafetyCheckDeepLinks
com.apple.Preferences.OpenScreenTimeDeepLinksIntent, com.apple.Preferences.OpenScreenshotServicesSettingsDeepLinkIntent, com.apple.Preferences.OpenSettingsCellularDeepLinks
com.apple.Preferences.OpenSettingsDeepLink, com.apple.Preferences.OpenSettingsSOSDeepLinks, com.apple.Preferences.OpenTVProviderDeepLinks
com.apple.Preferences.OpenTwentyFourHourTimeEntity, com.apple.Preferences.OpenWalletDeepLinksIntent, com.apple.Preferences.OpeniCloudCalendarSettingsDeepLinks
com.apple.Preferences.OpeniCloudMailSettingsDeepLinks, com.apple.Preview.OpenIntent, com.apple.Safari.OpenBookmark
com.apple.Safari.OpenBookmarkAssistantIntent, com.apple.Safari.OpenTab, com.apple.Safari.OpenTabGroup
com.apple.Safari.OpenTabGroupForFocus, com.apple.Safari.OpenView, com.apple.TransparencySettingsIntents.OpenTransparencyPublicVerificationCodeDeepLink
com.apple.TransparencySettingsIntents.OpenTransparencyStatusDeepLink, com.apple.VoiceMemos.OpenFolder, com.apple.VoiceMemos.OpenResetAnalyticsIdentifierEntity
com.apple.clock.OpenAlarmIntent, com.apple.clock.OpenTab, com.apple.clock.OpenTabIntent
com.apple.compass.CompassSettingsAppIntents.OpenCompassSettingsDeepLink, com.apple.donotdisturb.DoNotDisturbAppIntents.OpenFocusSettingsDynamicDeepLinks, com.apple.finder.OpenItemIntent
com.apple.iBooksX.OpenBookIntent, com.apple.iBooksX.OpenDefaultCollectionIntent, com.apple.iBooksX.OpenMostRecentBookIntent
com.apple.iBooksX.OpenSpecificBookIntent, com.apple.iBooksX.OpenTabBarItemIntent, com.apple.iBooksX.OpenTableOfContentsIntent
com.apple.iCal.OpenCalendarEditorIntent, com.apple.iCal.OpenCalendarViewIntent, com.apple.iCal.OpenDateIntent
com.apple.iCal.OpenEventDetailsIntent, com.apple.iCal.OpenEventEditorIntent, com.apple.intelligenceflow.IntelligenceFlowAppIntentsExtension.OpenApplication
com.apple.intelligenceflow.IntelligenceFlowAppIntentsExtension.OpenFile, com.apple.intelligenceflow.IntelligenceFlowAppIntentsExtension.OpenURL, com.apple.journal.OpenEntryEntityIntent
com.apple.journal.OpenJournalSettingsDeeplinks, com.apple.mail.OpenDraftIntent, com.apple.mail.OpenDraftURLIntent
com.apple.mail.OpenMessageURLIntent, com.apple.mobilecal.OpenSettingsCalendarStaticDeepLinks, com.apple.mobilesafari.OpenLinksInBackgroundEntity
com.apple.mobilesafari.OpenLinksInBackgroundEntity-UpdatableEntity, com.apple.mobilesafari.OpenSafariSettingDeepLinks, com.apple.news.OpenArticleIntent
com.apple.news.OpenFeedIntent, com.apple.news.OpenHistoryIntent, com.apple.news.OpenNewsSettingsAutomaticDownloadDynamicDeepLinks
com.apple.news.OpenNewsSettingsDynamicDeepLinks, com.apple.news.OpenRecipeIntent, com.apple.news.OpenSavedIntent
com.apple.news.OpenSavedRecipesIntent, com.apple.news.OpenStaticFeed, com.apple.omniSearch.SearchToolExtension.OpenFlightReservationEntityIntent
com.apple.omniSearch.SearchToolExtension.OpenGenericEventEntityIntent, com.apple.omniSearch.SearchToolExtension.OpenHotelReservationEntityIntent, com.apple.omniSearch.SearchToolExtension.OpenIDCardBusinessEntityIntent
com.apple.omniSearch.SearchToolExtension.OpenIDCardPersonalEntityIntent, com.apple.omniSearch.SearchToolExtension.OpenMediaEntityIntent, com.apple.omniSearch.SearchToolExtension.OpenRestaurantReservationEntityIntent
com.apple.omniSearch.SearchToolExtension.OpenSearchSpotlightEntityIntent, com.apple.omniSearch.SearchToolExtension.OpenTicketedShowEntityIntent, com.apple.omniSearch.SearchToolExtension.OpenTicketedTransportationEntityIntent
com.apple.omniSearch.SearchToolExtension.OpenVehicleReservationEntityIntent, com.apple.podcasts.OpenAppLocationAppIntent, com.apple.podcasts.OpenChannelAppIntent
com.apple.podcasts.OpenEpisodeAppIntent, com.apple.podcasts.OpenShowAppIntent, com.apple.reminders.OpenGroupAppIntent
com.apple.reminders.OpenIncludeDueTodayDeepLink, com.apple.reminders.OpenMuteNotificationsDeepLink, com.apple.reminders.OpenReminderAppIntent
com.apple.reminders.OpenRemindersSettingsDeepLink, com.apple.reminders.OpenSectionAppIntent, com.apple.reminders.OpenShowAsOverdueDeepLink
com.apple.reminders.OpenShowSuggestionsDeepLink, com.apple.reminders.OpenSmartListAppIntent, com.apple.reminders.OpenTagsAppIntent
com.apple.reminders.OpenTodayNotificationDeepLink, com.apple.shortcuts.OpenAppIntent, com.apple.shortcuts.OpenNavigationDestinationAction
com.apple.shortcuts.OpenShortcutsStaticDeepLinks, com.apple.shortcuts.OpenWorkflowAction, com.apple.siri.AssistantSettingsControls.OpenAlwaysPrintSiriResponseEntity
com.apple.siri.AssistantSettingsControls.OpenAlwaysShowSpeechEntity, com.apple.siri.AssistantSettingsControls.OpenAskSiriEntity, com.apple.siri.AssistantSettingsControls.OpenKeyboardShortcutEntity
com.apple.siri.AssistantSettingsControls.OpenSiriAndDictationHistoryEntity, com.apple.siri.AssistantSettingsControls.OpenSiriLanguageEntity, com.apple.siri.AssistantSettingsControls.OpenSiriSuggestionsAndPrivacyEntity
com.apple.siri.AssistantSettingsControls.OpenSiriSuggestionsAndPrivacyForAppEntity, com.apple.siri.AssistantSettingsControls.OpenSiriSuggestionsShowInAppEntity, com.apple.siri.AssistantSettingsControls.OpenSiriVoiceEntity
com.apple.siri.AssistantSettingsControls.OpenVoiceFeedbackToggleEntity, com.apple.springboard.OpenCamera, com.apple.stocks.OpenArticleIntent
com.apple.stocks.OpenBusinessNewsIntent, com.apple.stocks.OpenFeedIntent, com.apple.stocks.OpenHistoryIntent
com.apple.stocks.OpenRecipeIntent, com.apple.stocks.OpenSavedIntent, com.apple.stocks.OpenSavedRecipesIntent
com.apple.stocks.OpenStaticFeed, com.apple.stocks.OpenSymbolIntent, com.apple.stocks.OpenWatchlistIntent
com.apple.systempreferences.OpenAboutSettingsStaticDeepLinks, com.apple.systempreferences.OpenAccessibilityAudioDescriptionsStaticDeepLinks, com.apple.systempreferences.OpenAccessibilityAudioStaticDeepLinks
com.apple.systempreferences.OpenAccessibilityCaptionsStaticDeepLinks, com.apple.systempreferences.OpenAccessibilityDisplayStaticDeepLinks, com.apple.systempreferences.OpenAccessibilityHearingDevicesStaticDeepLinks
com.apple.systempreferences.OpenAccessibilityHoverTextStaticDeepLinks, com.apple.systempreferences.OpenAccessibilityKeyboardStaticDeepLinks, com.apple.systempreferences.OpenAccessibilityLiveCaptionsStaticDeepLinks
com.apple.systempreferences.OpenAccessibilityLiveSpeechStaticDeepLinks, com.apple.systempreferences.OpenAccessibilityMotionStaticDeepLinks, com.apple.systempreferences.OpenAccessibilityPersonalVoiceStaticDeepLinks
com.apple.systempreferences.OpenAccessibilityPointerControlStaticDeepLinks, com.apple.systempreferences.OpenAccessibilityRTTStaticDeepLinks, com.apple.systempreferences.OpenAccessibilityRootStaticDeepLinks
com.apple.systempreferences.OpenAccessibilityShortcutStaticDeepLinks, com.apple.systempreferences.OpenAccessibilitySiriStaticDeepLinks, com.apple.systempreferences.OpenAccessibilitySpokenContentStaticDeepLinks
com.apple.systempreferences.OpenAccessibilitySwitchControlStaticDeepLinks, com.apple.systempreferences.OpenAccessibilityVocalShortcutsStaticDeepLinks, com.apple.systempreferences.OpenAccessibilityVoiceControlStaticDeepLinks
com.apple.systempreferences.OpenAccessibilityVoiceOverStaticDeepLinks, com.apple.systempreferences.OpenAccessibilityZoomStaticDeepLinks, com.apple.systempreferences.OpenAirDropHandoffDeepLinks
com.apple.systempreferences.OpenAppearanceSettingsDeepLink, com.apple.systempreferences.OpenAppleAccountMainDeepLink, com.apple.systempreferences.OpenApplicationNotificationsSettings
com.apple.systempreferences.OpenAutoBrightnessEntityDeepLink, com.apple.systempreferences.OpenAutomaticReconnectEntityDeepLink, com.apple.systempreferences.OpenAutomaticallySetDateTimeSetting
com.apple.systempreferences.OpenAutomaticallySetTimeZoneSetting, com.apple.systempreferences.OpenBatteryHealthPaneDynamicDeepLinks, com.apple.systempreferences.OpenBatteryOptionsPaneDynamicDeepLinks
com.apple.systempreferences.OpenBatterySettingsPaneDynamicDeepLinks, com.apple.systempreferences.OpenBiometricsAndPasswordSettingsEntityDeepLinks, com.apple.systempreferences.OpenBluetoothPowerDeepLink
com.apple.systempreferences.OpenBluetoothSettingsDeepLinks, com.apple.systempreferences.OpenClassKitAppIntentsDeepLinks, com.apple.systempreferences.OpenClassroomDynamicDeepLinks
com.apple.systempreferences.OpenClockOptionsEntity, com.apple.systempreferences.OpenConfiguredInternetAccountSettings, com.apple.systempreferences.OpenControlCenterModule
com.apple.systempreferences.OpenCurrentTimeZoneSetting, com.apple.systempreferences.OpenDateTimeDeepLinks, com.apple.systempreferences.OpenDesktopSettingsDeepLink
com.apple.systempreferences.OpenDesktopSettingsEntity, com.apple.systempreferences.OpenDeviceManagementStaticDeepLinks, com.apple.systempreferences.OpenDisplaysSettingsDeepLinks
com.apple.systempreferences.OpenDockSettingsEntity, com.apple.systempreferences.OpenEnergySaverPaneDynamicDeepLinks, com.apple.systempreferences.OpenFamilyMemberSettings
com.apple.systempreferences.OpenFamilySettings, com.apple.systempreferences.OpenFamilySetup, com.apple.systempreferences.OpenFamilySubscriptions
com.apple.systempreferences.OpenInternationalSettingsDeepLink, com.apple.systempreferences.OpenInternetAccountsSettings, com.apple.systempreferences.OpenKeyboardSettingsDeepLink
com.apple.systempreferences.OpenLockScreenDeepLinks, com.apple.systempreferences.OpenLoginItemsDeepLinks, com.apple.systempreferences.OpenMagicEdgeEntityDeepLink
com.apple.systempreferences.OpenMissionControlSettingsEntity, com.apple.systempreferences.OpenMouseDeepLink, com.apple.systempreferences.OpenNetworkSettingsDeepLinks
com.apple.systempreferences.OpenNewDeviceOutreachStaticDeepLinks, com.apple.systempreferences.OpenNotificationCenterEntity, com.apple.systempreferences.OpenNotificationSummarizationEntity
com.apple.systempreferences.OpenPrinterScannerDeepLinks, com.apple.systempreferences.OpenPrivacySecurityDeepLinks, com.apple.systempreferences.OpenSUSDeepLinks
com.apple.systempreferences.OpenShareKeyboardEntityDeepLink, com.apple.systempreferences.OpenSoundSettingsDeepLinks, com.apple.systempreferences.OpenSoundSettingsFeedbackSoundEntity
com.apple.systempreferences.OpenSoundSettingsInterfaceEffectsEntity, com.apple.systempreferences.OpenSoundSettingsStartupSoundEntity, com.apple.systempreferences.OpenSpotlightSettingsDeepLinks
com.apple.systempreferences.OpenStartupDiskStaticDeepLinks, com.apple.systempreferences.OpenStorageSettingsDeeplinks, com.apple.systempreferences.OpenTheCurrentDateTimeSetting
com.apple.systempreferences.OpenTimeMachineSettingsStaticDeepLinks, com.apple.systempreferences.OpenTrackpadDeepLinks, com.apple.systempreferences.OpenTransferResetDeepLinks
com.apple.systempreferences.OpenTrueToneEntityDeepLink, com.apple.systempreferences.OpenTwentyFourHourTimeSetting, com.apple.systempreferences.OpenUsersGroupsDeepLinks
com.apple.systempreferences.OpenVPNDeepLink, com.apple.systempreferences.OpenWallpaperDeepLinks, com.apple.systempreferences.OpenWidgetSettingsEntity
com.apple.systempreferences.OpenWindowsSettingsEntity, com.apple.systempreferences.SharingSettingsIntents.OpenSharingDeepLinks, com.apple.weather.OpenMoonIntent
com.apple.weather.OpenNotificationsConfigurationIntent, com.apple.weather.OpenSunriseSunsetIntent, com.apple.weather.OpenUnitsConfigurationIntent
com.apple.weather.OpenWeatherAirQualityIntent, com.apple.weather.OpenWeatherSpecificConditionIntent
```

### Create* (Creation Actions)
```
com.apple.AddressBook.CreateContactIntent, com.apple.Notes.CreateChecklistItemLinkAction, com.apple.Notes.CreateFolderLinkAction
com.apple.Notes.CreateNoteFromMarkdownLinkAction, com.apple.Notes.CreateTableLinkAction, com.apple.Notes.CreateTagLinkAction
com.apple.Photos.CreateAlbumIntent, com.apple.Photos.CreateAssetsIntent, com.apple.Safari.CreateNewBookmark
com.apple.Safari.CreateNewTab, com.apple.Safari.CreateNewTabGroup, com.apple.Safari.CreateNewWindow
com.apple.Safari.CreateTabAssistantIntent, com.apple.VoiceMemos.CreateFolder, com.apple.finder.CreateFolderIntent
com.apple.iCal.CreateCalendarIntent, com.apple.iCal.CreateEventIntent, com.apple.iCal.CreateEventIntent_v0
com.apple.journal.CreateEntryAudioIntent, com.apple.journal.CreateEntryIntent, com.apple.mobilenotes.CreateTagLinkAction
com.apple.reminders.CreateCustomSmartListAppIntent, com.apple.reminders.CreateGroupAppIntent, com.apple.reminders.CreateQuickReminderIntent
com.apple.reminders.CreateSectionAppIntent, com.apple.shortcuts.CreateFolderAction, com.apple.shortcuts.CreateShortcutiCloudLinkAction
com.apple.shortcuts.CreateWorkflowAction
```

### Toggle* (Toggle Actions)
```
com.apple.Home.ToggleAttributeIntent, com.apple.Home.ToggleControlConfigurationIntent, com.apple.Home.ToggleIntent
com.apple.ShortcutsActions.ToggleCellularPlanAction, com.apple.Spotlight.ToggleSpotlightIntent, com.apple.VoiceMemos.ToggleRecording
com.apple.news.ToggleAudioPlaybackIntent, com.apple.springboard.ToggleFlashlight, com.apple.systempreferences.ToggleHighPowerModeBatteryNoBatteryIntent
com.apple.systempreferences.ToggleHighPowerModeOnBatteryIntent, com.apple.systempreferences.ToggleLowPowerModeIntent
```

### Set* (Setting Actions)
```
com.apple.Bridge.SettingsNavigationEventDonationIntent, com.apple.DocumentsApp.SetFilenameExtensionVisibilityIntent, com.apple.DocumentsApp.SetGroupingModeIntent
com.apple.Fitness.SetFitnessGoalIntent, com.apple.Fitness.SetFitnessGoalScheduleIntent, com.apple.Fitness.SetWorkoutEffortIntent
com.apple.Home.SetAttributeValueIntent, com.apple.Notes.SetAttachmentSizeLinkAction, com.apple.Notes.SetChecklistItemCheckedLinkActionv2
com.apple.Notes.SetParagraphStyleLinkAction, com.apple.Passbook.SetDefaultCardIntent, com.apple.Photos.SetApertureIntent
com.apple.Photos.SetAudioMixIntent, com.apple.Photos.SetExposureIntent, com.apple.Photos.SetPlaybackRateIntent
com.apple.Photos.SetSaturationIntent, com.apple.Photos.SetWarmthIntent, com.apple.Preferences.SettingsCellularDeepLinks
com.apple.Preferences.SettingsDeepLink, com.apple.Preferences.SettingsNavigationEventDonationIntent, com.apple.ShortcutsActions.SetDataRoamingAction
com.apple.ShortcutsActions.SetDefaultCellularPlanAction, com.apple.ShortcutsActions.SetSilentModeAction, com.apple.ShortcutsActions.SetVoiceDataModeAction
com.apple.controlcenter.SetDarkModeEnabledIntent, com.apple.controlcenter.SetNightShiftEnabledIntent, com.apple.controlcenter.SetTrueToneEnabledIntent
com.apple.dock.SetDockAutoHideEnabledIntent, com.apple.donotdisturb.DoNotDisturbAppIntents.SetFocusState, com.apple.homed.SetPersonalContentSettingIntent
com.apple.iCal.SetCalendarFocusConfiguration, com.apple.mail.SetMailMessageIsRead, com.apple.mail.SetReadLaterIntent
com.apple.mobilecal.SettingsAllDayDefaultAlertTimesEntity, com.apple.mobilecal.SettingsAllDayDefaultAlertTimesEntity-UpdatableEntity, com.apple.mobilecal.SettingsAlternateCalendarEntity
com.apple.mobilecal.SettingsAlternateCalendarEntity-UpdatableEntity, com.apple.mobilecal.SettingsBirthdaysDefaultAlertTimesEntity, com.apple.mobilecal.SettingsBirthdaysDefaultAlertTimesEntity-UpdatableEntity
com.apple.mobilecal.SettingsDurationForNewEventsEntity, com.apple.mobilecal.SettingsDurationForNewEventsEntity-UpdatableEntity, com.apple.mobilecal.SettingsEventsDefaultAlertTimesEntity
com.apple.mobilecal.SettingsEventsDefaultAlertTimesEntity-UpdatableEntity, com.apple.mobilecal.SettingsShowInviteeDeclinesEntity, com.apple.mobilecal.SettingsShowInviteeDeclinesEntity-UpdatableEntity
com.apple.mobilecal.SettingsShowLocationSuggestionsEntity, com.apple.mobilecal.SettingsShowLocationSuggestionsEntity-UpdatableEntity, com.apple.mobilecal.SettingsShowWeekNumbersEntity
com.apple.mobilecal.SettingsShowWeekNumbersEntity-UpdatableEntity, com.apple.mobilecal.SettingsStartWeekOnEntity, com.apple.mobilecal.SettingsStartWeekOnEntity-UpdatableEntity
com.apple.mobilecal.SettingsSyncDurationsEntity, com.apple.mobilecal.SettingsSyncDurationsEntity-UpdatableEntity, com.apple.mobilecal.SettingsTimeToLeaveEntity
com.apple.mobilecal.SettingsTimeToLeaveEntity-UpdatableEntity, com.apple.mobilecal.SettingsWeekViewStartsOnTodayEntity, com.apple.mobilecal.SettingsWeekViewStartsOnTodayEntity-UpdatableEntity
com.apple.shortcuts.SetShortcutAttributesAction, com.apple.springboard.SetAppearanceStyleIntent, com.apple.springboard.SetFlashlightIntent
com.apple.springboard.SetSilentModeIntent, com.apple.systempreferences.SetupFamilyDeepLink, com.apple.wallpaper.agent.SetWallpaperIntent
com.apple.wallpaper.agent.SetWallpaperPhotoIntent, com.apple.weather.SetDistanceUnitIntent, com.apple.weather.SetPrecipitationUnitIntent
com.apple.weather.SetPressureUnitIntent, com.apple.weather.SetTemperatureUnitIntent, com.apple.weather.SetWindUnitIntent
```

### Find* (Search Actions)
```
com.apple.Safari.FindOnPage, com.apple.intelligenceplatform.IntelligencePlatform.IntelligencePlatformDataActionsAppIntentsExtension.FindSportsEvents
```

### All AppIntent Identifiers (full IDs)
```
com.apple.AddressBook.ContactEntity
com.apple.AddressBook.CreateContactIntent
com.apple.AddressBook.DeleteContactIntent
com.apple.AddressBook.FetchContactAvatarIntent
com.apple.AddressBook.FetchContactIntent
com.apple.AddressBook.SearchInContactsIntent
com.apple.AddressBook.UpdateContactIntent
com.apple.AddressBook.ViewContactCardIntent
com.apple.AppKit.FetchIntelligenceCommands
com.apple.AppKit.InsertIntelligenceText
com.apple.AppKit.RunIntelligenceCommand
com.apple.AppKit.RunIntelligenceCommandForKey
com.apple.AppKit.WindowTabActivateIntent
com.apple.AppKit.WindowTabEntity
com.apple.AppKit.WritingToolsComposeIntent
com.apple.AppKit.WritingToolsProofreadIntent
com.apple.AppKit.WritingToolsRewriteIntent
com.apple.AppStore.SystemSearchIntent
com.apple.Desktop-Settings.extension.OpenDesktopSettingsDeepLink
com.apple.GameCenter.Settings.DeviceExpertExtension.OpenGameCenterSettingsDeepLinks
com.apple.GenerativePlaygroundApp.GenerateImageIntent
com.apple.Home.ActivateSceneIntent
com.apple.Home.AutomateAttributeValueIntent
com.apple.Home.AutomateSceneIntent
com.apple.Home.CameraClipEntity
com.apple.Home.DeltaAttributeValueIntent
com.apple.Home.DeviceEntity
com.apple.Home.ErrorIntent
com.apple.Home.ForecastWidgetConfiguration
com.apple.Home.GetAttributeValueIntent
com.apple.Home.GetDeviceInfoIntent
com.apple.Home.HistoricalUsageWidgetConfiguration
com.apple.Home.HomeAppIntentsExtensionTestAppIntent
com.apple.Home.HomeEntity
com.apple.Home.HomeSingleTileConfigurationIntent
com.apple.Home.HomeXLModuleConfigurationIntent
com.apple.Home.OpenURLInHomeIntent
com.apple.Home.RecommendedItemIntent
com.apple.Home.RoomEntity
com.apple.Home.SceneEntity
com.apple.Home.SecureToggleIntent
com.apple.Home.SelectedHomeEntity
com.apple.Home.SetAttributeValueIntent
com.apple.Home.ShowDeviceResultIntent
com.apple.Home.ShowErrorIntent
com.apple.Home.ShowNavigationIntent
com.apple.Home.ShowSceneResultIntent
com.apple.Home.TileControlAction
com.apple.Home.ToggleAttributeIntent
com.apple.Home.ToggleControlConfigurationIntent
com.apple.Home.ToggleIntent
com.apple.Home.UtilityRateInfoWidgetConfiguration
com.apple.Home.ZoneEntity
com.apple.HydraUSDAppIntents.ConvertToUSDZ
com.apple.Magnifier.DescribeThisIntent
com.apple.Magnifier.DetectDoorsIntent
com.apple.Magnifier.DetectFurnitureIntent
com.apple.Magnifier.DetectPeopleIntent
com.apple.Magnifier.DetectTextIntent
com.apple.Magnifier.MagnifierIntent
com.apple.Magnifier.PointAndSpeakIntent
com.apple.Magnifier.ReaderModeIntent
com.apple.Magnifier.StartDetectionTypeIntent
com.apple.MobileSMS.ChangeFilterModeIntent
com.apple.MobileSMS.ConversationEntity
com.apple.MobileSMS.ConversationListFocusFilterAction
com.apple.MobileSMS.DeleteConversationIntent
com.apple.MobileSMS.DeleteMessageIntent
com.apple.MobileSMS.FetchConversationIdentifierIntent
com.apple.MobileSMS.FetchDowntimeConversationListIntent
com.apple.MobileSMS.FetchMutedConversationListIntent
com.apple.MobileSMS.MarkConversationAsUnreadIntent
com.apple.MobileSMS.MessageEntity
com.apple.MobileSMS.MuteConversationIntent
com.apple.MobileSMS.OpenConversationIntent
com.apple.MobileSMS.OpenConversationListIntent
com.apple.MobileSMS.OpenMessageIntent
com.apple.MobileSMS.RemoveTapbackIntent
com.apple.MobileSMS.SendMessageReactionIntent
com.apple.MobileSMS.SendReplyIntent
com.apple.MobileSMS.SendTapbackIntent
com.apple.Notes.AddFileAttachmentLinkAction
com.apple.Notes.AddLinkAttachmentLinkAction
com.apple.Notes.AddOrRemoveNoteLockLinkAction
com.apple.Notes.AddTagsToNotesLinkAction
com.apple.Notes.AppendMarkdownToNoteLinkAction
com.apple.Notes.ApplyFormattingLinkAction
com.apple.Notes.AttachmentEntity
com.apple.Notes.ChangeFolderSettingLinkAction
com.apple.Notes.ChangeSettingLinkAction
com.apple.Notes.ChangeTagSelectionIntent
com.apple.Notes.CloseAppLocationLinkAction
com.apple.Notes.CloseNoteLinkAction
com.apple.Notes.CreateChecklistItemLinkAction
com.apple.Notes.CreateFolderLinkAction
com.apple.Notes.CreateNoteFromMarkdownLinkAction
com.apple.Notes.CreateTableLinkAction
com.apple.Notes.CreateTagLinkAction
com.apple.Notes.DeleteAttachmentsLinkAction
com.apple.Notes.DeleteChecklistItemsLinkAction
com.apple.Notes.DeleteFoldersLinkAction
com.apple.Notes.DeleteNotesLinkAction
com.apple.Notes.DeleteTablesLinkAction
com.apple.Notes.DeleteTagsLinkAction
com.apple.Notes.GetLinkedNotesLinkAction
com.apple.Notes.InsertAllMentionLinkAction
com.apple.Notes.InsertMentionLinkAction
com.apple.Notes.InsertNoteLinkLinkAction
com.apple.Notes.MoveNotesToFolderLinkAction
com.apple.Notes.OpenAccountLinkAction
com.apple.Notes.OpenAppLocationLinkAction
com.apple.Notes.OpenAttachmentLinkAction
com.apple.Notes.OpenChecklistItemLinkAction
com.apple.Notes.OpenFolderLinkAction
com.apple.Notes.OpenTableLinkAction
com.apple.Notes.OpenTagLinkAction
com.apple.Notes.OpenTopLevelFolderLinkAction
com.apple.Notes.PinNotesLinkAction
com.apple.Notes.QuickNoteIntent
com.apple.Notes.RemoveTagsFromNotesLinkAction
com.apple.Notes.RenameFolderLinkAction
com.apple.Notes.ReplaceSelectionLinkAction
com.apple.Notes.SetAttachmentSizeLinkAction
com.apple.Notes.SetChecklistItemCheckedLinkActionv2
com.apple.Notes.SetParagraphStyleLinkAction
com.apple.Notes.ShowNotesAppSearchResultsLinkAction
com.apple.Notes.ShowQuickNoteIntent
com.apple.Notes.StartRecordingLinkAction
com.apple.Notes.TableEntity
com.apple.PeopleViewService.SelectPersonIntent
com.apple.PeopleViewService.URLAppIntent
com.apple.Photos.AddAssetsToAlbumIntent
com.apple.Photos.ApplyFilterIntent
com.apple.Photos.ApplyStyleIntent
com.apple.Photos.CleanupIntent
com.apple.Photos.CopyEditsIntent
com.apple.Photos.CreateAlbumIntent
com.apple.Photos.CreateAssetsIntent
com.apple.Photos.CropIntent
com.apple.Photos.DeleteAlbumsIntent
com.apple.Photos.DeleteAssetsIntent
com.apple.Photos.DuplicateAssetsIntent
com.apple.Photos.EditAssetIntent
com.apple.Photos.EnableDepthIntent
com.apple.Photos.EnhanceIntent
com.apple.Photos.FavoriteAssetsIntent
com.apple.Photos.FavoriteMemoriesIntent
com.apple.Photos.FavoritePeopleIntent
com.apple.Photos.FilterLibraryIntent
com.apple.Photos.HideAssetsIntent
com.apple.Photos.HidePeopleIntent
com.apple.Photos.MarkupIntent
com.apple.Photos.MoveAssetsToPersonalLibraryIntent
com.apple.Photos.MoveAssetsToSharedLibraryIntent
com.apple.Photos.OpenAlbumIntent
com.apple.Photos.OpenAssetIntent
com.apple.Photos.OpenDestinationIntent
com.apple.Photos.OpenMemoryCreationViewIntent
com.apple.Photos.OpenMemoryIntent
com.apple.Photos.OpenPersonIntent
com.apple.Photos.PLPhotosReliveWidgetConfigurationIntent
com.apple.Photos.PasteEditsIntent
com.apple.Photos.PhotosAddAssetsToAlbumAssistantIntent
com.apple.Photos.PhotosCleanupPhotoAssistantIntent
com.apple.Photos.PhotosCopyEditsAssistantIntent
com.apple.Photos.PhotosCreateAlbumAssistantIntent
com.apple.Photos.PhotosCreateAssetsAssistantIntent
com.apple.Photos.PhotosCropAssistantIntent
com.apple.Photos.PhotosDeleteAlbumsAssistantIntent
com.apple.Photos.PhotosDeleteAssetsAssistantIntent
com.apple.Photos.PhotosDuplicateAssetsAssistantIntent
com.apple.Photos.PhotosPasteEditsAssistantIntent
com.apple.Photos.PhotosReliveWidgetFeaturedConfiguration
com.apple.Photos.PhotosRemoveAssetsFromAlbumAssistantIntent
com.apple.Photos.PhotosSearchAssistantIntent
com.apple.Photos.PhotosSetDepthAssistantIntent
com.apple.Photos.PhotosSetExposureAssistantIntent
com.apple.Photos.PhotosSetFilterAssistantIntent
com.apple.Photos.PhotosSetRotationAssistantIntent
com.apple.Photos.PhotosSetSaturationAssistantIntent
com.apple.Photos.PhotosSetWarmthAssistantIntent
com.apple.Photos.PhotosStraightenAssistantIntent
com.apple.Photos.PhotosToggleDepthAssistantIntent
com.apple.Photos.PhotosToggleSuggestedEditsAssistantIntent
com.apple.Photos.PhotosUpdateAlbumAssistantIntent
com.apple.Photos.PhotosUpdateAssetAssistantIntent
com.apple.Photos.PhotosUpdateRecognizedPersonAssistantIntent
com.apple.Photos.RemoveAssetsFromAlbumIntent
com.apple.Photos.RenameAlbumIntent
com.apple.Photos.RenamePersonIntent
com.apple.Photos.RevealAlbumsIntent
com.apple.Photos.RevealAssetsIntent
com.apple.Photos.RotateIntent
com.apple.Photos.SetApertureIntent
com.apple.Photos.SetAudioMixIntent
com.apple.Photos.SetExposureIntent
com.apple.Photos.SetPlaybackRateIntent
com.apple.Photos.SetSaturationIntent
com.apple.Photos.SetWarmthIntent
com.apple.Photos.StraightenIntent
com.apple.Preview.AutoEnhanceIntent
com.apple.Preview.BookmarkIntent
com.apple.Preview.CloseIntent
com.apple.Preview.DeletePageIntent
com.apple.Preview.DocumentEntity
com.apple.Preview.ExportIntent
com.apple.Preview.FlipIntent
com.apple.Preview.GetPagesIntent
com.apple.Preview.InsertPageIntent
com.apple.Preview.OpenIntent
com.apple.Preview.RemoveBackgroundIntent
com.apple.Preview.ResizeIntent
com.apple.Preview.RevealDocumentIntent
com.apple.Preview.RevealPageIntent
com.apple.Preview.RotateIntent
com.apple.Preview.RotatePageIntent
com.apple.Preview.SaveIntent
com.apple.Preview.SearchIntent
com.apple.Safari.BookmarkEntity
com.apple.Safari.BookmarkTabIntent
com.apple.Safari.BookmarkURLIntent
com.apple.Safari.CloseTab
com.apple.Safari.CloseTabsAssistantIntent
com.apple.Safari.CloseView
com.apple.Safari.CloseWindowsIntent
com.apple.Safari.CreateNewBookmark
com.apple.Safari.CreateNewTab
com.apple.Safari.CreateNewTabGroup
com.apple.Safari.CreateNewWindow
com.apple.Safari.CreateTabAssistantIntent
com.apple.Safari.DeleteBookmarks
com.apple.Safari.DeleteTabGroups
com.apple.Safari.FindOnPage
com.apple.Safari.LoadURLInTab
com.apple.Safari.MoveTabsToTabGroup
com.apple.Safari.MoveTabsToWindowIntent
com.apple.Safari.OpenBookmark
com.apple.Safari.OpenBookmarkAssistantIntent
com.apple.Safari.OpenTab
com.apple.Safari.OpenTabGroup
com.apple.Safari.OpenTabGroupForFocus
com.apple.Safari.OpenView
com.apple.Safari.QuickWebsiteSearchIntent
com.apple.Safari.QuickWebsiteSearchProviderEntity
com.apple.Safari.SearchTabs
com.apple.Safari.ShowWindowIntent
com.apple.Safari.TabEntity
com.apple.Safari.TabGroupEntity
com.apple.Safari.WindowEntity
com.apple.ShortcutsActions.CellularPlanEntity
com.apple.ShortcutsActions.GetOrientationAction
com.apple.ShortcutsActions.GetPhysicalActivity
com.apple.ShortcutsActions.PlayMusicTopHitAction
com.apple.ShortcutsActions.PlayPodcastTopHitAction
com.apple.ShortcutsActions.ResetCellularDataStatisticsAction
com.apple.ShortcutsActions.SetDataRoamingAction
com.apple.ShortcutsActions.SetDefaultCellularPlanAction
com.apple.ShortcutsActions.SetSilentModeAction
com.apple.ShortcutsActions.SetVoiceDataModeAction
com.apple.ShortcutsActions.ShowControlCenterAction
com.apple.ShortcutsActions.StartCallTopHitAction
com.apple.ShortcutsActions.StartFaceTimeAudioCallTopHitAction
com.apple.ShortcutsActions.StartFaceTimeCallTopHitAction
com.apple.ShortcutsActions.StartFaceTimeVideoCallTopHitAction
com.apple.ShortcutsActions.TimeMachineAction
com.apple.ShortcutsActions.ToggleCellularPlanAction
com.apple.ShortcutsActions.TranscribeAudioAction
com.apple.Spotlight.ClearSpotlightIntent
com.apple.Spotlight.SearchFieldEntity
com.apple.Spotlight.SearchSpotlightIntent
com.apple.Spotlight.SearchSpotlightIntentInternal
com.apple.Spotlight.SearchUIContinuationIntent
com.apple.Spotlight.SearchUIOpenKnowledgeIntent
com.apple.Spotlight.ToggleSpotlightIntent
com.apple.TransparencySettingsIntents.OpenTransparencyPublicVerificationCodeDeepLink
com.apple.TransparencySettingsIntents.OpenTransparencyStatusDeepLink
com.apple.TransparencySettingsIntents.TransparencyPublicVerificationCodeEntity
com.apple.TransparencySettingsIntents.TransparencySettingsIntents
com.apple.TransparencySettingsIntents.TransparencyStatusEntity
com.apple.VoiceMemos.AudioQualityEntity
com.apple.VoiceMemos.AudioQualityEntity-UpdatableEntity
com.apple.VoiceMemos.ChangeRecordingPlaybackSetting
com.apple.VoiceMemos.ClearDeletedEntity
com.apple.VoiceMemos.ClearDeletedEntity-UpdatableEntity
com.apple.VoiceMemos.CreateFolder
com.apple.VoiceMemos.DeleteFolder
com.apple.VoiceMemos.DeleteRecording
com.apple.VoiceMemos.LocationBasedNamingEntity
com.apple.VoiceMemos.LocationBasedNamingEntity-UpdatableEntity
com.apple.VoiceMemos.OpenFolder
com.apple.VoiceMemos.OpenResetAnalyticsIdentifierEntity
com.apple.VoiceMemos.PlaybackVoiceMemoIntent
com.apple.VoiceMemos.RCCombineRecordings
com.apple.VoiceMemos.RCControlCenterToggleRecording
com.apple.VoiceMemos.RCImportRecording
com.apple.VoiceMemos.RCRecordingEntity
com.apple.VoiceMemos.RecordVoiceMemoIntent
com.apple.VoiceMemos.ResetAnalyticsIdentifierEntity
com.apple.VoiceMemos.SearchRecordings
com.apple.VoiceMemos.SelectRecording
com.apple.VoiceMemos.StopRecording
com.apple.VoiceMemos.ToggleRecording
com.apple.VoiceMemos.WFAppSettingEntityUpdaterAction
com.apple.VoiceMemos.WFGetAppSettingAction
com.apple.WindowManager.AppExposeAction
com.apple.WindowManager.CornersTileAction
com.apple.WindowManager.MissionControlAction
com.apple.WindowManager.ShowDesktopAction
com.apple.WindowManager.StageManagerToggleIntent
com.apple.WindowManager.ThreeUpTileAction
com.apple.WindowManager.TwoUpTileAction
com.apple.WritingTools.WritingToolsAppIntentsExtension.AdjustToneIntent
com.apple.WritingTools.WritingToolsAppIntentsExtension.FormatListIntent
com.apple.WritingTools.WritingToolsAppIntentsExtension.FormatTableIntent
com.apple.WritingTools.WritingToolsAppIntentsExtension.ProofreadIntent
com.apple.WritingTools.WritingToolsAppIntentsExtension.RewriteTextIntent
com.apple.WritingTools.WritingToolsAppIntentsExtension.SummarizeTextIntent
com.apple.calculator.LaunchCalculatorOpenIntent
com.apple.clock.AddWorldClockIntent
com.apple.clock.CancelTimerIntent
com.apple.clock.DeleteAlarmIntent
com.apple.clock.GetCurrentTimerDetailsIntent
com.apple.clock.GetTimeForCityIntent
com.apple.clock.LapStopwatchIntent
com.apple.clock.OpenAlarmIntent
com.apple.clock.OpenTab
com.apple.clock.OpenTabIntent
com.apple.clock.PauseTimerIntent
com.apple.clock.RemoveWorldClockIntent
com.apple.clock.ResetStopwatchIntent
com.apple.clock.ResumeTimerIntent
com.apple.clock.StartStopwatchIntent
com.apple.clock.StopStopwatchIntent
com.apple.controlcenter.DisplaySleepIntent
com.apple.controlcenter.LockScreenIntent
com.apple.controlcenter.ScreenSaverIntent
com.apple.controlcenter.SetDarkModeEnabledIntent
com.apple.controlcenter.SetNightShiftEnabledIntent
com.apple.controlcenter.SetTrueToneEnabledIntent
com.apple.dock.SetDockAutoHideEnabledIntent
com.apple.donotdisturb.DoNotDisturbAppIntents.FocusEntity
com.apple.donotdisturb.DoNotDisturbAppIntents.OpenFocusSettingsDynamicDeepLinks
com.apple.donotdisturb.DoNotDisturbAppIntents.SetFocusState
com.apple.finder.CompressItemsIntent
com.apple.finder.CopyItemsIntent
com.apple.finder.CreateFolderIntent
com.apple.finder.DuplicateItemsIntent
com.apple.finder.GetInfoIntent
com.apple.finder.GetLocationIntent
com.apple.finder.GetSelectedItemsIntent
com.apple.finder.GoToEnclosingFolderIntent
com.apple.finder.GoToFolderIntent
com.apple.finder.GoToLocationIntent
com.apple.finder.MoveItemsIntent
com.apple.finder.OpenItemIntent
com.apple.finder.RenameItemIntent
com.apple.finder.RevealItemsIntent
com.apple.finder.SearchInBrowserIntent
com.apple.finder.TrashItemsIntent
com.apple.findmy.FriendSelectorIntent
com.apple.findmy.Intent
com.apple.findmy.ItemEntity
com.apple.findmy.ItemSelectorIntent
com.apple.findmy.PersonEntity
com.apple.findmy.WidgetItemEntity
com.apple.findmy.WidgetPersonEntity
com.apple.freeform.CRLAddItemToBoardIntent
com.apple.freeform.CRLAddStickyNoteToBoardIntent
com.apple.freeform.CRLAddTextToBoardIntent
com.apple.freeform.CRLChangeBoardCanvasGridIntent
com.apple.freeform.CRLChangeBoardObjectConnectorsIntent
com.apple.freeform.CRLChangeSelectionColorIntent
com.apple.freeform.CRLChangeSelectionFontSizeIntent
com.apple.freeform.CRLChangeSelectionFontStyleIntent
com.apple.freeform.CRLCreateBoardIntent
com.apple.freeform.CRLDeleteBoardIntent
com.apple.freeform.CRLFavoriteBoardIntent_v2
com.apple.freeform.CRLInsertFilesToBoardIntent
com.apple.freeform.CRLInsertPhotosToBoardIntent
com.apple.freeform.CRLInsertShapeToBoardIntent
com.apple.freeform.CRLInsertTextToBoardIntent
com.apple.freeform.CRLInsertURLToBoardIntent
com.apple.freeform.CRLOpenBoardIntent
com.apple.freeform.CRLRenameBoardIntent
com.apple.freeform.CRLResizeSelectionFontIntent
com.apple.freeform.CRLResizeSelectionFontIntent_v2
com.apple.freeform.CRLUpdateBoardIntent
com.apple.freeform.CRLUtilitiesIntent
com.apple.freeform.CRLiOSCreateBoardIntent
com.apple.freeform.CRLiOSOpenBoardIntent
com.apple.generativeassistanttools.GenerativeAssistantExtension.GenerateKnowledgeResponseIntent
com.apple.generativeassistanttools.GenerativeAssistantExtension.GenerateRichContentFromMediaIntent
com.apple.generativeassistanttools.GenerativeAssistantExtension.GenerateRichContentIntent
com.apple.generativeassistanttools.GenerativeAssistantExtension.PrewarmGenerativeAssistantExtensionIntent
com.apple.helpviewer.CollectionOpenIntent
com.apple.homed.SetPersonalContentSettingIntent
com.apple.iBooksX.AudiobookSleepTimerIntent
com.apple.iBooksX.BookAppEntity
com.apple.iBooksX.BookReaderChangeThemeIntent
com.apple.iBooksX.BookReaderNavigatePageInBookIntent
com.apple.iBooksX.BookReaderNavigatePagesIntent
com.apple.iBooksX.BookSettingsEntity
com.apple.iBooksX.BookSettingsEntity-UpdatableEntity
com.apple.iBooksX.ChangeFontSizeIntent
com.apple.iBooksX.CloseBookIntent
com.apple.iBooksX.DeepLinkIntent
com.apple.iBooksX.DefaultCollectionEntity
com.apple.iBooksX.OpenBookIntent
com.apple.iBooksX.OpenDefaultCollectionIntent
com.apple.iBooksX.OpenMostRecentBookIntent
com.apple.iBooksX.OpenSpecificBookIntent
com.apple.iBooksX.OpenTabBarItemIntent
com.apple.iBooksX.OpenTableOfContentsIntent
com.apple.iBooksX.PauseCurrentAudiobookIntent
com.apple.iBooksX.PlayAudiobookIntent
com.apple.iBooksX.PlayMostRecentAudiobookIntent
com.apple.iBooksX.PlaySpecificAudiobookIntent
com.apple.iBooksX.SearchBooksAppIntent
com.apple.iBooksX.SearchBooksIntent
com.apple.iBooksX.UpdateBookSettingsIntent
com.apple.iCal.CreateCalendarIntent
com.apple.iCal.CreateEventIntent
com.apple.iCal.CreateEventIntent_v0
com.apple.iCal.DeleteCalendarsIntent
com.apple.iCal.DeleteEventIntent
com.apple.iCal.DeleteEventIntent_v0
com.apple.iCal.EditEventIntent
com.apple.iCal.EditEventIntent_v0
com.apple.iCal.EmailAttendeesIntent
com.apple.iCal.EmailOrganizerIntent
com.apple.iCal.EventEntity
com.apple.iCal.FetchTransferableEventByURLIntent
com.apple.iCal.FetchTransferableEventsInRangeIntent
com.apple.iCal.HighlightEventIntent
com.apple.iCal.InboxItemEntity
com.apple.iCal.JoinEventIntent
com.apple.iCal.ListEventsIntent
com.apple.iCal.OpenCalendarEditorIntent
com.apple.iCal.OpenCalendarViewIntent
com.apple.iCal.OpenDateIntent
com.apple.iCal.OpenEventDetailsIntent
com.apple.iCal.OpenEventEditorIntent
com.apple.iCal.RespondToInboxItemIntent
com.apple.iCal.SetCalendarFocusConfiguration
com.apple.iCal.TransferableCalendarEntity
com.apple.iCal.TransferableSourceEntity
com.apple.iWork.Keynote.KNDocumentBackgroundExportIntent
com.apple.iWork.Keynote.KNNewDocumentIntent
com.apple.iWork.Numbers.TNDocumentBackgroundExportIntent
com.apple.iWork.Numbers.TNNewDocumentIntent
com.apple.iWork.Pages.TPDocumentBackgroundExportIntent
com.apple.iWork.Pages.TPNewDocumentIntent
com.apple.intelligenceflow.IntelligenceFlowAppIntentsExtension.OpenApplication
com.apple.intelligenceflow.IntelligenceFlowAppIntentsExtension.OpenFile
com.apple.intelligenceflow.IntelligenceFlowAppIntentsExtension.OpenURL
com.apple.intelligenceplatform.IntelligencePlatform.IntelligencePlatformDataActionsAppIntentsExtension.CalculateAppUsageIntent
com.apple.intelligenceplatform.IntelligencePlatform.IntelligencePlatformDataActionsAppIntentsExtension.FindSportsEvents
com.apple.intelligenceplatformd.PersonalKnowledgeTool
com.apple.journal.AddCurrentLocationEntity
com.apple.journal.AddCurrentLocationEntity-UpdatableEntity
com.apple.journal.AddCurrentLocationIntent
com.apple.journal.AlwaysUseMomentDateEntity
com.apple.journal.AlwaysUseMomentDateEntity-UpdatableEntity
com.apple.journal.AlwaysUseMomentDateIntent
com.apple.journal.CreateEntryAudioIntent
com.apple.journal.CreateEntryIntent
com.apple.journal.OpenEntryEntityIntent
com.apple.journal.OpenJournalSettingsDeeplinks
com.apple.journal.RefreshIntent
com.apple.journal.SaveToPhotosEntity
com.apple.journal.SaveToPhotosEntity-UpdatableEntity
com.apple.journal.SaveToPhotosIntent
com.apple.journal.SearchEntriesIntent
com.apple.journal.SkipJournalingSuggestionsEntity
com.apple.journal.SkipJournalingSuggestionsEntity-UpdatableEntity
com.apple.journal.SkipJournalingSuggestionsIntent
com.apple.journal.StreaksWidgetConfigurationIntent
com.apple.mail.ArchiveMessageIntent
com.apple.mail.BlockSenderIntent
com.apple.mail.CancelDraftIntent
com.apple.mail.ComposeMessageIntent
com.apple.mail.DeleteDraftIntent
com.apple.mail.DeleteMessageIntent
com.apple.mail.DeleteReadLaterIntent
com.apple.mail.ForwardMessageIntent
com.apple.mail.MailFocusConfigurationAction
com.apple.mail.MailMessage
com.apple.mail.MailMessageEntity
com.apple.mail.MuteThreadIntent
com.apple.mail.OpenDraftIntent
com.apple.mail.OpenDraftURLIntent
com.apple.mail.OpenMessageURLIntent
com.apple.mail.RemoveFollowUpIntent
com.apple.mail.ReplyMessageIntent
com.apple.mail.SaveDraftIntent
com.apple.mail.SearchMailIntent
com.apple.mail.SendDraftIntent
com.apple.mail.SendMail
com.apple.mail.SetMailMessageIsRead
com.apple.mail.SetReadLaterIntent
com.apple.mail.SummarizeThreadIntent
com.apple.mail.UndoSendMessageIntent
com.apple.mail.UnsubscribeMessageIntent
com.apple.mail.UpdateDraftIntent
com.apple.mail.UpdateMessageIntent
com.apple.mobilenotes.SharingExtension
com.apple.mobiletimer-framework.MobileTimerIntents.MTCreateAlarmIntent
com.apple.mobiletimer-framework.MobileTimerIntents.MTGetAlarmsIntent
com.apple.mobiletimer-framework.MobileTimerIntents.MTToggleAlarmIntent
com.apple.news.BlockIntent
com.apple.news.DecreaseTextSizeIntent
com.apple.news.FollowIntent
com.apple.news.GameCenterEntity
com.apple.news.GameCenterEntity-UpdatableEntity
com.apple.news.IncreaseTextSizeIntent
com.apple.news.NewsSettingsAutomaticDownloadDynamicDeepLinks
com.apple.news.NewsSettingsDynamicDeepLinks
com.apple.news.NewsTabDeepLink
com.apple.news.OpenArticleIntent
com.apple.news.OpenFeedIntent
com.apple.news.OpenHistoryIntent
com.apple.news.OpenRecipeIntent
com.apple.news.OpenSavedIntent
com.apple.news.OpenSavedRecipesIntent
com.apple.news.OpenStaticFeed
com.apple.news.RestrictStoriesInTodaySettingEntity
com.apple.news.RestrictStoriesInTodaySettingEntity-UpdatableEntity
com.apple.news.SaveArticleIntent
com.apple.news.ToggleAudioPlaybackIntent
com.apple.news.UnblockIntent
com.apple.news.UnsaveArticleIntent
com.apple.news.WFAppSettingEntityUpdaterAction
com.apple.news.WFGetAppSettingAction
com.apple.omniSearch.SearchToolExtension.OpenFlightReservationEntityIntent
com.apple.omniSearch.SearchToolExtension.OpenGenericEventEntityIntent
com.apple.omniSearch.SearchToolExtension.OpenHotelReservationEntityIntent
com.apple.omniSearch.SearchToolExtension.OpenIDCardBusinessEntityIntent
com.apple.omniSearch.SearchToolExtension.OpenIDCardPersonalEntityIntent
com.apple.omniSearch.SearchToolExtension.OpenMediaEntityIntent
com.apple.omniSearch.SearchToolExtension.OpenRestaurantReservationEntityIntent
com.apple.omniSearch.SearchToolExtension.OpenSearchSpotlightEntityIntent
com.apple.omniSearch.SearchToolExtension.OpenTicketedShowEntityIntent
com.apple.omniSearch.SearchToolExtension.OpenTicketedTransportationEntityIntent
com.apple.omniSearch.SearchToolExtension.OpenVehicleReservationEntityIntent
com.apple.omniSearch.SearchToolExtension.SearchTool
com.apple.omniSearch.SearchToolExtension.SearchToolControl
com.apple.omniSearch.SearchToolExtension.SearchToolMCGrounding
com.apple.omniSearch.SearchToolExtension.SearchToolMCQU
com.apple.podcasts.DownloadEpisodesAppIntent
com.apple.podcasts.FetchShowLatestEpisodesAppIntent
com.apple.podcasts.FollowRSSFeedAppIntent
com.apple.podcasts.FollowShowAppIntent
com.apple.podcasts.MarkEpisodeAsPlayedAppIntent
com.apple.podcasts.MarkEpisodeAsUnplayedAppIntent
com.apple.podcasts.OpenAppLocationAppIntent
com.apple.podcasts.OpenChannelAppIntent
com.apple.podcasts.OpenEpisodeAppIntent
com.apple.podcasts.OpenShowAppIntent
com.apple.podcasts.PlayAudioIntent
com.apple.podcasts.PlayEpisodeAppIntent
com.apple.podcasts.PlayEpisodeLastAppIntent
com.apple.podcasts.PlayEpisodeNextAppIntent
com.apple.podcasts.PlayNextChapterAppIntent
com.apple.podcasts.PlayPauseStationAppIntent
com.apple.podcasts.PlayPauseWidgetIntent
com.apple.podcasts.PlayPreviousChapterAppIntent
com.apple.podcasts.PlayStationAppIntent
com.apple.podcasts.RemoveEpisodesDownloadAppIntent
com.apple.podcasts.SaveEpisodeAppIntent
com.apple.podcasts.SearchPodcastsAppIntent
com.apple.podcasts.SelectLibraryListAppIntent
com.apple.podcasts.SelectWidgetShowAppIntent
com.apple.podcasts.UnfollowShowAppIntent
com.apple.podcasts.UnsaveEpisodeAppIntent
com.apple.podcasts.ViewTranscriptAppIntent
com.apple.printcenter.CancelPrintJob
com.apple.printcenter.LaunchPrintCenterAppIntent
com.apple.printcenter.PrintDocuments
com.apple.reminders.AddOrRemoveTagsAppIntent
com.apple.reminders.CompleteReminderAppIntent
com.apple.reminders.CompleteRemindersAppIntent
com.apple.reminders.CreateCustomSmartListAppIntent
com.apple.reminders.CreateGroupAppIntent
com.apple.reminders.CreateSectionAppIntent
com.apple.reminders.DeleteListsAppIntent
com.apple.reminders.DeleteRemindersAppIntent
com.apple.reminders.DeleteRemindersListGroupsAppIntent
com.apple.reminders.DeleteSectionsAppIntent
com.apple.reminders.GroupEntity-UpdatableEntity
com.apple.reminders.ListEntity-UpdatableEntity
com.apple.reminders.MoveRemindersAppIntent
com.apple.reminders.MoveRemindersToListAppIntent
com.apple.reminders.MoveRemindersToParentReminderAppIntent
com.apple.reminders.MoveRemindersToSectionAppIntent
com.apple.reminders.OpenGroupAppIntent
com.apple.reminders.OpenReminderAppIntent
com.apple.reminders.OpenSectionAppIntent
com.apple.reminders.OpenSmartListAppIntent
com.apple.reminders.OpenTagsAppIntent
com.apple.reminders.RemotePreferencesEntity
com.apple.reminders.SectionEntity-UpdatableEntity
com.apple.reminders.SmartListEntity
com.apple.reminders.TTRCreateListAppIntent
com.apple.reminders.TTRCreateReminderAppIntent
com.apple.reminders.TTROpenListAppIntent
com.apple.reminders.TTROpenSmartListAppIntent
com.apple.reminders.TTRReminderSetCompletedIntent
com.apple.reminders.TTRSearchRemindersAppIntent
com.apple.reminders.UpdateGroupAppIntent
com.apple.reminders.UpdateListAppIntent
com.apple.reminders.UpdateReminderAppIntent
com.apple.reminders.UpdateSectionAppIntent
com.apple.reminders.UpdateSmartListAppIntent
com.apple.reminders.UpdateSmartListIsHiddenAppIntent
com.apple.screenshot.launcher.CaptureScreenIntent
com.apple.screenshot.launcher.CaptureSelectionIntent
com.apple.screenshot.launcher.CustomCaptureConfiguration
com.apple.screenshot.launcher.CustomCaptureIntent
com.apple.screenshot.launcher.CustomRecordConfiguration
com.apple.screenshot.launcher.CustomRecordIntent
com.apple.screenshot.launcher.RecordScreenIntent
com.apple.screenshot.launcher.RecordSelectionIntent
com.apple.shortcuts.AddShortcutToHomeScreenAction
com.apple.shortcuts.ChangeShortcutIconAction
com.apple.shortcuts.CreateFolderAction
com.apple.shortcuts.CreateShortcutiCloudLinkAction
com.apple.shortcuts.CreateWorkflowAction
com.apple.shortcuts.DeleteWorkflowAction
com.apple.shortcuts.GetShortcutAttributesAction
com.apple.shortcuts.MoveShortcutToFolderAction
com.apple.shortcuts.OpenAppIntent
com.apple.shortcuts.OpenNavigationDestinationAction
com.apple.shortcuts.OpenShortcutsStaticDeepLinks
com.apple.shortcuts.OpenWorkflowAction
com.apple.shortcuts.RenameShortcutAction
com.apple.shortcuts.RunShortcutConfigurationIntent
com.apple.shortcuts.RunShortcutFromCollectionIntent
com.apple.shortcuts.RunShortcutIntent
com.apple.shortcuts.SearchActionDrawerAction
com.apple.shortcuts.SearchShortcutsAction
com.apple.shortcuts.SetShortcutAttributesAction
com.apple.shortcuts.ShortcutsFolderConfigurationIntent
com.apple.shortcuts.StopWorkflowAction
com.apple.siri.AssistantSettingsControls.AlwaysPrintSiriResponseEntity
com.apple.siri.AssistantSettingsControls.AlwaysPrintSiriResponseEntity-UpdatableEntity
com.apple.siri.AssistantSettingsControls.AlwaysShowSpeechEntity
com.apple.siri.AssistantSettingsControls.AlwaysShowSpeechEntity-UpdatableEntity
com.apple.siri.AssistantSettingsControls.AskSiriEntity
com.apple.siri.AssistantSettingsControls.KeyboardShortcutEntity
com.apple.siri.AssistantSettingsControls.OpenAlwaysPrintSiriResponseEntity
com.apple.siri.AssistantSettingsControls.OpenAlwaysShowSpeechEntity
com.apple.siri.AssistantSettingsControls.OpenAskSiriEntity
com.apple.siri.AssistantSettingsControls.OpenKeyboardShortcutEntity
com.apple.siri.AssistantSettingsControls.OpenSiriAndDictationHistoryEntity
com.apple.siri.AssistantSettingsControls.OpenSiriLanguageEntity
com.apple.siri.AssistantSettingsControls.OpenSiriSuggestionsAndPrivacyEntity
com.apple.siri.AssistantSettingsControls.OpenSiriSuggestionsAndPrivacyForAppEntity
com.apple.siri.AssistantSettingsControls.OpenSiriSuggestionsShowInAppEntity
com.apple.siri.AssistantSettingsControls.OpenSiriVoiceEntity
com.apple.siri.AssistantSettingsControls.OpenVoiceFeedbackToggleEntity
com.apple.siri.AssistantSettingsControls.SiriAndDictationHistoryEntity
com.apple.siri.AssistantSettingsControls.SiriLanguageEntity
com.apple.siri.AssistantSettingsControls.SiriSuggestionsAndPrivacyEntity
com.apple.siri.AssistantSettingsControls.SiriSuggestionsAndPrivacyForAppEntity
com.apple.siri.AssistantSettingsControls.SiriSuggestionsAndPrivacyForAppEntity-UpdatableEntity
com.apple.siri.AssistantSettingsControls.SiriSuggestionsShowInAppEntity
com.apple.siri.AssistantSettingsControls.SiriSuggestionsShowInAppEntity-UpdatableEntity
com.apple.siri.AssistantSettingsControls.SiriVoiceEntity
com.apple.siri.AssistantSettingsControls.VoiceFeedbackToggleEntity
com.apple.siri.AssistantSettingsControls.VoiceFeedbackToggleEntity-UpdatableEntity
com.apple.stocks.AddSymbolToWatchlistIntent
com.apple.stocks.BlockIntent
com.apple.stocks.DecreaseTextSizeIntent
com.apple.stocks.DeleteSymbolFromWatchlistIntent
com.apple.stocks.DeleteWatchlistsIntent
com.apple.stocks.FollowIntent
com.apple.stocks.GetSymbolQuoteIntent
com.apple.stocks.IncreaseTextSizeIntent
com.apple.stocks.NewWatchlistIntent
com.apple.stocks.NewsTabDeepLink
com.apple.stocks.OpenArticleIntent
com.apple.stocks.OpenBusinessNewsIntent
com.apple.stocks.OpenFeedIntent
com.apple.stocks.OpenHistoryIntent
com.apple.stocks.OpenRecipeIntent
com.apple.stocks.OpenSavedIntent
com.apple.stocks.OpenSavedRecipesIntent
com.apple.stocks.OpenStaticFeed
com.apple.stocks.OpenSymbolIntent
com.apple.stocks.OpenWatchlistIntent
com.apple.stocks.SaveArticleIntent
com.apple.stocks.StockIntent
com.apple.stocks.StocksOverviewIntent
com.apple.stocks.SymbolEntity
com.apple.stocks.SymbolWidgetEntity
com.apple.stocks.UnblockIntent
com.apple.stocks.UnsaveArticleIntent
com.apple.stocks.WatchlistEntity
com.apple.systempreferences.AccentColorEntity
com.apple.systempreferences.AccentColorEntity-UpdatableEntity
com.apple.systempreferences.AirDropEntity
com.apple.systempreferences.AirDropEntity-UpdatableEntity
com.apple.systempreferences.AirPlayIntent
com.apple.systempreferences.AirPlayReceiverIntent
com.apple.systempreferences.AirPlayRequiresPasswordIntent
com.apple.systempreferences.AllowWallPaperTintingEntity
com.apple.systempreferences.AllowWallPaperTintingEntity-UpdatableEntity
com.apple.systempreferences.AppearanceEntity
com.apple.systempreferences.AppearanceEntity-UpdatableEntity
com.apple.systempreferences.AppearanceSettingsDeepLink
com.apple.systempreferences.AppleAccountMainDynamicDeepLinks
com.apple.systempreferences.ApplicationNotificationsSettings
com.apple.systempreferences.ApplicationNotificationsSettings-UpdatableEntity
com.apple.systempreferences.AutoBrightnessEntity
com.apple.systempreferences.AutoBrightnessEntity-UpdatableEntity
com.apple.systempreferences.AutoDateTimeEntity
com.apple.systempreferences.AutoHideMenuBarOptionEntity
com.apple.systempreferences.AutoHideMenuBarOptionEntity-UpdatableEntity
com.apple.systempreferences.AutoLoginIntent
com.apple.systempreferences.AutoTimeZoneEntity
com.apple.systempreferences.AutomaticReconnectEntity
com.apple.systempreferences.AutomaticReconnectEntity-UpdatableEntity
com.apple.systempreferences.AvailableDisplaysEntity
com.apple.systempreferences.AxAdaptiveVoiceShortcutsEntity
com.apple.systempreferences.AxAdaptiveVoiceShortcutsEntity-UpdatableEntity
com.apple.systempreferences.AxAltMouseButtonsEntity
com.apple.systempreferences.AxAltMouseButtonsEntity-UpdatableEntity
com.apple.systempreferences.AxAltMouseEnableSoundsEntity
com.apple.systempreferences.AxAltMouseEnableSoundsEntity-UpdatableEntity
com.apple.systempreferences.AxAltMouseEnableVisualsEntity
com.apple.systempreferences.AxAltMouseEnableVisualsEntity-UpdatableEntity
com.apple.systempreferences.AxAnimatedImagesEntity
com.apple.systempreferences.AxAnimatedImagesEntity-UpdatableEntity
com.apple.systempreferences.AxBackgroundSoundsEntity
com.apple.systempreferences.AxBackgroundSoundsEntity-UpdatableEntity
com.apple.systempreferences.AxBackgroundSoundsLockScreenEntity
com.apple.systempreferences.AxBackgroundSoundsLockScreenEntity-UpdatableEntity
com.apple.systempreferences.AxCaptioningPreferSdhEntity
com.apple.systempreferences.AxCaptioningPreferSdhEntity-UpdatableEntity
com.apple.systempreferences.AxDifferentiateWithoutColorEntity
com.apple.systempreferences.AxDifferentiateWithoutColorEntity-UpdatableEntity
com.apple.systempreferences.AxDimFlashingEntity
com.apple.systempreferences.AxDimFlashingEntity-UpdatableEntity
com.apple.systempreferences.AxDisplayFilterEnabledEntity
com.apple.systempreferences.AxDisplayFilterEnabledEntity-UpdatableEntity
com.apple.systempreferences.AxDisplayFilterTypeEntity
com.apple.systempreferences.AxDisplayFilterTypeEntity-UpdatableEntity
com.apple.systempreferences.AxDwellActionEntity
com.apple.systempreferences.AxDwellActionEntity-UpdatableEntity
com.apple.systempreferences.AxDwellAutoRevertEntity
com.apple.systempreferences.AxDwellAutoRevertEntity-UpdatableEntity
com.apple.systempreferences.AxDwellCursorColorEntity
com.apple.systempreferences.AxDwellCursorColorEntity-UpdatableEntity
com.apple.systempreferences.AxDwellInMenuExtraEntity
com.apple.systempreferences.AxDwellInMenuExtraEntity-UpdatableEntity
com.apple.systempreferences.AxDwellInPanelsEntity
com.apple.systempreferences.AxDwellInPanelsEntity-UpdatableEntity
com.apple.systempreferences.AxDwellProgressIndicatorEntity
com.apple.systempreferences.AxDwellProgressIndicatorEntity-UpdatableEntity
com.apple.systempreferences.AxDwellZoomEntity
com.apple.systempreferences.AxDwellZoomEntity-UpdatableEntity
com.apple.systempreferences.AxFacetimeTranscriptionsEntity
com.apple.systempreferences.AxFacetimeTranscriptionsEntity-UpdatableEntity
com.apple.systempreferences.AxFeatureLivespeechEntity
com.apple.systempreferences.AxFeatureLivespeechEntity-UpdatableEntity
com.apple.systempreferences.AxFeatureSwitchcontrolEntity
com.apple.systempreferences.AxFeatureSwitchcontrolEntity-UpdatableEntity
com.apple.systempreferences.AxFeatureVoicecontrolEntity
com.apple.systempreferences.AxFeatureVoicecontrolEntity-UpdatableEntity
com.apple.systempreferences.AxFeatureVoiceoverEntity
com.apple.systempreferences.AxFeatureVoiceoverEntity-UpdatableEntity
com.apple.systempreferences.AxFeatureZoomEntity
com.apple.systempreferences.AxFeatureZoomEntity-UpdatableEntity
com.apple.systempreferences.AxFindCursorEntity
com.apple.systempreferences.AxFindCursorEntity-UpdatableEntity
com.apple.systempreferences.AxFkaAutoHideCheckboxEntity
com.apple.systempreferences.AxFkaAutoHideCheckboxEntity-UpdatableEntity
com.apple.systempreferences.AxFkaEnableCheckboxEntity
com.apple.systempreferences.AxFkaEnableCheckboxEntity-UpdatableEntity
com.apple.systempreferences.AxFkaHighContrastCheckboxEntity
com.apple.systempreferences.AxFkaHighContrastCheckboxEntity-UpdatableEntity
com.apple.systempreferences.AxFkaIncreaseSizeCheckboxEntity
com.apple.systempreferences.AxFkaIncreaseSizeCheckboxEntity-UpdatableEntity
com.apple.systempreferences.AxFlashScreenEntity
com.apple.systempreferences.AxFlashScreenEntity-UpdatableEntity
com.apple.systempreferences.AxHeadMouseEntity
com.apple.systempreferences.AxHeadMouseEntity-UpdatableEntity
com.apple.systempreferences.AxHomePanelDwellActionsEntity
com.apple.systempreferences.AxHomePanelDwellActionsEntity-UpdatableEntity
com.apple.systempreferences.AxHotCornerBottomLeftEntity
com.apple.systempreferences.AxHotCornerBottomLeftEntity-UpdatableEntity
com.apple.systempreferences.AxHotCornerBottomRightEntity
com.apple.systempreferences.AxHotCornerBottomRightEntity-UpdatableEntity
com.apple.systempreferences.AxHotCornerMoveHomePanelEntity
com.apple.systempreferences.AxHotCornerMoveHomePanelEntity-UpdatableEntity
com.apple.systempreferences.AxHotCornerTopLeftEntity
com.apple.systempreferences.AxHotCornerTopLeftEntity-UpdatableEntity
com.apple.systempreferences.AxHotCornerTopRightEntity
com.apple.systempreferences.AxHotCornerTopRightEntity-UpdatableEntity
com.apple.systempreferences.AxHoverTextActivationLockModeEntity
com.apple.systempreferences.AxHoverTextActivationLockModeEntity-UpdatableEntity
com.apple.systempreferences.AxHoverTextEnableEntity
com.apple.systempreferences.AxHoverTextEnableEntity-UpdatableEntity
com.apple.systempreferences.AxHoverTextModifierEntity
com.apple.systempreferences.AxHoverTextModifierEntity-UpdatableEntity
com.apple.systempreferences.AxHoverTypingEnableEntity
com.apple.systempreferences.AxHoverTypingEnableEntity-UpdatableEntity
com.apple.systempreferences.AxHoverTypingEntryLocationEntity
com.apple.systempreferences.AxHoverTypingEntryLocationEntity-UpdatableEntity
com.apple.systempreferences.AxIgnoreTrackpadEntity
com.apple.systempreferences.AxIgnoreTrackpadEntity-UpdatableEntity
com.apple.systempreferences.AxIncreaseContrastEntity
com.apple.systempreferences.AxIncreaseContrastEntity-UpdatableEntity
com.apple.systempreferences.AxInvertColorEntity
com.apple.systempreferences.AxInvertColorEntity-UpdatableEntity
com.apple.systempreferences.AxInvertColorModeEntity
com.apple.systempreferences.AxInvertColorModeEntity-UpdatableEntity
com.apple.systempreferences.AxKbAppearanceTypeEntity
com.apple.systempreferences.AxKbAppearanceTypeEntity-UpdatableEntity
com.apple.systempreferences.AxKbAutoCapitalizationEntity
com.apple.systempreferences.AxKbAutoCapitalizationEntity-UpdatableEntity
com.apple.systempreferences.AxKbAutoSpacingEntity
com.apple.systempreferences.AxKbAutoSpacingEntity-UpdatableEntity
com.apple.systempreferences.AxKbHideEntity
com.apple.systempreferences.AxKbHideEntity-UpdatableEntity
com.apple.systempreferences.AxKbKeyAcceptedMouseEntity
com.apple.systempreferences.AxKbKeyAcceptedMouseEntity-UpdatableEntity
com.apple.systempreferences.AxKbRightClickEntity
com.apple.systempreferences.AxKbRightClickEntity-UpdatableEntity
com.apple.systempreferences.AxKbUseClickSoundsEntity
com.apple.systempreferences.AxKbUseClickSoundsEntity-UpdatableEntity
com.apple.systempreferences.AxMenubarDwellActionsEntity
com.apple.systempreferences.AxMenubarDwellActionsEntity-UpdatableEntity
com.apple.systempreferences.AxMonoAudioEntity
com.apple.systempreferences.AxMonoAudioEntity-UpdatableEntity
com.apple.systempreferences.AxMotionCuesEnabledEntity
com.apple.systempreferences.AxMotionCuesEnabledEntity-UpdatableEntity
com.apple.systempreferences.AxMouseKeysEntity
com.apple.systempreferences.AxMouseKeysEntity-UpdatableEntity
com.apple.systempreferences.AxMouseKeysIgnoreTrackpadEntity
com.apple.systempreferences.AxMouseKeysIgnoreTrackpadEntity-UpdatableEntity
com.apple.systempreferences.AxMouseKeysShortcutEntity
com.apple.systempreferences.AxMouseKeysShortcutEntity-UpdatableEntity
com.apple.systempreferences.AxMouseScrollBehaviorEntity
com.apple.systempreferences.AxMouseScrollBehaviorEntity-UpdatableEntity
com.apple.systempreferences.AxMouseScrollEntity
com.apple.systempreferences.AxMouseScrollEntity-UpdatableEntity
com.apple.systempreferences.AxPrefersHorizTextLayoutEntity
com.apple.systempreferences.AxPrefersHorizTextLayoutEntity-UpdatableEntity
com.apple.systempreferences.AxReduceCursorModulationEntity
com.apple.systempreferences.AxReduceCursorModulationEntity-UpdatableEntity
com.apple.systempreferences.AxReduceMotionEntity
com.apple.systempreferences.AxReduceMotionEntity-UpdatableEntity
com.apple.systempreferences.AxReduceTransparencyEntity
com.apple.systempreferences.AxReduceTransparencyEntity-UpdatableEntity
com.apple.systempreferences.AxRttEnableEntity
com.apple.systempreferences.AxRttEnableEntity-UpdatableEntity
com.apple.systempreferences.AxRttSendImmediatelyEntity
com.apple.systempreferences.AxRttSendImmediatelyEntity-UpdatableEntity
com.apple.systempreferences.AxShowToolbarButtonShapesEntity
com.apple.systempreferences.AxShowToolbarButtonShapesEntity-UpdatableEntity
com.apple.systempreferences.AxShowWindowTitlebarIconsEntity
com.apple.systempreferences.AxShowWindowTitlebarIconsEntity-UpdatableEntity
com.apple.systempreferences.AxSiriAtypicalSpeechEntity
com.apple.systempreferences.AxSiriAtypicalSpeechEntity-UpdatableEntity
com.apple.systempreferences.AxSlowKeysEntity
com.apple.systempreferences.AxSlowKeysEntity-UpdatableEntity
com.apple.systempreferences.AxSlowKeysSoundEntity
com.apple.systempreferences.AxSlowKeysSoundEntity-UpdatableEntity
com.apple.systempreferences.AxSpatialAudioFollowsHeadEntity
com.apple.systempreferences.AxSpatialAudioFollowsHeadEntity-UpdatableEntity
com.apple.systempreferences.AxSpokenAlertsEntity
com.apple.systempreferences.AxSpokenAlertsEntity-UpdatableEntity
com.apple.systempreferences.AxSpokenDetectLanguagesEntity
com.apple.systempreferences.AxSpokenDetectLanguagesEntity-UpdatableEntity
com.apple.systempreferences.AxSpokenHotkeyEntity
com.apple.systempreferences.AxSpokenHotkeyEntity-UpdatableEntity
com.apple.systempreferences.AxSpokenPointerElementEntity
com.apple.systempreferences.AxSpokenPointerElementEntity-UpdatableEntity
com.apple.systempreferences.AxSpokenPointerElementModeEntity
com.apple.systempreferences.AxSpokenPointerElementModeEntity-UpdatableEntity
com.apple.systempreferences.AxSpokenPointerElementVerbosityEntity
com.apple.systempreferences.AxSpokenPointerElementVerbosityEntity-UpdatableEntity
com.apple.systempreferences.AxSpokenPronunciationsEntity
com.apple.systempreferences.AxSpokenPronunciationsEntity-UpdatableEntity
com.apple.systempreferences.AxSpokenSelectionHighlightContentEntity
com.apple.systempreferences.AxSpokenSelectionHighlightContentEntity-UpdatableEntity
com.apple.systempreferences.AxSpokenSelectionHighlightSentenceColorEntity
com.apple.systempreferences.AxSpokenSelectionHighlightSentenceColorEntity-UpdatableEntity
com.apple.systempreferences.AxSpokenSelectionHighlightSentenceStyleEntity
com.apple.systempreferences.AxSpokenSelectionHighlightSentenceStyleEntity-UpdatableEntity
com.apple.systempreferences.AxSpokenSelectionHighlightWordColorEntity
com.apple.systempreferences.AxSpokenSelectionHighlightWordColorEntity-UpdatableEntity
com.apple.systempreferences.AxSpokenSelectionShowControllerEntity
com.apple.systempreferences.AxSpokenSelectionShowControllerEntity-UpdatableEntity
com.apple.systempreferences.AxSpokenTypingEchoCharsEntity
com.apple.systempreferences.AxSpokenTypingEchoCharsEntity-UpdatableEntity
com.apple.systempreferences.AxSpokenTypingEchoEntity
com.apple.systempreferences.AxSpokenTypingEchoEntity-UpdatableEntity
com.apple.systempreferences.AxSpokenTypingEchoModifierKeysEntity
com.apple.systempreferences.AxSpokenTypingEchoModifierKeysEntity-UpdatableEntity
com.apple.systempreferences.AxSpokenTypingEchoSelectionEntity
com.apple.systempreferences.AxSpokenTypingEchoSelectionEntity-UpdatableEntity
com.apple.systempreferences.AxSpokenTypingEchoWordsEntity
com.apple.systempreferences.AxSpokenTypingEchoWordsEntity-UpdatableEntity
com.apple.systempreferences.AxSpringLoadingEntity
com.apple.systempreferences.AxSpringLoadingEntity-UpdatableEntity
com.apple.systempreferences.AxStickyKeysBeepEntity
com.apple.systempreferences.AxStickyKeysBeepEntity-UpdatableEntity
com.apple.systempreferences.AxStickyKeysDisplayEntity
com.apple.systempreferences.AxStickyKeysDisplayEntity-UpdatableEntity
com.apple.systempreferences.AxStickyKeysDisplayLocationEntity
com.apple.systempreferences.AxStickyKeysDisplayLocationEntity-UpdatableEntity
com.apple.systempreferences.AxStickyKeysEntity
com.apple.systempreferences.AxStickyKeysEntity-UpdatableEntity
com.apple.systempreferences.AxStickyKeysShortcutEntity
com.apple.systempreferences.AxStickyKeysShortcutEntity-UpdatableEntity
com.apple.systempreferences.AxSwitchAutoCapitalizationEntity
com.apple.systempreferences.AxSwitchAutoCapitalizationEntity-UpdatableEntity
com.apple.systempreferences.AxSwitchAutoSpacingEntity
com.apple.systempreferences.AxSwitchAutoSpacingEntity-UpdatableEntity
com.apple.systempreferences.AxSwitchAutoscanEntity
com.apple.systempreferences.AxSwitchAutoscanEntity-UpdatableEntity
com.apple.systempreferences.AxSwitchControlAppearanceTypeEntity
com.apple.systempreferences.AxSwitchControlAppearanceTypeEntity-UpdatableEntity
com.apple.systempreferences.AxSwitchCursorSizeEntity
com.apple.systempreferences.AxSwitchCursorSizeEntity-UpdatableEntity
com.apple.systempreferences.AxSwitchHideAfterDelayEntity
com.apple.systempreferences.AxSwitchHideAfterDelayEntity-UpdatableEntity
com.apple.systempreferences.AxSwitchHoverTextToolbarEntity
com.apple.systempreferences.AxSwitchHoverTextToolbarEntity-UpdatableEntity
com.apple.systempreferences.AxSwitchMouseCursorEdgeEntity
com.apple.systempreferences.AxSwitchMouseCursorEdgeEntity-UpdatableEntity
com.apple.systempreferences.AxSwitchMouseMoveStyleEntity
com.apple.systempreferences.AxSwitchMouseMoveStyleEntity-UpdatableEntity
com.apple.systempreferences.AxSwitchNavFeedbackEntity
com.apple.systempreferences.AxSwitchNavFeedbackEntity-UpdatableEntity
com.apple.systempreferences.AxSwitchResumeAutoScanningEntity
com.apple.systempreferences.AxSwitchResumeAutoScanningEntity-UpdatableEntity
com.apple.systempreferences.AxSwitchScanRestartEntity
com.apple.systempreferences.AxSwitchScanRestartEntity-UpdatableEntity
com.apple.systempreferences.AxSystemTranscriptionEnabledEntity
com.apple.systempreferences.AxSystemTranscriptionEnabledEntity-UpdatableEntity
com.apple.systempreferences.AxTouchBarZoomEnableEntity
com.apple.systempreferences.AxTouchBarZoomEnableEntity-UpdatableEntity
com.apple.systempreferences.AxTrackpadScrollBehaviorEntity
com.apple.systempreferences.AxTrackpadScrollBehaviorEntity-UpdatableEntity
com.apple.systempreferences.AxTrackpadScrollEntity
com.apple.systempreferences.AxTrackpadScrollEntity-UpdatableEntity
com.apple.systempreferences.AxTypeToSiriEnabledEntity
com.apple.systempreferences.AxTypeToSiriEnabledEntity-UpdatableEntity
com.apple.systempreferences.AxVideoDescriptionEntity
com.apple.systempreferences.AxVideoDescriptionEntity-UpdatableEntity
com.apple.systempreferences.AxVirtualKeyboardEntity
com.apple.systempreferences.AxVirtualKeyboardEntity-UpdatableEntity
com.apple.systempreferences.AxVoiceControlOverlayEntity
com.apple.systempreferences.AxVoiceControlOverlayEntity-UpdatableEntity
com.apple.systempreferences.AxVoiceControlOverlayFadingEnabledEntity
com.apple.systempreferences.AxVoiceControlOverlayFadingEnabledEntity-UpdatableEntity
com.apple.systempreferences.AxVoiceControlPlaySoundEnabledEntity
com.apple.systempreferences.AxVoiceControlPlaySoundEnabledEntity-UpdatableEntity
com.apple.systempreferences.AxVoiceControlShowHintsEnabledEntity
com.apple.systempreferences.AxVoiceControlShowHintsEnabledEntity-UpdatableEntity
com.apple.systempreferences.AxZoomDisableUniversalControlEntity
com.apple.systempreferences.AxZoomDisableUniversalControlEntity-UpdatableEntity
com.apple.systempreferences.AxZoomEnableGestureEntity
com.apple.systempreferences.AxZoomEnableGestureEntity-UpdatableEntity
com.apple.systempreferences.AxZoomEnableHotkeysEntity
com.apple.systempreferences.AxZoomEnableHotkeysEntity-UpdatableEntity
com.apple.systempreferences.AxZoomFlashEntity
com.apple.systempreferences.AxZoomFlashEntity-UpdatableEntity
com.apple.systempreferences.AxZoomFocusMovementEntity
com.apple.systempreferences.AxZoomFocusMovementEntity-UpdatableEntity
com.apple.systempreferences.AxZoomFollowFocusActivationEntity
com.apple.systempreferences.AxZoomFollowFocusActivationEntity-UpdatableEntity
com.apple.systempreferences.AxZoomFollowFocusModeEntity
com.apple.systempreferences.AxZoomFollowFocusModeEntity-UpdatableEntity
com.apple.systempreferences.AxZoomFreezePanningEntity
com.apple.systempreferences.AxZoomFreezePanningEntity-UpdatableEntity
com.apple.systempreferences.AxZoomIndividualDisplaysEntity
com.apple.systempreferences.AxZoomIndividualDisplaysEntity-UpdatableEntity
com.apple.systempreferences.AxZoomInvertEntity
com.apple.systempreferences.AxZoomInvertEntity-UpdatableEntity
com.apple.systempreferences.AxZoomKeepStationaryEntity
com.apple.systempreferences.AxZoomKeepStationaryEntity-UpdatableEntity
com.apple.systempreferences.AxZoomMonitorSelectionEntity
com.apple.systempreferences.AxZoomMonitorSelectionEntity-UpdatableEntity
com.apple.systempreferences.AxZoomMonitorSelectionTrackpadEntity
com.apple.systempreferences.AxZoomMonitorSelectionTrackpadEntity-UpdatableEntity
com.apple.systempreferences.AxZoomMoveEntity
com.apple.systempreferences.AxZoomMoveEntity-UpdatableEntity
com.apple.systempreferences.AxZoomResizeShortcutsEntity
com.apple.systempreferences.AxZoomResizeShortcutsEntity-UpdatableEntity
com.apple.systempreferences.AxZoomRestoreEntity
com.apple.systempreferences.AxZoomRestoreEntity-UpdatableEntity
com.apple.systempreferences.AxZoomSmoothEntity
com.apple.systempreferences.AxZoomSmoothEntity-UpdatableEntity
com.apple.systempreferences.AxZoomStylePopupEntity
com.apple.systempreferences.AxZoomStylePopupEntity-UpdatableEntity
com.apple.systempreferences.AxZoomTempDetachEntity
com.apple.systempreferences.AxZoomTempDetachEntity-UpdatableEntity
com.apple.systempreferences.AxZoomTempToggleEntity
com.apple.systempreferences.AxZoomTempToggleEntity-UpdatableEntity
com.apple.systempreferences.AxZoomToggleFsAndPipEntity
com.apple.systempreferences.AxZoomToggleFsAndPipEntity-UpdatableEntity
com.apple.systempreferences.AxZoomTrackpadEntity
com.apple.systempreferences.AxZoomTrackpadEntity-UpdatableEntity
com.apple.systempreferences.BackgroundLoginItemsIntent
com.apple.systempreferences.BatteryHealthPaneDynamicDeepLinks
com.apple.systempreferences.BatteryOptionsPaneDynamicDeepLinks
com.apple.systempreferences.BatterySettingsPaneDynamicDeepLinks
com.apple.systempreferences.BluetoothPowerEntity
com.apple.systempreferences.BluetoothPowerEntity-UpdatableEntity
com.apple.systempreferences.ChangeMouseTrackingSpeedIntent
com.apple.systempreferences.ChangeTrackpadTrackingSpeedIntent
com.apple.systempreferences.CheckForUpdatesIntent
com.apple.systempreferences.ClassroomDynamicDeepLinks
com.apple.systempreferences.ClickScrollBarToEntity
com.apple.systempreferences.ClickScrollBarToEntity-UpdatableEntity
com.apple.systempreferences.ClockOptionsEntity
com.apple.systempreferences.ClockOptionsEntity-UpdatableEntity
com.apple.systempreferences.ComputerNameEntity
com.apple.systempreferences.ControlCenterModule-UpdatableEntity
com.apple.systempreferences.CurrentUserIntent
com.apple.systempreferences.CurrentlyConnectedVPN
com.apple.systempreferences.CurrentlyConnectedVPN-UpdatableEntity
com.apple.systempreferences.DateTimeEntity
com.apple.systempreferences.DesktopSettingsEntity
com.apple.systempreferences.DesktopSettingsEntity-UpdatableEntity
com.apple.systempreferences.DeviceGraphicsEntity
com.apple.systempreferences.DeviceMemoryEntity
com.apple.systempreferences.DeviceModelNameEntity
com.apple.systempreferences.DeviceOSInfoEntity
com.apple.systempreferences.DeviceProcessorEntity
com.apple.systempreferences.DeviceSSOIntent
com.apple.systempreferences.DeviceSerialNumberEntity
com.apple.systempreferences.DeviceStorageEntity
com.apple.systempreferences.DockSettingsEntity
com.apple.systempreferences.DockSettingsEntity-UpdatableEntity
com.apple.systempreferences.DownloadUpdatesPreferenceEntity
com.apple.systempreferences.DownloadUpdatesPreferenceEntity-UpdatableEntity
com.apple.systempreferences.EnergySaverPaneDynamicDeepLinks
com.apple.systempreferences.FamilyMemberDetailsDeepLink
com.apple.systempreferences.FamilySettingsDeepLink
com.apple.systempreferences.FamilySubscriptionsDeepLink
com.apple.systempreferences.FirewallAllowDownloadedSignedEntity
com.apple.systempreferences.FirewallAllowSignedEntity
com.apple.systempreferences.FirewallStateEntity
com.apple.systempreferences.FirewallStealthModeEntity
com.apple.systempreferences.FullScreenSwipeEntity
com.apple.systempreferences.FullScreenSwipeEntity-UpdatableEntity
com.apple.systempreferences.GetStartupDiskIntent
com.apple.systempreferences.GroupMembershipIntent
com.apple.systempreferences.GuestIntent
com.apple.systempreferences.GuestParentalControlStatusIntent
com.apple.systempreferences.GuestSharedAccessStatusIntent
com.apple.systempreferences.GuestStatusIntent
com.apple.systempreferences.HandoffIntent
com.apple.systempreferences.HighlightColorEntity
com.apple.systempreferences.HighlightColorEntity-UpdatableEntity
com.apple.systempreferences.HourFormatEntity
com.apple.systempreferences.HourFormatEntity-UpdatableEntity
com.apple.systempreferences.IdentifierIntent
com.apple.systempreferences.InstallMacUpdatesPreferenceEntity
com.apple.systempreferences.InstallMacUpdatesPreferenceEntity-UpdatableEntity
com.apple.systempreferences.InstallSecurityUpdatesPreferenceEntity
com.apple.systempreferences.InstallSecurityUpdatesPreferenceEntity-UpdatableEntity
com.apple.systempreferences.KeyboardSettingsDeepLink
com.apple.systempreferences.ListOfAccountsIntent
com.apple.systempreferences.ListOfNetworkServersIntent
com.apple.systempreferences.LockMessageIntent
com.apple.systempreferences.LoginItemEntity
com.apple.systempreferences.LoginWindowModeIntent
com.apple.systempreferences.LoginWindowShowsButtonsIntent
com.apple.systempreferences.MagicEdgeEntity
com.apple.systempreferences.MagicEdgeEntity-UpdatableEntity
com.apple.systempreferences.MissionControlEntity
com.apple.systempreferences.MissionControlEntity-UpdatableEntity
com.apple.systempreferences.MissionControlSettingsEntity
com.apple.systempreferences.MissionControlSettingsEntity-UpdatableEntity
com.apple.systempreferences.MouseSettingDeepLink
com.apple.systempreferences.MouseTrackingSpeedEntity
com.apple.systempreferences.MouseTrackingSpeedEntity-UpdatableEntity
com.apple.systempreferences.NotificationCenterEntity
com.apple.systempreferences.NotificationCenterEntity-UpdatableEntity
com.apple.systempreferences.NotificationSummarizationEntity
com.apple.systempreferences.OpenAboutSettingsStaticDeepLinks
com.apple.systempreferences.OpenAccessibilityAudioDescriptionsStaticDeepLinks
com.apple.systempreferences.OpenAccessibilityAudioStaticDeepLinks
com.apple.systempreferences.OpenAccessibilityCaptionsStaticDeepLinks
com.apple.systempreferences.OpenAccessibilityDisplayStaticDeepLinks
com.apple.systempreferences.OpenAccessibilityHearingDevicesStaticDeepLinks
com.apple.systempreferences.OpenAccessibilityHoverTextStaticDeepLinks
com.apple.systempreferences.OpenAccessibilityKeyboardStaticDeepLinks
com.apple.systempreferences.OpenAccessibilityLiveCaptionsStaticDeepLinks
com.apple.systempreferences.OpenAccessibilityLiveSpeechStaticDeepLinks
com.apple.systempreferences.OpenAccessibilityMotionStaticDeepLinks
com.apple.systempreferences.OpenAccessibilityPersonalVoiceStaticDeepLinks
com.apple.systempreferences.OpenAccessibilityPointerControlStaticDeepLinks
com.apple.systempreferences.OpenAccessibilityRTTStaticDeepLinks
com.apple.systempreferences.OpenAccessibilityRootStaticDeepLinks
com.apple.systempreferences.OpenAccessibilityShortcutStaticDeepLinks
com.apple.systempreferences.OpenAccessibilitySiriStaticDeepLinks
com.apple.systempreferences.OpenAccessibilitySpokenContentStaticDeepLinks
com.apple.systempreferences.OpenAccessibilitySwitchControlStaticDeepLinks
com.apple.systempreferences.OpenAccessibilityVocalShortcutsStaticDeepLinks
com.apple.systempreferences.OpenAccessibilityVoiceControlStaticDeepLinks
com.apple.systempreferences.OpenAccessibilityVoiceOverStaticDeepLinks
com.apple.systempreferences.OpenAccessibilityZoomStaticDeepLinks
com.apple.systempreferences.OpenAirDropHandoffDeepLinks
com.apple.systempreferences.OpenAppearanceSettingsDeepLink
com.apple.systempreferences.OpenAppleAccountMainDeepLink
com.apple.systempreferences.OpenApplicationNotificationsSettings
com.apple.systempreferences.OpenAutoBrightnessEntityDeepLink
com.apple.systempreferences.OpenAutomaticReconnectEntityDeepLink
com.apple.systempreferences.OpenAutomaticallySetDateTimeSetting
com.apple.systempreferences.OpenAutomaticallySetTimeZoneSetting
com.apple.systempreferences.OpenBatteryHealthPaneDynamicDeepLinks
com.apple.systempreferences.OpenBatteryOptionsPaneDynamicDeepLinks
com.apple.systempreferences.OpenBatterySettingsPaneDynamicDeepLinks
com.apple.systempreferences.OpenBiometricsAndPasswordSettingsEntityDeepLinks
com.apple.systempreferences.OpenBluetoothPowerDeepLink
com.apple.systempreferences.OpenBluetoothSettingsDeepLinks
com.apple.systempreferences.OpenClassKitAppIntentsDeepLinks
com.apple.systempreferences.OpenClassroomDynamicDeepLinks
com.apple.systempreferences.OpenClockOptionsEntity
com.apple.systempreferences.OpenConfiguredInternetAccountSettings
com.apple.systempreferences.OpenControlCenterModule
com.apple.systempreferences.OpenCurrentTimeZoneSetting
com.apple.systempreferences.OpenDateTimeDeepLinks
com.apple.systempreferences.OpenDesktopSettingsDeepLink
com.apple.systempreferences.OpenDesktopSettingsEntity
com.apple.systempreferences.OpenDeviceManagementStaticDeepLinks
com.apple.systempreferences.OpenDisplaysSettingsDeepLinks
com.apple.systempreferences.OpenDockSettingsEntity
com.apple.systempreferences.OpenEnergySaverPaneDynamicDeepLinks
com.apple.systempreferences.OpenFamilyMemberSettings
com.apple.systempreferences.OpenFamilySettings
com.apple.systempreferences.OpenFamilySetup
com.apple.systempreferences.OpenFamilySubscriptions
com.apple.systempreferences.OpenInternationalSettingsDeepLink
com.apple.systempreferences.OpenInternetAccountsSettings
com.apple.systempreferences.OpenKeyboardSettingsDeepLink
com.apple.systempreferences.OpenLockScreenDeepLinks
com.apple.systempreferences.OpenLoginItemsDeepLinks
com.apple.systempreferences.OpenMagicEdgeEntityDeepLink
com.apple.systempreferences.OpenMissionControlSettingsEntity
com.apple.systempreferences.OpenMouseDeepLink
com.apple.systempreferences.OpenNetworkSettingsDeepLinks
com.apple.systempreferences.OpenNewDeviceOutreachStaticDeepLinks
com.apple.systempreferences.OpenNotificationCenterEntity
com.apple.systempreferences.OpenNotificationSummarizationEntity
com.apple.systempreferences.OpenPrinterScannerDeepLinks
com.apple.systempreferences.OpenPrivacySecurityDeepLinks
com.apple.systempreferences.OpenSUSDeepLinks
com.apple.systempreferences.OpenShareKeyboardEntityDeepLink
com.apple.systempreferences.OpenSoundSettingsDeepLinks
com.apple.systempreferences.OpenSoundSettingsFeedbackSoundEntity
com.apple.systempreferences.OpenSoundSettingsInterfaceEffectsEntity
com.apple.systempreferences.OpenSoundSettingsStartupSoundEntity
com.apple.systempreferences.OpenSpotlightSettingsDeepLinks
com.apple.systempreferences.OpenStartupDiskStaticDeepLinks
com.apple.systempreferences.OpenStorageSettingsDeeplinks
com.apple.systempreferences.OpenTheCurrentDateTimeSetting
com.apple.systempreferences.OpenTimeMachineSettingsStaticDeepLinks
com.apple.systempreferences.OpenTrackpadDeepLinks
com.apple.systempreferences.OpenTransferResetDeepLinks
com.apple.systempreferences.OpenTrueToneEntityDeepLink
com.apple.systempreferences.OpenTwentyFourHourTimeSetting
com.apple.systempreferences.OpenUsersGroupsDeepLinks
com.apple.systempreferences.OpenVPNDeepLink
com.apple.systempreferences.OpenWallpaperDeepLinks
com.apple.systempreferences.OpenWidgetSettingsEntity
com.apple.systempreferences.OpenWindowsSettingsEntity
com.apple.systempreferences.PaperSizeEntity
com.apple.systempreferences.PaperSizeEntity-UpdatableEntity
com.apple.systempreferences.RecentDocumentsOptionEntity
com.apple.systempreferences.RecentDocumentsOptionEntity-UpdatableEntity
com.apple.systempreferences.RequirePasswordDelayIntent
com.apple.systempreferences.ScreenSaverDelayEntity
com.apple.systempreferences.ScreenSaverDelayEntity-UpdatableEntity
com.apple.systempreferences.ScreenSaverNameIntent
com.apple.systempreferences.ScrollDirectionEntity
com.apple.systempreferences.ScrollDirectionEntity-UpdatableEntity
com.apple.systempreferences.SecondaryClickEntity
com.apple.systempreferences.SecondaryClickEntity-UpdatableEntity
com.apple.systempreferences.SetupFamilyDeepLink
com.apple.systempreferences.ShareKeyboardEntity
com.apple.systempreferences.ShareKeyboardEntity-UpdatableEntity
com.apple.systempreferences.SharingSettingsIntents.OpenSharingDeepLinks
com.apple.systempreferences.SharingSettingsIntents.SharingIntents
com.apple.systempreferences.ShowAsScreenSaverEntity
com.apple.systempreferences.ShowAsScreenSaverEntity-UpdatableEntity
com.apple.systempreferences.ShowAsWallpaperEntity
com.apple.systempreferences.ShowAsWallpaperEntity-UpdatableEntity
com.apple.systempreferences.ShowBatteryPercentageEntity
com.apple.systempreferences.ShowBatteryPercentageEntity-UpdatableEntity
com.apple.systempreferences.ShowLargeClockIntent
com.apple.systempreferences.ShowMenuBarBackgroundEntity
com.apple.systempreferences.ShowMenuBarBackgroundEntity-UpdatableEntity
com.apple.systempreferences.ShowPasswordHintsIntent
com.apple.systempreferences.ShowScreenSaverOnAllSpacesEntity
com.apple.systempreferences.ShowScreenSaverOnAllSpacesEntity-UpdatableEntity
com.apple.systempreferences.ShowScrollBarsEntity
com.apple.systempreferences.ShowScrollBarsEntity-UpdatableEntity
com.apple.systempreferences.ShowWallpaperOnAllSpacesEntity
com.apple.systempreferences.ShowWallpaperOnAllSpacesEntity-UpdatableEntity
com.apple.systempreferences.SidebarIconSizeEntity
com.apple.systempreferences.SidebarIconSizeEntity-UpdatableEntity
com.apple.systempreferences.SmartZoomEntity
com.apple.systempreferences.SmartZoomEntity-UpdatableEntity
com.apple.systempreferences.SoundSettingsFeedbackSoundEntity
com.apple.systempreferences.SoundSettingsFeedbackSoundEntity-UpdatableEntity
com.apple.systempreferences.SoundSettingsInterfaceEffectsEntity
com.apple.systempreferences.SoundSettingsInterfaceEffectsEntity-UpdatableEntity
com.apple.systempreferences.SoundSettingsStartupSoundEntity
com.apple.systempreferences.SoundSettingsStartupSoundEntity-UpdatableEntity
com.apple.systempreferences.SpotlightSettingsDeepLinks
com.apple.systempreferences.StorageSettingsDeeplinks
com.apple.systempreferences.SwipeBetweenPagesEntity
com.apple.systempreferences.SwipeBetweenPagesEntity-UpdatableEntity
com.apple.systempreferences.TimeZoneEntity
com.apple.systempreferences.ToggleHighPowerModeBatteryNoBatteryIntent
com.apple.systempreferences.ToggleHighPowerModeOnBatteryIntent
com.apple.systempreferences.ToggleLowPowerModeIntent
com.apple.systempreferences.TrackpadAppExposeEntity
com.apple.systempreferences.TrackpadAppExposeEntity-UpdatableEntity
com.apple.systempreferences.TrackpadClickPressureEntity
com.apple.systempreferences.TrackpadClickPressureEntity-UpdatableEntity
com.apple.systempreferences.TrackpadForceClickEntity
com.apple.systempreferences.TrackpadForceClickEntity-UpdatableEntity
com.apple.systempreferences.TrackpadLaunchpadEntity
com.apple.systempreferences.TrackpadLaunchpadEntity-UpdatableEntity
com.apple.systempreferences.TrackpadLookUpAndDataDetectorsEntity
com.apple.systempreferences.TrackpadLookUpAndDataDetectorsEntity-UpdatableEntity
com.apple.systempreferences.TrackpadMissionControlEntity
com.apple.systempreferences.TrackpadMissionControlEntity-UpdatableEntity
com.apple.systempreferences.TrackpadNotificiationCenterEntity
com.apple.systempreferences.TrackpadNotificiationCenterEntity-UpdatableEntity
com.apple.systempreferences.TrackpadQuietClickEntity
com.apple.systempreferences.TrackpadQuietClickEntity-UpdatableEntity
com.apple.systempreferences.TrackpadRotateEntity
com.apple.systempreferences.TrackpadRotateEntity-UpdatableEntity
com.apple.systempreferences.TrackpadSecondaryClickEntity
com.apple.systempreferences.TrackpadSecondaryClickEntity-UpdatableEntity
com.apple.systempreferences.TrackpadSettingDeepLink
com.apple.systempreferences.TrackpadShowDesktopEntity
com.apple.systempreferences.TrackpadShowDesktopEntity-UpdatableEntity
com.apple.systempreferences.TrackpadSmartZoomEntity
com.apple.systempreferences.TrackpadSmartZoomEntity-UpdatableEntity
com.apple.systempreferences.TrackpadSwipeBetweenAppsEntity
com.apple.systempreferences.TrackpadSwipeBetweenAppsEntity-UpdatableEntity
com.apple.systempreferences.TrackpadSwipeBetweenPagesEntity
com.apple.systempreferences.TrackpadSwipeBetweenPagesEntity-UpdatableEntity
com.apple.systempreferences.TrackpadTapToClickEntity
com.apple.systempreferences.TrackpadTapToClickEntity-UpdatableEntity
com.apple.systempreferences.TrackpadTrackingSpeedEntity
com.apple.systempreferences.TrackpadTrackingSpeedEntity-UpdatableEntity
com.apple.systempreferences.TrackpadZoomInOutEntity
com.apple.systempreferences.TrackpadZoomInOutEntity-UpdatableEntity
com.apple.systempreferences.TrueToneEntity
com.apple.systempreferences.TrueToneEntity-UpdatableEntity
com.apple.systempreferences.UserGroupIntent
com.apple.systempreferences.UserHomeFolderIntent
com.apple.systempreferences.UserIsAdminIntent
com.apple.systempreferences.UserLoginItemsIntent
com.apple.systempreferences.UserSSOIntent
com.apple.systempreferences.UserSwitcherMenuStyleEntity
com.apple.systempreferences.UserSwitcherMenuStyleEntity-UpdatableEntity
com.apple.systempreferences.VPNConfigurationEntity-UpdatableEntity
com.apple.systempreferences.WidgetSettingsEntity
com.apple.systempreferences.WidgetSettingsEntity-UpdatableEntity
com.apple.systempreferences.WindowsSettingsEntity
com.apple.systempreferences.WindowsSettingsEntity-UpdatableEntity
com.apple.wallpaper.agent.SetWallpaperIntent
com.apple.wallpaper.agent.SetWallpaperPhotoIntent
com.apple.wallpaper.agent.SkipShuffledContentAction
com.apple.wallpaper.agent.WallpaperEntity
com.apple.weather.AddSavedLocationIntent
com.apple.weather.LocationEntity
com.apple.weather.LocationSearchEntity
com.apple.weather.OpenMoonIntent
com.apple.weather.OpenNotificationsConfigurationIntent
com.apple.weather.OpenSunriseSunsetIntent
com.apple.weather.OpenUnitsConfigurationIntent
com.apple.weather.OpenWeatherAirQualityIntent
com.apple.weather.OpenWeatherSpecificConditionIntent
com.apple.weather.PreferredUnitsEntity
com.apple.weather.RemoveSavedLocationIntent
com.apple.weather.ResetUnitsIntent
com.apple.weather.SetDistanceUnitIntent
com.apple.weather.SetPrecipitationUnitIntent
com.apple.weather.SetPressureUnitIntent
com.apple.weather.SetTemperatureUnitIntent
com.apple.weather.SetWindUnitIntent
```

> **Note:** `is.workflow.actions.appendnote`, `is.workflow.actions.filter.notes`, and `is.workflow.actions.shownote` are WF-namespace actions documented in [ACTIONS.md](ACTIONS.md), not AppIntents.

---

## Invocation Template

To invoke any AppIntent:

```
<dict>
    <key>WFWorkflowActionIdentifier</key>
    <string>APP_INTENT_FULL_ID</string>
    <key>WFWorkflowActionParameters</key>
    <dict>
        <key>AppIntentDescriptor</key>
        <dict>
            <key>BundleIdentifier</key>
            <string>APP_BUNDLE_ID</string>
            <key>Name</key>
            <string>DISPLAY_NAME</string>
            <key>AppIntentIdentifier</key>
            <string>APP_INTENT_IDENTIFIER</string>
        </dict>
        <!-- Additional parameters as needed -->
    </dict>
</dict>
```

Common Bundle Identifiers:
- `com.apple.systempreferences` - System Settings
- `com.apple.Safari` - Safari
- `com.apple.Notes` - Notes
- `com.apple.reminders` - Reminders
- `com.apple.iCal` - Calendar
- `com.apple.clock` - Clock
