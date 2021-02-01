# -*- coding: utf-8 -*-
# @Author  : pengj    <ugeg@163.com>
# @Time    : 2021/2/1 21:50
# @File    : draw.py
import pandas as pd
from sqlalchemy.orm import Session

from utils import mysql_connector
from utils.entity import Daily, StockBasic
from pyecharts import options as opts
from pyecharts.charts import Kline, Bar, Grid
from typing import List, Union
mysql_engine = mysql_connector.engine
session = Session(mysql_connector.engine, autocommit=True)


def get_data(ts_code: str):
    query = session.query(Daily).filter(Daily.ts_code == ts_code) \
        # .filter(Daily.trade_date>='20210101')
    return pd.read_sql(query.statement, mysql_engine)


def get_code(ts_name: str):
    """
    查询股票代码，有多个时报错
    :param ts_name: 模糊股票代码或股票名
    :return: 股票代码
    """
    if len(ts_name) >= 6:
        result = session.query(StockBasic.ts_code, StockBasic.name).filter(StockBasic.ts_code.like(ts_name + "%")).all()
    else:
        result = session.query(StockBasic.ts_code, StockBasic.name).filter(StockBasic.name.like(ts_name + "%")).all()
    if len(result) == 1:
        return result[0][0]
    elif len(result) == 0:
        raise LookupError("ts_code not found: " + ts_name)
    elif len(result) > 1:
        raise LookupError("ts_code found Multiple records :", result)


def get_name(ts_code: str):
    """
    查询stock名
    :param ts_code: 精确的code
    :return: stock名
    """
    return session.query(StockBasic.name).filter(StockBasic.ts_code == ts_code).first()[0]

def calculate_ma(day_count: int, data):
    result: List[Union[float, str]] = []
    for i in range(len(data["values"])):
        if i < day_count:
            result.append("-")
            continue
        sum_total = 0.0
        for j in range(day_count):
            sum_total += float(data["values"][i - j][1])
        result.append(abs(float("%.3f" % (sum_total / day_count))))
    return result
def draw(df: pd.DataFrame, ts_name: str):
    kline = (Kline().add_xaxis(df["trade_date"].values.tolist()).add_yaxis(ts_name, df[
        ["open", "close", "low", "high"]].values.tolist()).set_global_opts(
        xaxis_opts=opts.AxisOpts(is_scale=True),
        yaxis_opts=opts.AxisOpts(
            is_scale=True,
            splitarea_opts=opts.SplitAreaOpts(
                is_show=True, areastyle_opts=opts.AreaStyleOpts(opacity=1)
            ),
        ),
        datazoom_opts=[opts.DataZoomOpts(pos_bottom="-2%")],
        title_opts=opts.TitleOpts(title="Kline-DataZoom-slider-Position"),
    ))
    kline.render("a.html")
def draw2(df: pd.DataFrame, ts_name: str):
    kline = (Kline().add_xaxis(df["trade_date"].values.tolist())
        .add_yaxis(series_name = ts_name,
                   y_axis = df[["open", "close", "low", "high"]].values.tolist(),
                   itemstyle_opts=opts.ItemStyleOpts(color="#ec0000", color0="#00da3c"))
        .set_global_opts(
        legend_opts=opts.LegendOpts(
            is_show=False, pos_bottom=10, pos_left="center"
        ),
        datazoom_opts=[opts.DataZoomOpts(pos_bottom="-2%")],
        # datazoom_opts=[
        #     opts.DataZoomOpts(
        #         is_show=False,
        #         type_="inside",
        #         xaxis_index=[0, 1],
        #         range_start=98,
        #         range_end=100,
        #     ),
        #     opts.DataZoomOpts(
        #         is_show=True,
        #         xaxis_index=[0, 1],
        #         type_="slider",
        #         pos_top="85%",
        #         range_start=98,
        #         range_end=100,
        #     ),
        # ],
        yaxis_opts=opts.AxisOpts(
            is_scale=True,
            splitarea_opts=opts.SplitAreaOpts(
                is_show=True, areastyle_opts=opts.AreaStyleOpts(opacity=1)
            ),
        ),
        tooltip_opts=opts.TooltipOpts(
            trigger="axis",
            axis_pointer_type="cross",
            background_color="rgba(245, 245, 245, 0.8)",
            border_width=1,
            border_color="#ccc",
            textstyle_opts=opts.TextStyleOpts(color="#000"),
        ),
        visualmap_opts=opts.VisualMapOpts(
            is_show=False,
            dimension=2,
            series_index=5,
            is_piecewise=True,
            pieces=[
                {"value": 1, "color": "#00da3c"},
                {"value": -1, "color": "#ec0000"},
            ],
        ),
        axispointer_opts=opts.AxisPointerOpts(
            is_show=True,
            link=[{"xAxisIndex": "all"}],
            label=opts.LabelOpts(background_color="#777"),
        ),
        brush_opts=opts.BrushOpts(
            x_axis_index="all",
            brush_link="all",
            out_of_brush={"colorAlpha": 0.1},
            brush_type="lineX",
        ),)
    )
    bar = (
        Bar()
            .add_xaxis(xaxis_data=df["trade_date"].values.tolist())
            .add_yaxis(
            series_name="Volume",
            y_axis=df["vol"].values.tolist(),
            xaxis_index=1,
            yaxis_index=1,
            label_opts=opts.LabelOpts(is_show=False),
        )
            .set_global_opts(
            xaxis_opts=opts.AxisOpts(
                type_="category",
                is_scale=True,
                grid_index=1,
                boundary_gap=False,
                axisline_opts=opts.AxisLineOpts(is_on_zero=False),
                axistick_opts=opts.AxisTickOpts(is_show=False),
                splitline_opts=opts.SplitLineOpts(is_show=False),
                axislabel_opts=opts.LabelOpts(is_show=False),
                split_number=20,
                min_="dataMin",
                max_="dataMax",
            ),
            yaxis_opts=opts.AxisOpts(
                grid_index=1,
                is_scale=True,
                split_number=2,
                axislabel_opts=opts.LabelOpts(is_show=False),
                axisline_opts=opts.AxisLineOpts(is_show=False),
                axistick_opts=opts.AxisTickOpts(is_show=False),
                splitline_opts=opts.SplitLineOpts(is_show=False),
            ),
            legend_opts=opts.LegendOpts(is_show=False),
        )
    )
    # Grid Overlap + Bar
    grid_chart = Grid(
        init_opts=opts.InitOpts(
            width="1000px",
            height="800px",
            animation_opts=opts.AnimationOpts(animation=False),
        )
    )
    grid_chart.add(
        kline,
        grid_opts=opts.GridOpts(pos_left="10%", pos_right="8%", height="50%"),
    )
    grid_chart.add(
        bar,
        grid_opts=opts.GridOpts(
            pos_left="10%", pos_right="8%", pos_top="63%", height="16%"
        ),
    )
    grid_chart.render("b.html")

if __name__ == '__main__':
    stock = "中兴通讯"
    code = get_code(stock)
    df = get_data(code)
    draw(df, get_name(code))
