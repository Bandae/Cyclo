import math

### ZAŁOŻENIA:
# 1: z_w to liczba łączna tuleji i jest = z_o. więc fi_kj = fi_t_j.
# 2: zawsze M_g > M_u dowolne
# 3: F_j jest takie samo dla każdego trzpienia, też dla obu kół jak są dwa koła
# 4: Rwt = Rwk tylko w innym układzie odniesienia
# 5: l_1 to polowa l_2; l_k1 = l_1; l_k2 = 3*l_k1 + szpara; l_k3 = 4*l_k1 + szpara

### ZAPYTAĆ:

j = 0 # obecny trzpień/tuleja/otwór
z_0 = 0 # liczba łączna otworów/ tuleji / sworzni
R_wk = 0 # promień rozmieszczenia otworów (X1 O1 Y)
e = 0 # mimośród
E = 0 # moduł Younga materiału trzpienia
M_gmax = 0 # moment gnący max na sworzeń
k_g = 0 # dop. naprężenia na zginanie, dla materiału sworznia
f_s = 0 # strzałka ugięcia sworzeń

d_smax = ((32 * M_gmax) / (math.pi * k_g)) ** (1/3)
J = (math.pi * (d_smax ** 4)) / 64 # moment bezwladnosci trzpien

# Kąt rozmieszczenia j-tego otworu w kole cykloidalnym
fi_kj = (2 * math.pi * (j - 1)) / z_0

# współrzędne środka otworu j-tego (bez odchyłek) --- w układzie stałym - X1 O1 Y
x_okj = R_wk * math.sin(fi_kj)
y_okj = R_wk * math.cos(fi_kj)

# środek tuleji (bez odchyłek) --- w układzie stałym - X1 O1 Y
x_oktj = x_okj
y_oktj = y_okj - e


##########################

# średnica sworznia
F_j = 0 # siła na sworzen
l_2 = 0 # szerokość koła
l_1 = l_2 / 2 # pół szerokości koła

# jedno koło
M_gmax = F_j * l_1
f_s = - (F_j * (l_1 ** 3)) / (3 * E * J)

# jedno koło, jeden koniec zamocowany, luźne śruby
M_u = F_j * (l_1 / (2 * (l_2 ** 2))) * ((l_1 ** 2) - 3 * l_1 * l_2 + 2 * (l_2 ** 2))
R = F_j - (F_j * ((l_1 ** 3) / (2 * (l_2 ** 3))) * (3 * l_2 - l_1))

M_gmax = -M_u + R * l_1
f_s = (F_j * (l_1 ** 2) * (l_2 - l_1)) / (2 * E * J)

# ciasne śruby
R_B = F_j * ((2 * ((l_2 - l_1) ** 3) - 3 * ((l_2 - l_1) ** 2) * l_2 + (l_2 ** 3)) / (l_2 ** 3))
M_uB = F_j * (((l_2 - l_1) * (l_1 ** 2)) / (l_2 ** 2))

M_g = -M_uB + R_B * l_1
f_s = (2 * F_j * (l_1 ** 3) * ((l_2 - l_1) ** 2)) / (2 * E * J * ((l_2 - 2 * l_1) ** 2))

# dwa koła
prz_miedzy_kolami = 0
l_k1 = l_1 # odległość do pierwszego koła
l_k2 = l_2 * 1.5 + prz_miedzy_kolami # odległość do drugiego koła
l_k3 = l_2 * 2 + prz_miedzy_kolami # laczna grubosc obu kol + przerwy miedzy nimi

M_gkI = -(F_j * l_k1) + F_j * l_k1
M_gkII = -(F_j * l_k2) + F_j * l_k2
f_sI = - (F_j * (l_k1 ** 3)) / (3 * E * J)
f_sII = - (F_j * (l_k2 ** 3)) / (3 * E * J)

# dwa koła jeden koniec zamocowany, luźne śruby
M_uI = F_j * (l_k1 / (2 * (l_k3 ** 2))) * ((l_k1 ** 2) - 3 * l_k1 * l_k3 + 2 * (l_k3 ** 2))
M_uII = F_j * (l_k2 / (2 * (l_k3 ** 2))) * ((l_k2 ** 2) - 3 * l_k2 * l_k3 + 2 * (l_k3 ** 2))

M_gkI = -M_uI + (F_j - (F_j * ((l_k1 ** 3) / (2 * (l_k3 ** 3))) * (3 * l_k3 - l_k1))) * l_k1
M_gkII = -M_uII + (F_j - (F_j * ((l_k2 ** 3) / (2 * (l_k3 ** 3))) * (3 * l_k3 - l_k2))) * l_k2

f_sI = (F_j * (l_k1 ** 2) * (l_k3 - l_k1)) / (2 * E * J)
f_sII = (F_j * (l_k2 ** 2) * (l_k3 - l_k2)) / (2 * E * J)

# dwa koła jeden koniec zamocowany, ciasne śruby
R_BI = F_j * ((2 * ((l_k3 - l_k1) ** 3) - 3 * ((l_k3 - l_k1) ** 2) * l_k3+ (l_k3 ** 3)) / (l_k3 ** 3))
R_BII = F_j * ((2 * ((l_k3 - l_k2) ** 3) - 3 * ((l_k3 - l_k2) ** 2) * l_k3 + (l_k3 ** 3)) / (l_k3 ** 3))

M_uBI = F_j * (((l_k3 - l_k1) * (l_k1 ** 2)) / (l_k3 ** 2))
M_uBII = F_j * (((l_k3 - l_k2) * (l_k2 ** 2)) / (l_k3 ** 2))

M_gmaxI = -M_uBI + R_BI * l_k1
M_gmaxII = -M_uBII + R_BII * l_k2

f_sI = (2 * F_j * (l_k1 ** 3) * ((l_k3 - l_k1) ** 2)) / (2 * E * J * ((l_k3 - 2 * l_k1) ** 2))
f_sII = (2 * F_j * (l_k2 ** 3) * ((l_k3 - l_k2) ** 2)) / (2 * E * J * ((l_k3 - 2 * l_k2) ** 2))
