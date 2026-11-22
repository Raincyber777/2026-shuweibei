$ErrorActionPreference = "Stop"
$path = "D:\2026-shuweibei\B题\01_论文\数维杯B题_中文初稿_11图_最新.docx"
$out  = "D:\2026-shuweibei\B题\99_归档\调试脚本\_paper_11fig_check.pdf"
$word = New-Object -ComObject Word.Application
$word.Visible = $false
$word.DisplayAlerts = 0
try {
    $doc = $word.Documents.Open($path, $false, $false)
    $doc.ExportAsFixedFormat($out, 17)
    $doc.Close($false)
    Write-Output ("EXPORTED=" + $out)
} finally {
    $word.Quit()
}
