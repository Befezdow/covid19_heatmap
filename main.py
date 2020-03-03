import json
from data_preparation import get_covid_data, get_map_data

covid_df = get_covid_data()
maps_df = get_map_data()

merged = maps_df.merge(covid_df, left_on='country', right_on='country', how='left')
merged_json = json.loads(merged.to_json())
json_data = json.dumps(merged_json)

from bokeh.io import show
from bokeh.plotting import figure
from bokeh.models import GeoJSONDataSource, LinearColorMapper, ColorBar
from bokeh.palettes import brewer

# Input GeoJSON source that contains features for plotting.
geosource = GeoJSONDataSource(geojson=json_data)

# Define a sequential multi-hue color palette.
palette = brewer['YlGnBu'][8]

# Reverse color order so that dark blue is highest obesity.
palette = palette[::-1]

# Instantiate LinearColorMapper that linearly maps numbers in a range, into a sequence of colors.
color_mapper = LinearColorMapper(palette=palette, low=0, high=1000)

# Define custom tick labels for color bar.
# tick_labels = {'0': '0%', '5': '5%', '10': '10%', '15': '15%', '20': '20%', '25': '25%', '30': '30%', '35': '35%',
#                '40': '>40%'}

# Create color bar.
color_bar = ColorBar(color_mapper=color_mapper, label_standoff=8, width=500, height=20,
                     border_line_color=None, location=(0, 0), orientation='horizontal')

# Create figure object.
p = figure(title='covid19', plot_height=600, plot_width=950, toolbar_location=None)
p.xgrid.grid_line_color = None
p.ygrid.grid_line_color = None

# Add patch renderer to figure.
p.patches('xs', 'ys', source=geosource, fill_color={'field': 'confirmed', 'transform': color_mapper},
          line_color='black', line_width=0.25, fill_alpha=1)

# Specify figure layout.
p.add_layout(color_bar, 'below')

# Display figure.
show(p)
