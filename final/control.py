SETO_POINTO = 51
UTERMS_1 = 0.999
UTERMS_2 = 9.181e-47
YTERMS = 4.234e-45

def get_temp(error: float, previous_error: float, previous_output: float) -> float:

    uterms = (UTERMS_1* (error) - UTERMS_2*(previous_error))
    yterms = (YTERMS* (previous_output))

    output = clamp(uterms+yterms)
    return output 

def get_error(input_: float) -> float:
    return SETO_POINTO - input_
    
def clamp(value: float, min_: float = 0, max_: float = 5) -> float:
    return max(min_, min(value, max_))




    
