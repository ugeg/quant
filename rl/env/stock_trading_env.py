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
    metadata = {'render_modes': ['human'],"render_fps":1}
    def __init__(self, raw_data: pd.DataFrame, window_size: int) -> None:
        self.trade_fee_ask_percent = 0.0015  # 卖出手续费+印花税
        self.trade_fee_bid_percent = 0.0005  # 买入手续费
        self.start_idx = 0
        self.end_idx = 0
        self._current_idx = None
        self._last_trade_tick = None
        self._position = Positions.FLAT
        self._position_history = []
        self._trade_history = []
        self._total_reward = 0.
        self.episode_length = 253  # 每次交易的天数
        self.raw_close_prices = raw_data.loc[:, 'close'].to_numpy()  # 用于计算奖励
        self.df = raw_data
        self.window_size = window_size
        # 定义动作空间和观察空间
        self.action_space = spaces.Discrete(len(Actions))
        self.observation_space = spaces.Box(low=-np.inf, high=np.inf,
                                            shape=(window_size, raw_data.shape[1] + 1))  # 加1是为了存储是否持仓的信息
        self._profit_history = [1.] * self.window_size
        # 数据标准化
        EPS = 1e-10
        self.df = self.df.apply(lambda x: (x - x.mean()) / (x.std() + EPS), axis=0)
        print("初始化完成")

    def step(self, action: ActType) -> tuple[ObsType, SupportsFloat, bool, bool, dict[str, Any]]:
        terminated = False  # 是否结束
        truncated = False  # 是否超时
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
        info = {
            'total_reward': self._total_reward,
            'position': self._position.value,
        }
        return observation, step_reward, terminated, truncated, info

    def reset(self, *, seed: int | None = None, options: dict[str, Any] | None = None) -> tuple[
        ObsType, dict[str, Any]]:
        # return super().reset(seed=seed, options=options)
        # 随机选择开始和结束索引
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
        matplotlib.rcParams['font.family'] = 'SimSun'  # 使用宋体
        matplotlib.rcParams['axes.unicode_minus'] = False  # 解决负号 '-' 显示为方块的问题
        import datetime
        # matplotlib.use('TkAgg')
        plt.clf()
        # self.max_possible_profit()
        # plt.title("max_possible_profit:"+str(self.max_possible_profit())+"\nfinal_profit:"+str(self._profit_history[-1]))
        plt.title("最终利润:"+str(self._profit_history[-1]))
        plt.xlabel('交易天数')
        plt.ylabel('利润')
        plt.plot(self._profit_history)
        fig_dir = "./fig"
        import os
        os.makedirs(fig_dir,exist_ok=True)
        plt.savefig(f"{fig_dir}/{datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}-profit.png")

        plt.clf()
        plt.xlabel('交易天数')
        plt.ylabel('收盘价')
        eps_price = self.raw_close_prices[self.start_idx-self.window_size+1:self.end_idx + 1]
        plt.plot(eps_price,color='black', lw=2.)
        # 标记买入和卖出点
        long_ticks = [i for i in range(len(self._trade_history)) if self._trade_history[i] == 1]
        flat_ticks = [i for i in range(len(self._trade_history)) if self._trade_history[i] == -1]
        plt.plot(long_ticks, eps_price[long_ticks], 'r^', markersize=4, label="买入")
        plt.plot(flat_ticks, eps_price[flat_ticks], 'gv', markersize=4, label="卖出")
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
            # 计算卖出时的奖励
            step_reward = np.log(ratio * cost)
        else:
            # 资金闲置 沉没成本
            step_reward = -0.000045
        return step_reward
