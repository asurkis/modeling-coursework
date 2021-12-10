import numpy as np

g_rng = np.random.default_rng()


def uniform(mean: float, std: float, size, rng=None) -> (str, np.ndarray):
    rng = g_rng if rng is None else rng
    # mean = (low + high) / 2
    # variation = integral from 0 to 1 of ((high - low) * (x - 0.5))^2 dx
    # = (high - low)^2 * integral from -0.5 to 0.5 of x^2 dx =
    # = (high - low)^2 * (x^3 / 3 from -0.5 to 0.5) =
    # = (high - low)^2 / 12
    # std = sqrt(variation) = (high - low) / sqrt(12)

    # high - low = sqrt(12) * std
    # high + low = 2 * mean
    # 2 * high = 2 * mean + sqrt(12) * std
    # 2 * low = 2 * mean - sqrt(12) * std
    # high = mean + sqrt(3) * std
    # low = mean - sqrt(3) * std

    diff = 3 ** 0.5 * std
    high = mean + diff
    low = mean - diff
    return 'Равномерное распределение', rng.uniform(low=low, high=high, size=size)


def exponential(mean: float, _std: float, size, rng=None) -> (str, np.ndarray):
    rng = g_rng if rng is None else rng
    return 'Экспоненциальное распределение', rng.exponential(scale=mean, size=size)


def __gamma(mean: float, shape: float, size, rng=None) -> np.ndarray:
    rng = g_rng if rng is None else rng
    return rng.gamma(shape=shape, scale=mean / shape, size=size)


def gamma(mean: float, std: float, size, rng=None) -> (str, np.ndarray):
    # std / mean = 1 / sqrt(shape)
    # mean^2 = shape * var
    # shape = mean^2 / var
    # shape * scale = mean
    # scale = mean / shape
    shape = (mean / std) ** 2
    return 'Гамма-распределение', __gamma(mean=mean, shape=shape, size=size, rng=rng)


def erlang_floor(mean: float, std: float, size, rng=None) -> (str, np.ndarray):
    shape = (mean / std) ** 2
    k = np.floor(shape)
    return f'Распределение Эрланга {k:.0f}-го порядка', __gamma(mean=mean, shape=k, size=size, rng=rng)


def erlang_ceil(mean: float, std: float, size, rng=None) -> (str, np.ndarray):
    shape = (mean / std) ** 2
    k = np.ceil(shape)
    return f'Распределение Эрланга {k:.0f}-го порядка', __gamma(mean=mean, shape=k, size=size, rng=rng)


casual = {
    'Равномерное распределение': uniform,
    'Экспоненциальное распределение': exponential,
    'Гамма-распределение': gamma,
    'Распределение Эрланга с округлением вниз': erlang_floor,
    'Распределение Эрланга с округлением вверх': erlang_ceil,
}
