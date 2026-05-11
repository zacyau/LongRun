"""
技术指标计算服务模块

功能说明:
- 提供各种技术指标的计算功能
- 主要用于股票/指数的技术分析

支持的指标:
1. SMA (简单移动平均线)
   - 计算指定窗口的收盘价简单平均值
   - 用于判断价格趋势方向

2. 包络线 (Envelope Bands)
   - 基于SMA的百分比通道
   - 上轨 = SMA * (1 + 百分比)
   - 下轨 = SMA * (1 - 百分比)
   - 用于识别价格偏离程度

3. RSI (相对强弱指数)
   - Wilder平滑算法
   - 衡量价格涨跌的相对强度
   - 范围0-100，>70超买，<30超卖

4. 周线RSI
   - 将日线数据转换为周线后计算RSI
   - 用于判断中期趋势

5. 滚动最大回撤 (Rolling Drawdown)
   - 计算从滚动窗口高点以来的最大跌幅
   - 用于风险管理和止损参考

6. 乖离率 (Deviation Rate)
   - (当前价格 - SMA) / SMA * 100
   - 衡量价格偏离均线的程度

7. 图表数据准备
   - 整合所有指标数据
   - 转换为前端图表所需的格式
"""
import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class IndicatorService:
    """
    技术指标计算服务类

    提供各种技术指标的静态计算方法
    所有方法都是类方法，通过IndicatorService.calculate_xxx调用
    """

    @staticmethod
    def calculate_sma(data: pd.DataFrame, window: int = 1210) -> pd.DataFrame:
        """
        计算简单移动平均线 (Simple Moving Average)

        公式: SMA = (C1 + C2 + ... + Cn) / n
        其中C为收盘价，n为窗口大小

        参数说明:
            data: 包含close列的DataFrame
            window: 移动平均窗口大小，默认1210（约5年交易日）

        返回值:
            添加了sma{window}列的DataFrame
        """
        df = data.copy()
        df[f'sma{window}'] = df['close'].rolling(window=window).mean()
        return df
    
    @staticmethod
    def calculate_envelope_bands(data: pd.DataFrame, window: int = 1210,
                                  percent: float = 0.15) -> pd.DataFrame:
        """
        计算SMA包络线（基于SMA的百分比通道）

        包络线原理:
        - 以SMA为中轴
        - 上轨 = SMA * (1 + percent)
        - 下轨 = SMA * (1 - percent)
        - 当价格触及上轨时可能超买，触及下轨时可能超卖

        参数说明:
            data: 包含 close 列的 DataFrame
            window: 移动平均窗口，默认1210（约5年）
            percent: 包络线百分比，默认 15%

        返回值:
            添加了upper_band、lower_band、sma列的DataFrame
        """
        df = data.copy()
        sma = df['close'].rolling(window=window).mean()

        df['upper_band'] = sma * (1 + percent)  # 上轨
        df['lower_band'] = sma * (1 - percent)  # 下轨
        df['sma'] = sma

        return df
    
    @staticmethod
    def calculate_rsi(data: pd.DataFrame, period: int = 14) -> pd.DataFrame:
        """
        计算 RSI 指标 (Relative Strength Index)

        RSI = 100 - (100 / (1 + RS))
        RS = 平均涨幅 / 平均跌幅

        计算方法（改良Wilder平滑算法）:
        1. 前period个值使用简单平均初始化
        2. 之后的值使用平滑公式: AVG = (前一日AVG * (period-1) + 今日值) / period

        参数说明:
            data: 包含 close 列的 DataFrame
            period: RSI 周期，默认14

        返回值:
            添加了rsi列的DataFrame

        信号解读:
            - RSI > 70: 超买区域
            - RSI < 30: 超卖区域
            - RSI = 50: 多空平衡
        """
        df = data.copy()

        # 计算价格变动
        delta = df['close'].diff()

        # 分离上涨和下跌
        gain = delta.where(delta > 0, 0)   # 只保留正变动
        loss = -delta.where(delta < 0, 0)   # 只保留负变动，取绝对值

        # 初始化avg_gain和avg_loss
        avg_gain = pd.Series(np.nan, index=df.index)
        avg_loss = pd.Series(np.nan, index=df.index)

        # 前period个值使用简单平均
        first_gain = gain.iloc[:period].mean()
        first_loss = loss.iloc[:period].mean()
        avg_gain.iloc[period - 1] = first_gain
        avg_loss.iloc[period - 1] = first_loss

        # Wilder平滑算法
        factor = period - 1
        for i in range(period, len(df)):
            avg_gain.iloc[i] = (avg_gain.iloc[i - 1] * factor + gain.iloc[i]) / period
            avg_loss.iloc[i] = (avg_loss.iloc[i - 1] * factor + loss.iloc[i]) / period

        # 计算RS和RSI
        rs = avg_gain / avg_loss
        df['rsi'] = 100 - (100 / (1 + rs))

        return df
    
    @staticmethod
    def calculate_weekly_rsi(data: pd.DataFrame, period: int = 14) -> pd.DataFrame:
        """
        计算周线 RSI

        计算流程:
        1. 将日线数据重采样为周线（取每周最后一个交易日的数据）
        2. 在周线数据上计算RSI

        参数说明:
            data: 包含 date 和 close 列的 DataFrame
            period: RSI 周期，默认14

        返回值:
            包含 date 和 rsi 列的DataFrame（周线数据）
        """
        df = data[['date', 'close']].copy()
        df.set_index('date', inplace=True)
        
        # 重采样为周线（取每周最后一个交易日的数据）
        # 'W'表示周，last()表示取最后一个值
        weekly = df.resample('W').last().dropna()
        
        # 计算周线 RSI
        weekly = IndicatorService.calculate_rsi(weekly, period)
        
        weekly.reset_index(inplace=True)
        return weekly[['date', 'rsi']].dropna()
    
    @staticmethod
    def calculate_rolling_drawdown(data: pd.DataFrame, 
                                    window: int = 1260) -> pd.DataFrame:
        """
        计算滚动最大回撤 (Rolling Maximum Drawdown)

        回撤定义:
        - 从滚动窗口内的最高点到当前价格的跌幅百分比
        - 反映投资组合或资产从峰值回落的风险

        计算公式:
        - 滚动最大值 = 窗口内收盘价的最高值
        - 回撤 = (当前价格 - 滚动最大值) / 滚动最大值 * 100

        参数说明:
            data: 包含 close 列的 DataFrame
            window: 滚动窗口（交易日），默认1260（约5年，252交易日/年）

        返回值:
            添加了drawdown列的DataFrame（负值表示回撤）
        """
        df = data.copy()
        
        # 滚动窗口内的最高价（作为峰值参考）
        rolling_max = df['close'].rolling(window=window, min_periods=1).max()
        
        # 计算回撤比例
        # (当前值 - 滚动最大值) / 滚动最大值 * 100
        # 结果为负值表示回撤
        df['drawdown'] = ((df['close'] - rolling_max) / rolling_max * 100)
        
        return df
    
    @staticmethod
    def calculate_deviation_rate(data: pd.DataFrame, 
                                  sma_column: str = 'sma1210') -> Optional[float]:
        """
        计算当前乖离率 (Deviation Rate)

        乖离率原理:
        - 衡量当前价格相对于均线的偏离程度
        - 正值表示价格高于均线（可能偏高）
        - 负值表示价格低于均线（可能偏低）

        公式: 乖离率 = (当前价格 - SMA) / SMA * 100

        参数说明:
            data: 包含close列和sma_column的DataFrame
            sma_column: SMA列名，默认'sma1210'

        返回值:
            乖离率百分比值（保留2位小数）
            如果数据为空或SMA为0则返回None
        """
        if data.empty or sma_column not in data.columns:
            return None
        
        latest = data.iloc[-1]
        if pd.isna(latest[sma_column]) or latest[sma_column] == 0:
            return None
        
        # 计算乖离率
        deviation = (latest['close'] - latest[sma_column]) / latest[sma_column] * 100
        return round(deviation, 2)
    
    @staticmethod
    def prepare_chart_data(data: pd.DataFrame) -> Dict:
        """
        准备图表所需的所有数据

        整合以下指标数据用于前端绑图:
        1. 价格数据：日期、收盘价
        2. SMA1210：1210日简单移动平均线（约5年）
        3. 包络线：上下轨（±15%）
        4. 乖离率：价格偏离均线的百分比
        5. RSI数据：日线和周线RSI
        6. 回撤数据：滚动5年最大回撤

        参数说明:
            data: 包含 date、close 等列的 DataFrame

        返回值:
            Dict，包含字段：
            - dates: 日期列表（字符串格式）
            - index_values: 收盘价列表
            - sma1210: SMA1210值列表
            - upper_band: 上轨值列表
            - lower_band: 下轨值列表
            - deviation_rate: 当前乖离率
            - rsi_dates: RSI日期列表
            - rsi14: RSI值列表
            - rsi_daily: 日线RSI值列表（对应dates）
            - current_rsi: 当前RSI值
            - drawdown_5y: 5年回撤数据列表
            - min_drawdown: 最小回撤值
            - last_update: 数据更新时间
        """
        if data.empty:
            return {
                "dates": [],
                "index_values": [],
                "sma1210": [],
                "upper_band": [],
                "lower_band": [],
                "deviation_rate": None,
                "rsi_dates": [],
                "rsi14": [],
                "current_rsi": None,
                "drawdown_5y": [],
                "min_drawdown": None,
                "last_update": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
        
        df = data.copy()
        
        # 1. 计算 SMA1210 和包络线（±15%）
        df = IndicatorService.calculate_sma(df, 1210)
        df = IndicatorService.calculate_envelope_bands(df, 1210, 0.15)
        
        # 2. 计算周线 RSI14
        weekly_rsi = IndicatorService.calculate_weekly_rsi(df, 14)
        
        # 3. 计算滚动 5 年最大回撤（1260个交易日）
        df = IndicatorService.calculate_rolling_drawdown(df, 1260)
        
        # 4. 计算乖离率
        deviation_rate = IndicatorService.calculate_deviation_rate(df, 'sma1210')
        
        # 5. 提取价格数据
        dates = df['date'].dt.strftime('%Y-%m-%d').tolist()
        index_values = df['close'].tolist()
        sma1210 = [round(v, 2) if not pd.isna(v) else None for v in df['sma1210'].tolist()]
        upper_band = [round(v, 2) if not pd.isna(v) else None for v in df['upper_band'].tolist()]
        lower_band = [round(v, 2) if not pd.isna(v) else None for v in df['lower_band'].tolist()]
        
        # 6. 提取周线RSI数据
        rsi_dates = weekly_rsi['date'].dt.strftime('%Y-%m-%d').tolist()
        rsi_values = [round(v, 2) if not pd.isna(v) else None for v in weekly_rsi['rsi'].tolist()]
        current_rsi = rsi_values[-1] if rsi_values else None
        
        # 7. 将周线RSI映射到日线日期（每个交易日显示最近一周的RSI）
        rsi_daily = [None] * len(dates)
        rsi_idx = 0
        j = 0
        while rsi_idx < len(rsi_dates) and j < len(dates):
            w_date_str = rsi_dates[rsi_idx]
            # 找到第一个日期 >= 周线日期的位置
            while j + 1 < len(dates) and dates[j + 1] <= w_date_str:
                j += 1
            rsi_daily[j] = rsi_values[rsi_idx]
            rsi_idx += 1
        
        # 8. 提取回撤数据
        drawdown_values = [round(v, 2) if not pd.isna(v) else None for v in df['drawdown'].tolist()]
        min_drawdown = round(df['drawdown'].min(), 2) if not df['drawdown'].isna().all() else None
        
        return {
            "dates": dates,
            "index_values": index_values,
            "sma1210": sma1210,
            "upper_band": upper_band,
            "lower_band": lower_band,
            "deviation_rate": deviation_rate,
            "rsi_dates": rsi_dates,
            "rsi14": rsi_values,
            "rsi_daily": rsi_daily,
            "current_rsi": current_rsi,
            "drawdown_5y": drawdown_values,
            "min_drawdown": min_drawdown,
            "last_update": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }


indicator_service = IndicatorService()
