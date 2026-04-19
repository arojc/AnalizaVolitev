import geopandas as gpd
import pandas as pd
import matplotlib.pyplot as plt

# =========================
# 1. NALOŽI PODATKE
# =========================

def draw_units(ax, color="white"):

    # narisi meje volilnih enot (čez)
    enote = gpd.read_file("volilne_enote.json")
    enote = enote.to_crs(epsg=4326)
    enote.boundary.plot(
        ax=ax,
        linewidth=1,
        edgecolor=color
    )

def draw_districts(ax, color="white"):

    # narisi meje volilnih enot (čez)
    okraji = gpd.read_file("volilni_okraji_mb_lj_po_1.json")
    okraji = okraji.to_crs(epsg=4326)
    okraji.boundary.plot(
        ax=ax,
        linewidth=0.2,
        edgecolor=color
    )

def posrafiraj(ax, stranka="Svoboda"):

    okraji = gpd.read_file("volilni_okraji_mb_lj_po_1.json")
    try:
        mandati = pd.read_excel("mandati.ods", sheet_name=stranka)
    except:
        return

    df = pd.read_excel("izidi26.ods", engine="odf")

    okraji_id = "NAZIV"
    rez_id = "Volilni Okraj"

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

    # ax.set_title("Volilni rezultati po okrajih (%)")
    # ax.axis("off")

    # plt.show()

def draw_map(podatek_za_prikaz="Odstotek udeležbe", trim_range=False, posrafiram=False):

    # GeoJSON (pričakujemo D96/TM)
    okraji = gpd.read_file("volilni_okraji_mb_lj_po_1.json")

    # Rezultati (ODS)
    df = pd.read_excel("izidi26.ods", engine="odf")

    # =========================
    # 2. PREVERI IMENA STOLPCEV
    # =========================
    print("OKRAJI columns:", okraji.columns)
    print("ODS columns:", df.columns)

    # >>> TU PRILAGODI IMENA <<<
    okraji_id = "NAZIV"
    rez_id = "Volilni Okraj"
    value_col = podatek_za_prikaz   # npr. % glasov

    gdf = okraji.merge(df, left_on=okraji_id, right_on=rez_id)

    print(gdf[[okraji_id, value_col]].head())
    print(gdf[value_col].describe())

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
        posrafiraj(ax, podatek_za_prikaz.split('-')[0])

    draw_units(ax)

    ax.set_title("Volilni rezultati po okrajih (%)")
    ax.axis("off")

    plt.show()

def draw_dots():

    # GeoJSON s točkami
    points = gpd.read_file("tocke.geojson")
    mandati = pd.read_excel("mandati.ods", sheet_name="SDS")

    # ODS rezultati
    df = pd.read_excel("izidi26.ods", engine="odf")

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




draw_map("NSI-%", True, False)
# draw_dots()
# posrafiraj()





