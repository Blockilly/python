# CO2 线性回归作业：经验总结与策略

本文件不属于提交内容。提交的是 `New_Agent_Submission/CO2Regression.py`（加 `CO2.csv`）。

## 一、老师这次明确说的话

- 作业第 6 节："Additional libraries, helper classes, abstractions, validation systems, and extra features are not required and do not automatically earn additional credit." "Unnecessary complexity can make a program harder to understand."
- 作业第 6 节：用了 notebook 里没演示过的写法，要写一句注释说明**为什么需要**和**怎么起作用**。
- 课上原话："I found this in the last assignment, a lot of students put a lot of extra features in. Didn't explain them, and didn't explain why the extra additions were added."

## 二、上次（Pandas SQL，16/20）每条扣分，这次怎么做

| 上次的扣分 | 这次的做法 |
|---|---|
| Modularity 4/5：设计比需要的复杂（5 个类） | 题目列了 3 项职责，就写 3 个类，每个类只用一个库；`main` 是函数，不加协调类 |
| Robustness 4/5：清理和验证代码超出要求 | 只处理题目写明的 "missing or unusable data"：`-99.99` 和空值、缺文件、缺列、数据不够。全程序只有 1 处检查 |
| Scalability 4/5：改了原始列名 | 不改列名，直接用 `decimal` 和 `average` |
| Clarity 3/5：多余的控件、转换、验证、状态 | 没有 GUI、没有额外功能、没有验证方法；71 行代码 |
| Notebook 8/10：主要来自旧作业 | 全部来自本模块的 notebook：Dataframes.py、Numpy.ipynb、Data Visualization.ipynb、Pandas.ipynb |
| Comments 8/10：注释和实现细节仍偏多 | 注释从 66 行降到 27 行，只有三类：改编记录、非 notebook 写法的 why/how、不明显的原因 |

## 三、设计

| 类 | 库 | 改编自（都已对照原文核实） | 主要改动 |
|---|---|---|---|
| `CO2Data` | pandas | Dataframes.py 的 `PandasDataFrameDashboard` | DataFrame 改成来自 `pd.read_csv()`；设为私有；用 `to_numpy()` 交出数组；删掉统计方法 |
| `LinearRegression` | NumPy | Numpy.ipynb 的 `NumPyDashboard.class_trend()` | 保留"返回 slope, intercept"；`np.polyfit()`（题目禁止）换成题目给的公式；x 改为传入的数组 |
| `CO2Plot` | Matplotlib | Data Visualization.ipynb 的 practice plot 单元格 | 保留 `plt.subplots()`、标题、轴标签、`plt.show()`；加 `ax.scatter()`、`ax.plot()`、`ax.legend()` |

唯一一个 notebook 里没有的写法是 `read_csv(na_values=...)`，注释里按题目要求写了 Why 和 How。

## 四、数据事实（都实测过）

- `average` 列有 5 个 `-99.99`（1964 年 2–4 月、1975 年 12 月、1984 年 4 月），表示当月没有测量值。
- 不处理时斜率是 1.76；去掉后是 1.58。所以必须处理。
- 选 `average` 而不是 `interpolated`：题目和 notebook 都说 "measured / original observations"，`interpolated` 在这 5 个月里是估计值。两种选法结果很接近（1.5797 和 1.5780）。
- 散点和回归线默认都是同一种蓝色，所以回归线要指定颜色。

## 五、验证结果（pandas 2.3 和 3.1 都跑过）

- 726 个观测值；斜率 1.5797 ppm/年，截距 -2787.43；和 `np.polyfit` 的结果相差 10⁻¹² 量级（`polyfit` 只用于核对，提交的代码里没有）。
- `x`、`y`、`predicted` 都是 726 个元素的 NumPy 数组；图上的散点和回归线用的就是这三个数组；标题、轴标签、图例齐全。
- 10 种坏数据情况都只输出一句清楚的提示，没有崩溃也没有警告：缺文件、空文件、只有表头、缺列、只有一行、全是 -99.99、x 全相同、有空格子、行数变少、列里混进文字。
- 代码里没有循环，没有 `polyfit`/`sklearn`；`main` 不直接碰 pandas、NumPy、Matplotlib。
- 注释里的 12 条引用全部在仓库文件里核对到原文。

## 六、还不确定的地方

1. 老师心里的"合适的 CO2 列"可能是 `interpolated`。我们选了 `average` 并写明了理由。
2. 回归类里那一处检查（少于 2 个点或 x 全相同）可能被看成多余，也可能被看成健壮性。
3. 注释 27 行，绝对数量比上次少一半多，但程序很短，所以比例看起来不低。
