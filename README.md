## Control and Data Aquisition scripts for FAST magnetic test stand
Developed by John Wieland, 2024

testStandControlsClass.py is a small python library that will setup and control
the rasperry pi and lakeshore crytronics teslameter of the FAST test stand.
The move\_pt command will make relative movements in x,y,z coordinates in mm.
The take\_data will read hall probe data in gauss.
There is no absolute reference frame or management of hysteresis. 
An example aqusition script is included in example\_scan.py
