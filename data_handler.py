import pandas as pd
from datetime import datetime
import geopandas as gpd
from os import listdir
from os.path import isfile, join


class DataHandler:
    def __init__(self, data_dir_path, shape_file_path):
        self.data_dir_path = data_dir_path
        self.shape_file_path = shape_file_path

        self._covid_df = self._get_covid_data()
        self._maps_df = self._get_map_data()

        self._data = self._maps_df.merge(self._covid_df, left_on='country', right_on='country', how='left')

    def _get_map_data(self):
        # Read shapefile using Geopandas
        gdf = gpd.read_file(self.shape_file_path)[['ADMIN', 'ADM0_A3', 'geometry']]

        # Rename columns.
        gdf.columns = ['country', 'country_code', 'geometry']

        # Drop row corresponding to 'Antarctica'
        gdf = gdf.drop(gdf.index[159])

        return gdf

    def _get_covid_data(self):
        dir_path = self.data_dir_path
        files_data = [(f[:-4], join(dir_path, f)) for f in listdir(dir_path) if isfile(join(dir_path, f))]

        total_data = pd.DataFrame()
        for date, filename in files_data:
            df = pd.read_csv(filename, names=['region', 'country', 'date', 'confirmed', 'deaths', 'recovered'],
                             skiprows=1)
            df['date'] = datetime.strptime(date, '%m-%d-%Y').strftime('%Y-%m-%d')
            # df['date'] = pd.to_datetime(df['date'], format='%m-%d-%Y')
            df['region'].fillna(df['country'], inplace=True)
            df['country'].replace(['Mainland China', 'Macau', 'Hong Kong'], 'China', inplace=True)
            df['country'].replace('US', 'United States of America', inplace=True)
            total_data = pd.concat([total_data, df], axis=0, sort=False, ignore_index=True)

        return total_data.groupby(['country', 'date'], as_index=False).agg(
            {
                'confirmed': 'sum',
                'deaths': 'sum',
                'recovered': 'sum'
            }
        )

    @property
    def data(self):
        return self._data

    def get_data_per_date(self, date):
        return self._maps_df.merge(
            self._covid_df[self._covid_df['date'] == date], left_on='country', right_on='country', how='left'
        )

    @property
    def dates_list(self):
        return sorted(self._data['date'].unique().tolist()[1:])
