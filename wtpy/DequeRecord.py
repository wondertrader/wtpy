import numpy as np
import pandas as pd

class DequeRecord:
    __cursor__: int
    __size__: int
    __mask__: list
    __data__: np.ndarray
    __view__: np.recarray

    def __init__(self, size: int, fields: dict):
        self.__cursor__: int = 0
        self.__size__: int = size
        self.__mask__: list = list(range(self.__size__))
        self.__data__: np.ndarray = np.empty(
            self.__size__, dtype=list(fields.items()))
        self.__view__: np.recarray = self.__data__.view(np.recarray)
        self.__view__.flags.writeable = False

    def append(self, row: tuple) -> int:
        self.__data__[self.__cursor__ % self.__size__] = row
        self.__cursor__ += 1
        if self.__cursor__ > self.__size__:
            self.__mask__.append(self.__mask__.pop(0))
        return self.__cursor__

    @property
    def shape(self) -> np.shape:
        return self.__view__.shape

    @property
    def size(self) -> int:
        return self.__size__

    @property
    def dtype(self) -> np.dtype:
        return self.__view__.dtype

    def __len__(self) -> int:
        return min(self.__cursor__, self.__size__)

    def __getattr__(self, name: str) -> np.recarray:
        if self.__cursor__ > self.__size__:
            return self.__view__[name][self.__mask__]
        else:
            return self.__view__[name][:self.__cursor__]

    def __getitem__(self, index) -> np.recarray:
        if isinstance(index, str):
            return self.__getattr__(index)
        elif isinstance(index, tuple):
            if isinstance(index[0], str) \
                    and (isinstance(index[1], slice) or isinstance(index[1], int)):
                if self.__cursor__ > self.__size__:
                    return self.__view__[index[0]][self.__mask__[index[1]]]
                else:
                    return self.__view__[index[0]][:self.__cursor__][index[1]]
            elif (isinstance(index[0], slice) or isinstance(index[0], int)) \
                    and isinstance(index[1], str):
                if self.__cursor__ > self.__size__:
                    return self.__view__[index[1]][self.__mask__[index[0]]]
                else:
                    return self.__view__[index[1]][:self.__cursor__][index[0]]
            else:
                raise KeyError(index)
        else:
            if self.__cursor__ > self.__size__:
                return self.__view__[self.__mask__[index]]
            else:
                return self.__view__[:self.__cursor__][index]

    def to_df(self) -> pd.DataFrame:
        return pd.DataFrame(self[:])