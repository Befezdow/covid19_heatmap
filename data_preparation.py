import pandas as pd
import geopandas as gpd


def get_covid_data():
    datafile = 'covid19/01-22-2020.csv'

    df = pd.read_csv(datafile, names=['region', 'country', 'date', 'confirmed', 'deaths', 'recovered'], skiprows=1)
    df['region'].fillna(df['country'], inplace=True)

    df['country'].replace('Mainland China', 'China', inplace=True)
    return df.groupby(['country'], as_index=False).agg(
        {
            'confirmed': 'sum',
            'deaths': 'sum',
            'recovered': 'sum'
        }
    )


def get_map_data():
    shapefile = './data/countries_110m/ne_110m_admin_0_countries.shp'
    # Read shapefile using Geopandas
    gdf = gpd.read_file(shapefile)[['ADMIN', 'ADM0_A3', 'geometry']]
    # Rename columns.
    gdf.columns = ['country', 'country_code', 'geometry']

    print(gdf[gdf['country'] == 'Antarctica'])
    # Drop row corresponding to 'Antarctica'
    gdf = gdf.drop(gdf.index[159])

    return gdf