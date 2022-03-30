from Exel import create_load_workbook
from PI_try_conductivity import control_math
from datetime import datetime
from labjack import ljm
import time

date_time = datetime.fromtimestamp(time.time())
date_time = str(date_time).replace(':', '-').split('.')[0]
file = f'/home/partenio/Desktop/HOTBOX/Excel/{date_time}.xlsx'

# creating the sheet.
wb, sheet = create_load_workbook(file)
blank_row = 3

handle = ljm.openS("ANY", "ANY", "ANY")  # T7 device, Any connection, Any identifier
info = ljm.getHandleInfo(handle)
print("Opened a LabJack with Device type: %i, Connection type: %i,\n"
      "Serial number: %i, IP address: %s, Port: %i,\nMax bytes per MB: %i" %
      (info[0], info[1], info[2], ljm.numberToIP(info[3]), info[4], info[5]))

deviceType = info[0]  # saves the dive type
intervalHandle = 1  # sets the properties of the in hardware delay
ljm.startInterval(intervalHandle, 1000000)  # Change the velocity of the readings, every 1000000 that is seconds

aAddresses = [9004, 9006, 9008, 9010, 9012, 9014, 9016, 9018, 9020, 9022, 9024, 9026,
                    9304, 9306, 9308, 9310, 9312, 9314, 9316, 9318, 9320, 9322, 9324, 9326]  # address to write
aDataTypes = [ljm.constants.UINT32 for _ in aAddresses]
aValues = [22, 22, 22, 22, 22, 22, 22, 22, 22, 22, 22, 22,
                1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]  # [values to output]
numFrames = len(aAddresses)
ljm.eWriteAddresses(handle, numFrames, aAddresses, aDataTypes, aValues)

# print the results of the the actions before for debugging purposes
print("\neWriteAddresses: ")
for i in range(numFrames):
    print("    Address - %i, data type - %i, value : %f" %
          (aAddresses[i], aDataTypes[i], aValues[i]))

while(True):

    aAddresses = [7004, 7006, 7008, 7010, 7012]  # 5 termocuplas [see addresses in https://labjack.com/support/software/api/modbus/modbus-map]
    aDataTypes = [ljm.constants.FLOAT32 for _ in aAddresses]
    numFrames = len(aAddresses)
    results_HOT = ljm.eReadAddresses(handle, numFrames, aAddresses, aDataTypes)

    # seeing the read values of temperature
    for i in range(numFrames):
        print(results_HOT[i])
    
    TEMP_average_HOT = sum(results_HOT )/numFrames

    #generte PI values

    write_value = control_math(TEMP_average_HOT)
    print("...")
    print(write_value)
    print("...")
    print(TEMP_average_HOT)
    print("...")

    # write the PID calculate value in the DAC of the Data logger
    
    aAddresses = [1000]  # [DAC0]
    aDataTypes = [ljm.constants.FLOAT32 for _ in aAddresses]  # data type
    aValues = [write_value]  # [write of output]
    numFrames = len(aAddresses)
    ljm.eWriteAddresses(handle, numFrames, aAddresses, aDataTypes, aValues)

    time_date = [datetime.fromtimestamp(time.time())]
    # Exel write data
    data = results_HOT
    sheet.cell(blank_row, 1).value = blank_row - 2
    for i, dat in enumerate(data):
        offset = 1 if i > 6 else 0
        sheet.cell(blank_row, i + offset + 2).value = dat

    wb.save(file)
    blank_row += 1
    skippedIntervals = ljm.waitForNextInterval(intervalHandle)
    if skippedIntervals > 0:
        print("\nSkippedIntervals: %s" % skippedIntervals)
