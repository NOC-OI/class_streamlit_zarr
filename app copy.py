import os
import leafmap.foliumap as leafmap
import leafmap.colormaps as cm
import streamlit as st
from streamlit_zarr.zarr_visualization_new import ZarrVisualization
import urllib
st.set_page_config(layout="wide")

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

st.write(f"Data Path: {zarr_vis.data_path}")

ds = load_zarr_file(zarr_vis, subdata_select)

st.write(f"Dataset dimensions: {ds.sizes}")

if "x" in ds.dims and "bounds" not in subdata_select:
    st.markdown('#### SELECT LIMITS')

    # m = leafmap.Map(google_map="SATELLITE", latlon_control=False)

    lat_limits = st.slider(
        'Select latitude limits',
        -89, 89, (40, 60))

    lon_limits = st.slider(
        'Select longitude limits',
        -179, 179, (-54, -37))

    time_counter_limit = None
    if 'time_counter' in list(ds.coords):
        time_values = ds.time_counter.values
        time_counter_limit = st.selectbox("Select the timestamp", time_values)

    limits = [lat_limits, lon_limits, time_counter_limit]
    # limits = [time_counter_limit]

    plot_data = st.button("Clip and Plot Data", key='plot_data')

    if plot_data:
        st.markdown('#### RESULTS')
        with st.spinner("Preparing and plotting data..."):
            # st.write("Clipping Data...")
            zarr_vis.sel_zarr_data(ds, limits)
            # st.write("Reproject Data...")
            # zarr_vis.reproject_data()
            # st.write("Convert to geotiff and plot...")
            # geotiff_file = zarr_vis.convert_to_geotiff()
            # st.write("Plotting Data...")
            fig = zarr_vis.plot_data_on_mapbox()
            # png_file = zarr_vis.convert_to_png()

        # st.write('Data dimensions:')
        # for dims in zarr_vis.ds.sizes:
        #     st.write(f"{dims}: {zarr_vis.ds.sizes[dims]}")

        try:
            # m.add_local_tile(geotiff_file, colormap="terrain", layer_name=subdata_select[:-5], debug=True)
            # image = leafmap.ImageOverlay(url=png_file, bounds=(
            #     (zarr_vis.limits[0][0], zarr_vis.limits[0][1]), (zarr_vis.limits[1][0], zarr_vis.limits[1][1])))

            # m.add_layer(image)
            # m.add_tile_layer(url="https://titiler.xyz/cog/tiles/WebMercatorQuad/{z}/{x}/{y}.png?colormap_name=RdBu_r&url=" + urllib.parse.quote(geotiff_file), name="COG Layer", attribution="COG Data")

            # import numpy as np
            # latitudes = zarr_vis.ds.y.values
            # st.write(latitudes)
            # latitude_grid = np.tile(latitudes[:, np.newaxis], (1, ds.x.size)).flatten()
            # st.write(latitude_grid)

            # longitudes = zarr_vis.ds.x.values
            # st.write(longitudes)
            # longitude_grid = np.tile(longitudes[:, np.newaxis], (ds.y.size,1)).flatten()
            # st.write(longitude_grid)

            # data_values = zarr_vis.ds.values.flatten()
            # st.write(data_values.shape, latitude_grid.shape, longitude_grid.shape)
            st.markdown(f'##### {subdata_select[:-5]}')
            st.plotly_chart(fig)
            # m.add_raster(geotiff_file, colormap="RdBu_r", layer_name=subdata_select[:-5], debug=True)
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

# m.to_streamlit()
