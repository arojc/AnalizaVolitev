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

def plot_party_shift(file1, file2, party1, party2):

    df1 = pd.read_excel(file1, engine="odf", sheet_name="Podatki")
    df2 = pd.read_excel(file2, engine="odf", sheet_name="Podatki")

    p1_old = get_data(df1, party1)
    p1_new = get_data(df2, party1)
    p2_old = get_data(df1, party2)
    p2_new = get_data(df2, party2)

    polling_places = df1[vo]

    xs = []
    ys = []

    print(len(polling_places))
    for v in polling_places:
        print(v)
        if not(isinstance(v, str)) and math.isnan(v):
            continue

        old1 = p1_old.query(f"{vo} == '{v}'").iloc[0, 1]
        new1 = p1_new.query(f"{vo} == '{v}'").iloc[0, 1]

        old2 = p2_old.query(f"{vo} == '{v}'").iloc[0, 1]
        new2 = p2_new.query(f"{vo} == '{v}'").iloc[0, 1]

        # sprememba
        xs.append(new1 - old1)
        ys.append(new2 - old2)

    xs = np.array(xs)
    ys = np.array(ys)

    # =========================
    # LINEARNA REGRESIJA
    # =========================

    slope, intercept = np.polyfit(xs, ys, 1)

    reg_x = np.linspace(xs.min(), xs.max(), 100)
    reg_y = slope * reg_x + intercept

    print(f"y = {slope:.3f}x + {intercept:.3f}")


    plt.figure(figsize=(8, 8))

    plt.scatter(xs, ys, s=10, alpha=0.6)

    plt.plot(reg_x, reg_y)

    plt.axhline(0)
    plt.axvline(0)

    plt.xlabel(f"Sprememba podpore: {party1}")
    plt.ylabel(f"Sprememba podpore: {party2}")

    plt.title("Sprememba podpore po voliščih")

    plt.show()

plot_party_shift(
    "volitve_2022/izidi_2022.ods",
    "volitve_2026/izidi_2026.ods",
    "POVEŽIMO",
    "DEMOKRATI"
)