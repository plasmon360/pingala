from collections import defaultdict
from bokeh.plotting import figure, show, save
from bokeh.models import Plot, Label, CDSView, Filter, Slider, CustomJS, CustomJSFilter
from bokeh.models.glyphs import Text
from bokeh.layouts import column, Row
from bokeh.models import ColumnDataSource
from bokeh.models.widgets import Div

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


def find_first_non_zero(mylist):
    i = 0
    while i < len(mylist):
        if mylist[i] != 0:
            return i
        else:
            i = i + 1
    return 0


size = 2

data = defaultdict(list)
slider_initial_val = 2
slider_final_val = 13

for word_length in range(slider_initial_val, slider_final_val+1):
    results = pingala(word_length, size)

    results.sort(key=lambda x: (
        x[-1] == 1,
        sum(x),
        find_first_non_zero(x),
    ))

    for height_id, result in enumerate(results):
        i = 0
        while i < len(result):
            if result[i] == 1:
                data['x'].append(i + size / 4)
                data['type'].append('long')
                i = i + size
            else:
                data['x'].append(i)
                data['type'].append('short')
                i = i + 1
            data['y'].append(height_id)
            data['word_length'].append(word_length)

source = ColumnDataSource(data)
text = Div(text="""<font size="4">""" + str(slider_initial_val) + """</font>""", )

# Create the slider that modifies the filtered indices
# I am just creating one that shows 0 to 100% of the existing data rows
slider = Slider(start=slider_initial_val, end=slider_final_val, value=2., step=1, title="Word Length")

# This callback is crucial, otherwise the filter will not be triggered when the slider changes
callback = CustomJS(args=dict(source=source,text = text,slider = slider),
                    code="""
            var columns= [];
            for (var i = 0; i <= source.data['word_length'].length; i++){
                if (source.data['word_length'][i] == slider.value) {
                    columns.push(source.data['y'][i]);
                }
            }
    var uniqueItems = Array.from(new Set(columns));
     text.text = "<font size=40>" + uniqueItems.length+ "</font>";
    source.change.emit();
""")
slider.js_on_change('value', callback)

# Define the custom filter to return the indices from 0 to the desired percentage of total data rows. You could also compare against values in source.data
js_filter = CustomJSFilter(args=dict(slider=slider, text = text),
                           code='''
            var indices = [];
            for (var i = 0; i <= source.data['word_length'].length; i++){
                if (source.data['word_length'][i] == slider.value) {
                    indices.push(i)
                }
            }
            return indices
''')
# Use the filter in a view
long_filter = Filter([item == 'long' for item in data['type']])
long_view = CDSView(source=source, filters=[long_filter, js_filter])
short_filter = Filter([item == 'short' for item in data['type']])
short_view = CDSView(source=source, filters=[short_filter, js_filter])

fig = figure(toolbar_location=None)
fig.axis.visible = False
fig.xgrid.visible = False
fig.ygrid.visible = False
fig.outline_line_color = None
fig.rect(x='x',
         y='y',
         source=source,
         view=long_view,
         width=size - .05,
         height=0.6,
         color='red')
fig.rect(x='x',
         y='y',
         source=source,
         view=short_view,
         width=0.95,
         height=0.6,
         color='navy')




save(Row(slider, fig,text))
