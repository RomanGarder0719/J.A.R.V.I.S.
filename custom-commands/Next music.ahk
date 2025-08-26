#NoEnv
SendMode Input
SetWorkingDir %A_ScriptDir%

; Если AIMP не запущен — запускаем
Process, Exist, AIMP.exe
If (ErrorLevel = 0)
{
    Run, "C:\Program Files\AIMP\AIMP.exe"
    Sleep, 2000
}

; Теперь отправляем горячую клавишу
Send,m
Return
