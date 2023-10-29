import math

# Czy w przypadku dwóch kół, dwóch momentów wystarczy wziąć pod uwagę większy z nich i na jego podstawie policzyć d_smax?
# Czy M_u zawsze wieksze niz to srodkowe?

def oblicz_fs(wariant_podparcia, F_j, E, b_kola, d_smax):
    e1 = 0 # przerwa miedzy kolem a tarczą wyjściową
    e2 = 0 # przerwa miedzy kolami
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

def oblicz_Mgmax(wariant_podparcia, F_j, E, b_kola):
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
    e1 = 0 # miedzy kolem a tarczą wyjściową
    e2 = 0 # szpara miedzy kolami
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
        # R_B = F_j * ((2 * ((l_2 - l_1) ** 3) - 3 * ((l_2 - l_1) ** 2) * l_2 + (l_2 ** 3)) / (l_2 ** 3))
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

def obliczenia_mech_wyjsciowy(wariant_podparcia, k_g, E, b_kola, n_sworzni, M_k, R_wk):
    '''
    E, k_g, b_kola, R_wk - wziac z interfejsu od uzytkownika
    M_k - policzone, od Pawla
    '''
    sily = oblicz_sily(M_k, R_wk, n_sworzni)
    momenty = [oblicz_Mgmax(wariant_podparcia, F_j, E, b_kola) for F_j in sily]
    d_smax = oblicz_d_sworzen(max(momenty), k_g)
    strzalki = [oblicz_fs(wariant_podparcia, F_j, E, b_kola, d_smax) for F_j in sily]

    return {
        "d_smax": d_smax,
    }
