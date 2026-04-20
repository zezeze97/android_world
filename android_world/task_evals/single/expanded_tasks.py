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

from android_world.task_evals.single import markor
from android_world.task_evals.single.calendar import calendar


def _goal_from_template(template: str):

  def goal(self):
    return template.format(**self.params)

  return property(goal)


def _validation_function(name: str, base: type):
  """Creates a dedicated validation function for one expanded task."""

  def validate(self, env):
    return base.is_successful(self, env)

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
]


ALL_TASKS = tuple(_make_task(*spec) for spec in _SPECS)
METADATA: list[dict[str, Any]] = [task.expanded_metadata for task in ALL_TASKS]
