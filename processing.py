import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import approximations


class MathModel:
    _all_variants = pd.read_csv('variants.csv')
    _variant_id = ''
    _variant = None
    _results = {}
    _allowed_keys = {key: False for key in approximations.all_distributions}
    _used_keys = {key: False for key in approximations.all_distributions}

    _sample_count = 10_000
    _bucket_count = 10
    _hyper_exponent_q1 = 0.001
    _hyper_exponent_q2 = 0.001
    _hyper_exponent_count = 2
    _fig_hist = None

    def _recalc_mean_std_approximations(self):
        for key, fun in approximations.possible_mean_std_distributions(
                self._results['variant'].coeff_var).items():
            self._results[key] = fun(mean=self._results['variant'].mean,
                                     std=self._results['variant'].std,
                                     size=self._sample_count)

    def _recalc_hyper_exponents(self):
        self._results = {key: val for key, val in self._results.items() if not key.startswith('hyper_exponential')}

        qs = np.linspace(self._hyper_exponent_q1, self._hyper_exponent_q2, self._hyper_exponent_count)
        for i, q in enumerate(qs):
            hexpi = approximations.hyper_exponential(
                mean=self._results['variant'].mean,
                coeff_var=self._results['variant'].coeff_var,
                q=q, size=self._sample_count)
            hexpi.name = f'Гиперэкспоненциальное распределение #{i}'
            self._results[f'hyper_exponential_{i + 1}'] = hexpi

    def _get_possible_variants(self):
        return self._all_variants.columns

    def _is_hyper_exponent_allowed(self):
        return self._results['variant'].coeff_var > 1

    def _get_hyper_exponent_limit(self):
        return approximations.hyper_exponential_max_q(self._results['variant'].coeff_var)

    def _get_results(self):
        return self._results

    def _get_allowed_keys(self):
        return self._allowed_keys

    def _get_used_results(self):
        keys = ['variant']
        for key in approximations.mean_std_distributions:
            if self._used_keys[key]:
                keys.append(key)

        if self._used_keys['hyper_exponential']:
            for key in self._results:
                if key.startswith('hyper_exponential'):
                    keys.append(key)

        used_results = [self._results[key] for key in keys]
        return used_results

    def _get_sample_count(self):
        return self._sample_count

    def _get_bucket_count(self):
        return self._bucket_count

    def _get_hyper_exponent_q1(self):
        return self._hyper_exponent_q1

    def _get_hyper_exponent_q2(self):
        return self._hyper_exponent_q2

    def _get_hyper_exponent_count(self):
        return self._hyper_exponent_count

    def _set_variant_id(self, variant_id):
        if self._variant_id == variant_id:
            return
        self._variant_id = variant_id
        self._variant = self._all_variants[variant_id].to_numpy()
        self._results.clear()
        self._results['variant'] = approximations.SeriesDescription(name='Последовательность по варианту',
                                                                    series=self._variant)
        self._allowed_keys['uniform'] = True
        self._allowed_keys['uniform'] = True
        self._allowed_keys['exponential'] = True
        self._allowed_keys['gamma'] = True
        self._allowed_keys['erlang_floor'] = not self.hyper_exponent_allowed
        self._allowed_keys['erlang_ceil'] = not self.hyper_exponent_allowed
        self._allowed_keys['hyper_exponential'] = self.hyper_exponent_allowed

        self._recalc_mean_std_approximations()

    def _set_sample_count(self, sample_count):
        if self._sample_count == sample_count:
            return
        self._sample_count = sample_count
        self._recalc_mean_std_approximations()

    def _set_bucket_count(self, bucket_count):
        if self._bucket_count == bucket_count:
            return
        self._bucket_count = bucket_count

    def _set_hyper_exponent_q1(self, hyper_exponent_qmin):
        self._hyper_exponent_q1 = hyper_exponent_qmin
        self._recalc_hyper_exponents()

    def _set_hyper_exponent_q2(self, hyper_exponent_qmax):
        self._hyper_exponent_q2 = hyper_exponent_qmax
        self._recalc_hyper_exponents()

    def _set_hyper_exponent_count(self, hyper_exponent_count):
        if self._hyper_exponent_count == hyper_exponent_count: return
        self._hyper_exponent_count = hyper_exponent_count
        self._recalc_hyper_exponents()

    def _set_used_keys(self, used_keys):
        self._used_keys = used_keys

    possible_variants = property(fget=_get_possible_variants)
    variant_id = property(fset=_set_variant_id)
    allowed_keys = property(fget=_get_allowed_keys)
    results = property(fget=_get_results)
    used_keys = property(fset=_set_used_keys)
    used_results = property(fget=_get_used_results)
    sample_count = property(fget=_get_sample_count, fset=_set_sample_count)
    bucket_count = property(fget=_get_bucket_count, fset=_set_bucket_count)

    hyper_exponent_limit = property(fget=_get_hyper_exponent_limit)
    hyper_exponent_q1 = property(fget=_get_hyper_exponent_q1, fset=_set_hyper_exponent_q1)
    hyper_exponent_q2 = property(fget=_get_hyper_exponent_q2, fset=_set_hyper_exponent_q2)
    hyper_exponent_count = property(fget=_get_hyper_exponent_count, fset=_set_hyper_exponent_count)
    hyper_exponent_allowed = property(fget=_is_hyper_exponent_allowed)

    def make_plots(self):
        if self._fig_hist is not None:
            plt.close(self._fig_hist)
        self._fig_hist, ax = plt.subplots()
        used_results = self.used_results
        values = [r.series for r in used_results]
        names = [r.name for r in used_results]
        if len(values) > 1:
            ax.hist(np.array(values, dtype=object), density=True, bins=self._bucket_count)
        else:
            ax.hist(values[0], density=True, bins=self._bucket_count)
        ax.legend(names)
        self._fig_hist.show()
