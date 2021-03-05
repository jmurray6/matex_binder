from plot_util import *
from filter_column import *
from log import logger
import panel as pn
from bokeh.resources import INLINE
from css import CSS
from bokeh.layouts import gridplot
# from bokeh.embed import components

def launch_grid():
    pn.extension(raw_css=[CSS])

    gspec = pn.GridSpec(sizing_mode='fixed', width=1500, height=1200)
    plot_grid = pn.GridSpec(sizing_mode='fixed', width=1000, height=800)
    filters_grid = pn.GridSpec(width_policy='max')
    results_grid = pn.GridSpec(width=1500, height=400)

    gspec[0:8, 0:2] = filters_grid
    gspec[0:5, 3:8] = plot_grid
    gspec[5:8, 3:10] = results_grid
    # pn.serve(gspec)

    flt = pd.Series([True]*len(mdf), index=mdf.index)

    pn_row_fig = pn.Row(sizing_mode='scale_both')
    pn_row_results = pn.Row(width_policy='max', css_classes=['panel-widget-box'])

    filters_col = FiltersColumn(pn_row_fig, pn_row_results)
    filters_col.run_button.on_click(filters_col.apply_filters)
    filters_col.clear_filters_button.on_click(filters_col.clear_filters_and_plot)
    filters_col.add_keyword_button.on_click(filters_col.add_keyword_row)

    filters_grid[0, 0] = filters_col.filters
    # plot_grid[3, 0] = filters_col.filterUtils
    plot_grid[0:4, 0:8] = pn_row_fig
    results_grid[0:8, 0] = pn_row_results

    gspec.show()
    # gspec.servable({'localhost:5006'})
    # return gspec
    # doc.add_root(gridplot(gspec))

def main():
    launch_grid()

# if __name__ == "__main__":
#     main()



