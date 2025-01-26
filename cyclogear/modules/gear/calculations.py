import math
import numpy as np
from modules.common.calculations.tolerance_calc import normal_in_tolerance, normal_in_tolerance_set
SAMPLES = 500

# TODO: skoro w R_eke sie odejmuje g to jak potem sie bierze pod uwagę odchyłke tego to chyba też sie powinno odjąć. Dowiedzieć sie, narazie zmieniłem na -.
# druga sprawa to czy eta wszędzie może mieć dodaną odchyłke> bo tylko w dwoch miejscach ma dodane...
# TODO: zapytac o 21 strone o obliczanie liczby obciazonych rolek

def get_lam_min(z: int) -> float:
    return (z - 1) / (2 * z + 1)

def get_ro_min(z: int, lam: float, g: float) -> float:
    return math.sqrt(g**2 * (z + 2)**3 / (27 * z * (z+1)**2 * (1 - lam**2)))

def gear_error_check(z, lam, g, e, Rg, ro):
    # Warunek nie podcinania zębów koła podstawowego
    min_e1 = g * ((z + 2) / (3 * math.sqrt(3) * (z + 1))) * math.sqrt((z + 2) / z) * math.sqrt(lam**2 / (1 - lam**2))
    kat_mu = math.acos((lam**2 * (2 * z + 1) - (z - 1)) / (lam * (z + 2))) / z
    min_e2 = (lam * g * (1 - lam * (z + 2) * math.cos(z * kat_mu) + (lam**2 * (z + 1)))) / ((z + 1) * (1 - (2 * lam * math.cos(z * kat_mu)) + lam**2)**(3/2))
    if e < min_e1 or e < min_e2:
        return {"podcinanie zebow": True}
    
    # Warunek sąsiedztwa rolek
    min_e3 = g * lam / ((z + 1) * math.sin(math.pi / (z + 1)))
    max_g = ro * (z+1) * math.sin(math.pi / (z+1))
    if e <= min_e3 or g >= max_g:
        return {"sasiedztwo rolek": True}
    
    # Dodatkowe warunki dla zazębienia epicykloidalnego:
    # promień rozmieszczenia rolek
    Rg_min = math.sqrt((g**2 * (z + 2)**3) / (27 * z) + e**2 * (z + 1)**2)
    if Rg < Rg_min:
        return {"Rg male": True}
    
    # promień rolki, chwilowo wycofany, zdaje się że daje fałszywe pozytywy, nie ma w excelu go
    # g_max = math.sqrt(27 * z * (Rg_min**2 - e**2 * (z + 1)**2) / (z + 2)**3)
    # if g > g_max:
    #     return {"g duze": True}
    
    # mimośród, nie ma w excelu
    # e_max = math.sqrt((27 * z * Rg_min**2 - g**2 * (z + 2)**3) / (27 * z * (z + 1)**2))
    # if e > e_max:
    #     return {"e duze": True}


def calculate_gear(gear_data, material_data, out_data, tolerancje=None):
    liczba_rolek = gear_data["z"] + 1
    liczba_obciazonych_rolek = int(gear_data["z"]/2 if gear_data["z"]%2 == 0 else (gear_data["z"]+1)/2)
    F_max = 1000 * 4 * (out_data["M_wyj"] / gear_data["K"]) / (gear_data["Rw1"] * liczba_rolek)

    Fx = [0] * liczba_obciazonych_rolek
    Fy = [0] * liczba_obciazonych_rolek
    sily = [0] * liczba_obciazonych_rolek
    naciski = [0] * liczba_obciazonych_rolek
    straty = [0] * liczba_obciazonych_rolek
    R_eke = [0] * liczba_obciazonych_rolek
    al_si = [0] * liczba_obciazonych_rolek

    for i in range(liczba_obciazonych_rolek):
        #TODO: w wykresach jest takie coś co zeruje wyniki, ale żeby to w raporcie, i ich sumy miały sens, to zeruję je tutaj.
        # może to być problem dla obliczeń z luzami.
        # if i==0 or i+1 > liczba_obciazonych_rolek:
        #     continue

        #SILY
        al_ki = 2 * math.pi * i / liczba_rolek
        al_si[i] = (math.pi / 2) - abs(math.atan(gear_data["Rb2"] * math.sin(al_ki) / ((gear_data["Rw1"] + gear_data["e"]) - gear_data["Rb2"] * math.cos(al_ki))))
        hi = gear_data["Rw1"] * math.cos(al_si[i])
        Fx[i] = F_max * hi * math.cos(al_si[i]) / gear_data["Rw1"]
        Fy[i] = F_max * hi * math.sin(al_si[i]) / gear_data["Rw1"]
        sily[i] = math.sqrt(Fx[i]**2 + Fy[i]**2)

        R_eke[i] = (gear_data["ro"] * liczba_rolek * ((1 - (2 * gear_data["lam"] * math.cos(gear_data["z"] * al_ki)) + (gear_data["lam"]**2))**1.5)/(1-(gear_data["lam"]*(gear_data["z"]+2)*math.cos(gear_data["z"]*al_ki)) + (gear_data["lam"]**2 * liczba_rolek))) - gear_data["g"]
        naciski[i] = math.sqrt((sily[i] * abs(gear_data["g"] + R_eke[i])) / ((gear_data["g"] * abs(R_eke[i]) * material_data["b_wheel"]) * (((1 - material_data["wheel"]["v"]**2) / material_data["wheel"]["E"]) + ((1 - material_data["roller"]["v"]**2) / material_data["roller"]["E"])) * math.pi))

        AIC = math.sqrt(gear_data["Rw2"]**2 + (gear_data["Ra2"] + gear_data["g"])**2 - 2 * gear_data["Rw2"] * (gear_data["Ra2"] + gear_data["g"]) * math.cos(al_ki)) - gear_data["g"]
        straty[i] = (math.pi * out_data["n_wej"] / 30) * (gear_data["e"] / gear_data["Rw1"]) * ((AIC / gear_data["g"]+1) * material_data["f_kr"] + (AIC/gear_data["g"]) * material_data["f_ro"]) * sily[i]


    common_return_values = {
        "F_max": round(F_max, 1),
        "F_wzx": round(sum(Fx), 1),
        "F_wzy": round(sum(Fy), 1),
        "F_wz": round(math.sqrt(sum(Fx)**2 + sum(Fy)**2), 1),
    }

    if tolerancje is not None and type(list(tolerancje.values())[0]) == tuple:
        results = calculate_gear_tolerances(gear_data, material_data, out_data, sily, R_eke, al_si, tolerancje)
        common_return_values.update(results)
        return common_return_values
    elif tolerancje is not None:
        results = calculate_gear_clearance(gear_data, material_data, out_data, sily, R_eke, al_si, tolerancje)
        common_return_values.update(results)
        return common_return_values

    common_return_values.update({
        "p_max": round(max(naciski), 2),
        # TODO: to jest obejscie zeby sie dopasowac do schematu od tulei (punkty + gladki wykres). Potem dodac tutaj tez liczenie gladkie
        "sily": (sily, sily),
        "naciski": (naciski, naciski),
        "straty": (straty, straty),
        "N_Ck-ri": round(sum(straty), 3),
        "luzy": ([0] * liczba_obciazonych_rolek, [0] * liczba_obciazonych_rolek)
    })
    return common_return_values


def calculate_gear_clearance(gear_data, material_data, out_data, sily_0, R_eke_0, al_si_0, tolerancje):
    liczba_rolek = gear_data["z"] + 1
    liczba_obciazonych_rolek = int(gear_data["z"]/2 if gear_data["z"]%2 == 0 else (gear_data["z"]+1)/2)

    luzy = [0 for _ in range(liczba_obciazonych_rolek)]
    ac = [0 for _ in range(liczba_obciazonych_rolek)]
    etas = [i*2*math.pi / liczba_rolek for i in range(liczba_obciazonych_rolek)]

    for i, eta in enumerate(etas):
        x_ze = (gear_data["Rb"]+gear_data["ro"])*math.sin(eta)-gear_data["e"]*math.sin(((gear_data["Rb"]+gear_data["ro"])/gear_data["ro"])*eta)-(gear_data["g"]+tolerancje["T_ze"])*((math.sin(eta)-gear_data["lam"]*math.sin((gear_data["z"]+1)*eta))/((1-2*gear_data["lam"]*math.cos(gear_data["z"]*eta)+gear_data["lam"]**2)**0.5))
        y_ze = (gear_data["Rb"]+gear_data["ro"])*math.cos(eta)-gear_data["e"]*math.cos(((gear_data["Rb"]+gear_data["ro"])/gear_data["ro"])*eta)-(gear_data["g"]+tolerancje["T_ze"])*((math.cos(eta)-gear_data["lam"]*math.cos((gear_data["z"]+1)*eta))/((1-2*gear_data["lam"]*math.cos(gear_data["z"]*eta)+gear_data["lam"]**2)**0.5))
        x_ozri = (gear_data["Rb2"]+tolerancje["T_Rg"])*math.sin(eta+tolerancje["T_fi_Ri"])
        y_ozri = (gear_data["Rb2"]+tolerancje["T_Rg"])*math.cos(eta+tolerancje["T_fi_Ri"])-(gear_data["e"]+tolerancje["T_e"])
        luzy[i] = ((x_ozri-x_ze)**2 + (y_ozri-y_ze)**2)**0.5 - gear_data["g"]
        ac[i] = (x_ozri**2 + (y_ozri-gear_data["Rw1"])**2)**0.5 - (gear_data["g"]+tolerancje["T_Rr"])

    c = (4.9*10**-3)*((max(sily_0)/material_data["b_wheel"])*(((1-material_data["wheel"]["v"]**2)/material_data["wheel"]["E"])+((1-material_data["roller"]["v"]**2)/material_data["roller"]["E"]))*((max(R_eke_0)*gear_data["g"])/(max(R_eke_0)+gear_data["g"])))**0.5
    delta_max = (max(sily_0)/(math.pi*material_data["b_wheel"]))*((((1-material_data["wheel"]["v"]**2)/material_data["wheel"]["E"])*((1/3)+math.log(4*max(R_eke_0)/c)))+(((1-material_data["roller"]["v"]**2)/material_data["roller"]["E"])*((1/3)+math.log(4*gear_data["g"]/c))))

    delta = [delta_max * math.sin(math.pi/2 - alfa) for alfa in al_si_0]
    h_list = [gear_data["Rw1"] * math.cos(alfa) for alfa in al_si_0]
    beta_obr = [luz / h for luz, h in zip(luzy, h_list)]
    h_t_beta_obr_min = [h * min(beta_obr[1:-1]) for h in h_list]

    temp = [(delta[i]-(luzy[i]-h_t_beta_obr_min[i]))*h_list[i] for i in range(liczba_obciazonych_rolek)]
    temp_sum = sum([el if el > 0 else 0 for el in temp])

    sily_temp = [1000*(out_data["M_wyj"] / gear_data["K"])*(delta[i]-(luzy[i]-h_t_beta_obr_min[i]))/temp_sum for i in range(liczba_obciazonych_rolek)]
    sily = [sila_temp if sila_temp > 0 else 0 for sila_temp in sily_temp]

    R_eke = [rek - tolerancje["T_ze"] for rek in R_eke_0]
    naciski = [((sily[i]*abs(gear_data["g"]+R_eke[i]))/((gear_data["g"]*abs(R_eke[i])*material_data["b_wheel"])*(((1-material_data["wheel"]["v"]**2)/material_data["wheel"]["E"])+((1-material_data["roller"]["v"]**2)/material_data["roller"]["E"]))*math.pi))**0.5 for i in range(liczba_obciazonych_rolek)]

    omg_wej = math.pi*out_data["n_wej"]/30
    straty = [omg_wej * (gear_data["e"]/gear_data["Rw1"])*sily[i]*(((ac[i]/(gear_data["g"]+tolerancje["T_Rr"])+1)*material_data["f_kr"]+(ac[i]/(gear_data["g"]+tolerancje["T_Rr"]))*material_data["f_ro"])) for i in range(liczba_obciazonych_rolek)]

    return {
        "p_max": round(max(naciski), 2),
        # TODO: to jest obejscie zeby sie dopasowac do schematu od tulei (punkty + gladki wykres). Potem dodac tutaj tez liczenie gladkie
        "sily": (sily, sily),
        "naciski": (naciski, naciski),
        "straty": (straty, straty),
        "N_Ck-ri": round(sum(straty), 3),
        "luzy": (luzy, luzy),
    }


def calculate_gear_tolerances(gear_data, material_data, out_data, sily_0, R_eke_0, al_si_0, tolerancje):
    # TODO: T_ze problem bo tez jest dodawana odchylka do R_eke. Moze zamiast liczyć w głównej i podawać tutaj jako R_eke_0 i dodawac odchylke, to policzyc juz z ta odchylka od razu jak licze R_eke_0. Ale najlatwiej po prostu dodam tutaj tą idealną wartość (bo we wzorze R_eke jest odejmowana (g)) i dodam
    # TODO: wyciagnac stale elementy wzorow poza petle
    liczba_rolek = gear_data["z"] + 1
    liczba_obciazonych_rolek = int(gear_data["z"]/2 if gear_data["z"]%2 == 0 else (gear_data["z"]+1)/2)
    etas = np.array([i * 2 * math.pi / liczba_rolek for i in range(liczba_obciazonych_rolek)])
    odch_zarys = normal_in_tolerance(gear_data["g"], tolerancje["T_ze"], sample_amount=SAMPLES)
    odch_rolka = normal_in_tolerance(gear_data["g"], tolerancje["T_Rr"], sample_amount=SAMPLES)
    odch_rb2 = normal_in_tolerance(gear_data["Rb2"], tolerancje["T_Rg"], sample_amount=SAMPLES)
    odch_eta = normal_in_tolerance_set(etas, tolerancje["T_fi_Ri"], sample_amount=SAMPLES)
    odch_e = normal_in_tolerance(gear_data["e"], tolerancje["T_e"], sample_amount=SAMPLES)

    omg_wej = math.pi*out_data["n_wej"]/30
    c = (4.9*10**-3)*((max(sily_0)/material_data["b_wheel"])*(((1-material_data["wheel"]["v"]**2)/material_data["wheel"]["E"])+((1-material_data["roller"]["v"]**2)/material_data["roller"]["E"]))*((max(R_eke_0)*gear_data["g"])/(max(R_eke_0)+gear_data["g"])))**0.5
    delta_max = (max(sily_0)/(math.pi*material_data["b_wheel"]))*((((1-material_data["wheel"]["v"]**2)/material_data["wheel"]["E"])*((1/3)+math.log(4*max(R_eke_0)/c)))+(((1-material_data["roller"]["v"]**2)/material_data["roller"]["E"])*((1/3)+math.log(4*gear_data["g"]/c))))
    delta = np.array([delta_max * math.sin(math.pi/2 - alfa) for alfa in al_si_0])
    h_list = np.array([gear_data["Rw1"] * math.cos(al_si) for al_si in al_si_0])

    luzy = np.zeros(SAMPLES*liczba_obciazonych_rolek)
    ac = np.zeros(SAMPLES*liczba_obciazonych_rolek)
    beta_obr = np.zeros(SAMPLES*liczba_obciazonych_rolek)
    for i in range(SAMPLES*liczba_obciazonych_rolek):
        x_ze = (gear_data["Rb"]+gear_data["ro"])*math.sin(etas[i%liczba_obciazonych_rolek])-gear_data["e"]*math.sin(((gear_data["Rb"]+gear_data["ro"])/gear_data["ro"])*etas[i%liczba_obciazonych_rolek])-odch_zarys[i//liczba_obciazonych_rolek]*((math.sin(etas[i%liczba_obciazonych_rolek])-gear_data["lam"]*math.sin((gear_data["z"]+1)*etas[i%liczba_obciazonych_rolek]))/((1-2*gear_data["lam"]*math.cos(gear_data["z"]*etas[i%liczba_obciazonych_rolek])+gear_data["lam"]**2)**0.5))
        y_ze = (gear_data["Rb"]+gear_data["ro"])*math.cos(etas[i%liczba_obciazonych_rolek])-gear_data["e"]*math.cos(((gear_data["Rb"]+gear_data["ro"])/gear_data["ro"])*etas[i%liczba_obciazonych_rolek])-odch_zarys[i//liczba_obciazonych_rolek]*((math.cos(etas[i%liczba_obciazonych_rolek])-gear_data["lam"]*math.cos((gear_data["z"]+1)*etas[i%liczba_obciazonych_rolek]))/((1-2*gear_data["lam"]*math.cos(gear_data["z"]*etas[i%liczba_obciazonych_rolek])+gear_data["lam"]**2)**0.5))
        x_ozri = odch_rb2[i//liczba_obciazonych_rolek]*math.sin(odch_eta[i])
        y_ozri = odch_rb2[i//liczba_obciazonych_rolek]*math.cos(odch_eta[i])-(odch_e[i//liczba_obciazonych_rolek])
        luzy[i] = ((((x_ozri-x_ze)**2)+((y_ozri-y_ze)**2))**0.5)-(gear_data["g"])
        ac[i] = (x_ozri**2+(y_ozri-gear_data["Rw1"])**2)**0.5-(odch_rolka[i//liczba_obciazonych_rolek])
        beta_obr[i] = luzy[i] / h_list[i%liczba_obciazonych_rolek]

    h_t_beta_obr_min = np.array([h_list[i%liczba_obciazonych_rolek] * min(beta_obr[(i//liczba_obciazonych_rolek)*liczba_obciazonych_rolek+1:((i//liczba_obciazonych_rolek)+1)*liczba_obciazonych_rolek-1]) for i in range(SAMPLES*liczba_obciazonych_rolek)])

    temp = [(delta[i%liczba_obciazonych_rolek]-(luzy[i]-h_t_beta_obr_min[i]))*h_list[i%liczba_obciazonych_rolek] for i in range(SAMPLES*liczba_obciazonych_rolek)]
    temp_sum = sum([el if el > 0 else 0 for el in temp])

    sily = np.zeros(SAMPLES*liczba_obciazonych_rolek)
    naciski = np.zeros(SAMPLES*liczba_obciazonych_rolek)
    straty = np.zeros(SAMPLES*liczba_obciazonych_rolek)
    for i in range(SAMPLES*liczba_obciazonych_rolek):
        sila_temp = 1000*(out_data["M_wyj"] / gear_data["K"])*(delta[i%liczba_obciazonych_rolek]-(luzy[i]-h_t_beta_obr_min[i]))/temp_sum
        sily[i] = sila_temp if sila_temp > 0 else 0
        R_eke = R_eke_0[i%liczba_obciazonych_rolek] + gear_data["g"] - odch_zarys[i//liczba_obciazonych_rolek]
        naciski[i] = ((sily[i]*abs(gear_data["g"]+R_eke))/((gear_data["g"]*abs(R_eke)*material_data["b_wheel"])*(((1-material_data["wheel"]["v"]**2)/material_data["wheel"]["E"])+((1-material_data["roller"]["v"]**2)/material_data["roller"]["E"]))*math.pi))**0.5
        straty[i] = omg_wej * (gear_data["e"]/gear_data["Rw1"])*sily[i]*(((ac[i]/odch_rolka[i//liczba_obciazonych_rolek]+1)*material_data["f_kr"]+(ac[i]/odch_rolka[i//liczba_obciazonych_rolek])*material_data["f_ro"]))
    
    results = {
        "sily": sily,
        "naciski": naciski,
        "straty": straty,
        "luzy": luzy,
    }
    graph_values = {
        "sily": [np.zeros(liczba_obciazonych_rolek), np.zeros(liczba_obciazonych_rolek), np.zeros(liczba_obciazonych_rolek)],
        "naciski": [np.zeros(liczba_obciazonych_rolek), np.zeros(liczba_obciazonych_rolek), np.zeros(liczba_obciazonych_rolek)],
        "straty": [np.zeros(liczba_obciazonych_rolek), np.zeros(liczba_obciazonych_rolek), np.zeros(liczba_obciazonych_rolek)],
        "luzy": [np.zeros(liczba_obciazonych_rolek), np.zeros(liczba_obciazonych_rolek), np.zeros(liczba_obciazonych_rolek)],
    }

    for key in results:
        for i in range(liczba_obciazonych_rolek):
            graph_values[key][1][i] = results[key][i]
    
    for key in results:
        for i in range(1, SAMPLES*liczba_obciazonych_rolek):
            graph_values[key][0][i%liczba_obciazonych_rolek] += results[key][i]
            if results[key][i] < graph_values[key][1][i%liczba_obciazonych_rolek]:
                graph_values[key][1][i%liczba_obciazonych_rolek] = results[key][i]
            if results[key][i] > graph_values[key][2][i%liczba_obciazonych_rolek]:
                graph_values[key][2][i%liczba_obciazonych_rolek] = results[key][i]

    for key in results:
        np.divide(graph_values[key][0], SAMPLES, out=graph_values[key][0])
    
    graph_values.update({
        "p_max": max(graph_values["naciski"][2]),
        "N_Ck-ri": sum(graph_values["straty"][0]),
    })
    return graph_values
