# Expanded Tasks

本文档说明本仓库新增并保留的 16 条 AndroidWorld expanded tasks。这批任务集中覆盖两个应用：

- Markor：8 条文件系统类笔记任务
- Simple Calendar Pro：8 条 SQLite 日历事件任务

这些任务的统一注册入口在 `android_world/task_evals/single/expanded_tasks.py`。`registry.py` 通过 `*expanded_tasks.ALL_TASKS` 将它们加入 Android task registry；`task_metadata.json` 中也只保留这 16 条新增任务的 metadata。

## 文件位置

- Expanded task 入口：`android_world/task_evals/single/expanded_tasks.py`
- Markor 任务实现：`android_world/task_evals/single/markor.py`
- Simple Calendar Pro 任务实现：`android_world/task_evals/single/calendar/calendar.py`
- Markor 测试：`android_world/task_evals/single/markor_test.py`
- Calendar 测试：`android_world/task_evals/single/calendar/calendar_test.py`
- Registry：`android_world/registry.py`
- Metadata：`android_world/task_metadata.json`

## 设计说明

`expanded_tasks.py` 负责集中声明新增任务清单。每个 expanded task 都由 `_SPECS` 中的一条配置生成，配置内容包括：

- task name
- 继承的基础实现类
- task template
- difficulty
- tags
- optimal steps

每条 expanded task 都会生成独立的 `validate_success` 函数入口，函数名和 `__qualname__` 对应具体任务，例如：

- `MarkorAppendToNote.validate_success`
- `SimpleCalendarAddEventWithLocation.validate_success`

这样 registry 中注册的是 expanded task 自身，而不是直接把基础实现类裸注册进去。验证函数入口是任务级独立的；具体的设备状态检查仍委托给对应 app 实现类中的 `is_successful` 逻辑。

## Markor Tasks

Markor 任务主要验证文件系统中的 note 文件或目录状态。数据路径基于 `device_constants.MARKOR_DATA`，常用验证能力包括创建文件、删除文件、检查文件是否存在、检查文件内容是否精确匹配。

| Task | Template | 目标行为 | 初始化数据 | 验证方式 |
| --- | --- | --- | --- | --- |
| `MarkorCreateNoteInFolder` | `In Markor, create a note named {file_name} inside the {folder_name} folder with the following text: {text}` | 在指定 Markor 子文件夹中创建 note | 创建目标目录，并生成干扰 note | 检查目标目录下指定文件存在且内容等于目标文本 |
| `MarkorCreateChecklistNote` | `Create a checklist note in Markor named {file_name} with these items: {items}. Each checklist item should be unchecked.` | 创建 unchecked checklist note | 无需预置目标文件 | 检查新文件内容为 `- [ ] item` 格式的 checklist |
| `MarkorAppendToNote` | `Open the Markor note {file_name} and add this text as a new line at the bottom: "{appended_text}".` | 给已有 note 末尾追加一行文本 | 预置目标 note 和干扰 note | 检查文件内容为原内容、换行、追加文本 |
| `MarkorCopyNote` | `In Markor, copy the contents of {source_name} into a new note named {new_name}. Leave the original note unchanged.` | 将已有 note 内容复制到新 note，原文件保留 | 预置 source note 和干扰 note | 检查 source 与 new note 均存在且内容一致 |
| `MarkorDeleteNoteInFolder` | `In Markor, delete the note {file_name} from the {subfolder} folder.` | 删除指定子文件夹中的 note | 预置待删除文件和干扰文件 | 使用文件删除验证逻辑确认目标文件不存在 |
| `MarkorPrependDateToNote` | `Open the Markor note {file_name} and add {date} as the first line of the note.` | 在已有 note 第一行插入日期 | 预置目标 note 和干扰 note | 检查文件内容为日期、换行、原内容 |
| `MarkorReplaceTextInNote` | `In the Markor note {file_name}, replace the text "{old_text}" with "{new_text}".` | 替换已有 note 中的指定文本 | 预置包含旧文本的目标 note 和干扰 note | 检查文件内容精确等于替换后的文本 |
| `MarkorRenameNote` | `Rename the Markor note {original_name} to {new_name} without changing its contents.` | 重命名 note 且内容不变 | 预置 original note 和干扰 note | 检查旧文件不存在、新文件存在且内容不变 |

### Markor 参数特点

- 文件名和文本内容随机生成，避免固定样本导致过拟合。
- 多数编辑类任务会生成 noise files，要求 agent 在 UI 中定位正确 note。
- `MarkorCreateNoteInFolder` 和 `MarkorDeleteNoteInFolder` 涉及子文件夹路径，覆盖更复杂的文件导航。
- `MarkorCreateChecklistNote` 要求生成 unchecked checklist 行，而不是普通纯文本列表。

## Simple Calendar Pro Tasks

Calendar 任务主要验证 SQLite 数据库中的 calendar event 行。数据库路径是 Simple Calendar Pro 的 `events.db`，验证逻辑基于已有的 SQLite task 基类和 calendar evaluator。

| Task | Template | 目标行为 | 初始化数据 | 验证方式 |
| --- | --- | --- | --- | --- |
| `SimpleCalendarAddEventWithLocation` | `In Simple Calendar Pro, create a calendar event on {year}-{month}-{day} at {hour}h located at '{location}' with the title '{event_title}' and the description '{event_description}'. The event should last for {duration_mins} mins.` | 创建带 location 的单个日历事件 | 插入干扰事件 | 检查新增事件的时间、标题、描述、location 和时长 |
| `SimpleCalendarAddLongEvent` | `In Simple Calendar Pro, create a long calendar event on {year}-{month}-{day} at {hour}h with the title '{event_title}' and the description '{event_description}'. The event should last for {duration_mins} mins.` | 创建 90/120/180 分钟的长事件 | 插入干扰事件 | 检查新增事件的 start/end 时间和内容字段 |
| `SimpleCalendarAddEventNextWeek` | `In Simple Calendar Pro, create a calendar event for next {day_of_week} at {hour}h with the title '{event_title}' and the description '{event_description}'. The event should last for {duration_mins} mins.` | 按“next weekday”创建下周事件 | 插入干扰事件 | 检查新增事件落在下周指定 weekday |
| `SimpleCalendarAddTwoEventsSameDay` | `In Simple Calendar Pro, create two calendar events on {year}-{month}-{day}: first at {hour1}h titled '{event_title1}' with description '{event_description1}' lasting {duration_mins1} mins, and second at {hour2}h titled '{event_title2}' with description '{event_description2}' lasting {duration_mins2} mins.` | 在同一天创建两个不同时间的事件 | 插入避开目标日的干扰事件 | 检查两个目标事件都被新增，且日期相同、时间不同 |
| `SimpleCalendarAddTwoEventsDifferentDays` | `In Simple Calendar Pro, create two calendar events: one on {year}-{month}-{day1} at {hour1}h titled '{event_title1}' with description '{event_description1}' lasting {duration_mins1} mins, and one on {year}-{month}-{day2} at {hour2}h titled '{event_title2}' with description '{event_description2}' lasting {duration_mins2} mins.` | 在两个不同日期创建两个事件 | 插入避开目标日期的干扰事件 | 检查两个目标事件都被新增，且日期不同 |
| `SimpleCalendarDeleteEventByTitle` | `In Simple Calendar Pro, delete the calendar event titled '{event_title}'.` | 只根据标题删除一个事件 | 预置目标事件和不同标题的干扰事件 | 检查目标事件被删除，其他事件保留 |
| `SimpleCalendarDeleteEventByTitleAndDate` | `In Simple Calendar Pro, delete the calendar event titled '{event_title}' on {year}-{month}-{day}.` | 根据标题和日期删除一个事件 | 预置目标事件和干扰事件 | 检查匹配标题与日期的事件被删除 |
| `SimpleCalendarDeleteTomorrowEvents` | `In Simple Calendar Pro, delete all calendar events for tomorrow.` | 删除明天的所有事件 | 预置明天的目标事件和非明天干扰事件 | 检查明天目标事件被删除，其他日期事件保留 |

### Calendar 参数特点

- 新增事件任务会通过 `events_generator` 生成目标 `CalendarEvent` 行。
- 删除任务会预置目标 rows 和 noise rows，再比较执行前后的数据库状态。
- `SimpleCalendarAddEventNextWeek` 和 `SimpleCalendarDeleteTomorrowEvents` 使用相对日期，覆盖日期推理能力。
- 双事件任务使用 `n_rows = 2`，要求 agent 完成重复但不完全相同的 UI 操作。

## Metadata

这 16 条任务的 metadata 字段由 `expanded_tasks.py` 中的 `_SPECS` 维护，并同步写入 `android_world/task_metadata.json`。当前新增任务数量应满足：

- `len(expanded_tasks.ALL_TASKS) == 16`
- `task_metadata.json` 总数为原始 116 条加新增 16 条，即 132 条
- 新增 16 条 task name 在 metadata 中各出现一次

如果以后修改 expanded task 名称、template、difficulty、tags 或 optimal steps，需要同时确认 `task_metadata.json` 与 `expanded_tasks.py` 保持一致。

## Registry

`registry.py` 中通过以下方式注册 expanded tasks：

```python
*expanded_tasks.ALL_TASKS,
```

这意味着 registry 不直接枚举 16 个具体类名，而是由 `expanded_tasks.py` 统一维护任务集合。新增或移除 expanded task 时，优先修改 `_SPECS`，再同步 metadata 和测试。

## 验证命令

建议在 conda 环境 `android_world` 中执行以下检查：

```bash
PYTHONPATH=/Users/zezeze/python/code/android_world conda run -n android_world python -m py_compile android_world/task_evals/single/expanded_tasks.py android_world/registry.py
PYTHONPATH=/Users/zezeze/python/code/android_world conda run -n android_world python -m json.tool android_world/task_metadata.json
PYTHONPATH=/Users/zezeze/python/code/android_world conda run -n android_world pytest -q android_world/suite_utils_test.py android_world/task_evals/single/markor_test.py android_world/task_evals/single/calendar/calendar_test.py
```

也可以用下面的脚本快速检查数量和注册状态：

```bash
PYTHONPATH=/Users/zezeze/python/code/android_world conda run -n android_world python -c 'import json; from collections import Counter; from android_world import registry; from android_world.task_evals.single import expanded_tasks; exp=[c.__name__ for c in expanded_tasks.ALL_TASKS]; meta=json.load(open("android_world/task_metadata.json")); meta_names=[x["task_name"] for x in meta]; reg=registry.TaskRegistry().get_registry(registry.TaskRegistry.ANDROID_FAMILY); print("expanded_tasks", len(exp)); print("metadata_entries", len(meta_names)); print("metadata_duplicates", [n for n,c in Counter(meta_names).items() if c>1]); print("expanded_in_metadata", sum(n in set(meta_names) for n in exp)); print("expanded_in_android_registry", sum(n in set(reg) for n in exp)); print("validators_unique", len({c.validate_success for c in expanded_tasks.ALL_TASKS}))'
```

期望结果：

- `expanded_tasks 16`
- `metadata_entries 132`
- `metadata_duplicates []`
- `expanded_in_metadata 16`
- `expanded_in_android_registry 16`
- `validators_unique 16`
