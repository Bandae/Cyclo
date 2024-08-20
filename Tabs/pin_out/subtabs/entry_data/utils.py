import math

def sprawdz_przecinanie_otworow(R_wk, n_sworzni, d_otw):
    '''Sprawdza czy otwory w kole cykloidalnym będą się przecinać'''

    x_o1 = R_wk * math.sin(0)
    y_o1 = R_wk * math.cos(0)
    x_o2 = R_wk * math.sin(2 * math.pi / n_sworzni)
    y_o2 = R_wk * math.cos(2 * math.pi / n_sworzni)

    distance = math.sqrt((x_o2 - x_o1)**2 + (y_o2 - y_o1)**2)
    return distance < d_otw
