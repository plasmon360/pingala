import pandas as pd
from bokeh.io import curdoc
from collections import defaultdict
from bokeh.plotting import figure, show, save
from bokeh.models import Plot, Label, CDSView, Filter, Slider, CustomJS, CustomJSFilter, GroupFilter, BooleanFilter
from bokeh.models.glyphs import Text
from bokeh.layouts import column, Row, layout
from bokeh.models import ColumnDataSource
from bokeh.models.widgets import Div
from bokeh.transform import factor_cmap


def pingala(m, size=2):
    # Generates all the possible pingala combinations
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
    # Find the index of the first non zero in mylist or else return 0
    i = 0
    while i < len(mylist):
        if mylist[i] != 0:
            return i
        else:
            i = i + 1
    return 0


size = 2
slider_initial_val = 5
slider_final_val = 10
data = defaultdict(list)

for word_length in range(slider_initial_val - 2, slider_final_val + 1):
    results = pingala(word_length, size)

    # Sort the results by based on if a particular result 1)ends with long, 2) sum of long
    # 3) occurrence of the first long
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
                data['width'].append(2 - 0.05)
                i = i + size
            else:
                data['x'].append(i)
                data['type'].append('short')
                data['width'].append(1 - 0.05)
                i = i + 1
            data['y'].append(height_id)
            data['word_length'].append(word_length)
            data['ends_with_long'].append(result[-1] == 1)

source = ColumnDataSource(data)

all_combinations = Div(text="""<span class="display-1">""" +
                       str(len(pingala(slider_initial_val))) + """</span>""",
                       name='all_combinations')
all_combinations.css_classes = ['combinations_style1']

word_length_div = Div(text="""<span class="display-3">""" +
                      str(slider_initial_val) + """</span>""",
                      name='word_length')
word_length_div.css_classes = ['wordlength_style1']

all_combinations_1 = Div(text="""<span class="display-2">""" +
                         str(len(pingala(slider_initial_val-1))) + """</span>""",
                         name='all_combinations_1')

all_combinations_1.css_classes = ['combinations_style1']

word_length_div_1 = Div(text="""<span class="display-3">""" +
                        str(slider_initial_val - 1) + """</span>""",
                        name='word_length_1')

all_combinations_2 = Div(text="""<span class="display-2">""" +
                         str(len(pingala(slider_initial_val-2))) + """</span>""",
                         name='all_combinations_2')

word_length_div_2 = Div(text="""<span class="display-3">""" +
                        str(slider_initial_val - 2) + """</span>""",
                        name='word_length_2')
all_combinations_2.css_classes = ['combinations_style1']

#
# Create the slider that modifies the filtered indices
# Create the slider that modifies the filtered indices
# I am just creating one that shows 0 to 100% of the existing data rows
slider = Slider(start=slider_initial_val,
                end=slider_final_val,
                value=slider_initial_val,
                step=1,
                title="Word Length",
                name='word_length_slider',
                sizing_mode='stretch_width')

# This callback is crucial, otherwise the filter will not be triggered when the slider changes
callback = CustomJS(args=dict(source=source,
                              all_combinations=all_combinations,
                              word_length_div=word_length_div,
                              all_combinations_1=all_combinations_1,
                              word_length_div_1=word_length_div_1,
                              all_combinations_2=all_combinations_2,
                              word_length_div_2=word_length_div_2,
                              slider=slider),
                    code="""
            var columns= [];
            var columns_1 = [];
            var columns_2 = [];
            for (var i = 0; i <= source.data['word_length'].length; i++){
                if (source.data['word_length'][i] == slider.value) {
                    columns.push(source.data['y'][i]);
                }
                if (source.data['word_length'][i] == slider.value-1) {
                    columns_1.push(source.data['y'][i]);
                }
                if (source.data['word_length'][i] == slider.value-2) {
                    columns_2.push(source.data['y'][i]);
                }

            }
    var uniqueItems = Array.from(new Set(columns));
     all_combinations.text = "<span class= display-1> " + uniqueItems.length+ "</span>";

    var uniqueItems_1 = Array.from(new Set(columns_1));
     all_combinations_1.text = "<span class= display-2> " + uniqueItems_1.length+ "</span>";

    var uniqueItems_2 = Array.from(new Set(columns_2));
     all_combinations_2.text = "<span class= display-2> " + uniqueItems_2.length+ "</span>";


     word_length_div.text = "<span class= display-3> " +slider.value+ "</span>";
     word_length_div_1.text = "<span class= display-3> " +(slider.value-1)+ "</span>";

     word_length_div_2.text = "<span class= display-3> " +(slider.value-2)+ "</span>";


    source.change.emit();
""")
slider.js_on_change('value', callback)


def js_filter(modifier, slider, source):
    code = '''
                var indices = [];
                for (var i = 0; i <= source.data['word_length'].length; i++){{
                    if (source.data['word_length'][i] == slider.value-{0}) {{
                        indices.push(i)
                    }}
                }}
                return indices
        '''.format(modifier)

    return CustomJSFilter(args=dict(slider=slider, source=source), code=code)


def main_fig(name, view, height, width=400):

    fig = figure(
        toolbar_location=None,
        name=name,
    )
    fig.axis.visible = False
    fig.xgrid.visible = False
    fig.ygrid.visible = False
    fig.outline_line_color = 'Blue'
    fig.min_border = 0
    fig.x_range.range_padding = 0
    fig.y_range.range_padding = 0.03
    fig.plot_height = height
    fig.sizing_mode = "stretch_both"
    groups = ['long', 'short']
    fig.rect(x='x',
             y='y',
             source=source,
             view=view,
             width='width',
             height=0.7,
             alpha=0.8,
             color=factor_cmap(field_name='type',
                               palette=['red', 'grey'],
                               factors=groups))
    return fig


HEIGHT = 500
# fig_n_not_long_ending = myfig(
#    name="fig_n",
#    view=CDSView(source=source,
#                 filters=[
#                     BooleanFilter(
#                         [not item for item in source.data['ends_with_long']]),
#                     js_filter_n
#                 ]),
#    height=HEIGHT,
# )
# fig_n_long_ending = myfig(
#    name="fig_n",
#    view=CDSView(
#        source=source,
#        filters=[BooleanFilter(source.data['ends_with_long']), js_filter_n]),
#    height=int(HEIGHT / 1.618),
# )
# fig_n_long_ending.x_range = fig_n_not_long_ending.x_range
#
# fig_n = column([fig_n_long_ending, fig_n_not_long_ending], name='fig_n')
filter = js_filter(modifier=0, slider=slider, source=source)
filter_1 = js_filter(modifier=1, slider=slider, source=source)
filter_2 = js_filter(modifier=2, slider=slider, source=source)

fig_n = main_fig(name="fig_n",
                 view=CDSView(source=source, filters=[filter]),
                 height=HEIGHT)

fig_n_1 = main_fig(name="fig_n_1",
                   view=CDSView(source=source, filters=[filter_1]),
                   height=int(HEIGHT / 1.618))

fig_n_2 = main_fig(name="fig_n_2",
                   view=CDSView(source=source, filters=[filter_2]),
                   height=HEIGHT - int(HEIGHT / 1.618))

fig_n_1.x_range = fig_n.x_range
fig_n_2.x_range = fig_n.x_range
print(fig_n_1.plot_height)
print(fig_n_2.plot_height)
for item in [
        fig_n, fig_n_1, fig_n_2, slider, word_length_div, all_combinations,
        word_length_div_1, all_combinations_1,
        word_length_div_2, all_combinations_2

]:
    curdoc().add_root(item)
curdoc().title = "Pingala"
