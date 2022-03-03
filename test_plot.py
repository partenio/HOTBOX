import matplotlib.pyplot as plt
import numpy as np

def plot_temp(ypoints, xpoints):


    plt.xlabel('Tiempo', weight = 'bold')
    plt.ylabel('Temperatura',weight = 'bold')
    plt.title('Caja calinte(temperatura promedio])',weight = 'bold')
    plt.xticks(xpoints, weight = 'bold')
    plt.yticks(ypoints, weight = 'bold')
    
    plt.plot(xpoints, ypoints)
    plt.savefig("/home/partenio/Desktop/HOTBOX/output.png", transparent=True)
