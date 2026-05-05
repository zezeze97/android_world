# Copyright 2026 The android_world Authors.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Expanded AndroidWorld tasks with task-local validation entry points."""

from typing import Any

from android_world.task_evals.single import audio_recorder
from android_world.task_evals.single import camera as camera_tasks
from android_world.task_evals.single import contacts
from android_world.task_evals.single import expense
from android_world.task_evals.single import files
from android_world.task_evals.single import clock
from android_world.task_evals.single import markor
from android_world.task_evals.single import recipe
from android_world.task_evals.single import retro_music
from android_world.task_evals.single import simple_gallery_pro
from android_world.task_evals.single import sms
from android_world.task_evals.single import system
from android_world.task_evals.single import vlc
from android_world.task_evals.single.calendar import calendar


def _goal_from_template(template: str):

  def goal(self):
    return template.format(**self.params)

  return property(goal)


def _validation_function(name: str, base: type):
  """Creates a dedicated validation function for one expanded task."""

  def validate(self, env):
    return float(base.is_successful(self, env))

  validate.__name__ = f"validate_{name}"
  validate.__qualname__ = f"{name}.validate_success"
  return validate


def _is_successful(self, env):
  return self.validate_success(env)


def _make_task(
    name: str,
    base: type,
    template: str,
    difficulty: str,
    tags: list[str],
    optimal_steps: str,
) -> type:
  return type(
      name,
      (base,),
      {
          "__module__": __name__,
          "__doc__": f"Expanded task for {base.__name__}.",
          "template": template,
          "goal": _goal_from_template(template),
          "validate_success": _validation_function(name, base),
          "is_successful": _is_successful,
          "expanded_metadata": {
              "task_name": name,
              "task_template": template,
              "difficulty": difficulty,
              "tags": tags,
              "optimal_steps": optimal_steps,
          },
      },
  )


_SPECS = [
    (
        "MarkorAppendToNote",
        markor.MarkorAppendToNote,
        "Open the Markor note {file_name} and add this text as a new line at"
        ' the bottom: "{appended_text}".',
        "medium",
        ["data_edit", "data_entry", "requires_setup", "parameterized"],
        "5",
    ),
    (
        "MarkorCopyNote",
        markor.MarkorCopyNote,
        "In Markor, copy the contents of {source_name} into a new note named"
        " {new_name}. Leave the original note unchanged.",
        "medium",
        ["data_entry", "data_edit", "requires_setup", "parameterized"],
        "8",
    ),
    (
        "MarkorCreateChecklistNote",
        markor.MarkorCreateChecklistNote,
        "Create a checklist note in Markor named {file_name} with these items:"
        " {items}. Each checklist item should be unchecked.",
        "medium",
        ["data_entry", "complex_ui_understanding", "parameterized"],
        "10",
    ),
    (
        "MarkorCreateNoteInFolder",
        markor.MarkorCreateNoteInFolder,
        "In Markor, create a note named {file_name} inside the {folder_name}"
        " folder with the following text: {text}",
        "medium",
        [
            "data_entry",
            "complex_ui_understanding",
            "requires_setup",
            "parameterized",
        ],
        "10",
    ),
    (
        "MarkorDeleteNoteInFolder",
        markor.MarkorDeleteNoteInFolder,
        "In Markor, delete the note {file_name} from the {subfolder} folder.",
        "medium",
        [
            "data_edit",
            "complex_ui_understanding",
            "requires_setup",
            "parameterized",
        ],
        "7",
    ),
    (
        "MarkorPrependDateToNote",
        markor.MarkorPrependDateToNote,
        "Open the Markor note {file_name} and add {date} as the first line of"
        " the note.",
        "medium",
        ["data_edit", "data_entry", "requires_setup", "parameterized"],
        "5",
    ),
    (
        "MarkorRenameNote",
        markor.MarkorRenameNote,
        "Rename the Markor note {original_name} to {new_name} without changing"
        " its contents.",
        "medium",
        ["data_edit", "requires_setup", "parameterized"],
        "5",
    ),
    (
        "MarkorReplaceTextInNote",
        markor.MarkorReplaceTextInNote,
        'In the Markor note {file_name}, replace the text "{old_text}" with'
        ' "{new_text}".',
        "medium",
        ["data_edit", "data_entry", "requires_setup", "parameterized"],
        "5",
    ),
    (
        "MarkorMoveNoteBetweenFolders",
        markor.MarkorMoveNote,
        "In Markor, file {file_name} under {destination_folder}; it should no"
        " longer remain in {source_folder}.",
        "medium",
        [
            "data_edit",
            "complex_ui_understanding",
            "requires_setup",
            "parameterized",
        ],
        "8",
    ),
    (
        "MarkorRewriteAndRenameNote",
        markor.MarkorChangeNoteContent,
        "In Markor, turn {original_name} into {new_name} and make the note"
        ' contain only this text: "{updated_content}".',
        "medium",
        ["data_edit", "data_entry", "requires_setup", "parameterized"],
        "7",
    ),
    (
        "MarkorAddHeaderAndRenameNote",
        markor.MarkorAddNoteHeader,
        "Edit {original_name} in Markor so it starts with \"{header}\", then a"
        " blank line, then the original note text. Save the result as"
        " {new_name}.",
        "medium",
        ["data_edit", "data_entry", "requires_setup", "parameterized"],
        "7",
    ),
    (
        "MarkorCreateClipboardNote",
        markor.MarkorCreateNoteFromClipboard,
        "Create {file_name} in Markor and paste the current clipboard text as"
        " its contents.",
        "medium",
        ["data_entry", "cross_app", "requires_setup", "parameterized"],
        "8",
    ),
    (
        "MarkorMergeThreeNotes",
        markor.MarkorMergeNotes,
        "Make a new Markor note called {new_file_name} by combining"
        " {file1_name}, {file2_name}, and {file3_name} in that order, with an"
        " empty line separating each note.",
        "hard",
        ["data_entry", "data_edit", "repetition", "requires_setup"],
        "18",
    ),
    (
        "SimpleCalendarAddEventNextWeek",
        calendar.SimpleCalendarAddEventNextWeek,
        "In Simple Calendar Pro, create a calendar event for next {day_of_week}"
        " at {hour}h with the title '{event_title}' and the description"
        " '{event_description}'. The event should last for {duration_mins} mins.",
        "medium",
        ["data_entry", "math_counting", "parameterized"],
        "13",
    ),
    (
        "SimpleCalendarAddEventWithLocation",
        calendar.SimpleCalendarAddEventWithLocation,
        "In Simple Calendar Pro, create a calendar event on {year}-{month}-{day}"
        " at {hour}h located at '{location}' with the title '{event_title}' and"
        " the description '{event_description}'. The event should last for"
        " {duration_mins} mins.",
        "hard",
        [
            "data_entry",
            "complex_ui_understanding",
            "requires_setup",
            "parameterized",
        ],
        "19",
    ),
    (
        "SimpleCalendarAddLongEvent",
        calendar.SimpleCalendarAddLongEvent,
        "In Simple Calendar Pro, create a long calendar event on"
        " {year}-{month}-{day} at {hour}h with the title '{event_title}' and"
        " the description '{event_description}'. The event should last for"
        " {duration_mins} mins.",
        "hard",
        ["data_entry", "complex_ui_understanding", "parameterized"],
        "18",
    ),
    (
        "SimpleCalendarAddTwoEventsDifferentDays",
        calendar.SimpleCalendarAddTwoEventsDifferentDays,
        "In Simple Calendar Pro, create two calendar events: one on"
        " {year}-{month}-{day1} at {hour1}h titled '{event_title1}' with"
        " description '{event_description1}' lasting {duration_mins1} mins, and"
        " one on {year}-{month}-{day2} at {hour2}h titled '{event_title2}' with"
        " description '{event_description2}' lasting {duration_mins2} mins.",
        "hard",
        ["data_entry", "repetition", "parameterized"],
        "32",
    ),
    (
        "SimpleCalendarAddTwoEventsSameDay",
        calendar.SimpleCalendarAddTwoEventsSameDay,
        "In Simple Calendar Pro, create two calendar events on"
        " {year}-{month}-{day}: first at {hour1}h titled '{event_title1}' with"
        " description '{event_description1}' lasting {duration_mins1} mins, and"
        " second at {hour2}h titled '{event_title2}' with description"
        " '{event_description2}' lasting {duration_mins2} mins.",
        "hard",
        ["data_entry", "repetition", "parameterized"],
        "30",
    ),
    (
        "SimpleCalendarDeleteEventByTitle",
        calendar.SimpleCalendarDeleteEventByTitle,
        "In Simple Calendar Pro, delete the calendar event titled"
        " '{event_title}'.",
        "medium",
        [
            "data_edit",
            "search",
            "complex_ui_understanding",
            "requires_setup",
            "parameterized",
        ],
        "6",
    ),
    (
        "SimpleCalendarDeleteEventByTitleAndDate",
        calendar.SimpleCalendarDeleteEventByTitleAndDate,
        "In Simple Calendar Pro, delete the calendar event titled"
        " '{event_title}' on {year}-{month}-{day}.",
        "medium",
        [
            "data_edit",
            "search",
            "complex_ui_understanding",
            "requires_setup",
            "parameterized",
        ],
        "7",
    ),
    (
        "SimpleCalendarDeleteTomorrowEvents",
        calendar.SimpleCalendarDeleteTomorrowEvents,
        "In Simple Calendar Pro, delete all calendar events for tomorrow.",
        "medium",
        ["data_edit", "math_counting", "requires_setup", "parameterized"],
        "6",
    ),
    (
        "SimpleCalendarAddTomorrowEvent",
        calendar.SimpleCalendarAddOneEventTomorrow,
        "For tomorrow in Simple Calendar Pro, put '{event_title}' on the"
        " calendar at {hour}h for {duration_mins} mins. Set the description to"
        " '{event_description}'.",
        "medium",
        ["data_entry", "math_counting", "parameterized"],
        "13",
    ),
    (
        "SimpleCalendarAddEventInTwoWeeks",
        calendar.SimpleCalendarAddOneEventInTwoWeeks,
        "Add '{event_title}' to Simple Calendar Pro for the date two weeks"
        " from today. It starts at {hour}h, runs {duration_mins} mins, and has"
        " description '{event_description}'.",
        "medium",
        ["data_entry", "math_counting", "parameterized"],
        "13",
    ),
    (
        "SimpleCalendarAddRepeatingWeeklyEvent",
        calendar.SimpleCalendarAddRepeatingEvent,
        "Set up '{event_title}' in Simple Calendar Pro starting"
        " {year}-{month}-{day} at {hour}h as a {repeat_rule} repeating event."
        " Each occurrence lasts {duration_mins} mins and uses description"
        " '{event_description}'.",
        "hard",
        ["data_entry", "complex_ui_understanding", "parameterized"],
        "20",
    ),
    (
        "SimpleCalendarDeleteSingleTimedEvent",
        calendar.SimpleCalendarDeleteOneEvent,
        "Find the {year}-{month}-{day} {hour}h Simple Calendar Pro entry named"
        " '{event_title}' and delete it.",
        "medium",
        ["data_edit", "search", "requires_setup", "parameterized"],
        "7",
    ),
    (
        "SimpleCalendarDeleteEventsThisWeekday",
        calendar.SimpleCalendarDeleteEventsOnRelativeDay,
        "For this {day_of_week}, remove the whole day's Simple Calendar Pro"
        " schedule.",
        "medium",
        ["data_edit", "math_counting", "requires_setup", "parameterized"],
        "7",
    ),
    (
        "ContactsAddClipboardContact",
        contacts.ContactsAddClipboardContact,
        "In Contacts, create a new contact using the name and phone number"
        " currently in the clipboard.",
        "medium",
        ["data_entry", "cross_app", "parameterized"],
        "7",
    ),
    (
        "ContactsAddEmergencyContact",
        contacts.ContactsAddEmergencyContact,
        "In Contacts, add the emergency contact described in the latest text"
        " message from {sender_number}.",
        "medium",
        ["data_entry", "information_extraction", "requires_setup"],
        "9",
    ),
    (
        "ContactsAddFromIncomingSms",
        contacts.ContactsAddFromIncomingSms,
        "In Contacts, add the person and phone number described in the latest"
        " text message from {sender_number}.",
        "medium",
        ["data_entry", "information_extraction", "requires_setup"],
        "9",
    ),
    (
        "ContactsAddFromMarkorNote",
        contacts.ContactsAddFromMarkorNote,
        "In Markor, open contacts_to_add.txt and add the contact listed for"
        " {role} to Contacts.",
        "hard",
        [
            "data_entry",
            "cross_app",
            "information_extraction",
            "requires_setup",
        ],
        "13",
    ),
    (
        "ContactsAddContractorFromClipboard",
        contacts.ContactsAddContractorFromClipboard,
        "In Contacts, create a new contact for the contractor listed in the"
        " clipboard.",
        "medium",
        ["data_entry", "cross_app", "information_extraction"],
        "7",
    ),
    (
        "ContactsAddClinicCallbackFromSms",
        contacts.ContactsAddClinicCallbackFromSms,
        "In Contacts, add the clinic callback contact described in the latest"
        " text message from {sender_number}.",
        "medium",
        ["data_entry", "information_extraction", "requires_setup"],
        "9",
    ),
    (
        "ContactsAddVendorFromMarkorNote",
        contacts.ContactsAddVendorFromMarkorNote,
        "In Markor, open contacts_to_add.txt and add the contact listed for"
        " {role} to Contacts.",
        "hard",
        [
            "data_entry",
            "cross_app",
            "information_extraction",
            "requires_setup",
        ],
        "13",
    ),
    (
        "ExpenseAddFoodPurchase",
        expense.ExpenseAddFoodPurchase,
        "In Pro Expense, add this {category} expense: name {expense_name},"
        " amount {amount}, note {note}.",
        "medium",
        ["data_entry", "parameterized"],
        "9",
    ),
    (
        "ExpenseAddHighValueExpensesFromMarkor",
        expense.ExpenseAddHighValueExpensesFromMarkor,
        "In Markor, open expense_candidates.txt. Add only the expenses with"
        " amount at least {min_amount} into Pro Expense.",
        "hard",
        [
            "data_entry",
            "cross_app",
            "information_extraction",
            "requires_setup",
        ],
        "28",
    ),
    (
        "ExpenseAddTwoEducationExpenses",
        expense.ExpenseAddTwoEducationExpenses,
        "In Pro Expense, add these two Education expenses:\n{expense_summary}",
        "hard",
        ["data_entry", "repetition", "parameterized"],
        "18",
    ),
    (
        "ExpenseDeleteEntertainmentExpenses",
        expense.ExpenseDeleteEntertainmentExpenses,
        "In Pro Expense, delete all {category} expenses and leave the other"
        " expenses unchanged.",
        "medium",
        ["data_edit", "search", "requires_setup", "parameterized"],
        "12",
    ),
    (
        "ExpenseAddTransportationPurchase",
        expense.ExpenseAddTransportationPurchase,
        "In Pro Expense, record this {category} expense with name"
        " {expense_name}, amount {amount}, and note {note}.",
        "medium",
        ["data_entry", "parameterized"],
        "9",
    ),
    (
        "ExpenseAddTwoHealthCareExpenses",
        expense.ExpenseAddTwoHealthCareExpenses,
        "In Pro Expense, add these two Health Care expenses:\n"
        "{expense_summary}",
        "hard",
        ["data_entry", "repetition", "parameterized"],
        "18",
    ),
    (
        "ExpenseDeleteHousingExpenses",
        expense.ExpenseDeleteHousingExpenses,
        "In Pro Expense, delete all {category} expenses and keep every other"
        " category unchanged.",
        "medium",
        ["data_edit", "search", "requires_setup", "parameterized"],
        "12",
    ),
    (
        "ExpenseDeleteTransportationExpenses",
        expense.ExpenseDeleteTransportationExpenses,
        "In Pro Expense, remove every {category} expense while leaving the"
        " rest of the expense list alone.",
        "medium",
        ["data_edit", "search", "requires_setup", "parameterized"],
        "12",
    ),
    (
        "RecipeAddRecipesFromMarkorWithIngredient",
        recipe.RecipeAddRecipesFromMarkorWithIngredient,
        "In Markor, open recipe_candidates.txt. Add only the recipes whose"
        " directions mention {ingredient} into Broccoli app.",
        "hard",
        [
            "data_entry",
            "cross_app",
            "information_extraction",
            "requires_setup",
        ],
        "32",
    ),
    (
        "RecipeAddThirtyMinuteRecipe",
        recipe.RecipeAddThirtyMinuteRecipe,
        "In Broccoli app, add the recipe {recipe_title}. Description:"
        " {description}. Servings: {servings}. Preparation time: {prep_time}."
        " Ingredients: {ingredients}. Directions: {directions}.",
        "hard",
        ["data_entry", "parameterized"],
        "18",
    ),
    (
        "RecipeAddTwoFamilyServingRecipes",
        recipe.RecipeAddTwoFamilyServingRecipes,
        "In Broccoli app, add these two recipes that each make {servings}:\n"
        "{recipe_summary}",
        "hard",
        ["data_entry", "repetition", "parameterized"],
        "32",
    ),
    (
        "RecipeDeleteThirtyMinuteRecipes",
        recipe.RecipeDeleteThirtyMinuteRecipes,
        "In Broccoli app, delete every recipe with preparation time"
        " {prep_time}.",
        "medium",
        ["data_edit", "search", "requires_setup", "parameterized"],
        "12",
    ),
    (
        "RecipeAddTwentyMinuteRecipe",
        recipe.RecipeAddTwentyMinuteRecipe,
        "In Broccoli app, add the recipe {recipe_title}. Description:"
        " {description}. Servings: {servings}. Preparation time: {prep_time}."
        " Ingredients: {ingredients}. Directions: {directions}.",
        "hard",
        ["data_entry", "parameterized"],
        "18",
    ),
    (
        "RecipeAddTwoSmallServingRecipes",
        recipe.RecipeAddTwoSmallServingRecipes,
        "In Broccoli app, add these two recipes that each make {servings}:\n"
        "{recipe_summary}",
        "hard",
        ["data_entry", "repetition", "parameterized"],
        "32",
    ),
    (
        "RecipeDeleteTwentyMinuteRecipes",
        recipe.RecipeDeleteTwentyMinuteRecipes,
        "In Broccoli app, delete every recipe with preparation time"
        " {prep_time}.",
        "medium",
        ["data_edit", "search", "requires_setup", "parameterized"],
        "12",
    ),
    (
        "RecipeAddRecipesFromMarkorWithChicken",
        recipe.RecipeAddRecipesFromMarkorWithChicken,
        "In Markor, open recipe_candidates.txt. Add only the recipes whose"
        " directions mention {ingredient} into Broccoli app.",
        "hard",
        [
            "data_entry",
            "cross_app",
            "information_extraction",
            "requires_setup",
        ],
        "32",
    ),
    (
        "SimpleSmsForwardSecurityCode",
        sms.SimpleSmsForwardSecurityCode,
        "In Simple SMS Messenger, forward the security code from {sender_name}"
        " to {recipient_name}. Send only the code.",
        "medium",
        [
            "data_entry",
            "information_extraction",
            "requires_setup",
            "parameterized",
        ],
        "10",
    ),
    (
        "SimpleSmsForwardTrackingNumber",
        sms.SimpleSmsForwardTrackingNumber,
        "In Simple SMS Messenger, forward the package tracking number from"
        " {sender_name} to {recipient_name}. Send only the tracking number.",
        "medium",
        [
            "data_entry",
            "information_extraction",
            "requires_setup",
            "parameterized",
        ],
        "10",
    ),
    (
        "SimpleSmsSendToSavedContact",
        sms.SimpleSmsSendToSavedContact,
        "In Simple SMS Messenger, send {message} to the saved contact {name}.",
        "medium",
        ["data_entry", "search", "requires_setup", "parameterized"],
        "8",
    ),
    (
        "SimpleSmsTextClipboardToSavedContact",
        sms.SimpleSmsTextClipboardToSavedContact,
        "In Simple SMS Messenger, send the clipboard content to the saved"
        " contact {name}.",
        "medium",
        ["data_entry", "cross_app", "requires_setup", "parameterized"],
        "9",
    ),
    (
        "SimpleSmsForwardDoorCode",
        sms.SimpleSmsForwardDoorCode,
        "In Simple SMS Messenger, forward the door code from {sender_name} to"
        " {recipient_name}. Send only the code.",
        "medium",
        [
            "data_entry",
            "information_extraction",
            "requires_setup",
            "parameterized",
        ],
        "10",
    ),
    (
        "SimpleSmsForwardAppointmentTime",
        sms.SimpleSmsForwardAppointmentTime,
        "In Simple SMS Messenger, forward the appointment time from"
        " {sender_name} to {recipient_name}. Send only the time.",
        "medium",
        [
            "data_entry",
            "information_extraction",
            "requires_setup",
            "parameterized",
        ],
        "10",
    ),
    (
        "SimpleSmsSendNoteSnippetToSavedContact",
        sms.SimpleSmsSendNoteSnippetToSavedContact,
        "In Simple SMS Messenger, send only the snippet from the clipboard to"
        " the saved contact {name}.",
        "medium",
        [
            "data_entry",
            "cross_app",
            "information_extraction",
            "requires_setup",
        ],
        "9",
    ),
    (
        "SystemCopyReservationCodeToClipboard",
        system.SystemCopyToClipboard,
        "Put the following reservation text on the clipboard, character for"
        " character: {clipboard_content}",
        "easy",
        ["data_entry", "parameterized"],
        "3",
    ),
    (
        "SystemTurnBrightnessAllTheWayDown",
        system.SystemBrightnessMin,
        "Use Settings to drag screen brightness down to its minimum level.",
        "easy",
        ["data_edit", "parameterized"],
        "4",
    ),
    (
        "SystemTurnBrightnessAllTheWayUp",
        system.SystemBrightnessMax,
        "Use Settings to push screen brightness up to its maximum level.",
        "easy",
        ["data_edit", "parameterized"],
        "4",
    ),
    (
        "SystemEnableWifiFromSettings",
        system.SystemWifiTurnOn,
        "Go into Settings and switch on WiFi.",
        "easy",
        ["data_edit", "parameterized"],
        "4",
    ),
    (
        "SystemDisableBluetoothFromSettings",
        system.SystemBluetoothTurnOff,
        "Go into Settings and switch off Bluetooth.",
        "easy",
        ["data_edit", "parameterized"],
        "4",
    ),
    (
        "FilesMoveMediaFileToAnotherFolder",
        files.FilesMoveFile,
        "With the Files app, transfer {file_name} from {source_folder} into"
        " {destination_folder} on Android storage.",
        "medium",
        ["data_edit", "search", "screen_reading", "parameterized"],
        "10",
    ),
    (
        "FilesDeleteDownloadedFile",
        files.FilesDeleteFile,
        "In the Files app, remove {file_name} from the Android storage folder"
        " {subfolder}.",
        "medium",
        ["data_edit", "search", "parameterized"],
        "5",
    ),
    (
        "ClockCreateFocusTimer",
        clock.ClockTimerEntry,
        "Set up, but do not run, a Clock countdown reading {hours}:{minutes}:"
        "{seconds}.",
        "easy",
        ["data_entry", "parameterized"],
        "3",
    ),
    (
        "ClockStartStopwatch",
        clock.ClockStopWatchRunning,
        "Launch Clock and get the stopwatch running.",
        "easy",
        ["data_edit"],
        "3",
    ),
    (
        "ClockLeaveStopwatchPaused",
        clock.ClockStopWatchPausedVerify,
        "Show the stopwatch in Clock in its paused state.",
        "easy",
        ["verification"],
        "1",
    ),
    (
        "CameraCaptureReferencePhoto",
        camera_tasks.CameraTakePhoto,
        "Capture a single still image with the Camera app.",
        "easy",
        ["data_entry"],
        "2",
    ),
    (
        "CameraRecordShortVideo",
        camera_tasks.CameraTakeVideo,
        "Capture one video clip with the Camera app.",
        "medium",
        ["data_entry"],
        "3",
    ),
    (
        "AudioRecorderRecordVoiceMemo",
        audio_recorder.AudioRecorderRecordAudio,
        "Use Audio Recorder to make and keep one new recording.",
        "easy",
        ["data_entry", "requires_setup"],
        "6",
    ),
    (
        "AudioRecorderRecordNamedBriefing",
        audio_recorder.AudioRecorderRecordAudioWithFileName,
        "Make a new recording in Audio Recorder and give the saved clip the"
        " name {file_name}.",
        "medium",
        [
            "data_entry",
            "complex_ui_understanding",
            "requires_setup",
            "parameterized",
        ],
        "10",
    ),
    (
        "VlcCreateReviewPlaylist",
        vlc.VlcCreatePlaylist,
        "Build a VLC playlist titled {playlist_name}. Add the video files in"
        " this exact sequence: {files}.",
        "hard",
        ["data_entry", "repetition", "requires_setup", "parameterized"],
        "18",
    ),
    (
        "VlcCreateTwoReviewPlaylists",
        vlc.VlcCreateTwoPlaylists,
        "In VLC, make two ordered playlists. The first is {playlist_name1} with"
        " {files1}; the second is {playlist_name2} with {files2}.",
        "hard",
        ["data_entry", "repetition", "requires_setup", "parameterized"],
        "32",
    ),
    (
        "RetroMusicCreateCommutePlaylist",
        retro_music.RetroCreatePlaylist,
        "Create a Retro Music playlist called {playlist_name} and place these"
        " tracks in order: {files}.",
        "hard",
        ["data_entry", "repetition", "requires_setup", "parameterized"],
        "18",
    ),
    (
        "RetroMusicAddSongsToQueue",
        retro_music.RetroPlayingQueue,
        "Queue up these Retro Music tracks in the listed order: {files}.",
        "hard",
        ["data_entry", "repetition", "requires_setup", "parameterized"],
        "16",
    ),
    (
        "SimpleGalleryCopyReceiptToDownloads",
        simple_gallery_pro.SaveCopyOfReceiptTaskEval,
        "Using Simple Gallery Pro, duplicate the DCIM image {file_name} into"
        " the Download folder.",
        "medium",
        ["data_edit", "requires_setup", "parameterized"],
        "6",
    ),
    (
        "OpenNamedSystemApp",
        system.OpenAppTaskEval,
        "Bring up the {app_name} app, accepting any required permission"
        " prompts.",
        "easy",
        ["parameterized"],
        "2",
    ),
]



ALL_TASKS = tuple(_make_task(*spec) for spec in _SPECS)
METADATA: list[dict[str, Any]] = [task.expanded_metadata for task in ALL_TASKS]
