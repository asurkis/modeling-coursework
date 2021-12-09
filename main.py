import numpy as np
import wx
from matplotlib import pyplot as plt
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg

app = wx.App()
frame = wx.Frame(None, title='Hello, world!')

fig, ax = plt.subplots(figsize=(8, 6), dpi=108)
ax.plot(np.linspace(0, 5, 10), np.linspace(5, 0, 10))

canvas = FigureCanvasWxAgg(frame, wx.ID_ANY, figure=fig)
sizer = wx.BoxSizer()
sizer.Add(canvas)
sizer.Fit(frame)

frame.Show()
app.MainLoop()
                                                                        