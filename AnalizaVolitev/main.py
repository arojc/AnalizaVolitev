from pyproj import Transformer
import json
import pandas as pd

from izidi_zemljevid import *

def to_geojson():

    transformer = Transformer.from_crs("EPSG:3794", "EPSG:4326", always_xy=True)

    with open("zemljevidi/sredisca_1.json") as f:
        data = json.load(f)

    features = []

    for name, x, y in data:
        lon, lat = transformer.transform(x, y)

        features.append({
            "type": "Feature",
            "properties": {"name": name},
            "geometry": {
                "type": "Point",
                "coordinates": [lon, lat]
            }
        })

    geojson = {"type": "FeatureCollection", "features": features}

    with open("tocke.geojson", "w") as f:
        json.dump(geojson, f, indent=2, ensure_ascii=False)

def odstrani_najdena():

    vsa = pd.read_csv(f"zemljevidi/volisca_iskana.csv", index_col=False)
    try:
        vsa.drop('Unnamed: 0', axis=1, inplace=True)
    except:
        pass
    najdena = pd.read_csv(f"zemljevidi/volisca_output.csv", index_col=False)

    df3 = vsa[~vsa["naslov"].isin(najdena["address"])]

    # df3 = pd.concat([vsa, najdena])
    df3.to_csv("zemljevidi/volisca_iskana.csv", index=False)

    print(len(df3))
    print(df3.columns)
    print(df3.head(5))

def concatenate():

    vsa = pd.read_csv(f"zemljevidi/volisca_najdena.csv", index_col=False)
    vsa.drop('Unnamed: 0', axis=1, inplace=True)
    najdena = pd.read_csv(f"zemljevidi/volisca_output.csv", index_col=False)

    df3 = pd.concat([vsa, najdena])
    df3.to_csv("zemljevidi/volisca_najdena.csv", index=False)

    print(len(df3))
    print(df3.columns)
    print(df3.head(5))

def clean_volisca():

    vsa = pd.read_csv(f"zemljevidi/volisca_najdena.csv", index_col=False)
    vsa.drop('Unnamed: 0', axis=1, inplace=True)
    najdena = pd.read_csv(f"zemljevidi/volisca_output.csv", index_col=False)

    df3 = pd.concat([vsa, najdena])
    # df3.drop(columns=['Unnamed: 0'])
    df3.to_csv("zemljevidi/volisca_najdena.csv", index=False)

    # df3 = vsa[~vsa["naslov"].isin(najdena["address"])]    # m1 = m[]
    # df3.to_csv("zemljevidi/volisca_iskana_1.csv", index=False)

    # print(df.head(5))

    # df1 = df.dropna()
    # df2 = df[df['lat'].isnull()]
    print(len(df3))
    print(df3.columns)
    print(df3.head(5))
    # print(len(najdena))
    # print(najdena.columns)
    # print(najdena.head(5))

    # df1.to_csv("zemljevidi/volisca_najdena_1.csv")
    # df2.to_csv("zemljevidi/volisca_zgubljena.csv")


# def split_by_coords(files):
#     with_coords = []
#     without_coords = []
#
#     for f in files:
#         df = pd.read_csv(f)
#
#         mask = df["Latitude"].notna() & df["Longitude"].notna()
#
#         with_coords.append(df[mask])
#         without_coords.append(df[~mask])
#
#     # združi vse tri datoteke
#     df_with = pd.concat(with_coords, ignore_index=True)
#     df_without = pd.concat(without_coords, ignore_index=True)
#
#     # shrani
#     df_with.to_csv("z_koordinatami.csv", index=False)
#     df_without.to_csv("brez_koordinat.csv", index=False)

def split_by_coords(files):
    with_coords = []
    without_coords = []

    for f in files:
        df = pd.read_csv(f)

        # če so prazni stringi
        df[["Latitude", "Longitude"]] = df[["Latitude", "Longitude"]].replace("", pd.NA)

        mask = df["Latitude"].notna() & df["Longitude"].notna()

        with_coords.append(df[mask])
        without_coords.append(df[~mask].drop(columns=["Latitude", "Longitude"]))

    df_with = pd.concat(with_coords, ignore_index=True)
    df_without = pd.concat(without_coords, ignore_index=True)

    df_with.to_csv("z_koordinatami_1.csv", index=False)
    df_without.to_csv("brez_koordinat_2.csv", index=False)
# split_by_coords(["zemljevidi/brez_koordinat_1a.csv", "zemljevidi/brez_koordinat_2a.csv"])


# draw_map(2022, "SVOBODA-%", True, True)
# draw_dots()

# odstrani_najdena()
# concatenate()

