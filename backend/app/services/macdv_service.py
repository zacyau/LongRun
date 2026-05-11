"""
趋势信号服务模块

功能说明:
- 提供股票/指数的趋势分析服务
- 基于MACD-V指标和RSI14指标判断市场状态和买卖信号
- 支持批量查询多只股票的技术指标

数据来源: 新浪财经
核心指标:
    - MACD-V (MACD归一化指标): 衡量价格动能，将MACD值除以ATR进行标准化
    - RSI14: 相对强弱指数，14日周期，用于判断超买超卖状态

信号体系:
    - MACD-V趋势信号: 极度多头/强势多头/温和多头/中性/强势空头/极度空头
    - RSI信号: 极度超买/超买/中性偏强/中性/中性偏弱/超卖/极度超卖
    - 综合状态描述: 根据MACD-V和RSI的组合给出市场状态解读
"""
import math
import pandas as pd
import numpy as np
import requests
from datetime import datetime
from typing import Optional


# 常用股票/指数代码映射表
# 支持中文名称、6位代码、sh/sz前缀等多种输入格式自动识别
# 格式: "名称或代码": "新浪格式代码"
_COMMON_STOCKS = {
    "贵州茅台": "sh600519", "茅台": "sh600519",
    "中国平安": "sh601318", "平安": "sh601318",
    "招商银行": "sh600036",
    "万科A": "sz000002", "万科": "sz000002",
    "格力电器": "sz000651", "格力": "sz000651",
    "美的集团": "sz000333", "美的": "sz000333",
    "比亚迪": "sz002594",
    "宁德时代": "sz300750", "宁德": "sz300750",
    "中国中免": "sh601888", "中免": "sh601888",
    "隆基绿能": "sh601012", "隆基": "sh601012",
    "五粮液": "sz000858",
    "泸州老窖": "sz000568",
    "海天味业": "sh603288", "海天": "sh603288",
    "伊利股份": "sh600887", "伊利": "sh600887",
    "恒瑞医药": "sh600276", "恒瑞": "sh600276",
    "中信证券": "sh600030", "中信": "sh600030",
    "东方财富": "sz300059", "东财": "sz300059",
    "同花顺": "sz300033",
    "光大证券": "sh601788",
    "海通证券": "sh600837",
    "中信建投": "sh601066",
    "中国中车": "sh601766", "中车": "sh601766",
    "工商银行": "sh601398", "工行": "sh601398",
    "建设银行": "sh601939",
    "中国银行": "sh601988",
    "农业银行": "sh601288",
    "交通银行": "sh601328",
    "浦发银行": "sh600000",
    "兴业银行": "sh601166",
    "民生银行": "sh600016",
    "平安银行": "sz000001",
    "华夏银行": "sh600015",
    "招商证券": "sh600999",
    "华泰证券": "sh601688",
    "国泰君安": "sh601211",
    "中国神华": "sh601088",
    "中国石油": "sh601857",
    "中国石化": "sh600028",
    "中国建筑": "sh601668",
    "中国中铁": "sh601390",
    "中国铁建": "sh601186",
    "中国电建": "sh601669",
    "中国交建": "sh601800",
    "中国化学": "sh601117",
    "中国核电": "sh601985",
    "中国国航": "sh601111",
    "中国东航": "sh600115",
    "中国南航": "sh600029",
    "南方航空": "sh600029",
    "东方航空": "sh600115",
    "顺丰控股": "sz002352", "顺丰": "sz002352",
    "海康威视": "sz002415", "海康": "sz002415",
    "中兴通讯": "sz000063", "中兴": "sz000063",
    "三一重工": "sh600031", "三一": "sh600031",
    "中联重科": "sz000157",
    "徐工机械": "sz000425",
    "柳工": "sz000528",
    "宝钢股份": "sh600019", "宝钢": "sh600019",
    "鞍钢股份": "sz000898",
    "华菱钢铁": "sz000932",
    "新希望": "sz000876",
    "温氏股份": "sz300498",
    "牧原股份": "sz002714",
    "海大集团": "sz002311",
    "双汇发展": "sz000895",
    "用友网络": "sh600588", "用友": "sh600588",
    "宝信软件": "sh600845",
    "恒生电子": "sh600570",
    "广联达": "sz002410",
    "金山办公": "sh688111",
    "沪电股份": "sz002463",
    "深南电路": "sz002916",
    "生益科技": "sh600183",
    "三安光电": "sh600703", "三安": "sh600703",
    "三花智控": "sz002050", "三花": "sz002050",
    "拓普集团": "sh601689",
    "德赛西威": "sz002920",
    "华阳集团": "sz002906",
    "德赛电池": "sz000049",
    "欣旺达": "sz300207",
    "亿纬锂能": "sz300014",
    "赣锋锂业": "sz002460",
    "天齐锂业": "sz002466",
    "华友钴业": "sh603799",
    "洛阳钼业": "sh603993",
    "紫金矿业": "sh601899",
    "江西铜业": "sh600362",
    "中国铝业": "sh601600",
    "宝钛股份": "sh600456",
    "西部超导": "sh688122",
    "科创50": "sh000688",
    "沪深300": "sh000300",
    "中证500": "sh000905",
    "中证1000": "sh000852",
    "创业板": "sz399006",
    "上证指数": "sh000001",
    "深证成指": "sz399001",
    "国证A股": "sz399317",
    "上证50": "sh000016",
    "沪深000001": "sh000001",
    "深证000001": "sz399001",
}


def _normalize(raw: str) -> Optional[str]:
    """
    将用户输入的股票代码或名称规范化为新浪格式代码

    支持的输入格式:
    1. 中文名称：如"贵州茅台"、"茅台"
    2. 标准代码带前缀：如"sh600519"、"sz000002"
    3. 带点的格式：如"sh.600519"、"sz.000002"
    4. 纯数字代码：根据数字范围判断交易所

    股票代码规则:
    - 6开头：上海证券交易所（sh）
    - 5开头：上海证券交易所（sh）
    - 0或3开头：深圳证券交易所（sz）
    - 4或8开头：北京证券交易所（bj）

    返回值:
    - 成功：新浪格式代码如"sh600519"
    - 失败：None
    """
    raw = raw.strip()
    if not raw:
        return None

    # 1. 首先尝试从常用股票映射表中查找（支持中文名称）
    if raw.lower() in {k.lower() for k in _COMMON_STOCKS}:
        for k, v in _COMMON_STOCKS.items():
            if k.lower() == raw.lower():
                return v

    # 2. 处理带点的格式，如"sh.600519" -> "sh600519"
    if raw.startswith(("sh.", "sz.", "bj.")):
        code = raw.split(".", 1)[1]
        prefix = raw[:2]  # "sh"或"sz"或"bj"
        return f"{prefix}{code}"

    # 3. 处理纯数字代码，根据前缀判断交易所
    pure = raw.lstrip("shzxbjSHZXBJ./- ")
    if pure.isdigit():
        code = pure
        # 北京证券交易所：4开头（A股）、8开头（北交所）
        if code.startswith(("4", "8")):
            return f"bj{code}"
        # 上海证券交易所：6开头或5开头
        elif code.startswith("6") or code.startswith("5"):
            return f"sh{code}"
        # 深圳证券交易所：其他数字（主要是0、3开头）
        else:
            return f"sz{code}"

    # 4. 最后尝试通过新浪搜索API查询
    url = f"https://suggest3.sinajs.cn/suggest/type=11,12,13,14,15&key={raw}"
    headers = {"Referer": "https://finance.sina.com.cn"}
    try:
        resp = requests.get(url, headers=headers, timeout=5)
        text = resp.text.strip()
        if text and "=" in text:
            # 解析返回格式: var suggest_xx = "名称,代码,...";
            content = text.split("=", 1)[1].strip().strip('";\n')
            if content:
                fields = content.split(",")
                if len(fields) >= 3:
                    code = fields[2].strip()
                    if code.startswith(("sh", "sz", "bj")):
                        return code
    except Exception:
        pass

    return None


def _kline_code(sina_code: str) -> str:
    """
    从新浪完整代码中提取纯数字代码

    例如: "sh600519" -> "600519"
    """
    return sina_code[2:]


def _fetch_kline_sina(sina_code: str, datalen: int = 300) -> pd.DataFrame:
    """
    从新浪财经API获取K线数据

    参数说明:
        sina_code: 新浪格式的股票代码，如"sh600519"
        datalen: 请求的数据条数，默认300条（约1年多日线数据）

    返回值:
        pd.DataFrame，包含列：date、open、close、high、low、volume
    """
    url = (
        f"https://money.finance.sina.com.cn/quotes_service/api/json_v2.php"
        f"/CN_MarketData.getKLineData?symbol={sina_code}&scale=240&ma=5&datalen={datalen}"
    )
    resp = requests.get(url, timeout=15)
    resp.raise_for_status()
    data = resp.json()
    if not data:
        return pd.DataFrame()

    records = []
    for line in data:
        records.append({
            "date": line["day"],
            "open": float(line["open"]),
            "close": float(line["close"]),
            "high": float(line["high"]),
            "low": float(line["low"]),
            "volume": float(line["volume"]),
        })

    df = pd.DataFrame(records)
    df["date"] = pd.to_datetime(df["date"])
    df = df.sort_values("date").reset_index(drop=True)
    return df


def _fetch_realtime_sina(sina_code: str) -> dict:
    """
    从新浪财经获取股票实时行情数据

    参数说明:
        sina_code: 新浪格式的股票代码，如"sh600519"

    返回值:
        dict，包含字段：
        - name: 股票名称
        - current_price: 当前价格
        - yesterday_close: 昨日收盘价
        - today_open: 今日开盘价
        - today_high: 今日最高价
        - today_low: 今日最低价
        - date: 交易日期

    数据来源:
        新浪财经实时行情API (hq.sinajs.cn)
        返回数据格式: var hq_str_sh600519="名称,今日开盘价,昨日收盘价,当前价格,今日最高价,今日最低价,...";
    """
    url = f"https://hq.sinajs.cn/list={sina_code}"
    headers = {"Referer": "https://finance.sina.com.cn"}
    resp = requests.get(url, headers=headers, timeout=10)
    resp.raise_for_status()
    text = resp.text.strip()

    # 检查是否返回空数据
    if "=\"\"}" in text or "var hq_str" not in text:
        raise ValueError(f"未找到股票 {sina_code} 的实时数据")

    # 解析新浪返回的实时数据
    # 格式: var hq_str_sh600519="贵州茅台,1800.00,1790.00,1810.50,1820.00,1790.00,...2024-01-15";
    raw = text.split('"')[1]
    fields = raw.split(",")
    if len(fields) < 10:
        raise ValueError(f"股票 {sina_code} 数据格式异常")

    # 字段索引说明:
    # 0: 股票名称
    # 1: 今日开盘价
    # 2: 昨日收盘价
    # 3: 当前价格
    # 4: 今日最高价
    # 5: 今日最低价
    # 30: 交易日期（可能为空）

    name = fields[0]
    current_price = float(fields[3]) if fields[3] else 0.0
    yesterday_close = float(fields[2]) if fields[2] else 0.0
    today_open = float(fields[1]) if fields[1] else 0.0
    today_high = float(fields[4]) if fields[4] else 0.0
    today_low = float(fields[5]) if fields[5] else 0.0
    date_str = fields[30] if len(fields) > 30 and fields[30].strip() else ""

    return {
        "name": name,
        "current_price": current_price,
        "yesterday_close": yesterday_close,
        "today_open": today_open,
        "today_high": today_high,
        "today_low": today_low,
        "date": date_str,
    }


def _calculate_macdv(close: pd.Series, high: pd.Series, low: pd.Series) -> pd.Series:
    """
    计算MACD-V指标（MACD归一化版本）

    MACD-V = (EMA12 - EMA26) / ATR26 * 100

    计算步骤:
    1. 计算真实波幅（TR）：max(H-L, max(|H-PC|, |L-PC|))
       其中PC是前一日收盘价
    2. 计算ATR26：TR的26日移动平均
    3. 计算EMA12：收盘价的12日指数移动平均
    4. 计算EMA26：收盘价的26日指数移动平均
    5. 计算DIF：EMA12 - EMA26
    6. 计算MACD-V：DIF / ATR26 * 100

    参数说明:
        close: 收盘价序列
        high: 最高价序列
        low: 最低价序列

    返回值:
        MACD-V值序列，正值表示多头动能，负值表示空头动能

    信号解读:
        - MACD-V > 0: 多头趋势
        - MACD-V < 0: 空头趋势
        - |MACD-V| 越大，动能越强
    """
    # 数据不足26条时返回零值（无法计算有效指标）
    if len(close) < 26:
        return pd.Series([0.0] * len(close), index=close.index)

    # 前一日收盘价（用于计算真实波幅）
    prev_close = close.shift(1)

    # 计算真实波幅（True Range, TR）
    # TR = max(H-L, |H-PC|, |L-PC|)
    # 这里计算三个值的最大值
    mytr = np.maximum(
        high - low,  # 当日高低点差
        np.maximum((high - prev_close).abs(), (low - prev_close).abs())  # 跳空幅度
    )

    # 计算ATR26：TR的26日移动平均（用于标准化MACD）
    atr26 = mytr.rolling(window=26, min_periods=1).mean()

    # 计算EMA12和EMA26（指数移动平均线）
    ema12 = close.ewm(span=12, adjust=False).mean()
    ema26 = close.ewm(span=26, adjust=False).mean()

    # 计算DIF（差离值）：短期EMA与长期EMA的差值
    diff = ema12 - ema26

    # 归一化：将DIF除以ATR得到MACD-V
    # 乘以100是为了将数值放大，便于阅读和比较
    rawvalue = diff / atr26.replace(0, np.nan)  # 避免除零错误
    macdv = np.where(atr26 > 0, rawvalue * 100, 0.0)

    return pd.Series(macdv, index=close.index)


def _calculate_rsi14(close: pd.Series) -> pd.Series:
    """
    计算RSI14指标（相对强弱指数）

    RSI = 100 - (100 / (1 + RS))
    其中 RS = 平均涨幅 / 平均跌幅

    计算方法:
    - 使用Wilder平滑算法（指数移动平均）
    - 前14日使用简单平均初始化
    - 第15日开始使用平滑公式: AVG = (前一日AVG * 13 + 今日值) / 14

    参数说明:
        close: 收盘价序列

    返回值:
        RSI值序列，范围0-100

    信号解读:
        - RSI > 70: 超买区域
        - RSI < 30: 超卖区域
        - RSI = 50: 多空平衡
    """
    # 数据不足14条时返回中性值50
    if len(close) < 14:
        return pd.Series([50.0] * len(close), index=close.index)

    # 计算价格变动（今日收盘价 - 昨日收盘价）
    delta = close.diff()

    # 分离上涨和下跌部分
    gain = delta.where(delta > 0, 0.0)   # 只保留正变动（上涨）
    loss = (-delta).where(delta < 0, 0.0) # 只保留负变动（下跌），取绝对值

    # 初始化前14日的平均值（简单移动平均）
    avg_gain = gain.rolling(window=14, min_periods=14).mean().copy()
    avg_loss = loss.rolling(window=14, min_periods=14).mean().copy()

    # Wilder平滑算法：从第14日开始（索引14），逐日计算
    # 公式: AVG(i) = (AVG(i-1) * 13 + value(i)) / 14
    # 等价于 EMA(alpha=1/14)
    for i in range(14, len(gain)):
        avg_gain.iloc[i] = (avg_gain.iloc[i - 1] * 13 + gain.iloc[i]) / 14
        avg_loss.iloc[i] = (avg_loss.iloc[i - 1] * 13 + loss.iloc[i]) / 14

    # 计算RS（相对强度）
    rs = avg_gain / avg_loss.replace(0, np.nan)

    # 计算RSI
    # 公式: RSI = 100 - (100 / (1 + RS))
    # 当avg_loss为0时，RS为无穷大，RSI=100
    rsi = (100 - (100 / (1 + rs))).fillna(50.0)

    return rsi


def _get_macdv_trend(macdv: float) -> str:
    """
    根据MACD-V值判断趋势强度

    参数说明:
        macdv: MACD-V指标值

    返回值:
        趋势描述字符串

    分级标准:
        - 极度多头 (>150): 动能极强，可能处于狂热上涨阶段
        - 强势多头 (50-150): 上升趋势强劲
        - 温和多头 (0-50): 轻微多头，动能较弱
        - 中性 (-50-0): 多空平衡
        - 强势空头 (-150--50): 下降趋势强劲
        - 极度空头 (<-150): 动能极强，可能处于恐慌下跌阶段
    """
    if macdv > 150:
        return "极度多头"
    elif macdv > 50:
        return "强势多头"
    elif macdv > 0:
        return "温和多头"
    elif macdv >= -50:
        return "中性"
    elif macdv >= -150:
        return "强势空头"
    else:
        return "极度空头"


def _get_rsi_signal(rsi: float) -> str:
    """
    根据RSI值判断超买超卖状态

    参数说明:
        rsi: RSI指标值（0-100）

    返回值:
        信号描述字符串

    分级标准:
        - 极度超买 (>80): 市场可能过热，注意风险
        - 超买 (70-80): 上涨过快，可能调整
        - 中性偏强 (55-70): 多方占优但未过热
        - 中性 (45-55): 多空平衡
        - 中性偏弱 (30-45): 空方占优但未超卖
        - 超卖 (20-30): 下跌过快，可能反弹
        - 极度超卖 (<20): 市场可能恐慌
    """
    if rsi > 80:
        return "极度超买"
    elif rsi > 70:
        return "超买"
    elif rsi > 55:
        return "中性偏强"
    elif rsi >= 45:
        return "中性"
    elif rsi >= 30:
        return "中性偏弱"
    elif rsi >= 20:
        return "超卖"
    else:
        return "极度超卖"


# MACD-V趋势与RSI信号的组合状态描述映射表
# 格式: (MACD-V趋势, RSI信号) -> 状态描述
# 用于综合判断市场状态，识别潜在的交易机会和风险
_COMBINED_STATUS = {
    ("极度多头", "极度超买"): "动能与情绪均处极端狂热区域",
    ("极度多头", "超买"): "动能极端，价格已过热",
    ("极度多头", "中性偏强"): "动能极端，价格偏强但未过热",
    ("极度多头", "中性"): "动能极端，价格均衡",
    ("极度多头", "中性偏弱"): "动能极端，价格偏弱，背离",
    ("极度多头", "超卖"): "动能极端，价格超卖，严重背离",
    ("极度多头", "极度超卖"): "动能极端，价格极度超卖，强烈背离",
    ("强势多头", "极度超买"): "动能强势，价格极度超买",
    ("强势多头", "超买"): "趋势强势，价格已过热",
    ("强势多头", "中性偏强"): "健康上升趋势，未过热",
    ("强势多头", "中性"): "趋势向上，价格均衡",
    ("强势多头", "中性偏弱"): "强势趋势中出现回调",
    ("强势多头", "超卖"): "强势上升中出现深幅回调",
    ("强势多头", "极度超卖"): "强势上升中出现极端回调",
    ("温和多头", "极度超买"): "动能温和，价格极度超买",
    ("温和多头", "超买"): "动能温和，价格过热",
    ("温和多头", "中性偏强"): "震荡偏多，价格偏强",
    ("温和多头", "中性"): "震荡偏多，价格均衡",
    ("温和多头", "中性偏弱"): "震荡偏多，价格偏弱",
    ("温和多头", "超卖"): "震荡偏多，超跌反弹结构",
    ("温和多头", "极度超卖"): "震荡偏多，极度超跌",
    ("中性", "极度超买"): "方向不明，价格极度超买",
    ("中性", "超买"): "方向不明，价格过热",
    ("中性", "中性偏强"): "方向不明，价格偏强",
    ("中性", "中性"): "无方向盘整，动能与情绪均衡",
    ("中性", "中性偏弱"): "方向不明，价格偏弱",
    ("中性", "超卖"): "方向不明，价格过冷",
    ("中性", "极度超卖"): "方向不明，价格极度超卖",
    ("强势空头", "极度超买"): "强势下跌中出现极端反弹",
    ("强势空头", "超买"): "强势下跌中出现急速反弹",
    ("强势空头", "中性偏强"): "强势下跌中出现反弹",
    ("强势空头", "中性"): "趋势向下，价格均衡",
    ("强势空头", "中性偏弱"): "健康下跌趋势，未超跌",
    ("强势空头", "超卖"): "趋势弱势，价格已过冷",
    ("强势空头", "极度超卖"): "趋势弱势，价格极度过冷",
    ("极度空头", "极度超买"): "动能极端，价格极度超买，强烈背离",
    ("极度空头", "超买"): "动能极端，价格超买，严重背离",
    ("极度空头", "中性偏强"): "动能极端，价格偏强，背离",
    ("极度空头", "中性"): "动能极端，价格均衡",
    ("极度空头", "中性偏弱"): "动能极端，价格偏弱但未过冷",
    ("极度空头", "超卖"): "动能极端，价格已过冷",
    ("极度空头", "极度超卖"): "动能与情绪均处极端恐慌区域",
}


def _get_status_description(macdv_trend: str, rsi_signal: str) -> str:
    """
    根据MACD-V趋势和RSI信号获取综合状态描述

    参数说明:
        macdv_trend: MACD-V趋势描述（从_get_macdv_trend获取）
        rsi_signal: RSI信号描述（从_get_rsi_signal获取）

    返回值:
        组合后的市场状态描述字符串
        如果组合不在预定义表中，返回"状态待定"
    """
    return _COMBINED_STATUS.get((macdv_trend, rsi_signal), "状态待定")


def query_single_stock(code_or_name: str) -> dict:
    """
    查询单只股票的技术指标和趋势信号

    参数说明:
        code_or_name: 股票代码或名称，支持多种格式

    返回值:
        dict，包含字段：
        - stock_name: 股票名称
        - stock_code: 股票代码（纯数字部分）
        - trade_date: 交易日期
        - current_price: 当前价格
        - macdv: MACD-V指标值
        - rsi14: RSI14指标值
        - macdv_trend: MACD-V趋势描述
        - rsi14_signal: RSI信号描述
        - status_description: 综合状态描述
        - error: 错误信息（无错误时为None）

    计算流程:
    1. 规范化输入代码
    2. 获取300条历史K线数据
    3. 计算MACD-V和RSI14指标
    4. 获取实时行情数据
    5. 生成趋势信号和状态描述
    """
    try:
        # 1. 规范化输入代码
        sina_code = _normalize(code_or_name)
        if not sina_code:
            raise ValueError(f"无法解析股票代码: {code_or_name}")

        # 2. 获取K线数据（需要至少26条数据计算MACD-V）
        df = _fetch_kline_sina(sina_code, datalen=300)
        if df.empty:
            raise ValueError(f"K线数据为空")
        if len(df) < 26:
            raise ValueError(f"数据不足（{len(df)}条），需要至少26条数据")

        # 3. 提取价格数据
        close = df["close"].astype(float)
        high = df["high"].astype(float)
        low = df["low"].astype(float)

        # 4. 计算技术指标
        macdv_series = _calculate_macdv(close, high, low)
        rsi_series = _calculate_rsi14(close)

        # 获取最新指标值
        latest_macdv = float(macdv_series.iloc[-1])
        latest_rsi = float(rsi_series.iloc[-1])

        # 5. 获取实时行情
        rt = _fetch_realtime_sina(sina_code)
        # 如果实时日期为空，使用K线数据中最新日期
        trade_date = rt["date"] if rt["date"] else df["date"].max().strftime("%Y-%m-%d")
        # 如果实时价格为0，使用K线收盘价
        current_price = rt["current_price"] if rt["current_price"] > 0 else float(df.iloc[-1]["close"])

        # 提取股票代码和名称
        stock_code = sina_code[2:]
        stock_name = rt["name"] if rt["name"] else stock_code

        # 6. 生成趋势信号
        macdv_trend = _get_macdv_trend(latest_macdv)
        rsi_signal = _get_rsi_signal(latest_rsi)

        return {
            "stock_name": stock_name,
            "stock_code": stock_code,
            "trade_date": trade_date,
            "current_price": round(current_price, 2),
            "macdv": round(latest_macdv, 2),
            "rsi14": round(latest_rsi, 2),
            "macdv_trend": macdv_trend,
            "rsi14_signal": rsi_signal,
            "status_description": _get_status_description(macdv_trend, rsi_signal),
            "error": None,
        }

    except Exception as e:
        # 发生错误时返回错误信息
        return {
            "stock_name": code_or_name.strip(),
            "stock_code": "",
            "trade_date": "",
            "current_price": 0.0,
            "macdv": 0.0,
            "rsi14": 0.0,
            "macdv_trend": "中性",
            "rsi14_signal": "中性",
            "status_description": None,
            "error": str(e),
        }


def query_batch_stocks(queries: list[str]) -> dict:
    """
    批量查询多只股票的技术指标

    参数说明:
        queries: 股票代码或名称列表

    返回值:
        dict，包含字段：
        - results: 每只股票的查询结果列表
        - updated_at: 查询时间

    说明:
        结果按RSI14值降序排列（RSI高的排在前面）
        发生错误的股票RSI值视为-999以排在最后
    """
    results = [query_single_stock(q) for q in queries]
    # 按RSI14降序排列，错误的排在最后
    results.sort(key=lambda r: r.get("rsi14", 0.0) if not r.get("error") else -999, reverse=True)
    return {
        "results": results,
        "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }