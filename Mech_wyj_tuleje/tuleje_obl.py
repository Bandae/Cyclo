import math

# nie sprawdzilem wersji z jednym kolem momentow obliczen, ale podzielilem wszystkie przez 1000
# poczekac narazie z liczeniem luzow. Może to da rade statystką zrobić.

def lista_fi_sworzni(n_sworzni, kat):
    def obl_fi_kj(i):
        return (2 * math.pi * (i - 1)) / n_sworzni
    
    return [obl_fi_kj(i) + kat * 0.01745 for i in range(1, n_sworzni + 1)]

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

def oblicz_sily(F_max, lista_fi_kj):
    return [F_max * math.sin(fi_kj) if F_max * math.sin(fi_kj) > 0 else 0 for fi_kj in lista_fi_kj]

def oblicz_naciski(sily, d_otw, d_tul, b_kola, v_k, v_t, E_k, E_t, tolerancje):
    R_otw = d_otw / 2 if tolerancje is None else d_otw / 2 + tolerancje["T_o"]
    R_tul = d_tul / 2 if tolerancje is None else d_tul / 2 + tolerancje["T_t"]

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

def oblicz_sily_odchylka(M_k, lista_fi_kj, F_max, b_kola, R_wt, mimosrod, d_tul, d_otw, strzalki, tolerancje, E_k, v_k, E_t, v_t):
    del_max = oblicz_przemieszczenie_tul_otw(F_max, b_kola, d_otw, d_tul, E_k, v_k, E_t, v_t)
    delty = [del_max * math.sin(fi) for fi in lista_fi_kj]
    luzy = oblicz_luzy_odchylka(R_wt, mimosrod, d_tul, d_otw, lista_fi_kj, tolerancje)

    list_h_j = [R_wt * math.sin(fi) for fi in lista_fi_kj]
    min_beta_obr = min([luz / h_j for luz, h_j in zip(luzy, list_h_j) if h_j > 0])
    temp = [(f_j + del_j - (luz_j - h_j * min_beta_obr)) * h_j for f_j, del_j, luz_j, h_j in zip(strzalki, delty, luzy, list_h_j)]
    suma = sum([temp_j if temp_j > 0 else 0 for temp_j in temp])
    sily_temp = [1000 * M_k * (f_j + del_j - (luz_j - h_j * min_beta_obr)) / suma for f_j, del_j, luz_j, h_j in zip(strzalki, delty, luzy, list_h_j)]
    return [sila if sila > 0 else 0 for sila in sily_temp]

def oblicz_straty(omg_0, sily, e, R_w1, d_tul, d_sw, tolerancje, f_kt, f_ts):
    odch_e = e if tolerancje is None else e + tolerancje["T_e"]
    odch_R_sw = d_sw / 2 if tolerancje is None else d_sw / 2 + tolerancje["T_s"]
    odch_R_tul = d_tul / 2 if tolerancje is None else d_tul / 2 + tolerancje["T_t"]

    stala = omg_0 * (odch_e / R_w1) * ((R_w1 + odch_e) / (odch_R_tul - odch_R_sw)) * (f_kt + f_ts)
    return [F_j * stala for F_j in sily]

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
    lista_fi_kj = lista_fi_sworzni(n_sworzni, kat)
    lista_fi_gladka = lista_fi_sworzni(40, kat)
    sily_0 = oblicz_sily(F_max, lista_fi_kj)
    sily_0_gladkie = oblicz_sily(F_max, lista_fi_gladka)
    M_gmax = oblicz_Mgmax(podparcie, K, F_max, b_kola, e1, e2)
    d_smax = oblicz_d_sworzen(M_gmax, k_g)


    d_sw_wybrane = d_smax if d_sw <= d_smax or d_sw >= d_smax + 10 else d_sw
    d_tul_obl = round(d_sw_wybrane * dane["wsp_k"], 2)
    d_tul_wybrane = d_tul_obl if d_tul <= d_tul_obl or d_tul >= d_tul_obl + 10 else d_tul
    d_otw_obl = round(d_tul_wybrane + (2 * e), 2)

    strzalki = oblicz_fs(podparcie, K, sily_0, E, b_kola, d_sw, e1, e2)
    strzalki_gladkie = oblicz_fs(podparcie, K, sily_0_gladkie, E, b_kola, d_sw, e1, e2)
    sily = oblicz_sily_odchylka(M_k, lista_fi_kj, F_max, b_kola, R_wt, e, d_tul, d_otw_obl, strzalki, tolerancje["tolerances"], E_k, v_k, E_t, v_t) if mode == "deviations" else sily_0
    sily_gladkie = oblicz_sily_odchylka(M_k, lista_fi_gladka, F_max, b_kola, R_wt, e, d_tul, d_otw_obl, strzalki_gladkie, tolerancje["tolerances"], E_k, v_k, E_t, v_t) if mode == "deviations" else sily_0_gladkie
    p_max = oblicz_naciski((F_max,), d_otw_obl, d_tul_wybrane, b_kola, v_k, v_t, E_k, E_t, tolerancje["tolerances"])[0]
    naciski = oblicz_naciski(sily, d_otw_obl, d_tul_wybrane, b_kola, v_k, v_t, E_k, E_t, tolerancje["tolerances"])
    naciski_gladkie = oblicz_naciski(sily_gladkie, d_otw_obl, d_tul_wybrane, b_kola, v_k, v_t, E_k, E_t, tolerancje["tolerances"])
    straty = oblicz_straty(omg_0, sily, e, dane_zew["R_w1"], d_tul_wybrane, d_sw_wybrane, tolerancje["tolerances"], f_kt, f_ts)
    straty_gladkie = oblicz_straty(omg_0, sily_gladkie, e, dane_zew["R_w1"], d_tul_wybrane, d_sw_wybrane, tolerancje["tolerances"], f_kt, f_ts)

    return {
        "d_s_obl": d_smax,
        "d_t_obl": d_tul_obl,
        "d_o_obl": d_otw_obl,
        "F_max": round(F_max, 1),
        "p_max": round(p_max, 2),
        "sily": ([round(sila, 2) for sila in sily], [round(sila, 2) for sila in sily_gladkie]),
        "naciski": ([round(nacisk, 2) for nacisk in naciski], [round(nacisk, 2) for nacisk in naciski_gladkie]),
        "straty": ([round(strata, 3) for strata in straty], [round(strata, 2) for strata in straty_gladkie]),
    }

# def oblicz_luzy(n_sworzni, R_wk, mimosrod, d_tul, d_otw, tolerancje):
#     '''
#     Tolerancje:
#     T_o: promienia otworu
#     T_t: promienia zew tuleji
#     T_s: promienia zew tuleji
#     T_Rk: promienia rozmieszczenia otworów
#     T_Rt: promienia rozmieszczenia tuleji
#     T_fi_k: kątowego rozmieszczenia otworów w kole cykloidalnym
#     T_fi_t: kątowego rozmieszczenia tulei w elemencie wyjściowym
#     T_e: wykonania mimośrodu

#     Oblicza wszystkie możliwości przechodząc po polach tolerancji krokiem 0.001mm. Zwraca dla każdego otworu min i max wartosc
#     '''
#     def obl_fi_kj(i):
#         return (2 * math.pi * (i - 1)) / n_sworzni

#     tol_R_otwj = [(d_otw/2) + i for i in range(tolerancje["T_o"][0], tolerancje["T_o"][1] + 0.001, 0.001)]
#     tol_R_tzj = [(d_tul/2) + i for i in range(tolerancje["T_t"][0], tolerancje["T_t"][1] + 0.001, 0.001)]
#     tol_R_wk = [R_wk + i for i in range(tolerancje["T_Rk"][0], tolerancje["T_Rk"][1] + 0.001, 0.001)]
#     tol_R_wt = [R_wk + i for i in range(tolerancje["T_Rt"][0], tolerancje["T_Rt"][1] + 0.001, 0.001)]
#     pole_tol_fi_kj = range(tolerancje["T_fi_k"][0], tolerancje["T_fi_k"][1] + 0.001, 0.001)
#     pole_tol_fi_tj = range(tolerancje["T_fi_t"][0], tolerancje["T_fi_t"][1] + 0.001, 0.001)
#     tol_e = [mimosrod + i for i in range(tolerancje["T_e"][0], tolerancje["T_e"][1] + 0.001, 0.001)]

#     def oblicz_luz(fi_kj):
#         tol_fi_kj = [fi_kj + i for i in pole_tol_fi_kj]
#         tol_fi_tj = [fi_kj + i for i in pole_tol_fi_tj]
#         tol_y_okj = [round(R * math.cos(fi), 3) for R in tol_R_wk for fi in tol_fi_kj]
#         tol_y_otj = [round(R * math.cos(fi), 3) for R in tol_R_wt for fi in tol_fi_tj]
#         tol_y_oktj = [y_otj - e for y_otj in tol_y_otj for e in tol_e]
#         luz_el1 =  [abs(y_oktj - R_tzj) for y_oktj in tol_y_oktj for R_tzj in tol_R_tzj]
#         luz_el2 =  [abs(y_okj - R_otwj) for y_okj in tol_y_okj for R_otwj in tol_R_otwj]
#         luz = [lu_1 - lu_2 for lu_1 in luz_el1 for lu_2 in luz_el2]
#         return [min(luz), max(luz)]

#     luzy = [oblicz_luz(obl_fi_kj(ind)) for ind in range(1, n_sworzni + 1)]

# def oblicz_sily_z_luzami():
#     ...
