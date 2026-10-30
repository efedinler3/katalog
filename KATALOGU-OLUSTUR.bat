@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo Novibrasyon katalogu olusturuluyor (Turkce ve Ingilizce)...
python build.py
if errorlevel 1 (
  echo.
  echo HATA: Katalog olusturulamadi. Python yuklu mu?
  pause
  exit /b 1
)
echo.
echo Tamam! PDF dosyalari bu klasorde:
echo   TURKCE
echo     Novibrasyon-Katalog-2026-TR.pdf                  (ekran / ofis yazicisi)
echo     Novibrasyon-Katalog-2026-TR-BASKI-3mm-tasma.pdf  (matbaa, 3 mm tasma payli)
echo     Novibrasyon-Katalog-2026-TR-eposta.pdf           (e-posta / WhatsApp, kucuk dosya)
echo   INGILIZCE
echo     Novibrasyon-Catalogue-2026-EN.pdf
echo     Novibrasyon-Catalogue-2026-EN-PRINT-3mm-bleed.pdf
echo     Novibrasyon-Catalogue-2026-EN-email.pdf
echo   MOBIL (telefon)
echo     Novibrasyon-Katalog-2026-TR-mobil.pdf
echo     Novibrasyon-Catalogue-2026-EN-mobile.pdf
pause
