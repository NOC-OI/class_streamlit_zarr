import leafmap.foliumap as leafmap
import os
import streamlit as st
from streamlit_zarr.zarr_visualization import ZarrVisualization
import urllib
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import matplotlib.pyplot as plt
from dotenv import load_dotenv

load_dotenv()
st.set_page_config(layout="wide")


TILESERVER_URL = os.environ.get('TILESERVER_URL')
TILESERVER_ENDPOINT = "/tiles/WebMercatorQuad/{z}/{x}/{y}@1x"
@st.cache_data
def load_file_list():
    """ Load the file list

    Returns:
        ZarrVisualization: ZarrVisualization object
    """
    zarr_vis_object = ZarrVisualization()
    return zarr_vis_object

@st.cache_data
def load_zarr_file(_zarr_vis: ZarrVisualization, subdata_select_value: str):
    """ Load the Zarr file

    Args:
        _zarr_vis (): ZaarVisualization object
        subdata_select_value (str): The selected subdata

    Returns:
        _type_: _description_
    """
    with st.spinner('Loading File...'):
        dataset = zarr_vis.process_zarr_file(subdata_select_value)
    return dataset


@st.cache_data
def get_palettes_cartopy():
    """ Get the palettes

    Returns:
        List[str]: List of palettes
    """
    list_of_palettes = ['Accent', 'Accent_r', 'Blues', 'Blues_r', 'BrBG', 'BrBG_r', 'BuGn', 'BuGn_r', 'BuPu', 'BuPu_r', 'CMRmap', 'CMRmap_r', 'Dark2', 'Dark2_r', 'GnBu', 'GnBu_r', 'Grays', 'Greens', 'Greens_r', 'Greys', 'Greys_r', 'OrRd', 'OrRd_r', 'Oranges', 'Oranges_r', 'PRGn', 'PRGn_r', 'Paired', 'Paired_r', 'Pastel1', 'Pastel1_r', 'Pastel2', 'Pastel2_r', 'PiYG', 'PiYG_r', 'PuBu', 'PuBuGn', 'PuBuGn_r', 'PuBu_r', 'PuOr', 'PuOr_r', 'PuRd', 'PuRd_r', 'Purples', 'Purples_r', 'RdBu', 'RdBu_r', 'RdGy', 'RdGy_r', 'RdPu', 'RdPu_r', 'RdYlBu', 'RdYlBu_r', 'RdYlGn', 'RdYlGn_r', 'Reds', 'Reds_r', 'Set1', 'Set1_r', 'Set2', 'Set2_r', 'Set3', 'Set3_r', 'Spectral', 'Spectral_r', 'Wistia', 'Wistia_r', 'YlGn', 'YlGnBu', 'YlGnBu_r', 'YlGn_r', 'YlOrBr', 'YlOrBr_r', 'YlOrRd', 'YlOrRd_r', 'afmhot', 'afmhot_r', 'autumn', 'autumn_r', 'binary', 'binary_r', 'bone', 'bone_r', 'brg', 'brg_r', 'bwr', 'bwr_r', 'cividis', 'cividis_r', 'cool', 'cool_r', 'coolwarm', 'coolwarm_r', 'copper', 'copper_r', 'cubehelix', 'cubehelix_r', 'flag', 'flag_r', 'gist_earth', 'gist_earth_r', 'gist_gray', 'gist_gray_r', 'gist_grey', 'gist_heat', 'gist_heat_r', 'gist_ncar', 'gist_ncar_r', 'gist_rainbow', 'gist_rainbow_r', 'gist_stern', 'gist_stern_r', 'gist_yarg', 'gist_yarg_r', 'gist_yerg', 'gnuplot', 'gnuplot2', 'gnuplot2_r', 'gnuplot_r', 'gray', 'gray_r', 'grey', 'hot', 'hot_r', 'hsv', 'hsv_r', 'inferno', 'inferno_r', 'jet', 'jet_r', 'magma', 'magma_r', 'nipy_spectral', 'nipy_spectral_r', 'ocean', 'ocean_r', 'pink', 'pink_r', 'plasma', 'plasma_r', 'prism', 'prism_r', 'rainbow', 'rainbow_r', 'seismic', 'seismic_r', 'spring', 'spring_r', 'summer', 'summer_r', 'tab10', 'tab10_r', 'tab20', 'tab20_r', 'tab20b', 'tab20b_r', 'tab20c', 'tab20c_r', 'terrain', 'terrain_r', 'turbo', 'turbo_r', 'twilight', 'twilight_r', 'twilight_shifted', 'twilight_shifted_r', 'viridis', 'viridis_r', 'winter', 'winter_r']
    return list_of_palettes
    # palettes = dir(palettable.matplotlib)[:-16]
    # return ["matplotlib." + p for p in palettes]

@st.cache_data
def get_palettes_leaflet():
    """ Get the palettes

    Returns:
        List[str]: List of palettes
    """
    list_of_palettes = ['accent','accent_r','afmhot','afmhot_r','algae','algae_r','amp','amp_r','autumn','autumn_r','balance','balance_r','binary','binary_r','blues','blues_r','bone','bone_r','brbg','brbg_r','brg','brg_r','bugn','bugn_r','bupu','bupu_r','bwr','bwr_r','cfastie','cividis','cividis_r','cmrmap','cmrmap_r','cool','cool_r','coolwarm','coolwarm_r','copper','copper_r','cubehelix','cubehelix_r','curl','curl_r','dark2','dark2_r','deep','deep_r','delta','delta_r','dense','dense_r','diff','diff_r','flag','flag_r','gist_earth','gist_earth_r','gist_gray','gist_gray_r','gist_heat','gist_heat_r','gist_ncar','gist_ncar_r','gist_rainbow','gist_rainbow_r','gist_stern','gist_stern_r','gist_yarg','gist_yarg_r','gnbu','gnbu_r','gnuplot','gnuplot2','gnuplot2_r','gnuplot_r','gray','gray_r','greens','greens_r','greys','greys_r','haline','haline_r','hot','hot_r','hsv','hsv_r','ice','ice_r','inferno','inferno_r','jet','jet_r','magma','magma_r','matter','matter_r','nipy_spectral','nipy_spectral_r','ocean','ocean_r','oranges','oranges_r','orrd','orrd_r','oxy','oxy_r','paired','paired_r','pastel1','pastel1_r','pastel2','pastel2_r','phase','phase_r','pink','pink_r','piyg','piyg_r','plasma','plasma_r','prgn','prgn_r','prism','prism_r','pubu','pubu_r','pubugn','pubugn_r','puor','puor_r','purd','purd_r','purples','purples_r','rain','rain_r','rainbow','rainbow_r','rdbu','rdbu_r','rdgy','rdgy_r','rdpu','rdpu_r','rdylbu','rdylbu_r','rdylgn','rdylgn_r','reds','reds_r','rplumbo','schwarzwald','seismic','seismic_r','set1','set1_r','set2','set2_r','set3','set3_r','solar','solar_r','spectral','spectral_r','speed','speed_r','spring','spring_r','summer','summer_r','tab10','tab10_r','tab20','tab20_r','tab20b','tab20b_r','tab20c','tab20c_r','tarn','tarn_r','tempo','tempo_r','terrain','terrain_r','thermal','thermal_r','topo','topo_r','turbid','turbid_r','turbo','turbo_r','twilight','twilight_r','twilight_shifted','twilight_shifted_r','viridis','viridis_r','winter','winter_r','wistia','wistia_r','ylgn','ylgn_r','ylgnbu','ylgnbu_r','ylorbr','ylorbr_r','ylorrd','ylorrd_r']
    return list_of_palettes
    # palettes = dir(palettable.matplotlib)[:-16]
    # return ["matplotlib." + p for p in palettes]



st.title("Visualize Zarr Datasets")
st.markdown('### An interactive web app for visualizing local raster datasets.')

st.markdown('#### SELECT DATASET AND VARIABLE')

if 'open_zarr_button' not in st.session_state:
    st.session_state.disabled = True

zarr_vis = load_file_list()
variable_select = st.selectbox("Select the type of data", zarr_vis.list_of_variables)

subdata_select = st.selectbox("Select the variable",
                              zarr_vis.get_list_of_subdata(variable_select),
                              index=len(zarr_vis.get_list_of_subdata(variable_select))-1)

zarr_vis.update_data_path(variable_select, subdata_select)

data_path = zarr_vis.data_path
st.write(f"Data Path: {zarr_vis.data_path}")

ds = load_zarr_file(zarr_vis, subdata_select)

st.write(f"Dataset dimensions: {ds.sizes}")

if "x" in ds.dims and "bounds" not in subdata_select:
    st.markdown('#### SELECT LIMITS')

    lat_limits = st.slider(
        'Select latitude limits',
        -89, 89, (45, 65))

    lon_limits = st.slider(
        'Select longitude limits',
        -179, 179, (-8, 5))

    time_counter_limit = None
    if 'time_counter' in list(ds.coords):
        time_values = ds.time_counter.values
        time_counter_limit = st.selectbox("Select the timestamp", time_values)

    limits = [lat_limits, lon_limits, time_counter_limit]

    st.markdown('#### PLOT PREFERENCES')

    plot_type = st.selectbox("Select Plot Style", ['plotly', 'cartopy', 'leaflet'] )
    disabled_button = False
    if plot_type == 'leaflet':
        pallete = st.selectbox("Select the color pallete", get_palettes_leaflet())
        min_scale = st.number_input("Scale Min Value (Leave empty for default)", value=-2)
        max_scale = st.number_input("Scale Max Value (Leave empty for default)", value=2)
        if min_scale is not None and max_scale is not None:
            if min_scale >= max_scale:
                st.error("Min value must be less than max value")
                disabled_button = True
    elif plot_type == 'cartopy':
        pallete = st.selectbox("Select the color pallete", get_palettes_cartopy())
    else:
        disabled_button = False

    plot_data = st.button(
        "Clip and Plot Data", key='plot_data', disabled=disabled_button)

    if plot_data:
        st.markdown('#### RESULTS')
        with st.spinner("Preparing and plotting data..."):
            zarr_vis.sel_zarr_data(ds, limits)

        try:
            if plot_type == 'plotly':
                fig = zarr_vis.plot_data_on_mapbox()
                st.markdown(f'##### {subdata_select[:-5]}')
                st.plotly_chart(fig)
            elif plot_type == 'cartopy':
                fig, ax = plt.subplots(subplot_kw={'projection': ccrs.PlateCarree()})
                ax.set_extent([lon_limits[0], lon_limits[1], lat_limits[0], lat_limits[1]], crs=ccrs.PlateCarree())
                ax.add_feature(cfeature.COASTLINE)
                ax.add_feature(cfeature.BORDERS, linestyle=':')
                data_array = zarr_vis.ds.values
                im = ax.pcolormesh(zarr_vis.ds.x.values,
                                   zarr_vis.ds.y.values,
                                   data_array,
                                   transform=ccrs.PlateCarree(),
                                   cmap=pallete)
                plt.colorbar(im, ax=ax, orientation='vertical', label=subdata_select)
                st.pyplot(fig)
            else:
                m = leafmap.Map(google_map="SATELLITE", latlon_control=False)
                center_lat = (limits[0][0] + limits[0][1]) / 2
                center_lon = (limits[1][0] + limits[1][1]) / 2
                m.set_center(lat=center_lat, lon=center_lon, zoom=6)               
                if min_scale is not None and max_scale is not None:
                    rescale = f"{min_scale},{max_scale}"
                else:
                    rescale = "-2,2"
                params = {
                    "url": data_path,
                    "variable": f"projected_{subdata_select[:-5]}",
                    "reference": "false",
                    "decode_times": "true",
                    "date_time": limits[2],
                    "tile_scale": "1",
                    "return_mask": "true",
                    "rescale": rescale,
                    "colormap_name": pallete,
                }
                encoded_params = urllib.parse.urlencode(params)

                url = f"{TILESERVER_URL}{TILESERVER_ENDPOINT}?{encoded_params}"
                m.add_tile_layer(
                    url=url,
                    name="Zarr Layer",
                    attribution="Zarr Data")

                st.markdown(f'##### {subdata_select[:-5]}')
                m.to_streamlit()

            # st.plotly_chart(fig)
        except Exception as e:
            st.error(e)
            st.error("Work in progress. Try it again later.")

else:
    st.markdown('#### RESULTS')
    if "bounds" in subdata_select:
        st.write("This variable is a bounds dataset. Please select another variable or dataset.")
    else:
        st.write("This variable is not a raster dataset. Please select another variable or dataset.")
        st.write("These are the variable values:")
        st.write(ds.values)
        # m.to_streamlit()
