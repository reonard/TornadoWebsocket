__author__ = 'reonard'


import wmi

proc = wmi.WMI()

for process in proc.Win32_Process(name="QQ.exe"):
    result = process.Terminate()
    print result





