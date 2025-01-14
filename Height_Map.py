import os
import base64
import shutil
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as colors
import imageio
import streamlit as st
from ridge_map import RidgeMap

filename = "./Height_Map"

# Streamlit app setup
st.title("Elevation Map Generator")
st.sidebar.header("Configuration")

# Label configuration section
with st.sidebar.expander("Label Configuration"):
    Label = st.text_input("Map Label", "Washington")
    Label_Size = st.slider("Label Size", min_value=10, max_value=500, step=1, value=20, help="Font size of the label.")
    col1, col2 = st.columns(2)
    with col1:
        Label_X = st.slider("Label X Position", min_value=0.0, max_value=1.0, step=0.01, value=0.85, help="X position of the label.")
    with col2:
        Label_Y = st.slider("Label Y Position", min_value=0.0, max_value=1.0, step=0.01, value=0.8, help="Y position of the label.")

# Sidebar sections
with st.sidebar.expander("Bounding Box Coordinates"):
    # Create two columns for coordinate input
    col1, col2 = st.columns(2)
    with col1:
        max_longitude = st.number_input("Max Longitude", value=-116.463262)
        min_longitude = st.number_input("Min Longitude", value=-124.848974)
    with col2:
        max_latitude = st.number_input("Max Latitude", value=49.345786)
        min_latitude = st.number_input("Min Latitude", value=46.292035)

# Coordinates tuple
Coordinates = (min_longitude, min_latitude, max_longitude, max_latitude)

# Map appearance section
with st.sidebar.expander("Map Appearance"):
    Color_Map = st.selectbox("Color Map", list(plt.colormaps())+list(colors.CSS4_COLORS), index=plt.colormaps().index("plasma"))
    Background_Color = st.color_picker("Background Color", value="#FFEDC4", help="Select the background color of the map.")
    Max_Lines = st.slider("Max Number of Lines", min_value=10, max_value=400, step=10, value=100)
    Line_Width = st.slider("Line Width", min_value=0.1, max_value=10.0, step=0.1, value=1.0, help="Width of the elevation lines.")
    Vertical_Ratio = st.slider("Vertical Ratio", min_value=1, max_value=500, step=1, value=120, help="Adjusts the vertical exaggeration.")
    Scale = st.slider("Map Scale", min_value=1.0, max_value=400.0, step=0.5, value=20.0, help="Adjusts the map scale.")
    
if Color_Map in plt.colormaps():
    Line_Color = plt.get_cmap(Color_Map)
else:
    Line_Color = Color_Map

# Preprocessing configuration
with st.sidebar.expander("Data Configuration"):
    Lake_Flatness = st.slider("Lake Flatness", min_value=0, max_value=100, step=1, value=1, help="Controls the smoothness of lake regions.")
    Water_Ntile = st.slider("Water Ntile", min_value=0, max_value=100, step=1, value=20, help="Determines the percentile for water level.")

# Frame generation and GIF configuration
with st.sidebar.expander("GIF Configuration"):
    Change = st.selectbox("Modified Value", ["Number of Lines","Vertical Ratio"])
    Step = st.slider("Steps per Frame", min_value=1, max_value=100, step=1, value=10, help="The amount of change per frame")
    Duration = st.slider("GIF Frame Duration (seconds)", min_value=0.1, max_value=5.0, step=0.1, value=0.5)

# Generate PNG button
if st.sidebar.button("Generate PNG"):
    st.warning("Generating PNG...")
    
    # Delete previous files
    if os.path.exists(filename + ".png"):
        os.remove(filename + ".png")
    if os.path.exists(filename + ".gif"):
        os.remove(filename + ".gif")

    # Initialize RidgeMap for the specified coordinates
    rm = RidgeMap(Coordinates)

    # Generate elevation data and process it
    values = rm.get_elevation_data(num_lines=Max_Lines)
    processed_values = rm.preprocess(values=values, lake_flatness=Lake_Flatness, water_ntile=Water_Ntile, vertical_ratio=Vertical_Ratio)

    # Plot the map
    rm.plot_map(
        values=processed_values,
        label=Label,
        label_y=Label_Y,
        label_x=Label_X,
        label_size=Label_Size,
        line_color=Line_Color,
        kind="elevation",
        linewidth=Line_Width,
        background_color=Background_Color,
        size_scale=Scale,
    )

    plt.savefig(filename)
    plt.close()

# Generate GIF button
if st.sidebar.button("Generate GIF", help="Ensure that scale, Steps per Frame and Max Lines are not too high, otherwise program will crash"):
    st.warning("Generating GIF...")

    # Delete previous files
    if os.path.exists(filename + ".png"):
        os.remove(filename + ".png")
    if os.path.exists(filename + ".gif"):
        os.remove(filename + ".gif")

    # Initialize RidgeMap for the specified coordinates
    rm = RidgeMap(Coordinates)

    # Set up directories
    frame_dir = "./Frames"
    if os.path.exists(frame_dir):
        shutil.rmtree(frame_dir)
    os.makedirs(frame_dir)

    # Generate frames
    images = []
    if Change == "Number of Lines":
        for x in range(10, Max_Lines, Step):
            values = rm.get_elevation_data(num_lines=x)
            processed_values = rm.preprocess(values=values, lake_flatness=Lake_Flatness, water_ntile=Water_Ntile, vertical_ratio=Vertical_Ratio)
    
            rm.plot_map(
                values=processed_values,
                label=Label,
                label_y=Label_Y,
                label_x=Label_X,
                label_size=Label_Size,
                line_color=Line_Color,
                kind="elevation",
                linewidth=Line_Width,
                background_color=Background_Color,
                size_scale=Scale,
            )
            
            frame_path = os.path.join(frame_dir, f"{x}.png")
            plt.savefig(frame_path)
            plt.close()
            images.append(imageio.v2.imread(frame_path))
        
    if Change == "Vertical Ratio":
        for x in range(1, Vertical_Ratio, Step):
            values = rm.get_elevation_data(num_lines=Max_Lines)
            processed_values = rm.preprocess(values=values, lake_flatness=Lake_Flatness, water_ntile=Water_Ntile, vertical_ratio=x)
    
            rm.plot_map(
                values=processed_values,
                label=Label,
                label_y=Label_Y,
                label_x=Label_X,
                label_size=Label_Size,
                line_color=Line_Color,
                kind="elevation",
                linewidth=Line_Width,
                background_color=Background_Color,
                size_scale=Scale,
            )

            frame_path = os.path.join(frame_dir, f"{x}.png")
            plt.savefig(frame_path)
            plt.close()
            images.append(imageio.v2.imread(frame_path))

    # Create GIF
    filename = "./Height_Map.gif"
    imageio.mimsave(filename, images, duration=Duration)
    
st.fragment(run_every="5s")
def display_file():
    if os.path.exists(filename + ".png"):
        st.success("PNG generation complete")
        file_ = open(filename + ".png", "rb")
        contents = file_.read()
        data_url = base64.b64encode(contents).decode("utf-8")
        file_.close()
    
        st.markdown(
            f'<img src="data:image/gif;base64,{data_url}" alt="Generated PNG">',
            unsafe_allow_html=True,
        )
    if os.path.exists(filename + ".gif"):
        st.success("GIF generation complete")
        file_ = open(filename + ".gif", "rb")
        contents = file_.read()
        data_url = base64.b64encode(contents).decode("utf-8")
        file_.close()
    
        st.markdown(
            f'<img src="data:image/gif;base64,{data_url}" alt="Generated GIF">',
            unsafe_allow_html=True,
        )
        
display_file()

st.sidebar.write("---")
st.sidebar.write("Application by Freeman - https://github.com/Freeman-Trader")
st.sidebar.write("Special Credits to:")
st.sidebar.write("http://www.acgeospatial.co.uk/ridge-map-plots-using-python/")
st.sidebar.write("https://github.com/ColCarroll/ridge_map/tree/main")