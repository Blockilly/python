# Threading 作业：策略

本文件不属于提交内容。提交的是 `Submission/ThreadedProducerConsumer.py`（加 `CO2.csv`）。

## 依据（都在仓库里）

- 作业 PDF：`Exercise Threading.pdf`
- 直接模板：`Examples/ThreadingDriver.py`（Threading notebook 配套代码）的 `TechniqueBase`、`BasicQueueTechnique`、`CompositeGUI`
- `Documents/Threading.pdf`：结构化消息 `(sequence, item)`、序号规则、哨兵、GUI 队列 + `after()`
- 课上原话（`Lecture - Threading.txt`）："the base class that you'll be designing… holding the information that's common to both the consumer and the producer"；"Adding a lot of additional code… and then documenting the additional code by describing what each line does. And that's not the purpose"
- `QueryBuilder`、`CommandExecutor`：自己的 SQLite 作业

## 上两次评语的教训怎么落实

| 评语 | 这次 |
|---|---|
| CO2 原版：多余的私有属性、property、常量、异常处理（Program structure 3/5） | 没有私有属性、没有 property；只有 3 处 try（CSV 读取、SQL 失败回滚、和 notebook 一样的 GUI 队列读取） |
| CO2 原版：注释在为多余结构辩护（Comments 5/10） | 注释只写改编点 |
| CO2 重交：解释太少，尤其是核心部分和整体类设计 | 文件开头写了类设计为什么这样拆；每个类写 kept / changed / removed 和原因；核心的 Client、Server 两个类写得最清楚 |

## 设计

| 类 | 改编自 | 主要改动和原因 |
|---|---|---|
| `QueueWorker` | `TechniqueBase` | 保留共享队列和往 GUI 队列放消息的方法；去掉 `maxsize=10`，这样 Server 还没启动时 Client 也能发送而不会卡住 |
| `Client` | `BasicQueueTechnique.producer()` | cookie 换成 QueryBuilder 生成的 SQL；固定的 `sequence_order` 换成基于 `next_sequence` 的序号；按钮通过一个命令队列让发送在 Client 线程里做 |
| `Server` | `BasicQueueTechnique.consumer()` | 保留 expected 和接受/拒绝规则、哨兵；接受时用 CommandExecutor 执行，拒绝的不执行；sqlite 连接在 Server 线程里创建 |
| `QueryBuilder` / `CommandExecutor` | SQLite 作业 | 只保留 CREATE/INSERT 和回滚 |
| `ThreadingGUI` | `CompositeGUI` | 保留 `log_queue` + `after(100)`、浅红/浅绿文本框；按钮换成题目要求的 4 个，加两个状态标签 |

## 测试（真实 Tk 窗口，xvfb）

- 先启动 Client 再启动 Server：查询在队列里等着，Server 启动后照常处理。
- "Send Out of Order"：#7 早到被拒绝且没有执行，之后 #6、#7 正常接受；数据库 11 行，没有重复。
- 小文件：-99.99 的行被排除；发完后哨兵送到 Server，两边状态都是 finished；只剩最后一条时点 Out of Order 也正常。
- CSV 不存在：Client 日志里一句提示，状态 stopped，界面不卡。
- 只有主线程更新过控件。
- 注释里 10 条出处全部对照原文核实；注释/代码比 0.30。
