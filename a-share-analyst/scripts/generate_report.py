#!/usr/bin/env python3
"""
A股分析报告生成模块
生成个股分析报告和每日市场报告
"""

import akshare as ak
import pandas as pd
import numpy as np
from datetime import datetime
from technical_analysis import analyze_stock


def _get_index_amount_yi_map(codes: list[str]) -> dict[str, float | None]:
    """Fetch index 成交额 in 亿 for given codes.

    Prefer Sina spot (稳定且包含成交额). Fallback to Eastmoney spot.
    Returns: {code -> amount_yi} where amount_yi is float or None.
    """

    def _extract_amount(df: pd.DataFrame, code: str):
        if df is None or len(df) == 0:
            return None
        if "代码" not in df.columns or "成交额" not in df.columns:
            return None
        row = df.loc[df["代码"].astype(str) == str(code)]
        if row.empty:
            return None
        try:
            return float(row.iloc[0]["成交额"]) / 1e8
        except Exception:
            return None

    # 1) Sina spot
    try:
        spot = ak.stock_zh_index_spot_sina()
        out = {code: _extract_amount(spot, code) for code in codes}
        if sum(v is not None for v in out.values()) >= max(1, len(codes) // 2):
            return out
    except Exception:
        pass

    # 2) Eastmoney spot
    try:
        spot = ak.stock_zh_index_spot_em()
        return {code: _extract_amount(spot, code) for code in codes}
    except Exception:
        return {code: None for code in codes}


def generate_stock_report(symbol: str) -> str:
    """
    生成个股分析报告

    Args:
        symbol: 股票代码，如 "000001"
    """
    # 获取股票基本信息
    try:
        info = ak.stock_individual_info_em(symbol=symbol)
        info_dict = dict(zip(info["item"], info["value"]))
    except:
        info_dict = {}

    # 获取历史K线
    df = ak.stock_zh_a_hist(symbol=symbol, period="daily", adjust="qfq")
    df = df.tail(120)

    if len(df) == 0:
        return f"未找到股票代码: {symbol}"

    latest = df.iloc[-1]
    prev = df.iloc[-2] if len(df) > 1 else latest
    close = float(latest.get("收盘", latest.get("close", np.nan)))
    prev_close = float(prev.get("收盘", prev.get("close", close)))
    if prev_close:
        change_pct_fallback = (close - prev_close) / prev_close * 100
    else:
        change_pct_fallback = 0.0
    change_pct = float(latest.get("涨跌幅", change_pct_fallback))
    volume = float(latest.get("成交量", np.nan))
    amount = float(latest.get("成交额", np.nan))
    turnover = latest.get("换手率", None)

    # 技术分析
    analysis = analyze_stock(df)

    # 生成报告
    report = f"""
# {symbol} 分析报告

**生成时间**: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

---

## 基本信息

| 项目 | 数值 |
|------|------|
| 当前价格 | ¥{close:.2f} |
| 涨跌幅 | {change_pct:+.2f}% |
| 成交量 | {volume / 10000:.2f}万手 |
| 成交额 | {amount / 100000000:.2f}亿 |
| 换手率 | {f"{float(turnover):.2f}%" if turnover is not None and str(turnover) != "nan" else "N/A"} |
| 量比 | N/A |
| 市盈率(动态) | N/A |
| 市净率 | N/A |
| 总市值 | N/A |
| 流通市值 | N/A |

---

## 技术面分析

### 趋势判断
- **当前趋势**: {analysis["trend"]}
- **支撑位**: ¥{analysis["support_resistance"]["support"]}
- **阻力位**: ¥{analysis["support_resistance"]["resistance"]}
- **枢轴点**: ¥{analysis["support_resistance"]["pivot"]}

### 技术指标

| 指标 | 数值 | 信号 |
|------|------|------|
| MACD | DIF={analysis["indicators"]["MACD"]["DIF"]:.4f}, DEA={analysis["indicators"]["MACD"]["DEA"]:.4f} | {analysis["indicators"]["MACD"]["signal"]} |
| KDJ | K={analysis["indicators"]["KDJ"]["K"]:.2f}, D={analysis["indicators"]["KDJ"]["D"]:.2f}, J={analysis["indicators"]["KDJ"]["J"]:.2f} | {analysis["indicators"]["KDJ"]["signal"]} |
| RSI(14) | {analysis["indicators"]["RSI"]["value"]:.2f} | {analysis["indicators"]["RSI"]["signal"]} |
| BOLL | 上轨={analysis["indicators"]["BOLL"]["upper"]:.2f}, 中轨={analysis["indicators"]["BOLL"]["mid"]:.2f}, 下轨={analysis["indicators"]["BOLL"]["lower"]:.2f} | {analysis["indicators"]["BOLL"]["signal"]} |
| ATR(14) | {analysis["indicators"]["ATR"]:.2f} | 波动参考 |

---

## 综合评分

- **技术评分**: {analysis["score"]["score"]}/100
- **评级**: {analysis["score"]["rating"]}
- **星级**: {"⭐" * analysis["score"]["stars"]}

---

## 操作建议

"""

    score = analysis["score"]["score"]
    if score >= 70:
        report += """
✅ **建议买入**

当前技术面表现良好，各项指标偏多，可考虑逢低布局。

**注意事项**:
- 建议分批建仓，控制单只股票仓位不超过20%
- 设置止损位在支撑位下方3-5%
- 关注成交量变化，无量上涨需谨慎
"""
    elif score >= 50:
        report += """
⚠️ **建议观望**

当前技术面处于震荡整理阶段，方向不明确。

**注意事项**:
- 等待趋势明朗后再做决策
- 关注是否突破关键支撑/阻力位
- 可设置价格提醒，突破后再介入
"""
    else:
        report += """
❌ **建议回避**

当前技术面偏弱，多项指标发出卖出信号。

**注意事项**:
- 如持有建议逢高减仓
- 等待企稳信号出现后再考虑
- 关注下方支撑位是否有效
"""

    report += """
---

## 风险提示

⚠️ **免责声明**: 以上分析仅供参考，不构成投资建议。股市有风险，投资需谨慎。请根据自身风险承受能力做出投资决策。
"""

    return report


def generate_market_report() -> str:
    """生成每日市场报告"""

    # 获取指数数据
    indices = {
        "上证指数": "sh000001",
        "深证成指": "sz399001",
        "创业板指": "sz399006",
    }

    amount_yi_map = _get_index_amount_yi_map(list(indices.values()))

    index_data = []
    for name, code in indices.items():
        df = ak.stock_zh_index_daily(symbol=code)
        if len(df) < 2:
            continue
        latest = df.iloc[-1]
        prev = df.iloc[-2]
        change = (latest["close"] - prev["close"]) / prev["close"] * 100
        amount_yi = amount_yi_map.get(code)
        index_data.append(
            {
                "name": name,
                "close": latest["close"],
                "change": change,
                "amount_yi": float(amount_yi) if amount_yi is not None else None,
            }
        )

    # 获取板块数据（避免 Eastmoney board 接口不稳定）
    # 用资金流榜单近似“热点板块”，字段更稳定。
    try:
        concept_boards = ak.stock_fund_flow_concept()
        if "行业" in concept_boards.columns and "行业-涨跌幅" in concept_boards.columns:
            concept_boards = concept_boards.rename(
                columns={"行业": "板块名称", "行业-涨跌幅": "涨跌幅"}
            )
    except Exception:
        concept_boards = pd.DataFrame(columns=["板块名称", "涨跌幅"])

    try:
        industry_boards = ak.stock_fund_flow_industry()
        if (
            "行业" in industry_boards.columns
            and "行业-涨跌幅" in industry_boards.columns
        ):
            industry_boards = industry_boards.rename(
                columns={"行业": "板块名称", "行业-涨跌幅": "涨跌幅"}
            )
    except Exception:
        industry_boards = pd.DataFrame(columns=["板块名称", "涨跌幅"])

    top_concept = (
        concept_boards.nlargest(5, "涨跌幅") if len(concept_boards) else concept_boards
    )
    bottom_concept = (
        concept_boards.nsmallest(5, "涨跌幅") if len(concept_boards) else concept_boards
    )
    top_industry = (
        industry_boards.nlargest(5, "涨跌幅")
        if len(industry_boards)
        else industry_boards
    )

    # 获取涨跌停数据
    try:
        zt_count = len(ak.stock_zt_pool_em(date=datetime.now().strftime("%Y%m%d")))
    except:
        zt_count = "N/A"

    try:
        dt_count = len(ak.stock_zt_pool_dtgc_em(date=datetime.now().strftime("%Y%m%d")))
    except:
        dt_count = "N/A"

    # 获取全市场涨跌情况
    try:
        spot_df = ak.stock_zh_a_spot()
        if "涨跌幅" in spot_df.columns:
            up_count = len(spot_df[spot_df["涨跌幅"] > 0])
            down_count = len(spot_df[spot_df["涨跌幅"] < 0])
            flat_count = len(spot_df[spot_df["涨跌幅"] == 0])
            up_down_ratio = (
                f"{up_count / down_count:.2f}:1" if down_count > 0 else "N/A"
            )
        else:
            up_count = down_count = flat_count = up_down_ratio = "N/A"
    except Exception:
        up_count = down_count = flat_count = up_down_ratio = "N/A"

    report = f"""
# 每日市场报告

**日期**: {datetime.now().strftime("%Y-%m-%d")}
**生成时间**: {datetime.now().strftime("%H:%M:%S")}

---

## 大盘指数

| 指数 | 收盘点位 | 涨跌幅 | 成交额(亿) |
|------|----------|--------|------------|
"""

    for idx in index_data:
        amount_yi_display = (
            f"{idx['amount_yi']:.2f}" if idx["amount_yi"] is not None else "N/A"
        )
        report += f"| {idx['name']} | {idx['close']:.2f} | {idx['change']:+.2f}% | {amount_yi_display} |\n"

    report += f"""
---

## 市场情绪

- **上涨家数**: {up_count}
- **下跌家数**: {down_count}
- **平盘家数**: {flat_count}
- **涨跌比**: {up_down_ratio}
- **涨停家数**: {zt_count}
- **跌停家数**: {dt_count}

---

## 热门概念板块 TOP5

| 排名 | 板块名称 | 涨跌幅 | 最新价 | 换手率 |
|------|----------|--------|--------|--------|
"""

    for i, (_, row) in enumerate(top_concept.iterrows(), 1):
        report += f"| {i} | {row['板块名称']} | {row['涨跌幅']:+.2f}% | N/A | N/A |\n"

    report += f"""
---

## 热门行业板块 TOP5

| 排名 | 板块名称 | 涨跌幅 | 最新价 | 换手率 |
|------|----------|--------|--------|--------|
"""

    for i, (_, row) in enumerate(top_industry.iterrows(), 1):
        report += f"| {i} | {row['板块名称']} | {row['涨跌幅']:+.2f}% | N/A | N/A |\n"

    report += f"""
---

## 跌幅居前概念板块 TOP5

| 排名 | 板块名称 | 涨跌幅 |
|------|----------|--------|
"""

    for i, (_, row) in enumerate(bottom_concept.iterrows(), 1):
        report += f"| {i} | {row['板块名称']} | {row['涨跌幅']:+.2f}% |\n"

    report += """
---

## 市场总结

"""

    # 简单判断市场情绪
    sh_change = index_data[0]["change"]
    sentiment_score = 0

    if sh_change > 1:
        sentiment_score += 2
    elif sh_change > 0:
        sentiment_score += 1
    elif sh_change > -1:
        sentiment_score -= 1
    else:
        sentiment_score -= 2

    if up_down_ratio != "N/A":
        ratio_val = float(up_down_ratio.split(":")[0])
        if ratio_val > 2:
            sentiment_score += 2
        elif ratio_val > 1.5:
            sentiment_score += 1
        elif ratio_val > 1:
            sentiment_score += 0
        elif ratio_val > 0.67:
            sentiment_score -= 1
        else:
            sentiment_score -= 2

    if sentiment_score >= 3:
        report += "📈 **市场情绪**: 今日市场表现强势，做多情绪高涨。建议关注热点板块龙头，把握短线机会。\n"
    elif sentiment_score >= 1:
        report += (
            "📊 **市场情绪**: 今日市场小幅上涨，整体偏暖。可适度参与，但需控制仓位。\n"
        )
    elif sentiment_score >= -1:
        report += "📉 **市场情绪**: 今日市场小幅调整，情绪偏谨慎。建议观望为主，等待企稳信号。\n"
    else:
        report += (
            "⚠️ **市场情绪**: 今日市场大幅下跌，恐慌情绪蔓延。建议控制仓位，防范风险。\n"
        )

    report += """
---

## 风险提示

⚠️ **免责声明**: 以上分析仅供参考，不构成投资建议。股市有风险，投资需谨慎。
"""

    return report


if __name__ == "__main__":
    # 生成市场报告
    print(generate_market_report())

    print("\n" + "=" * 60 + "\n")

    # 生成个股报告示例
    print(generate_stock_report("000001"))
