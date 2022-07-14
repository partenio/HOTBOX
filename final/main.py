#imported python mudules
import time
import threading
import concurrent.futures
from datetime import datetime

#imported labayack library
from labjack import ljm

#imported custom codes
from power_sensor import power
from control import get_error, get_temp
from data_save import  init_file, write_data
from temperature import con_calculation, heat_flux

# setting the Datalogger
handle = ljm.openS("ANY", "ANY", "ANY")  # initialiazing the datalogger

INTERVAL_HANDLE = 1  # sets the properties of the in hardware delay
VELOCITY = 1 * 1_000_000  # Change the reading velocity of the readings, every 1,000,000 is a seconds
ljm.startInterval(INTERVAL_HANDLE , VELOCITY) 

file = init_file("/home/partenio/Desktop/HOTBOX/Excel")

# configure the A/D values to read the thermocouples in degrees C 
# the to ani0 and ain1 are the voltage values for the heat flux.
# address to write 11 cus the to first are voltage reades for the heatflux
config_addreses   = [ 9004,9006,9008, 9010, 9012, 9014, 9016, 9018, 9020, 9022, 9024, 9026,
                      9304, 9306, 9308, 9310, 9312, 9314, 9316, 9318, 9320, 9322,9324,9326]  
config_data_types = [ljm.constants.UINT32 for _ in config_addreses]

#24 thermocuples type T, 22 thermocuples type k, 1 is the celcius configuration
config_values = [24, 24, 24, 24, 22, 22, 22, 22, 22, 22, 22,22,22,
                  1,  1,  1,  1,  1,  1,  1,  1,  1,  1,  1, 1, 1 ]  
           
config_total_addresses = len(config_addreses)
ljm.eWriteAddresses(handle, config_total_addresses, config_addreses, config_data_types, config_values)

# print the results of the the actions before for debugging purposes
print("\nPorts configuration complete ")
for i in range(config_total_addresses):
    print("    Address - %i, value : %f" %
          (config_addreses[i], config_values[i]))

# set the inputs to the hotside
hot_addresses = [0, 2, 7006, 7008, 7010, 7016, 7012, 7014, 7018, 7020, 7022]  # 6 termocuplas [see addresses in https://labjack.com/support/software/api/modbus/modbus-map]
hot_data_types = [ljm.constants.FLOAT32 for _ in hot_addresses]
hot_total_addresses = len(hot_addresses)

# set the inputs to the cold side
cold_addresses = [7024,7026]  # [see addresses in https://labjack.com/support/software/api/modbus/modbus-map]
cold_data_types = [ljm.constants.FLOAT32 for _ in cold_addresses]
cold_total_addresses = len(cold_addresses)

#set the output 
output_addresses = [1000]  # [DAC0]
output_data_types = [ljm.constants.FLOAT32 for _ in output_addresses]  # data type

#initializing variables
error = get_error(29)
previous_error = 0
output = 0

#power fntion tu run the power sensor in aother threath 
# for code execution time porpuses
def power_get():
    with concurrent.futures.ThreadPoolExecutor() as executor:
        global power_input
        while(True):
            future = executor.submit(power)
            power_input = future.result()
            time.sleep(5)

t = threading.Thread(target=power_get)
t.daemon = True
t.start()

#power sensor initializaction
power_input = 0

#the loop where all the control is executed
while True:

    #reading the senors input for the hot side
    results_hot = ljm.eReadAddresses(handle, hot_total_addresses, hot_addresses, hot_data_types)

    # seeing the read values of temperature
    print("\nHot sensors reads: ")
    for i in range(hot_total_addresses):
        print("    Address -> %i, value : %f" %
              (hot_addresses[i], results_hot[i]))

    #calculating the hot side sensor average
    temp_average_hot = sum(results_hot [2:] )/(hot_total_addresses-2)

    #reading and calculating the heatflux input
    heatflux_21681 = heat_flux(results_hot[3], -1*results_hot[1], 1.35) 
    heatflux_21680 = heat_flux(results_hot[2], -1*results_hot[0], 1.34)

    #gets the error
    error = get_error(temp_average_hot)
    
    # send the average of the data values to controller code
    #the control start runing afeter 45 degrees celcius to make the heatig quiker
    if temp_average_hot > 45:
        output = get_temp(error,previous_error,output)
    else:
        output = 5

    #saves the previws error so it can be pass to the controller code in the nex iteration
    previous_error = error
    
    #prints all the values for debuggin and vizualitation propuses
    print("Average temperature:", temp_average_hot)
    print("power input:", power_input)
    print("heat_flux_1:", heatflux_21680)
    print("heat_flux_2:", heatflux_21681)

    # write the controller calculate value in the DAC 0 of the Data logger
    output_values = [output]  # [write of output]
    output_tolat_addresses = len(output_addresses)
    ljm.eWriteAddresses(handle, output_tolat_addresses, output_addresses, output_data_types, output_values)

    # print the results of the controller write
    print("\nOutput values ")
    for i in range(output_tolat_addresses):
        print("    Address -> %i, value : %f" %
              (output_addresses[i], output_values[i]))

    #reads the colde side sensors
    results_cold = ljm.eReadAddresses(handle, cold_total_addresses, cold_addresses, cold_data_types)

    # print the read values of the cold side
    print("\nCold sensors reads: ")
    for i in range(cold_total_addresses):
        print("    Address -> %i, value : %f" %
              (cold_addresses[i], results_cold[i]))

    #calculating the cold side sensor average
    temp_average_cold = (results_cold[0]+results_cold[1])/2
    
    #send the read values to calculate the conductivity of the test plate
    condutivity = con_calculation(temp_average_hot, temp_average_cold,((heatflux_21680 + heatflux_21681)/2))
    print("Calculated conductivity:", condutivity)
    
    print("--------------")

    # Exel write data
    data = results_hot[2:] + results_cold 
    time_date = datetime.fromtimestamp(time.time())

    write_data(time_date, data,heatflux_21680,heatflux_21681,power_input,condutivity, file)

    # Repeat every 1 second, in hardware delay
    skippedIntervals = ljm.waitForNextInterval(INTERVAL_HANDLE)
    if skippedIntervals > 0:
        print("\nSkippedIntervals: %s" % skippedIntervals)





