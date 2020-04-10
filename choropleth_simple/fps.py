import pandas as pd
import os

with open('fips_codes.txt', 'r') as f:
	codes_raw = f.read()

# Separate each line into another list
codes_raw = codes_raw.split('\n')

# Seaprate each item in the line by the tab in the document
for i, code in enumerate(codes_raw):
	codes_raw[i] = code.split('\t')

# Create a pandas dataframe using the first row 
# ['Name', 'Postal Code', 'FIPS'] for columns and the remaining rows
# for the body elements
fips_codes = pd.DataFrame(codes_raw[1:-1], columns = codes_raw[0])

# Save the data to a csv for later parsing
fips_codes.to_csv(os.path.join('output', 'fips_codes.csv'))