REM External call from Mapmaker to kill zombie instances of MapMaker
REM This will effectively close all running zombies

taskkill /im python.exe /F
taskkill /im wsl.exe /F
