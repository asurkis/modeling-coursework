import pandas as pd
import matplotlib.pyplot as plt
import approximations

all_variants = pd.read_csv('variants.csv')
variant_id: str
variant: pd.Series
current_approximations = {}
info = {}
sample_count = 1
bucket_count = 1

sort_order = ['variant'] + list(approximations.all_distributions.keys())
used_series = ['variant']


def describe_series(tpl):
    name, series = tpl
    result = {
        'name': name,
        'mean': series.mean(),
        'var': series.var(),
        'std': series.std(),
        'epsilon': {}
    }
    result['coeff_var'] = result['std'] / abs(result['mean'])

    std_mean = result['std'] / len(series) ** .5
    intervals = [{'p': 0.90, 't': 1.643},
                 {'p': 0.95, 't': 1.960},
                 {'p': 0.99, 't': 2.576}]
    epsilons = result['epsilon']
    for row in intervals:
        epsilons[row['p']] = row['p'] * row['t'] * std_mean
    return result


def update_plots():
    pass


def update_approximations_info():
    pass


def recalc_approximations():
    global current_approximations
    current_approximations = {}
    for key in approximations.possible_distributions(mean=info['variant']['mean'], std=info['variant']['std']):
        fun = approximations.all_distributions[key]
        current_approximations[key] = fun(mean=info['variant']['mean'], std=info['variant']['std'], size=sample_count)
        info[key] = describe_series(current_approximations[key])
    update_approximations_info()
    update_plots()


def update_variant(v):
    global variant
    variant = all_variants[v]
    info.clear()
    info['variant'] = describe_series(('Последовательность по варианту', variant))
    recalc_approximations()


def update_sample_count(n):
    global sample_count
    if sample_count == n:
        return
    sample_count = n
    recalc_approximations()


def update_bucket_count(n):
    global bucket_count
    if bucket_count == n:
        return
    bucket_count = n
    update_plots()


def update_used_approximations(used):
    global used_series
    used_series = ['variant'] + [key for key, value in used.items() if value and key in info]


update_variant('1')
update_sample_count(1)
update_bucket_count(1)
