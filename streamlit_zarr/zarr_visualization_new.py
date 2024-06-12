"""_summary_
"""
import os
from tempfile import NamedTemporaryFile
import numpy as np
import xarray as xr
import urllib3
from dotenv import load_dotenv
import s3fs
import iris
import cartopy.crs as ccrs
import numpy as np
import plotly.graph_objects as go


# import ipywidgets as widgets
# from ipyleaflet import Map, basemaps
# from ipyleaflet.leaflet import TileLayer, LayersControl
# from localtileserver import get_leaflet_tile_layer, TileClient
# from rio_tiler.io import COGReader

# load_dotenv()
load_dotenv()
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class ZarrVisualization():
    """_summary_
    """

    def __init__(self, bucket_name='tobfer6') -> None:
        self.bucket_name = bucket_name
        self.remote_options = {
            "anon": False,
            "key":os.environ.get('aws_access_key_id'),
            "secret": os.environ.get('aws_secret_access_key'),
            "endpoint_url": os.environ.get('endpoint_url')
        }
        self.fs = s3fs.S3FileSystem(**self.remote_options)

        self.list_of_variables = [item.split('/')[-1] for item in self.fs.ls(bucket_name)]
        self.data_path = ''
        self.ds = None
        self.data_path = None

    def get_list_of_subdata(self, variable):
        return [item.split('/')[-1] for item in self.fs.ls(f"{self.bucket_name}/{variable}")]

    def update_data_path(self, variable, subdata):
        """_summary_
        """
        self.data_path = f"{self.remote_options['endpoint_url']}{self.bucket_name}/{variable}/{subdata}"

    def convert_to_geotiff(self):
        """_summary_
        """
        temp_file = NamedTemporaryFile(suffix='.tif', delete=False)
        # self.ds.rio.to_raster(temp_file.name, driver="COG", tiled=True, windowed=True)
        self.ds = self.ds.where(self.ds != 0, np.nan)
        self.ds.rio.set_nodata(np.nan, inplace=True)

        self.ds.rio.to_raster(temp_file.name)
        temp_file.close()
        return temp_file.name

        # temp_file = NamedTemporaryFile(suffix='.tif', delete=False)
        # self.ds.rio.to_raster(temp_file.name, driver="COG", tiled=True, windowed=True)
        # # self.ds.rio.to_raster(temp_file.name)
        # temp_file.close()
        
        # with self.fs.open(f"{self.bucket_name}/temp_images/{temp_file.name}", 'wb') as f:
        #     with open(temp_file.name, 'rb') as source_file:
        #         f.write(source_file.read())

        # return f"{self.remote_options['endpoint_url']}{self.bucket_name}/temp_images/{temp_file.name}"

    def convert_to_png(self):
        """_summary_
        """
        temp_file = NamedTemporaryFile(suffix='.tif', delete=False)
        # self.ds.rio.to_raster(temp_file.name, driver="COG", tiled=True, windowed=True)
        self.ds.rio.to_raster(temp_file.name, driver="PNG")
 
        temp_file.close()
        return temp_file.name

    def sel_zarr_data(self, ds, limits):
        """_summary_
        """
        self.ds = ds
        self.limits = limits
        self.ds = self.ds.sel(y=slice(self.limits[0][0], self.limits[0][1]))
        self.ds = self.ds.sel(x=slice(self.limits[1][0], self.limits[1][1]))
        if self.limits[2]:
            self.ds = self.ds.sel(time_counter=self.limits[2])
        self.ds.attrs['scale_factor'] = 1.0
        self.ds.attrs['add_offset'] = 0.0
        # self.ds = self.ds.compute()
        self.ds = self.ds.assign_coords(band=1)
        # self.ds = self.ds.assign_coords({
        #     "lon": (("y", "x"), self.ds['nav_lon'].data),
        #     "lat": (("y", "x"), self.ds['nav_lat'].data)
        # })
        self.ds = self.ds.sortby('x')
        self.ds = self.ds.sortby('y', ascending=False)
        self.ds.rio.write_crs("epsg:4326", inplace=True)


    def plot_data_on_mapbox(self):
        """Plot data array on a Mapbox map using Plotly."""
        self.ds = self.ds.where(self.ds != 0.0, np.nan)


        latitudes = self.ds.y.values
        longitudes = self.ds.x.values
        data_values = self.ds.values

        # latitude_grid = np.tile(latitudes[:, np.newaxis], (1, self.ds.x.size))
        # longitude_grid = np.tile(longitudes[:, np.newaxis], (1, self.ds.y.size))

        # fig = go.Figure(go.Densitymapbox(
        #     z=data_values.flatten(),
        #     lon=longitude_grid.flatten(),
        #     lat=latitude_grid.flatten(),
        #     colorscale='Viridis',
        #     colorbar=dict(title='Data Value')
        # ))


        fig = go.Figure(go.Heatmap(
            z=data_values,
            x=longitudes,
            y=latitudes,
            colorscale='Viridis',
            colorbar=dict(title='Data Value'),
        ))
        fig.update_layout(mapbox_style="open-street-map")
        fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
        # token = os.environ.get('mapbox_token')
        # fig.update_layout(
        #     mapbox=dict(
        #         style='carto-positron',
        #         zoom=3,
        #         center=dict(lat=latitudes.mean(), lon=longitudes.mean()),
        #         accesstoken=token,
        #         layers=[
        #             {
        #                 'sourcetype': 'raster',
        #                 'source': [
        #                     'https://a.tile.openstreetmap.org/{z}/{x}/{y}.png',
        #                     'https://b.tile.openstreetmap.org/{z}/{x}/{y}.png',
        #                     'https://c.tile.openstreetmap.org/{z}/{x}/{y}.png'
        #                 ],
        #                 'below': 'traces',
        #                 'opacity': 0.6
        #             }
        #         ]
        #     ),
        #     margin=dict(l=0, r=0, t=0, b=0)
        # )
        # fig.update_layout(mapbox_style="open-street-map")

        return fig

    def reproject_data(self):
        """_summary_
        """
        cube = self.ds.to_iris()
        cube.remove_coord('latitude')
        cube.remove_coord('longitude')
        latitude = iris.coords.AuxCoord(
            self.ds['nav_lat'].values,
            standard_name='latitude',
            units='degrees')
        longitude = iris.coords.AuxCoord(
            self.ds['nav_lon'].values,
            standard_name='longitude',
            units='degrees')
        cube.add_aux_coord(latitude, (0, 1))
        cube.add_aux_coord(longitude, (0, 1))
        target_projection = ccrs.PlateCarree()
        try:
            projected_cube = iris.analysis.cartography.project(
                cube,
                target_projection,
                nx=self.ds.shape[1],
                ny=self.ds.shape[0])
        except ValueError as e:
            print("Error during projection:", e)
            return
        data_da = xr.DataArray.from_iris(projected_cube[0])
        data_da = data_da.rio.write_crs("epsg:4326")
        data_da = data_da.sortby('projection_x_coordinate')
        data_da = data_da.sortby('projection_y_coordinate', ascending=False)
        self.ds = data_da


    def open_zarr_file(self, subdata_select):
        """_summary_

        Returns:
            _type_: _description_
        """
        ds = xr.open_zarr(self.data_path)
        if "x" not in ds.dims:
            return ds
        if "bounds" in subdata_select:
            return ds
        # print(ds)
        ds = ds.assign_coords(y=ds.projected_y.values, x=ds.projected_x.values)
        ds = ds.sortby('x')
        ds = ds.sortby('y')
        if "nvertex" in ds.dims:
            ds = ds.drop_dims("nvertex")

        if "x" not in ds.dims and "y" not in ds.dims:
            latitude_var_name = "lat"
            longitude_var_name = "lon"
            if "latitude" in ds.dims:
                latitude_var_name = "latitude"
            if "longitude" in ds.dims:
                longitude_var_name = "longitude"
            ds = ds.rename({latitude_var_name: "y", longitude_var_name: "x"})
        if "time_counter" in ds.dims:
            ds = ds.transpose("time_counter", "y", "x")
        else:
            ds = ds.transpose("y", "x")
        if (ds.x > 180).any():
            ds = ds.assign_coords(x=(ds.x + 180) % 360 - 180)
            ds = ds.sortby(ds.x)
        crs = ds.rio.crs or "epsg:4326"
        ds.rio.write_crs(crs, inplace=True)
        return ds

    def process_zarr_file(self, subdata_select):
        """_summary_
        """
        ds = self.open_zarr_file(subdata_select[:-5])
        try:
            ds = ds[f"projected_{subdata_select[:-5]}"]
        except KeyError:
            ds = ds[f"{subdata_select[:-5]}"]
        return ds
        # self.update_limits('')


