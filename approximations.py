import numpy as np

g_rng = np.random.default_rng()


class SeriesDescription:
    def __init__(self, name: str, series: np.ndarray, params=None):
        self.name = name
        self.params = params
        self.series = series
        self.mean = series.mean()
        self.var = series.var()
        self.std = series.std()
        self.coeff_var = self.std / self.mean

        std_mean = self.std / len(series) ** .5
        intervals = [{'p': 0.90, 't': 1.643},
                     {'p': 0.95, 't': 1.960},
                     {'p': 0.99, 't': 2.576}]
        epsilons = {}
        for row in intervals:
            epsilons[row['p']] = row['p'] * row['t'] * std_mean
        self.epsilon = epsilons


def uniform(mean: float, std: float, size, rng=None) -> SeriesDescription:
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
    return SeriesDescription('Равномерное распределение',
                             rng.uniform(low=low, high=high, size=size),
                             {'low': low, 'high': high})


def exponential(mean: float, std: float, size, rng=None) -> SeriesDescription:
    rng = g_rng if rng is None else rng
    return SeriesDescription('Экспоненциальное распределение',
                             rng.exponential(scale=mean, size=size),
                             {'mean': mean})


def __gamma(mean: float, shape: float, size, rng=None) -> np.ndarray:
    rng = g_rng if rng is None else rng
    return rng.gamma(shape=shape, scale=mean / shape, size=size)


def gamma(mean: float, std: float, size, rng=None) -> SeriesDescription:
    # std / mean = 1 / sqrt(shape)
    # mean^2 = shape * var
    # shape = mean^2 / var
    # shape * scale = mean
    # scale = mean / shape
    shape = (mean / std) ** 2
    return SeriesDescription('Гамма-распределение', __gamma(mean=mean, shape=shape, size=size, rng=rng),
                             {'mean': mean, 'shape': shape})


def erlang_floor(mean: float, std: float, size, rng=None) -> SeriesDescription:
    shape = (mean / std) ** 2
    k = np.floor(shape)
    return SeriesDescription(f'Распределение Эрланга {k:.0f}-го порядка',
                             __gamma(mean=mean, shape=k, size=size, rng=rng),
                             {'mean': mean, 'shape': k})


def erlang_ceil(mean: float, std: float, size, rng=None) -> SeriesDescription:
    shape = (mean / std) ** 2
    k = np.ceil(shape)
    return SeriesDescription(f'Распределение Эрланга {k:.0f}-го порядка',
                             __gamma(mean=mean, shape=k, size=size, rng=rng),
                             {'mean': mean, 'shape': k})


def hyper_exponential(mean: float, coeff_var: float, q: float, size, rng=None) -> SeriesDescription:
    rng = g_rng if rng is None else rng

    t1 = (1 + ((1 - q) / (2 * q) * (coeff_var * coeff_var - 1)) ** 0.5) * mean
    t2 = (1 - (q / (2 * (1 - q)) * (coeff_var * coeff_var - 1)) ** 0.5) * mean

    exp1 = np.sign(t1) * rng.exponential(scale=np.abs(t1), size=size)
    proc = rng.uniform(size=size) >= q
    exp1[proc] *= t2 / t1
    return SeriesDescription('Гиперэкспоненциальное распределение', exp1,
                             {'t1': t1, 't2': t2, 'q': q, 'p': 1 - q})


def hyper_exponential_max_q(coeff_var: float) -> float:
    return 2 / (1 + coeff_var * coeff_var)


mean_std_distributions = [
    'uniform',
    'exponential',
    'gamma',
    'erlang_floor',
    'erlang_ceil',
]

all_distributions = mean_std_distributions + ['hyper_exponential']


def possible_mean_std_distributions(coeff: float):
    answer = {'uniform': uniform, 'exponential': exponential, 'gamma': gamma}
    if coeff < 1:
        answer['erlang_floor'] = erlang_floor
        answer['erlang_ceil'] = erlang_ceil
    return answer
