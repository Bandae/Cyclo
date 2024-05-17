import math
import numpy as np
from scipy.stats import truncnorm
# różnica z excelem w odchyłkach jest dlatego, że licze wszystkie sworznie, a w excelu są 6na10, te przenoszące normalnie obciążenie. To ma znaczenie w obliczeniach z odchyłką przy braniu pod uwagę sum wartości z kilku sworzni. To psuje obliczenia gładkie całkiem.
# odchyłki częściowo poprawione, ale połowa sworzni nie jest obliczana, mimo że przenosi obciążenie w niektóych przypadkach.
SAMPLES = 50

def lista_fi_sworzni(n_sworzni, kat, mode="standard"):
    def obl_fi_kj(i):
        return (2 * math.pi * (i - 1)) / n_sworzni
    
    n_sworzni_aktywne = n_sworzni
    if mode == "active_only":
        n_sworzni_aktywne = n_sworzni / 2
        if n_sworzni % 2:
            n_sworzni_aktywne = (n_sworzni+1) / 2
    
    return [obl_fi_kj(i) + kat * 0.01745 for i in range(1, int(n_sworzni_aktywne) + 1)]

def oblicz_fs(podparcie, K, sily_0, E, b_kola, d_sw, e1, e2):
    l_1 = b_kola / 2 + e1 # odleglosc do polowy kola pierwszego
    l_2 = b_kola + e1 # odleglosc do podparcia jesli jedno kolo cykloidalne
    l_k2 = b_kola * 1.5 + e1 + e2 # odleglosc do polowy kola drugiego
    l_k3 = b_kola * 2 + e1 * 2 + e2 # odleglosc do podparcia jesli dwa kola cykloidalne

    J = math.pi * d_sw**4 / 64 # moment bezwladnosci sworznia

    if podparcie == "jednostronnie utwierdzony" and K == 1:
        return [(F_j * l_1**3) / (3 * E * J) for F_j in sily_0]
    
    elif podparcie == "utwierdzony podpartyy" and K == 1:
        return [(F_j * l_1**2 * (l_2 - l_1)) / (2 * E * J) for F_j in sily_0]

    elif podparcie == "obustronnie utwierdzony" and K == 1:
        return [(2 * F_j * l_1**3 * (l_2 - l_1)**2) / (3 * E * J * (l_2 + 2 * l_1)**2) for F_j in sily_0]

    elif podparcie == "jednostronnie utwierdzony" and K == 2:
        return [(F_j * l_k2**3) / (3 * E * J) for F_j in sily_0]

    elif podparcie == "utwierdzony podparty" and K == 2:
        return [(F_j * l_k2**2 * (l_k3 - l_k2)) / (2 * E * J) for F_j in sily_0]

    elif podparcie == "obustronnie utwierdzony" and K == 2:
        return [(2 * F_j * l_1**3 * (l_k3 - l_1)**2) / (3 * E * J * (l_k3 + 2 * l_1)**2) for F_j in sily_0]

def oblicz_Mgmax(podparcie, K, F_max, b_kola, e1, e2):
    '''
    Oblicza max. moment gnący ze wszystkich działających na sworznie [Nm]
    '''
    l_1 = b_kola / 2 + e1 # odleglosc do polowy kola pierwszego
    l_2 = b_kola + e1 # odleglosc do podparcia jesli jedno kolo cykloidalne
    l_k2 = b_kola * 1.5 + e1 + e2 # odleglosc do polowy kola drugiego
    l_k3 = b_kola * 2 + e1 * 2 + e2 # odleglosc do podparcia jesli dwa kola cykloidalne

    if podparcie == "jednostronnie utwierdzony" and K == 1:
        return abs(F_max * l_1 / 1000)

    elif podparcie == "utwierdzony podparty" and K == 1:
        M_u = F_max * (l_1 / (2 * l_2**2)) * (l_1**2 - 3 * l_1 * l_2 + 2 * l_2**2) / 1000
        return abs(M_u)

    elif podparcie == "obustronnie utwierdzony" and K == 1:
        M_uA = F_max * (((l_2 - l_1) * l_1**2) / l_2**2) / 1000
        M_uB = F_max * (((l_2 - l_1)**2 * l_1) / l_2**2) / 1000
        return max(abs(M_uA), abs(M_uB))
 
    elif podparcie == "jednostronnie utwierdzony" and K == 2:
        M_uI = F_max * l_1 / 1000
        M_uII = F_max * l_k2 / 1000
        return max(abs(M_uI), abs(M_uII))

    elif podparcie == "utwierdzony podparty" and K == 2:
        M_uI = F_max * (l_1 / (2 * l_k3**2)) * (l_1**2 - 3 * l_1 * l_k3 + 2 * l_k3**2) / 1000
        M_uII = F_max * (l_k2 / (2 * l_k3**2)) * (l_k2**2 - 3 * l_k2 * l_k3 + 2 * l_k3**2) / 1000
        return max(abs(M_uI), abs(M_uII))

    elif podparcie == "obustronnie utwierdzony" and K == 2:
        M_uAI = F_max * (((l_k3 - l_1) * l_1**2) / l_k3**2) / 1000
        M_uAII = F_max * (((l_k3 - l_k2) * l_k2**2) / l_k3**2) / 1000
        M_uBI = F_max * (((l_k3 - l_1)**2 * l_1) / l_k3**2) / 1000
        M_uBII = F_max * (((l_k3 - l_k2)**2 * l_k2) / l_k3**2) / 1000
        return max(abs(M_uAI), abs(M_uAII), abs(M_uBI), abs(M_uBII))

def oblicz_d_sworzen(M_gmax, k_g):
    return round((32 * M_gmax / (math.pi * k_g * 10**6))**(1/3) * 1000, 2)

def oblicz_sily(F_max, lista_fi_kj, n_sworzni):
    f_list = [round(F_max * math.sin(fi_kj), 1) if F_max * math.sin(fi_kj) > 0 else 0 for fi_kj in lista_fi_kj]
    for _ in range(n_sworzni - len(lista_fi_kj)):
        f_list.append(0)
    return f_list

def oblicz_naciski(sily, d_otw, d_tul, b_kola, v_k, v_t, E_k, E_t, tolerancje):
    R_otw = d_otw / 2 if tolerancje is None else (d_otw + tolerancje["T_o"]) / 2
    R_tul = d_tul / 2 if tolerancje is None else (d_tul + tolerancje["T_t"]) / 2

    stala = (R_otw - R_tul) / (b_kola * math.pi * R_tul * R_otw * (((1 - v_k**2) / E_k) + ((1 - v_t**2) / E_t)))
    return [round(math.sqrt(F_j * stala), 2) for F_j in sily]

def oblicz_luzy_odchylka(R_wt, mimosrod, d_tul, d_otw, lista_fi_kj, tolerancje):
    odch_R_otwj = (d_otw/2) + tolerancje["T_o"]
    odch_R_tzj = (d_tul/2) + tolerancje["T_t"]
    odch_R_wk = R_wt + tolerancje["T_Rk"]
    odch_R_wt = R_wt + tolerancje["T_Rt"]
    odch_e = mimosrod + tolerancje["T_e"]

    def oblicz_luz(fi_kj):
        y_otj = odch_R_wt * math.cos(fi_kj + tolerancje["T_fi_t"])
        y_oktj = odch_R_wk * math.cos(fi_kj + tolerancje["T_fi_k"]) - odch_e
        return (y_oktj - odch_R_tzj) - (y_otj - odch_R_otwj)

    return [oblicz_luz(fi_kj) for fi_kj in lista_fi_kj]

def oblicz_przemieszczenie_tul_otw(F_max, b_kola, d_otw, d_tul, E_k, v_k, E_t, v_t):
    R_otw, R_tul = (d_otw / 2), (d_tul / 2)
    c = (4.9 * 10**-3) * math.sqrt((F_max / b_kola) * (((1 - v_k**2) / E_k) + ((1 - v_t**2) / E_t)) * (R_otw * R_tul / (R_otw - R_tul)))
    return (F_max / (math.pi * b_kola)) * (((1 - v_k**2) / E_k) * ((1 / 3) + math.log((4 * R_otw) / c))) + ((1 - v_t**2) / E_t) * ((1 / 3) + math.log((4 * R_tul) / c))

def oblicz_sily_odchylka(M_k, lista_fi_kj, F_max, b_kola, R_wt, mimosrod, d_tul, d_otw, strzalki, tolerancje, E_k, v_k, E_t, v_t, n_sworzni, min_beta=None, temp_sum=None):
    del_max = oblicz_przemieszczenie_tul_otw(F_max, b_kola, d_otw, d_tul, E_k, v_k, E_t, v_t)
    delty = [del_max * math.sin(fi) for fi in lista_fi_kj]
    luzy = oblicz_luzy_odchylka(R_wt, mimosrod, d_tul, d_otw, lista_fi_kj, tolerancje)

    list_h_j = [R_wt * math.sin(fi) for fi in lista_fi_kj]
    min_beta_obr = min([luz / h_j for luz, h_j in zip(luzy, list_h_j) if h_j > 0]) if min_beta is None else min_beta
    suma = temp_sum
    if temp_sum is None:
        temp = [(f_j + del_j - (luz_j - h_j * min_beta_obr)) * h_j for f_j, del_j, luz_j, h_j in zip(strzalki, delty, luzy, list_h_j)]
        suma = sum([temp_j if temp_j > 0 else 0 for temp_j in temp])
    sily_temp = [1000 * M_k * (f_j + del_j - (luz_j - h_j * min_beta_obr)) / suma for f_j, del_j, luz_j, h_j in zip(strzalki, delty, luzy, list_h_j)]
    sily = [round(sila, 1) if sila > 0 else 0 for sila in sily_temp]
    for _ in range(n_sworzni - len(lista_fi_kj)):
        sily.append(0)
    return sily, min_beta_obr, suma

def oblicz_straty(omg_0, sily, e, R_w1, d_tul, d_sw, tolerancje, f_kt, f_ts):
    odch_e = e if tolerancje is None else e + tolerancje["T_e"]
    odch_R_sw = d_sw / 2 if tolerancje is None else d_sw / 2 + tolerancje["T_s"]
    odch_R_tul = d_tul / 2 if tolerancje is None else d_tul / 2 + tolerancje["T_t"]

    stala = omg_0 * (odch_e / R_w1) * ((R_w1 + odch_e) / (odch_R_tul - odch_R_sw)) * (f_kt + f_ts)
    return [round(F_j * stala, 3) for F_j in sily]

def obliczenia_mech_wyjsciowy(dane, dane_zew, material_data, tolerancje, kat):
    M_k = dane_zew["M_wyj"] / dane_zew["K"]
    E, k_g = material_data["pin"]["E"], material_data["pin"]["Re"] / material_data["pin_sft_coef"]
    E_k, v_k = material_data["wheel"]["E"], material_data["wheel"]["v"]
    E_t, v_t = material_data["sleeve"]["E"], material_data["sleeve"]["v"]
    b_kola = dane_zew["B"]
    n_sworzni = dane["n"]
    R_wt = dane["R_wt"]
    e1, e2 = dane["e1"], dane["e2"]
    podparcie = dane["podparcie"]
    d_tul, d_sw = dane["d_tul"], dane["d_sw"]
    e, K = dane_zew["e"], dane_zew["K"]
    f_kt, f_ts = dane["f_kt"], dane["f_ts"]
    omg_0 = math.pi * dane_zew["n_wej"] / 30

    mode = "ideal"
    if tolerancje.get("tolerances") is not None and type(list(tolerancje["tolerances"].values())[0]) == list:
        mode = "tolerances"
    elif tolerancje.get("tolerances") is not None:
        mode = "deviations"

    F_max = 1000 * ((4 * M_k) / (R_wt * n_sworzni)) # N
    lista_fi_kj = lista_fi_sworzni(n_sworzni, kat, mode="active_only")
    sily = oblicz_sily(F_max, lista_fi_kj, n_sworzni)
    M_gmax = oblicz_Mgmax(podparcie, K, F_max, b_kola, e1, e2)
    d_smax = oblicz_d_sworzen(M_gmax, k_g)

    d_sw_wybrane = d_smax if d_sw <= d_smax or d_sw >= d_smax + 10 else d_sw
    d_tul_obl = round(d_sw_wybrane * dane["wsp_k"], 2)
    d_tul_wybrane = d_tul_obl if d_tul <= d_tul_obl or d_tul >= d_tul_obl + 10 else d_tul
    d_otw_obl = round(d_tul_wybrane + (2 * e), 2)

    if mode == "tolerances":
        results = oblicz_z_tolerancjami(n_sworzni, M_k, sily, d_otw_obl, d_tul, d_sw, e, R_wt, F_max, b_kola, E_k, v_k, E_t, v_t, E, e1, e2, dane_zew["R_w1"], omg_0, f_kt, f_ts, podparcie, K, tolerancje["tolerances"])
        
        R_otw = (d_otw_obl + tolerancje["tolerances"]["T_o"][1]) / 2
        R_tul = (d_tul_wybrane + tolerancje["tolerances"]["T_t"][0]) / 2
        stala = (R_otw - R_tul) / (b_kola * math.pi * R_tul * R_otw * (((1 - v_k**2) / E_k) + ((1 - v_t**2) / E_t)))
        p_max =  round(math.sqrt(F_max * stala), 2)

        return {
            "d_s_obl": d_smax,
            "d_t_obl": d_tul_obl,
            "d_o_obl": d_otw_obl,
            "F_max": round(F_max, 1),
            "p_max": p_max,
            "sily": results["sily"],
            "naciski": results["naciski"],
            "straty": results["straty"],
            "mode": mode,
        }
        

    p_max = oblicz_naciski((F_max,), d_otw_obl, d_tul_wybrane, b_kola, v_k, v_t, E_k, E_t, tolerancje["tolerances"])[0]
    strzalki = oblicz_fs(podparcie, K, sily, E, b_kola, d_sw, e1, e2)
    lista_fi_gladka = lista_fi_sworzni(40, kat)
    sily_gladkie = oblicz_sily(F_max, lista_fi_gladka, 40)
    strzalki_gladkie = oblicz_fs(podparcie, K, sily_gladkie, E, b_kola, d_sw, e1, e2)
    if mode == "deviations":
        sily, min_beta, temp_sum = oblicz_sily_odchylka(M_k, lista_fi_kj, F_max, b_kola, R_wt, e, d_tul, d_otw_obl, strzalki, tolerancje["tolerances"], E_k, v_k, E_t, v_t, n_sworzni)
        sily_gladkie = oblicz_sily_odchylka(M_k, lista_fi_gladka, F_max, b_kola, R_wt, e, d_tul, d_otw_obl, strzalki_gladkie, tolerancje["tolerances"], E_k, v_k, E_t, v_t, n_sworzni, min_beta, temp_sum)[0]
    naciski = oblicz_naciski(sily, d_otw_obl, d_tul_wybrane, b_kola, v_k, v_t, E_k, E_t, tolerancje["tolerances"])
    naciski_gladkie = oblicz_naciski(sily_gladkie, d_otw_obl, d_tul_wybrane, b_kola, v_k, v_t, E_k, E_t, tolerancje["tolerances"])
    straty = oblicz_straty(omg_0, sily, e, dane_zew["R_w1"], d_tul_wybrane, d_sw_wybrane, tolerancje["tolerances"], f_kt, f_ts)
    straty_gladkie = oblicz_straty(omg_0, sily_gladkie, e, dane_zew["R_w1"], d_tul_wybrane, d_sw_wybrane, tolerancje["tolerances"], f_kt, f_ts)

    return {
        "d_s_obl": d_smax,
        "d_t_obl": d_tul_obl,
        "d_o_obl": d_otw_obl,
        "F_max": round(F_max, 1),
        "p_max": p_max,
        "sily": (sily, sily_gladkie),
        "naciski": (naciski, naciski_gladkie),
        "straty": (straty, straty_gladkie),
        "mode": mode,
    }


def normal_in_tolerance(tolerances, main_value, sd=1, size=1):
    if tolerances[0] == 0 and tolerances[1] == 0:
        return np.array([main_value for _ in range(size)])
    tol_range = (tolerances[0]+main_value, tolerances[1]+main_value)
    mean = (tol_range[1] - tol_range[0]) / 2 + tol_range[0]
    return truncnorm((tol_range[0] - mean) / sd, (tol_range[1] - mean) / sd, loc=mean, scale=sd).rvs(size)


def normal_in_tolerance_set(tolerances, main_values, sd=1, size=1):
    if tolerances[0] == 0 and tolerances[1] == 0:
        return np.array([*main_values] * size)
    count_in_set = main_values.size
    mean = (tolerances[1] - tolerances[0]) / 2 + tolerances[0]
    deviations = truncnorm((tolerances[0] - mean) / sd, (tolerances[1] - mean) / sd, loc=mean, scale=sd).rvs(count_in_set*size)
    for i, value in enumerate(main_values):
        for j in range(size):
            deviations[i+j*count_in_set] += value
    return deviations


def jedno_obliczenie(n_sworzni, M_k, sily_0, d_otw, d_tul, d_sw, mimosrod, R_wt, F_max, b_kola, E_k, v_k, E_t, v_t, E_sw, e1, e2, R_w1, omg_0, f_kt, f_ts, podparcie, K, tolerancje):
    lista_fi = np.array([(2 * math.pi * (i - 1)) / n_sworzni for i in range(1, n_sworzni + 1)])
    odch_fik = normal_in_tolerance_set(tolerancje["T_fi_k"], lista_fi)
    odch_fit = normal_in_tolerance_set(tolerancje["T_fi_t"], lista_fi)
    odch_d_otw = normal_in_tolerance(tolerancje["T_o"], d_otw, size=n_sworzni)
    odch_d_tz = normal_in_tolerance(tolerancje["T_t"], d_tul, size=n_sworzni)
    odch_d_sw = normal_in_tolerance(tolerancje["T_s"], d_sw, size=n_sworzni)
    odch_e = normal_in_tolerance(tolerancje["T_e"], mimosrod)[0]
    odch_R_wk = normal_in_tolerance(tolerancje["T_Rk"], R_wt)[0]
    odch_R_wt = normal_in_tolerance(tolerancje["T_Rt"], R_wt)[0]

    del_max = oblicz_przemieszczenie_tul_otw(F_max, b_kola, d_otw, d_tul, E_k, v_k, E_t, v_t)
    delty = np.array([del_max * math.sin(fi_k) for fi_k in odch_fik])

    luzy = np.zeros(n_sworzni)
    for i in range(n_sworzni):
        y_otj = odch_R_wt * math.cos(odch_fit[i])
        y_oktj = odch_R_wk * math.cos(odch_fik[i]) - odch_e
        luzy[i] = (y_oktj - odch_d_tz[i]/2) - (y_otj - odch_d_otw[i]/2)
    
    list_h_j = np.array([round(odch_R_wt * math.sin(fi), 3) for fi in odch_fik])
    min_beta_obr = min([luz / h_j for luz, h_j in zip(luzy, list_h_j) if h_j > 0])

    strzalki = oblicz_fs(podparcie, K, sily_0, E_sw, b_kola, d_sw, e1, e2)
    temp = [(f_j + del_j - (luz_j - h_j * min_beta_obr)) * h_j for f_j, del_j, luz_j, h_j in zip(strzalki, delty, luzy, list_h_j)]
    suma = sum([temp_j if temp_j > 0 else 0 for temp_j in temp])
    sily_temp = [1000 * M_k * (f_j + del_j - (luz_j - h_j * min_beta_obr)) / suma for f_j, del_j, luz_j, h_j in zip(strzalki, delty, luzy, list_h_j)]
    sily = [round(sila, 1) if sila > 0 else 0 for sila in sily_temp]

    stala_naciski = (b_kola * math.pi * (((1 - v_k**2) / E_k) + ((1 - v_t**2) / E_t)))
    naciski = [round(math.sqrt(F_j * ((d_otw/2) - (d_tz/2)) / ((d_otw/2) * (d_tz/2) * stala_naciski)), 2) for F_j, d_tz, d_otw in zip(sily, odch_d_tz, odch_d_otw)]

    stala_straty = omg_0 * (odch_e / R_w1) * (R_w1 + odch_e) * (f_kt + f_ts)
    straty = [round(F_j * stala_straty / (d_tz/2 - d_sw/2), 3) for F_j, d_tz, d_sw in zip(sily, odch_d_tz, odch_d_sw)]

    return {
        "sily": sily,
        "naciski": naciski,
        "straty": straty,
    }


def oblicz_z_tolerancjami(n_sworzni, M_k, sily_0, d_otw, d_tul, d_sw, mimosrod, R_wt, F_max, b_kola, E_k, v_k, E_t, v_t, E_sw, e1, e2, R_w1, omg_0, f_kt, f_ts, podparcie, K, tolerancje):
    results = {
        "sily": [np.zeros(n_sworzni), np.zeros(n_sworzni), np.zeros(n_sworzni)],
        "naciski": [np.zeros(n_sworzni), np.zeros(n_sworzni), np.zeros(n_sworzni)],
        "straty": [np.zeros(n_sworzni), np.zeros(n_sworzni), np.zeros(n_sworzni)],
    }
    for i in range(SAMPLES):
        one_result = jedno_obliczenie(n_sworzni, M_k, sily_0, d_otw, d_tul, d_sw, mimosrod, R_wt, F_max, b_kola, E_k, v_k, E_t, v_t, E_sw, e1, e2, R_w1, omg_0, f_kt, f_ts, podparcie, K, tolerancje)
        if i==0:
            for element in one_result:
                for j in range(n_sworzni):
                    results[element][1][j] = one_result[element][j]
        for element in one_result:
            for j in range(n_sworzni):
                results[element][0][j] += one_result[element][j]
                if one_result[element][j] < results[element][1][j]:
                    results[element][1][j] = one_result[element][j]
                if one_result[element][j] > results[element][2][j]:
                    results[element][2][j] = one_result[element][j]

    for element in results:
        results[element][0] = np.divide(results[element][0], SAMPLES)
    
    return results
