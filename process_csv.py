import pandas as pd
from pyproj import Transformer

# Initialize the Transformer for converting Lambert 93 to WGS84
transformer = Transformer.from_crs(2154, 4326, always_xy=True)

# Load the raw CSV data containing network coverage information
data = pd.read_csv('2018_01_Sites_mobiles_2G_3G_4G_France_metropolitaine_L93.csv', sep=';', 
                   usecols=[0, 1, 2, 3, 4, 5],
                   names=['Operator', 'X', 'Y', '2G', '3G', '4G'],
                   header=0)

# Map operator codes to human-readable names
operator_map = {
    20801: 'orange',
    20810: 'SFR',
    20815: 'Free',
    20820: 'Bouygues'
}

# Replace operator codes with names and drop any rows with NaN values
data['Operator'] = data['Operator'].replace(operator_map)
data = data.dropna()

# Convert Lambert 93 (X, Y) coordinates to WGS84 (longitude, latitude)
data[['longitude', 'latitude']] = data.apply(
    lambda row: transformer.transform(row['X'], row['Y']), axis=1, result_type='expand'
)

# Save the processed data in a new file for future use
data.to_csv('processed_network_coverage.csv', index=False)
