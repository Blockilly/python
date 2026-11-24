# ThreadedCO2.py 评审（按老师之前的评分标准）

## 一、运行结果：功能完全正确

在真实 Tk 窗口（xvfb）里从头运行到结束：

- 731 行全部插入；故意提前发送的 #734 被拒绝且没有执行；COUNT 返回 731，没有重复行。
- 哨兵正常结束两个线程，数据库连接已关闭。
- 只有主线程更新过界面控件。

**但按老师之前的评分标准，估计只能拿到 70% 左右，扣分原因和 CO2 原版（65%）几乎一样。**

## 二、会被扣分的地方

### 1. 多余的代码和检查（最大的问题）

老师这次课上专门说过："a lot of you have been adding a lot of additional code… and then documenting the additional code"。CO2 原版也是因为 "more validation and structure than necessary"、"extra… exception handling" 被扣分。

| 多余的部分 | 位置 |
|---|---|
| 检查必须有 7 列、检查有没有非数字列、检查是否为空 | `Client.run` 第 109–113 行 |
| 额外的 COUNT 和 preview（`LIMIT 5`）查询，以及为它们加的 `fetchall` 分支 | `QueryBuilder`、`CommandExecutor` |
| 两处捕获 `OverflowError`；捕获 `pd.errors.ParserError` 是重复的（它本身就是 `ValueError` 的子类） | 第 70、140、188 行 |
| 接受、拒绝、出错的三个计数器 | `Server.run` |
| 每次最多处理 100 条消息的限流、红色高亮 tag、按钮逐个解锁的流程、底部说明文字 | `Application` |
| 一整套关闭流程（`closing` 标志、`finish_close` 轮询） | `close()` |
| 标识符加引号时还转义里面的 `"` | `QueryBuilder.__init__` |
| 每个类都有 docstring，文件开头还引用 README.txt | 全文件 |

### 2. 注释在为多出来的结构辩护

例如 "Process at most 100 messages per tick…"、"Do not join a running thread inside a GUI callback"、"Ordering and SQL success are different checks"。CO2 那次 Comments 只拿 5/10，原话是 "Much of the documentation explains or justifies the added structure"。

### 3. 没有基类

老师课上明确说过："the base class that you'll be designing… holding the information that's common to both the consumer and the producer"。现在 Client 和 Server 各自保存 `query_queue`、`log_queue` 和 `thread`，代码是重复的。

### 4. -99.99 被当作真实数值存进数据库

注释说这是"原样传输数据"，但题目的 Robustness 要求是 "handle missing or unusable data cleanly"。上次老师还专门表扬过处理 -99.99 的做法，这次却有 5 行 -99.99 被存成了 CO2 值。

### 5. 文件开头写了 "See README.txt"

如果不交 README.txt，这就是一个指向不存在文件的引用；如果交了，又多出一个文件。题目要的是一个能运行的程序。

## 三、做得好的地方

- 引用的出处是真实的，`BasicQueueTechnique` 发送 `(sequence, cookie)` 那段说明写得很好。
- 列名加引号保留了原始的 `#days`，回应了 Pandas SQL 那次 "quoting the existing names would have preserved the source data" 的意见。
- 线程安全、哨兵、sqlite 连接在 Server 线程里创建，这几处都做对了。

## 四、估分（按 CO2 那次的评分方式）

| 项目 | 估计 |
|---|---|
| 线程、队列、序号规则 | 5/5 |
| pandas | 4/5（多余的检查，-99.99 没处理） |
| SQL（QueryBuilder / CommandExecutor） | 4/5（多出来的 COUNT、preview、转义） |
| GUI | 4/5（限流、高亮、复杂的关闭流程） |
| 程序结构 | 3/5（没有基类，计数器和异常处理偏多） |
| Notebook 使用 | 6–7/10 |
| 注释 | 5–6/10 |
| **合计** | **约 31–33/45，大约 70%** |

## 五、建议

1. **交 `ThreadedProducerConsumer.py`**（在 `threading-submission` 分支的 `09_Threading/Submission/`）。它有老师提到的基类，处理了 -99.99，结构和 notebook 的 `BasicQueueTechnique`、`CompositeGUI` 一一对应，没有上面这些多余的东西，测试全部通过。
2. **或者在 ThreadedCO2.py 上删减**：去掉第二节表格里列的部分，加一个基类，过滤 -99.99，再删掉为多余结构写的注释。
