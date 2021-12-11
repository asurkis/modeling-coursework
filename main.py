import wx.grid
import approximations
import processing

model = processing.MathModel()
precision = 2

app = wx.App()
settings_frame = wx.Frame(None, title='Проверка лабораторной 1', style=wx.DEFAULT_FRAME_STYLE & ~wx.RESIZE_BORDER)
stats_table_frame = wx.MiniFrame(settings_frame, title='Статистические параметры', style=wx.CAPTION)

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

variant_ctrl = wx.ComboBox(settings_frame, choices=model.possible_variants)
precision_ctrl = wx.SpinCtrl(settings_frame, min=0, max=20, initial=precision)
sample_count_ctrl = wx.SpinCtrl(settings_frame, min=1, max=100_000, initial=model.sample_count)
bucket_count_ctrl = wx.SpinCtrl(settings_frame, min=1, max=1000, initial=model.bucket_count)

base_controls = [
    precision_ctrl,
    sample_count_ctrl,
    bucket_count_ctrl
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
sample_count_label = wx.StaticText(settings_frame, label='Количество проб')
bucket_count_label = wx.StaticText(settings_frame, label='Размер гистограммы')
hyper_exponents_q1_label = wx.StaticText(settings_frame, label='q (от)')
hyper_exponents_q2_label = wx.StaticText(settings_frame, label='q (до)')
hyper_exponents_count_label = wx.StaticText(settings_frame, label='Количество гиперэкспонент')

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
approximation_checkboxes = {}
for i, (key, label) in enumerate(basic_names.items()):
    checkbox = wx.CheckBox(settings_frame, label=label, name=key)
    approximation_checkboxes[key] = checkbox
    checkbox.Enable(False)
    settings_sizer.Add(checkbox, (i + 4, 0), (1, 2), flag=wx.EXPAND)

hyper_exponent_controls = [
    approximation_checkboxes['hyper_exponential'],
    hyper_exponents_q1_ctrl,
    hyper_exponents_q2_ctrl,
    hyper_exponents_count_ctrl,
]
for widget in hyper_exponent_controls:
    widget.Enable(False)

settings_sizer.Add(hyper_exponents_q1_ctrl, (len(approximations.all_distributions) + 4, 0),
                   flag=wx.EXPAND | wx.ALIGN_CENTER_VERTICAL)
settings_sizer.Add(hyper_exponents_q2_ctrl, (len(approximations.all_distributions) + 5, 0),
                   flag=wx.EXPAND | wx.ALIGN_CENTER_VERTICAL)
settings_sizer.Add(hyper_exponents_count_ctrl, (len(approximations.all_distributions) + 6, 0),
                   flag=wx.EXPAND | wx.ALIGN_CENTER_VERTICAL)

settings_sizer.Add(hyper_exponents_q1_label, (len(approximations.all_distributions) + 4, 1),
                   flag=wx.EXPAND | wx.ALIGN_CENTER_VERTICAL)
settings_sizer.Add(hyper_exponents_q2_label, (len(approximations.all_distributions) + 5, 1),
                   flag=wx.EXPAND | wx.ALIGN_CENTER_VERTICAL)
settings_sizer.Add(hyper_exponents_count_label, (len(approximations.all_distributions) + 6, 1),
                   flag=wx.EXPAND | wx.ALIGN_CENTER_VERTICAL)


def update_table():
    needed_cols = len(model.used_results)
    if needed_cols < stats_table.NumberCols:
        stats_table.DeleteCols(1, stats_table.NumberCols - needed_cols)
    elif needed_cols > stats_table.NumberCols:
        stats_table.AppendCols(needed_cols - stats_table.NumberCols)

    for col, info in enumerate(model.used_results):
        stats_table.SetColLabelValue(col, f'{info.name}')
        stats_table.SetCellValue(0, col, f'{info.mean:0.{precision}f}')
        stats_table.SetCellValue(1, col, f'{info.mean:0.{precision}f} ± {info.epsilon[0.90]:0.{precision}f}')
        stats_table.SetCellValue(2, col, f'{info.mean:0.{precision}f} ± {info.epsilon[0.95]:0.{precision}f}')
        stats_table.SetCellValue(3, col, f'{info.mean:0.{precision}f} ± {info.epsilon[0.99]:0.{precision}f}')
        stats_table.SetCellValue(4, col, f'{info.var:0.{precision}f}')
        stats_table.SetCellValue(5, col, f'{info.std:0.{precision}f}')
        stats_table.SetCellValue(6, col, f'{info.coeff_var:0.{precision}f}')
    stats_table.Fit()
    stats_table_frame.Fit()


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


variant_ctrl.Bind(wx.EVT_COMBOBOX, handle_variant)
precision_ctrl.Bind(wx.EVT_SPINCTRL, handle_precision)
sample_count_ctrl.Bind(wx.EVT_SPINCTRL, handle_sample_count)
bucket_count_ctrl.Bind(wx.EVT_SPINCTRL, handle_bucket_count)

hyper_exponents_q1_ctrl.Bind(wx.EVT_SPINCTRLDOUBLE, handle_hyper_exponent_qmin)
hyper_exponents_q2_ctrl.Bind(wx.EVT_SPINCTRLDOUBLE, handle_hyper_exponent_qmax)
hyper_exponents_count_ctrl.Bind(wx.EVT_SPINCTRL, handle_hyper_exponent_count)

for checkbox in approximation_checkboxes.values():
    checkbox.Bind(wx.EVT_CHECKBOX, toggle_approximation)

settings_frame.Sizer = settings_sizer
settings_frame.Fit()

stats_table_frame.Show()
settings_frame.Show()
app.MainLoop()
