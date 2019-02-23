# Distributed with a free-will license.
# Use it any way you want, profit or free, provided it fits in the licenses of its associated works.
# TSL2561
# This code is designed to work with the TSL2561_I2CS I2C Mini Module available from ControlEverything.com.
# https://www.controleverything.com/content/Light?sku=TSL2561_I2CS#tabs-0-product_tabset-2

from stl_tsl2561 import TSL2561

f = TSL2561()
f.calibrate()
ch_res = f.run_singleshot(50,True)


# Output data to screen
print ("[    lux    ]: Full Spectrum\t\t\t Infrared\t\t\tVisible\t\tCalib")
print ("[0x29 center]:",end=" ")
print ("\t\t%d," %ch_res[1][0],end=" ")
print ("\t\t%d," %ch_res[1][1],end=" ")
print ("\t\t%d," %(ch_res[1][0] - ch_res[1][1]),end=" ")
print ("\t\t%d  [lux]" %f.center[f.level])

print ("[0x39 right ]:",end=" ")
print ("\t\t%d, " %ch_res[0][0],end=" ")
print ("\t\t%d, " %ch_res[0][1],end=" ")
print ("\t\t%d, " %(ch_res[0][0] - ch_res[0][1]),end=" ")
print ("\t\t%d  [lux]" %f.right[f.level])

print ("[0x49 left  ]:",end=" ")
print ("\t\t%d, " %ch_res[2][0],end=" ")
print ("\t\t%d, " %ch_res[2][1],end=" ")
print ("\t\t%d, " %(ch_res[2][0] - ch_res[2][1]),end=" ")
print ("\t\t%d  [lux]" %f.left[f.level])

