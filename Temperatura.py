

def temp_calculation(temp_hot_box, temp_cold_box):
    temp_in = temp_hot_box - temp_cold_box
    q = 1
    a = 0.15*0.15
    output = q/(a*temp_in)
    return output
