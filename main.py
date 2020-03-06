import json
from ipywidgets import interact, widgets
import pandas as pd
import matplotlib.pyplot as plt

from bokeh.io import show, curdoc, output_notebook, push_notebook
from bokeh.plotting import figure
from bokeh.models import GeoJSONDataSource, LinearColorMapper, ColorBar, HoverTool
from bokeh.palettes import brewer

from data_handler import DataHandler

if __name__ == '__main__':
    data_handler = DataHandler('covid19', './data/countries_110m/ne_110m_admin_0_countries.shp')
    start_date = data_handler.dates_list[0]


    def json_data(date):
        temp = json.loads(data_handler.get_data_per_date(date).to_json())
        json_data = json.dumps(temp)
        return json_data


    # Input GeoJSON source that contains features for plotting.
    geosource = GeoJSONDataSource(geojson=json_data(start_date))

    # Define a sequential multi-hue color palette.
    palette = brewer['Oranges'][8]

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
    patches = p.patches('xs', 'ys', source=geosource, fill_color={'field': 'confirmed', 'transform': color_mapper},
                        line_color='black', line_width=0.25, fill_alpha=1)

    # Specify figure layout.
    p.add_layout(color_bar, 'below')

    def change_date(date):
        if date is None:
            return

        str_date = date.strftime('%Y-%m-%d')
        new_data = json_data(str_date)
        geosource.geojson = new_data
        p.title.text = 'COVID-19, %s' % str_date
        push_notebook()


    def change_color_field(field_name):
        patches.glyph.fill_color = {'field': field_name.lower(), 'transform': color_mapper}
        push_notebook()


    chart_data = data_handler.total_data
    plt.figure(figsize=(15, 8))
    plt.xticks(rotation='vertical')

    plt.plot(chart_data['dates'], chart_data['confirmed'], label='Confirmed', color='red')
    plt.plot(chart_data['dates'], chart_data['deaths'], label='Deaths', color='black')
    plt.plot(chart_data['dates'], chart_data['recovered'], label='Recovered', color='green')

    plt.xlabel('Date')
    plt.ylabel('People count')
    plt.title('COVID-19')
    plt.legend()
    plt.grid()

    interact(change_date, date=widgets.DatePicker(value=pd.to_datetime(start_date), description='Date'))
    interact(change_color_field, field_name=widgets.RadioButtons(options=['Confirmed', 'Deaths', 'Recovered'],
                                                                 value='Confirmed', description='Type'))

    curdoc().add_root(p)

    # Display plot inline in Jupyter notebook
    output_notebook()

    # Display plot
    show(p, notebook_handle=True)