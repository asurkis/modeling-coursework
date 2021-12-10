import wx.grid
import approximations


def update_sample_count(evt):
    print(f'update sample count: {evt.Int}')


def update_plots(evt):
    print(f'update bucket count: {evt.Int}')


app = wx.App()
settings_frame = wx.Frame(None, title='Проверка лабораторной 1')
plot_frame = wx.MiniFrame(settings_frame, title='Настройки', style=wx.CAPTION)
table_frame = wx.MiniFrame(settings_frame, title='Статистические параметры', style=wx.CAPTION)

settings_sizer = wx.GridBagSizer(2, hgap=10)
sample_count_ctrl = wx.SpinCtrl(settings_frame, min=1, max=100_000, style=wx.EXPAND)
bucket_count_ctrl = wx.SpinCtrl(settings_frame, min=1, max=1000, style=wx.EXPAND)
settings_sizer.Add(sample_count_ctrl, (0, 0), flag=wx.EXPAND | wx.ALIGN_CENTER_VERTICAL)
settings_sizer.Add(bucket_count_ctrl, (1, 0), flag=wx.EXPAND | wx.ALIGN_CENTER_VERTICAL)
settings_sizer.Add(wx.StaticText(settings_frame, label='Количество проб'), (0, 1), flag=wx.EXPAND | wx.ALIGN_CENTER_VERTICAL)
settings_sizer.Add(wx.StaticText(settings_frame, label='Размер гистограммы'), (1, 1), flag=wx.EXPAND | wx.ALIGN_CENTER_VERTICAL)

sample_count_ctrl.Bind(wx.EVT_SPINCTRL, update_sample_count)
bucket_count_ctrl.Bind(wx.EVT_SPINCTRL, update_plots)

for i, key in enumerate(approximations.casual):
    checkbox = wx.CheckBox(settings_frame, label=key)
    evt = wx.CommandEvent()
    evt.GetClientObject()
    checkbox.Bind(wx.EVT_CHECKBOX, lambda x: print(f'Triggered {key} ({x.IsChecked()})'))
    settings_sizer.Add(checkbox, (i + 2, 0), (1, 2), flag=wx.EXPAND)

settings_sizer.Fit(settings_frame)
settings_frame.Sizer = settings_sizer

table = wx.grid.Grid(table_frame)
table.EnableEditing(False)
table.CreateGrid(5, 2)
table.SetColLabelValue(1, 'col label')
table.SetRowLabelValue(2, 'row label')

# table_frame.Show()
# plot_frame.Show()
settings_frame.Show()
app.MainLoop()
