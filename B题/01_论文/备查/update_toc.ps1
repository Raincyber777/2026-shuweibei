# Update the TOC field in the Chinese draft with Word COM.
# Run after any regeneration of the docx:
#   powershell -NoProfile -ExecutionPolicy Bypass -File update_toc.ps1
$ErrorActionPreference = "Stop"
$path = Join-Path $PSScriptRoot "数维杯B题_中文初稿.docx"
if (-not (Test-Path $path)) { throw "not found: $path" }
$word = New-Object -ComObject Word.Application
$word.Visible = $false
$word.DisplayAlerts = 0
try {
    $doc = $word.Documents.Open($path, $false, $false)
    $doc.Fields.Update() | Out-Null
    foreach ($toc in $doc.TablesOfContents) { $toc.Update() }
    $doc.Save()
    $pages = $doc.ComputeStatistics(2)
    $doc.Close($false)
    Write-Output ("TOC updated; total pages = " + $pages)
} finally {
    $word.Quit()
}
