#! /usr/bin/env python3


from Temperatura import temp_calculation
from Temperatura import  heat_flux
from Exel import create_load_workbook
from test_plot import plot_temp
from datetime import datetime
from labjack import ljm
import time

from PI_try_conductivity import control_math 
from kivymd.app import MDApp
from kivy.clock import Clock
from kivy.lang import Builder

from kivy.core.window import Window #You must import this
Window.size = (1280 ,720) #Set it to a tuple with the (width, height) in Pixels


class Hotbox(MDApp):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.screen = Builder.load_file('/home/partenio/Desktop/HOTBOX/kivi.kv')
        
        # custom variables
        self.write_value = 0
        self.TEMP_average_HOT = 0.0
        self.TEMP_average_COLD = 0.0
        self.blank_row = 3
        self.time_constant = time.time()
        self.temp_polt = [] 
        self.execution_time = 60*120  # time for the program to run, change second number to the desire time in minutes.
        # where the values are read, write,

        self.loading_time = 0
        self.plot_time = []

        self.intervalHandle = 1  # sets the properties of the in hardware delay
        ljm.startInterval(self.intervalHandle, 1000000)  # Change the velocity of the readings, every 1000000 that is seconds

        # initialize the PID to control the Temperature
        

        # creating the file name.
        date_time = datetime.fromtimestamp(time.time())
        date_time = str(date_time).replace(':', '-').split('.')[0]
        self.file = f'/home/partenio/Desktop/HOTBOX/Excel/{date_time}.xlsx'
        
        # creating the sheet.
        self.wb, self.sheet = create_load_workbook(self.file)
        self.timer = Clock.schedule_interval(self.run_time, 1)
        self.configuration()
        
    
    def configuration(self):

        self.handle = ljm.openS("ANY", "ANY", "ANY")  # T7 device, Any connection, Any identifier
        info = ljm.getHandleInfo(self.handle)
        print("Opened a LabJack with Device type: %i, Connection type: %i,\n"
            "Serial number: %i, IP address: %s, Port: %i,\nMax bytes per MB: %i" %
            (info[0], info[1], info[2], ljm.numberToIP(info[3]), info[4], info[5]))

        deviceType = info[0]  # saves the dive type

        # configure the A/D values to read the thermocouples in degrees C the to ani0 and ain1 are the voltage values for the heat flux.
        aAddresses = [9004, 9006, 9008, 9010, 9012, 9014, 9016, 9018, 9020, 9022, 9024, 9026,
                    9304, 9306, 9308, 9310, 9312, 9314, 9316, 9318, 9320, 9322, 9324, 9326]  # address to write
        aDataTypes = [ljm.constants.UINT32 for _ in aAddresses]
        aValues = [22, 22, 22, 22, 22, 22, 22, 22, 22, 22, 22, 22,
                1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]  # [values to output]
        numFrames = len(aAddresses)
        ljm.eWriteAddresses(self.handle, numFrames, aAddresses, aDataTypes, aValues)

        # print the results of the the actions before for debugging purposes
        print("\neWriteAddresses: ")
        for i in range(numFrames):
            print("    Address - %i, data type - %i, value : %f" %
                (aAddresses[i], aDataTypes[i], aValues[i]))

    def run_time(self, dt):
    
        self.loading_time += 1
        self.plot_time.append(self.loading_time)

        # set the inputs to read: HOTBOX
        aAddresses = [0, 2, 7004, 7012, 7014, 7018, 7020, 7022, 7024, 7026]  # 6 termocuplas [see addresses in https://labjack.com/support/software/api/modbus/modbus-map]
        aDataTypes = [ljm.constants.FLOAT32 for _ in aAddresses]
        numFrames = len(aAddresses)
        self.results_HOT  = ljm.eReadAddresses(self.handle, numFrames, aAddresses, aDataTypes)

        # seeing the read values of temperature
        print("\neReadAddresses results: ")
        for i in range(numFrames):
            print("    Address - %i, data type - %i, value : %f" %
                (aAddresses[i], aDataTypes[i], self.results_HOT [i]))

        TEMP_average_HOT = sum(self.results_HOT [2:] )/numFrames
        self.temp_polt.append(TEMP_average_HOT)
        self.heatflux_21680 = heat_flux(self.results_HOT [2], self.results_HOT [0], 1.34)
        self.heatflux_21681 = heat_flux(self.results_HOT [3], self.results_HOT [1], 1.35)

        # send the average of the data values to PID calculations
        write_value = control_math(TEMP_average_HOT)
        print("...")
        print("pid working:", write_value)  # Print the value for debugging
        print("heat_flux_1:", self.heatflux_21680)
        print("heat_flux_2:", self.heatflux_21681)

        # write the PID calculate value in the DAC of the Data logger
        aAddresses = [1000, 1002]  # [DAC0]
        aDataTypes = [ljm.constants.FLOAT32 for _ in aAddresses]  # data type
        aValues = [write_value, 5]  # [write of output]
        numFrames = len(aAddresses)
        ljm.eWriteAddresses(self.handle, numFrames, aAddresses, aDataTypes, aValues)

        # print the results of the the actions before
        print("\neWriteAddresses: ")
        for i in range(numFrames):
            print("    Address - %i, data type - %i, value : %f" %
                (aAddresses[i], aDataTypes[i], aValues[i]))

        #set the inputs to read: COLDBOX
        aAddresses = [7020, 7022, 7024, 7026]  # [see addresses in https://labjack.com/support/software/api/modbus/modbus-map]
        aDataTypes = [ljm.constants.FLOAT32 for _ in aAddresses]
        numFrames = len(aAddresses)
        self.results_COLD = ljm.eReadAddresses(self.handle, numFrames, aAddresses, aDataTypes)

        #seeing the read values of temperature
        print("\neReadAddresses results: ")
        for i in range(numFrames):
            print("    Address - %i, data type - %i, value : %f" %
                (aAddresses[i], aDataTypes[i], self.results_COLD[i]))

        TEMP_average_COLD = sum(self.results_COLD)/numFrames

        temp_calculation(TEMP_average_HOT, TEMP_average_COLD)
        TEMP_average_COLD = 0  # reset the variable to rerun the loop
        TEMP_average_HOT = 0  # reset the variable to rerun the loop

        # Repeat every 1 second, in hardware delay
        skippedIntervals = ljm.waitForNextInterval(self.intervalHandle)
        if skippedIntervals > 0:
            print("\nSkippedIntervals: %s" % skippedIntervals)

        time_date = [datetime.fromtimestamp(time.time())]
        # Exel write data
        data = self.results_HOT [2:] + self.results_COLD + time_date
        self.sheet.cell(self.blank_row, 1).value = self.blank_row - 2
        for i, dat in enumerate(data):
            offset = 1 if i > 6 else 0
            self.sheet.cell(self.blank_row, i + offset + 2).value = dat
        #adjusted_width = (len (time_date) + 2) * 1.2
        #sheet.column_dimensions['17'].width = int(adjusted_width)
        self.wb.save(self.file)
        self.blank_row += 1
        
        self.write_values()
        self.bar()
        plot_temp(self.temp_polt, self.plot_time)
        if(self.loading_time > 60):
            while(True):
                pass
        self.screen.ids.plot.source = '/home/partenio/Desktop/HOTBOX/output.png'
        self.screen.ids.plot.reload()


    def write_values(self):

        self.screen.ids.flujo_derecha.text = str(self.heatflux_21680)
        self.screen.ids.flujo_izquierda.text = str(self.heatflux_21681)
        self.screen.ids.flujo_Temp_derecha.text = str(self.results_HOT[2])
        self.screen.ids.flujo_Temp_izquierda.text = str(self.results_HOT [3])

        self.screen.ids.abajo_centro.text = str(self.results_HOT [4])
        self.screen.ids.arriba_centro.text = str(self.results_HOT [5])
        self.screen.ids.abajo_izquierda.text = str(self.results_HOT [6])
        self.screen.ids.arriba_derecha.text = str(self.results_HOT [7])
        #self.screen.ids.abajo_derecha.text = str(self.results_HOT [8])
        #self.screen.ids.arriba_izquierda.text = str(self.results_HOT [9])

        self.screen.ids.Muestra_arriba_calinete.text = str(self.results_HOT [8])
        self.screen.ids.Muestra_abajo_calinete .text = str(self.results_HOT [9])
        self.screen.ids.Muestra_abajo_fria.text = str(self.results_COLD[0])
        self.screen.ids.Muestra_arriba_fria.text = str(self.results_COLD [1])

        self.screen.ids.abajo_centro_frio.text = str(self.results_COLD [2])
        self.screen.ids.arriba_centro_frio.text = str(self.results_COLD [3])
    
    def bar(self,*args):
         
        self.screen.ids.Time_left.value = self.loading_time

    def build(self):
        return self.screen


if __name__ == "__main__":

    Hotbox().run()