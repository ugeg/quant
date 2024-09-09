from enum import Enum
from typing import Any, SupportsFloat

import gymnasium
import numpy as np
import pandas as pd
from gymnasium.core import RenderFrame, ObsType, ActType
from gymnasium.vector.utils import spaces


class Actions(int, Enum):
    SELL = 0
    HOLD = 1
    BUY = 2


class Positions(int, Enum):
    # SHORT = -1
    FLAT = 0
    LONG = 1


def transform(position: Positions, action: int) -> [Positions, bool]:
    if action == Actions.SELL and position == Positions.LONG:
        return Positions.FLAT, True
    if action == Actions.BUY and position == Positions.FLAT:
        return Positions.LONG, True
    return position, False


class StockTradingEnv(gymnasium.Env):
    metadata = {'render_modes': ['human']}
    # metadata = {'render_mode': 'human'}
    render_mode = 'human'
    def __init__(self, raw_data: pd.DataFrame, window_size: int) -> None:
        self.trade_fee_ask_percent = 0.0015  # 卖出手续费+印花税
        self.trade_fee_bid_percent = 0.0005  # 买入手续费
        self.train_range = None
        self.test_range = None
        self.start_idx = 0
        self.end_idx = 0
        self._current_idx = None
        self._last_trade_tick = None
        self._position = None
        self._position_history = None
        self._trade_history = None
        self._total_reward = None
        # 每次玩1年
        self.episode_length = 253
        trade_feature = ["is_hold"]
        self.raw_close_prices = raw_data.loc[:, 'close'].to_numpy()  # 用于计算reward
        self.df = raw_data
        self.window_size = window_size
        self.action_space = spaces.Discrete(len(Actions))
        self.observation_space = spaces.Box(low=-np.inf, high=np.inf,
                                            shape=(window_size, raw_data.shape[1] + len(trade_feature)))
        # 正态化
        EPS = 1e-10
        if self.train_range is None or self.test_range is None:
            self.df = self.df.apply(lambda x: (x - x.mean()) / (x.std() + EPS), axis=0)
        else:
            boundary = int(len(self.df) * self.train_range)
            train_data = raw_data[:boundary].copy()
            boundary = int(len(raw_data) * (1 + self.test_range))
            test_data = raw_data[boundary:].copy()

            train_data = train_data.apply(lambda x: (x - x.mean()) / (x.std() + EPS), axis=0)
            test_data = test_data.apply(lambda x: (x - x.mean()) / (x.std() + EPS), axis=0)
            self.df.loc[train_data.index, train_data.columns] = train_data
            self.df.loc[test_data.index, test_data.columns] = test_data
        print("init finish")

    def step(self, action: ActType) -> tuple[ObsType, SupportsFloat, bool, bool, dict[str, Any]]:
        terminated = False  # 游戏结束
        truncated = False  # 游戏超时
        self._current_idx += 1
        if self._current_idx >= self.end_idx:
            truncated = True
            terminated = True
        step_reward = self._calculate_reward(action)
        self._position, trade = transform(self._position, action)
        if trade:
            self._last_trade_tick = self._current_idx
            self._trade_history.append(1 if self._position == Positions.LONG else -1)
        else:
            self._trade_history.append(0)
        self._total_reward += step_reward
        self._position_history.append(self._position)
        self._profit_history.append(float(np.exp(self._total_reward)))
        observation = self._get_observation()
        info = dict(
            total_reward=self._total_reward,
            position=self._position.value,
        )
        return observation, step_reward, terminated, truncated, info

    def reset(self, *, seed: int | None = None, options: dict[str, Any] | None = None) -> tuple[
        ObsType, dict[str, Any]]:
        # return super().reset(seed=seed, options=options)
        # 设置区间
        if self.train_range is not None:
            boundary = int(len(self.df) * self.train_range)
            assert boundary - self.episode_length > self.window_size, \
                "parameter test_range is too small!"
            self.start_idx = np.random.randint(self.window_size, boundary - self.episode_length)
        else:
            self.start_idx = np.random.randint(self.window_size, len(self.df) - self.episode_length)
        self.end_idx = self.start_idx + self.episode_length - 1
        self._current_idx = self.start_idx
        self._position = Positions.FLAT
        self._position_history = [self._position] * self.window_size
        self._trade_history = [0] * self.window_size
        self._profit_history = [1.] * self.window_size
        self._total_reward = 0.
        return self._get_observation(), {}

    def render(self,mode='human') -> None:
        import matplotlib.pyplot as plt
        import matplotlib
        import datetime
        matplotlib.use('TkAgg')
        plt.clf()
        # self.max_possible_profit()
        # plt.title("max_possible_profit:"+str(self.max_possible_profit())+"\nfinal_profit:"+str(self._profit_history[-1]))
        plt.title("final_profit:"+str(self._profit_history[-1]))
        plt.xlabel('trading days')
        plt.ylabel('profit')
        plt.plot(self._profit_history)
        fig_dir = "./fig"
        import os
        os.makedirs(fig_dir,exist_ok=True)
        plt.savefig(f"{fig_dir}/{datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}-profit.png")

        plt.clf()
        plt.xlabel('trading days')
        plt.ylabel('close price')
        window_ticks = np.arange(len(self._trade_history))
        # eps_price = self.raw_close_prices[self.start_idx:self.end_idx + 1]
        eps_price = self.raw_close_prices[self.start_idx-self.window_size+1:self.end_idx + 1]
        plt.plot(eps_price,color='black', lw=2.)
        short_ticks = []
        long_ticks = []
        flat_ticks = []
        for i, tick in enumerate(window_ticks):
            # if self._position_history[i] == Positions.SHORT:
            #     short_ticks.append(tick)
            # if self._position_history[i] == Positions.LONG:
            if self._trade_history[i] == 1:
                long_ticks.append(tick)
            elif self._trade_history[i] == -1:
                flat_ticks.append(tick)

        # plt.plot(long_ticks, window_ticks[long_ticks], 'r^', markersize=4, label="Buy")
        # plt.plot(flat_ticks, window_ticks[flat_ticks], 'gv', markersize=4, label="Sell")
        plt.plot(long_ticks, eps_price[long_ticks], 'r^', markersize=4, label="Buy")
        plt.plot(flat_ticks, eps_price[flat_ticks], 'gv', markersize=4, label="Sell")
        # plt.plot(short_ticks, eps_price[short_ticks], 'rv', markersize=3, label="Short")
        plt.legend(loc='upper left', bbox_to_anchor=(0.05, 0.95))
        plt.savefig(f"./fig/{datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}--price.png")
        plt.show()

    def close(self):
        super().close()

    def _get_observation(self):
        market_info = self.df[self._current_idx - self.window_size + 1:self._current_idx + 1]
        market_info = market_info.reset_index(drop=True)
        trade_info = self._position_history[-self.window_size:]
        obs = pd.concat([market_info, pd.DataFrame({"position_history": trade_info})], axis=1)
        return obs.to_numpy().astype(np.float32)

    def _calculate_reward(self, action: int) -> np.float32:
        step_reward = 0.
        if action == Actions.SELL and self._position == Positions.LONG:
            current_price = (self.raw_close_prices[self._current_idx])
            last_trade_price = (self.raw_close_prices[self._last_trade_tick])
            ratio = current_price / last_trade_price
            cost = (1 - self.trade_fee_ask_percent) * (1 - self.trade_fee_bid_percent)
            step_reward = np.log(ratio * cost)
        else:
            # 资金闲置 沉没成本
            step_reward = -0.000045
        return step_reward
