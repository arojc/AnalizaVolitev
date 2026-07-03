import geopandas as gpd
import pandas as pd
import matplotlib.pyplot as plt

# =========================
# 1. NALOŽI PODATKE
# =========================

path_okraji = "zemljevidi/volilni_okraji_mb_lj_po_1.json"
path_okraji_1 = "zemljevidi/volilni_okraji.json"
path_enote = "zemljevidi/volilne_enote.json"
stolpec_okraj = "Volilni_Okraj"

def draw_units(ax, color="white"):

    # narisi meje volilnih enot (čez)
    enote = gpd.read_file(path_enote)
    enote = enote.to_crs(epsg=4326)
    enote.boundary.plot(
        ax=ax,
        linewidth=1,
        edgecolor=color
    )

def draw_districts(ax, color="white", povecaj=True):

    # narisi meje volilnih enot (čez)
    if povecaj:
        okraji = gpd.read_file(path_okraji)
    else:
        okraji = gpd.read_file(path_okraji_1)
    okraji = okraji.to_crs(epsg=4326)
    okraji.boundary.plot(
        ax=ax,
        linewidth=0.2,
        edgecolor=color
    )

def posrafiraj(ax, leto, stranka="Svoboda"):

    okraji = gpd.read_file(path_okraji)
    try:
        mandati = pd.read_excel(f"volitve_{leto}/mandati.ods", sheet_name=stranka)
    except :
        print()
        return

    df = pd.read_csv(f"volitve_{leto}/okraji.csv", on_bad_lines='skip', lineterminator='\n')

    okraji_id = "NAZIV"
    rez_id = stolpec_okraj

    gdf = okraji.merge(df, left_on=okraji_id, right_on=rez_id)
    gdf = gdf.merge(mandati, left_on=okraji_id, right_on="Okraj")

    gdf = gdf.to_crs(epsg=4326)

    gdf.plot(
        ax=ax,
        linewidth=1,
        edgecolor="black",
        hatch="..",
        facecolor="none"
    )

def draw_map(leto, podatek_za_prikaz="Odstotek udeležbe", trim_range=False, posrafiram=False):

    okraji = gpd.read_file(path_okraji)

    df = pd.read_csv(f"volitve_{leto}/okraji.csv", on_bad_lines='skip', lineterminator='\n')

    # >>> TU PRILAGODI IMENA <<<
    okraji_id = "NAZIV"
    rez_id = stolpec_okraj
    value_col = podatek_za_prikaz   # npr. % glasov

    gdf = okraji.merge(df, left_on=okraji_id, right_on=rez_id)

    gdf = gdf.to_crs(epsg=4326)

    if trim_range:
        vmin=gdf[value_col].min()
        vmax=gdf[value_col].max()
    else:
        vmin=0
        vmax=1

    fig, ax = plt.subplots(figsize=(10, 10))

    # narisi okraje (barvani)
    gdf.plot(
        column=value_col,
        cmap="YlGn",
        linewidth=0.2,
        edgecolor="white",
        legend=True,
        vmin=vmin,
        vmax=vmax,
        ax=ax
    )

    if(posrafiram):
        posrafiraj(ax, leto, podatek_za_prikaz.split('-')[0])

    draw_units(ax)

    ax.set_title("Volilni rezultati po okrajih (%)")
    ax.axis("off")

    plt.show()

def draw_dots():

    # GeoJSON s točkami
    points = gpd.read_file("zemljevidi/tocke.geojson")
    mandati = pd.read_excel(f"volitve_2026/mandati_2026.ods", sheet_name="SDS")

    # ODS rezultati
    df = pd.read_excel("volitve_2026/izidi_2026.ods", engine="odf")

    # # >>> PRILAGODI <<<
    points_id = "name"  # ID v GeoJSON
    rez_id = "Volilni Okraj"  # ID v ODS
    value_col = "Odstotek udeležbe"  # vrednost (0–100)
    gdf = points.merge(df, left_on=points_id, right_on=rez_id)
    gdf = gdf.merge(mandati, left_on=points_id, right_on="Okraj")

    gdf = gdf.to_crs(epsg=4326)

    fig, ax = plt.subplots(figsize=(10, 10))

    gdf.plot(
        column=value_col,
        cmap="viridis",
        markersize=70,
        legend=True,
        vmin=0,
        vmax=1,
        ax=ax
    )

    ax.set_title("Rezultati po točkah (%)")
    ax.axis("off")

    draw_districts(ax)
    draw_units(ax)

    plt.show()


draw_map("2018_dz", "SD-%", True, True)
# draw_dots()
# posrafiraj()





