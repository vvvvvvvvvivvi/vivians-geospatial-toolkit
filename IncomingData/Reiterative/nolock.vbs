Set objShell =
WScript.CreateObject("WScript.Shell")
Do While True
    objShell.sendkeys "{NUMLOCK}{NUMLOCK}"
    WScript.Sleep 30000
    Loop    