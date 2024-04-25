"""_summary_
"""
import os
from tempfile import NamedTemporaryFile
import numpy as np
import xarray as xr
import urllib3
from dotenv import load_dotenv
import s3fs
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

    def __init__(self, bucket_name='tobfer') -> None:
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
        # self.create_first_widgets()
        # self.m = Map(center=[40, 0],
        #              zoom=3,
        #              basemap=basemaps.CartoDB.DarkMatter,
        #              interpolation='nearest')
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
        self.ds.rio.to_raster(temp_file.name)
 
        temp_file.close()
        return temp_file.name

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
        self.ds = self.ds.assign_coords(band=1)
        self.ds = self.ds.drop_vars(['nav_lat', 'nav_lon'])

    def open_zarr_file(self):
        """_summary_

        Returns:
            _type_: _description_
        """
        ds = xr.open_zarr(self.data_path)
        nav_lat = ds.nav_lat.values
        new_y = np.linspace(nav_lat.min(), nav_lat.max(), num=nav_lat.shape[0])
        nav_lon = ds.nav_lon.values
        # new_x = np.linspace(nav_lon.min(), nav_lon.max(), num=nav_lon.shape[1])
        new_x = nav_lon[1000]
        ds = ds.assign_coords(y=new_y, x=new_x)
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
        ds = self.open_zarr_file()
        try:
            ds = ds[subdata_select[:-5]]
        except KeyError:
            ds = ds
        return ds
        # self.update_limits('')


