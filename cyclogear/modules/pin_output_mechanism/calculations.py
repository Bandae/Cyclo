import math
import numpy as np
from modules.common.calculations.tolerance_calc import normal_in_tolerance, normal_in_tolerance_set
# różnica z excelem w odchyłkach jest dlatego, że licze wszystkie sworznie, a w excelu są 6na10, te przenoszące normalnie obciążenie. To ma znaczenie w obliczeniach z odchyłką przy braniu pod uwagę sum wartości z kilku sworzni. To psuje obliczenia gładkie całkiem.
# odchyłki częściowo poprawione, ale połowa sworzni nie jest obliczana, mimo że przenosi obciążenie w niektóych przypadkach.
SAMPLES = 1000
POINTS_SMOOTH_GRAPH = 40

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
    f_list = [F_max * math.sin(fi_kj) if F_max * math.sin(fi_kj) > 0 else 0 for fi_kj in lista_fi_kj]
    for _ in range(n_sworzni - len(lista_fi_kj)):
        f_list.append(0)
    return f_list

def oblicz_naciski(sily, d_otw, d_tul, b_kola, v_k, v_t, E_k, E_t, tolerancje):
    R_otw = d_otw / 2 if tolerancje is None else (d_otw + tolerancje["T_o"]) / 2
    R_tul = d_tul / 2 if tolerancje is None else (d_tul + tolerancje["T_t"]) / 2

    stala = (R_otw - R_tul) / (b_kola * math.pi * R_tul * R_otw * (((1 - v_k**2) / E_k) + ((1 - v_t**2) / E_t)))
    return [math.sqrt(F_j * stala) for F_j in sily]

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
    sily = [sila if sila > 0 else 0 for sila in sily_temp]
    
    for _ in range(n_sworzni - len(lista_fi_kj)):
        sily.append(0)
        luzy.append(0)
    return {"sily": sily, "beta": min_beta_obr, "suma": suma, "luzy": luzy}

def oblicz_straty(omg_0, sily, e, R_w1, d_tul, d_sw, tolerancje, f_kt, f_ts):
    odch_e = e if tolerancje is None else e + tolerancje["T_e"]
    odch_R_sw = d_sw / 2 if tolerancje is None else d_sw / 2 + tolerancje["T_s"]
    odch_R_tul = d_tul / 2 if tolerancje is None else d_tul / 2 + tolerancje["T_t"]

    stala = omg_0 * (odch_e / R_w1) * ((R_w1 + odch_e) / (odch_R_tul - odch_R_sw)) * (f_kt + f_ts)
    return [F_j * stala for F_j in sily]

def obliczenia_mech_wyjsciowy(dane, dane_zew, material_data, tolerancje, kat):
    M_k = dane_zew["M_wyj"] / dane_zew["K"]
    E, k_g = material_data["pin_mat"]["E"], material_data["pin_mat"]["Re"] / material_data["pin_safety_coef"]
    E_k, v_k = material_data["wheel_mat"]["E"], material_data["wheel_mat"]["v"]
    E_t, v_t = material_data["sleeve_mat"]["E"], material_data["sleeve_mat"]["v"]
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
    if tolerancje is not None and type(list(tolerancje.values())[0]) == tuple:
        mode = "tolerances"
    elif tolerancje is not None:
        mode = "deviations"

    F_max = 1000 * ((4 * M_k) / (R_wt * n_sworzni)) # N
    # lista_fi_kj = lista_fi_sworzni(n_sworzni, kat, mode="active_only")
    lista_fi_kj = lista_fi_sworzni(n_sworzni, kat)
    sily = oblicz_sily(F_max, lista_fi_kj, n_sworzni)
    M_gmax = oblicz_Mgmax(podparcie, K, F_max, b_kola, e1, e2)
    d_smax = oblicz_d_sworzen(M_gmax, k_g)

    d_sw_wybrane = d_sw if d_sw is not None and d_sw > d_smax else d_smax

    # d_sw_wybrane = d_smax if d_sw <= d_smax else d_sw
    d_tul_obl = round(d_sw_wybrane * dane["wsp_k"], 2)
    d_tul_wybrane = d_tul if d_tul is not None and d_tul > d_tul_obl else d_tul_obl
    # d_tul_wybrane = d_tul_obl if d_tul <= d_tul_obl else d_tul
    d_otw_obl = round(d_tul_wybrane + (2 * e), 2)

    if mode == "tolerances":
        results = obliczenia_z_tolerancjami(n_sworzni, M_k, sily, d_otw_obl, d_tul, d_sw, e, R_wt, F_max, b_kola, E_k, v_k, E_t, v_t, E, e1, e2, dane_zew["R_w1"], omg_0, f_kt, f_ts, podparcie, K, tolerancje)
        
        R_otw = (d_otw_obl + tolerancje["T_o"][1]) / 2
        R_tul = (d_tul_wybrane + tolerancje["T_t"][0]) / 2
        stala = (R_otw - R_tul) / (b_kola * math.pi * R_tul * R_otw * (((1 - v_k**2) / E_k) + ((1 - v_t**2) / E_t)))
        p_max =  round(math.sqrt(F_max * stala), 2)

        return_values = {
            "d_s_obl": d_smax,
            "d_t_obl": d_tul_obl,
            "d_o_obl": d_otw_obl,
            "F_max": round(F_max, 1),
            "p_max": p_max,
        }
        return_values.update(results)
        return return_values
    
    p_max = oblicz_naciski((F_max,), d_otw_obl, d_tul_wybrane, b_kola, v_k, v_t, E_k, E_t, tolerancje)[0]
    strzalki = oblicz_fs(podparcie, K, sily, E, b_kola, d_sw_wybrane, e1, e2)
    lista_fi_gladka = lista_fi_sworzni(POINTS_SMOOTH_GRAPH, kat)
    sily_gladkie = oblicz_sily(F_max, lista_fi_gladka, POINTS_SMOOTH_GRAPH)
    strzalki_gladkie = oblicz_fs(podparcie, K, sily_gladkie, E, b_kola, d_sw_wybrane, e1, e2)
    luzy = [[0] * n_sworzni, [0] * POINTS_SMOOTH_GRAPH]
    if mode == "deviations":
        wyniki_point = oblicz_sily_odchylka(M_k, lista_fi_kj, F_max, b_kola, R_wt, e, d_tul, d_otw_obl, strzalki, tolerancje, E_k, v_k, E_t, v_t, n_sworzni)
        sily, luzy[0] =  wyniki_point["sily"], wyniki_point["luzy"]
        wyniki_gladkie = oblicz_sily_odchylka(M_k, lista_fi_gladka, F_max, b_kola, R_wt, e, d_tul, d_otw_obl, strzalki_gladkie, tolerancje, E_k, v_k, E_t, v_t, n_sworzni, wyniki_point["beta"], wyniki_point["suma"])
        sily_gladkie, luzy[1] = wyniki_gladkie["sily"], wyniki_gladkie["luzy"]
    naciski = oblicz_naciski(sily, d_otw_obl, d_tul_wybrane, b_kola, v_k, v_t, E_k, E_t, tolerancje)
    naciski_gladkie = oblicz_naciski(sily_gladkie, d_otw_obl, d_tul_wybrane, b_kola, v_k, v_t, E_k, E_t, tolerancje)
    straty = oblicz_straty(omg_0, sily, e, dane_zew["R_w1"], d_tul_wybrane, d_sw_wybrane, tolerancje, f_kt, f_ts)
    straty_gladkie = oblicz_straty(omg_0, sily_gladkie, e, dane_zew["R_w1"], d_tul_wybrane, d_sw_wybrane, tolerancje, f_kt, f_ts)

    return {
        "d_s_obl": d_smax,
        "d_t_obl": d_tul_obl,
        "d_o_obl": d_otw_obl,
        "F_max": round(F_max, 1),
        "p_max": round(p_max, 2),
        "sily": (sily, sily_gladkie),
        "naciski": (naciski, naciski_gladkie),
        "straty": (straty, straty_gladkie),
        "luzy": luzy,
    }

def obliczenia_z_tolerancjami(n_sworzni, M_k, sily_0, d_otw, d_tul, d_sw, mimosrod, R_wt, F_max, b_kola, E_k, v_k, E_t, v_t, E_sw, e1, e2, R_w1, omg_0, f_kt, f_ts, podparcie, K, tolerancje):
    lista_fi = np.array([(2 * math.pi * (i - 1)) / n_sworzni for i in range(1, n_sworzni + 1)])
    odch_fik = normal_in_tolerance_set(lista_fi, tolerancje["T_fi_k"], sample_amount=SAMPLES)
    odch_fit = normal_in_tolerance_set(lista_fi, tolerancje["T_fi_t"], sample_amount=SAMPLES)
    odch_d_otw = normal_in_tolerance(d_otw, tolerancje["T_o"], sample_amount=n_sworzni*SAMPLES)
    odch_d_tz = normal_in_tolerance(d_tul, tolerancje["T_t"], sample_amount=n_sworzni*SAMPLES)
    odch_d_sw = normal_in_tolerance(d_sw, tolerancje["T_s"], sample_amount=n_sworzni*SAMPLES)
    odch_e = normal_in_tolerance(mimosrod, tolerancje["T_e"], sample_amount=SAMPLES)
    odch_R_wk = normal_in_tolerance(R_wt, tolerancje["T_Rk"], sample_amount=SAMPLES)
    odch_R_wt = normal_in_tolerance(R_wt, tolerancje["T_Rt"], sample_amount=SAMPLES)

    del_max = oblicz_przemieszczenie_tul_otw(F_max, b_kola, d_otw, d_tul, E_k, v_k, E_t, v_t)
    delty = np.array([del_max * math.sin(fi_k) for fi_k in odch_fik])

    luzy = np.zeros(SAMPLES*n_sworzni)
    for i in range(SAMPLES*n_sworzni):
        y_otj = odch_R_wt[i//n_sworzni] * math.cos(odch_fit[i])
        y_oktj = odch_R_wk[i//n_sworzni] * math.cos(odch_fik[i]) - odch_e[i//n_sworzni]
        luzy[i] = (y_oktj - odch_d_tz[i]/2) - (y_otj - odch_d_otw[i]/2)
    
    # TODO: czy zaokrąglenie tu potrzebne?
    list_h_j = np.array([odch_R_wt[i//n_sworzni] * math.sin(odch_fik[i]) for i in range(SAMPLES*n_sworzni)])

    min_beta_obroty = np.zeros(SAMPLES)
    for i in range(SAMPLES):
        min_beta_obroty[i] = min([luz / h_j for luz, h_j in zip(luzy[i*n_sworzni:(i+1)*n_sworzni], list_h_j[i*n_sworzni:(i+1)*n_sworzni]) if h_j > 0])

    strzalki = oblicz_fs(podparcie, K, sily_0, E_sw, b_kola, d_sw, e1, e2)

    sily = np.zeros(SAMPLES*n_sworzni)
    suma = np.zeros(SAMPLES)
    for i in range(SAMPLES*n_sworzni):
        temp = (strzalki[i%n_sworzni] + delty[i] - (luzy[i] - list_h_j[i] * min_beta_obroty[i//n_sworzni])) * list_h_j[i]
        suma[i//n_sworzni] += temp if temp > 0 else 0
    
    for i in range(SAMPLES*n_sworzni):
        sila = 1000 * M_k * (strzalki[i%n_sworzni] + delty[i] - (luzy[i] - list_h_j[i] * min_beta_obroty[i//n_sworzni]))
        sily[i] = sila / suma[i//n_sworzni] if sila > 0 and suma[i//n_sworzni] > 0 else 0

    naciski = np.zeros(SAMPLES*n_sworzni)
    straty = np.zeros(SAMPLES*n_sworzni)
    stala_naciski = (b_kola * math.pi * (((1 - v_k**2) / E_k) + ((1 - v_t**2) / E_t)))
    # TODO: moze tutaj uzyc odch_e a nie stalego
    stala_straty = omg_0 * (mimosrod / R_w1) * (R_w1 + mimosrod) * (f_kt + f_ts)
    for i in range(SAMPLES*n_sworzni):
        naciski[i] = math.sqrt(sily[i] * ((odch_d_otw[i]/2) - (odch_d_tz[i]/2)) / ((odch_d_otw[i]/2) * (odch_d_tz[i]/2) * stala_naciski))
        straty[i] = sily[i] * stala_straty / (odch_d_tz[i]/2 - odch_d_sw[i]/2)
    
    results = {
        "sily": sily,
        "naciski": naciski,
        "straty": straty,
        "luzy": luzy,
    }
    graph_values = {
        "sily": [np.zeros(n_sworzni), np.zeros(n_sworzni), np.zeros(n_sworzni)],
        "naciski": [np.zeros(n_sworzni), np.zeros(n_sworzni), np.zeros(n_sworzni)],
        "straty": [np.zeros(n_sworzni), np.zeros(n_sworzni), np.zeros(n_sworzni)],
        "luzy": [np.zeros(n_sworzni), np.zeros(n_sworzni), np.zeros(n_sworzni)],
    }

    for key in results:
        for i in range(n_sworzni):
            graph_values[key][1][i] = results[key][i]
    
    for key in results:
        for i in range(1, SAMPLES*n_sworzni):
            graph_values[key][0][i%n_sworzni] += results[key][i]
            if results[key][i] < graph_values[key][1][i%n_sworzni]:
                graph_values[key][1][i%n_sworzni] = results[key][i]
            if results[key][i] > graph_values[key][2][i%n_sworzni]:
                graph_values[key][2][i%n_sworzni] = results[key][i]

    for key in results:
        np.divide(graph_values[key][0], SAMPLES, out=graph_values[key][0])
    
    return graph_values
