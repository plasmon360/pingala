from bokeh.embed import file_html, components, autoload_static
from bokeh.resources import CDN
from bokeh.io import curdoc
from collections import defaultdict
from bokeh.plotting import figure, show, save
from bokeh.models import Plot, Label, CDSView, Filter, Slider, CustomJS, CustomJSFilter, GroupFilter, BooleanFilter
from bokeh.models.glyphs import Text
from bokeh.layouts import Column, Row, layout
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
slider_initial_val = 3
slider_final_val = 11
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

combinations = []
word_length_divs = []

for i in range(3):

    temp1 = Div(text=f"""<span class="combinations_{i}">""" +
                str(len(pingala(slider_initial_val-i))) + """</span>""",
                name=f'all_combinations_{i}')
    temp1.css_classes = [f'combinations']

    temp2 = Div(text=f"""<span class="wordlength">""" + 'P'+str(slider_initial_val-i) +
                """</span>""",
                name=f'word_length_{i}')

    temp2.css_classes = [f'wordlength']

    combinations.append(temp1)
    word_length_divs.append(temp2)

ratio_div = Div(text=f"""<span class="ratio_div">""" +
            str(len(pingala(slider_initial_val-1)) / len(pingala(slider_initial_val-2))  ) + """</span>""",
            name=f'ratio_div')

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
                              combinations_0=combinations[0],
                              word_length_div_0=word_length_divs[0],
                              combinations_1=combinations[1],
                              word_length_div_1=word_length_divs[1],
                              combinations_2=combinations[2],
                              word_length_div_2=word_length_divs[2],
                              ratio_div = ratio_div,
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
    var uniqueItems_0 = Array.from(new Set(columns));
     combinations_0.text = "<span class=combinations_0> " + uniqueItems_0.length+ "</span>";

    var uniqueItems_1 = Array.from(new Set(columns_1));
     combinations_1.text = "<span class= combinations_1> " + \
         uniqueItems_1.length+ "</span>";

    var uniqueItems_2 = Array.from(new Set(columns_2));
     combinations_2.text = "<span class=combinations_2> " + \
         uniqueItems_2.length+ "</span>";

     ratio_div.text = "<span class= ratio_div>" + (uniqueItems_1.length/uniqueItems_2.length).toFixed(4) + "</span>";

     word_length_div_0.text = "<span class= wordlength> " + 'P' + slider.value+ "</span>";
     word_length_div_1.text = "<span class= wordlength> " + 'P'+(slider.value-1)+ "</span>";
     word_length_div_2.text = "<span class= wordlength> " + 'P'+(slider.value-2)+ "</span>";


    source.change.emit();
""")
slider.js_on_change('value', callback)


def js_filter(modifier, slider):
    code = '''
                var indices = [];
                for (var i = 0; i <= source.data['word_length'].length; i++){{
                    if (source.data['word_length'][i] == slider.value-{0}) {{
                        indices.push(i)
                    }}
                }}
                return indices
        '''.format(modifier)

    return CustomJSFilter(args=dict(slider=slider), code=code)


# Bokeh figure for each figure


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


HEIGHT = 400
# Create a list of filters for each figure
filters = [js_filter(modifier=x, slider=slider) for x in range(3)]

fig_n_not_long_ending = main_fig(
   name="fig_n_not_long_ending",
   view=CDSView(source=source,
                filters=[
                    BooleanFilter(
                        [not item for item in source.data['ends_with_long']]),
                    filters[0]
                ]),
   height=HEIGHT,
)
fig_n_long_ending = main_fig(
   name="fig_n_long_ending",
   view=CDSView(
       source=source,
       filters=[BooleanFilter(source.data['ends_with_long']), filters[0]]),
   height=int(HEIGHT / 1.618),
)
fig_n_long_ending.x_range = fig_n_not_long_ending.x_range


# Make Figures

items = [slider, combinations[0], combinations[1], combinations[2],
         word_length_divs[0], fig_n_long_ending, fig_n_not_long_ending, ratio_div]
for item in items:
    curdoc().add_root(item)


