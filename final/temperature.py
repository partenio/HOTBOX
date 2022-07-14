
def con_calculation(temp_hot_box: float, temp_cold_box: float, flux: float) -> float:
    delta_temp = temp_hot_box-temp_cold_box
    output = flux*0.018/(delta_temp)
    return output

def heat_flux(temp_in: float, v_in: float, cal: float) -> float:
    stc = ((0.00334*temp_in)+1.917)*cal
    flux = (v_in*1_000_000)/stc
    return flux