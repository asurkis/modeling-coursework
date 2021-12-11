import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import approximations

all_variants = pd.read_csv('variants.csv')
variant_id: str
variant: pd.Series
results = {}
sample_count = 10_000
bucket_count = 10

hyper_exponent_qmin = 0.0
hyper_exponent_qmax = 1.0
hyper_exponent_count = 2

sort_order_base = ['variant'] + approximations.mean_std_distributions
sort_order_hyper_exponents = []
sort_order = sort_order_base
used_series = ['variant']

fig_hist = None


def hyper_exponent_allowed() -> bool:
    return results['variant'].coeff_var > 1


def update_plots():
    global fig_hist
    if fig_hist is not None:
        plt.close(fig_hist)
    fig_hist, ax = plt.subplots()
    values = [results[key].series for key in used_series]
    names = [results[key].name for key in used_series]
    if len(values) > 1:
        ax.hist(np.array(values, dtype=object), density=True, bins=bucket_count)
    else:
        ax.hist(values[0], density=True, bins=bucket_count)
    ax.legend(names)
    fig_hist.show()


def recalc_mean_std_approximations():
    for key, fun in approximations.possible_mean_std_distributions(
            results['variant'].coeff_var).items():
        results[key] = fun(mean=results['variant'].mean, std=results['variant'].std, size=sample_count)


def update_variant(v):
    global variant
    variant = all_variants[v]
    results.clear()
    results['variant'] = approximations.SeriesDescription('Последовательность по варианту', variant)
    recalc_mean_std_approximations()


def update_sample_count(n):
    global sample_count
    if sample_count == n:
        return
    sample_count = n
    recalc_mean_std_approximations()


def update_bucket_count(n):
    global bucket_count
    if bucket_count == n:
        return
    bucket_count = n


def update_used_approximations(used):
    used_series.clear()
    used_series.append('variant')
    for key in sort_order:
        if key in results and (
                (key in used and used[key]) or (key.startswith('hyper_exponential') and used['hyper_exponential'])):
            used_series.append(key)


def update_hyper_exponent(qmin, qmax, qn):
    global hyper_exponent_qmin
    global hyper_exponent_qmax
    global hyper_exponent_count
    hyper_exponent_qmin = qmin
    hyper_exponent_qmax = qmax
    hyper_exponent_count = qn

    qs = np.linspace(qmin, qmax, qn)
    sort_order_hyper_exponents.clear()
    for i, q in enumerate(qs):
        hexpi = approximations.hyper_exponential(results['variant'].mean, results['variant'].std, q, sample_count)
        hexpi.name = f'Гиперэкспоненциальное распределение #{i}'
        results[f'hyper_exponential_{i}'] = hexpi
        sort_order_hyper_exponents.append(f'hyper_exponential_{i}')

    global sort_order
    sort_order = sort_order_base + sort_order_hyper_exponents
