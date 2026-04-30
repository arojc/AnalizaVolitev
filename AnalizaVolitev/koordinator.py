import pandas as pd

import csv
import time
import json
import re
from geopy.geocoders import Nominatim

INPUT_FILE = "zemljevidi/volisca_iskana.csv"
OUTPUT_FILE = "zemljevidi/volisca_output.csv"
CACHE_FILE = "zemljevidi/cache.json"

def izlusci_okraj(okraj:str):
    okrajarr = okraj.split(' ')
    if len(okrajarr[-1]) == 1:
        okrajarr = okrajarr[:-1]
    okrajarr = ' '.join(okrajarr[3:])
    okrajarr = okrajarr[0].upper() + okrajarr[1:].lower()
    return okrajarr

def replace_shorthands(address: str):
    addtmp = re.sub(r"\b[a-zA-ZčšžČŠŽ]{1,5}\.", '', address) # replace shorthands
    return addtmp

def process_address_b(address: str):
    addtmp = replace_shorthands(address)
    add = addtmp.replace(', ', ',').split(',')
    address1 = ', '.join([add[-1], add[0]])
    return address1

def process_address(address: str):

    addtmp = re.sub(r"\b[a-zA-ZčšžČŠŽ]{1,5}\.", '', address) # replace shorthands
    add = addtmp.replace(', ', ',').split(',')
    address1 = ', '.join(add[-2:])
    return address1


def geocode(cache, geolocator, address, okraj=""):
    if address in cache:
        # print("Address in cache")
        return cache[address]

    try:
        # print("Locating")
        address_a = process_address(address)
        address_b = process_address_b(address)
        loc = geolocator.geocode(address_a + ", Slovenia", timeout=10)
        locb = geolocator.geocode(address_b + ", Slovenia", timeout=10)
        locc = geolocator.geocode(address_a + ", " + izlusci_okraj(okraj), timeout=10)
        if loc:
            result = (loc.latitude, loc.longitude)
        elif locb:
            result = (locb.latitude, locb.longitude)
            print(".", end='')
        elif locc:
            result = (locb.latitude, locb.longitude)
            print(":", end='')
        else:
            result = (None, None)
    except:
        result = (None, None)
        # print("Exception")

    if (result[0] is not None) and (result[1] is not None):
        cache[address] = result
    return result


def geocode_all():
    try:
        with open(CACHE_FILE) as f:
            cache = json.load(f)
    except:
        cache = {}

    geolocator = Nominatim(user_agent="geo_batch")


    with open(INPUT_FILE) as f, open(OUTPUT_FILE, "w", newline="") as out:
        reader = csv.DictReader(f)
        writer = csv.writer(out)
        writer.writerow(["address", "lat", "lon"])

        for i, row in enumerate(reader, start=len(cache)):
            addr = row["naslov"]
            okraj = row["okraj"]

            lat, lon = geocode(cache, geolocator, addr, okraj)
            if (lat is not None) and (lon is not None):
                writer.writerow([addr, lat, lon])

            # shrani cache vsakih 100
            if i % 50 == 0:
                with open(CACHE_FILE, "w") as f:
                    json.dump(cache, f)
                print(f"volisce {i}")

            time.sleep(1)  # Nominatim limit!

    # final save
    with open(CACHE_FILE, "w") as f:
        json.dump(cache, f)


# geocode_all()



# naslov = "Mali Rakitovec 15, Blagovica"
# try:
#     with open(CACHE_FILE) as f:
#         cache = json.load(f)
# except:
#     cache = {}
#
# geolocator = Nominatim(user_agent="geo_batch")
#
# print(geocode(cache, geolocator, naslov))
#
# print(naslov)
# print(process_address(naslov))
# print(process_address_b(naslov))

# print(izlusci_okraj("VO 1006 - KRANJ 3"))


# print(process_address("Osnovka, zadnji vhod,Orodišče Kočna, Kočna bš,Kočna"))
# print(geocode(cache, geolocator, process_address(naslov)))

import pandas as pd
import matplotlib.pyplot as plt

def plot_two_csv(file1="zemljevidi/volisca_najdena.csv", file2="zemljevidi/volisca_najdena_1.csv", file3="zemljevidi/volisca_najdena_2.csv"):
    df1 = pd.read_csv(file1)
    print(df1.head(5))

    print(df1.loc[df1["lat"].idxmin(), "address"])
    print(df1.loc[df1["lon"].idxmax(), "address"])

    df2 = pd.read_csv(file2)
    df3 = pd.read_csv(file3)

    plt.figure(figsize=(8, 8))

    plt.scatter(df1["lon"], df1["lat"], s=10, label="df1")
    plt.scatter(df2["lon"], df2["lat"], s=10, label="df2")
    plt.scatter(df3["lon"], df3["lat"], s=10, label="df2")

    plt.xlabel("Longitude")
    plt.ylabel("Latitude")
    plt.legend()
    plt.title("Točke iz dveh CSV")

    plt.show()

plot_two_csv()