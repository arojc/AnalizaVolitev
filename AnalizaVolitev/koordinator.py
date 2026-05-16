import pandas as pd
import matplotlib.pyplot as plt
import math
from izidi_zemljevid import draw_units, draw_districts

INPUT_FILE = "zemljevidi/volisca_iskana.csv"
OUTPUT_FILE = "zemljevidi/volisca_output.csv"
CACHE_FILE = "zemljevidi/cache.json"

def plot_two_csv():
    file1 = "volisca/volisca_2/volisca_29.csv"

    df1 = pd.read_csv(file1)

    plt.figure(figsize=(8, 8))

    plt.scatter(df1["Longitude"], df1["Latitude"], s=10, label="df1")

    plt.xlabel("Longitude")
    plt.ylabel("Latitude")
    plt.legend()
    plt.title("Točke iz dveh CSV")

    draw_districts()

    plt.show()


def razdeli_na_100():

    chunk_size = 100
    file1 = "volisca/volisca.csv"

    df1 = pd.read_csv(file1)

    print(df1.head(5))

    for i in range(math.ceil(len(df1) / chunk_size)):
        df1.iloc[i * chunk_size:(i + 1) * chunk_size].to_csv(f"volisca/volisca_{i + 1}.csv", index=False)

    # df1.to_csv("volisca.csv", index=False)


def merge_csv():
    df = pd.concat(
        [pd.read_csv(f"volisca/volisca_2/volisca_{i}.csv") for i in range(1, 30)],
        ignore_index=True
    )

    df.to_csv("volisca/volisca_2/volisca_vsa.csv", index=False)

# plot_two_csv()
# razdeli_na_100()