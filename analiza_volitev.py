import json
import itertools
import csv
from decimal import Decimal

def prikaz():
    with open('volilne_enote.json') as f:
        d=json.load(f)

        print(type(d['features'][0]['geometry']['coordinates'][0][0]))
        print(len(d['features'][0]['geometry']['coordinates'][0][0]))

def skrajsaj(stevilka):

    with open('dvomeje_1.json', 'r') as d:
        dvomeje = json.load(d)
        print(dvomeje)

    with open('tromeje.json', 'r') as t:
        tromeje = json.load(t)
        print(tromeje)

    with open('volilne_enote.json') as f:
        d=json.load(f)
        for enota in d['features']:
            # print(len(enota['geometry']['coordinates'][0][0]))
            koordinate = enota['geometry']['coordinates'][0]
            enota['geometry']['coordinates'][0] = [i for i in koordinate if i[0] * 100 % stevilka == 0 or i in tromeje or i in dvomeje]
            najdi_bbox(enota)
            print(len(enota['geometry']['coordinates'][0]))
        with open(f"volilne_enote_{stevilka}.json", 'w') as o:
            json.dump(d, o, indent=1)

def najdi_bbox(enota):
    koordinate = enota['geometry']['coordinates'][0]
    minx, miny, maxx, maxy = koordinate[0][0], koordinate[0][1], koordinate[0][0], koordinate[0][1]
    for koordinata in koordinate:
        minx = min(minx, koordinata[0])
        maxx = max(maxx, koordinata[0])
        miny = min(miny, koordinata[1])
        maxy = max(maxy, koordinata[1])
    enota['bbox'] = [minx, miny, maxx, maxy]

def najdi_tromeje():
    with open('volilne_enote.json') as f:
        d=json.load(f)
        enote = d['features']
        st_enot = len(enote)

        list_of_lists_of_tuples = [[tuple(koordinata) for koordinata in enota['geometry']['coordinates'][0]] for enota in enote]

        list_of_sets_of_tuples = [frozenset(lolot) for lolot in list_of_lists_of_tuples]

        set_of_sets_of_tuples = set(list_of_sets_of_tuples)

        list_of_triborders = []

        for thruple in itertools.combinations(set_of_sets_of_tuples, 3):
            tromeja = thruple[0].intersection(thruple[1], thruple[2])
            if(len(tromeja) > 0):
                list_of_triborders.append(list(tromeja)[0])

        print(list_of_triborders)

        with open('tromeje.json', 'w') as t:
            json.dump(list_of_triborders, t)

def najdi_dvomeje(stevilka):
    with open(f'volilne_enote_{stevilka}.json') as f:
        d=json.load(f)
        enote = d['features']
        st_enot = len(enote)

        dvomeje = set({})

        for i in range(st_enot):
            print()
            for j in range(i+1, st_enot, 1):
                dvomeje_tmp = set({})
                enota1 = enote[i]['geometry']['coordinates'][0]
                enota2 = enote[j]['geometry']['coordinates'][0]

                enota1.append(enota1[0])
                enota2.append(enota2[0])

                prej_bool = True
                tmp_bool = True
                prej_koor = enota1[0]
                tmp_koor = enota1[0]

                for l, e in enumerate(enota1):
                    tmp_lst = [k for k in enota2 if (k[0] == e[0] and k[1] == e[1])]

                    tmp_bool = len(tmp_lst) > 0
                    if tmp_bool:
                        tmp_koor = tmp_lst[0]

                    if((tmp_bool != prej_bool) and (l != 0)):
                        if tmp_bool:
                            print(f"{e[0]} {e[1]}")
                            dvomeje_tmp.add(tuple(e))
                        elif prej_bool:
                            print(f"{prej_koor[0]} {prej_koor[1]}")
                            dvomeje_tmp.add(tuple(prej_koor))

                    prej_bool = tmp_bool
                    if prej_bool:
                        prej_koor = tmp_lst[0]

                print(f"{int(enote[i]['properties']['SIFRA']/1000)} "
                      f"{int(enote[j]['properties']['SIFRA']/1000)} "
                      f"{dvomeje_tmp} "
                      f"\n")

                dvomeje.update(dvomeje_tmp)

        print(dvomeje)

        with open(f'dvomeje_{stevilka}.json', 'w') as d:
            json.dump(list(dvomeje), d)

        # Writing to a CSV file
        with open(f'dvomeje_{stevilka}.csv', 'w', newline='') as d:
            writer = csv.writer(d)
            writer.writerow(['X', 'Y'])     # Write header
            writer.writerows(dvomeje)      #

def find_first_coordinates(stevilka):
    with open(f'volilne_enote_{stevilka}.json') as f:
        d=json.load(f)
        enote = d['features']
        zacetki = set({})
        for enota in enote:
            zacetki.add(tuple(enota['geometry']['coordinates'][0][0]))

    # Writing to a CSV file
    with open(f'zacetki_{stevilka}.csv', 'w', newline='') as d:
        writer = csv.writer(d)
        writer.writerow(['X', 'Y'])  # Write header
        writer.writerows(zacetki)  #

def find_bbox_area(okraj):
    return round(((okraj["bbox"][2] - okraj["bbox"][0])/10000) * ((okraj["bbox"][3] - okraj["bbox"][1])/10000), 2)


def find_povrsina_okrajev(stevilka, enota):
    with open(f'volilni_okraji_{stevilka}.json') as f:
        d=json.load(f)
        okraji = d['features']
        print(len(okraji))
        for okraj in okraji:
            if okraj["properties"]["SESTAVLJENA_SIFRA"] in range(enota, enota+12, 1):
                povrsina = find_bbox_area(okraj)
                print(f"{povrsina} - {okraj["properties"]["SESTAVLJENA_SIFRA"]} - {okraj["properties"]["NAZIV"]} - {okraj["bbox"]}")


def maribor_okvir(stevilka):
    with open(f'volilni_okraji_{stevilka}.json') as f:
        d=json.load(f)
        okraji = d['features']
        okvir = [545166.52, 152302.79, 550705.39, 157003.13]
        for okraj in okraji:
            if okraj["properties"]["SESTAVLJENA_SIFRA"] in range(7008, 7012, 1):
                if okvir[0] < okraj["bbox"][0]:
                    okvir[0] = okraj["bbox"][0]
                if okvir[1] < okraj["bbox"][1]:
                    okvir[1] = okraj["bbox"][1]
                if okvir[2] > okraj["bbox"][2]:
                    okvir[2] = okraj["bbox"][2]
                if okvir[3] > okraj["bbox"][3]:
                    okvir[3] = okraj["bbox"][3]

        with open(f'okvir_mb_{stevilka}.json', 'w') as f1:
            json.dump(okvir, f1)


def ljubljana_okvir(stevilka):
    with open(f'volilni_okraji_{stevilka}.json') as f:
        d=json.load(f)
        okraji = d['features']
        okvir = [461346.09, 102232.45, 465221.33, 105560.47]
        for okraj in okraji:
            if okraj["properties"]["SESTAVLJENA_SIFRA"] in range(3004, 3011, 1) or okraj["properties"]["SESTAVLJENA_SIFRA"] in range(4005, 4009, 1):
                if okvir[0] < okraj["bbox"][0]:
                    okvir[0] = okraj["bbox"][0]
                if okvir[1] < okraj["bbox"][1]:
                    okvir[1] = okraj["bbox"][1]
                if okvir[2] > okraj["bbox"][2]:
                    okvir[2] = okraj["bbox"][2]
                if okvir[3] > okraj["bbox"][3]:
                    okvir[3] = okraj["bbox"][3]

        with open(f'okvir_lj_{stevilka}.json', 'w') as f1:
            json.dump(okvir, f1)


def postojna_okvir(stevilka):
    with open(f'volilni_okraji_{stevilka}.json') as f:
        d=json.load(f)
        okraji = d['features']
        okvir = [387754.25, 34813.02, 399347.53, 45387.43]
        for okraj in okraji:
            if okraj["properties"]["SESTAVLJENA_SIFRA"] in range(2002, 2005, 1):
                if okvir[0] < okraj["bbox"][0]:
                    okvir[0] = okraj["bbox"][0]
                if okvir[1] < okraj["bbox"][1]:
                    okvir[1] = okraj["bbox"][1]
                if okvir[2] > okraj["bbox"][2]:
                    okvir[2] = okraj["bbox"][2]
                if okvir[3] > okraj["bbox"][3]:
                    okvir[3] = okraj["bbox"][3]

        with open(f'okvir_po_{stevilka}.json', 'w') as f1:
            json.dump(okvir, f1)


def move_maribor(stevilka):

    with open(f'okvir_mb_{stevilka}.json') as f:
        okvir=json.load(f)

    with open(f'volilni_okraji_{stevilka}.json') as f:
        d=json.load(f)
        okraji = d['features']
        for okraj in okraji:
            sifra = okraj["properties"]["SESTAVLJENA_SIFRA"]
            if sifra in range(7008, 7012, 1):
                povrsina = round(((okraj["bbox"][2] - okraj["bbox"][0])/10000) * ((okraj["bbox"][3] - okraj["bbox"][1])/10000), 2)
                for koordinata in okraj["geometry"]["coordinates"][0]:
                    koordinata[0] = 3*(koordinata[0]-okvir[0]) + okvir[0]*1.05
                    koordinata[1] = 3*(koordinata[1]-okvir[1]) + okvir[1]*0.65

        with open(f'volilni_okraji_mb_{stevilka}.json', 'w') as f1:
            json.dump(d, f1)


def move_ljubljana(stevilka):

    with open(f'okvir_lj_{stevilka}.json') as f:
        okvir=json.load(f)

    with (open(f'volilni_okraji_{stevilka}.json') as f):
        d=json.load(f)
        okraji = d['features']
        for okraj in okraji:
            sifra = okraj["properties"]["SESTAVLJENA_SIFRA"]
            if sifra in range(3004, 3006, 1) or sifra in range(3007, 3011, 1) or sifra in range(4006, 4010, 1):
                for koordinata in okraj["geometry"]["coordinates"][0]:
                    koordinata[0] = 3*(koordinata[0]-okvir[0]) + okvir[0]*1.25
                    koordinata[1] = 3*(koordinata[1]-okvir[1]) + okvir[1]*0.60

        with open(f'volilni_okraji_lj_{stevilka}.json', 'w') as f1:
            json.dump(d, f1)


def move_mb_lj(stevilka):

    with open(f'okvir_lj_{stevilka}.json') as f:
        okvir_lj=json.load(f)
    with open(f'okvir_mb_{stevilka}.json') as f:
        okvir_mb=json.load(f)
    with open(f'okvir_po_{stevilka}.json') as f:
        okvir_po=json.load(f)

    with (open(f'volilni_okraji_{stevilka}.json') as f):
        d=json.load(f)
        okraji = d['features']
        for okraj in okraji:
            sifra = okraj["properties"]["SESTAVLJENA_SIFRA"]
            if sifra in range(3004, 3006, 1) or sifra in range(3007, 3011, 1) or sifra in range(4006, 4010, 1):
                prestavi_okraj(okraj, okvir_lj, 2.5, 1.22, 0.57)
            elif sifra in range(7008, 7012, 1):
                prestavi_okraj(okraj, okvir_mb, 3, 1.05, 0.65)
            elif sifra in range(2002, 2005, 1):
                prestavi_okraj(okraj, okvir_po, 2, 0.96, 1.25)

        with open(f'volilni_okraji_mb_lj_po_{stevilka}.json', 'w') as f1:
            json.dump(d, f1)
            print("fertik")


def prestavi_okraj(okraj, okvir_lj, raztezek, premik_x, premik_y):
    for koordinata in okraj["geometry"]["coordinates"][0]:
        koordinata[0] = raztezek*(koordinata[0]-okvir_lj[0]) + okvir_lj[0]*premik_x
        koordinata[1] = raztezek*(koordinata[1]-okvir_lj[1]) + okvir_lj[1]*premik_y
    okraj["bbox"][0] = raztezek*(okraj["bbox"][0]-okvir_lj[0]) + okvir_lj[0]*premik_x
    okraj["bbox"][2] = raztezek*(okraj["bbox"][2]-okvir_lj[0]) + okvir_lj[0]*premik_x
    okraj["bbox"][1] = raztezek*(okraj["bbox"][1]-okvir_lj[1]) + okvir_lj[1]*premik_y
    okraj["bbox"][3] = raztezek*(okraj["bbox"][3]-okvir_lj[1]) + okvir_lj[1]*premik_y



def prestej_vecdelne_okraje(stevilka):

    with (open(f'volilni_okraji_{stevilka}.json') as f):
        d=json.load(f)
        okraji = d['features']
        for okraj in okraji:
            if len(okraj["geometry"]["coordinates"]) > 1:
                print(okraj["properties"]["NAZIV"])


def najdi_sredisca_okrajev(stevilka):
    sredisca = []

    with (open(f'volilni_okraji_mb_lj_po_{stevilka}.json') as f):
        d=json.load(f)
        okraji = d['features']
        for okraj in okraji:
            sredisce = (okraj["properties"]["NAZIV"], (okraj["bbox"][0] + okraj["bbox"][2])/2, (okraj["bbox"][1] + okraj["bbox"][3])/2)
            sredisca.append(sredisce)

        with open(f'sredisca_{stevilka}.json', 'w') as f1:
            json.dump(sredisca, f1)

        # Writing to a CSV file
        with open(f'sredisca_{stevilka}.csv', 'w', newline='') as d:
            writer = csv.writer(d)
            writer.writerow(['IME', 'X', 'Y'])     # Write header
            writer.writerows(sredisca)      #




# najdi_dvomeje(1)
# skrajsaj(1000)
# najdi_tromeje()
# maribor_okvir(1)
# postojna_okvir(1)
# move_maribor(1)
# find_povrsina_okrajev(1, 2000)
# ljubljana_okvir(1)
# move_ljubljana(1)
# move_mb_lj(1)
# najdi_sredisca_okrajev(1)