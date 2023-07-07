import folium

def plot_coordinates_on_map(coordinates, output_file):
    # Create a map object
    map_object = folium.Map()

    # Plot each coordinate on the map
    for key, value in coordinates.items():
        lat = value['lat']
        lon = value['lon']
        folium.Marker(location=[lat, lon], popup=key).add_to(map_object)

    # Save the map as an HTML file
    map_object.save(output_file)
