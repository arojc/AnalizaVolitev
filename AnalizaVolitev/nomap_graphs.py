import numpy as np
import pandas as pd

from tkinter import *
import matplotlib
matplotlib.use("TkAgg")
import matplotlib.pyplot as plt
from scipy.stats import gaussian_kde


default_col = "Udelezba-%"
ve = "Volilna_Enota"
vo = "Volilni_Okraj"
id = "ID_Volisca"
lvlv = "volisca"
lvlo = "okraji"

def dot_size(level):

    if level == "volisca":
        dot_size = 1
    elif level == "okraji":
        dot_size = 10

    return dot_size

def dodaj_odstotek(word):
    return word + "-%"

def get_data(df1, party1):

    if dodaj_odstotek(party1) not in df1:
        p1_old = (df1[[vo, default_col]])
        p1_old[default_col] = 0
        print("Not found")
    else:
        p1_old = (
            df1[[vo, dodaj_odstotek(party1)]]
        )
        print("Found")

    return p1_old

def get_data_1(df1, party1, level):

    if dodaj_odstotek(party1) not in df1:
        if level == lvlv:
            p1_old = (df1[[ve, vo, id, default_col]])
        else:
            p1_old = (df1[[ve, vo, default_col]])
        p1_old[default_col] = 0
        p1_old = p1_old.rename(columns={default_col: dodaj_odstotek(party1)})
        print("Not found")
    elif level == lvlv:
        p1_old = (
            df1[[ve, vo, id, dodaj_odstotek(party1)]]
        )
        print("Found")
    elif level == lvlo:
        p1_old = (
            df1[[ve, vo, dodaj_odstotek(party1)]]
        )
        print("Found")

    return p1_old

def sheet_to_csv(volitve, shname="Podatki"):
    try:
        df1 = pd.read_excel(f"volitve_{volitve}/izidi.ods", engine="odf", sheet_name=shname)
        df1.to_csv(f"volitve_{volitve}/{shname}.csv")
    except:
        print(f"{shname} not found")

def remove_outliers(xs, ys, n, std=False):
    xs = np.asarray(xs)
    ys = np.asarray(ys)

    # povprečje
    mx = xs.mean()
    my = ys.mean()

    sx = xs.std()
    sy = ys.std()

    if std:
        # standardizirana razdalja
        dist = np.sqrt(
            ((xs - mx) / sx)**2 +
            ((ys - my) / sy)**2
        )
    else:
        dist = np.sqrt(
            (xs - mx)**2 +
            (ys - my)**2
        )

    # # razdalja od povprečja
    # dist = np.sqrt((xs - mx)**2 + (ys - my)**2)

    # indeksi n najbolj oddaljenih
    outliers = np.argsort(dist)[-n:]

    # obdrži ostale
    mask = np.ones(len(xs), dtype=bool)
    mask[outliers] = False

    x_new = xs[mask]
    y_new = ys[mask]

    return x_new, y_new

def reg_slope(xs, ys):
    return np.corrcoef(xs, ys)[0, 1]

def reg_fun_1d(xs, ys):

    slope, intercept = np.polyfit(xs, ys, 1)

    reg_x = np.linspace(xs.min(), xs.max(), 100)
    reg_y = slope * reg_x + intercept

    return reg_x, reg_y

def reg_fun(xs, ys, deg=2):
    x = np.linspace(min(xs), max(xs), len(xs))

    coefs = np.polyfit(xs, ys, deg)

    thef = np.poly1d(coefs)
    y = thef(x)

    return x, y

def get_params_from_level(level):

    mergeon = ["Volilna_Enota", "Volilni_Okraj"]
    if level == "volisca":
        mergeon.append("ID_Volisca")

    return mergeon


def get_the_points(election1, election2, parties, level="volisca"):

    pall = pd.DataFrame()
    mergeon = get_params_from_level(level)

    df1 = pd.read_csv(f"volitve_{election1}/{level}.csv", on_bad_lines='skip', lineterminator='\n')
    df2 = pd.read_csv(f"volitve_{election2}/{level}.csv", on_bad_lines='skip', lineterminator='\n')

    for party in parties:
        p1_old = get_data_1(df1, party, level).dropna()
        p1_new = get_data_1(df2, party, level).dropna()

        p1 = p1_old.merge(
            p1_new,
            on=mergeon,
            how="inner",
            suffixes=("_before", "_after")
        )

        if pall.empty:
            pall = p1
        else:
            pall = pall.merge(
                p1,
                on=mergeon,
                how="inner"
            )

    if len(parties) == 1:
        xs = (pall.iloc[:, -2]).to_numpy()
        ys = (pall.iloc[:, -1]).to_numpy()
    elif len(parties) == 2:
        xs = (pall.iloc[:, -3] - pall.iloc[:, -4]).to_numpy()
        ys = (pall.iloc[:, -1] - pall.iloc[:, -2]).to_numpy()

    xs = np.array(xs)
    ys = np.array(ys)

    return xs, ys

def plot_party_shift(election1, election2, party1, party2, regression=True, level="volisca"):

    xs, ys = get_the_points(election1, election2, [party1, party2], level)

    xy = np.vstack([xs, ys])
    z = gaussian_kde(xy)(xy)
    idx = z.argsort()

    plt.figure(figsize=(8, 8))

    plt.scatter(
        xs,
        ys,
        s=dot_size(level),
        alpha=0.6
    )

    # plt.hexbin(xs, ys, gridsize=100, cmap="viridis")

    plt.axhline(0)
    plt.axvline(0)

    if regression:
        reg_x, reg_y = reg_fun(xs, ys, 1)
        plt.plot(reg_x, reg_y, color="red")

    plt.xlabel(f"Sprememba podpore: {party1}")
    plt.ylabel(f"Sprememba podpore: {party2}")

    plt.title(f"Sprememba podpore po okrajih - R={round(reg_slope(xs, ys), 3)}")

    plt.show()




def plot_change_histogram(election1, election2, party, level="okraji"):
    # =========================
    # TUKAJ NALOŽI PODATKE
    # =========================

    df1 = pd.read_csv(f"volitve_{election1}/{level}.csv", on_bad_lines='skip', lineterminator='\n')
    df2 = pd.read_csv(f"volitve_{election2}/{level}.csv", on_bad_lines='skip', lineterminator='\n')

    before = get_data(df1, party).dropna()
    after = get_data(df2, party).dropna()

    # =========================
    # ZDRUŽI PODATKE
    # =========================

    df = before.merge(
        after,
        on=vo,
        how="outer",
        suffixes=("_before", "_after")
    ).fillna(0)

    # =========================
    # SPREMEMBA
    # =========================

    delta = (
        df[f"{dodaj_odstotek(party)}_after"]
        - df[f"{dodaj_odstotek(party)}_before"]
    )

    # =========================
    # HISTOGRAM
    # =========================

    plt.figure(figsize=(8, 5))

    plt.hist(delta, bins=30)

    plt.xlabel("Sprememba podpore (%)")
    plt.ylabel("Število okrajev")

    plt.title("Histogram spremembe podpore")

    plt.axvline(0)

    plt.show()



def plot_change_scatter(election1, election2, party, level="okraji"):

    x, y = get_the_points(election1, election2, [party], level)

    # =========================
    # GRAF
    # =========================

    plt.figure(figsize=(8, 8))

    plt.scatter(x, y, s=dot_size(level), alpha=0.7)

    # diagonala brez spremembe
    mn = min(x.min(), y.min())
    mx = max(x.max(), y.max())

    plt.plot([mn, mx], [mn, mx], linestyle=":")

    reg_x, reg_y = reg_fun(x, y)
    plt.plot(reg_x, reg_y, color="red")
    # reg_x, reg_y = reg_fun(x, y, 1)
    # plt.plot(reg_x, reg_y, color="orange")

    plt.xlabel("Podpora prej (%)")
    plt.ylabel("Podpora zdaj (%)")

    plt.title(f"Sprememba podpore po okrajih - {party}")

    plt.axis("equal")

    plt.show()

def plot_change_scatter_1(election1, election2, party, level="volisca"):
    # =========================
    # TUKAJ NALOŽI PODATKE
    # =========================

    df1 = pd.read_csv(f"volitve_{election1}/{level}.csv", on_bad_lines='skip', lineterminator='\n')
    df2 = pd.read_csv(f"volitve_{election2}/{level}.csv", on_bad_lines='skip', lineterminator='\n')

    before = get_data_1(df1, party).dropna()
    after = get_data_1(df2, party).dropna()

    print(before.head())
    print(before.head())

    df = before.merge(
        after,
        on=["Volilni_Okraj", "ID_Volisca"],
        how="inner",
        suffixes=("_before", "_after")
    ).fillna(0)

    print(df.head())

    x = df[f"{dodaj_odstotek(party)}_before"]
    y = df[f"{dodaj_odstotek(party)}_after"]

    plt.figure(figsize=(8, 8))

    plt.scatter(x, y, s=1, alpha=0.7)

    # diagonala brez spremembe
    mn = min(x.min(), y.min())
    mx = max(x.max(), y.max())

    plt.plot([mn, mx], [mn, mx], linestyle=":")

    plt.xlabel("Podpora prej (%)")
    plt.ylabel("Podpora zdaj (%)")

    plt.title(f"Sprememba podpore po okrajih - {party}")

    plt.axis("equal")

    plt.show()


# =========================
# IZVRŠLJIVA KODA
# =========================


# plot_change_histogram(
#     "2022_dz",
#     "2026_dz",
#     "LEVICA",
#     "volisca"
# )

# plot_change_scatter(
#     "2022_dz",
#     "2026_dz",
#     "LEVICA",
#     "volisca"
# )

plot_party_shift(
    "2022_dz",
    "2026_dz",
    "SVOBODA",
    "DEMOKRATI",
    False,
    "volisca"
)

# def create_csvs_from_odts():
#     for volitve in ("2018_dz", "2019_e", "2022_dz", "2022_p", "2024_e", "2025_r", "2026_dz"):
#         for level in ("okraji", "volisca"):
#             print(f"{volitve} - {level}")
#             sheet_to_csv(volitve, shname=level)
# create_csvs_from_odts()

# sheet_to_csv("2026_dz", shname="volisca")