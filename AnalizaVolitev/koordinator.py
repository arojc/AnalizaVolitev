import pandas as pd
import matplotlib.pyplot as plt
import math
import json

from shapely.geometry import Point, Polygon
from pyproj import Transformer

import pandas as pd

from izidi_zemljevid import draw_districts



INPUT_FILE = "zemljevidi/volisca_iskana.csv"
OUTPUT_FILE = "zemljevidi/volisca_output.csv"
CACHE_FILE = "zemljevidi/cache.json"

def plot_two_csv(input_file):

    df1 = pd.read_csv(input_file)
    # df1 = df.query("Longitude>13.25 and Latitude<47 and Latitude>45 and Latitude>Longitude+30.15")
    # df2 = df.query("Longitude<13.25 or Latitude>47 or Latitude<45 or Latitude<Longitude+30.15")
    # print(len(df2))
    # print(df2.columns)
    # print(df2[["Volilni okraj", "ID Volišča"]])

    fig, ax = plt.subplots()
    draw_districts(ax, "black", False)

    plt.scatter(df1["Longitude"], df1["Latitude"], s=10, label="df1")

    plt.show()


def razdeli_na_100():

    chunk_size = 100
    file1 = "volisca/volisca.csv"

    df1 = pd.read_csv(file1)

    print(df1.head(5))

    for i in range(math.ceil(len(df1) / chunk_size)):
        df1.iloc[i * chunk_size:(i + 1) * chunk_size].to_csv(f"volisca/volisca_{i + 1}.csv", index=False)


def merge_csv():
    df = pd.concat(
        [pd.read_csv(f"volisca/volisca_2/volisca_{i}.csv") for i in range(1, 30)],
        ignore_index=True
    )

    df.to_csv("volisca/volisca_2/volisca_vsa.csv", index=False)



def latlon_to_d96(lat, lon):
    # WGS84 -> D96/TM
    transformer = Transformer.from_crs(
        "EPSG:4326",   # lat/lon
        "EPSG:3794",   # D96/TM
        always_xy=True
    )
    x, y = transformer.transform(lon, lat)
    return x, y

def point_in_polygon(lat, lon, polygon_points):
    # polygon = Polygon([(lon, lat) for lat, lon in polygon_points])
    polygon = Polygon(polygon_points)
    point = Point(latlon_to_d96(lat, lon))

    # print(polygon.area)

    return polygon.contains(point) or polygon.covers(point) or polygon.intersects(point)

def find_polygon_by_name(polygons, name):
    for p in polygons:
        # print(p["properties"]["NAZIV"])
        if p["properties"]["NAZIV"].lower() == "Maribor 3".lower():
            return [p["geometry"]["coordinates"][0][0], p["geometry"]["coordinates"][1][0]]
        if p["properties"]["NAZIV"].lower() == name.lower():
            return [p["geometry"]["coordinates"][0]]
    print(f"{p["properties"]["NAZIV"].lower()} == {name.lower()}")
    return None


def check_points_in_polygons(number):
    da = 0
    none = 0
    ne = 0
    # naloži poligone
    with open("zemljevidi/volilni_okraji.json") as f:
        polygons1 = json.load(f)
        polygons = polygons1["features"]

    # naloži točke
    df = pd.read_csv(f"volisca/volisca_{number}/volisca_vsa.csv")

    results = []

    for _, row in df.iterrows():
        pid = " ".join(str(row["Volilni okraj"]).split(' ')[3:])

        the_polygons = find_polygon_by_name(polygons, pid)

        if the_polygons is None:
            results.append(False)
            # continue
            print("Polygon not found")
            continue

        inside = False
        for p in the_polygons:
            tmp = point_in_polygon(
                row["Latitude"],
                row["Longitude"],
                p
            )
            inside = inside or tmp

        if inside:
            da += 1
        elif row["Latitude"] == '':
            none += 1
        else:
            print(row["Latitude"])
            ne+=1

        results.append(inside)

    df["inside_polygon"] = results

    df.to_csv(f"volisca/volisca_{number}/checked_points.csv", index=False)
    print(f"DA: {da} - NONE: {none} - NE: {ne}")


def convert_csv_3794_to_4326(input_csv, output_csv):
    df = pd.read_csv(input_csv)
    df.to_csv(output_csv, index=False)

def switch_lat_lon(input_csv, output_csv):
    df = pd.read_csv(input_csv)

    lon, lat = df["Latitude"].values, df["Longitude"].values

    df["Latitude"] = lat
    df["Longitude"] = lon

    df.to_csv(output_csv, index=False)





# convert_csv_3794_to_4326("volisca/volisca_1/volisca_vsa.csv", "volisca/volisca_1/checked_points.csv")
# convert_csv_3794_to_4326("volisca/volisca_2/volisca_vsa.csv", "volisca/volisca_2/checked_points.csv")
# switch_lat_lon("volisca/volisca_2/checked_points.csv", "volisca/volisca_2/checked_points.csv")

# plot_two_csv("volisca/volisca_2/checked_points.csv")
# check_points_in_polygons(2)