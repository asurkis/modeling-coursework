import wx.grid
import approximations
import processing

model = processing.MathModel()
precision = 2

app = wx.App()
settings_frame = wx.Frame(None, title='Проверка лабораторной 1', style=wx.DEFAULT_FRAME_STYLE & ~wx.RESIZE_BORDER)
stats_table_frame = wx.MiniFrame(settings_frame, title='Статистические параметры', style=wx.CAPTION)
# autocorr_table_frame = wx.MiniFrame(settings_frame, title='Автокорреляция', style=wx.CAPTION)
params_table_frame = wx.MiniFrame(settings_frame, title='Параметры распределений', style=wx.CAPTION)

stats_table = wx.grid.Grid(stats_table_frame)
stats_table.EnableEditing(False)
stats_table.CreateGrid(7, 0)
stats_table.SetRowLabelValue(0, 'Мат. ож.')
stats_table.SetRowLabelValue(1, 'Дов. инт. (p=0.90)')
stats_table.SetRowLabelValue(2, 'Дов. инт. (p=0.95)')
stats_table.SetRowLabelValue(3, 'Дов. инт. (p=0.99)')
stats_table.SetRowLabelValue(4, 'Дисперсия')
stats_table.SetRowLabelValue(5, 'С.к.о.')
stats_table.SetRowLabelValue(6, 'К. вар.')
stats_table.ColLabelSize = wx.grid.GRID_AUTOSIZE
stats_table.RowLabelSize = wx.grid.GRID_AUTOSIZE
stats_table.SetDefaultCellAlignment(wx.ALIGN_RIGHT, wx.ALIGN_CENTER_VERTICAL)

# autocorr_table = wx.grid.Grid(autocorr_table_frame)
# autocorr_table.EnableEditing(False)
# autocorr_table.CreateGrid(0, 0)
# autocorr_table.ColLabelSize = wx.grid.GRID_AUTOSIZE
# autocorr_table.RowLabelSize = wx.grid.GRID_AUTOSIZE
# autocorr_table.SetDefaultCellAlignment(wx.ALIGN_RIGHT, wx.ALIGN_CENTER_VERTICAL)

params_table = wx.grid.Grid(params_table_frame)
params_table.EnableEditing(False)
params_table.CreateGrid(4, 0)
params_table.ColLabelSize = wx.grid.GRID_AUTOSIZE
params_table.RowLabelSize = wx.grid.GRID_AUTOSIZE

variant_ctrl = wx.ComboBox(settings_frame, choices=model.possible_variants)
precision_ctrl = wx.SpinCtrl(settings_frame, min=0, max=20, initial=precision)
sample_count_ctrl = wx.SpinCtrl(settings_frame, min=1, max=100_000, initial=model.sample_count)
bucket_count_ctrl = wx.SpinCtrl(settings_frame, min=1, max=1000, initial=model.bucket_count)

plot_hist_btn = wx.Button(settings_frame, label='Построить гистограммы')
plot_autocorr_btn = wx.Button(settings_frame, label='Построить графики автокорреляции')

base_controls = [
    precision_ctrl,
    sample_count_ctrl,
    bucket_count_ctrl,
    plot_hist_btn,
    plot_autocorr_btn,
]
for widget in base_controls:
    widget.Enable(False)

hyper_exponents_q1_ctrl = wx.SpinCtrlDouble(settings_frame, min=0.001, max=1, inc=0.001,
                                            initial=model.hyper_exponent_q1)
hyper_exponents_q2_ctrl = wx.SpinCtrlDouble(settings_frame, min=0.001, max=1, inc=0.001,
                                            initial=model.hyper_exponent_q2)
hyper_exponents_count_ctrl = wx.SpinCtrl(settings_frame, min=1, max=10, initial=model.hyper_exponent_count)

variant_label = wx.StaticText(settings_frame, label='Вариант')
precision_label = wx.StaticText(settings_frame, label='Цифры после запятой')
sample_count_label = wx.StaticText(settings_frame, label='Размер случайной выборки')
bucket_count_label = wx.StaticText(settings_frame, label='Количество интервалов на гистограмме')
hyper_exponents_q1_label = wx.StaticText(settings_frame,
                                         label='Параметр Q первого гиперэкспоненциального распределения')
hyper_exponents_q2_label = wx.StaticText(settings_frame,
                                         label='Параметр Q последнего гиперэкспоненциального распределения')
hyper_exponents_count_label = wx.StaticText(settings_frame, label='Количество гиперэкспонент')
hyper_exponents_explanation_label = wx.StaticText(settings_frame, label='''
Гиперэкспонента с параметрами Q, t1, t2
с вероятностью Q принимает значение, распределенное по
экспоненциальному закону с математическим ожиданием t1,
и с вероятностью P = 1 - Q — с t2.

Q выбирается у первого и последнего гиперэкспоненциального распределения,
у оставшихся — выбирается линейно. Т.е. из N гиперэкспонент
Q[i] - Q[1] ~ i - 1
Q[i] = Q[1] + (Q[N] - Q[1]) * (i - 1) / (N - 1)

t1 и t2 гиперэкспоненциального распределения
и любые параметры остальных распределений выбираются так,
чтобы математическое ожидание и дисперсия совпали
у распределения и последовательности по варианту.
''')
credits_label = wx.StaticText(settings_frame, label='''
Автор программы: Суркис Антон Игоревич
Тестировщик: Прикота Виталий Александрович
''')

settings_sizer = wx.GridBagSizer(2, hgap=10)
settings_sizer.Add(variant_ctrl, (0, 0), flag=wx.EXPAND | wx.ALIGN_CENTER_VERTICAL)
settings_sizer.Add(precision_ctrl, (1, 0), flag=wx.EXPAND | wx.ALIGN_CENTER_VERTICAL)
settings_sizer.Add(sample_count_ctrl, (2, 0), flag=wx.EXPAND | wx.ALIGN_CENTER_VERTICAL)
settings_sizer.Add(bucket_count_ctrl, (3, 0), flag=wx.EXPAND | wx.ALIGN_CENTER_VERTICAL)

settings_sizer.Add(variant_label, (0, 1), flag=wx.EXPAND | wx.ALIGN_CENTER_VERTICAL)
settings_sizer.Add(precision_label, (1, 1), flag=wx.EXPAND | wx.ALIGN_CENTER_VERTICAL)
settings_sizer.Add(sample_count_label, (2, 1), flag=wx.EXPAND | wx.ALIGN_CENTER_VERTICAL)
settings_sizer.Add(bucket_count_label, (3, 1), flag=wx.EXPAND | wx.ALIGN_CENTER_VERTICAL)

basic_names = {
    'uniform': 'Равномерное распределение',
    'exponential': 'Экспоненциальное распределение',
    'gamma': 'Гамма-распределение',
    'erlang_floor': 'Распределение Эрланга 1',
    'erlang_ceil': 'Распределение Эрланга 2',
    'hyper_exponential': 'Гиперэкспоненциальное распределение',
}
y_shift = 4
approximation_checkboxes = {}
for i, (key, label) in enumerate(basic_names.items()):
    checkbox = wx.CheckBox(settings_frame, label=label, name=key)
    approximation_checkboxes[key] = checkbox
    checkbox.Enable(False)
    settings_sizer.Add(checkbox, (y_shift + i, 0), (1, 2), flag=wx.EXPAND)

hyper_exponent_controls = [
    approximation_checkboxes['hyper_exponential'],
    hyper_exponents_q1_ctrl,
    hyper_exponents_q2_ctrl,
    hyper_exponents_count_ctrl,
]
for widget in hyper_exponent_controls:
    widget.Enable(False)

y_shift = len(approximations.all_distributions) + 4
settings_sizer.Add(hyper_exponents_q1_ctrl, (y_shift + 0, 0), flag=wx.EXPAND | wx.ALIGN_CENTER_VERTICAL)
settings_sizer.Add(hyper_exponents_q2_ctrl, (y_shift + 1, 0), flag=wx.EXPAND | wx.ALIGN_CENTER_VERTICAL)
settings_sizer.Add(hyper_exponents_count_ctrl, (y_shift + 2, 0), flag=wx.EXPAND | wx.ALIGN_CENTER_VERTICAL)

settings_sizer.Add(hyper_exponents_q1_label, (y_shift + 0, 1), flag=wx.EXPAND | wx.ALIGN_CENTER_VERTICAL)
settings_sizer.Add(hyper_exponents_q2_label, (y_shift + 1, 1), flag=wx.EXPAND | wx.ALIGN_CENTER_VERTICAL)
settings_sizer.Add(hyper_exponents_count_label, (y_shift + 2, 1), flag=wx.EXPAND | wx.ALIGN_CENTER_VERTICAL)

settings_sizer.Add(plot_hist_btn, (y_shift + 3, 0), (1, 2), flag=wx.EXPAND)
settings_sizer.Add(plot_autocorr_btn, (y_shift + 4, 0), (1, 2), flag=wx.EXPAND)

settings_sizer.Add(hyper_exponents_explanation_label, (y_shift + 5, 0), (1, 2), flag=wx.EXPAND)
settings_sizer.Add(credits_label, (y_shift + 6, 0), (1, 2), flag=wx.EXPAND)

def adjust_table_size(table: wx.grid.Grid, required_rows: int, required_cols: int):
    if table.NumberCols < required_cols:
        table.AppendCols(required_cols - table.NumberCols)
    elif table.NumberCols > required_cols:
        table.DeleteCols(0, table.NumberCols - required_cols)

    if table.NumberRows < required_rows:
        table.AppendRows(required_rows - table.NumberRows)
    elif table.NumberRows > required_rows:
        table.DeleteRows(0, table.NumberRows - required_rows)


def update_table():
    used_results = model.used_results
    adjust_table_size(stats_table, 7, len(used_results))
    # adjust_table_size(autocorr_table, 0, len(used_results))
    adjust_table_size(params_table, 4, len(used_results) - 1)

    for col, info in enumerate(used_results):
        stats_table.SetColLabelValue(col, f'{info.name}')
        stats_table.SetCellValue(0, col, f'{info.mean:0.{precision}f}')
        stats_table.SetCellValue(1, col, f'{info.mean:0.{precision}f} ± {info.epsilon["0.90"]:0.{precision}f}')
        stats_table.SetCellValue(2, col, f'{info.mean:0.{precision}f} ± {info.epsilon["0.95"]:0.{precision}f}')
        stats_table.SetCellValue(3, col, f'{info.mean:0.{precision}f} ± {info.epsilon["0.99"]:0.{precision}f}')
        stats_table.SetCellValue(4, col, f'{info.var:0.{precision}f}')
        stats_table.SetCellValue(5, col, f'{info.std:0.{precision}f}')
        stats_table.SetCellValue(6, col, f'{info.coeff_var:0.{precision}f}')

        # autocorr_table.SetColLabelValue(col, f'{info.name}')

        if col >= 1:
            for row, (key, val) in enumerate(info.params.items()):
                params_table.SetColLabelValue(col - 1, f'{info.name}')
                params_table.SetCellValue(row, col - 1, f'{key} = {val:0.{precision}f}')

    stats_table.Fit()
    # autocorr_table.Fit()
    params_table.Fit()
    stats_table_frame.Fit()
    # autocorr_table_frame.Fit()
    params_table_frame.Fit()


def handle_variant(evt):
    model.variant_id = evt.String
    model.used_keys = {key: cb.Value for key, cb in approximation_checkboxes.items()}

    for key, cb in approximation_checkboxes.items():
        if model.allowed_keys[key] and key in model.results:
            cb.Label = model.results[key].name
        cb.Enable(bool(model.allowed_keys[key]))

    for widget in base_controls:
        widget.Enable()

    for widget in hyper_exponent_controls:
        widget.Enable(bool(model.hyper_exponent_allowed))

    hyper_exponents_q1_ctrl.Max = model.hyper_exponent_limit
    hyper_exponents_q2_ctrl.Max = model.hyper_exponent_limit

    settings_sizer.Fit(settings_frame)
    update_table()


def handle_precision(evt):
    global precision
    precision = evt.Int
    update_table()


def handle_sample_count(evt):
    model.sample_count = evt.Int
    update_table()


def handle_bucket_count(evt):
    model.bucket_count = evt.Int


def toggle_approximation(evt):
    model.used_keys = {key: cb.Value for key, cb in approximation_checkboxes.items()}
    update_table()


def handle_hyper_exponent_qmin(evt):
    model.hyper_exponent_q1 = evt.Value
    update_table()


def handle_hyper_exponent_qmax(evt):
    model.hyper_exponent_q2 = evt.Value
    update_table()


def handle_hyper_exponent_count(evt):
    model.hyper_exponent_count = evt.Int
    update_table()


def handle_plot_histograms(evt):
    model.plot_histograms()


def handle_plot_autocorr(evt):
    model.plot_autocorr()


variant_ctrl.Bind(wx.EVT_COMBOBOX, handle_variant)
precision_ctrl.Bind(wx.EVT_SPINCTRL, handle_precision)
sample_count_ctrl.Bind(wx.EVT_SPINCTRL, handle_sample_count)
bucket_count_ctrl.Bind(wx.EVT_SPINCTRL, handle_bucket_count)

plot_hist_btn.Bind(wx.EVT_BUTTON, handle_plot_histograms)
plot_autocorr_btn.Bind(wx.EVT_BUTTON, handle_plot_autocorr)

hyper_exponents_q1_ctrl.Bind(wx.EVT_SPINCTRLDOUBLE, handle_hyper_exponent_qmin)
hyper_exponents_q2_ctrl.Bind(wx.EVT_SPINCTRLDOUBLE, handle_hyper_exponent_qmax)
hyper_exponents_count_ctrl.Bind(wx.EVT_SPINCTRL, handle_hyper_exponent_count)

for checkbox in approximation_checkboxes.values():
    checkbox.Bind(wx.EVT_CHECKBOX, toggle_approximation)

settings_frame.Sizer = settings_sizer
settings_sizer.Fit(settings_frame)
# settings_frame.Fit()

params_table_frame.Show()
# autocorr_table_frame.Show()
stats_table_frame.Show()
settings_frame.Show()
app.MainLoop()
