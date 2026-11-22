$ErrorActionPreference = "Stop"
$path = "D:\2026-shuweibei\B题\01_论文\数维杯B题_中文初稿_11图_最新.docx"
$word = New-Object -ComObject Word.Application
$word.Visible = $false
$word.DisplayAlerts = 0
try {
    $doc = $word.Documents.Open($path, $false, $false)
    $doc.Fields.Update() | Out-Null
    foreach ($toc in $doc.TablesOfContents) { $toc.Update() }
    $doc.Save()
    $pages = $doc.ComputeStatistics(2)
    $appendixPage = -1
    foreach ($p in $doc.Paragraphs) {
        $t = $p.Range.Text.Trim()
        if ($t -eq "附录") {
            $appendixPage = $p.Range.Information(3)
            break
        }
    }
    Write-Output ("TOTAL_PAGES=" + $pages)
    Write-Output ("APPENDIX_PAGE=" + $appendixPage)
    $doc.Close($false)
} finally {
    $word.Quit()
}
