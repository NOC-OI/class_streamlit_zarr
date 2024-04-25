import os
import leafmap.foliumap as leafmap
import leafmap.colormaps as cm
import streamlit as st
from streamlit_zarr.zarr_visualization import ZarrVisualization

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


st.title("Visualize Raster Datasets")
st.markdown(
    """
An interactive web app for visualizing local raster datasets).
"""
)

if 'open_zarr_button' not in st.session_state:
    st.session_state.disabled = True

zarr_vis = load_file_list()
variable_select = st.selectbox("Select the type of data", zarr_vis.list_of_variables)

subdata_select = st.selectbox("Select the variable", zarr_vis.get_list_of_subdata(variable_select))

zarr_vis.update_data_path(variable_select, subdata_select)

st.write(f"Data Path: {zarr_vis.data_path}")

ds = load_zarr_file(zarr_vis, subdata_select)

m = leafmap.Map(latlon_control=False)


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

plot_data = st.button("Clip and Plot Data", key='plot_data')


if plot_data:
    with st.spinner('Clipping and Plotting Data...'):
        zarr_vis.sel_zarr_data(ds, limits)
        geotiff_file = zarr_vis.convert_to_geotiff()
        
    # st.write('Data dimensions:')
    # for dims in zarr_vis.ds.sizes:
    #     st.write(f"{dims}: {zarr_vis.ds.sizes[dims]}")

    try:
        m.add_raster(geotiff_file, colormap="terrain", layer_name=subdata_select[:-5])
    except Exception as e:
        st.error(e)
        st.error("Work in progress. Try it again later.")
    
    m.to_streamlit()



