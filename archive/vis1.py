from bokeh.plotting import figure, show, save
from bokeh.models import Plot, Label
from bokeh.models.glyphs import Text
from bokeh.layouts import column, Row


def pingala(m, size=2):

    if m < size:
        return [[0] * m]
    elif m == size:
        return [[0] * size, [1] * size]
    else:
        result = []
        seeds = [[0] * size]
        seeds += [[0] * i + [1] * size for i in range(size)]
        for seed in seeds:
            for item in pingala(m - len(seed), size):
                if not len(seed + item) > m:
                    result.append(seed + item)
        return result


size = 2
results = pingala(10, size)


def find_first_non_zero(mylist):
    i = 0
    while i < len(mylist):
        if mylist[i] != 0:
            return i
        else:
            i = i + 1
    return 0


results.sort(key=lambda x: (
    x[-1] == 1,
    sum(x),
    find_first_non_zero(x),
))

fig = figure(toolbar_location=None)
fig.axis.visible = False
fig.xgrid.visible = False
fig.ygrid.visible = False
fig.outline_line_color = None
for height_id, result in enumerate(results):
    i = 0
    while i < len(result):
        if result[i] == 1:
            fig.rect(x=i + size / 4,
                     y=height_id,
                     width=size - .05,
                     height=0.6,
                     color='red')
            i = i + size
        else:
            fig.rect(x=i, y=height_id, width=0.95, height=0.6, color='navy')
            i = i + 1

text = figure(toolbar_location=None)
text.axis.visible = False
text.xgrid.visible = False
text.ygrid.visible = False
text.outline_line_color = None
text.add_layout(
    Label(x=text.plot_width / 2,
          y=text.plot_height / 2,
          x_units='screen',
          y_units='screen',
          text=str(len(results)),
          text_align="center",
          render_mode='css',
          text_font_size='100pt'))

save(Row(fig, text))
