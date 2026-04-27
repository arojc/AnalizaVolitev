from pyproj import Transformer
import json

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


draw_map(2024, "VESNA-%", True, True)
# draw_dots()

