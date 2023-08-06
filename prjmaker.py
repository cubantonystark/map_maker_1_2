import pyproj

def get_epsg_code(latitude, longitude):
    transformer = pyproj.Transformer.from_crs('EPSG:4326', 'EPSG:3857', always_xy=True)
    x, y = transformer.transform(longitude, latitude)
    zone_number = (x + 180) // 6 + 1
    epsg_code = 32600 + zone_number
    return int(epsg_code)

# Example latitude and longitude
latitude = 41.80819641
longitude = -0.85973448

# Get EPSG code
epsg_code = get_epsg_code(latitude, longitude)
print("EPSG code:", epsg_code)