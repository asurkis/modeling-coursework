import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import approximations

all_variants = pd.read_csv('variants.csv')
variant_id: str
variant: pd.Series
current_series = {}
info = {}
sample_count = 10_000
bucket_count = 10

sort_order = ['variant'] + list(approximations.all_distributions.keys())
used_series = ['variant']

fig_hist = None


def describe_series(tpl: (str, pd.Series)):
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
    global fig_hist
    if fig_hist is not None:
        plt.close(fig_hist)
    fig_hist, ax = plt.subplots()
    values = []
    names = []
    for key in sort_order:
        if key in used_series and key in current_series:
            values.append(current_series[key])
            names.append(info[key]['name'])
    if len(values) > 1:
        ax.hist(np.array(values, dtype=object), density=True, bins=bucket_count)
    else:
        ax.hist(values[0], density=True, bins=bucket_count)
    ax.legend(names)
    fig_hist.show()


def recalc_approximations():
    for key in approximations.possible_distributions(mean=info['variant']['mean'], std=info['variant']['std']):
        fun = approximations.all_distributions[key]
        name, current_series[key] = fun(mean=info['variant']['mean'], std=info['variant']['std'], size=sample_count)
        info[key] = describe_series((name, current_series[key]))
    update_plots()


def update_variant(v):
    global variant
    variant = all_variants[v]
    info.clear()
    current_series.clear()
    current_series['variant'] = variant
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
    update_plots()
