import math

# Czy w przypadku dwóch kół, dwóch momentów wystarczy wziąć pod uwagę większy z nich i na jego podstawie policzyć d_smax?
# Czy M_u zawsze wieksze niz to srodkowe?
# Czy nie trzeba dawac - prze MuA MuB i innymi?
# Czy l_2 powinno byc e1 * 2 czy jedno tylko
# Czy jak są dwa koła to mam obie strzałki i momenty zapisywać i wykreślać, czy tylko większe z danej pary
# TODO: jednostki

def oblicz_fs(wariant_podparcia, F_j, E, b_kola, d_smax, e1, e2):
    l_1 = b_kola / 2 + e1 # odleglosc do polowy kola pierwszego
    l_2 = b_kola + e1 # odleglosc do podparcia jesli jedno kolo cykloidalne
    l_k2 = b_kola * 1.5 + e1 + e2 # odleglosc do polowy kola drugiego
    l_k3 = b_kola * 2 + e1 * 2 + e2 # odleglosc do podparcia jesli dwa kola cykloidalne

    J = (math.pi * (d_smax ** 4)) / 64 # moment bezwladnosci trzpien

    if wariant_podparcia == "jedno koło cykloidalne":
        return - (F_j * l_1**3) / (3 * E * J)
    
    elif wariant_podparcia == "jedno koło, jeden koniec zamocowany, luźne śruby":
        return (F_j * l_1**2 * (l_2 - l_1)) / (2 * E * J)

    elif wariant_podparcia == "jedno koło, jeden koniec zamocowany, ciasne śruby":
        return (2 * F_j * l_1**3 * (l_2 - l_1)**2) / (3 * E * J * (l_2 + 2 * l_1)**2)

    elif wariant_podparcia == "dwa koła":
        f_sI = - ((F_j/2) * l_1**3) / (3 * E * J)
        f_sII = - ((F_j/2) * l_k2**3) / (3 * E * J)
        return max(f_sI, f_sII)

    elif wariant_podparcia == "dwa koła, jeden koniec zamocowany, luźne śruby":
        f_sI = ((F_j/2) * l_1**2 * (l_k3 - l_1)) / (2 * E * J)
        f_sII = ((F_j/2) * l_k2**2 * (l_k3 - l_k2)) / (2 * E * J)
        return max(f_sI, f_sII)

    elif wariant_podparcia == "dwa koła jeden koniec zamocowany, ciasne śruby":
        f_sI = (2 * (F_j/2) * l_1**3 * (l_k3 - l_1)**2) / (3 * E * J * (l_k3 + 2 * l_1)**2)
        f_sII = (2 * (F_j/2) * l_k2**3 * (l_k3 - l_k2)**2) / (3 * E * J * (l_k3 + 2 * l_k2)**2)
        return max(f_sI, f_sII)

def oblicz_Mgmax(wariant_podparcia, F_j, b_kola, e1, e2):
    '''
    Oblicza Max moment gnący działający na sworzeń i strzałkę ugięcia
    wariant_podparcia:
    1 - jedno koło cykloidalne
    2 - jedno koło, jeden koniec zamocowany, luźne śruby
    3 - jedno koło, jeden koniec zamocowany, ciasne śruby
    4 - dwa koła
    5 - dwa koła, jeden koniec zamocowany, luźne śruby
    6 - dwa koła jeden koniec zamocowany, ciasne śruby
    '''
    l_1 = b_kola / 2 + e1 # odleglosc do polowy kola pierwszego
    l_2 = b_kola + e1 # odleglosc do podparcia jesli jedno kolo cykloidalne
    l_k2 = b_kola * 1.5 + e1 + e2 # odleglosc do polowy kola drugiego
    l_k3 = b_kola * 2 + e1 * 2 + e2 # odleglosc do podparcia jesli dwa kola cykloidalne

    if wariant_podparcia == "jedno koło cykloidalne":
        return F_j * l_1

    elif wariant_podparcia == "jedno koło, jeden koniec zamocowany, luźne śruby":
        M_u = F_j * (l_1 / (2 * l_2**2)) * (l_1**2 - 3 * l_1 * l_2 + 2 * l_2**2)
        R = F_j - (F_j * (l_1**2 / (2 * l_2**3)) * (3 * l_2 - l_1))
        M_gI = -M_u + R * l_1
        M_gII = -M_u + R * l_2 - F_j * (l_2 - l_1)
        return max(M_gI, M_gII, M_u)

    elif wariant_podparcia == "jedno koło, jeden koniec zamocowany, ciasne śruby":
        R_B = F_j * ((l_2 - l_1)**2 / l_2**3) * (l_2 + 2 * l_1)
        M_uA = F_j * (((l_2 - l_1) * l_1**2) / l_2**2)
        M_uB = F_j * (((l_2 - l_1)**2 * l_1) / l_2**2)
        M_g = -M_uB + R_B * l_1
        return max(M_uA, M_uB, M_g)
 
    elif wariant_podparcia == "dwa koła":
        M_gI = (F_j/2) * l_1
        M_gII = (F_j/2) * l_k2
        return max(M_gI, M_gII)

    elif wariant_podparcia == "dwa koła, jeden koniec zamocowany, luźne śruby":
        M_uI = (F_j/2) * (l_1 / (2 * l_k3**2)) * (l_1**2 - 3 * l_1 * l_k3 + 2 * l_k3**2)
        M_uII = (F_j/2) * (l_k2 / (2 * l_k3**2)) * (l_k2**2 - 3 * l_k2 * l_k3 + 2 * l_k3**2)

        M_gI = -M_uI + ((F_j/2) - ((F_j/2) * (l_1**2 / (2 * l_k3**3)) * (3 * l_k3 - l_1))) * l_1
        M_gII = -M_uII + ((F_j/2) - ((F_j/2) * (l_k2**2 / (2 * l_k3**3)) * (3 * l_k3 - l_k2))) * l_k2
        return max(max(M_uI, M_gI), max(M_uII, M_gII))

    elif wariant_podparcia == "dwa koła jeden koniec zamocowany, ciasne śruby":
        R_BI = (F_j/2) * ((l_k3 - l_1)**2 / l_k3**3) * (l_k3 + 2 * l_1)
        R_BII = (F_j/2) * ((l_k3 - l_k2)**2 / l_k3**3) * (l_k3 + 2 * l_k2)

        M_uAI = (F_j/2) * (((l_k3 - l_1) * l_1**2) / l_k3**2)
        M_uAII = (F_j/2) * (((l_k3 - l_k2) * l_k2**2) / l_k3**2)
        M_uBI = (F_j/2) * (((l_k3 - l_1)**2 * l_1) / l_k3**2)
        M_uBII = (F_j/2) * (((l_k3 - l_k2)**2 * l_k2) / l_k3**2)

        M_gI = -M_uBI + R_BI * l_1
        M_gII = -M_uBII + R_BII * l_k2

        M_gmaxI = max(M_uAI, M_uBI, M_gI)
        M_gmaxII = max(M_uAII, M_uBII, M_gII)
        return max(M_gmaxI, M_gmaxII)

def oblicz_d_sworzen(M_gmax, k_g):
    return ((32 * M_gmax) / (math.pi * k_g)) ** (1/3)

def oblicz_sily(M_k, R_wk, n_sworzni):
    F_list = []

    def obl_fi_kj(i):
        return (2 * math.pi * (i - 1)) / n_sworzni
    
    for i in range(1, n_sworzni + 1):
        F_j = M_k * (R_wk * math.sin(obl_fi_kj(i)) / sum(
            [R_wk**2 * math.sin(obl_fi_kj(j))**2 for j in range(1, n_sworzni + 1)]
        ))
        F_list.append(F_j)
    
    return F_list

def oblicz_naciski(sily, d_otw, d_tul, b_kola, v_k, v_t, E_k, E_t):
    R_otw = d_otw / 2
    R_tul = d_tul / 2

    # TODO: usunac te kombinacje, sily nie powinny byc ujemne
    # jesli mi powie szef, ze tak maja wygladac, ze sily zrownywac z 0 , to dam w liczeniu sil
    stala = (R_otw - R_tul) / (b_kola * math.pi * R_tul * R_otw * (((1 - v_k**2) / E_k) + ((1 - v_t**2) / E_t)))
    try:
        return [math.sqrt(F_j if F_j >= 0 else 0 * stala) for F_j in sily]
    except ValueError:
        return None

def oblicz_straty(omg_0, mimosrod, sily, d_tul, d_sw, f_kt, f_ts):
    # nie wiem...
    R_tzj, R_sj = d_tul / 2, d_sw / 2
    u = None
    [omg_0 * ((u + 1) / u) * (mimosrod / (R_tzj - R_sj)) * (f_kt - f_ts) * sum(sily)]

def obliczenia_mech_wyjsciowy(dane, dane_zew, d_otw=1):
    M_k = dane_zew["M"] / dane_zew["K"]
    E, k_g = dane["mat_sw"]["E"], dane["mat_sw"]["k_g"]
    b_kola = dane["b"]
    n_sworzni = dane["n"]
    R_wk = dane["R_wk"]
    e1 = dane["e1"]
    e2 = dane["e2"]
    wariant_podparcia = dane["podparcie"]
    d_tul = dane["d_tul"]

    sily = oblicz_sily(M_k, R_wk, n_sworzni)

    E_k, v_k = dane_zew["E_kola"], dane_zew["v_kola"]
    E_t, v_t = dane["mat_tul"]["E"], dane["mat_tul"]["v"]
    naciski = oblicz_naciski(sily, d_otw, d_tul, b_kola, v_k, v_t, E_k, E_t)
    momenty = [oblicz_Mgmax(wariant_podparcia, F_j, b_kola, e1, e2) for F_j in sily]
    d_smax = oblicz_d_sworzen(max(momenty), k_g)
    strzalki = [oblicz_fs(wariant_podparcia, F_j, E, b_kola, d_smax, e1, e2) for F_j in sily]

    return {
        "d_smax": d_smax,
        "sily": sily,
        "naciski": naciski,
    }

def oblicz_luzy(n_sworzni, R_wk, mimosrod, d_tul, d_otw, tolerancje):
    '''
    Tolerancje:
    T_o: promienia otworu
    T_t: promienia zew tuleji
    T_Rk: promienia rozmieszczenia otworów
    T_Rt: promienia rozmieszczenia tuleji
    T_fi_k: kątowego rozmieszczenia otworów w kole cykloidalnym
    T_fi_t: kątowego rozmieszczenia tulei w elemencie wyjściowym
    T_e: wykonania mimośrodu

    Oblicza wszystkie możliwości przechodząc po polach tolerancji krokiem 0.001mm. Zwraca dla każdego otworu min i max wartosc
    '''
    def obl_fi_kj(i):
        return (2 * math.pi * (i - 1)) / n_sworzni

    tol_R_otwj = [(d_otw/2) + i for i in range(tolerancje["T_o"][0], tolerancje["T_o"][1] + 0.001, 0.001)]
    tol_R_tzj = [(d_tul/2) + i for i in range(tolerancje["T_t"][0], tolerancje["T_t"][1] + 0.001, 0.001)]
    tol_R_wk = [R_wk + i for i in range(tolerancje["T_Rk"][0], tolerancje["T_Rk"][1] + 0.001, 0.001)]
    tol_R_wt = [R_wk + i for i in range(tolerancje["T_Rt"][0], tolerancje["T_Rt"][1] + 0.001, 0.001)]
    pole_tol_fi_kj = range(tolerancje["T_fi_k"][0], tolerancje["T_fi_k"][1] + 0.001, 0.001)
    pole_tol_fi_tj = range(tolerancje["T_fi_t"][0], tolerancje["T_fi_t"][1] + 0.001, 0.001)
    tol_e = [mimosrod + i for i in range(tolerancje["T_e"][0], tolerancje["T_e"][1] + 0.001, 0.001)]

    def oblicz_luz(fi_kj):
        tol_fi_kj = [fi_kj + i for i in pole_tol_fi_kj]
        tol_fi_tj = [fi_kj + i for i in pole_tol_fi_tj]
        tol_y_okj = [round(R * math.cos(fi), 3) for R in tol_R_wk for fi in tol_fi_kj]
        tol_y_otj = [round(R * math.cos(fi), 3) for R in tol_R_wt for fi in tol_fi_tj]
        tol_y_oktj = [y_otj - e for y_otj in tol_y_otj for e in tol_e]
        luz_el1 =  [abs(y_oktj - R_tzj) for y_oktj in tol_y_oktj for R_tzj in tol_R_tzj]
        luz_el2 =  [abs(y_okj - R_otwj) for y_okj in tol_y_okj for R_otwj in tol_R_otwj]
        luz = [lu_1 - lu_2 for lu_1 in luz_el1 for lu_2 in luz_el2]
        return [min(luz), max(luz)]

    luzy = [oblicz_luz(obl_fi_kj(ind)) for ind in range(1, n_sworzni + 1)]

def oblicz_przemieszczenie_tul_otw(sily, b_kola, d_otw, d_tul, E_k, v_k, E_t, v_t):
    R_otw, R_tul = (d_otw / 2), (d_tul / 2)
    c = math.sqrt(((4 * max(sily)) / (math.pi * b_kola)) * (((1 - v_k**2) / E_k) + ((1 - v_t**2) / E_t)) * (R_otw * R_tul / (R_otw - R_tul)))
    return (max(sily) / (math.pi * b_kola)) * (((1 - v_k**2) / E_k) * ((1 / 3) + math.log((4 * R_otw) / c)) + ((1 - v_t**2) / E_t) * ((1 / 3) + math.log((4 * R_tul) / c)))

def oblicz_sily_z_luzami(M_k, n_sworzni, b_kola, R_wk, mimosrod, d_tul, d_otw, tolerancje, E_k, v_k, E_t, v_t):
    def obl_fi_kj(i):
        return (2 * math.pi * (i - 1)) / n_sworzni
    
    sily_0 = oblicz_sily(M_k, R_wk, n_sworzni)
    del_max = oblicz_przemieszczenie_tul_otw(sily_0, b_kola, d_otw, d_tul, E_k, v_k, E_t, v_t)
    delty = [del_max * math.sin(obl_fi_kj(i)) for i in range(1, n_sworzni+1)]
    poprawione_luzy = [[luz[0] - delty[i], luz[1] - delty[i]] for i, luz in enumerate(oblicz_luzy(n_sworzni, R_wk, mimosrod, d_tul, d_otw, tolerancje))]

    # co dac w tych sum(), jak wziac pod uwage ze mam min i max luz...
    sily_z_luzami = [[M_k * del_max / (R_wk * obl_fi_kj(i) * sum([0])),
                      M_k * del_max / (R_wk * obl_fi_kj(i) * sum([0]))
                      ] for i in range(1, n_sworzni + 1)]
