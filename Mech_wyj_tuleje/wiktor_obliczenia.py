import math

j = 0 # obecny trzpień/tuleja/otwór
z_0 = 0 # liczba łączna otworów
z_w = 0 # liczba tuleji ze sworzniami
R_wk = 0 # promień rozmieszczenia otworów (X1 O1 Y)
R_wt = 0 # promień rozmieszczenia tuleji (X2 O2 Y)
e = 0 # mimośród
E = 0 # moduł Younga materiału trzpienia
J = (math.pi * (d_smax ** 4)) / 64 # moment bezwladnosci trzpien

# Kąt rozmieszczenia j-tego otworu w kole cykloidalnym
fi_kj = (2 * math.pi * (j - 1)) / z_0

# współrzędne środka otworu j-tego (bez odchyłek) --- w układzie stałym - X1 O1 Y
x_okj = R_wk * math.sin(fi_kj)
y_okj = R_wk * math.cos(fi_kj)


# Kąt rozmieszczenia j-tej tuleji w kole cykloidalnym
fi_tj = (2 * math.pi * (j - 1)) / z_w

# współrzędne środka j-tej tulei (bez odchyłek) --- w ruchomym układzie - X2 O2 Y.
x_otj = R_wt * math.sin(fi_tj)
y_otj = R_wt * math.cos(fi_tj)

# środek tuleji (bez odchyłek) --- w układzie stałym - X2 O2 Y
x_oktj = x_otj
y_oktj = y_otj - e


##########################

# średnica sworznia
M_gmax = 0 # moment gnący max na sworzeń
k_g = 0 # dop. naprężenia na zginanie, dla materiału sworznia
f_s = 0 # strzałka ugięcia sworzeń
F_j = 0 # siła na sworzen
l_1 = 0 # pół szerokości koła
l_2 = 0 # szerokość koła  -- ???  2 * l_1

# jedno koło
M_gmax = F_j * l_1
f_s = - (F_j * (l_1 ** 3)) / (3 * E * J)

# jedno koło, jeden koniec zamocowany, luźne śruby
M_u = F_j * (l_1 / (2 * (l_2 ** 2))) * ((l_1 ** 2) - 3 * l_1 * l_2 + 2 * (l_2 ** 2))
R = F_j - (F_j * ((l_1 ** 3) / (2 * (l_2 ** 3))) * (3 * l_2 - l_1))

M_gI = -M_u + R * l_1
M_gII = -M_u + R * l_2 - F_j * (l_2 - l_1)
M_gmax = max(M_gI, M_gII)
f_s = (F_j * (l_1 ** 2) * (l_2 - l_1)) / (2 * E * J)

# ciasne śruby
R_B = F_j * ((2 * ((l_2 - l_1) ** 3) - 3 * ((l_2 - l_1) ** 2) * l_2 + (l_2 ** 3)) / (l_2 ** 3))
M_uA = F_j * ((((l_2 - l_1) ** 2) * l_1) / (l_2 ** 2))
M_uB = F_j * (((l_2 - l_1) * (l_1 ** 2)) / (l_2 ** 2))
M_g = -M_uB + R_B * l_1

M_gmax = max(M_uA, M_uB, M_g)

f_s = (2 * F_j * (l_1 ** 3) * ((l_2 - l_1) ** 2)) / (2 * E * J * ((l_2 - 2 * l_1) ** 2))

# dwa koła
l_k1 = 0 # odległość do pierwszego koła
l_k2 = 0 # odległość do drugiego koła
l_k3 = 0 # laczna grubosc obu kol + przerwy miedzy nimi
F_jI = 0 # sila na blizszy trzpien
F_jII = 0 # sila na dalszy trzpien

M_gkI = -(F_jI * l_k1) + F_jI * l_k1
M_gkII = -(F_jII * l_k2) + F_jII * l_k2
f_sI = - (F_jI * (l_k1 ** 3)) / (3 * E * J)
f_sII = - (F_jII * (l_k2 ** 3)) / (3 * E * J)

# dwa koła jeden koniec zamocowany, luźne śruby
M_uI = F_jI * (l_k1 / (2 * (l_k3 ** 2))) * ((l_k1 ** 2) - 3 * l_k1 * l_k3 + 2 * (l_k3 ** 2))
M_uII = F_jII * (l_k2 / (2 * (l_k3 ** 2))) * ((l_k2 ** 2) - 3 * l_k2 * l_k3 + 2 * (l_k3 ** 2))

M_gkI = -M_uI + (F_jI - (F_jI * ((l_k1 ** 3) / (2 * (l_k3 ** 3))) * (3 * l_k3 - l_k1))) * l_k1
M_gkII = -M_uII + (F_jII - (F_jII * ((l_k2 ** 3) / (2 * (l_k3 ** 3))) * (3 * l_k3 - l_k2))) * l_k2

f_sI = (F_jI * (l_k1 ** 2) * (l_k3 - l_k1)) / (2 * E * J)
f_sII = (F_jII * (l_k2 ** 2) * (l_k3 - l_k2)) / (2 * E * J)

# dwa koła jeden koniec zamocowany, ciasne śruby
R_BI = F_jI * ((2 * ((l_k3 - l_k1) ** 3) - 3 * ((l_k3 - l_k1) ** 2) * l_k3+ (l_k3 ** 3)) / (l_k3 ** 3))
R_BII = F_jII * ((2 * ((l_k3 - l_k2) ** 3) - 3 * ((l_k3 - l_k2) ** 2) * l_k3 + (l_k3 ** 3)) / (l_k3 ** 3))

M_uAI = F_jI * ((((l_k3 - l_k1) ** 2) * l_k3) / (l_k3 ** 2))
M_uAII = F_jII * ((((l_k3 - l_k2) ** 2) * l_k2) / (l_k3 ** 2))
M_uBI = F_jI * (((l_k3 - l_k1) * (l_k1 ** 2)) / (l_k3 ** 2))
M_uBII = F_jII * (((l_k3 - l_k2) * (l_k2 ** 2)) / (l_k3 ** 2))

M_gI = -M_uBI + R_BI * l_k1
M_gII = -M_uBII + R_BII * l_k2

M_gmaxI = max(M_uAI, M_uBI, M_gI)
M_gmaxII = max(M_uAII, M_uBII, M_gII)

f_sI = (2 * F_jI * (l_k1 ** 3) * ((l_k3 - l_k1) ** 2)) / (2 * E * J * ((l_k3 - 2 * l_k1) ** 2))
f_sII = (2 * F_jII * (l_k2 ** 3) * ((l_k3 - l_k2) ** 2)) / (2 * E * J * ((l_k3 - 2 * l_k2) ** 2))

d_smax = ((32 * M_gmax) / (math.pi * k_g)) ** (1/3)
