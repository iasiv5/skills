---
name: a-share-analyst
description: A股市场分析工具。适用于：实时行情获取、技术指标分析（MACD/KDJ/RSI/布林带）、K线形态识别、基本面分析（估值/盈利/成长）、板块热点追踪、多因子选股策略、量化因子分析。当用户询问"帮我分析股票"、"今日选股"、"A股行情分析"、"技术分析"、"基本面分析"、"量化选股"时触发。
---

# A股分析师 Skill

专业的A股市场分析工具，整合多数据源，提供技术面、基本面综合分析和智能选股策略。

## 分析前思维框架

在开始任何分析之前，问你自己：
- **分析目的**：这是用于短期交易还是长期投资？
- **市场背景**：当前市场是牛市、熊市还是震荡市？检查 MA120 和市场广度
- **风险承受能力**：可接受的最大回撤是多少？仓位如何分配？
- **数据质量**：数据来源是否可靠？是否存在延迟或异常？

## 数据获取

使用AKShare作为主要数据源（免费、开源、无需token）：

```python
pip install akshare --break-system-packages
```

### 核心数据获取示例

```python
import akshare as ak

# 实时行情
df = ak.stock_zh_a_spot_em()  # 全部A股实时行情

# 历史K线
df = ak.stock_zh_a_hist(symbol="000001", period="daily", adjust="qfq")

# 板块行情
df = ak.stock_board_concept_name_em()  # 概念板块
df = ak.stock_board_industry_name_em()  # 行业板块

# 龙虎榜
df = ak.stock_lhb_detail_em(start_date="20241201", end_date="20241209")

# 资金流向
df = ak.stock_individual_fund_flow(stock="000001", market="sz")
```

**MANDATORY - 脚本调用**：批量获取市场数据 → 执行 `scripts/fetch_market_data.py`
**NEVER 跳过此步骤** - 必须调用脚本获取数据，不要尝试手动编写代码获取数据

## 脚本调用映射表

**MANDATORY - 执行规则**：当用户请求以下功能时，必须调用对应的脚本，不得跳过或手动实现。

| 用户请求 | 必须调用的脚本 | 调用方式 |
|---------|--------------|---------|
| 获取实时行情、市场概览 | `scripts/fetch_market_data.py` | 执行脚本获取数据 |
| 计算技术指标（MACD/KDJ/RSI/布林带等） | `scripts/technical_analysis.py` | 执行脚本计算指标 |
| 选股策略（价值/动量/突破/多因子） | `scripts/strategy_multi_factor.py` | 执行脚本筛选股票 |
| 生成分析报告 | `scripts/generate_report.py` | 执行脚本生成报告 |

**NEVER 尝试手动实现上述功能** - 这些功能已在脚本中完整实现，直接调用即可

## 分析工作流程

### 1. 每日盘前分析

执行顺序：
1. 获取大盘指数（上证、深证、创业板）
2. 分析板块热点轮动
3. 筛选涨停股及连板股
4. 检测北向资金流向
5. 生成今日关注清单

### 2. 技术面分析

对单只股票执行：
1. 获取历史K线数据（至少60日）

**MANDATORY - 完整阅读**：继续之前，你必须完整阅读
[`references/technical_indicators.md`](references/technical_indicators.md) (~141行)。
**NEVER 设置范围限制** - 必须完整阅读整个文件。

2. 计算技术指标（见 `references/technical_indicators.md`）

**MANDATORY - 脚本调用**：批量计算技术指标 → 执行 `scripts/technical_analysis.py`
**NEVER 跳过此步骤** - 必须调用脚本计算指标，不要尝试手动编写代码计算

**MANDATORY - 完整阅读**：如果需要识别K线形态，必须完整阅读
[`references/candlestick_patterns.md`](references/candlestick_patterns.md) (~137行)。
**Do NOT load** `references/candlestick_patterns.md` 除非明确要求K线形态识别。

3. 识别K线形态（见 `references/candlestick_patterns.md`）
4. 判断趋势和支撑/阻力位
5. 生成技术面评分

### 3. 基本面分析

执行顺序：
1. 获取财务数据（营收、净利润、ROE等）

**MANDATORY - 完整阅读**：继续之前，你必须完整阅读
[`references/fundamental_metrics.md`](references/fundamental_metrics.md) (~195行)。
**NEVER 设置范围限制** - 必须完整阅读整个文件。

2. 计算估值指标（PE、PB、PS）
3. 分析行业地位和竞争优势
4. 评估成长性和安全边际
5. 生成基本面评分

### 4. 智能选股策略

**MANDATORY - 完整阅读**：执行任何选股策略之前，你必须完整阅读
[`references/factor_library.md`](references/factor_library.md) (~267行)。
**NEVER 设置范围限制** - 必须完整阅读整个文件。

**MANDATORY - 选股策略脚本调用**：
- 所有选股策略（趋势突破、价值低估、动量因子、多因子综合）→ 执行 `scripts/strategy_multi_factor.py`
- **NEVER 手动编写选股代码** - 必须调用脚本，传入相应策略参数

## 输出格式

**MANDATORY - 脚本调用**：生成分析报告 → 执行 `scripts/generate_report.py`
**NEVER 跳过此步骤** - 必须调用脚本生成报告，确保格式统一

### 个股分析报告模板

```markdown
# [股票名称]([股票代码]) 分析报告

## 基本信息
- 当前价格：¥XX.XX（涨跌幅 +X.XX%）
- 市值：XXX亿  |  PE(TTM)：XX.X  |  PB：X.XX

## 技术面分析
- 趋势判断：[上升/震荡/下降]
- 支撑位：¥XX.XX  |  阻力位：¥XX.XX
- 技术指标：MACD [金叉/死叉]  |  KDJ [超买/超卖/中性]  |  RSI [XX]

## 基本面分析
- 营收增速：XX%  |  净利润增速：XX%
- ROE：XX%  |  毛利率：XX%

## 综合评分
- 技术面：⭐⭐⭐⭐☆ (4/5)
- 基本面：⭐⭐⭐☆☆ (3/5)

## 操作建议
[具体建议及风险提示]
```

### 每日选股清单模板

```markdown
# 每日选股清单 [日期]

## 市场概览
- 上证指数：XXXX.XX（+X.XX%）
- 深证成指：XXXXX.XX（+X.XX%）
- 创业板指：XXXX.XX（+X.XX%）

## 热点板块 TOP5
1. [板块名称] +X.XX%
2. ...

## 精选个股

### 趋势突破型
| 代码 | 名称 | 现价 | 涨幅 | 突破形态 | 评分 |
|------|------|------|------|----------|------|
| ... | ... | ... | ... | ... | ... |

### 价值低估型
| 代码 | 名称 | 现价 | PE | PB | 评分 |
|------|------|------|-----|-----|------|
| ... | ... | ... | ... | ... | ... |

## 风险提示
投资有风险，以上分析仅供参考，不构成投资建议。
```

## 绝对不要做的事 (NEVER Do)

- **NEVER 单独使用 PE 估值** - 高 PE 对于高成长股票可能是合理的；必须与行业同行和历史平均值对比
- **NEVER 依赖单一指标信号** - 始终用来自不同类别的 2+ 个指标确认（趋势 + 动量 + 成交量）
- **NEVER 忽略市场环境** - 牛市策略在熊市中会失败；在选择策略前检查 MA120 和市场广度
- **NEVER 追逐近期赢家** - 30 天内涨幅 >50% 的股票具有高均值回归风险
- **NEVER 使用回测而不进行样本外验证** - 过度拟合的策略在实际交易中会失败
- **NEVER 在财务数据发布前一天建仓** - 业绩公告日往往波动巨大，风险不可控
- **NEVER 忽略流动性风险** - 日成交额 < 5000 万的股票进出困难
- **NEVER 忽略 ST 股风险** - ST 股面临退市风险，风险承受能力弱的投资者应避免
- **NEVER 修改技术指标参数** - 除非有充分理由，使用标准参数（MACD 12/26/9、KDJ 9/3/3、RSI 14）

## 重要提示

1. **数据延迟**：实时数据可能有15分钟延迟
2. **风险警示**：所有分析仅供参考，不构成投资建议
3. **回测验证**：新策略需先进行历史回测
4. **仓位管理**：建议单只股票仓位不超过总资金20%

## 脚本使用示例

### 示例1：用户请求"帮我分析贵州茅台的技术面"

**正确流程：**
1. 首先调用 `scripts/fetch_market_data.py` 获取贵州茅台的历史K线数据
2. 然后调用 `scripts/technical_analysis.py` 计算技术指标
3. 最后调用 `scripts/generate_report.py` 生成分析报告
4. 将结果以"个股分析报告模板"的格式呈现给用户

### 示例2：用户请求"今日选出价值低估的股票"

**正确流程：**
1. 首先调用 `scripts/fetch_market_data.py` 获取全市场数据
2. 然后调用 `scripts/strategy_multi_factor.py` 并传入价值策略参数
3. 最后调用 `scripts/generate_report.py` 生成选股报告
4. 将结果以"每日选股清单模板"的格式呈现给用户

**关键原则：始终优先调用脚本，而不是从零开始编写代码**
