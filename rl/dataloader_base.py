import os.path
from typing import List

import pandas as pd
import sqlalchemy
import stockstats


class Dataloader:

    def __init__(self, ticker_list: List[str], start_date: str, end_date: str, time_interval: str = "1d", **kwargs):
        self.ticker_list = list(set(ticker_list))  # 去重
        self.start_date: str = start_date.replace('-', '')
        self.end_date: str = end_date.replace('-', '')
        self.time_interval: str = time_interval
        self.dataframe: pd.DataFrame = pd.DataFrame()

    def download_data(self):
        pass

    def get_trading_days(self, start_date: str, end_date: str) -> List[str]:
        pass

    def clean_data(self):
        df = self.dataframe.copy()
        df = df.rename(columns={"date": "time"})
        trading_days = self.get_trading_days(self.start_date, self.end_date)
        new_df = pd.DataFrame()
        for tic in self.ticker_list:
            print(("Clean data for ") + tic)
            # create empty DataFrame using complete time index
            tmp_df = pd.DataFrame(
                columns=["open", "high", "low", "close", "volume"], index=trading_days
            )
            # get data for current ticker
            tic_df = df[df.tic == tic]
            # fill empty DataFrame using orginal data
            for i in range(tic_df.shape[0]):
                tmp_df.loc[tic_df.iloc[i]["time"]] = tic_df.iloc[i][["open", "high", "low", "close", "volume"]]
            # 如果第一天停牌，用第一个不为空的收盘价代替，成交量设为0
            if str(tmp_df.iloc[0]["close"]) == "nan":
                print("NaN data on start date, fill using first valid data.")
                for i in range(tmp_df.shape[0]):
                    if str(tmp_df.iloc[i]["close"]) != "nan":
                        first_valid_close = tmp_df.iloc[i]["close"]
                        tmp_df.iloc[0] = [first_valid_close, first_valid_close, first_valid_close, first_valid_close,
                                          0.0, ]
                        break
            # 其他停牌日收盘价为以前一天收盘价，，成交量设为0
            for i in range(tmp_df.shape[0]):
                if str(tmp_df.iloc[i]["close"]) == "nan":
                    previous_close = tmp_df.iloc[i - 1]["close"]
                    if str(previous_close) == "nan":
                        raise ValueError
                    tmp_df.iloc[i] = [previous_close, previous_close, previous_close, previous_close, 0.0, ]
            # merge single ticker data to new DataFrame
            # tmp_df = tmp_df.astype(float)
            tmp_df["tic"] = tic
            # new_df = new_df.append(tmp_df)
            new_df = pd.concat([new_df, tmp_df])
            print(("Data clean for ") + tic + (" is finished."))

        # reset index and rename columns
        new_df = new_df.reset_index()
        self.dataframe = new_df.rename(columns={"index": "time"})
        print("Data clean all finished!")

    def add_technical_indicator(self, tech_indicator_list: List[str]):
        print("tech_indicator_list: ", tech_indicator_list)
        stock = stockstats.StockDataFrame.retype(self.dataframe)
        unique_ticker = stock.tic.unique()
        for indicator in tech_indicator_list:
            print("indicator: ", indicator)
            indicator_df = pd.DataFrame()
            for i in range(len(unique_ticker)):
                try:
                    temp_indicator = stock[stock.tic == unique_ticker[i]][indicator]
                    temp_indicator = pd.DataFrame(temp_indicator)
                    temp_indicator["tic"] = unique_ticker[i]
                    temp_indicator["time"] = self.dataframe[self.dataframe.tic == unique_ticker[i]][
                        "time"
                    ].to_list()
                    indicator_df = pd.concat([indicator_df, temp_indicator], ignore_index=True)
                except Exception as e:
                    print(e)
            if not indicator_df.empty:
                self.dataframe = self.dataframe.merge(
                    indicator_df[["tic", "time", indicator]], on=["tic", "time"], how="left"
                )
        self.dataframe.sort_values(by=["time", "tic"], inplace=True)
        time_to_drop = self.dataframe[self.dataframe.isna().any(axis=1)].time.unique()
        self.dataframe = self.dataframe[~self.dataframe.time.isin(time_to_drop)]
        self.dataframe.reset_index(drop=True, inplace=True)
        print("Succesfully add technical indicators")


class MySQLDataloader(Dataloader):

    def __init__(self, ticker_list: List[str], start_date: str, end_date: str, time_interval: str, engine):
        super().__init__(ticker_list, start_date, end_date, time_interval)
        self.mysql_engine = engine

    def download_data(self):
        ticker_list_str = "'" + "','".join(self.ticker_list) + "'"
        # 注意使用前复权的数据（前复权调整历史价格数据，后复权调整当前价格数据）
        query_sql = (f"SELECT trade_date as date,`open`,high,low,`close`, volume,symbol as tic from stock_zh_a_hist"
                     f" WHERE symbol in ({ticker_list_str}) and trade_date>= {self.start_date} and  trade_date<= {self.end_date}")
        print("query_sql:", query_sql)
        data_df = pd.read_sql(query_sql, self.mysql_engine)
        # create day of the week column (monday = 0)
        data_df["date"] = pd.to_datetime(data_df["date"])
        # data_df["day"] = data_df["date"].dt.dayofweek
        # convert date to standard string format, easy to filter
        data_df["date"] = data_df.date.apply(lambda x: x.strftime("%Y-%m-%d"))
        # drop missing data
        data_df = data_df.dropna()
        data_df = data_df.reset_index(drop=True)
        print("Shape of DataFrame: ", data_df.shape)
        # print("Display DataFrame: ", data_df.head())

        self.dataframe = data_df.sort_values(by=["date", "tic"]).reset_index(drop=True)

    def get_trading_days(self, start_date: str, end_date: str) -> List[str]:
        df = pd.read_sql(
            f"SELECT cal_date from trade_cal WHERE cal_date>={self.start_date} and cal_date<={self.end_date} and is_open=1",
            self.mysql_engine)
        return [i[0:4] + "-" + i[4:6] + "-" + i[6:8] for i in list(df['cal_date'])]
class CsvDataloader(Dataloader):

    def __init__(self, ticker_list: List[str], start_date: str, end_date: str, time_interval: str, data_dir:str):
        super().__init__(ticker_list, start_date, end_date, time_interval)
        self.data_dir=data_dir

    def download_data(self):
        for ticker in self.ticker_list:
            df = pd.read_csv(os.path.join(self.data_dir,ticker))
            df = df[(df['trade_date']>=self.start_date) & (df['trade_date']<self.end_date)]
            self.dataframe = pd.concat([self.dataframe,df],ignore_index=True)

    def get_trading_days(self, start_date: str, end_date: str) -> List[str]:
        return self.dataframe['trade_date'].unique()





