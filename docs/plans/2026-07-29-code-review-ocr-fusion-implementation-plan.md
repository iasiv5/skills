# Code Review Skill OCR 价值融合 实施计划（v2 · 评审订正版）

## 目标

把阿里 Open Code Review (OCR) 中与 code review 相关、且与本地 skill 不冲突的有价值设定，融合进本地 `/code-review` skill。融合成果须同时满足 writing-great-skills 与 darwin-skill 质量要求。

## 架构快照

本次采用**分级吸收**思路：不是整体移植 OCR，而是按 grill 会话达成的 Q1–Q6 共识，逐条判断"吸收 / 拒绝 / 改造"，只引入与本地双轨证据体系兼容或互补的设定。

与现有结构衔接：
- 本地 skill 的核心体系（Spec/Standards 双轨证据 + 🔴🟡🟢 分级 + 待确认/验证缺口 transparency）**保留不变**。
- OCR 设定按 6 条共识落入 SKILL.md 的对应 Step + 3 份 resources 文件，不新增文件、不新增独立 phase。
- 反模式速查表补充 2 条 OCR 吸收项。

Q1–Q6 共识处置摘要（自包含；grill 原始记录在会话内存，已被本表取代为可追溯依据）：

| # | 共识 | OCR 设定处置 | 落点 |
|---|------|-------------|------|
| Q1 | 分级精度：🟢 不确定即沉默；🔴🟡 不确定即明示待确认 | 拒绝全局 silence-on-uncertainty，仅下沉到 🟢 | SKILL 头部原则 + Step 4 🟢 行 + resources 头部衔接句 |
| Q2 | 证伪自检（仅 🔴🟡）：diff 反证 → 自否决降级 + 验证状态段记录 | 引入 falsify-not-verify 精神，改 silent-drop 为透明记录 | 新 Step 4.5 + Step 6 验证状态占位行 |
| Q3 | 不引入 strict focus | 拒绝；吸收 deleted-code-as-context + 不评论未改动代码 | 反模式速查 +2 条 |
| Q4 | 双面 checklist（仅误报高发项） | 引入"应报/不应报"结构，限覆盖高 signal 反例，与现有"待确认"形成证据阶梯 | FIRMWARE-CHECKS + REVIEW-CHECKLIST |
| Q5 | 风险预扫（吸收式，无独立 phase） | 拒绝独立 plan phase；精神零成本落进 Step 1 可选输出 | Step 1 输出 ⑤ 项（**v2 订正：解耦 400 行 gate，落 Step 1 而非 Step 0**） |
| Q6 | 定位失败兜底 | 吸收 OCR location-fail 机制 | Step 4 新增纪律（术语纳入头部术语纲领） |

新术语在本计划的统一登记（便执行者交叉核对，最终在 Task 1 落入 SKILL.md 头部术语体系）：

| 术语 | 定位 | 与现有术语关系 |
|------|------|---------------|
| 分级精度（tiered precision） | Q1 北极星 | 统摄 🔴🟡🟢 分级行为的新顶层规则 |
| 风险预扫 = 动作（吸收 OCR plan phase 精神）；风险摘要 = 其产出物（Step 1 列出的"风险点位置+类别"） | Q5 | 二者为动作/产出关系，不混用 |
| 证伪自检（falsification self-check） | Q2 Step 4.5 子步骤 | 处理"确定假阳性"（diff 直接反证），与"待确认"（处理"不确定项"）互补不重叠 |
| 自否决降级（self-rejection downgrade） | Q2 证伪自检的结果动作 | 证伪自检判定反证成立后对发现的处置 |
| 定位失败兜底 / 位置待重锚定 | Q6 Step 4 纪律 / 发现标注 | 与"范围外观察""验证缺口"同族——均为"把不确定性显式交给人类" |

## 全局约束

- 语言：skill 正文与 resources 保持中文（与现有文件一致）。
- 术语：新增术语必须纳入 `SKILL.md` 现有术语体系（Spec 轨 / Standards 轨 / 待确认 / 验证缺口 / 范围外观察 / 🔴🟡🟢 分级）；Task 1 头部原则段须一并点出新术语与已有术语的关系，不游离。
- 文件结构：不新增 skill 文件，不拆子文件（Q4 明确避免 sprawl）；所有改动就地落入现有 SKILL.md + 3 份 resources。
- 不引入外部依赖（OCR 是 CLI 工具，本次融合只吸收其方法论设定，不引入 `ocr` 命令依赖）。
- writing-great-skills 纪律：渐进式披露——改动落在已有层级（in-skill step / in-skill reference），不新建 context pointer。

## 输入工件

- grill 共识：共识表已内联到上文"架构快照"（自包含，不依赖会话内存）。
- 现有 skill：`code-review/SKILL.md`
- 现有 resources：`code-review/resources/{REVIEW-CHECKLIST,FIRMWARE-CHECKS,FEEDBACK-GUIDELINES}.md`
- 现有测试 prompt（Task 9 行为验证用）：`code-review/test-prompts.json`
- OCR 参考（只读）：`https://github.com/alibaba/open-code-review`（5 个 prompt 模板 + rule_docs + SKILL.md）

## v2 相对 v1 的变更摘要（评审订正）

- C1：Task 2/3 锚点订正——400 行 gate 在 Step 4 不在 Step 0；"风险摘要"重定位为 Step 1 可选输出，触发条件改为"diff 大或跨文件"，解耦 400 行 gate，消除时间线断裂与 Step 4 编辑冲突。
- C2：输入工件删除坏路径 `/memories/session/ocr-fusion-CONTEXT.md`，共识表内联自包含。
- M1：Task 4 增加 Step 3d——更新 Step 6 `### 验证状态` 模板，预留"证伪自检"占位行。
- M2：Task 9 新增 Step 9——test-prompts 行为验证（冒烟级）。
- m1：Task 4 Step 3c 锚点改写——L103 是 STOP 表后的独立段落，非表内行。
- m2：Task 4 Step 3b 锚点精确化——改为 L94 说明段之后、STOP 表之前。
- m3：Task 2 开头声明"风险预扫=动作，风险摘要=产出物"。
- m4：Task 4 Produces 补登"自否决降级"。
- m5：Task 1 头部术语纲领补登"位置待重锚定"与"证伪自检"的术语关系。
- m6：Task 6 Step 3b"现有两段"改为"该段现有正文"。
- m7：Task 6 反例措辞与已有"待确认"句式对齐，形成证据阶梯。

## 文件结构与职责

- Modify: `code-review/SKILL.md`——头部原则段+术语纲领（Q1/m5）、Step 1 输出 ⑤ 风险摘要（Q5/C1）、Step 4 🟢 行精度补充+定位失败兜底纪律段（Q1/Q6）、Step 4.5 证伪自检子步骤（Q2）、Step 6 验证状态占位行（M1）、反模式速查 +2 条（Q3）
- Modify: `code-review/resources/FIRMWARE-CHECKS.md`——4 个专项段各补"不应报"高 signal 反例小节（Q4/m7），头部加 Q1 衔接句
- Modify: `code-review/resources/REVIEW-CHECKLIST.md`——误报高发项（并发/安全）补"不应报"反例小节（Q4），头部加 Q1 衔接句
- Modify: `code-review/resources/FEEDBACK-GUIDELINES.md`——新增"位置待重锚定""自否决降级"措辞示例（Q2/Q6）
- Test: grep 字面验证（Task 9）+ test-prompts 冒烟行为验证（Task 9 Step 9）

## 任务清单

### Task 1: SKILL.md 头部——写入"分级精度"顶层原则 + 术语纲领（Q1 + m5）

- 目标：在 SKILL.md 头部原则段加入分级精度哲学，确立 🟢 沉默 / 🔴🟡 明示的顶层规则；并在术语句一并登记新术语与已有术语的关系，避免新标签游离（m5）。
- 涉及文件：`Modify: code-review/SKILL.md`（头部原则段，第一行 frontmatter 之后、`## Step 0` 之前）
- 接口契约
  - Consumes: 无
  - Produces: 术语"分级精度"（tiered precision）、"位置待重锚定""证伪自检"的纲领性登记——Task 2/3/5/6/7 引用（Task 4 反模式独立、Consumes 无）
- 验证范围：grep 到"分级精度"且含 🟢 沉默 + 🔴🟡 明示；grep 到"位置待重锚定"或"证伪自检"在头部出现

- [ ] Step 1: 确认当前 SKILL.md 头部原则段无"分级精度"概念
- Run: `grep -n "分级精度" code-review/SKILL.md`
- Expected: 无匹配；确认缺口存在
- [ ] Step 2: 确认缺口
- [ ] Step 3: 在头部原则段（`每条发现须追溯...不虚构命令结果。` 这段之后、`## Step 0` 之前）插入分级精度原则段 + 术语纲领
- Change: 插入一段，要点——【分级精度】当上下文不清、无法证实也无法证伪一个发现时，按严重度分流感——🟢 建议（无量化影响的命名/风格/文档）选择不报，不消耗信任；🔴 必须修复与 🟡 强烈建议绝不沉默，标注"待确认"并留验证缺口。理由：BMC/固件领域沉默可能放过炸硬件的时序/寄存器 bug，精度纪律只下沉到低危层。同段术语句补登记：证伪自检（Step 4.5，处理 diff 直接反证的确定假阳性，与"待确认"处理的不确定项互补）、位置待重锚定（定位失败兜底的发现标注，与"范围外观察""验证缺口"同属"显式交给人类"族）。
- [ ] Step 4: 确认落地
- Run: `grep -n "分级精度" code-review/SKILL.md`
- Expected: 匹配到 1 处，位于头部原则段
- Run: `grep -n "证伪自检\|位置待重锚定" code-review/SKILL.md`
- Expected: 头部段出现至少 1 处（术语纲领）
- [ ] Step 5: 可选 checkpoint commit

### Task 2: SKILL.md Step 1——增加可选"风险摘要"输出（Q5，v2 订正落点）

- 目标：把 OCR plan phase 精神零成本吸收为 Step 1 的可选输出，产出"风险摘要"。
- 术语声明（m3）：风险预扫 = 动作（吸收 OCR plan phase 精神），风险摘要 = 其产出物（Step 1 列出的"风险点位置 + 类别"）。本任务按"风险摘要"一致用词。
- 涉及文件：`Modify: code-review/SKILL.md`（`## Step 1` 输出描述段；**不碰 Step 0、不碰 Step 4**，v2 C1 订正）
- 接口契约
  - Consumes: Task 1 的"分级精度"术语
  - Produces: Step 1 输出含"风险摘要"——供 Step 2 双轨证据链建设参考（与本任务 Step 3 Change 措辞一致）
- 验证范围：grep 到 Step 1 段含"风险摘要"，触发条件为"diff 大或跨文件"（非"Step 0 触发"），且含"不把 🟢 提级"

- [ ] Step 1: 确认 Step 1 当前输出清单无风险摘要项
- Run: `sed -n '/## Step 1/,/## Step 2/p' code-review/SKILL.md | grep -c "风险摘要"`
- Expected: 0
- [ ] Step 2: 确认缺口
- [ ] Step 3: 在 Step 1 "列出"清单现有四项后，追加第 ⑤ 项（合并 v1 的 Task 2+3 为一步，避免重复动 Step 1）
- Change: 追加"⑤ 当 diff 较大或跨文件时（Step 1 读完代码即可判断，不依赖后续 Step 4 的 400 行 gate），列出风险摘要（最可能的风险点位置 + 类别，按 Spec/Standards 自然分流），供 Step 2 双轨证据链建设参考。风险摘要只驱动 🔴🟡，不把 🟢 提级（守分级精度）。"
- [ ] Step 4: 确认落地
- Run: `sed -n '/## Step 1/,/## Step 2/p' code-review/SKILL.md | grep "风险摘要"`
- Expected: 匹配到，含"diff 较大或跨文件"且含"不把 🟢 提级"
- [ ] Step 5: 可选 checkpoint commit

### Task 3: SKILL.md Step 4🟢 行 + 定位失败兜底 + Step 4.5 证伪自检 + Step 6 验证状态占位行（Q1/Q2/Q6/M1，含 m1/m2/m4 订正）

- 目标：Step 4 内补 🟢 精度纪律行 + 定位失败兜底纪律段；`## Step 4` 与 `## Step 5` 之间插入 `### Step 4.5: 证伪自检（仅 🔴🟡）` 子步骤；Step 6 `### 验证状态` 模板预留"证伪自检"占位行。这是本次改动量最大的任务（合并 v1 Task 4 的全部 Step 3a–3c，并新增 M1 的 Step 3d）。
- 涉及文件：`Modify: code-review/SKILL.md`（Step 4 全段 + 新 Step 4.5 + Step 6 验证状态模板）
- 接口契约
  - Consumes: Task 1 "分级精度""证伪自检""位置待重锚定"术语；OCR falsify-not-verify 原则
  - Produces: 术语"证伪自检"（falsification self-check）+ "自否决降级"（self-rejection downgrade，m4 补登）+ "定位失败兜底"——Task 7（FEEDBACK-GUIDELINES）引用
- 验证范围：grep 到"Step 4.5" + "证伪自检" + "定位失败兜底" + "自否决降级"；确认仅 🔴🟡 + 不静默两条守则写入；Step 6 验证状态含证伪自检占位行

- [ ] Step 1: 确认 Step 4 当前无证伪自检、无定位失败兜底
- Run: `grep -n "证伪自检\|Step 4.5\|定位失败\|位置待重锚定\|自否决" code-review/SKILL.md`
- Expected: 仅 Task 1 头部登记处匹配，Step 4 区域无匹配；确认 Step 4 缺口
- [ ] Step 2: 确认缺口
- [ ] Step 3a: 在 Step 4 的 🟢 行说明里补充精度纪律
- Change: 在 🟢 建议行（"无量化影响但影响可维护性"那行）末尾追加："上下文不清时，对 🟢 选择不报而非报错估（分级精度：🟢 沉默优先，避免消耗信任）。"
- [ ] Step 3b: 在 Step 4 主体内插入"定位失败兜底"纪律段（锚点精确化，m2）
- Change: 插入位置——在 L94 "每个发现标注"说明段之后、L96 🛑 STOP 表之前（m2 订正：非"分级表之后"）。插入一段——【定位失败兜底】当一个发现的位置无法锚定到具体行/函数（如引用的代码已改动、跨文件推断无法精确落点），不丢弃该发现，降级处理：在发现标注"位置待重锚定"，或移入"范围外观察"；不得因定位失败而沉默。理由：BMC/固件领域定位漂移的发现仍有价值，需人类复核而非丢弃。
- [ ] Step 3c: 在 `## Step 5` 之前插入 `### Step 4.5: 证伪自检（仅 🔴🟡）`（锚点订正，m1）
- Change: 插入位置——在 L103 "对 BIOS/BMC 改动，将专项检查与 Spec/Standards 交叉验证"该独立段落（**注意 m1：L103 是 STOP 表 L96–102 之后的独立段落，不是表内行**）之后、`## Step 5` 之前。新增完整子步骤——输入：Step 4 的 🔴🟡 发现列表。动作：对每条 🔴🟡 发现，检查 diff 本身是否提供直接反证（与发现的核心断言矛盾）。判定：证伪不证实——只在 diff 内有直接反证时，将发现**自否决降级**或移除；diff 之外信息不可证伪（即使可疑也放行，交由分级精度的待确认处理）。输出：在报告"验证状态"段如实记录"证伪自检：移除/降级 N 条（自否决理由）"，不静默删除。🟢 不做证伪自检。已知限制：跨文件发现的反证多在 diff 外，自检对它们基本失效（Q3=C 已记录）。
- [ ] Step 3d: 更新 Step 6 验证状态模板，预留证伪自检占位行（M1）
- Change: 在 Step 6 报告模板的 `### 验证状态` 段（现有"已执行/未执行"行 + "验证边界"行）之间或末尾，新增一行占位：`- 证伪自检：[移除/降级 N 条 🔴🟡 发现，理由：diff 直接反证 — <简述>；未执行则填"无"]`
- [ ] Step 4: 确认全部落地
- Run: `grep -n "Step 4.5\|证伪自检\|定位失败兜底\|位置待重锚定\|自否决降级" code-review/SKILL.md`
- Expected: 在 Step 4 区域匹配到
- Run: `grep -n "不静默\|证伪不证实" code-review/SKILL.md`
- Expected: 匹配到，位于 Step 4.5
- Run: `sed -n '/### 验证状态/,/###/p' code-review/SKILL.md | grep "证伪自检"`
- Expected: 匹配到占位行
- [ ] Step 5: 可选 checkpoint commit

### Task 4: SKILL.md 反模式速查——补充 2 条 OCR 吸收项（Q3）

- 目标：反模式速查表末尾追加 2 行，吸收 OCR 的 deleted-code-as-context 和不评论未改动代码两条规则，脱离 strict focus 独立落地。
- 涉及文件：`Modify: code-review/SKILL.md`（反模式速查表）
- 接口契约
  - Consumes: 无
  - Produces: 无
- 验证范围：grep 到 2 条新反模式行

- [ ] Step 1: 确认反模式表当前无这 2 条
- Run: `grep -n "删除的代码仅作参考\|未改动代码\|deleted code" code-review/SKILL.md`
- Expected: 无匹配
- [ ] Step 2: 确认缺口
- [ ] Step 3: 在反模式表最后一行（"用通用 checklist 推翻项目规范/EDK2/MISRA/硬件资料"那行）下方追加 2 行
- Change:
  - `| 把删除的代码当审查目标去报问题 | 删除的代码仅作参考上下文，不对其发表评论（吸收 OCR） |`
  - `| 对未改动或正确代码发表评论 | 未改动代码不评论，审查聚焦新增/修改行（吸收 OCR） |`
- [ ] Step 4: 确认落地
- Run: `grep -n "吸收 OCR" code-review/SKILL.md`
- Expected: 匹配到 ≥2 处，位于反模式表
- [ ] Step 5: 可选 checkpoint commit

### Task 5: FIRMWARE-CHECKS.md——4 专项段补"不应报"反例 + 头部衔接句（Q4，含 m6/m7 订正）

- 目标：在 4 个专项段各补"不应报"高 signal 反例小节，头部加 Q1 分级精度衔接句；反例措辞与已有"待确认"句式对齐，形成证据阶梯（m7）。
- 涉及文件：`Modify: code-review/resources/FIRMWARE-CHECKS.md`
- 接口契约
  - Consumes: Task 1 "分级精度"术语
  - Produces: per-段"不应报"反例清单
- 验证范围：grep 到 ≥4 个"不应报"小节 + 头部衔接句

- [ ] Step 1: 确认当前文件无双面结构
- Run: `grep -c "不应报" code-review/resources/FIRMWARE-CHECKS.md`
- Expected: 0
- [ ] Step 2: 确认缺口
- [ ] Step 3a: 头部（第一段"激活 BIOS/UEFI..."之后）加分级精度衔接句
- Change: 追加一句"上下文不清时，对 🟢 建议选择不报而非报错估（分级精度，见 SKILL.md）；以下各段的'不应报'反例是该纪律的机械边界，与现有'待确认'形成证据阶梯——'待确认'用于证据不足的不确定项，'不应报'用于已有正面证据可排除的情形。"
- [ ] Step 3b: 在"## 1. 原始硬件数据"段（m6：该段现有正文 L7 之后）追加"### 不应报（高 signal 反例）"小节（m7：与 L7 "仅单位已知→待确认"对齐）
- Change: 列——已用数据表确认原始编码、量程、缩放均在定义范围内（与"仅单位已知不足以证明编码正确→待确认"形成证据阶梯：前者有数据表正面证据排除，后者证据不足留待确认）；数据表未给阈值但代码逻辑无内部矛盾（归"待确认"，不报为缺陷）。
- [ ] Step 3c: 在"## 2. 通信与长度"段追加"### 不应报"小节
- Change: 列——载荷长度在已确认缓冲区内且头部校验通过；`start + length <= end` 等加法式检查仅当已先确认 `total_len >= header_len` 减法式前提时不报减法缺失（前提存在才不报）。
- [ ] Step 3d: 在"## 3. 检查后使用（TOCTOU）"段追加"### 不应报"小节
- Change: 列——调用方在可信内存中已复制经验证数据（经确认后）；确定单线程非并发路径（如确认无 DMA/中断介入，标已确认）；只读操作不涉及校验后写入。
- [ ] Step 3e: 在"## 4. 时序结论"段追加"### 不应报"小节
- Change: 列——阈值或硬件限制未知（标验证缺口，不报为违规）；代码逻辑无内部时序矛盾且无规格阈值可比对。
- [ ] Step 4: 确认落地
- Run: `grep -c "不应报" code-review/resources/FIRMWARE-CHECKS.md`
- Expected: ≥4
- Run: `grep "分级精度" code-review/resources/FIRMWARE-CHECKS.md`
- Expected: 匹配到头部衔接句
- [ ] Step 5: 可选 checkpoint commit

### Task 6: REVIEW-CHECKLIST.md——误报高发项补"不应报"反例 + 头部衔接句（Q4）

- 目标：在并发处理、安全性（误报高发区）补"不应报"反例小节，头部加分级精度衔接句。固件专项已在 Task 5 覆盖，本任务只补通用清单高发项。
- 涉及文件：`Modify: code-review/resources/REVIEW-CHECKLIST.md`
- 接口契约
  - Consumes: Task 1 "分级精度"术语
  - Produces: per-段"不应报"反例
- 验证范围：grep 到"不应报"小节 + 头部衔接句

- [ ] Step 1: 确认当前清单无双面结构
- Run: `grep -c "不应报" code-review/resources/REVIEW-CHECKLIST.md`
- Expected: 0
- [ ] Step 2: 确认缺口
- [ ] Step 3a: 头部（第一段说明之后）加衔接句
- Change: 追加"上下文不清时，对 🟢 建议选择不报而非报错估（分级精度，见 SKILL.md）；以下'不应报'反例是该纪律的机械边界，与现有'待确认'形成证据阶梯。"
- [ ] Step 3b: 在"### 并发处理"段（现有 4 条 checked-box 之后）追加"#### 并发不应报（高 signal 反例）"小节
- Change: 列——方法内局部变量（天生线程安全）；确定单线程上下文（无多线程调用证据，需 code_search 确认）；只读操作（即使非线程安全数据结构）；已有正确同步（synchronized/Lock/atomic 类已使用）；final 字段指向不可变对象。
- [ ] Step 3c: 在"### 认证与授权"或"### 输入验证"段追加"#### 安全不应报（高 signal 反例）"小节
- Change: 列——参数化查询/预编译语句已使用（SQL 注入不报）；输出已转义或使用 textContent（XSS 不报）；测试桩/mock 中的占位密钥（非生产路径，标已确认）；静态 SQL 无动态参数拼接。
- [ ] Step 4: 确认落地
- Run: `grep -c "不应报" code-review/resources/REVIEW-CHECKLIST.md`
- Expected: ≥3
- [ ] Step 5: 可选 checkpoint commit

### Task 7: FEEDBACK-GUIDELINES.md——新增 Q2/Q6 措辞示例

- 目标：在反馈场景措辞示例中新增"位置待重锚定"发现（Q6）和"自否决降级"报告（Q2）的措辞，让报告输出与新机制对齐。
- 涉及文件：`Modify: code-review/resources/FEEDBACK-GUIDELINES.md`
- 接口契约
  - Consumes: Task 3 的"证伪自检""自否决降级""定位失败兜底"术语
  - Produces: 2 条新措辞示例
- 验证范围：grep 到 2 条新场景示例

- [ ] Step 1: 确认当前无这 2 类措辞
- Run: `grep -c "位置待重锚定\|自否决\|证伪自检" code-review/resources/FEEDBACK-GUIDELINES.md`
- Expected: 0
- [ ] Step 2: 确认缺口
- [ ] Step 3: 在"常见反馈场景"末尾追加 2 条
- Change:
  - `**🟡 位置待重锚定**：该发现引用的代码位置无法精确锚定到当前 diff（可能因跨文件推断或行漂移）。已在发现上标注"位置待重锚定"；请人工结合上下文复核具体落点。`
  - `**验证状态段**：证伪自检：自否决降级/移除 N 条 🔴🟡 发现（理由：diff 提供直接反证 — <简述反证>）。此操作未静默，保留可审计记录。`
- [ ] Step 4: 确认落地
- Run: `grep "位置待重锚定\|自否决" code-review/resources/FEEDBACK-GUIDELINES.md`
- Expected: 各匹配到 ≥1 处
- [ ] Step 5: 可选 checkpoint commit

### Task 8: 最终一致性验证 + test-prompts 冒烟行为验证（M2）

- 目标：确认 Q1–Q6 共识全部在文件中有落点、术语跨文件一致（grep 字面，必要不充分）；再用 test-prompts 跑一次冒烟行为验证，确认新机制在 diff 有反证/🟢 命名问题时被正确触发、Spec/Standards 双轨不破（M2 字面≠行为）。
- 涉及文件：全部 4 个改动文件 + `code-review/test-prompts.json`
- 接口契约
  - Consumes: Task 1–7 全部产出
  - Produces: 无（验证任务）
- 验证范围：6 条共识 grep 命中 + 术语一致 + 1–2 个 test-prompt 冒烟

- [ ] Step 1: Q1 分级精度——SKILL.md + 2 resources 有落点
- Run: `grep -l "分级精度" code-review/SKILL.md code-review/resources/FIRMWARE-CHECKS.md code-review/resources/REVIEW-CHECKLIST.md`
- Expected: 3 个文件均命中
- [ ] Step 2: Q2/Q6——SKILL.md Step 4.5 + 定位失败兜底落地
- Run: `grep -n "Step 4.5.*证伪自检\|定位失败兜底\|自否决降级" code-review/SKILL.md`
- Expected: 匹配到
- [ ] Step 3: Q3——反模式 2 条
- Run: `grep -c "吸收 OCR" code-review/SKILL.md`
- Expected: ≥2
- [ ] Step 4: Q4——双面反例覆盖
- Run: `grep -c "不应报" code-review/resources/FIRMWARE-CHECKS.md code-review/resources/REVIEW-CHECKLIST.md`
- Expected: FIRMWARE ≥4，REVIEW ≥3
- [ ] Step 5: Q5——风险摘要（v2：落 Step 1，非 Step 0）
- Run: `sed -n '/## Step 1/,/## Step 2/p' code-review/SKILL.md | grep "风险摘要"`
- Expected: 匹配到，触发条件为"diff 较大或跨文件"
- [ ] Step 6: FEEDBACK-GUIDELINES 措辞
- Run: `grep "位置待重锚定\|自否决" code-review/resources/FEEDBACK-GUIDELINES.md`
- Expected: 各命中
- [ ] Step 7: 术语一致性——"待确认""验证缺口""分级精度"在改动段未被改名
- Run: `grep -c "待确认\|验证缺口" code-review/SKILL.md`
- Expected: 与改前持平或增加（不减少）
- [ ] Step 8: Step 6 验证状态模板含证伪自检占位行（M1 落地确认）
- Run: `sed -n '/### 验证状态/,/^###\|^## /p' code-review/SKILL.md | grep "证伪自检"`
- Expected: 匹配到占位行
- [ ] Step 9: 冒烟行为验证（M2）——挑 test-prompts.json 中 1–2 个代表性 prompt 实跑 skill
- 说明：本轮只做"新机制被触发且不破坏既有双轨"的冒烟级确认，不要求完整 darwin Phase 2 paired 评审（那是实施后另起的工作）。
- 代表性用例覆盖：(a) diff 内含直接反证 → 证伪自检触发、自否决降级且在验证状态段留记录（非静默）；(b) 🟢 命名/风格问题在上下文不清时被选择不报（分级精度）。若 test-prompts.json 无现成贴合用例，可就地构造一个最小 diff 片段并附带说明。
- Run: `cat code-review/test-prompts.json`（先看现有 prompt，决定复用或构造）
- Expected: 实跑后确认证伪自检/分级精度被触发，Spec/Standards 双轨 pass/输出结构未被破坏；否则回退到对应 Task 修正。若子 agent 跑不通，退化干跑（标注 dry_run 并说明判断依据），不跳过本步。
- [ ] Step 10: 人审——通读 4 个文件改动段，确认与 Q1–Q6 共识一致、无矛盾、无 sprawl

## 执行纪律

- 开始实现前先批判性复查整份计划；发现缺项、矛盾、命名不一致或验证无效，先修计划。
- 按任务顺序执行（Task 1 是后续术语来源，必须先做）。
- 每完成一个任务，运行该任务定义的验证（grep 命令；Task 8 另含冒烟）。
- 遇到阻塞、重复失败或计划与仓库现实不符，立即停下说明，不猜。
- 本次改动均为 .md 文件，无需构建；验证靠 grep 字面（必要不充分）+ Task 8 冒烟行为 + 人审。
- 行号偏移：本计划行号为撰写时快照；Task 1/2 插入内容后后续行号（如 Task 3 的 L94/L103）全部下移，一律以语义锚点（段落首句文字，如"每个发现标注说明段""对 BIOS/BMC 改动…该独立段落"）为准定位，行号仅作辅助。
- 全部任务完成后，运行 Task 8 最终验证并输出修改摘要。

## 最终验证

- 命令：Task 8 的 Step 1–9
- 预期结果：6 条共识全部命令中命中、术语跨文件一致、Step 6 占位行就位、test-prompt 冒烟能触发新机制且不破坏双轨
- 环境：bash（仓库惯例；本次无平台特定命令）