import math

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


def calculate_gear(gear_data, material_data, out_data):
    liczba_rolek = gear_data["z"] + 1
    liczba_obciazonych_rolek = liczba_rolek/2 if liczba_rolek%2 == 0 else (liczba_rolek+1)/2
    F_max = 1000 * 4 * (out_data["M_wyj"] / gear_data["K"]) / (gear_data["Rw1"] * liczba_rolek)

    Fx = [0] * liczba_rolek
    Fy = [0] * liczba_rolek
    sily = [0] * liczba_rolek
    naprezenia = [0] * liczba_rolek
    straty_mocy = [0] * liczba_rolek
    # luzy = [0] * liczba_rolek

    for i in range(liczba_rolek):
        #TODO: w wykresach jest takie coś co zeruje wyniki, ale żeby to w raporcie, i ich sumy miały sens, to zeruję je tutaj.
        # może to być problem dla obliczeń z luzami.
        if i==0 or i+1 > liczba_obciazonych_rolek:
            continue

        #SILY
        al_ki = 2 * math.pi * i / liczba_rolek
        al_si = (math.pi / 2) - abs(math.atan(gear_data["Rb2"] * math.sin(al_ki) / ((gear_data["Rw1"] + gear_data["e"]) - gear_data["Rb2"] * math.cos(al_ki))))
        hi = gear_data["Rw1"] * math.cos(al_si)
        Fx[i] = F_max * hi * math.cos(al_si) / gear_data["Rw1"]
        Fy[i] = F_max * hi * math.sin(al_si) / gear_data["Rw1"]
        sily[i] = round(math.sqrt(Fx[i]**2 + Fy[i]**2), 1)

        #NACISKI
        reke = (gear_data["ro"] * liczba_rolek * ((1 - (2 * gear_data["lam"] * math.cos(gear_data["z"] * al_ki)) + ((gear_data["lam"])**2))**1.5)/(1-(gear_data["lam"]*(gear_data["z"]+2)*math.cos(gear_data["z"]*al_ki)) + (gear_data["lam"]**2 * liczba_rolek))) - gear_data["g"]
        naprezenia[i] = round(math.sqrt((sily[i] * abs(gear_data["g"] + reke)) / ((gear_data["g"] * abs(reke) * material_data["b_wheel"]) * (((1 - material_data["wheel"]["v"]**2) / material_data["wheel"]["E"]) + ((1 - material_data["roller"]["v"]**2) / material_data["roller"]["E"])) * math.pi)), 2)

        #STRATY_MOCY
        AIC = math.sqrt(gear_data["Rw2"]**2 + (gear_data["Ra2"] + gear_data["g"])**2 - 2 * gear_data["Rw2"] * (gear_data["Ra2"] + gear_data["g"]) * math.cos(al_ki)) - gear_data["g"]
        straty_mocy[i] = round((math.pi * out_data["n_wej"] / 30) * (gear_data["e"] / gear_data["Rw1"]) * ((AIC / gear_data["g"]+1) * material_data["f_kr"] + (AIC/gear_data["g"]) * material_data["f_ro"]) * sily[i], 3)

        #LUZY MIEDZYZEBNE:
        # x_ze=(gear_data["Rw1"]+gear_data["ro"])*math.sin(al_ki)-gear_data["e"]*math.sin(((gear_data["Rw1"]+gear_data["ro"])/gear_data["ro"])*al_ki)-(gear_data["g"]+gear_data["l-ze"])*((math.sin(al_ki)-gear_data["lam"]*math.sin((gear_data["z"]+1)*al_ki))/((1-2*gear_data["lam"]*math.cos(gear_data["z"]*al_ki)+gear_data["lam"]**2)**0.5))
        # y_ze=(gear_data["Rw1"]+gear_data["ro"])*math.cos(al_ki)-gear_data["e"]*math.cos(((gear_data["Rw1"]+gear_data["ro"])/gear_data["ro"])*al_ki)-(gear_data["g"]+gear_data["l-ze"])*((math.cos(al_ki)-gear_data["lam"]*math.cos((gear_data["z"]+1)*al_ki))/((1-2*gear_data["lam"]*math.cos(gear_data["z"]*al_ki)+gear_data["lam"]**2)**0.5))
        # x_ozri=(gear_data["Rb2"]+gear_data["l-rg"])*math.sin(al_ki+gear_data["l-ri"])
        # y_ozri=(gear_data["Rb2"]+gear_data["l-rg"])*math.cos(al_ki+gear_data["l-ri"])-(gear_data["e"]+gear_data["l-e"])
        # luzy[i]=((((x_ozri-x_ze)**2)+((y_ozri-y_ze)**2))**0.5)-(gear_data["g"])

    return {
        "F_max": round(F_max, 1),
        "p_max": round(max(naprezenia), 2),
        "F_wzx": round(sum(Fx), 1),
        "F_wzy": round(sum(Fy), 1),
        "F_wz": round(math.sqrt(sum(Fx)**2 + sum(Fy)**2), 1),
        "sily": sily,
        "naciski": naprezenia,
        "straty": straty_mocy,
        # "luzy": luzy,
    }

        # STARE
        #kat = kat_glowny*self.przyrost_kata
        #reke=((gear_data["ro"]*(gear_data["z"]+1)*math.pow((1-(2*gear_data["lam"]*math.cos(gear_data["z"]*kat*0.0175))+math.pow(gear_data["lam"],2)),(3/2)))/(1-(gear_data["lam"]*(gear_data["z"]+2)*(math.cos(gear_data["z"]*kat*0.0175)))+(math.pow(gear_data["lam"],2)*(gear_data["z"]+1)))-(gear_data["g"]))
        #reke = ((gear_data["ro"] * (gear_data["z"] + 1) * math.pow(
        #    (1 - (2 * gear_data["lam"] * math.cos(kat * 0.0175)) + math.pow(gear_data["lam"], 2)),
        #    (3 / 2))) / (1 - (gear_data["lam"] * (gear_data["z"] + 2) * (math.cos(kat * 0.0175))) + (
        #            math.pow(gear_data["lam"], 2) * (gear_data["z"] + 1))) - (gear_data["g"]))
        #teta=i*self.przyrost_kata
        #x=math.sqrt((math.pow(gear_data["Rb"],2))+(math.pow(gear_data["Rw1"],2))-(2*gear_data["Rb"]*gear_data["Rw1"]*math.cos(teta * 0.0175)))
        #beta = math.degrees(math.asin(gear_data["Rb"]*math.sin(teta * 0.0175)/x))
        #al_ki[i]=90-beta
        #sily[a]=(4*Mk*math.cos(alfa[a] * 0.0175))/(gear_data["Rw1"]*(gear_data["z"]+1))
        #naprezenia[a]=math.sqrt((sily[a]*(reke+gear_data["g"]))/(gear_data["b"]*math.pi*reke*gear_data["g"]*(((1-math.pow(gear_data["v1"],2))/(gear_data["E1"])))+((1-math.pow(gear_data["v1"],2))/(gear_data["E2"]))))
        #naprezenia[a]=math.sqrt((sily[i]*(reke+gear_data["g"]))/((gear_data["b"]*3.1415*reke*gear_data["g"])*(((1-math.pow(gear_data["v1"],2))/(gear_data["E1"]))+((1-math.pow(gear_data["v2"],2))/(gear_data["E2"])))))

        #Straty Mocy

        #AIC = (math.sqrt(math.pow(gear_data["Rw2"],2)+math.pow((gear_data["Rf1"]+gear_data["g"]),2)-2*gear_data["g"]*(gear_data["Rf1"]+gear_data["g"])*math.cos(kat*0.0175)))-gear_data["g"]
        #straty_mocy[a]= ((math.pi*gear_data["nwej"])/30)*(gear_data["Rf2"]/gear_data["e"])*(((AIC/gear_data["g"])+1)*gear_data["t1"]+(AIC/gear_data["g"])*gear_data["t2"])*sily[i]
        #luzy[a]= 1+kat
