 @echo off
  cd /d D:\SSD\Python\tacada
  set PYTHONUTF8=1
  .venv\Scripts\python.exe -m pygbag --build tacada_web
  xcopy /E /Y /I tacada_web\build\web\* tacada_web\
  cd tacada_web
  git add -A
  git commit -m "Atualiza jogo web"
  git push