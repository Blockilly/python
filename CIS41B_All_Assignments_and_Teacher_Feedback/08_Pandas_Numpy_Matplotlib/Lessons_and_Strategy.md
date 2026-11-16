# CO2 线性回归作业：经验总结与策略

本文件不属于提交内容。提交的是 `New_Agent_Submission/CO2Regression.py`（加 `CO2.csv`）。

## 一、老师这次明确说的话

- 作业第 6 节："Additional libraries, helper classes, abstractions, validation systems, and extra features are not required and do not automatically earn additional credit." "Unnecessary complexity can make a program harder to understand."
- 作业第 6 节：用了 notebook 里没演示过的写法，要写一句注释说明**为什么需要**和**怎么起作用**。
- 课上原话："I found this in the last assignment, a lot of students put a lot of extra features in. Didn't explain them, and didn't explain why the extra additions were added."

## 二、历次评价逐条对照（重新读了仓库里的评价原文）

| 作业 | 老师的评语要点 | 这次的做法 |
|---|---|---|
| Web Scraping（好评） | 简单、可读、看得出理解了课堂内容 | 71 行代码，3 个类 |
| Tkinter 7/10 | 注释只复述代码，"do not really address why those changes were necessary" | 每条改编记录都写了原因（例如"输出改成 NumPy 数组，因为回归类必须接收数组而不是 DataFrame"） |
| Streaming 15/20 | 要引用 notebook 的具体部分，说明哪些是改编、哪些是自己写的 | 每个类一条改编记录；唯一非 notebook 的写法标了 "Not in the notebooks" |
| Streaming 重交（85% AI） | 编造引用、教程口吻、过度验证、超出范围的架构、每个类都有 repr 和严格验证 | 引用全部对照原文核实；没有教程口吻；全程序 1 处检查；没有协调类 |
| SQLite 22.8/30 | Notebook 6/10：扩展成框架而不是贴近改编小模式；Dunders 3/5 | 回归公式和画图代码与 notebook/题目几乎逐行对应；`__len__` 在 `main` 里真的被调用 |
| Midterm 46/50 | Notebook 9/10：有些联系太宽泛；Comments 7/10：注释太多，解释基础代码行为 | 每个类只引用一个主要来源；删掉所有解释实现细节的注释 |
| Pandas SQL 16/20 | 设计偏复杂；清理和验证超出要求；改了原始列名；注释和实现细节仍偏多 | 3 个类对应题目的 3 项职责；不改列名；只处理题目写明的 missing/unusable data |

## 三、设计

| 类 | 库 | 改编自（都已对照原文核实） | 主要改动和原因 |
|---|---|---|---|
| `CO2Data` | pandas | Dataframes.py 的 `PandasDataFrameDashboard` | 来源改成 `pd.read_csv()`；输出改成 NumPy 数组，因为回归类必须接收数组；删掉统计方法，计算归回归类 |
| `LinearRegression` | NumPy | Numpy.ipynb 的 `class_trend()` | 保留"返回 slope, intercept"；`np.polyfit()`（题目禁止）换成题目给的公式；x 是日期而不是 `np.arange()` |
| `CO2Plot` | Matplotlib | Data Visualization.ipynb 的 practice plot 单元格 | 保留 `plt.subplots()`、标题、轴标签、`plt.show()`；加 `ax.scatter()`、`ax.plot()`、`ax.legend()` |

唯一一个 notebook 里没有的写法是 `read_csv(na_values=...)`，注释里按题目要求写了 Why 和 How。

## 四、数据事实（都实测过）

- `average` 列有 5 个 `-99.99`（1964 年 2–4 月、1975 年 12 月、1984 年 4 月），表示当月没有测量值。
- 不处理时斜率是 1.76；去掉后是 1.58。所以必须处理。
- 选 `average` 而不是 `interpolated`：题目和 notebook 都说 "measured / original observations"，`interpolated` 在这 5 个月里是估计值。两种选法结果很接近（1.5797 和 1.5780）。
- 散点和回归线默认都是同一种蓝色，所以回归线要指定颜色。

## 五、验证结果（pandas 2.3 和 3.1 都跑过）

- 726 个观测值；斜率 1.5797 ppm/年，截距 -2787.43；和 `np.polyfit` 的结果相差 10⁻¹² 量级（`polyfit` 只用于核对，提交的代码里没有）。另用 4 组能心算的数据核对过。
- `x`、`y`、`predicted` 都是 726 个元素的 NumPy 数组；图上的散点和回归线用的就是这三个数组；标题、轴标签、图例齐全；在真实的 Matplotlib 窗口里跑过。
- 9 种坏数据情况都只输出一句清楚的提示，没有崩溃也没有警告：缺文件、空文件、只有表头、缺列、只有一行、全是 -99.99、x 全相同、有空格子、行数变少。
- 代码里没有循环，没有 `polyfit`/`sklearn`；`main` 不直接碰 pandas、NumPy、Matplotlib。
- 注释里的 9 条引用全部在仓库文件里核对到原文。

## 六、第二遍复查改了什么（重读全部评价之后）

注释密度对比：

| 作业 | 注释行 / 代码行 | Comments 得分 |
|---|---|---|
| Midterm | 0.79 | 7/10 |
| Pandas SQL | 0.27 | 8/10 |
| 这次第一版 | 0.38 | — |
| 这次定稿 | 0.27 | — |

第一版只看了绝对行数（27 对 66），忽略了程序很短，比例其实比上次还高。改动：

1. **删掉解释实现细节的零散注释**（检查条件、点的大小和颜色、`except` 的说明）。文件开头的说明也缩成一行标题。现在 19 行注释里，除了标题全部是改编记录和题目要求的 Why/How。
2. **每条改编记录补上原因**（Tkinter 那次扣分的原因）。
3. **去掉 `to_numpy(dtype=float)`**，改回题目原文的 `to_numpy()`。这是自己测试时加的额外防护，违反了"只做题目明确要求的"这条教训。
4. **引用精简到每个类一个主要来源**，去掉 `z_scores()` 和 `np.array(dtype=float)` 两条旁支引用（Midterm 的 "broader than necessary"）。

## 七、还不确定的地方

1. 老师心里的"合适的 CO2 列"可能是 `interpolated`。我们选了 `average` 并写明了理由。
2. 回归类里那一处检查（少于 2 个点或 x 全相同）可能被看成多余，也可能被看成健壮性。
3. 数值列里混进文字时程序会报错退出，没有处理。CO2.csv 里没有这种数据，题目也没要求。
4. 注释比例和上次一样（都是 0.27），但这次全部是改编记录。如果老师仍然觉得多，下一步只能缩短改编记录本身。
