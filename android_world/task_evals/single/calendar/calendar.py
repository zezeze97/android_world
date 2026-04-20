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

"""Tasks for Simple Calendar Pro app."""

import dataclasses
import random
from typing import Any, Callable, Optional
from android_world.env import device_constants
from android_world.task_evals.common_validators import sqlite_validators
from android_world.task_evals.single.calendar import calendar_evaluators
from android_world.task_evals.single.calendar import calendar_utils
from android_world.task_evals.single.calendar import events_generator
from android_world.task_evals.utils import sqlite_schema_utils
from android_world.utils import datetime_utils

# Keys in generated parameters and used to populate goal template.
_YEAR = "year"
_MONTH = "month"
_DAY = "day"
_DAY_OF_WEEK = "day_of_week"
_HOUR = "hour"
EVENT_TITLE = "event_title"
_EVENT_DESCRIPTION = "event_description"
_DURATION_MINS = "duration_mins"
_LOCATION = "location"
_REPEAT_INTERVAL = "repeat_rule"
_REPEAT_INTERVALS = {"daily": 60 * 60 * 24, "weekly": 60 * 60 * 24 * 7}
_EVENT_LOCATIONS = [
    "Building A Conference Room",
    "Downtown Library",
    "Main Office",
    "North Campus",
    "Remote Video Call",
    "Training Room 2",
]


def generate_noise_events(
    target_events: list[sqlite_schema_utils.CalendarEvent],
    n: int,
    filter_fn: Optional[
        Callable[[sqlite_schema_utils.CalendarEvent], bool]
    ] = None,
) -> list[sqlite_schema_utils.CalendarEvent]:
  if filter_fn is None:
    target_titles = set(event.title for event in target_events)
    filter_fn = lambda candidate: candidate.title not in target_titles

  return sqlite_schema_utils.get_random_items(
      n,
      lambda: events_generator.generate_event(
          datetime_utils.create_random_october_2023_unix_ts(start_day=1)
      ),
      filter_fn=filter_fn,
  )


class _SimpleCalendar(sqlite_validators.SQLiteApp):
  """Base class for calendar tasks and evaluation logic.

                  October 2023
              Su Mo Tu We Th Fr Sa
              1  2  3  4  5  6  7
              8  9 10 11 12 13 14
              [15]16 17 18 19 20 21
              22 23 24 25 26 27 28
              29 30 31

  The current date on the emulator will be set as October 15, 2023.
  """

  app_name_with_db = "simple calendar pro"
  app_names = ("simple calendar pro",)
  schema = {}

  db_key = "id"
  db_path = calendar_utils.DB_PATH
  table_name = calendar_utils.EVENTS_TABLE
  row_type = sqlite_schema_utils.CalendarEvent


class SimpleCalendarAddOneEvent(
    sqlite_validators.AddMultipleRows, _SimpleCalendar
):
  """Task for creating a calendar event in Simple Calendar Pro.

  Uses the absolute date in the template.
  """

  n_rows = 1  # Unused, but required by base class.
  complexity = 3.4
  template = (
      "In Simple Calendar Pro, create a calendar event on {year}-{month}-{day}"
      " at {hour}h with the title '{event_title}' and the description"
      " '{event_description}'. The event should last for {duration_mins} mins."
  )

  @classmethod
  def _get_random_target_row(cls) -> sqlite_schema_utils.CalendarEvent:
    """Generates a random calendar event."""
    return events_generator.generate_event(
        datetime_utils.create_random_october_2023_unix_ts()
    )

  def validate_addition_integrity(
      self,
      before: list[sqlite_schema_utils.CalendarEvent],
      after: list[sqlite_schema_utils.CalendarEvent],
      reference_rows: list[sqlite_schema_utils.CalendarEvent],
  ) -> bool:
    """Validates the integrity of the event addition."""
    return calendar_evaluators.validate_event_addition_integrity(
        before,
        after,
        reference_rows,
        extras_compare=["repeat_rule", "repeat_interval"],
    )

  @classmethod
  def generate_random_params(cls) -> dict[str, Any]:
    """Generate random parameters for a new calendar event task."""
    event = cls._get_random_target_row()
    n_noise_events = random.randint(0, 20)
    return {
        _YEAR: device_constants.DT.year,
        _MONTH: device_constants.DT.month,
        _DAY: event.start_datetime.day,
        _HOUR: event.start_datetime.hour,
        _DURATION_MINS: event.duration_mins,
        EVENT_TITLE: event.title,
        _EVENT_DESCRIPTION: event.description,
        sqlite_validators.ROW_OBJECTS: [event],
        sqlite_validators.NOISE_ROW_OBJECTS: generate_noise_events(
            [event], n_noise_events
        ),
    }


class SimpleCalendarAddOneEventRelativeDay(SimpleCalendarAddOneEvent):
  """Task for creating a calendar event in Simple Calendar Pro.

  Uses the relative day of week in the template: from "this Monday" -> "this
  Sunday".
  """

  complexity = 3.4
  _DAY_RANGE = 6

  template = (
      "In Simple Calendar Pro, create a calendar event for this {day_of_week}"
      " at {hour}h with the title '{event_title}' and the description"
      " '{event_description}'. The event should last for {duration_mins} mins."
  )

  @property
  def goal(self) -> str:
    # Add day of week.
    dt: sqlite_schema_utils.CalendarEvent = self.params[
        sqlite_validators.ROW_OBJECTS
    ][0]
    day_of_week = dt.start_datetime.strftime("%A")
    self.params[_DAY_OF_WEEK] = day_of_week
    return self.template.format(**self.params)

  @classmethod
  def _get_random_target_row(cls):
    return events_generator.generate_event(
        datetime_utils.create_random_october_2023_unix_ts(
            # Monday, Oct 16 -> Saturday, Oct 21.
            start_day=device_constants.DT.day + 1,
            end_day=(
                device_constants.DT.day
                + SimpleCalendarAddOneEventRelativeDay._DAY_RANGE
            ),
        )
    )


class SimpleCalendarAddOneEventTomorrow(SimpleCalendarAddOneEvent):
  """Task for creating a calendar event in Simple Calendar Pro for tomorrow."""

  complexity = 3.4
  template = (
      "In Simple Calendar Pro, create a calendar event for tomorrow"
      " at {hour}h with the title '{event_title}' and the description"
      " '{event_description}'. The event should last for {duration_mins} mins."
  )

  @classmethod
  def _get_random_target_row(cls):
    # Generate an event for tomorrow.
    return events_generator.generate_event(
        datetime_utils.create_random_october_2023_unix_ts(
            device_constants.DT.day + 1, device_constants.DT.day + 1
        )
    )


class SimpleCalendarAddOneEventInTwoWeeks(SimpleCalendarAddOneEvent):
  """Task for creating a calendar event in Simple Calendar Pro in two weeks from today."""

  complexity = 3.4
  template = (
      "In Simple Calendar Pro, create a calendar event in two weeks from today"
      " at {hour}h with the title '{event_title}' and the description"
      " '{event_description}'. The event should last for {duration_mins} mins."
  )

  @classmethod
  def _get_random_target_row(cls):
    return events_generator.generate_event(
        datetime_utils.create_random_october_2023_unix_ts(
            device_constants.DT.day + 14, device_constants.DT.day + 14
        )
    )


class SimpleCalendarAddEventWithLocation(SimpleCalendarAddOneEvent):
  """Task for creating a calendar event with a location."""

  complexity = 3.6
  template = (
      "In Simple Calendar Pro, create a calendar event on {year}-{month}-{day}"
      " at {hour}h located at '{location}' with the title '{event_title}' and"
      " the description '{event_description}'. The event should last for"
      " {duration_mins} mins."
  )

  @classmethod
  def generate_random_params(cls) -> dict[str, Any]:
    event = dataclasses.replace(
        cls._get_random_target_row(),
        location=random.choice(_EVENT_LOCATIONS),
    )
    n_noise_events = random.randint(0, 20)
    return {
        _YEAR: device_constants.DT.year,
        _MONTH: device_constants.DT.month,
        _DAY: event.start_datetime.day,
        _HOUR: event.start_datetime.hour,
        _DURATION_MINS: event.duration_mins,
        EVENT_TITLE: event.title,
        _EVENT_DESCRIPTION: event.description,
        _LOCATION: event.location,
        sqlite_validators.ROW_OBJECTS: [event],
        sqlite_validators.NOISE_ROW_OBJECTS: generate_noise_events(
            [event], n_noise_events
        ),
    }


class SimpleCalendarAddLongEvent(SimpleCalendarAddOneEvent):
  """Task for creating a longer calendar event."""

  complexity = 3.6
  template = (
      "In Simple Calendar Pro, create a long calendar event on"
      " {year}-{month}-{day} at {hour}h with the title '{event_title}' and"
      " the description '{event_description}'. The event should last for"
      " {duration_mins} mins."
  )

  @classmethod
  def generate_random_params(cls) -> dict[str, Any]:
    event_template = cls._get_random_target_row()
    duration_mins = random.choice([90, 120, 180])
    event = dataclasses.replace(
        event_template,
        end_ts=event_template.start_ts + duration_mins * 60,
    )
    return {
        _YEAR: device_constants.DT.year,
        _MONTH: device_constants.DT.month,
        _DAY: event.start_datetime.day,
        _HOUR: event.start_datetime.hour,
        _DURATION_MINS: event.duration_mins,
        EVENT_TITLE: event.title,
        _EVENT_DESCRIPTION: event.description,
        sqlite_validators.ROW_OBJECTS: [event],
        sqlite_validators.NOISE_ROW_OBJECTS: generate_noise_events(
            [event], random.randint(0, 20)
        ),
    }


class SimpleCalendarAddEventNextWeek(SimpleCalendarAddOneEvent):
  """Task for creating an event on a named day next week."""

  complexity = 3.6
  template = (
      "In Simple Calendar Pro, create a calendar event for next {day_of_week}"
      " at {hour}h with the title '{event_title}' and the description"
      " '{event_description}'. The event should last for {duration_mins} mins."
  )

  @classmethod
  def _get_random_target_row(cls):
    return events_generator.generate_event(
        datetime_utils.create_random_october_2023_unix_ts(
            start_day=device_constants.DT.day + 7,
            end_day=device_constants.DT.day + 13,
        )
    )

  @classmethod
  def generate_random_params(cls) -> dict[str, Any]:
    event = cls._get_random_target_row()
    return {
        _DAY_OF_WEEK: event.start_datetime.strftime("%A"),
        _HOUR: event.start_datetime.hour,
        _DURATION_MINS: event.duration_mins,
        EVENT_TITLE: event.title,
        _EVENT_DESCRIPTION: event.description,
        sqlite_validators.ROW_OBJECTS: [event],
        sqlite_validators.NOISE_ROW_OBJECTS: generate_noise_events(
            [event], random.randint(0, 20)
        ),
    }


class SimpleCalendarAddTwoEventsSameDay(SimpleCalendarAddOneEvent):
  """Task for creating two events on the same calendar day."""

  n_rows = 2
  complexity = 4.6
  template = (
      "In Simple Calendar Pro, create two calendar events on"
      " {year}-{month}-{day}: first at {hour1}h titled '{event_title1}' with"
      " description '{event_description1}' lasting {duration_mins1} mins, and"
      " second at {hour2}h titled '{event_title2}' with description"
      " '{event_description2}' lasting {duration_mins2} mins."
  )

  @classmethod
  def generate_random_params(cls) -> dict[str, Any]:
    day = random.randint(device_constants.DT.day, 31)
    hour1, hour2 = sorted(random.sample(range(8, 20), 2))
    event1 = events_generator.generate_event(
        datetime_utils._create_unix_ts(day=day, hour=hour1)
    )
    event2 = events_generator.generate_event(
        datetime_utils._create_unix_ts(day=day, hour=hour2)
    )
    events = [event1, event2]
    noise_events = generate_noise_events(
        events,
        random.randint(0, 20),
        filter_fn=lambda candidate: (
            candidate.start_datetime.day != day
            and candidate.title not in (event.title for event in events)
        ),
    )
    return {
        _YEAR: device_constants.DT.year,
        _MONTH: device_constants.DT.month,
        _DAY: day,
        "hour1": event1.start_datetime.hour,
        "hour2": event2.start_datetime.hour,
        "duration_mins1": event1.duration_mins,
        "duration_mins2": event2.duration_mins,
        "event_title1": event1.title,
        "event_title2": event2.title,
        "event_description1": event1.description,
        "event_description2": event2.description,
        sqlite_validators.ROW_OBJECTS: events,
        sqlite_validators.NOISE_ROW_OBJECTS: noise_events,
    }


class SimpleCalendarAddTwoEventsDifferentDays(SimpleCalendarAddOneEvent):
  """Task for creating two events on different calendar days."""

  n_rows = 2
  complexity = 4.8
  template = (
      "In Simple Calendar Pro, create two calendar events: one on"
      " {year}-{month}-{day1} at {hour1}h titled '{event_title1}' with"
      " description '{event_description1}' lasting {duration_mins1} mins, and"
      " one on {year}-{month}-{day2} at {hour2}h titled '{event_title2}' with"
      " description '{event_description2}' lasting {duration_mins2} mins."
  )

  @classmethod
  def generate_random_params(cls) -> dict[str, Any]:
    day1, day2 = sorted(random.sample(range(device_constants.DT.day, 32), 2))
    hour1 = random.randint(8, 18)
    hour2 = random.randint(8, 18)
    event1 = events_generator.generate_event(
        datetime_utils._create_unix_ts(day=day1, hour=hour1)
    )
    event2 = events_generator.generate_event(
        datetime_utils._create_unix_ts(day=day2, hour=hour2)
    )
    events = [event1, event2]
    noise_events = generate_noise_events(
        events,
        random.randint(0, 20),
        filter_fn=lambda candidate: (
            candidate.start_datetime.day not in {day1, day2}
            and candidate.title not in (event.title for event in events)
        ),
    )
    return {
        _YEAR: device_constants.DT.year,
        _MONTH: device_constants.DT.month,
        "day1": day1,
        "day2": day2,
        "hour1": event1.start_datetime.hour,
        "hour2": event2.start_datetime.hour,
        "duration_mins1": event1.duration_mins,
        "duration_mins2": event2.duration_mins,
        "event_title1": event1.title,
        "event_title2": event2.title,
        "event_description1": event1.description,
        "event_description2": event2.description,
        sqlite_validators.ROW_OBJECTS: events,
        sqlite_validators.NOISE_ROW_OBJECTS: noise_events,
    }


class SimpleCalendarAddRepeatingEvent(SimpleCalendarAddOneEvent):
  """Task for creating a repeating calendar event in Simple Calendar Pro."""

  complexity = 3.4
  template = (
      "In Simple Calendar Pro, create a recurring calendar event titled"
      " '{event_title}' starting on {year}-{month}-{day} at"
      " {hour}h. The event recurs {repeat_rule}, forever, and lasts for"
      " {duration_mins} minutes each occurrence. The event description should"
      " be '{event_description}'."
  )

  @classmethod
  def generate_random_params(cls) -> dict[str, Any]:
    """Generate random parameters for a new calendar event task."""
    template = cls._get_random_target_row()
    repeat_interval = random.choice(list(_REPEAT_INTERVALS))
    if repeat_interval == "weekly":
      repeat_rule = calendar_utils.generate_simple_calendar_weekly_repeat_rule(
          template.start_datetime.isoweekday()
      )
    else:
      repeat_rule = 0
    event = dataclasses.replace(
        template,
        repeat_interval=_REPEAT_INTERVALS[repeat_interval],
        repeat_rule=repeat_rule,
    )
    noise_events = generate_noise_events([event], random.randint(0, 20))
    return {
        _YEAR: device_constants.DT.year,
        _MONTH: device_constants.DT.month,
        _DAY: event.start_datetime.day,
        _HOUR: event.start_datetime.hour,
        _DURATION_MINS: event.duration_mins,
        EVENT_TITLE: event.title,
        _EVENT_DESCRIPTION: event.description,
        sqlite_validators.ROW_OBJECTS: [event],
        sqlite_validators.NOISE_ROW_OBJECTS: noise_events,
        _REPEAT_INTERVAL: repeat_interval,
    }


class SimpleCalendarDeleteEvents(
    sqlite_validators.DeleteMultipleRows, _SimpleCalendar
):
  """Task to delete multiple calendar events in Simple Calendar Pro.

  Uses the absolute date in the template.
  """

  n_rows = 3
  n_rows_noise = 20
  complexity = 1.4
  template = (
      "In Simple Calendar Pro, delete all the calendar events on"
      " {year}-{month}-{day}"
  )

  def validate_deletion_integrity(
      self,
      before: list[sqlite_schema_utils.CalendarEvent],
      after: list[sqlite_schema_utils.CalendarEvent],
  ) -> bool:
    """Validates the integrity of the event deletion."""
    return calendar_evaluators.validate_event_removal_integrity(
        before, after, [r.id for r in self.rows_to_delete]
    )

  @classmethod
  def _get_random_target_row(cls, day: int):
    return events_generator.generate_event(
        datetime_utils.create_random_october_2023_unix_ts(
            start_day=day, end_day=day
        )
    )

  @classmethod
  def generate_random_params(cls) -> dict[str, Any]:
    """Generate random parameters for a remove calendar event task."""
    template = events_generator.generate_event(
        datetime_utils.create_random_october_2023_unix_ts()
    )
    events = [
        cls._get_random_target_row(template.start_datetime.day)
        for _ in range(cls.n_rows)
    ]
    noise_events = generate_noise_events(
        events,
        cls.n_rows_noise,
        filter_fn=lambda candidate: candidate.start_datetime.day
        not in (target.start_datetime.day for target in events),
    )
    return {
        _YEAR: device_constants.DT.year,
        _MONTH: device_constants.DT.month,
        _DAY: template.start_datetime.day,
        sqlite_validators.ROW_OBJECTS: events,
        sqlite_validators.NOISE_ROW_OBJECTS: noise_events,
    }


class SimpleCalendarDeleteOneEvent(SimpleCalendarDeleteEvents):
  """Task to delete a single calendar event in Simple Calendar Pro.

  Uses the absolute date in the template.
  """

  n_rows = 1
  complexity = 1.2
  template = (
      "In Simple Calendar Pro, delete the calendar event on"
      " {year}-{month}-{day} at {hour}h with the title '{event_title}'"
  )

  @classmethod
  def _get_random_target_row(cls):
    return events_generator.generate_event(
        datetime_utils.create_random_october_2023_unix_ts()
    )

  @classmethod
  def generate_random_params(cls) -> dict[str, Any]:
    """Generate random parameters for a remove calendar event task."""
    event = cls._get_random_target_row()
    noise_events = generate_noise_events(
        [event],
        cls.n_rows_noise,
        filter_fn=(
            lambda candidate: (candidate.start_datetime != event.start_datetime)
            and (candidate.title != event.title)
        ),
    )
    return {
        _YEAR: device_constants.DT.year,
        _MONTH: device_constants.DT.month,
        _DAY: event.start_datetime.day,
        _HOUR: event.start_datetime.hour,
        _DURATION_MINS: event.duration_mins,
        EVENT_TITLE: event.title,
        _EVENT_DESCRIPTION: event.description,
        sqlite_validators.ROW_OBJECTS: [event],
        sqlite_validators.NOISE_ROW_OBJECTS: noise_events,
    }


class SimpleCalendarDeleteEventByTitle(SimpleCalendarDeleteOneEvent):
  """Task to delete a single calendar event using only its title."""

  complexity = 1.4
  template = (
      "In Simple Calendar Pro, delete the calendar event titled"
      " '{event_title}'."
  )

  @classmethod
  def generate_random_params(cls) -> dict[str, Any]:
    event = cls._get_random_target_row()
    noise_events = generate_noise_events(
        [event],
        cls.n_rows_noise,
        filter_fn=lambda candidate: candidate.title != event.title,
    )
    return {
        EVENT_TITLE: event.title,
        sqlite_validators.ROW_OBJECTS: [event],
        sqlite_validators.NOISE_ROW_OBJECTS: noise_events,
    }


class SimpleCalendarDeleteEventByTitleAndDate(SimpleCalendarDeleteOneEvent):
  """Task to delete a single calendar event using title and date."""

  complexity = 1.4
  template = (
      "In Simple Calendar Pro, delete the calendar event titled"
      " '{event_title}' on {year}-{month}-{day}."
  )

  @classmethod
  def generate_random_params(cls) -> dict[str, Any]:
    event = cls._get_random_target_row()
    noise_events = generate_noise_events(
        [event],
        cls.n_rows_noise,
        filter_fn=lambda candidate: (
            candidate.title != event.title
            and candidate.start_datetime.day != event.start_datetime.day
        ),
    )
    return {
        _YEAR: device_constants.DT.year,
        _MONTH: device_constants.DT.month,
        _DAY: event.start_datetime.day,
        EVENT_TITLE: event.title,
        sqlite_validators.ROW_OBJECTS: [event],
        sqlite_validators.NOISE_ROW_OBJECTS: noise_events,
    }


class SimpleCalendarDeleteTomorrowEvents(SimpleCalendarDeleteEvents):
  """Task to delete all calendar events scheduled for tomorrow."""

  n_rows = 2
  n_rows_noise = 20
  complexity = 1.4
  template = "In Simple Calendar Pro, delete all calendar events for tomorrow."

  @classmethod
  def _get_random_target_row(cls):
    return events_generator.generate_event(
        datetime_utils.create_random_october_2023_unix_ts(
            start_day=device_constants.DT.day + 1,
            end_day=device_constants.DT.day + 1,
        )
    )

  @classmethod
  def generate_random_params(cls) -> dict[str, Any]:
    events = [cls._get_random_target_row() for _ in range(cls.n_rows)]
    tomorrow = device_constants.DT.day + 1
    noise_events = generate_noise_events(
        events,
        cls.n_rows_noise,
        filter_fn=lambda candidate: candidate.start_datetime.day != tomorrow,
    )
    return {
        sqlite_validators.ROW_OBJECTS: events,
        sqlite_validators.NOISE_ROW_OBJECTS: noise_events,
    }


class SimpleCalendarDeleteEventsOnRelativeDay(SimpleCalendarDeleteEvents):
  """Task for deleting calendar events for day_of_week in Simple Calendar Pro.

  Uses the relative day of week in the template: from "this Monday" -> "this
  Sunday".
  """

  complexity = 1.2
  n_rows = 2
  _DAY_RANGE: int = 6

  template = (
      "In Simple Calendar Pro, delete all events scheduled for this"
      " {day_of_week}."
  )

  @classmethod
  def _get_random_target_row(cls, day: int):
    return events_generator.generate_event(
        datetime_utils.create_random_october_2023_unix_ts(
            start_day=day, end_day=day
        )
    )

  @classmethod
  def generate_random_params(cls) -> dict[str, Any]:
    """Generate random parameters for a remove calendar event task."""
    template = events_generator.generate_event(
        datetime_utils.create_random_october_2023_unix_ts(
            # Monday, Oct 16 -> Saturday, Oct 21.
            start_day=device_constants.DT.day + 1,
            end_day=device_constants.DT.day + cls._DAY_RANGE,
        )
    )
    events = [
        cls._get_random_target_row(template.start_datetime.day)
        for _ in range(cls.n_rows)
    ]
    noise_events = generate_noise_events(
        events,
        cls.n_rows_noise,
        filter_fn=lambda candidate: candidate.start_datetime.day
        not in (target.start_datetime.day for target in events),
    )
    return {
        _YEAR: device_constants.DT.year,
        _MONTH: device_constants.DT.month,
        _DAY: template.start_datetime.day,
        _DAY_OF_WEEK: template.start_datetime.strftime("%A"),
        sqlite_validators.ROW_OBJECTS: events,
        sqlite_validators.NOISE_ROW_OBJECTS: noise_events,
    }
