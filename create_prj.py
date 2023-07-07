import utm

latlon = input("Please enter the latitude and longitude separated by a comma: ")

lat, lon = latlon.split(',')

utm_easting, utm_northing, zone, zone_letter = utm.from_latlon(float(lat), float(lon))

utm_easting = "%.2f" % utm_easting

utm_northing = "%.2f" % utm_northing

zone = str(zone) + zone_letter

prj_1 = 'PROJCS["WGS 84 / UTM zone '

prj_2 = '",GEOGCS["WGS 84",DATUM["WGS_1984",SPHEROID["WGS 84",6378137,298.257223563,AUTHORITY["EPSG","7030"]],AUTHORITY["EPSG","6326"]],PRIMEM["Greenwich",0,AUTHORITY["EPSG","8901"]],UNIT["degree",0.0174532925199433,AUTHORITY["EPSG","9122"]],AUTHORITY["EPSG","4326"]],PROJECTION["Transverse_Mercator"],PARAMETER["latitude_of_origin",0],PARAMETER["central_meridian",-81],PARAMETER["scale_factor",0.9996],PARAMETER["false_easting",500000],PARAMETER["false_northing",0],UNIT["metre",1,AUTHORITY["EPSG","9001"]],AXIS["Easting",EAST],AXIS["Northing",NORTH],AUTHORITY["EPSG","32617"]]'

with open('imgenious.xyz', 'w') as xyz:
    xyz.write(str(utm_easting + " " + str(utm_northing) + " " + "101.000"))

with open('imgenious.prj', 'w') as prj:
    prj.write(str(prj_1) + str(zone) + str(prj_2))