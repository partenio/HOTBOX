import time

from PI_try_conductivity import control_math 
from Temperatura import temp_calculation
from Exel import create_load_workbook
from Temperatura import  heat_flux
from datetime import datetime
from labjack import ljm

# setting the Datalogger
handle = ljm.openS("ANY", "ANY", "ANY")  # T7 device, Any connection, Any identifier
info = ljm.getHandleInfo(handle)
print("Opened a LabJack with Device type: %i, Connection type: %i,\n"
      "Serial number: %i, IP address: %s, Port: %i,\nMax bytes per MB: %i" %
      (info[0], info[1], info[2], ljm.numberToIP(info[3]), info[4], info[5]))

deviceType = info[0]  # saves the dive type
intervalHandle = 1  # sets the properties of the in hardware delay
ljm.startInterval(intervalHandle, 1000000)  # Change the velocity of the readings, every 1000000 that is seconds

# creating the file name.
date_time = datetime.fromtimestamp(time.time())
date_time = str(date_time).replace(':', '-').split('.')[0]
file = f'/home/partenio/Desktop/HOTBOX/Excel/{date_time}.xlsx'

# creating the sheet.
wb, sheet = create_load_workbook(file)

# configure the A/D values to read the thermocouples in degrees C the to ani0 and ain1 are the voltage values for the heat flux.
aAddresses = [9004, 9006, 9008, 9010, 9012, 9014, 9016, 9018, 9020, 9022, 9024, 9026,
              9304, 9306, 9308, 9310, 9312, 9314, 9316, 9318, 9320, 9322, 9324, 9326]  # address to write 11 cus the to first are voltage reades for the heatflux
aDataTypes = [ljm.constants.UINT32 for _ in aAddresses]
# [setting thermocuples (Thermocuples))]
aValues = [24, 24, 22, 22, 22, 22, 22, 24, 24, 22, 22, 22,
           1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]  
numFrames = len(aAddresses)
ljm.eWriteAddresses(handle, numFrames, aAddresses, aDataTypes, aValues)

# print the results of the the actions before for debugging purposes
print("\neWriteAddresses: ")
for i in range(numFrames):
    print("    Address - %i, data type - %i, value : %f" %
          (aAddresses[i], aDataTypes[i], aValues[i]))

# custom variables
write_value = 0
blank_row = 3
TEMP_average_HOT = 0.0
TEMP_average_COLD = 0.0
time_constant = time.time()
execution_time = 60*300 # time for the program to run, 
#change second number to the desire time in minutes, We recomend of 4.

end = True
write_exel = False

# where the values are read, write, print and calculate

while end:

    # set the inputs to read: HOTBOX
    aAddresses = [0, 2, 7012, 7014,7018,7020, 7022, 7024, 7026]  # 6 termocuplas [see addresses in https://labjack.com/support/software/api/modbus/modbus-map]
    aDataTypes = [ljm.constants.FLOAT32 for _ in aAddresses]
    numFrames = len(aAddresses)
    results_HOT = ljm.eReadAddresses(handle, numFrames, aAddresses, aDataTypes)

    # seeing the read values of temperature
    print("\neReadAddresses results: ")
    for i in range(numFrames):
        pass
        print("    Address - %i, data type - %i, value : %f" %
              (aAddresses[i], aDataTypes[i], results_HOT[i]))

    TEMP_average_HOT = sum(results_HOT [2:] )/(numFrames-2)
    heatflux_21680 = heat_flux(results_HOT[2], -results_HOT[0], 1.34)
    heatflux_21681 = heat_flux(results_HOT[3], -results_HOT[1], 1.35)

    # send the average of the data values to PID calculations
    write_value = control_math(TEMP_average_HOT)
    print("Average:", TEMP_average_HOT)
    print("pid working:", write_value)  # Print the value for debugging
    print("heat_flux_1:", heatflux_21680)
    print("heat_flux_2:", heatflux_21681)

    # write the PID calculate value in the DAC of the Data logger
    aAddresses = [1000, 1002]  # [DAC0]
    aDataTypes = [ljm.constants.FLOAT32 for _ in aAddresses]  # data type
    aValues = [write_value, 5]  # [write of output]
    numFrames = len(aAddresses)
    ljm.eWriteAddresses(handle, numFrames, aAddresses, aDataTypes, aValues)

    # print the results of the the actions before
    print("\neWriteAddresses: ")
    for i in range(numFrames):
        print("    Address - %i, data type - %i, value : %f" %
              (aAddresses[i], aDataTypes[i], aValues[i]))

    # set the inputs to read: COLDBOX
    aAddresses = [7008, 7010, 70016]  # [see addresses in https://labjack.com/support/software/api/modbus/modbus-map]
    aDataTypes = [ljm.constants.FLOAT32 for _ in aAddresses]
    numFrames = len(aAddresses)
    results_COLD = ljm.eReadAddresses(handle, numFrames, aAddresses, aDataTypes)

    # seeing the read values of temperature
    print("\neReadAddresses results: ")
    for i in range(numFrames):
        print("    Address - %i, data type - %i, value : %f" %
              (aAddresses[i], aDataTypes[i], results_COLD[i]))

    TEMP_average_COLD = sum(results_COLD[1:])/numFrames-1

    if write_exel:
        temp_calculation(TEMP_average_HOT, TEMP_average_COLD)
        TEMP_average_COLD = 0  # reset the variable to rerun the loop
        TEMP_average_HOT = 0  # reset the variable to rerun the loop

        print("--------------")

        time_date = [datetime.fromtimestamp(time.time())]
        # Exel write data
        data = results_HOT[2:] + results_COLD + time_date
        sheet.cell(blank_row, 1).value = blank_row - 2
        for i, dat in enumerate(data):
            offset = 1 if i > 6 else 0
            sheet.cell(blank_row, i + offset + 2).value = dat
        adjusted_width = (len (time_date) + 2) * 1.2
        wb.save(file)
        blank_row += 1
    
    # Repeat every 1 second, in hardware delay
    skippedIntervals = ljm.waitForNextInterval(intervalHandle)
    if skippedIntervals > 0:
        print("\nSkippedIntervals: %s" % skippedIntervals)
    
    if TEMP_average_HOT > 49.60:
        t_end = time.time() + execution_time #creating the timmer
        write_exel = True
        if time.time() >= t_end:
            end = False


