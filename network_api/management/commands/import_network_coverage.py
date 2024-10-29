from django.core.management.base import BaseCommand
from network_api.models import NetworkCoverage
from pyproj import Transformer
import pandas as pd

class Command(BaseCommand):
    help = 'Process raw CSV data and import network coverage data into the database'

    def handle(self, *args, **kwargs):
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

        # Replace operator codes with names
        data['Operator'] = data['Operator'].replace(operator_map)
        data = data.dropna()  # Drop any rows with NaN values

        # Convert Lambert 93 (X, Y) coordinates to WGS84 (longitude, latitude)
        data[['longitude', 'latitude']] = data.apply(
            lambda row: transformer.transform(row['X'], row['Y']), axis=1, result_type='expand'
        )

        # Iterate over DataFrame rows and save to the database
        coverage_instances = [
            NetworkCoverage(
                operator=row['Operator'],
                longitude=row['longitude'],
                latitude=row['latitude'],
                g2=bool(row['2G']),
                g3=bool(row['3G']),
                g4=bool(row['4G']),
            )
            for _, row in data.iterrows()
        ]

        # Bulk create all records in one operation for performance improvement
        NetworkCoverage.objects.bulk_create(coverage_instances, batch_size=1000)

        self.stdout.write(self.style.SUCCESS('Data processed and imported successfully.'))
