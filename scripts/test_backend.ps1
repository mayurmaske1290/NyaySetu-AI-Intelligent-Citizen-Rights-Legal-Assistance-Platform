$ErrorActionPreference = "Stop"
$health = Invoke-RestMethod "http://127.0.0.1:8000/api/health"
$health | ConvertTo-Json -Depth 10

$body = @{
    text = "A traffic police officer stopped me and demanded money without giving a receipt."
    language = "en"
} | ConvertTo-Json

Write-Host "`nTesting /api/analyze/text ..."
try {
    $result = Invoke-RestMethod -Uri "http://127.0.0.1:8000/api/analyze/text" -Method POST -ContentType "application/json; charset=utf-8" -Body $body
    $result | ConvertTo-Json -Depth 20
} catch {
    Write-Host "Backend analysis request failed: $($_.Exception.Message)" -ForegroundColor Red
    throw
}
