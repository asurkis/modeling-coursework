import wx.grid
import approximations
import processing

precision = 2

app = wx.App()
settings_frame = wx.Frame(None, title='Проверка лабораторной 1', style=wx.DEFAULT_FRAME_STYLE & ~wx.RESIZE_BORDER)
table_frame = wx.MiniFrame(settings_frame, title='Статистические параметры', style=wx.CAPTION)

table = wx.grid.Grid(table_frame)
table.EnableEditing(False)
table.CreateGrid(7, 0)
table.SetRowLabelValue(0, 'Мат. ож.')
table.SetRowLabelValue(1, 'Дов. инт. (p=0.90)')
table.SetRowLabelValue(2, 'Дов. инт. (p=0.95)')
table.SetRowLabelValue(3, 'Дов. инт. (p=0.99)')
table.SetRowLabelValue(4, 'Дисперсия')
table.SetRowLabelValue(5, 'С.к.о.')
table.SetRowLabelValue(6, 'К. вар.')
table.ColLabelSize = wx.grid.GRID_AUTOSIZE
table.RowLabelSize = wx.grid.GRID_AUTOSIZE
table.SetDefaultCellAlignment(wx.ALIGN_RIGHT, wx.ALIGN_CENTER_VERTICAL)

variant_ctrl = wx.ComboBox(settings_frame, choices=processing.all_variants.columns)
precision_ctrl = wx.SpinCtrl(settings_frame, min=0, max=20, initial=precision)
sample_count_ctrl = wx.SpinCtrl(settings_frame, min=1, max=100_000, initial=processing.sample_count)
bucket_count_ctrl = wx.SpinCtrl(settings_frame, min=1, max=1000, initial=processing.bucket_count)

base_controls = [
    precision_ctrl,
    sample_count_ctrl,
    bucket_count_ctrl
]
for widget in base_controls:
    widget.Enable(False)

hyper_exponents_qmin_ctrl = wx.SpinCtrlDouble(settings_frame, min=0, max=1, inc=0.0001)
hyper_exponents_qmax_ctrl = wx.SpinCtrlDouble(settings_frame, min=0, max=1, inc=0.0001)
hyper_exponents_count_ctrl = wx.SpinCtrl(settings_frame, min=1, max=10, initial=processing.hyper_exponent_count)

variant_label = wx.StaticText(settings_frame, label='Вариант')
precision_label = wx.StaticText(settings_frame, label='Цифры после запятой')
sample_count_label = wx.StaticText(settings_frame, label='Количество проб')
bucket_count_label = wx.StaticText(settings_frame, label='Размер гистограммы')
hyper_exponents_qmin_label = wx.StaticText(settings_frame, label='q (min)')
hyper_exponents_qmax_label = wx.StaticText(settings_frame, label='q (max)')
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
    hyper_exponents_qmin_ctrl,
    hyper_exponents_qmax_ctrl,
    hyper_exponents_count_ctrl,
]
for widget in hyper_exponent_controls:
    widget.Enable(False)

settings_sizer.Add(hyper_exponents_qmin_ctrl, (len(approximations.all_distributions) + 4, 0), flag=wx.EXPAND)
settings_sizer.Add(hyper_exponents_qmax_ctrl, (len(approximations.all_distributions) + 5, 0), flag=wx.EXPAND)
settings_sizer.Add(hyper_exponents_count_ctrl, (len(approximations.all_distributions) + 6, 0), flag=wx.EXPAND)

settings_sizer.Add(hyper_exponents_qmin_label, (len(approximations.all_distributions) + 4, 1), flag=wx.EXPAND)
settings_sizer.Add(hyper_exponents_qmax_label, (len(approximations.all_distributions) + 5, 1), flag=wx.EXPAND)
settings_sizer.Add(hyper_exponents_count_label, (len(approximations.all_distributions) + 6, 1), flag=wx.EXPAND)


def update_table():
    needed_cols = len(processing.used_series)
    if needed_cols < table.NumberCols:
        table.DeleteCols(1, table.NumberCols - needed_cols)
    elif needed_cols > table.NumberCols:
        table.AppendCols(needed_cols - table.NumberCols)

    col = 0
    for key in processing.used_series:
        info = processing.results[key]
        table.SetColLabelValue(col, f'{info.name}')
        table.SetCellValue(0, col, f'{info.mean:0.{precision}f}')
        table.SetCellValue(1, col, f'{info.mean:0.{precision}f} ± {info.epsilon[0.90]:0.{precision}f}')
        table.SetCellValue(2, col, f'{info.mean:0.{precision}f} ± {info.epsilon[0.95]:0.{precision}f}')
        table.SetCellValue(3, col, f'{info.mean:0.{precision}f} ± {info.epsilon[0.99]:0.{precision}f}')
        table.SetCellValue(4, col, f'{info.var:0.{precision}f}')
        table.SetCellValue(5, col, f'{info.std:0.{precision}f}')
        table.SetCellValue(6, col, f'{info.coeff_var:0.{precision}f}')
        col += 1
    table.Fit()
    table_frame.Fit()


def handle_variant(evt):
    processing.update_variant(evt.String)
    used = {key: cb.Value for key, cb in approximation_checkboxes.items()}
    processing.update_used_approximations(used)

    for key, cb in approximation_checkboxes.items():
        if key in processing.results:
            cb.Label = processing.results[key].name
        cb.Enable(key in processing.results)

    for widget in base_controls:
        widget.Enable()

    for widget in hyper_exponent_controls:
        widget.Enable(bool(processing.hyper_exponent_allowed()))

    settings_sizer.Fit(settings_frame)
    update_table()


def handle_precision(evt):
    global precision
    precision = evt.Int
    update_table()


def handle_sample_count(evt):
    processing.update_sample_count(evt.Int)
    update_table()


def handle_bucket_count(evt):
    processing.update_bucket_count(evt.Int)


def toggle_approximation(evt):
    used = {key: cb.Value for key, cb in approximation_checkboxes.items()}
    processing.update_used_approximations(used)
    update_table()


def handle_hyper_exponent(evt):
    processing.update_hyper_exponent(hyper_exponents_qmin_ctrl.Value,
                                     hyper_exponents_qmax_ctrl.Value,
                                     hyper_exponents_count_ctrl.Value)
    update_table()


variant_ctrl.Bind(wx.EVT_COMBOBOX, handle_variant)
precision_ctrl.Bind(wx.EVT_SPINCTRL, handle_precision)
sample_count_ctrl.Bind(wx.EVT_SPINCTRL, handle_sample_count)
bucket_count_ctrl.Bind(wx.EVT_SPINCTRL, handle_bucket_count)

hyper_exponents_qmin_ctrl.Bind(wx.EVT_SPINCTRLDOUBLE, handle_hyper_exponent)
hyper_exponents_qmax_ctrl.Bind(wx.EVT_SPINCTRLDOUBLE, handle_hyper_exponent)
hyper_exponents_count_ctrl.Bind(wx.EVT_SPINCTRL, handle_hyper_exponent)

for checkbox in approximation_checkboxes.values():
    checkbox.Bind(wx.EVT_CHECKBOX, toggle_approximation)

settings_frame.Sizer = settings_sizer
settings_frame.Fit()

table_frame.Show()
settings_frame.Show()
app.MainLoop()
