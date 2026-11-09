# Pandas SQL 作业：经验总结与策略

本文件不属于提交内容。

## 一、历次成绩和老师的评语

| 作业 | 结果 | 关键评语 |
|---|---|---|
| Web Scraping（真学生） | 正面 | 简单、可读、用 notebook 注释格式 |
| Tkinter | 7/10 | 注释只复述代码，没解释为什么改 |
| Streaming 初交 | 15/20 | 没有和 notebook 的对应关系 |
| Streaming 重交 | 被判 85% AI | 编造引用、教程口吻、过度验证、架构超出范围 |
| SQLite | 22.8/30 | Dunders 3/5、Notebook 6/10、Comments 5/10、Effective Coding 4/5 |
| **Midterm** | **46/50，没提 AI** | Dunders 5/5、Notebook 9/10（有些联系太宽泛）、Comments 7/10（**注释太多，解释了基础代码**） |

## 二、Midterm 证明有效、这次继续用的

1. 每个类都对应一段**真实的、结构上真的照着改**的课堂代码，引用逐条对照原文核实。
2. 改编处用 kept / changed / removed（老师 Example Assignment 的格式）。
3. 私有 `__` 属性 + `@property`；dunder 要在程序里真的被调用。
4. 不验证题目说不用验证的东西；没有测试文件、README、docstring、类型注解。
5. 实际数据有坑就写真实的原因（这次的坑都已经用 pandas 2.3 和 3.1 实测过，见第四节）。

## 三、这次要改进的（来自 Midterm 的 4 分扣分）

1. **注释减量**：Midterm 是 97 行注释 / 123 行代码（0.79）。这次目标约 0.3。题目最后一句也是 "Comment your code where the purpose or reasoning may not be obvious"。
   - 只写：改编记录（每个类一段）+ 不明显的原因（数据的坑、为什么这样设计）。
   - 不写：这行代码在做什么。
2. **引用只留直接的**：只引用 Pandas.ipynb（read_csv、to_sql、read_sql_query、display_dataframe）和自己 SQLite 作业的 4 个类（老师课上说这次就是 "a redo of the previous assignment using Pandas"），外加一处 BinaryPipes `choose_file()` 的 `filedialog`。不再引用颜色、字符类这种宽泛的联系。

## 四、实测发现的数据问题（都写进代码注释，因为是"不明显的原因"）

| 问题 | 实测结果 | 处理 |
|---|---|---|
| Temperature.csv 开头 3 行 `#` | 直接 `pd.read_csv()` 报 `ParserError` | 先数出开头的 `#` 行，用 `skiprows` 跳过 |
| 不能用 `comment="#"` | 会把 CO2.csv 的 `#days` 列吃掉 | 同上 |
| Presidents.csv 值后面有空格（"Federalist "） | 不去空格时 `WHERE Party = 'Federalist'` 返回 0 行 | 对文字列 `.str.strip()` |
| 列名有空格、括号（"Home State"、"Distance(AU)"） | SQL 里每次都要加引号 | 沿用 SQLite 作业的 `clean_name()` |
| 老师示例 `WHERE State = 'Ohio'` | Presidents.csv 没有 State 列，是 `Home State` | 清理后 `Home_State = 'Ohio'` 返回 7 位总统 |
| `read_sql_query("DROP TABLE t")` | 先删掉了表，然后才报错 | Viewer 只允许 SELECT |
| SQLite 往返 | 5 个文件写入再读回都和原 DataFrame `equals()` | 用它验证"表里的数据正确" |

## 五、设计（5 个类，main 只有 3 行）

| 类 | 改编自 | 职责 |
|---|---|---|
| `CSVData` | 自己 SQLite 的 `TableData` + Pandas.ipynb `read_csv()` | 读 CSV、清理、提供列名/行数/类型 |
| `Database` | 自己 SQLite 的 `CommandExecutor` + Pandas.ipynb `to_sql()`/`read_sql_query()` | 写表、执行 SELECT |
| `QueryBuilder` | 自己 SQLite 的 `QueryBuilder` | 生成 SELECT 和 WHERE，不写死列名 |
| `ResultsTable` | Pandas.ipynb `display_dataframe()` | Treeview 显示 DataFrame |
| `PandasSQLViewer` | 自己 SQLite 的 `SQLiteGUI` | GUI 驱动，不含 pandas/SQL 实现 |
