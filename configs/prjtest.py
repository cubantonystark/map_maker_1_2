def generate_prj(lat, lon):
    prj_content = f'GEOGCS["WGS 84",DATUM["WGS_1984",SPHEROID["WGS 84",6378137,298.257223563,AUTHORITY["EPSG","7030"]],AUTHORITY["EPSG","6326"]],PRIMEM["Greenwich",0],UNIT["degree",0.0174532925199433],AUTHORITY["EPSG","4326"]]'

    with open('output.prj', 'w') as prj_file:
        prj_file.write(prj_content)


if __name__ == "__main__":
    latitude = float(input("Enter latitude: "))
    longitude = float(input("Enter longitude: "))

    generate_prj(latitude, longitude)
    print("Projection file generated as 'output.prj'")