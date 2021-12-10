import wx.grid
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg
import approximations
import processing

approximation_checkboxes = {}
table: wx.grid.Grid
table_frame: wx.MiniFrame

precision = 2


def update_table():
    needed_cols = len(processing.used_series)
    if needed_cols < table.NumberCols:
        table.DeleteCols(1, table.NumberCols - needed_cols)
    elif needed_cols > table.NumberCols:
        table.AppendCols(needed_cols - table.NumberCols)

    col = 0
    for key in processing.sort_order:
        if key not in processing.used_series:
            continue
        info = processing.info[key]
        table.SetColLabelValue(col, f"{info['name']}")
        table.SetCellValue(0, col, f"{info['mean']:0.{precision}f}")
        table.SetCellValue(1, col, f"{info['mean']:0.{precision}f} ± {info['epsilon'][0.90]:0.{precision}f}")
        table.SetCellValue(2, col, f"{info['mean']:0.{precision}f} ± {info['epsilon'][0.95]:0.{precision}f}")
        table.SetCellValue(3, col, f"{info['mean']:0.{precision}f} ± {info['epsilon'][0.99]:0.{precision}f}")
        table.SetCellValue(4, col, f"{info['var']:0.{precision}f}")
        table.SetCellValue(5, col, f"{info['std']:0.{precision}f}")
        table.SetCellValue(6, col, f"{info['coeff_var']:0.{precision}f}")
        col += 1
    table.Fit()
    table_frame.Fit()


def handle_variant(evt):
    processing.update_variant(evt.String)
    used = {key: cb.Value for key, cb in approximation_checkboxes.items()}
    processing.update_used_approximations(used)
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


app = wx.App()
settings_frame = wx.Frame(None, title='Проверка лабораторной 1')
table_frame = wx.MiniFrame(settings_frame, title='Статистические параметры', style=wx.CAPTION)

variant_ctrl = wx.ComboBox(settings_frame, choices=processing.all_variants.columns)
precision_ctrl = wx.SpinCtrl(settings_frame, min=0, max=20, initial=precision)
sample_count_ctrl = wx.SpinCtrl(settings_frame, min=1, max=100_000, initial=processing.sample_count)
bucket_count_ctrl = wx.SpinCtrl(settings_frame, min=1, max=1000, initial=processing.bucket_count)

variant_ctrl.Bind(wx.EVT_COMBOBOX, handle_variant)
precision_ctrl.Bind(wx.EVT_SPINCTRL, handle_precision)
sample_count_ctrl.Bind(wx.EVT_SPINCTRL, handle_sample_count)
bucket_count_ctrl.Bind(wx.EVT_SPINCTRL, handle_bucket_count)

variant_label = wx.StaticText(settings_frame, label='Вариант')
precision_label = wx.StaticText(settings_frame, label='Цифры после запятой')
sample_count_label = wx.StaticText(settings_frame, label='Количество проб')
bucket_count_label = wx.StaticText(settings_frame, label='Размер гистограммы')

settings_sizer = wx.GridBagSizer(2, hgap=10)
settings_sizer.Add(variant_ctrl, (0, 0), flag=wx.EXPAND | wx.ALIGN_CENTER_VERTICAL)
settings_sizer.Add(precision_ctrl, (1, 0), flag=wx.EXPAND | wx.ALIGN_CENTER_VERTICAL)
settings_sizer.Add(sample_count_ctrl, (2, 0), flag=wx.EXPAND | wx.ALIGN_CENTER_VERTICAL)
settings_sizer.Add(bucket_count_ctrl, (3, 0), flag=wx.EXPAND | wx.ALIGN_CENTER_VERTICAL)

settings_sizer.Add(variant_label, (0, 1), flag=wx.EXPAND | wx.ALIGN_CENTER_VERTICAL)
settings_sizer.Add(precision_label, (1, 1), flag=wx.EXPAND | wx.ALIGN_CENTER_VERTICAL)
settings_sizer.Add(sample_count_label, (2, 1), flag=wx.EXPAND | wx.ALIGN_CENTER_VERTICAL)
settings_sizer.Add(bucket_count_label, (3, 1), flag=wx.EXPAND | wx.ALIGN_CENTER_VERTICAL)

for i, key in enumerate(approximations.all_distributions):
    checkbox = wx.CheckBox(settings_frame, label=key, name=key)
    approximation_checkboxes[key] = checkbox
    checkbox.Bind(wx.EVT_CHECKBOX, toggle_approximation)
    settings_sizer.Add(checkbox, (i + 4, 0), (1, 2), flag=wx.EXPAND)

settings_sizer.Fit(settings_frame)
settings_frame.Sizer = settings_sizer


table = wx.grid.Grid(table_frame)
table.EnableEditing(False)
table.CreateGrid(7, 0)
# table.SetColLabelValue(0, 'Последовательность по варианту')
table.SetRowLabelValue(0, 'Мат. ож.')
table.SetRowLabelValue(1, 'Дов. инт. (p=0.90)')
table.SetRowLabelValue(2, 'Дов. инт. (p=0.95)')
table.SetRowLabelValue(3, 'Дов. инт. (p=0.99)')
table.SetRowLabelValue(4, 'Дисперсия')
table.SetRowLabelValue(5, 'С.к.о.')
table.SetRowLabelValue(6, 'К. вар.')
table.ColLabelSize = wx.grid.GRID_AUTOSIZE
table.RowLabelSize = wx.grid.GRID_AUTOSIZE


table_frame.Show()
settings_frame.Show()
app.MainLoop()
