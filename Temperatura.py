

def temp_calculation(temp_hot_box, temp_cold_box, q):
    temp_in = temp_hot_box
    a = 0.15*0.15
    output = q*0.0254/(a*temp_in)
    print(output)
    return output


def heat_flux(temp_in, v_in, cal):
    # stc = ((0.00334*temp_in)+1.917)*cal
    # print("stc: ", stc)
    a = 0.15*0.15
    q = (0.1024*temp_in*a)/0.0254
    # q = v_in/stc
    return q

