from wtpy.DequeRecord import DequeRecord
from wtpy.WtCoreDefs import WTSBarStruct, WTSTickStruct
import numpy as np

class WtTickRecords(DequeRecord):
    def __init__(self, size: int):
        super().__init__(size=size, fields={
            'time': np.uint64,
            'exchg': 'U10',
            'code': 'U32',

            'price': np.double,
            'open': np.double,
            'high': np.double,
            'low': np.double,
            'settle_price': np.double,

            'upper_limit': np.double,
            'lower_limit': np.double,

            'total_volume': np.uint32,
            'volume': np.uint32,
            'total_turnover': np.double,
            'turn_over': np.double,
            'open_interest': np.uint32,
            'diff_interest': np.int32,

            'trading_date': np.uint32,
            'action_date': np.uint32,
            'action_time': np.uint32,

            'pre_close': np.double,
            'pre_settle': np.double,
            'pre_interest': np.uint32,

            'bid_prices_0': np.double,
            'bid_prices_1': np.double,
            'bid_prices_2': np.double,
            'bid_prices_3': np.double,
            'bid_prices_4': np.double,
            'bid_prices_5': np.double,
            'bid_prices_6': np.double,
            'bid_prices_7': np.double,
            'bid_prices_8': np.double,
            'bid_prices_9': np.double,

            'ask_prices_0': np.double,
            'ask_prices_1': np.double,
            'ask_prices_2': np.double,
            'ask_prices_3': np.double,
            'ask_prices_4': np.double,
            'ask_prices_5': np.double,
            'ask_prices_6': np.double,
            'ask_prices_7': np.double,
            'ask_prices_8': np.double,
            'ask_prices_9': np.double,

            'bid_qty_0': np.uint32,
            'bid_qty_1': np.uint32,
            'bid_qty_2': np.uint32,
            'bid_qty_3': np.uint32,
            'bid_qty_4': np.uint32,
            'bid_qty_5': np.uint32,
            'bid_qty_6': np.uint32,
            'bid_qty_7': np.uint32,
            'bid_qty_8': np.uint32,
            'bid_qty_9': np.uint32,

            'ask_qty_0': np.uint32,
            'ask_qty_1': np.uint32,
            'ask_qty_2': np.uint32,
            'ask_qty_3': np.uint32,
            'ask_qty_4': np.uint32,
            'ask_qty_5': np.uint32,
            'ask_qty_6': np.uint32,
            'ask_qty_7': np.uint32,
            'ask_qty_8': np.uint32,
            'ask_qty_9': np.uint32
        })

    def from_struct(self, data: WTSTickStruct):
        return self.append(
            (
                np.uint64(data.action_date)*1000000000+data.action_time,
                data.exchg,
                data.code,
                data.price,
                data.open,
                data.high,
                data.low,
                data.settle_price,
                data.upper_limit,
                data.lower_limit,
                data.total_volume,
                data.volume,
                data.total_turnover,
                data.turn_over,
                data.open_interest,
                data.diff_interest,
                data.trading_date,
                data.action_date,
                data.action_time,
                data.pre_close,
                data.pre_settle,
                data.pre_interest,
                data.bid_prices_0,
                data.bid_prices_1,
                data.bid_prices_2,
                data.bid_prices_3,
                data.bid_prices_4,
                data.bid_prices_5,
                data.bid_prices_6,
                data.bid_prices_7,
                data.bid_prices_8,
                data.bid_prices_9,
                data.ask_prices_0,
                data.ask_prices_1,
                data.ask_prices_2,
                data.ask_prices_3,
                data.ask_prices_4,
                data.ask_prices_5,
                data.ask_prices_6,
                data.ask_prices_7,
                data.ask_prices_8,
                data.ask_prices_9,
                data.bid_qty_0,
                data.bid_qty_1,
                data.bid_qty_2,
                data.bid_qty_3,
                data.bid_qty_4,
                data.bid_qty_5,
                data.bid_qty_6,
                data.bid_qty_7,
                data.bid_qty_8,
                data.bid_qty_9,
                data.ask_qty_0,
                data.ask_qty_1,
                data.ask_qty_2,
                data.ask_qty_3,
                data.ask_qty_4,
                data.ask_qty_5,
                data.ask_qty_6,
                data.ask_qty_7,
                data.ask_qty_8,
                data.ask_qty_9,
            )
        )


class WtBarRecords(DequeRecord):
    def __init__(self, size: int):
        super().__init__(size=size, fields=dict(
            bartime=np.uint64,
            time=np.uint64,
            open=np.double,
            high=np.double,
            low=np.double,
            close=np.double,
            settle=np.double,
            money=np.double,
            volume=np.uint32,
            hold=np.uint32,
            diff=np.int32,
        ))

    @property
    def opens(self) -> np.ndarray:
        return self.open

    @property
    def highs(self) -> np.ndarray:
        return self.high

    @property
    def lows(self) -> np.ndarray:
        return self.low

    @property
    def closes(self) -> np.ndarray:
        return self.close

    @property
    def volumes(self) -> np.ndarray:
        return self.volume

    @property
    def bartimes(self) -> np.ndarray:
        return self.bartime

    def get_bar(self, iLoc:int = -1) -> dict:
        return self[iLoc]

    def from_struct(self, data: WTSBarStruct) -> int:
        return self.append(
            (
                data.date,
                data.time if data.time == data.date else data.time + 199000000000,
                data.open,
                data.high,
                data.low,
                data.close,
                data.settle,
                data.money,
                data.vol,
                data.hold,
                data.diff
            )
        )
