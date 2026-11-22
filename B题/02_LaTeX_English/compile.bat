@echo off
cd /d "%~dp0"
echo ============================================
echo  Compiling main.tex with pdfLaTeX (2 passes)
echo ============================================
pdflatex -interaction=nonstopmode -halt-on-error main.tex
if errorlevel 1 goto fail
pdflatex -interaction=nonstopmode -halt-on-error main.tex
if errorlevel 1 goto fail
echo.
echo Done: main.pdf
pause
exit /b 0

:fail
echo.
echo Compilation failed. See main.log for details.
pause
exit /b 1
