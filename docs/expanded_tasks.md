# Expanded Tasks

本文档说明本仓库新增并保留的 76 条 AndroidWorld expanded tasks。这批任务覆盖原生 AndroidWorld 分布中的更多应用：

- Markor：13 条文件系统类笔记任务
- Simple Calendar Pro：13 条 SQLite 日历事件任务
- Contacts：7 条联系人任务
- Simple SMS Messenger：7 条短信任务
- Pro Expense：8 条 SQLite 记账任务
- Broccoli app：8 条 SQLite 菜谱任务
- System/Settings/Clipper/OpenApp：6 条系统设置、剪贴板和打开 app 任务
- Files：2 条文件管理任务
- Clock：3 条计时器和秒表任务
- Camera：2 条拍照和录像任务
- Audio Recorder：2 条录音任务
- VLC：2 条播放列表任务
- Retro Music：2 条音乐播放列表/队列任务
- Simple Gallery Pro：1 条图片复制任务

这些任务的统一注册入口在 `android_world/task_evals/single/expanded_tasks.py`。`registry.py` 通过 `*expanded_tasks.ALL_TASKS` 将它们加入 Android task registry；`task_metadata.json` 中同步保留全部 76 条 expanded tasks 的 metadata。

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

## 任务总表

下表按 app 汇总全部 76 条 expanded tasks。

| App | Task | Template | 目标行为 | 初始化数据 | 验证方式 |
| --- | --- | --- | --- | --- | --- |
| Markor | `MarkorAddHeaderAndRenameNote` | `Edit {original_name} in Markor so it starts with "{header}", then a blank line, then the original note text. Save the result as {new_name}.` | 在已有 note 顶部加入 header、空行和原文，并重命名 | 预置目标 note 和干扰 note | 检查旧文件不存在、新文件内容精确等于 header、空行、原文 |
| Markor | `MarkorAppendToNote` | `Open the Markor note {file_name} and add this text as a new line at the bottom: "{appended_text}".` | 给已有 note 末尾追加一行文本 | 预置目标 note 和干扰 note | 检查文件内容为原内容、换行、追加文本 |
| Markor | `MarkorCopyNote` | `In Markor, copy the contents of {source_name} into a new note named {new_name}. Leave the original note unchanged.` | 将已有 note 内容复制到新 note，原文件保留 | 预置 source note 和干扰 note | 检查 source 与 new note 均存在且内容一致 |
| Markor | `MarkorCreateChecklistNote` | `Create a checklist note in Markor named {file_name} with these items: {items}. Each checklist item should be unchecked.` | 创建 unchecked checklist note | 无需预置目标文件 | 检查新文件内容为 `- [ ] item` 格式的 checklist |
| Markor | `MarkorCreateClipboardNote` | `Create {file_name} in Markor and paste the current clipboard text as its contents.` | 用剪贴板内容创建新 note | 设置 clipboard 为目标文本 | 检查新 note 存在且内容等于剪贴板文本 |
| Markor | `MarkorCreateNoteInFolder` | `In Markor, create a note named {file_name} inside the {folder_name} folder with the following text: {text}` | 在指定 Markor 子文件夹中创建 note | 创建目标目录，并生成干扰 note | 检查目标目录下指定文件存在且内容等于目标文本 |
| Markor | `MarkorDeleteNoteInFolder` | `In Markor, delete the note {file_name} from the {subfolder} folder.` | 删除指定子文件夹中的 note | 预置待删除文件和干扰文件 | 使用文件删除验证逻辑确认目标文件不存在 |
| Markor | `MarkorMergeThreeNotes` | `Make a new Markor note called {new_file_name} by combining {file1_name}, {file2_name}, and {file3_name} in that order, with an empty line separating each note.` | 按顺序合并三条 note 到一个新 note，中间保留空行 | 预置三条源 note | 检查新 note 内容为三段源文本按顺序合并，且段落之间有空行 |
| Markor | `MarkorMoveNoteBetweenFolders` | `In Markor, file {file_name} under {destination_folder}; it should no longer remain in {source_folder}.` | 将指定 note 从源文件夹移动到目标文件夹 | 在源文件夹预置目标 note 和干扰 note，并创建目标文件夹 | 检查源文件夹中目标 note 不存在、目标文件夹中目标 note 存在 |
| Markor | `MarkorPrependDateToNote` | `Open the Markor note {file_name} and add {date} as the first line of the note.` | 在已有 note 第一行插入日期 | 预置目标 note 和干扰 note | 检查文件内容为日期、换行、原内容 |
| Markor | `MarkorRenameNote` | `Rename the Markor note {original_name} to {new_name} without changing its contents.` | 重命名 note 且内容不变 | 预置 original note 和干扰 note | 检查旧文件不存在、新文件存在且内容不变 |
| Markor | `MarkorReplaceTextInNote` | `In the Markor note {file_name}, replace the text "{old_text}" with "{new_text}".` | 替换已有 note 中的指定文本 | 预置包含旧文本的目标 note 和干扰 note | 检查文件内容精确等于替换后的文本 |
| Markor | `MarkorRewriteAndRenameNote` | `In Markor, turn {original_name} into {new_name} and make the note contain only this text: "{updated_content}".` | 清空并改写已有 note，同时重命名 | 预置目标 note 和干扰 note | 检查旧文件不存在、新文件存在且内容等于 `updated_content` |
| Simple Calendar Pro | `SimpleCalendarAddEventInTwoWeeks` | `Add '{event_title}' to Simple Calendar Pro for the date two weeks from today. It starts at {hour}h, runs {duration_mins} mins, and has description '{event_description}'.` | 为当前日期两周后创建事件 | 插入随机干扰事件 | 检查新增事件日期为两周后，且标题、描述、开始时间和时长正确 |
| Simple Calendar Pro | `SimpleCalendarAddEventNextWeek` | `In Simple Calendar Pro, create a calendar event for next {day_of_week} at {hour}h with the title '{event_title}' and the description '{event_description}'. The event should last for {duration_mins} mins.` | 按“next weekday”创建下周事件 | 插入干扰事件 | 检查新增事件落在下周指定 weekday |
| Simple Calendar Pro | `SimpleCalendarAddEventWithLocation` | `In Simple Calendar Pro, create a calendar event on {year}-{month}-{day} at {hour}h located at '{location}' with the title '{event_title}' and the description '{event_description}'. The event should last for {duration_mins} mins.` | 创建带 location 的单个日历事件 | 插入干扰事件 | 检查新增事件的时间、标题、描述、location 和时长 |
| Simple Calendar Pro | `SimpleCalendarAddLongEvent` | `In Simple Calendar Pro, create a long calendar event on {year}-{month}-{day} at {hour}h with the title '{event_title}' and the description '{event_description}'. The event should last for {duration_mins} mins.` | 创建 90/120/180 分钟的长事件 | 插入干扰事件 | 检查新增事件的 start/end 时间和内容字段 |
| Simple Calendar Pro | `SimpleCalendarAddRepeatingWeeklyEvent` | `Set up '{event_title}' in Simple Calendar Pro starting {year}-{month}-{day} at {hour}h as a {repeat_rule} repeating event. Each occurrence lasts {duration_mins} mins and uses description '{event_description}'.` | 创建 daily 或 weekly recurring event | 插入随机干扰事件 | 检查新增事件内容字段以及 `repeat_interval`、`repeat_rule` 正确 |
| Simple Calendar Pro | `SimpleCalendarAddTomorrowEvent` | `For tomorrow in Simple Calendar Pro, put '{event_title}' on the calendar at {hour}h for {duration_mins} mins. Set the description to '{event_description}'.` | 为明天创建一条事件 | 插入随机干扰事件 | 检查新增事件日期为明天，且标题、描述、开始时间和时长正确 |
| Simple Calendar Pro | `SimpleCalendarAddTwoEventsDifferentDays` | `In Simple Calendar Pro, create two calendar events: one on {year}-{month}-{day1} at {hour1}h titled '{event_title1}' with description '{event_description1}' lasting {duration_mins1} mins, and one on {year}-{month}-{day2} at {hour2}h titled '{event_title2}' with description '{event_description2}' lasting {duration_mins2} mins.` | 在两个不同日期创建两个事件 | 插入避开目标日期的干扰事件 | 检查两个目标事件都被新增，且日期不同 |
| Simple Calendar Pro | `SimpleCalendarAddTwoEventsSameDay` | `In Simple Calendar Pro, create two calendar events on {year}-{month}-{day}: first at {hour1}h titled '{event_title1}' with description '{event_description1}' lasting {duration_mins1} mins, and second at {hour2}h titled '{event_title2}' with description '{event_description2}' lasting {duration_mins2} mins.` | 在同一天创建两个不同时间的事件 | 插入避开目标日的干扰事件 | 检查两个目标事件都被新增，且日期相同、时间不同 |
| Simple Calendar Pro | `SimpleCalendarDeleteEventByTitle` | `In Simple Calendar Pro, delete the calendar event titled '{event_title}'.` | 只根据标题删除一个事件 | 预置目标事件和不同标题的干扰事件 | 检查目标事件被删除，其他事件保留 |
| Simple Calendar Pro | `SimpleCalendarDeleteEventByTitleAndDate` | `In Simple Calendar Pro, delete the calendar event titled '{event_title}' on {year}-{month}-{day}.` | 根据标题和日期删除一个事件 | 预置目标事件和干扰事件 | 检查匹配标题与日期的事件被删除 |
| Simple Calendar Pro | `SimpleCalendarDeleteEventsThisWeekday` | `For this {day_of_week}, remove the whole day's Simple Calendar Pro schedule.` | 删除本周指定 weekday 的所有事件 | 预置目标 weekday 事件和其他日期干扰事件 | 检查目标 weekday 事件全部删除，其他日期事件保留 |
| Simple Calendar Pro | `SimpleCalendarDeleteSingleTimedEvent` | `Find the {year}-{month}-{day} {hour}h Simple Calendar Pro entry named '{event_title}' and delete it.` | 删除指定日期、时间和标题的单个事件 | 预置目标事件和时间/标题不同的干扰事件 | 检查目标事件被删除，干扰事件保留 |
| Simple Calendar Pro | `SimpleCalendarDeleteTomorrowEvents` | `In Simple Calendar Pro, delete all calendar events for tomorrow.` | 删除明天的所有事件 | 预置明天的目标事件和非明天干扰事件 | 检查明天目标事件被删除，其他日期事件保留 |
| Contacts | `ContactsAddClinicCallbackFromSms` | `In Contacts, add the clinic callback contact described in the latest text message from {sender_number}.` | 从指定号码最新短信中提取 clinic callback 联系人并创建联系人 | 注入包含目标姓名和号码的短信 | 使用 contacts validator 检查目标联系人存在 |
| Contacts | `ContactsAddClipboardContact` | `In Contacts, create a new contact using the name and phone number currently in the clipboard.` | 根据剪贴板中的姓名和号码创建联系人 | 设置 clipboard 为目标联系人详情 | 使用 contacts validator 检查目标联系人存在 |
| Contacts | `ContactsAddContractorFromClipboard` | `In Contacts, create a new contact for the contractor listed in the clipboard.` | 从剪贴板中的 contractor 描述里提取姓名和号码并创建联系人 | 设置 clipboard 为 `Contractor contact - name: ...; phone: ...` 格式文本 | 使用 contacts validator 检查目标联系人存在 |
| Contacts | `ContactsAddEmergencyContact` | `In Contacts, add the emergency contact described in the latest text message from {sender_number}.` | 从最新短信中提取 emergency contact 并创建联系人 | 注入 emergency contact 短信 | 检查目标联系人存在 |
| Contacts | `ContactsAddFromIncomingSms` | `In Contacts, add the person and phone number described in the latest text message from {sender_number}.` | 从最新短信正文中提取姓名和号码并创建联系人 | 注入包含目标联系人信息的短信 | 检查目标联系人存在 |
| Contacts | `ContactsAddFromMarkorNote` | `In Markor, open contacts_to_add.txt and add the contact listed for {role} to Contacts.` | 从 Markor 文件中按 role 找到联系人并添加 | 创建 `contacts_to_add.txt`，包含目标和干扰联系人 | 检查目标联系人存在 |
| Contacts | `ContactsAddVendorFromMarkorNote` | `In Markor, open contacts_to_add.txt and add the contact listed for {role} to Contacts.` | 从 Markor note 中按 vendor role 找到联系人并添加 | 创建 `contacts_to_add.txt`，混入目标 role 和干扰联系人 | 使用 contacts validator 检查目标联系人存在 |
| Simple SMS Messenger | `SimpleSmsForwardAppointmentTime` | `In Simple SMS Messenger, forward the appointment time from {sender_name} to {recipient_name}. Send only the time.` | 从收到的短信中提取预约时间并只转发 time | 预置发送方和收件联系人，并注入包含预约时间的短信 | 检查 sent SMS 发送给目标号码且正文只等于 time |
| Simple SMS Messenger | `SimpleSmsForwardDoorCode` | `In Simple SMS Messenger, forward the door code from {sender_name} to {recipient_name}. Send only the code.` | 从收到的短信中提取门禁码并只转发 code | 预置发送方和收件联系人，并注入包含门禁码的短信 | 检查 sent SMS 发送给目标号码且正文只等于 code |
| Simple SMS Messenger | `SimpleSmsForwardSecurityCode` | `In Simple SMS Messenger, forward the security code from {sender_name} to {recipient_name}. Send only the code.` | 从收到的短信中提取验证码并转发给联系人 | 预置收件联系人和验证码短信 | 检查只发送验证码到目标号码 |
| Simple SMS Messenger | `SimpleSmsForwardTrackingNumber` | `In Simple SMS Messenger, forward the package tracking number from {sender_name} to {recipient_name}. Send only the tracking number.` | 从包裹短信中提取 tracking number 并转发 | 注入 tracking 短信并预置联系人 | 检查只发送 tracking number 到目标号码 |
| Simple SMS Messenger | `SimpleSmsSendNoteSnippetToSavedContact` | `In Simple SMS Messenger, send only the snippet from the clipboard to the saved contact {name}.` | 从剪贴板文本中提取 snippet 内容并发给联系人 | 预置联系人，并设置 clipboard 为 `Snippet to send: ...` | 检查 sent SMS 发送给目标号码且正文只等于 snippet |
| Simple SMS Messenger | `SimpleSmsSendToSavedContact` | `In Simple SMS Messenger, send {message} to the saved contact {name}.` | 给已保存联系人发指定消息 | 预置目标联系人 | 检查 sent SMS 的号码和正文 |
| Simple SMS Messenger | `SimpleSmsTextClipboardToSavedContact` | `In Simple SMS Messenger, send the clipboard content to the saved contact {name}.` | 将 clipboard 内容发给已保存联系人 | 预置联系人并设置 clipboard | 检查 sent SMS 正文等于 clipboard 内容 |
| Pro Expense | `ExpenseAddFoodPurchase` | `In Pro Expense, add this {category} expense: name {expense_name}, amount {amount}, note {note}.` | 新增单条 Food 类支出 | 插入干扰支出 | 检查新增支出的 name、amount、category、note |
| Pro Expense | `ExpenseAddHighValueExpensesFromMarkor` | `In Markor, open expense_candidates.txt. Add only the expenses with amount at least {min_amount} into Pro Expense.` | 从 Markor 文件只录入金额达到阈值的支出 | 创建 `expense_candidates.txt`，混入低金额干扰项 | 检查高金额目标支出新增 |
| Pro Expense | `ExpenseAddTransportationPurchase` | `In Pro Expense, record this {category} expense with name {expense_name}, amount {amount}, and note {note}.` | 新增单条 Transportation 类支出 | 插入干扰支出 | 检查新增支出的 name、amount、category、note |
| Pro Expense | `ExpenseAddTwoEducationExpenses` | `In Pro Expense, add these two Education expenses:\n{expense_summary}` | 新增两条 Education 类支出 | 插入干扰支出 | 检查两条目标支出都新增 |
| Pro Expense | `ExpenseAddTwoHealthCareExpenses` | `In Pro Expense, add these two Health Care expenses:\n{expense_summary}` | 新增两条 Health Care 类支出 | 插入干扰支出 | 检查两条目标支出都新增 |
| Pro Expense | `ExpenseDeleteEntertainmentExpenses` | `In Pro Expense, delete all {category} expenses and leave the other expenses unchanged.` | 删除所有 Entertainment 类目标支出 | 预置目标支出和其他分类干扰支出 | 检查目标删除且干扰保留 |
| Pro Expense | `ExpenseDeleteHousingExpenses` | `In Pro Expense, delete all {category} expenses and keep every other category unchanged.` | 删除所有 Housing 类目标支出 | 预置 Housing 目标支出和其他分类干扰支出 | 检查目标删除且干扰保留 |
| Pro Expense | `ExpenseDeleteTransportationExpenses` | `In Pro Expense, remove every {category} expense while leaving the rest of the expense list alone.` | 删除所有 Transportation 类目标支出 | 预置 Transportation 目标支出和其他分类干扰支出 | 检查目标删除且干扰保留 |
| Broccoli app | `RecipeAddRecipesFromMarkorWithChicken` | `In Markor, open recipe_candidates.txt. Add only the recipes whose directions mention {ingredient} into Broccoli app.` | 从 Markor 文件只录入 directions 包含 chicken 的菜谱 | 创建 `recipe_candidates.txt`，混入不含 chicken 的干扰菜谱 | 检查目标菜谱新增 |
| Broccoli app | `RecipeAddRecipesFromMarkorWithIngredient` | `In Markor, open recipe_candidates.txt. Add only the recipes whose directions mention {ingredient} into Broccoli app.` | 从 Markor 文件只录入 directions 包含指定 ingredient 的菜谱 | 创建 `recipe_candidates.txt`，混入不含该 ingredient 的干扰项 | 检查目标菜谱新增 |
| Broccoli app | `RecipeAddThirtyMinuteRecipe` | `In Broccoli app, add the recipe {recipe_title}. Description: {description}. Servings: {servings}. Preparation time: {prep_time}. Ingredients: {ingredients}. Directions: {directions}.` | 新增一条准备时间为 30 mins 的菜谱 | 插入干扰菜谱 | 检查 title、description、servings、preparationTime、ingredients、directions |
| Broccoli app | `RecipeAddTwentyMinuteRecipe` | `In Broccoli app, add the recipe {recipe_title}. Description: {description}. Servings: {servings}. Preparation time: {prep_time}. Ingredients: {ingredients}. Directions: {directions}.` | 新增一条准备时间为 20 mins 的菜谱 | 插入干扰菜谱 | 检查 title、description、servings、preparationTime、ingredients、directions |
| Broccoli app | `RecipeAddTwoFamilyServingRecipes` | `In Broccoli app, add these two recipes that each make {servings}:\n{recipe_summary}` | 新增两条 6 servings 菜谱 | 插入干扰菜谱 | 检查两条目标菜谱都新增 |
| Broccoli app | `RecipeAddTwoSmallServingRecipes` | `In Broccoli app, add these two recipes that each make {servings}:\n{recipe_summary}` | 新增两条 2 servings 菜谱 | 插入干扰菜谱 | 检查两条目标菜谱都新增 |
| Broccoli app | `RecipeDeleteThirtyMinuteRecipes` | `In Broccoli app, delete every recipe with preparation time {prep_time}.` | 删除准备时间为 30 mins 的菜谱 | 预置目标和非 30 mins 干扰菜谱 | 检查目标删除且干扰保留 |
| Broccoli app | `RecipeDeleteTwentyMinuteRecipes` | `In Broccoli app, delete every recipe with preparation time {prep_time}.` | 删除准备时间为 20 mins 的菜谱 | 预置目标菜谱和非 20 mins 干扰菜谱 | 检查目标删除且干扰保留 |
| System / Settings / Clipboard / OpenApp | `OpenNamedSystemApp` | `Bring up the {app_name} app, accepting any required permission prompts.` | 打开指定系统 app | 随机选择 camera/clock/contacts/settings/dialer 等 app | 检查当前 activity 的 package name 是否匹配目标 app |
| System / Settings / Clipboard / OpenApp | `SystemCopyReservationCodeToClipboard` | `Put the following reservation text on the clipboard, character for character: {clipboard_content}` | 将指定文本复制到剪贴板 | 初始化时清空剪贴板 | 检查剪贴板内容与目标文本 fuzzy match |
| System / Settings / Clipboard / OpenApp | `SystemDisableBluetoothFromSettings` | `Go into Settings and switch off Bluetooth.` | 在 Settings 中关闭 Bluetooth | 初始化时先打开 Bluetooth | 检查 `settings get global bluetooth_on` 为关闭状态 |
| System / Settings / Clipboard / OpenApp | `SystemEnableWifiFromSettings` | `Go into Settings and switch on WiFi.` | 在 Settings 中打开 WiFi | 初始化时先关闭 WiFi | 检查 `settings get global wifi_on` 为开启状态 |
| System / Settings / Clipboard / OpenApp | `SystemTurnBrightnessAllTheWayDown` | `Use Settings to drag screen brightness down to its minimum level.` | 将屏幕亮度调到最低 | 初始化时先把亮度设为最高 | 检查 `settings get system screen_brightness` 为最低值 |
| System / Settings / Clipboard / OpenApp | `SystemTurnBrightnessAllTheWayUp` | `Use Settings to push screen brightness up to its maximum level.` | 将屏幕亮度调到最高 | 初始化时先把亮度设为最低 | 检查 `settings get system screen_brightness` 为最高值 |
| Files | `FilesDeleteDownloadedFile` | `In the Files app, remove {file_name} from the Android storage folder {subfolder}.` | 删除指定子目录中的文件 | 在目标子目录创建目标文件和干扰文件 | 检查目标文件不存在 |
| Files | `FilesMoveMediaFileToAnotherFolder` | `With the Files app, transfer {file_name} from {source_folder} into {destination_folder} on Android storage.` | 在 Android 文件管理器中移动文件 | 在源文件夹创建目标文件和干扰文件，并创建目标文件夹 | 检查源文件夹目标文件不存在、目标文件夹目标文件存在 |
| Clock | `ClockCreateFocusTimer` | `Set up, but do not run, a Clock countdown reading {hours}:{minutes}:{seconds}.` | 创建但不启动指定时长 timer | 清空 Clock app state | 检查 Clock UI 中存在指定 timer 文本或 content description |
| Clock | `ClockLeaveStopwatchPaused` | `Show the stopwatch in Clock in its paused state.` | 保持秒表暂停 | 清空 Clock app state | 检查 Stopwatch 页面出现 Start 控件且处于暂停状态 |
| Clock | `ClockStartStopwatch` | `Launch Clock and get the stopwatch running.` | 启动秒表 | 清空 Clock app state，使秒表从暂停状态开始 | 检查 Stopwatch 页面出现 Pause 和 Lap 控件 |
| Camera | `CameraCaptureReferencePhoto` | `Capture a single still image with the Camera app.` | 拍摄一张照片 | 清空照片和视频目录，记录初始照片列表 | 检查照片目录新增一个文件 |
| Camera | `CameraRecordShortVideo` | `Capture one video clip with the Camera app.` | 录制一个视频 | 清空照片和视频目录，记录初始视频列表 | 检查视频目录新增一个文件 |
| Audio Recorder | `AudioRecorderRecordNamedBriefing` | `Make a new recording in Audio Recorder and give the saved clip the name {file_name}.` | 录制音频并保存为指定文件名 | 清空 Audio Recorder 数据目录 | 检查录音目录中存在 `{file_name}.m4a` |
| Audio Recorder | `AudioRecorderRecordVoiceMemo` | `Use Audio Recorder to make and keep one new recording.` | 录制并保存一段音频 | 记录录音目录初始文件列表 | 检查录音目录新增或变化一个非空文件 |
| VLC | `VlcCreateReviewPlaylist` | `Build a VLC playlist titled {playlist_name}. Add the video files in this exact sequence: {files}.` | 创建一个 VLC 播放列表并按顺序加入视频 | 写入目标视频和干扰视频，清空 VLC playlist DB | 查询 VLC SQLite playlist/media join 结果，检查 playlist 名称和视频顺序 |
| VLC | `VlcCreateTwoReviewPlaylists` | `In VLC, make two ordered playlists. The first is {playlist_name1} with {files1}; the second is {playlist_name2} with {files2}.` | 创建两个 VLC 播放列表 | 写入两组目标视频和干扰视频，清空 VLC playlist DB | 分别检查两个 playlist 名称和视频顺序 |
| Retro Music | `RetroMusicAddSongsToQueue` | `Queue up these Retro Music tracks in the listed order: {files}.` | 将指定歌曲按顺序加入播放队列 | 写入目标 MP3 和干扰 MP3，并触发媒体扫描 | 查询 playback state DB 的 `playing_queue`，检查队列歌曲顺序 |
| Retro Music | `RetroMusicCreateCommutePlaylist` | `Create a Retro Music playlist called {playlist_name} and place these tracks in order: {files}.` | 创建 Retro Music 播放列表 | 写入目标 MP3 和干扰 MP3，清空 playlist DB 并触发媒体扫描 | 查询 Retro Music playlist DB，检查 playlist 名称和歌曲顺序 |
| Simple Gallery Pro | `SimpleGalleryCopyReceiptToDownloads` | `Using Simple Gallery Pro, duplicate the DCIM image {file_name} into the Download folder.` | 将 DCIM 中的 receipt 图片复制到 Download | 生成 receipt 图片并写入 DCIM | 检查 Download 目录中存在同名文件 |

## Metadata

这 76 条任务的 metadata 字段由 `expanded_tasks.py` 中的 `_SPECS` 维护，并同步写入 `android_world/task_metadata.json`。当前新增任务数量应满足：

- `len(expanded_tasks.ALL_TASKS) == 76`
- `task_metadata.json` 总数为原始 116 条加新增 76 条，即 192 条
- 新增 76 条 task name 在 metadata 中各出现一次

如果以后修改 expanded task 名称、template、difficulty、tags 或 optimal steps，需要同时确认 `task_metadata.json` 与 `expanded_tasks.py` 保持一致。

## Registry

`registry.py` 中通过以下方式注册 expanded tasks：

```python
*expanded_tasks.ALL_TASKS,
```

这意味着 registry 不直接枚举 76 个具体类名，而是由 `expanded_tasks.py` 统一维护任务集合。新增或移除 expanded task 时，优先修改 `_SPECS`，再同步 metadata 和测试。

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

- `expanded_tasks 76`
- `metadata_entries 192`
- `metadata_duplicates []`
- `expanded_in_metadata 76`
- `expanded_in_android_registry 76`
- `validators_unique 76`
