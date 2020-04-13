import pandas as pd
from bokeh.models import ColumnDataSource, HoverTool, Patches
from bokeh.plotting import figure, curdoc
from bokeh.layouts import column
from bokeh.palettes import inferno, linear_palette, viridis
import numpy as np
import json
import requests
import io
import os

def findMax(arr):
	# Returns the highest value in an array
	temp = arr[0]
	for i in arr:
		if i > temp:
			temp = i
	print('MAX: {}'.format(temp))
	return temp

def assignColors(arr, maxval, minval, bins =10):
	"""
	Assign colors with a logarithmic increment using Bokeh's virids palette
	colors lower than bins are grey and above are max.
	input:
		arr: list of values
		maxval: Maximum value for color assignment
		minval: Minimum value for color assignment
		bins: Number of increments
	output:
		arr_colors: Color assigned for each color
	"""
	# Create a list of colors for increments
	colors = viridis(bins)

	# Create the increments between max and min on a log10 scale
	bin_ranges = np.logspace(minval,maxval,bins)

	arr_colors = []
	for val in arr:
		if val == 0:
			arr_colors.append('grey')
		elif val > bin_ranges[-1]:
			arr_colors.append(colors[-1])
		else:
			for i in range(len(bin_ranges)):
				if val < bin_ranges[i]:
					arr_colors.append(colors[i])
					break
	return arr_colors


# Tools for the figure
TOOLS = 'pan, tap, wheel_zoom, reset, save, box_select, lasso_select'

# Open the county boundary lines
with open(os.path.join('output', 'county.json'), 'r') as f:
	county_data = json.load(f)


# URL's for usafacts data
confirmed_url = 'https://static.usafacts.org/public/data/covid-19/covid_confirmed_usafacts.csv'
deaths_url = 'https://static.usafacts.org/public/data/covid-19/covid_deaths_usafacts.csv'

# Download data from usafacts and parse to pandas dataframes
with requests.Session() as s:
	# request csv file from url for download
	covid_confirmed = s.get(confirmed_url)
	# decode content as utf-8
	covid_confirmed = covid_confirmed.content.decode('utf-8')
	# read the string as a data file and fill all NaN's as zeros (required for JSON compliance)
	covid_confirmed = pd.read_csv(io.StringIO(covid_confirmed)).fillna(0)
	covid_deaths = s.get(deaths_url)
	covid_deaths = covid_deaths.content.decode('utf-8')
	covid_deaths = pd.read_csv(io.StringIO(covid_deaths)).fillna(0)

#create columndatasource (for bokeh interactivity)
fig_data = ColumnDataSource(data = county_data)

#create a new column for columndatasource containing confirmed and deaths
confirmed = []
deaths =[]
for fip in fig_data.data['countyfp']:
	#find corresponding FIP between confirmed and map
	data_c = covid_confirmed.loc[covid_confirmed['countyFIPS'] == np.int64(fip)]
	data_d = covid_deaths.loc[covid_deaths['countyFIPS'] == np.int64(fip)]
	#if the county is in the confirmed cases, add to the datasource
	if len(data_c)!=0:
		date = data_c.columns[-1]
		confirmed.append(data_c[date].values[0])
		date = data_d.columns[-1]
		deaths.append(data_d[date].values[0])
	#if it is not, append 0 as it can be assumed so
	else:
		confirmed.append(0)
		deaths.append(0)

#append the column
fig_data.data['confirmed'] = confirmed
fig_data.data['deaths'] = deaths
#assign colors
fig_data.data['colors'] = assignColors(confirmed, np.log10(findMax(confirmed)), 1,20)


# Create a figure with the tools added above
fig = figure(match_aspect=True, tools=TOOLS, sizing_mode  = 'scale_height')
# add invisible circles at centroids
fig.circle('cx', 'cy', source = fig_data, fill_alpha = 0.0, line_alpha = 0.0, size=0)
# Add the counties as polygon patches in the figure
fig_patches = fig.patches(xs = 'x_coords', ys = 'y_coords', color = 'colors', source = fig_data, line_color='white')

# Preferred to specify what rederers the HoverTool is on for improved interactivity
hover_tool = HoverTool(renderers=[fig_patches], tooltips = [('county', '@name'), ('state', '@state_postal_code'),
	('confirmed', '@confirmed'), ('deaths', '@deaths')])
# Add customized hovertool to figure
fig.add_tools(hover_tool)

curdoc().add_root(column(fig, sizing_mode = 'scale_height'))
