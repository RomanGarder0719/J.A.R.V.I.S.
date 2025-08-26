#NoEnv
SendMode Input
SetWorkingDir %A_ScriptDir%

Process, Exist, AIMP.exe
If ErrorLevel = 0
{
    ; AIMP не запущен — запускаем
    Run, "C:\Program Files\AIMP\AIMP.exe" /PLAY
}
Else
{
    ; AIMP уже работает
    ; Можно, например, нажать Play/Pause
    Send, {Media_Play_Pause}
}
Return
