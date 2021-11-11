

def temp_calculation(temp_hot_box, temp_cold_box):
    temp_in = temp_hot_box - temp_cold_box
    q = 1
    a = 0.15*0.15
    output = q/(a*temp_in)
    return output


def heat_flux(temp_in, v_in, cal):
    stc = (0.00334*temp_in+0.917)*cal
    q = v_in/stc
    return q

