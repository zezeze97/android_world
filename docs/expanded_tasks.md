# Expanded Tasks

本文档说明本仓库新增并保留的 32 条 AndroidWorld expanded tasks。这批任务覆盖六个应用：

- Markor：8 条文件系统类笔记任务
- Simple Calendar Pro：8 条 SQLite 日历事件任务
- Contacts：4 条联系人任务
- Simple SMS Messenger：4 条短信任务
- Pro Expense：4 条 SQLite 记账任务
- Broccoli app：4 条 SQLite 菜谱任务

这些任务的统一注册入口在 `android_world/task_evals/single/expanded_tasks.py`。`registry.py` 通过 `*expanded_tasks.ALL_TASKS` 将它们加入 Android task registry；`task_metadata.json` 中也只保留这 32 条 expanded tasks 的 metadata。

## 文件位置

- Expanded task 入口：`android_world/task_evals/single/expanded_tasks.py`
- Markor 任务实现：`android_world/task_evals/single/markor.py`
- Simple Calendar Pro 任务实现：`android_world/task_evals/single/calendar/calendar.py`
- Markor 测试：`android_world/task_evals/single/markor_test.py`
- Calendar 测试：`android_world/task_evals/single/calendar/calendar_test.py`
- Contacts/SMS/Expense/Recipe 实现：`android_world/task_evals/single/{contacts,sms,expense,recipe}.py`
- Contacts/SMS/Expense/Recipe 测试：`android_world/task_evals/single/{contacts,sms,expense,recipe}_test.py`
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

## Contacts Tasks

Contacts 任务验证系统联系人数据库中的目标联系人是否被创建，扩展重点是从其他信息源抽取联系人，而不是简单改写原始“新增联系人”指令。

| Task | Template | 目标行为 | 初始化数据 | 验证方式 |
| --- | --- | --- | --- | --- |
| `ContactsAddClipboardContact` | `In Contacts, create a new contact using the name and phone number currently in the clipboard.` | 根据剪贴板中的姓名和号码创建联系人 | 设置 clipboard 为目标联系人详情 | 使用 contacts validator 检查目标联系人存在 |
| `ContactsAddEmergencyContact` | `In Contacts, add the emergency contact described in the latest text message from {sender_number}.` | 从最新短信中提取 emergency contact 并创建联系人 | 注入 emergency contact 短信 | 检查目标联系人存在 |
| `ContactsAddFromIncomingSms` | `In Contacts, add the person and phone number described in the latest text message from {sender_number}.` | 从最新短信正文中提取姓名和号码并创建联系人 | 注入包含目标联系人信息的短信 | 检查目标联系人存在 |
| `ContactsAddFromMarkorNote` | `In Markor, open contacts_to_add.txt and add the contact listed for {role} to Contacts.` | 从 Markor 文件中按 role 找到联系人并添加 | 创建 `contacts_to_add.txt`，包含目标和干扰联系人 | 检查目标联系人存在 |

## Simple SMS Messenger Tasks

SMS 任务仍通过 Android SMS content provider 验证真实 sent message，新增任务加入 contacts、clipboard 和 received message 上下文，要求 agent 做信息抽取或联系人解析。

| Task | Template | 目标行为 | 初始化数据 | 验证方式 |
| --- | --- | --- | --- | --- |
| `SimpleSmsSendToSavedContact` | `In Simple SMS Messenger, send {message} to the saved contact {name}.` | 给已保存联系人发指定消息 | 预置目标联系人 | 检查 sent SMS 的号码和正文 |
| `SimpleSmsForwardSecurityCode` | `In Simple SMS Messenger, forward the security code from {sender_name} to {recipient_name}. Send only the code.` | 从收到的短信中提取验证码并转发给联系人 | 预置收件联系人和验证码短信 | 检查只发送验证码到目标号码 |
| `SimpleSmsTextClipboardToSavedContact` | `In Simple SMS Messenger, send the clipboard content to the saved contact {name}.` | 将 clipboard 内容发给已保存联系人 | 预置联系人并设置 clipboard | 检查 sent SMS 正文等于 clipboard 内容 |
| `SimpleSmsForwardTrackingNumber` | `In Simple SMS Messenger, forward the package tracking number from {sender_name} to {recipient_name}. Send only the tracking number.` | 从包裹短信中提取 tracking number 并转发 | 注入 tracking 短信并预置联系人 | 检查只发送 tracking number 到目标号码 |

## Pro Expense Tasks

Expense 任务基于 `accounting.db` 的 `expense` 表验证新增或删除记录，覆盖分类、金额阈值和跨 app 文件抽取。

| Task | Template | 目标行为 | 初始化数据 | 验证方式 |
| --- | --- | --- | --- | --- |
| `ExpenseAddFoodPurchase` | `In Pro Expense, add this {category} expense: name {expense_name}, amount {amount}, note {note}.` | 新增单条 Food 类支出 | 插入干扰支出 | 检查新增支出的 name、amount、category、note |
| `ExpenseAddTwoEducationExpenses` | `In Pro Expense, add these two Education expenses:\n{expense_summary}` | 新增两条 Education 类支出 | 插入干扰支出 | 检查两条目标支出都新增 |
| `ExpenseDeleteEntertainmentExpenses` | `In Pro Expense, delete all {category} expenses and leave the other expenses unchanged.` | 删除所有 Entertainment 类目标支出 | 预置目标支出和其他分类干扰支出 | 检查目标删除且干扰保留 |
| `ExpenseAddHighValueExpensesFromMarkor` | `In Markor, open expense_candidates.txt. Add only the expenses with amount at least {min_amount} into Pro Expense.` | 从 Markor 文件只录入金额达到阈值的支出 | 创建 `expense_candidates.txt`，混入低金额干扰项 | 检查高金额目标支出新增 |

## Broccoli Recipe Tasks

Recipe 任务基于 Broccoli app 的 `recipes` 表验证新增或删除记录，覆盖准备时间、份量和跨 app 条件抽取。

| Task | Template | 目标行为 | 初始化数据 | 验证方式 |
| --- | --- | --- | --- | --- |
| `RecipeAddThirtyMinuteRecipe` | `In Broccoli app, add the recipe {recipe_title}. Description: {description}. Servings: {servings}. Preparation time: {prep_time}. Ingredients: {ingredients}. Directions: {directions}.` | 新增一条准备时间为 30 mins 的菜谱 | 插入干扰菜谱 | 检查 title、description、servings、preparationTime、ingredients、directions |
| `RecipeAddTwoFamilyServingRecipes` | `In Broccoli app, add these two recipes that each make {servings}:\n{recipe_summary}` | 新增两条 6 servings 菜谱 | 插入干扰菜谱 | 检查两条目标菜谱都新增 |
| `RecipeDeleteThirtyMinuteRecipes` | `In Broccoli app, delete every recipe with preparation time {prep_time}.` | 删除准备时间为 30 mins 的菜谱 | 预置目标和非 30 mins 干扰菜谱 | 检查目标删除且干扰保留 |
| `RecipeAddRecipesFromMarkorWithIngredient` | `In Markor, open recipe_candidates.txt. Add only the recipes whose directions mention {ingredient} into Broccoli app.` | 从 Markor 文件只录入 directions 包含指定 ingredient 的菜谱 | 创建 `recipe_candidates.txt`，混入不含该 ingredient 的干扰项 | 检查目标菜谱新增 |

## Metadata

这 32 条任务的 metadata 字段由 `expanded_tasks.py` 中的 `_SPECS` 维护，并同步写入 `android_world/task_metadata.json`。当前新增任务数量应满足：

- `len(expanded_tasks.ALL_TASKS) == 32`
- `task_metadata.json` 总数为原始 116 条加新增 32 条，即 148 条
- 新增 32 条 task name 在 metadata 中各出现一次

如果以后修改 expanded task 名称、template、difficulty、tags 或 optimal steps，需要同时确认 `task_metadata.json` 与 `expanded_tasks.py` 保持一致。

## Registry

`registry.py` 中通过以下方式注册 expanded tasks：

```python
*expanded_tasks.ALL_TASKS,
```

这意味着 registry 不直接枚举 32 个具体类名，而是由 `expanded_tasks.py` 统一维护任务集合。新增或移除 expanded task 时，优先修改 `_SPECS`，再同步 metadata 和测试。

## 验证命令

建议在 conda 环境 `android_world` 中执行以下检查：

```bash
PYTHONPATH=/Users/zezeze/python/code/android_world conda run -n android_world python -m py_compile android_world/task_evals/single/expanded_tasks.py android_world/registry.py
PYTHONPATH=/Users/zezeze/python/code/android_world conda run -n android_world python -m json.tool android_world/task_metadata.json
PYTHONPATH=/Users/zezeze/python/code/android_world conda run -n android_world pytest -q android_world/suite_utils_test.py android_world/task_evals/single/contacts_test.py android_world/task_evals/single/sms_test.py android_world/task_evals/single/expense_test.py android_world/task_evals/single/recipe_test.py android_world/task_evals/single/markor_test.py android_world/task_evals/single/calendar/calendar_test.py
```

也可以用下面的脚本快速检查数量和注册状态：

```bash
PYTHONPATH=/Users/zezeze/python/code/android_world conda run -n android_world python -c 'import json; from collections import Counter; from android_world import registry; from android_world.task_evals.single import expanded_tasks; exp=[c.__name__ for c in expanded_tasks.ALL_TASKS]; meta=json.load(open("android_world/task_metadata.json")); meta_names=[x["task_name"] for x in meta]; reg=registry.TaskRegistry().get_registry(registry.TaskRegistry.ANDROID_FAMILY); print("expanded_tasks", len(exp)); print("metadata_entries", len(meta_names)); print("metadata_duplicates", [n for n,c in Counter(meta_names).items() if c>1]); print("expanded_in_metadata", sum(n in set(meta_names) for n in exp)); print("expanded_in_android_registry", sum(n in set(reg) for n in exp)); print("validators_unique", len({c.validate_success for c in expanded_tasks.ALL_TASKS}))'
```

期望结果：

- `expanded_tasks 32`
- `metadata_entries 148`
- `metadata_duplicates []`
- `expanded_in_metadata 32`
- `expanded_in_android_registry 32`
- `validators_unique 32`
