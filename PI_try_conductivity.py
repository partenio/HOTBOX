
from array import array
import numpy as np
import seaborn as sns
from sympy import *
import matplotlib.pyplot as plt
import control.matlab as control


def control_math(input):

    #compesated trasnfer funtion
    G = control.tf([0.002631, 11.35], [0.0003938, 1.003, 11.95])
    #print(G)

    #feedback with the input
    error = 52 - input
    print("error:",error)

    #multiplication with the setpoint
    if error < 1:
        G = 1*G
    # feedback with the input
    else:
        G = error*G
    #print(G)

    # limits whe s equals 0
    (num_list, den_list) = control.tfdata(G)

    num_array = np.array(num_list)
    den_array = np.array(den_list)
    num_array = num_array[0,0,:]
    den_array = den_array[0,0,:]

    # print(num_array[1])
    # print(den_array[2])

    value = num_array[1]/den_array[2]
    #print(value)

    #clamping the values

    if value > 5:
        value = 5
    if value < 0:
        value = 0 
    if error <= 0:
        value = 0
    
    return(value)


