import time

from utils import mysql_util
from dataloader_base import MySQLDataloader

from stable_baselines3 import PPO
from stable_baselines3.common.callbacks import BaseCallback
from stable_baselines3.common.vec_env import DummyVecEnv


class TensorboardCallback(BaseCallback):
    def __init__(self, verbose=0):
        super().__init__(verbose)

    def _on_step(self) -> bool:
        self.logger.record(key="train/reward", value=self.locals["rewards"][0])
        return True


def train_ppo(ticker_list: list, indicators: list, start_date: str, end_date: str, save_file_path: str):
    dataloader = MySQLDataloader(ticker_list, start_date, end_date, "1d", mysql_util.engine)
    dataloader.download_data()
    dataloader.clean_data()
    print(dataloader.dataframe)
    dataloader.add_technical_indicator(indicators)
    dataloader.dataframe.drop(["time", "tic"], axis=1, inplace=True)
    print(dataloader.dataframe)
    env = DummyVecEnv([lambda: gym.make("stock_env", raw_data=dataloader.dataframe, window_size=30)])
    model = PPO("MlpPolicy", env, verbose=1, tensorboard_log="ppo")
    start = time.time()
    model.learn(total_timesteps=200000, callback=TensorboardCallback())
    end = time.time()
    print(f"训练耗时:{round(end - start)}s")
    model.save(save_file_path)


def test_ppo(ticker_list: list, indicators: list, start_date: str, end_date: str, load_file_path: str):
    dataloader = MySQLDataloader(ticker_list, start_date, end_date, "1d", mysql_util.engine)
    dataloader.download_data()
    dataloader.clean_data()
    print(dataloader.dataframe)
    dataloader.add_technical_indicator(indicators)
    dataloader.dataframe.drop(["time", "tic"], axis=1, inplace=True)
    print(dataloader.dataframe)
    env = gym.make("stock_env", raw_data=dataloader.dataframe, window_size=30)
    model = PPO("MlpPolicy", env, verbose=1).load(load_file_path)
    obs, _ = env.reset()
    # for i in range(251):
    action, _states = model.predict(obs)
    obs, rewards, _, done, info = env.step(action)
    while not done:
        action, _states = model.predict(obs)
        obs, rewards, _, done, info = env.step(action)
    env.render()


if __name__ == '__main__':
    import gymnasium as gym

    gym.register(id='stock_env', entry_point='env.stock_trading_env:StockTradingEnv')
    ticker_list = ["002594", ]
    indicators = [
        "macd",
        "boll_ub",
        "boll_lb",
        "rsi_30",
        "cci_30",
        "dx_30",
        "close_30_sma",
        "close_60_sma",
    ]
    indicators = [
        "macd",
        "boll_ub",
        "boll_lb", ]
    start_date = "2021-01-01"
    end_date = "2023-01-01"
    save_path = "./test_ppo1.zip"
    train_ppo(ticker_list, indicators, start_date, end_date, save_path)
    test_ppo(ticker_list, indicators, start_date, end_date, save_path)
