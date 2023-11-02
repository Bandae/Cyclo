import math

# Czy w przypadku dwóch kół, dwóch momentów wystarczy wziąć pod uwagę większy z nich i na jego podstawie policzyć d_smax?
# Czy M_u zawsze wieksze niz to srodkowe?
# TODO: l_k3 cos z nim zrobic bo złe jest

def oblicz_fs(wariant_podparcia, F_j, E, b_kola, d_smax, e1, e2):
    l_1 = b_kola / 2 + e1 # odleglosc do polowy kola pierwszego
    l_2 = b_kola + e1 # odleglosc do podparcia jesli jedno kolo cykloidalne
    l_k2 = b_kola * 1.5 + e1 + e2 # odleglosc do polowy kola drugiego
    l_k3 = 0 # odleglosc do podparcia jesli dwa kola cykloidalne

    J = (math.pi * (d_smax ** 4)) / 64 # moment bezwladnosci trzpien
    f_s = 0

    if wariant_podparcia == "jedno koło cykloidalne":
        f_s = - (F_j * (l_1 ** 3)) / (3 * E * J)
    
    elif wariant_podparcia == "jedno koło, jeden koniec zamocowany, luźne śruby":
        f_s = (F_j * (l_1 ** 2) * (l_2 - l_1)) / (2 * E * J)

    elif wariant_podparcia == "jedno koło, jeden koniec zamocowany, ciasne śruby":
        f_s = (2 * F_j * (l_1 ** 3) * ((l_2 - l_1) ** 2)) / (2 * E * J * ((l_2 - 2 * l_1) ** 2))

    elif wariant_podparcia == "dwa koła":
        f_sI = - ((F_j/2) * (l_1 ** 3)) / (3 * E * J)
        f_sII = - ((F_j/2) * (l_k2 ** 3)) / (3 * E * J)

    elif wariant_podparcia == "dwa koła, jeden koniec zamocowany, luźne śruby":
        f_sI = ((F_j/2) * (l_1 ** 2) * (l_k3 - l_1)) / (2 * E * J)
        f_sII = ((F_j/2) * (l_k2 ** 2) * (l_k3 - l_k2)) / (2 * E * J)

    elif wariant_podparcia == "dwa koła jeden koniec zamocowany, ciasne śruby":
        f_sI = (2 * (F_j/2) * (l_1 ** 3) * ((l_k3 - l_1) ** 2)) / (2 * E * J * ((l_k3 - 2 * l_1) ** 2))
        f_sII = (2 * (F_j/2) * (l_k2 ** 3) * ((l_k3 - l_k2) ** 2)) / (2 * E * J * ((l_k3 - 2 * l_k2) ** 2))
    
    return f_s

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
    l_k3 = 0 # odleglosc do podparcia jesli dwa kola cykloidalne

    M_gmax = 0

    if wariant_podparcia == "jedno koło cykloidalne":
        M_gmax = F_j * l_1

    elif wariant_podparcia == "jedno koło, jeden koniec zamocowany, luźne śruby":
        M_u = F_j * (l_1 / (2 * (l_2 ** 2))) * ((l_1 ** 2) - 3 * l_1 * l_2 + 2 * (l_2 ** 2))
        R = F_j - (F_j * ((l_1 ** 2) / (2 * (l_2 ** 3))) * (3 * l_2 - l_1))
        M_gI = -M_u + R * l_1
        M_gII = -M_u + R * l_2 - F_j * (l_2 - l_1)
        M_gmax = max(M_gI, M_gII, M_u)

    elif wariant_podparcia == "jedno koło, jeden koniec zamocowany, ciasne śruby":
        R_B = F_j * ((2 * ((l_2 - l_1) ** 2)) / (l_2 ** 3)) * (l_2 + 2 * l_1)
        M_uA = F_j * (((l_2 - l_1) * (l_1 ** 2)) / (l_2 ** 2))
        M_uB = F_j * ((((l_2 - l_1) ** 2) * l_1) / (l_2 ** 2))
        M_g = -M_uB + R_B * l_1
        M_gmax = max(M_uA, M_uB, M_g)
 
    elif wariant_podparcia == "dwa koła":
        M_gI = (F_j/2) * l_1
        M_gII = (F_j/2) * l_k2
        M_gmax = max(M_gI, M_gII)

    elif wariant_podparcia == "dwa koła, jeden koniec zamocowany, luźne śruby":
        M_uI = (F_j/2) * (l_1 / (2 * (l_k3 ** 2))) * ((l_1 ** 2) - 3 * l_1 * l_k3 + 2 * (l_k3 ** 2))
        M_uII = (F_j/2) * (l_k2 / (2 * (l_k3 ** 2))) * ((l_k2 ** 2) - 3 * l_k2 * l_k3 + 2 * (l_k3 ** 2))

        M_gI = -M_uI + ((F_j/2) - ((F_j/2) * ((l_1 ** 2) / (2 * (l_k3 ** 3))) * (3 * l_k3 - l_1))) * l_1
        M_gII = -M_uII + ((F_j/2) - ((F_j/2) * ((l_k2 ** 2) / (2 * (l_k3 ** 3))) * (3 * l_k3 - l_k2))) * l_k2
        M_gmax = max(max(M_uI, M_gI), max(M_uII, M_gII))

    elif wariant_podparcia == "dwa koła jeden koniec zamocowany, ciasne śruby":
        R_BI = (F_j/2) * ((2 * ((l_k3 - l_1) ** 2)) / (l_k3 ** 3)) * (l_k3 + 2 * l_1)
        R_BII = (F_j/2) * ((2 * ((l_k3 - l_k2) ** 2)) / (l_k3 ** 3)) * (l_k3 + 2 * l_k2)

        M_uAI = (F_j/2) * (((l_k3 - l_1) * (l_1 ** 2)) / (l_k3 ** 2))
        M_uAII = (F_j/2) * (((l_k3 - l_k2) * (l_k2 ** 2)) / (l_k3 ** 2))
        M_uBI = (F_j/2) * ((((l_k3 - l_1) ** 2) * l_k3) / (l_k3 ** 2))
        M_uBII = (F_j/2) * ((((l_k3 - l_k2) ** 2) * l_k2) / (l_k3 ** 2))

        M_gI = -M_uBI + R_BI * l_1
        M_gII = -M_uBII + R_BII * l_k2

        M_gmaxI = max(M_uAI, M_uBI, M_gI)
        M_gmaxII = max(M_uAII, M_uBII, M_gII)
        M_gmax = max(M_gmaxI, M_gmaxII)

    return M_gmax

def oblicz_d_sworzen(M_gmax, k_g):
    return ((32 * M_gmax) / (math.pi * k_g)) ** (1/3)

def oblicz_sily(M_k, R_wk, n_sworzni):
    F_list = []

    def obl_fi_kj(i):
        return (2 * math.pi * (i - 1)) / n_sworzni
    
    for i in range(1, n_sworzni + 1):
        fi_kj = obl_fi_kj(i)
        F_j = M_k * (R_wk * math.sin(fi_kj) / sum(
            [(R_wk ** 2) * (math.sin(obl_fi_kj(j)) ** 2) for j in range(1, n_sworzni + 1)]
        ))
        F_list.append(F_j)
    
    return F_list

def oblicz_naciski(sily, sr_otw, sr_tul, b_kola, v_k, v_t, E_k, E_t):
    R_otw = sr_otw / 2
    R_tul = sr_tul / 2

    # TODO: usunac to abs(), sily nie powinny byc ujemne
    stala = (R_otw - R_tul) / (b_kola * math.pi * R_tul * R_otw * (((1 - (v_k ** 2)) / E_k) + ((1 - (v_t ** 2)) / E_t)))
    try:
        return [math.sqrt(abs(F_j) * stala) for F_j in sily]
    except ValueError:
        return None

def obliczenia_mech_wyjsciowy(dane, dane_zew, sr_otw=1):
    M_k = dane_zew["M"] / dane_zew["K"]
    k_g = dane["mat_sw"]["k_g"]
    E = dane["mat_sw"]["E"]
    b_kola = dane["b"]
    n_sworzni = dane["n"]
    R_wk = dane["R_wk"]
    e1 = dane["e1"]
    e2 = dane["e2"]
    wariant_podparcia = dane["podparcie"]
    sr_tul = dane["d_tul"]

    sily = oblicz_sily(M_k, R_wk, n_sworzni)

    # TODO: dodac zaciaganie materialow z bazy pietro wyzej
    v_k, v_t, E_k, E_t = 0.3, 0.3, 210000, 210000
    naciski = oblicz_naciski(sily, sr_otw, sr_tul, b_kola, v_k, v_t, E_k, E_t)
    momenty = [oblicz_Mgmax(wariant_podparcia, F_j, b_kola, e1, e2) for F_j in sily]
    d_smax = oblicz_d_sworzen(max(momenty), k_g)
    strzalki = [oblicz_fs(wariant_podparcia, F_j, E, b_kola, d_smax, e1, e2) for F_j in sily]

    return {
        "d_smax": d_smax,
        "sily": sily,
        "naciski": naciski,
    }
