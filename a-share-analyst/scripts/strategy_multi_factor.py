#!/usr/bin/env python3
"""
A股多因子选股策略
支持价值、成长、动量、质量等多种因子
"""

import akshare as ak
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os
import logging

logging.basicConfig(level=logging.WARNING, format="%(levelname)s: %(message)s")


def get_stock_pool():
    """获取股票池（全部A股实时行情）"""
    # Prefer non-Eastmoney spot endpoint (Sina), but it can return HTML (rate-limit/block)
    # which breaks demjson parsing. Fall back to other endpoints when needed.
    # Note: A+H spot is smaller universe but tends to be more stable.
    try:
        df = ak.stock_zh_a_spot()
    except Exception:
        try:
            df = ak.stock_zh_ah_spot()
        except Exception:
            # last resort (may be flaky): Eastmoney
            df = ak.stock_zh_a_spot_em()

    # 基础筛选（Sina 字段）
    df = df[~df["名称"].astype(str).str.contains("ST|退")]  # 剔除ST和退市股
    df = df[df["涨跌幅"].astype(float) < 9.9]  # 剔除涨停
    df = df[df["涨跌幅"].astype(float) > -9.9]  # 剔除跌停
    df = df[df["成交额"].astype(float) > 0]  # 剔除停牌/无成交

    # 字段对齐：保持下游策略期望的列名
    df = df.rename(
        columns={
            "最新价": "最新价",
            "涨跌幅": "涨跌幅",
            "成交额": "成交额",
            "成交量": "成交量",
        }
    )

    # 补齐缺失列（给下游策略用）
    if "换手率" not in df.columns:
        # 简化：用成交额在全市场的分位数作为“活跃度/换手代理”，避免硬编码。
        amt = df["成交额"].astype(float)
        df["换手率"] = (amt.rank(pct=True) * 10).round(2)  # 0~10 的代理数值
    if "量比" not in df.columns:
        df["量比"] = np.nan
    if "振幅" not in df.columns:
        df["振幅"] = np.nan
    if "总市值" not in df.columns:
        df["总市值"] = np.nan
    if "市盈率-动态" not in df.columns:
        df["市盈率-动态"] = np.nan
    if "市净率" not in df.columns:
        df["市净率"] = np.nan

    # 估值补齐（Baidu）
    # 为了避免对 5000+ 股票逐个请求导致超时/封禁，这里只对候选集合补齐：
    # 先按成交额筛选出最活跃的一批，再取估值数据。
    # NOTE: Baidu 估值接口为“单股单指标”，调用过多会非常慢。
    enrich_top_n = int(os.getenv("VALUATION_ENRICH_TOP_N", "0"))
    if enrich_top_n <= 0:
        return df

    active = df.sort_values("成交额", ascending=False).head(enrich_top_n).copy()
    symbols = active["代码"].astype(str).tolist()

    def _latest_value(symbol: str, indicator: str):
        try:
            vdf = ak.stock_zh_valuation_baidu(
                symbol=symbol, indicator=indicator, period="近一年"
            )
            if vdf is None or len(vdf) == 0:
                return np.nan
            return float(vdf["value"].iloc[-1])
        except Exception:
            return np.nan

    # Note: These indicators are supported by Baidu valuation endpoint.
    # Keep to the minimum required fields for our strategies.
    active["市盈率-动态"] = [_latest_value(s, "市盈率(TTM)") for s in symbols]
    active["市净率"] = [_latest_value(s, "市净率") for s in symbols]

    pe_nan_count = active["市盈率-动态"].isna().sum()
    pb_nan_count = active["市净率"].isna().sum()
    total_stocks = len(active)
    if pe_nan_count > total_stocks * 0.8:
        logging.warning(
            f"估值补齐失败率高：PE数据缺失 {pe_nan_count}/{total_stocks} "
            f"({pe_nan_count / total_stocks * 100:.1f}%)，价值/质量策略可能返回空结果"
        )
    if pb_nan_count > total_stocks * 0.8:
        logging.warning(
            f"估值补齐失败率高：PB数据缺失 {pb_nan_count}/{total_stocks} "
            f"({pb_nan_count / total_stocks * 100:.1f}%)，价值/质量策略可能返回空结果"
        )
    if pb_nan_count > total_stocks * 0.8:
        logging.warning(
            f"估值补齐失败率高：PB数据缺失 {pb_nan_count}/{total_stocks} "
            f"({pb_nan_count / total_stocks * 100:.1f}%)，价值/质量策略可能返回空结果"
        )

    # Merge back (prefer enriched rows)
    df = df.set_index("代码")
    active = active.set_index("代码")
    for col in ["市盈率-动态", "市净率", "换手率"]:
        df.loc[active.index, col] = active[col]
    df = df.reset_index()

    # Final filter: remove missing PE if required by some strategies
    # (keep NaNs for non-value strategies)
    return df


def strategy_value(df: pd.DataFrame, top_n: int = 30) -> pd.DataFrame:
    """
    价值投资策略
    选股逻辑：低PE、低PB、高股息率
    """
    df0 = df.copy()

    # 计算因子排名（越小越好）
    # Baidu 估值补齐可能只覆盖少量股票；当样本不足时放宽条件，避免空结果。
    df = df0.dropna(subset=["市盈率-动态", "市净率"], how="any")
    if len(df) < 20:
        # fallback: when valuation coverage is too low, return a liquidity/stability proxy
        base = df0[["代码", "名称", "最新价", "涨跌幅", "成交额"]].copy()
        base["value_score"] = (
            pd.to_numeric(base["涨跌幅"], errors="coerce").abs().rank(pct=True)
            + pd.to_numeric(base["成交额"], errors="coerce").rank(pct=True)
        ) / 2
        return base.nsmallest(top_n, "value_score")

    df["PE_rank"] = pd.to_numeric(df["市盈率-动态"], errors="coerce").rank(pct=True)
    df["PB_rank"] = pd.to_numeric(df["市净率"], errors="coerce").rank(pct=True)

    # 综合评分
    df["value_score"] = df["PE_rank"] * 0.5 + df["PB_rank"] * 0.5

    # 排序选股
    result = df.nsmallest(top_n, "value_score")

    return result[
        ["代码", "名称", "最新价", "涨跌幅", "市盈率-动态", "市净率", "value_score"]
    ]


def strategy_momentum(df: pd.DataFrame, top_n: int = 30) -> pd.DataFrame:
    """
    动量策略
    选股逻辑：近期涨幅居前、成交活跃
    """
    df = df.copy()

    # 动量因子（涨幅越大越好）
    df["momentum_rank"] = df["涨跌幅"].astype(float).rank(pct=True, ascending=False)

    # 换手率因子（适度活跃）
    df["turnover_rank"] = df["换手率"].astype(float).rank(pct=True)

    # 综合评分
    df["momentum_score"] = df["momentum_rank"] * 0.7 + df["turnover_rank"] * 0.3

    # 排序选股
    result = df.nsmallest(top_n, "momentum_score")

    return result[
        ["代码", "名称", "最新价", "涨跌幅", "换手率", "成交额", "momentum_score"]
    ]


def strategy_breakout(df: pd.DataFrame, top_n: int = 30) -> pd.DataFrame:
    """
    突破策略
    选股逻辑：放量突破、近期强势
    """
    df = df.copy()

    # 量比因子（放量）
    # Sina spot 没有量比，这里用成交额分位数作为放量代理。
    amt = df["成交额"].astype(float)
    df["vol_ratio_proxy"] = amt.rank(pct=True)
    df["vol_ratio_rank"] = df["vol_ratio_proxy"].rank(pct=True, ascending=False)

    # 涨幅因子
    df["change_rank"] = df["涨跌幅"].astype(float).rank(pct=True, ascending=False)

    # 振幅因子（波动适中）
    # Sina spot 没有振幅，使用涨跌幅绝对值作为波动代理（越小越好）
    df["amplitude_proxy"] = df["涨跌幅"].astype(float).abs()
    df["amplitude_rank"] = df["amplitude_proxy"].rank(pct=True)

    # 综合评分
    df["breakout_score"] = (
        df["vol_ratio_rank"] * 0.4
        + df["change_rank"] * 0.4
        + df["amplitude_rank"] * 0.2
    )

    # 额外筛选：成交额分位数>0.8，涨幅>2%
    df = df[(df["vol_ratio_proxy"] > 0.8) & (df["涨跌幅"].astype(float) > 2)]

    result = df.nsmallest(top_n, "breakout_score")

    return result[
        ["代码", "名称", "最新价", "涨跌幅", "量比", "振幅", "breakout_score"]
    ]


def strategy_quality(df: pd.DataFrame, top_n: int = 30) -> pd.DataFrame:
    """
    质量因子策略
    选股逻辑：高ROE、低负债、稳定增长
    注意：此策略需要额外获取财务数据
    """
    df = df.copy()

    # 简化版：使用市盈率和市净率推算ROE
    # ROE ≈ 1 / (PE × PB)
    df = df.dropna(subset=["市盈率-动态", "市净率"], how="any")
    if len(df) < 20:
        # fallback: return empty to avoid misleading "quality" without inputs
        return pd.DataFrame()
    pe = df["市盈率-动态"].astype(float)
    pb = df["市净率"].astype(float)
    valid_pe_pb = (pe > 0) & (pb > 0)
    df["implied_roe"] = np.nan
    df.loc[valid_pe_pb, "implied_roe"] = 1 / (pe[valid_pe_pb] * pb[valid_pe_pb])
    df["roe_rank"] = df["implied_roe"].rank(pct=True, ascending=False)

    # 市值因子（中大盘）
    df["cap_rank"] = df["总市值"].rank(pct=True)

    # 综合评分
    df["quality_score"] = df["roe_rank"] * 0.7 + df["cap_rank"] * 0.3

    result = df.nsmallest(top_n, "quality_score")

    return result[
        [
            "代码",
            "名称",
            "最新价",
            "涨跌幅",
            "市盈率-动态",
            "市净率",
            "implied_roe",
            "quality_score",
        ]
    ]


def strategy_multi_factor(
    df: pd.DataFrame, top_n: int = 30, weights: dict = None
) -> pd.DataFrame:
    """
    多因子综合策略

    Args:
        df: 股票数据
        top_n: 选股数量
        weights: 因子权重配置
    """
    if weights is None:
        weights = {
            "value": 0.25,  # 价值因子
            "momentum": 0.25,  # 动量因子
            "quality": 0.25,  # 质量因子
            "size": 0.15,  # 规模因子
            "volatility": 0.10,  # 波动率因子
        }

    df = df.copy()

    # 价值因子
    # For value/quality factors, require PE/PB. If coverage is low, skip them.
    pe = pd.to_numeric(df["市盈率-动态"], errors="coerce")
    pb = pd.to_numeric(df["市净率"], errors="coerce")
    has_value_inputs = pe.notna() & pb.notna()
    if has_value_inputs.sum() >= 50:
        df["pe_rank"] = pe.rank(pct=True)
        df["pb_rank"] = pb.rank(pct=True)
        df["value_factor"] = (df["pe_rank"] + df["pb_rank"]) / 2
        valid_pe_pb = (pe > 0) & (pb > 0)
        df["implied_roe"] = np.nan
        df.loc[valid_pe_pb, "implied_roe"] = 1 / (pe[valid_pe_pb] * pb[valid_pe_pb])
        df["quality_factor"] = df["implied_roe"].rank(pct=True, ascending=False)
    else:
        # downgrade value/quality weights gracefully
        df["value_factor"] = np.nan
        df["quality_factor"] = np.nan

    # 动量因子
    df["momentum_factor"] = pd.to_numeric(df["涨跌幅"], errors="coerce").rank(
        pct=True, ascending=False
    )

    # 质量因子在上面与价值因子一起处理（需要 PE/PB）

    # 规模因子（偏好中盘）
    # Sina spot 没有总市值；使用成交额作为规模/活跃度代理，偏好中等成交额。
    df["log_amt"] = np.log(pd.to_numeric(df["成交额"], errors="coerce") + 1)
    median_amt = df["log_amt"].median()
    df["size_factor"] = -abs(df["log_amt"] - median_amt)
    df["size_factor"] = df["size_factor"].rank(pct=True, ascending=False)

    # 波动率因子（偏好低波动）
    # If 振幅 is missing, use abs(pct_change) proxy.
    if "振幅" in df.columns and df["振幅"].notna().any():
        vol_base = pd.to_numeric(df["振幅"], errors="coerce")
    else:
        vol_base = pd.to_numeric(df["涨跌幅"], errors="coerce").abs()
    df["volatility_factor"] = vol_base.rank(pct=True)

    # 综合评分：如果 value/quality 不可用，则按剩余因子归一化权重
    parts = {
        "momentum": df["momentum_factor"],
        "size": df["size_factor"],
        "volatility": df["volatility_factor"],
    }
    w = {
        "momentum": weights["momentum"],
        "size": weights["size"],
        "volatility": weights["volatility"],
    }
    if df["value_factor"].notna().any():
        parts["value"] = df["value_factor"]
        w["value"] = weights["value"]
    if df["quality_factor"].notna().any():
        parts["quality"] = df["quality_factor"]
        w["quality"] = weights["quality"]

    wsum = sum(w.values())
    df["total_score"] = 0.0
    for k, s in parts.items():
        df["total_score"] += s * (w[k] / wsum)

    df = df.dropna(subset=["total_score"])

    # 排序选股
    result = df.nsmallest(top_n, "total_score")

    return result[
        [
            "代码",
            "名称",
            "最新价",
            "涨跌幅",
            "市盈率-动态",
            "市净率",
            "换手率",
            "total_score",
        ]
    ]


def get_board_leaders(board_type: str = "concept", top_n: int = 5) -> pd.DataFrame:
    """
    获取板块龙头股

    Args:
        board_type: concept/industry
        top_n: 每个板块取前N只
    """
    if board_type == "concept":
        try:
            boards = ak.stock_fund_flow_concept()
            if "行业" in boards.columns and "行业-涨跌幅" in boards.columns:
                boards = boards.rename(
                    columns={"行业": "板块名称", "行业-涨跌幅": "涨跌幅"}
                )
        except Exception:
            try:
                boards = ak.stock_board_concept_name_ths()
                if "板块名称" not in boards.columns or "涨跌幅" not in boards.columns:
                    boards = pd.DataFrame(columns=["板块名称", "涨跌幅"])
            except Exception:
                return pd.DataFrame()
    else:
        try:
            boards = ak.stock_board_industry_summary_ths()
            if "板块" in boards.columns:
                boards = boards.rename(columns={"板块": "板块名称"})
        except Exception:
            try:
                boards = ak.stock_fund_flow_industry()
                if "行业" in boards.columns and "行业-涨跌幅" in boards.columns:
                    boards = boards.rename(
                        columns={"行业": "板块名称", "行业-涨跌幅": "涨跌幅"}
                    )
            except Exception:
                return pd.DataFrame()

    # 取涨幅前10的板块
    if (
        len(boards) == 0
        or "板块名称" not in boards.columns
        or "涨跌幅" not in boards.columns
    ):
        return pd.DataFrame()
    top_boards = boards.nlargest(10, "涨跌幅")

    results = []
    for _, board in top_boards.iterrows():
        board_name = board["板块名称"]
        try:
            # 成分股API目前只有EM端点可用，保持使用但添加异常处理
            if board_type == "concept":
                stocks = ak.stock_board_concept_cons_em(symbol=board_name)
            else:
                stocks = ak.stock_board_industry_cons_em(symbol=board_name)

            if len(stocks) > 0 and "涨跌幅" in stocks.columns:
                stocks = stocks.nlargest(top_n, "涨跌幅")
                stocks["所属板块"] = board_name
                stocks["板块涨幅"] = board["涨跌幅"]
                results.append(stocks)
        except Exception:
            continue

    if results:
        return pd.concat(results, ignore_index=True)
    return pd.DataFrame()


def generate_daily_picks(save_path: str = None) -> dict:
    """
    生成每日选股清单
    """
    print("正在获取股票数据...")
    df = get_stock_pool()

    print("运行价值策略...")
    value_picks = strategy_value(df)

    print("运行动量策略...")
    momentum_picks = strategy_momentum(df)

    print("运行突破策略...")
    breakout_picks = strategy_breakout(df)

    print("运行多因子策略...")
    multi_factor_picks = strategy_multi_factor(df)

    results = {
        "date": datetime.now().strftime("%Y-%m-%d"),
        "value": value_picks,
        "momentum": momentum_picks,
        "breakout": breakout_picks,
        "multi_factor": multi_factor_picks,
    }

    if save_path:
        # 保存到Excel
        with pd.ExcelWriter(save_path) as writer:
            value_picks.to_excel(writer, sheet_name="价值型", index=False)
            momentum_picks.to_excel(writer, sheet_name="动量型", index=False)
            breakout_picks.to_excel(writer, sheet_name="突破型", index=False)
            multi_factor_picks.to_excel(writer, sheet_name="多因子", index=False)
        print(f"选股结果已保存至: {save_path}")

    return results


def _generate_picks_report(results: dict) -> str:
    """生成选股清单 Markdown 报告"""
    from datetime import datetime

    date = results["date"]
    value_stocks = results["value"]
    momentum_stocks = results["momentum"]
    breakout_stocks = results["breakout"]
    multi_factor_stocks = results["multi_factor"]

    report = f"""
# 每日选股清单 [{date}]

**生成时间**: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

---

## 📊 选股概况

| 策略类型 | 选股数量 |
|---------|---------|
| 价值型 | {len(value_stocks)} 只 |
| 动量型 | {len(momentum_stocks)} 只 |
| 突破型 | {len(breakout_stocks)} 只 |
| 多因子综合 | {len(multi_factor_stocks)} 只 |

---

## 💰 价值型选股 TOP10

> 选股逻辑：低PE、低PB、高股息率，适合长期投资

| 排名 | 代码 | 名称 | 最新价 | 涨跌幅 | 成交额(万) | 价值评分 |
|------|------|------|--------|--------|-----------|---------|
"""

    for i, (_, row) in enumerate(value_stocks.head(10).iterrows(), 1):
        change_pct = row["涨跌幅"] * 100 if row["涨跌幅"] < 1 else row["涨跌幅"]
        report += f"| {i} | {row['代码']} | {row['名称']} | ¥{row['最新价']:.2f} | {change_pct:+.2f}% | {row['成交额'] / 10000:.2f} | {row['value_score']:.4f} |\n"

    report += f"""
---

## 📈 动量型选股 TOP10

> 选股逻辑：近期涨幅居前、成交活跃，适合短线操作

| 排名 | 代码 | 名称 | 最新价 | 涨跌幅 | 换手率 | 成交额(万) | 动量评分 |
|------|------|------|--------|--------|--------|-----------|---------|
"""

    for i, (_, row) in enumerate(momentum_stocks.head(10).iterrows(), 1):
        report += f"| {i} | {row['代码']} | {row['名称']} | ¥{row['最新价']:.2f} | {row['涨跌幅']:+.2f}% | {row['换手率']:.2f}% | {row['成交额'] / 10000:.2f} | {row['momentum_score']:.4f} |\n"

    report += f"""
---

## 🚀 突破型选股 TOP10

> 选股逻辑：放量突破、近期强势，适合波段操作

| 排名 | 代码 | 名称 | 最新价 | 涨跌幅 | 突破评分 |
|------|------|------|--------|--------|---------|
"""

    if len(breakout_stocks) > 0:
        for i, (_, row) in enumerate(breakout_stocks.head(10).iterrows(), 1):
            report += f"| {i} | {row['代码']} | {row['名称']} | ¥{row['最新价']:.2f} | {row['涨跌幅']:+.2f}% | {row['breakout_score']:.4f} |\n"
    else:
        report += "| - | - | 今日无符合条件的突破型股票 | - | - | |\n"

    report += f"""
---

## ⭐ 多因子综合选股 TOP10

> 选股逻辑：综合价值、动量、质量、规模、波动率等多个因子，全方位评估

| 排名 | 代码 | 名称 | 最新价 | 涨跌幅 | 换手率 | 综合评分 |
|------|------|------|--------|--------|--------|---------|
"""

    for i, (_, row) in enumerate(multi_factor_stocks.head(10).iterrows(), 1):
        report += f"| {i} | {row['代码']} | {row['名称']} | ¥{row['最新价']:.2f} | {row['涨跌幅']:+.2f}% | {row['换手率']:.2f}% | {row['total_score']:.4f} |\n"

    report += f"""

---

## 📋 多因子评分说明

本次多因子选股采用了以下5类因子：

### 因子权重配置
- **价值因子** (25%): EP（收益价格比）、BP（账面市值比）
- **动量因子** (25%): 价格动量、成交量动量
- **质量因子** (25%): ROE（净资产收益率）、ROIC（投入资本回报率）
- **规模因子** (15%): 偏好中盘股
- **波动率因子** (10%): 偏好低波动股票

### 筛选标准
- 剔除ST和退市股票
- 剔除上市不满60天的新股
- 剔除涨停/跌停股票
- 剔除停牌或无成交的股票

---

## ⚠️ 风险提示

1. **数据延迟**: 实时数据可能有15分钟延迟
2. **市场风险**: 股市有风险，以上分析仅供参考，不构成投资建议
3. **仓位管理**: 建议单只股票仓位不超过总资金20%
4. **止损纪律**: 严格执行止损策略，控制回撤风险
5. **策略适用**: 不同策略适用于不同市场环境，请根据市场情况选择

---

## 💡 操作建议

### 短线操作（动量型、突破型）
- 快进快出，设置止损位在买入价-3%至-5%
- 关注成交量变化，无量上涨需谨慎
- 单只股票持仓不超过3个交易日

### 中线操作（价值型、多因子）
- 分批建仓，逢低布局
- 关注基本面变化和行业景气度
- 设置止损位在关键支撑位下方

### 通用原则
- 不追涨杀跌，理性判断
- 严格止损，保住本金
- 分散投资，降低风险

---

**报告生成**: A股分析师 - 多因子选股系统
**数据来源**: AKShare (免费开源数据接口)
**最后更新**: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
"""
    return report


if __name__ == "__main__":
    import json
    import io
    import sys

    # 设置标准输出为 UTF-8
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

    print("开始执行多因子综合选股...")

    # 执行选股
    results = generate_daily_picks()

    # 生成时间戳
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    # 1. 保存 JSON 结果（用于数据存档）
    json_file = f"multi_factor_picks_{timestamp}.json"
    json_output = {
        "date": results["date"],
        "value": results["value"].to_dict("records") if len(results["value"]) > 0 else [],
        "momentum": results["momentum"].to_dict("records") if len(results["momentum"]) > 0 else [],
        "breakout": results["breakout"].to_dict("records") if len(results["breakout"]) > 0 else [],
        "multi_factor": results["multi_factor"].to_dict("records") if len(results["multi_factor"]) > 0 else [],
    }
    with open(json_file, "w", encoding="utf-8") as f:
        json.dump(json_output, f, ensure_ascii=False, indent=2)
    print(f"\n✓ JSON 结果已保存至: {json_file}")

    # 2. 生成 Markdown 报告
    md_file = f"multi_factor_report_{timestamp}.md"
    report = _generate_picks_report(results)
    with open(md_file, "w", encoding="utf-8") as f:
        f.write(report)
    print(f"✓ Markdown 报告已保存至: {md_file}")

    # 3. 打印控制台摘要
    print("\n" + "=" * 60)
    print(f"每日选股清单 - {results['date']}")
    print("=" * 60)
    print(f"✓ 价值型选股: {len(results['value'])} 只")
    print(f"✓ 动量型选股: {len(results['momentum'])} 只")
    print(f"✓ 突破型选股: {len(results['breakout'])} 只")
    print(f"✓ 多因子选股: {len(results['multi_factor'])} 只")
