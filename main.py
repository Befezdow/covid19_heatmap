import json
from bokeh.io import show, curdoc, output_notebook
from bokeh.layouts import column, widgetbox
from bokeh.plotting import figure
from bokeh.models import GeoJSONDataSource, LinearColorMapper, ColorBar, HoverTool, Slider, Select
from bokeh.palettes import brewer

from data_handler import DataHandler

if __name__ == '__main__':
    start_date = '2020-02-26'
    data_handler = DataHandler('covid19', './data/countries_110m/ne_110m_admin_0_countries.shp')


    def json_data(date):
        temp = json.loads(data_handler.get_data_per_date(date).to_json())
        json_data = json.dumps(temp)
        return json_data


    # Input GeoJSON source that contains features for plotting.
    geosource = GeoJSONDataSource(geojson=json_data(start_date))

    # Define a sequential multi-hue color palette.
    palette = brewer['YlGnBu'][8]

    # Reverse color order so that dark blue is highest obesity.
    palette = palette[::-1]

    # Instantiate LinearColorMapper that linearly maps numbers in a range, into a sequence of colors.
    color_mapper = LinearColorMapper(palette=palette, low=0, high=1000)

    # Add hover tool
    hover = HoverTool(tooltips=[
        ('Country', '@country'), ('Confirmed', '@confirmed'), ('Deaths', '@deaths'), ('Recovered', '@recovered')
    ])

    # Create color bar.
    color_bar = ColorBar(color_mapper=color_mapper, label_standoff=5, width=1000, height=20,
                         border_line_color=None, location=(0, 0), orientation='horizontal')

    # Create figure object.
    p = figure(title=f'COVID-19, {start_date}', plot_height=600, plot_width=1000, toolbar_location=None, tools=[hover])
    p.xgrid.grid_line_color = None
    p.ygrid.grid_line_color = None

    # Add patch renderer to figure.
    p.patches('xs', 'ys', source=geosource, fill_color={'field': 'confirmed', 'transform': color_mapper},
              line_color='black', line_width=0.25, fill_alpha=1)

    # Specify figure layout.
    p.add_layout(color_bar, 'below')

    # Make a select object: select
    select = Select(title="Date", value=start_date, options=data_handler.dates_list)

    def update_plot(attr, old, new):
        date = select.value
        new_data = json_data(date)
        geosource.geojson = new_data
        p.title.text = 'COVID-19, %s' % date


    select.on_change('value', update_plot)

    # Make a column layout of widgetbox(slider) and plot, and add it to the current document
    layout = column(p, widgetbox(select))
    curdoc().add_root(layout)

    # Display plot inline in Jupyter notebook
    # output_notebook()

    # Display plot
    show(layout)
