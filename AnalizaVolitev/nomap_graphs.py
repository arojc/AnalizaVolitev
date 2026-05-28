import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import math

default_col = "Odstotek udeležbe"
vo = "Volilni_Okraj"

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

def sheet_to_csv(file):
    df1 = pd.read_excel(f"{file}.ods", engine="odf", sheet_name="Podatki")
    df1.to_csv(f"{file}.csv")

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


def plot_party_shift(election1, election2, party1, party2):

    df1 = pd.read_csv(election1, on_bad_lines='skip', lineterminator='\n')
    df2 = pd.read_csv(election2, on_bad_lines='skip', lineterminator='\n')

    polling_places = df1[vo].dropna()

    p1_old = get_data(df1, party1).dropna()
    p1_new = get_data(df2, party1).dropna()
    p2_old = get_data(df1, party2).dropna()
    p2_new = get_data(df2, party2).dropna()

    xs = (p1_new.iloc[:, 1] - p1_old.iloc[:, 1]).to_numpy()
    ys = (p2_new.iloc[:, 1] - p2_old.iloc[:, 1]).to_numpy()

    xs = np.array(xs)
    ys = np.array(ys)

    plt.figure(figsize=(8, 8))

    plt.scatter(xs, ys, s=10, alpha=0.6)

    plt.axhline(0)
    plt.axvline(0)

    reg_x, reg_y = reg_fun(xs, ys)
    plt.plot(reg_x, reg_y, color="red")
    reg_x, reg_y = reg_fun(xs, ys, 4)
    plt.plot(reg_x, reg_y, color="orange")

    plt.xlabel(f"Sprememba podpore: {party1}")
    plt.ylabel(f"Sprememba podpore: {party2}")

    plt.title("Sprememba podpore po okrajih")

    plt.show()




def plot_change_histogram(election1, election2, party):
    # =========================
    # TUKAJ NALOŽI PODATKE
    # =========================

    df1 = pd.read_csv(election1, on_bad_lines='skip', lineterminator='\n')
    df2 = pd.read_csv(election2, on_bad_lines='skip', lineterminator='\n')

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



def plot_change_scatter(election1, election2, party):
    # =========================
    # TUKAJ NALOŽI PODATKE
    # =========================

    df1 = pd.read_csv(election1, on_bad_lines='skip', lineterminator='\n')
    df2 = pd.read_csv(election2, on_bad_lines='skip', lineterminator='\n')

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

    x = df[f"{dodaj_odstotek(party)}_before"]
    y = df[f"{dodaj_odstotek(party)}_after"]

    # =========================
    # GRAF
    # =========================

    plt.figure(figsize=(8, 8))

    plt.scatter(x, y, s=20, alpha=0.7)

    # diagonala brez spremembe
    mn = min(x.min(), y.min())
    mx = max(x.max(), y.max())

    plt.plot([mn, mx], [mn, mx], linestyle=":")

    reg_x, reg_y = reg_fun(x, y)
    plt.plot(reg_x, reg_y, color="red")
    reg_x, reg_y = reg_fun(x, y, 1)
    plt.plot(reg_x, reg_y, color="orange")

    plt.xlabel("Podpora prej (%)")
    plt.ylabel("Podpora zdaj (%)")

    plt.title(f"Sprememba podpore po okrajih - {party}")

    plt.axis("equal")

    plt.show()



# =========================
# IZVRŠLJIVA KODA
# =========================


# plot_change_scatter(
#     "volitve_2022/izidi_2022.csv",
#     "volitve_2026/izidi_2026.csv",
#     "SVOBODA"
# )

plot_party_shift(
    "volitve_2022/izidi_2022.csv",
    "volitve_2026/izidi_2026.csv",
    "SDS",
    "DEMOKRATI"
)

# sheet_to_csv("volitve_2022/izidi_2022")
# df = pd.read_csv("volitve_2026/izidi_2026.csv")
# print(df.head(5))