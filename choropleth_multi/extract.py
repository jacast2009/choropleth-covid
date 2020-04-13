import shapefile
import pandas as pd
import json
from tqdm import tqdm
from skimage.measure import approximate_polygon, moments_coords
import numpy as np
import os


def coords2array(coords):
	"""
	Iterates through list[tuple(x, y)] to create seprate lists for x and y
	input: list[tuple(x, y)]
	output: tuple(list[x coords], list[y coords])
	"""
	x = []
	y = []
	for coord in coords:
		if coord[0] > 0:

			# Correct some Alaska counties
			coord[0] -= 350

		x.append(coord[0])
		y.append(coord[1])
		
	return x, y

def centroids(points):
	"""
	Calculate X and Y centroids for a polygon using OpenCV
	input: list[tuple(x, y)]
	output: (centroidx, centroidy)
	"""
	# Determine moments from points using OpenCV
	im_moment = moments_coords(points, order = 1)

	# Use moments to determine centroids
	cx = im_moment[1, 0]/ im_moment[0, 0]
	cy = im_moment[0, 1]/ im_moment[0, 0]

	return cx, cy

# Path to shapefile
file = os.path.join(os.getcwd(), 'cb_2018_us_county_20m', 'cb_2018_us_county_20m.shp')

# use shapefile to open file for boundary data
sf = shapefile.Reader(file)

#get shapes for point coordinates
shapes = sf.shapes()

#get data for name and county FIPS
shapeRecs = sf.shapeRecords()

#create dict for export
county_data = dict(
	countyfp = [],
	state_territory = [],
	state_postal_code = [],
	name = [],
	x_coords = [],
	y_coords = [],
	cx = [],
	cy = [],
	)

# Read state FIPS data for parsing
state_fips = pd.read_csv(os.path.join('output', 'fips_codes.csv'))

# Option to exclude a state (ie: separating AK and HI for mainland only)
# exclude = ['AK', 'HI']
exclude = []

# tqdm for a progress bar (not required)
for i in tqdm(range(len(shapeRecs))):

	# Use approximate_polygon to reduce complexity of shape for improved performance in Bokeh
	# (0 returns original) as this may be unnecessary with simple files like the 20m files.
	# This is not required
	points = approximate_polygon(np.array(shapes[i].points), 0)

	#convert to corresponding x's and y's (for most plotting tools)
	x, y = coords2array(points)
	cx, cy = centroids(points)

	try:
		state = state_fips.loc[state_fips['FIPS'] == int(shapeRecs[i].record[0])]['Postal Code'].values[0]
	except:
		continue
	if state not in exclude:

		try:
			# Use FIPS code to get state and postal code name from FIPS code dataframe
			county_data['state_territory'].append(state_fips.loc[state_fips['FIPS'] == int(shapeRecs[i].record[0])]['Name'].values[0])
			county_data['state_postal_code'].append(state_fips.loc[state_fips['FIPS'] == int(shapeRecs[i].record[0])]['Postal Code'].values[0])
			
			county_data['name'].append(shapeRecs[i].record[5])
			county_data['x_coords'].append(x)
			county_data['y_coords'].append(y)
			county_data['cx'].append(cx)
			county_data['cy'].append(cy)

			# Combine county and state FIPS codes for easy parsing in Bokeh
			county_data['countyfp'].append(shapeRecs[i].record[0] + shapeRecs[i].record[1])
		except:
			print(i)
	else:
		continue

with open(os.path.join('output','county.json'), 'w') as f:
	json.dump(county_data, f)
