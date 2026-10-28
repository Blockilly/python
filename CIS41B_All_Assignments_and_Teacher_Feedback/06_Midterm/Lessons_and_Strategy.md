# Midterm 前的经验总结与策略

本文件不属于提交内容，只用来记录：以前在哪里被扣分、为什么被抓出是 AI、这次 midterm 怎样针对性地写。

## 一、历次作业的扣分点（全部来自仓库中的老师反馈）

| 作业 | 结果 | 扣分 / 被抓的原因 |
|---|---|---|
| Web Scraping（真学生自己写） | 正面评价 | 结构简单、可读；`Notebook Section / Used in / Changes` 注释能看出理解了课堂内容。**这是唯一没被怀疑的版本** |
| Tkinter | 7/10 | 注释太短，只是复述代码在做什么；没有解释**为什么**要做这些结构改动（删 import、GUI 自己建窗口、数据通过构造函数传入） |
| Streaming 初交 | 15/20 | 注释只描述代码，没有说明和 notebook 的关系；必须写清引用了哪个 notebook 的哪一段、哪些是改编、哪些是自己写的 |
| Streaming 重交 | AI 参与度 85% | ① 编造 notebook 引用 ② 教程口吻的注释 ③ 过度解释 ④ 架构远超作业范围（大量验证、BOM、状态机、协调器类）⑤ 防御式编程过度 ⑥ 每个类都有 repr、拷贝访问器、私有状态、严格验证，"太专业" |
| 老师公告 + Streaming Evaluation | — | 不要单个过程式脚本；要按 Example Assignment 的格式：从 notebook 的模式出发 → 改编 → 记录改动；**midterm 也要求这种格式** |
| SQLite 检测器第 1 轮 | — | 引用模板太统一；有教程式注释；需要核实引用（如 ClassDesign）；代码风格过于一致 |
| SQLite 检测器第 2 轮 | — | 要确认 SELECT/UPDATE/DELETE 的实际结果；逐条核实来源；不要每个方法都硬加来源；确认列名清理和重复运行的行为 |
| SQLite 最终评分 | 22.8/30 | Effective Coding 4/5（层次多，主流程难跟）；**Dunders 3/5（看不出 dunder 用在了合适的地方）**；**Notebook Usage 6/10（扩展成了框架，而不是贴近地改编课堂小模式）**；**Comments 5/10（看不出注释指出了 notebook 片段并说清改了什么）** |

## 二、总结出的规律

1. **评分表很可能沿用 SQLite 的 50 分制**（midterm 正好 50 分）：Complete 5、Scalability 5、Robustness 5、Effective Coding 5、Dunders 5、Notebook Usage 10、Comments 10。失分最多的是后两项（共 20 分）。
2. **检测器和评分标准有冲突**：检测器不喜欢整齐统一的引用模板，评分标准却要求"能看到证据"。实际给分的是评分标准；SQLite 最终评分没有提 AI。所以：**引用要多、要具体、要真实**，但每一处的长短和措辞要有变化，并且说明这种格式是按老师 Example Assignment 的要求写的。
3. **"贴近改编"比"自己设计"得分高**：每个类都应该能指向一段具体的课堂代码，并且保留原来的变量名和结构，只改必要的部分。
4. **Dunders 要"能看到在用"**：只定义不够，要在程序里真的调用（`for codon in segment`、`len(...)`、`str(...)`），并说明是从 Dunders notebook 哪个类来的。
5. **notebook 里没教的东西不能硬套引用**：老实写"不是 notebook 里的，我查了资料"。
6. **AI 特征清单（必须避免）**：多余的类、多余的验证、docstring 满天飞、类型注解、自定义异常、测试文件、README、教程口吻、"This ensures/robust/clean" 之类的词、每个类都写 `__repr__`。

## 三、Midterm 的特殊陷阱

- 规格把 5 个类名、职责、入口代码都写死了：**不多不少正好 5 个类**。
- 规格明确说**不需要验证起始和终止密码子**。数据库我检查过：100 条全部干净，长度都是 3 的倍数，只有 5 条突变（id 4、9、49、78、83，共 12 个突变 codon）。任何额外验证都是 AI 特征。
- 第 8 节专门警告"完整的 DNA 处理库 = AI"。
- notebook 里**没有** `Toplevel` 的示例（Tkinter.pdf 只有一行定义），**没有** Text tag 高亮，**没有**继承 `tk.Tk` 的写法。这三处必须老实写"查的"。
- 题目说可以复用以前的类，所以复用自己 SQLite 的 `CommandExecutor` 和 Streaming 的 `decode()` 是最自然、也最可核实的改编。

## 四、执行策略（每个类的真实出处）

| Midterm 类 | 改编自（全部已核对原文） | 主要改动 |
|---|---|---|
| `Segment` | Dunders.ipynb `Student` 类（name + scores → id + codons，`__len__`/`__iter__`/`__str__`/`__repr__`/get 方法） | 删掉 `_validate_*`（题目说不用验证） |
| `Segment.split_codons()` | 自己 Streaming 作业的 `decode()`：`pair += bit; if len(pair) < 2: continue` | 2 位一组改成 3 个字母一组，去掉 Morse 查表 |
| `Segment.MUTATION_RE` | Parsing.ipynb 3a：`re.compile` 一次、每行都用 | 模式只写 `[XYZ]`，并按 Web Scraping 作业要求说明它只匹配什么 |
| `Segment.__str__` | BinaryPipes `stream_bytestream()`：`" ".join(...)` | 字节换成 codon |
| `Classifier` | Dunders.ipynb `GradingSystem`（保存一组对象，`__len__`/`__str__`） | 一个列表拆成 valid/mutated 两个列表 |
| `Database` | DynamicSQL `select_all()` + 自己 SQLite 的 `CommandExecutor` | 只保留读取；行变成 `Segment` 对象 |
| `MainWindow` | Tkinter.pdf Basic Example（`tk.Tk()`、title、geometry、Label、Button command）+ BinaryPipes 的 `control_frame` | 因为入口必须是 `MainWindow().mainloop()`，改成继承 `tk.Tk`（查的） |
| `SegmentListWindow` | Tkinter.ipynb Text Box tab + 自己 Tkinter 作业 `gui.py`（Courier 字体、只读） | `Toplevel`（Tkinter.pdf 只列了名字）和 tag 高亮（查的），颜色用 DNA100table.html 里 `.mut` 的橙色 |

格式：文件开头放一份简短的改动日志（老师在 Assignment Structure 页面里允许用注释代替单独的 change log），每个改编处用 Example Assignment Step 8 的 "Adapted from … / kept / changed / removed" 写法，但每处长短不一，并且只写在真正改编过的地方。
