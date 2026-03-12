#!/usr/bin/env python3
"""
A股市场数据获取模块
使用AKShare作为数据源
"""

import akshare as ak
import pandas as pd
from datetime import datetime, timedelta


def _get_index_amount_yi_map(indices: dict) -> dict:
    """Fetch index turnover amount (成交额) in 亿.

    Prefer Sina spot (more stable and includes 成交额). Fallback to Eastmoney spot.
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

    codes = list(indices.values())

    # 1) Sina index spot
    try:
        spot = ak.stock_zh_index_spot_sina()
        out = {code: _extract_amount(spot, code) for code in codes}
        if sum(v is not None for v in out.values()) >= max(1, len(codes) // 2):
            return out
    except Exception:
        pass

    # 2) Eastmoney index spot (may be flaky)
    try:
        spot = ak.stock_zh_index_spot_em()
        return {code: _extract_amount(spot, code) for code in codes}
    except Exception:
        return {code: None for code in codes}


def get_market_overview():
    """获取市场概览：主要指数行情"""
    indices = {
        "上证指数": "sh000001",
        "深证成指": "sz399001",
        "创业板指": "sz399006",
        "科创50": "sh000688",
        "沪深300": "sh000300",
        "中证500": "sh000905",
    }

    amount_yi_map = _get_index_amount_yi_map(indices)

    results = []
    for name, code in indices.items():
        try:
            df = ak.stock_zh_index_daily(symbol=code)
            if len(df) > 0:
                latest = df.iloc[-1]
                prev = df.iloc[-2] if len(df) > 1 else latest
                change_pct = (latest["close"] - prev["close"]) / prev["close"] * 100

                amount_yi = amount_yi_map.get(code)
                amount_yi_display = (
                    round(float(amount_yi), 2) if amount_yi is not None else None
                )
                results.append(
                    {
                        "指数名称": name,
                        "代码": code,
                        "最新点位": round(latest["close"], 2),
                        "涨跌幅": f"{change_pct:+.2f}%",
                        "成交额(亿)": amount_yi_display,
                    }
                )
        except Exception as e:
            print(f"获取{name}失败: {e}")

    return pd.DataFrame(results)


def get_all_stocks_realtime():
    """获取全部A股实时行情"""
    # Prefer non-Eastmoney endpoint to avoid frequent EM disconnects.
    # 新浪接口字段较少但稳定；需要更丰富字段时可在上层做数据补齐。
    # Note: Sina may temporarily block IP if called too frequently.
    df = ak.stock_zh_a_spot()
    return df


def get_stock_history(symbol: str, period: str = "daily", days: int = 120):
    """
    获取个股历史K线数据

    Args:
        symbol: 股票代码，如 "000001"
        period: K线周期 daily/weekly/monthly
        days: 获取天数
    """
    end_date = datetime.now().strftime("%Y%m%d")
    start_date = (datetime.now() - timedelta(days=days)).strftime("%Y%m%d")

    df = ak.stock_zh_a_hist(
        symbol=symbol,
        period=period,
        start_date=start_date,
        end_date=end_date,
        adjust="qfq",  # 前复权
    )
    return df


def get_concept_boards():
    """获取概念板块行情"""
    # Eastmoney board endpoints can be flaky; use non-EM alternatives.
    # Prefer fund-flow based concept ranking (provides 涨跌幅/资金流/领涨股等).
    # Fallback to THS concept list if needed.
    try:
        df = ak.stock_fund_flow_concept()
        # Align to common naming
        if "行业" in df.columns and "行业-涨跌幅" in df.columns:
            df = df.rename(columns={"行业": "板块名称", "行业-涨跌幅": "涨跌幅"})
        return df.sort_values("涨跌幅", ascending=False)
    except Exception:
        df = ak.stock_board_concept_name_ths()
        # THS list returns name/code only
        return df


def get_industry_boards():
    """获取行业板块行情"""
    # Eastmoney board endpoints can be flaky; use THS industry summary.
    try:
        df = ak.stock_board_industry_summary_ths()
        # Align to common naming
        if "板块" in df.columns and "涨跌幅" in df.columns:
            df = df.rename(columns={"板块": "板块名称"})
        return df.sort_values("涨跌幅", ascending=False)
    except Exception:
        df = ak.stock_fund_flow_industry()
        if "行业" in df.columns and "行业-涨跌幅" in df.columns:
            df = df.rename(columns={"行业": "板块名称", "行业-涨跌幅": "涨跌幅"})
        return df.sort_values("涨跌幅", ascending=False)


def get_board_stocks(board_name: str, board_type: str = "concept"):
    """获取板块成分股"""
    if board_type == "concept":
        df = ak.stock_board_concept_cons_em(symbol=board_name)
    else:
        df = ak.stock_board_industry_cons_em(symbol=board_name)
    return df


def get_limit_up_stocks():
    """获取涨停股票"""
    df = ak.stock_zt_pool_em(date=datetime.now().strftime("%Y%m%d"))
    return df


def get_limit_down_stocks():
    """获取跌停股票"""
    df = ak.stock_zt_pool_dtgc_em(date=datetime.now().strftime("%Y%m%d"))
    return df


def get_dragon_tiger_list(days: int = 5):
    """获取龙虎榜数据"""
    end_date = datetime.now().strftime("%Y%m%d")
    start_date = (datetime.now() - timedelta(days=days)).strftime("%Y%m%d")
    df = ak.stock_lhb_detail_em(start_date=start_date, end_date=end_date)
    return df


def get_north_money_flow():
    """获取北向资金流向"""
    # Use available Stock Connect summary endpoint.
    # Note: AkShare function set varies by version; prefer summary API.
    df = ak.stock_hsgt_fund_flow_summary_em()
    return df


def get_stock_fund_flow(symbol: str, market: str = "sh"):
    """
    获取个股资金流向

    Args:
        symbol: 股票代码
        market: sh/sz
    """
    df = ak.stock_individual_fund_flow(stock=symbol, market=market)
    return df


def get_financial_indicators(symbol: str):
    """获取财务指标"""
    df = ak.stock_financial_analysis_indicator(symbol=symbol)
    return df


def get_stock_info(symbol: str):
    """获取股票基本信息"""
    df = ak.stock_individual_info_em(symbol=symbol)
    return df


def get_earnings_forecast():
    """获取业绩预告"""
    df = ak.stock_yjyg_em()
    return df


if __name__ == "__main__":
    # 测试数据获取
    print("=== 市场概览 ===")
    print(get_market_overview())

    print("\n=== 概念板块 TOP10 ===")
    print(get_concept_boards().head(10))

    print("\n=== 行业板块 TOP10 ===")
    print(get_industry_boards().head(10))
