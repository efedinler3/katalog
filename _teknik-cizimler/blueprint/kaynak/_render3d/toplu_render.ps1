# Tum urunler: CAD -> STL (radyuslu) -> Blender Cycles ustten render (saydam PNG)
$k = "C:\Users\sefed\Documents\Novibrasyon Katalog\_teknik-cizimler\blueprint\kaynak"
$r = "$k\_render3d"
$bl = "C:\Program Files\Blender Foundation\Blender 5.2\blender.exe"
$log = "$r\toplu_render.log"
# kod, kaplama, saplama
$list = @(
  @("70","black","zinc"), @("75","black","zinc"), @("100","black","zinc"), @("150","black","zinc"), @("200","black","zinc"),
  @("400","alu","brass"), @("450","cast","zinc"), @("500","alu","brass"), @("600","cast","zinc"),
  @("VV1","black","zinc"), @("VV2","black","zinc"), @("VV3","black","zinc"), @("SD150","black","zinc"),
  @("MT1","black","zinc"), @("MT2","black","zinc"), @("MT3","black","zinc")
)
"basla $(Get-Date -Format 'HH:mm:ss')" | Out-File $log -Encoding utf8
foreach ($it in $list) {
  $c, $f, $s = $it
  $out = "$r\ust-$c.png"
  if (Test-Path $out) { "$c zaten var" | Out-File $log -Append -Encoding utf8; continue }
  Push-Location $k
  py render3d_export.py $c 2>&1 | Out-File $log -Append -Encoding utf8
  Pop-Location
  $t0 = Get-Date
  & $bl -b -P "$r\render_blender.py" -- $c $f $s top $out 192 2>&1 | Select-String "YAZILDI|Traceback|Error:" | Out-File $log -Append -Encoding utf8
  "$c bitti {0:N0} sn  $(Get-Date -Format 'HH:mm:ss')" -f ((Get-Date) - $t0).TotalSeconds | Out-File $log -Append -Encoding utf8
}
"hepsi bitti $(Get-Date -Format 'HH:mm:ss')" | Out-File $log -Append -Encoding utf8
