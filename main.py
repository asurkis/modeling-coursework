import wx.grid

import approximations

app = wx.App()
frame = wx.Frame(None, title='Проверка лабораторной № 1')

checkbox_frame = wx.MiniFrame(frame, title='Выбор приближений', style=wx.CAPTION)

approximation_checkboxes = wx.BoxSizer(wx.VERTICAL)
for key in approximations.casual:
    checkbox = wx.CheckBox(checkbox_frame, label=key)
    evt = wx.CommandEvent()
    evt.GetClientObject()
    checkbox.Bind(wx.EVT_CHECKBOX, lambda x: print(f'Triggered {key} ({x.IsChecked()})'))
    approximation_checkboxes.Add(checkbox)

approximation_checkboxes.Fit(checkbox_frame)
checkbox_frame.SetSizer(approximation_checkboxes)
checkbox_frame.Show()

table_frame = wx.MiniFrame(frame, title='Статистические параметры', style=wx.CAPTION)
table = wx.grid.Grid(table_frame)
table.EnableEditing(False)
table.CreateGrid(5, 2)
table.SetColLabelValue(1, 'col label')
table.SetRowLabelValue(2, 'row label')
table_frame.Show()

frame.Show()
app.MainLoop()
