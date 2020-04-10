from bokeh.models import ColumnDataSource, HoverTool,Patches
from bokeh.plotting import figure, curdoc, show
from bokeh.layouts import column, row, layout
import numpy as np
import json
import os

#tools for the figure
TOOLS = 'pan, tap, wheel_zoom, reset, save, box_select, lasso_select'

with open(os.path.join('output', 'county.json'), 'r') as f:
	county_data = json.load(f)

#create columndatasource (for bokeh interactivity)
fig_data = ColumnDataSource(data = county_data)

# Create a future with the tools added above
fig = figure(match_aspect=True, tools=TOOLS, sizing_mode  = 'scale_height')

# Add the counties as polygon patches in the figure
fig_patches = fig.patches(xs = 'x_coords', ys = 'y_coords', color = 'blue', source = fig_data, line_color='white')

# Preferred to specify what rederers the HoverTool is on for improved interactivity
hover_tool = HoverTool(renderers=[fig_patches], tooltips = [('county', '@name'), ('state', '@state_territory')])
# Add customized hovertool to figure
fig.add_tools(hover_tool)

# add root for current document in Bokeh server
# For now, this will only display the figure with the map
curdoc().add_root(column(fig, sizing_mode = 'scale_height'))
