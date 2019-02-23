# Distributed with a free-will license.
# Use it any way you want, profit or free, provided it fits in the licenses of its associated works.
# TSL2561
# This code is designed to work with the TSL2561_I2CS I2C Mini Module available from ControlEverything.com.
# https://www.controleverything.com/content/Light?sku=TSL2561_I2CS#tabs-0-product_tabset-2

import smbus
import time
import os
import RPi.GPIO as GPIO
from statistics import mean

# ADDRESS RESISTER NAME REGISTER FUNCTION
# −− COMMAND Specifies register address 
#       FIELD BIT DESCRIPTION
#       CMD   7  Select command register. Must write as 1.
#       CLEAR 6  Interrupt clear. Clears any pending interrupt. This bit is a write-one-to-clear bit. It is self clearing.
#       WORD  5  SMB Write/Read Word Protocol. 1 indicates that this SMB transaction is using either the SMB Write Word or
#                Read Word protocol.
#       BLOCK 4  Block Write/Read Protocol. 1 indicates that this transaction is using either the Block Write or the Block Read
#                protocol. 
#       ADDR 3:0 Register Address. This field selects the specific control or status register for following write and read
#                commands according to Table 2.
# 0h CONTROL Control of basic functions
#       FIELD BIT DESCRIPTION
#       Resv 7:2    Reserved. Write as 0.
#       POWER 1:0   Power up/power down. By writing a 03h to this register, the device is powered up. By writing a 00h to this
#                   register, the device is powered down.
#                   NOTE: If a value of 03h is written, the value returned during a read cycle will be 03   
# 1h TIMING Integration time/gain control
#       FIELD BIT DESCRIPTION
#       Resv 7−5    Reserved. Write as 0.
#       GAIN 4      Switches gain between low gain and high gain modes. Writing a 0 selects low gain (1×); writing a 1 selects
#                   high gain (16×).
#       Manual 3    Manual timing control. Writing a 1 begins an integration cycle. Writing a 0 stops an integration cycle.
#                   NOTE: This field only has meaning when INTEG = 11. It is ignored at all other times.
#       Resv 2      Reserved. Write as 0.
#       INTEG 1:0 Integrate time. This field selects the integration time for each conversion.
#
#       INTEG FIELD VALUE - SCALE - NOMINAL INTEGRATION TIME
#           00              0.034           13.7 ms
#           01              0.252           101 ms
#           10              1               402 ms
#           11              −−              N/A
# 2h THRESHLOWLOW Low byte of low interrupt threshold
# 3h THRESHLOWHIGH High byte of low interrupt threshold
# 4h THRESHHIGHLOW Low byte of high interrupt threshold
# 5h THRESHHIGHHIGH High byte of high interrupt threshold
# 6h INTERRUPT Interrupt control
# 7h −− Reserved
# 8h CRC Factory test — not a user register
# 9h −− Reserved
# Ah ID Part number/ Rev ID
# Bh −− Reserved
# Ch DATA0LOW Low byte of ADC channel 0
# Dh DATA0HIGH High byte of ADC channel 0
# Eh DATA1LOW Low byte of ADC channel 1
# Fh DATA1HIGH High byte of ADC channel 1

# setup commands in registers
TSL2561_Timing_Cmd_Manual_Integration_Start = 0x0B
TSL2561_Timing_Cmd_Manual_Integration_Stop = 0x03
TSL2561_Timing_Cmd_Manual_Integration_Gain = 0x10
TSL2561_Command_Reg = 0x80
TSL2561_Control_Reg = 0x00
TSL2561_Control_Power_ON = 0x03
TSL2561_Control_Power_OFF = 0x00
TSL2561_Timing_Reg    = 0x01
TSL2561_Interrupt_Reg = 0x06
TSL2561_Channel0L_Reg = 0x0C
TSL2561_Channel0H_Reg = 0x0D
TSL2561_Channel1L_Reg = 0x0E
TSL2561_Channel1H_Reg = 0x0F

debug = True

tsl2561_parfile = "//tmp//tsl2561.par"

class TSL2561:

    addr, valid, level = range(3)    # index to canter,right,left lists
    full_spectrum, infrared = range(2)    # index to result from lux readings
    r, c, l, rc, lc, rlc = range(6) # left,center,right index to result from lux readings
    right_dir = 0x1
    center_dir = 0x2
    left_dir = 0x4 
    #TSL2561 sensor mapped - valid is False if not found
    center = [0x39,True,0] # address,valid,calib_level
    right  = [0x29,True,0]
    left   = [0x49,True,0]
    # calibration level - sensors will have diofferent white peak levels
    calibration_time_default = 30
    calibration_delta_sleep = 500
    calibration_integration_time = 50
    busy_time = 0.005

    # Must be called as the first before calling calibrate and run.
    def __init__(self):
        # to use curses lib then term must be set in the environment
        os.environ["TERM"] = "linux"
        os.environ["TERMINFO"] = "/etc/terminfo"
        if debug:
            print(GPIO.RPI_INFO)
        bus_rev = GPIO.RPI_REVISION       
        if bus_rev == 2 or bus_rev == 3:
            self.bus = smbus.SMBus(1)
        else:
            self.bus = smbus.SMBus(0)
        # set GPIO numbering system to count pins from 1-40 from top to bottom
        GPIO.setmode(GPIO.BOARD)
        # TSL2561 address, 0x29,0x39,0x49
        # Select control register, 0x00(00) with command register, 0x80(128)
        #       0x03(03)    Power ON mode
        try:
            self.bus.write_byte_data(self.right[self.addr], TSL2561_Command_Reg | TSL2561_Control_Reg, TSL2561_Control_Power_ON)
        except:
            self.right[self.valid] = False
        try:    
            self.bus.write_byte_data(self.center[self.addr], TSL2561_Command_Reg | TSL2561_Control_Reg, TSL2561_Control_Power_ON)
        except:
            self.center[self.valid] = False
        try:    
            self.bus.write_byte_data(self.left[self.addr], TSL2561_Command_Reg | TSL2561_Control_Reg, TSL2561_Control_Power_ON)
        except:
            self.left[self.valid] = False
        # open parameter file and read calibration levels
        try:
            if os.path.exists(tsl2561_parfile):
                with open(tsl2561_parfile, "r") as f:
                    sensor = 0
                    for line in f:
                        if sensor == self.r:
                            self.right[self.level] = int(line.strip())
                        if sensor == self.c:
                            self.center[self.level] = int(line.strip())
                        if sensor == self.l:
                            self.left[self.level] = int(line.strip())
                        sensor += 1
                    if debug:
                        print("TSL2561 Calib levels: Right: %02d, Center: %02d, Left: %02d" % (self.right[self.level],self.center[self.level],self.left[self.level]))
        except IOError:
            print("Read of Calibration values failed - File not found or path is incorrect %s" % tsl2561_parfile)
   

    # Deleting (Calling destructor) 
    def __del__(self):
        self.powerdown(self.right[self.addr])
        self.powerdown(self.center[self.addr])
        self.powerdown(self.left[self.addr])
        self.bus.close()
     
    # Read TSL2561 register - multiple reads  of bytes
    # @param address is the I2C address of sensor
    # @param command is a TSL2561 command
    # @param bytes is the number of bytes to read at once
    # @return a list of read values
    def read_reg(self,address, command, bytes):
        try:
            ret_data = [] # type: List[int]
            ret_data = self.bus.read_i2c_block_data(address, command, bytes)
            if (debug):
                print("TSL2561.read_reg: data1 0x%02X from reg 0x%02X" % (ret_data[0], address))
        except IOError:
            print("TSL2561.read_reg: error reading bytes from reg 0x%02X" % address)
            ret_data[0] = 0
            time.sleep(2*float(self.busy_time))
        return ret_data

    # Write to TSL2561 register - one byte
    # @param address is the I2C address of sensor
    # @param command is a TSL2561 command
    # @param val is written to register
    # @retval 0 when operation went well otherwise fail
    def write_reg(self,address, command, val):
        ret = 0
        try:
            self.bus.write_byte_data(address, command, val)
            if (debug):
                print("TSL2561.write_reg: wrote 0x%02X to reg 0x%02X" % (val, address))
        except IOError:
            print("TSL2561.write_reg: error writing 0x%02X to reg 0x%02X" % (val, address))
            time.sleep(2*float(self.busy_time))
            ret = -1
        return ret

    # Power up the TSL2561 sensor
    # @param address is the I2C address of sensor
    def powerup(self,address):
        self.bus.write_byte_data(address, TSL2561_Command_Reg | TSL2561_Control_Reg, TSL2561_Control_Power_ON)

    # Power down the TSL2561 sensor
    # @param address is the I2C address of sensor
    def powerdown(self,address):
        self.bus.write_byte_data(address, TSL2561_Command_Reg | TSL2561_Control_Reg, TSL2561_Control_Power_OFF)

    # Reads LUX from both low and high channel in two bytes read
    # @param address is the I2C address of sensor
    def read_lux(self,address):
        ch0 = self.read_reg( address,  TSL2561_Command_Reg | TSL2561_Channel0L_Reg, 2)
        ch1 = self.read_reg( address,  TSL2561_Command_Reg | TSL2561_Channel1L_Reg, 2)
        channel0 = (ch0[1]<<8) | ch0[0]  # full spectrum
        channel1 = (ch1[1]<<8) | ch1[0]  # infrared
        if debug:
            print("TSL2561.readVisibleLux: %x - channel 0 = %i, channel 1 = %i " % (address, channel0, channel1))
        return [channel0,channel1]

    # Capture LUX values for all sensors with manual integration.
    # @param integration_time_in_sec defines integrattion time in msec. Float. ex. 50 msec
    # @param enable_gain boolean flag to enable gain of 16 (True) or 1 (False)
    # @return a 3*2-value array of (full spectrum, infrared) values for all 3 sensors
    def run_singleshot(self,integration_time_in_ms, enable_gain):
        # Get I2C bus
        self.bus = smbus.SMBus(1)
        # Select timing register, 0x01(01) with command register, 0x80(128)
        #       0x10(16) Gain=16, Manual integration time = xx ms  = 0x03
        if enable_gain:
            gain = TSL2561_Timing_Cmd_Manual_Integration_Gain 
        else:
            gain = 0
        if integration_time_in_ms > (2*1000*self.busy_time):
            # start integration
            self.write_reg(self.right[self.addr],TSL2561_Command_Reg | TSL2561_Timing_Reg, TSL2561_Timing_Cmd_Manual_Integration_Start | gain)
            time.sleep(float(self.busy_time))
            self.write_reg(self.center[self.addr],TSL2561_Command_Reg | TSL2561_Timing_Reg, TSL2561_Timing_Cmd_Manual_Integration_Start | gain)
            time.sleep(float(self.busy_time))
            self.write_reg(self.left[self.addr],TSL2561_Command_Reg | TSL2561_Timing_Reg, TSL2561_Timing_Cmd_Manual_Integration_Start | gain)
            # sleep integration_time_in_sec - integration time
            time.sleep(float(integration_time_in_ms+1-2*float(self.busy_time))/1000)
             #Stop integrating
            self.write_reg(self.right[self.addr],TSL2561_Command_Reg | TSL2561_Timing_Reg, TSL2561_Timing_Cmd_Manual_Integration_Stop | gain)
            time.sleep(float(self.busy_time))
            self.write_reg(self.center[self.addr],TSL2561_Command_Reg | TSL2561_Timing_Reg, TSL2561_Timing_Cmd_Manual_Integration_Stop | gain)
            time.sleep(float(self.busy_time))
            self.write_reg(self.left[self.addr],TSL2561_Command_Reg | TSL2561_Timing_Reg, TSL2561_Timing_Cmd_Manual_Integration_Stop | gain)
            time.sleep(float(self.busy_time))
            left_value = self.read_lux(self.right[self.addr])
            time.sleep(float(self.busy_time))
            center_value = self.read_lux(self.center[self.addr])
            time.sleep(float(self.busy_time))
            right_value = self.read_lux(self.left[self.addr])
            return [left_value,center_value,right_value]
        else:
            return [[0,0],[0,0],[0,0]]

    # Remove the smallest value(s) from a list
    # @param lst is the list
    # @param n is the number of smallest values to be removed
    # @return a reduced list with the smallest numbers removed
    def remove_n_smallest_from_lst(self,lst,n):
        for _ in range(n):
            m = min(lst)
            lst[:] = (x for x in lst if x != m)

    # @brief assign white peak level to sensor
    # every measurement on sensor values must be based on
    # diffentiated values of the sensor
    # @param calibration_time defines ow long we loop for white peak value
    def calibrate(self, calibration_time=None):
        print("Calibrating...\n")
        time.sleep(5)
        calibration_timeout = self.calibration_time_default
        if calibration_time:
            calibration_timeout = calibration_time 
        r_list, c_list, l_list=([] for i in range(3))
        start_time = time.time()
        while True:
            ch_res = self.run_singleshot(self.calibration_integration_time,True)
            r_list.append(ch_res[self.r][self.full_spectrum])
            c_list.append(ch_res[self.c][self.full_spectrum])
            l_list.append(ch_res[self.l][self.full_spectrum])
            time.sleep((float)(self.calibration_delta_sleep+1)/1000) # sleep for x milliseconds - release cpu
            if (time.time()- start_time) > calibration_timeout:
                break
        self.remove_n_smallest_from_lst( r_list, int(len(r_list)/2))
        self.remove_n_smallest_from_lst( c_list, int(len(c_list)/2))
        self.remove_n_smallest_from_lst( l_list, int(len(l_list)/2))
        self.right[self.level] = int(mean(r_list))
        self.center[self.level] = int(mean(c_list))
        self.left[self.level] = int(mean(l_list))
        try:
            with open(tsl2561_parfile, "w") as f:
                f.write(str(self.right[self.level]) +"\n")
                f.write(str(self.center[self.level]) +"\n")
                f.write(str(self.left[self.level]) +"\n")
        except IOError:
            print("Not able to write to file %s" % tsl2561_parfile)
    
    # select which direction to go
    # return right_dir,left_dir,center_dir
    def select_direction(self):
        selector = 0
        if self.right[self.level] != 0 and self.left[self.level] != 0 or self.center[self.level] != 0:
            ch_res = self.run_singleshot(self.calibration_integration_time,True)
            if ch_res[self.r][self.full_spectrum] > self.right[self.level]:
                selector |= self.right_dir
            if ch_res[self.c][self.full_spectrum] > self.center[self.level]:
                selector |= self.center_dir
            if ch_res[self.l][self.full_spectrum] > self.left[self.level]:
                selector |= self.left_dir
        else:
            print("Calibration is missing !!!")
        return selector


    