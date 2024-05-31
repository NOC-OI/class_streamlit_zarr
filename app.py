import os
import leafmap.foliumap as leafmap
import leafmap.colormaps as cm
import streamlit as st
from streamlit_zarr.zarr_visualization_new import ZarrVisualization
import urllib
st.set_page_config(layout="wide")


tileserver_url = "http://127.0.0.1:8000"
tileserver_enpoint = "/tiles/WebMercatorQuad/{z}/{x}/{y}@1x"
@st.cache_data
def load_file_list():
    zarr_vis = ZarrVisualization()
    return zarr_vis

@st.cache_data
def load_zarr_file(_zarr_vis, subdata_select):
    with st.spinner('Loading File...'):
        ds = zarr_vis.process_zarr_file(subdata_select)
    return ds


@st.cache_data
def get_palettes():
    return list(cm.palettes.keys())
    # palettes = dir(palettable.matplotlib)[:-16]
    # return ["matplotlib." + p for p in palettes]


st.title("Visualize Zarr Datasets")
st.markdown('### An interactive web app for visualizing local raster datasets.')

st.markdown('#### SELECT DATASET AND VARIABLE')

if 'open_zarr_button' not in st.session_state:
    st.session_state.disabled = True

zarr_vis = load_file_list()
variable_select = st.selectbox("Select the type of data", zarr_vis.list_of_variables)

subdata_select = st.selectbox("Select the variable", zarr_vis.get_list_of_subdata(variable_select), index=len(zarr_vis.get_list_of_subdata(variable_select))-1)

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

    plot_type = st.selectbox("Select Plot Style", ['plotly', 'leaflet'] )
    disabled_button = False
    if plot_type == 'leaflet':
        min_scale = st.number_input("Scale Min Value (Leave empty for default)", value=None)
        max_scale = st.number_input("Scale Max Value (Leave empty for default)", value=None)
        if min_scale is not None and max_scale is not None:
            if min_scale >= max_scale:
                st.error("Min value must be less than max value")
                disabled_button = True       
    else:
        disabled_button = False
        
    plot_data = st.button("Clip and Plot Data", key='plot_data', disabled=disabled_button)

    if plot_data:
        st.markdown('#### RESULTS')
        with st.spinner("Preparing and plotting data..."):
            zarr_vis.sel_zarr_data(ds, limits)

        try:
            # m.add_local_tile(geotiff_file, colormap="terrain", layer_name=subdata_select[:-5], debug=True)
            # image = leafmap.ImageOverlay(url=png_file, bounds=(
            #     (zarr_vis.limits[0][0], zarr_vis.limits[0][1]), (zarr_vis.limits[1][0], zarr_vis.limits[1][1])))

            # m.add_layer(image)
            # m.add_tile_layer(url="https://titiler.xyz/cog/tiles/WebMercatorQuad/{z}/{x}/{y}.png?colormap_name=RdBu_r&url=" + urllib.parse.quote('https://pilot-imfe-o.s3-ext.jc.rl.ac.uk/haig-fras/layers/bathymetry/emodnet/emodnet_2022.tif'), name="COG Layer", attribution="COG Data")
            if plot_type == 'plotly':
                fig = zarr_vis.plot_data_on_mapbox()
                st.markdown(f'##### {subdata_select[:-5]}')
                st.plotly_chart(fig)
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
                    "colormap_name": "viridis",
                }
                encoded_params = urllib.parse.urlencode(params)

                url = f"{tileserver_url}{tileserver_enpoint}?{encoded_params}"
                print(url)
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


