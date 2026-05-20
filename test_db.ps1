$ErrorActionPreference = 'Stop'
[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
$h = @{
    'apikey' = 'sb_publishable_Y3waCN-Y0LA26BC80eUO-g_Njmuq1Hu'
    'Authorization' = 'Bearer sb_publishable_Y3waCN-Y0LA26BC80eUO-g_Njmuq1Hu'
}
$p = Invoke-RestMethod -Uri 'https://yqolkvmrfvumpwlxjimp.supabase.co/rest/v1/properties?select=*' -Headers $h
$c = Invoke-RestMethod -Uri 'https://yqolkvmrfvumpwlxjimp.supabase.co/rest/v1/clients?select=*' -Headers $h
$prop = $p | Where-Object { $_.deposit -eq 1000 -and $_.monthly_rent -eq 40 } | Select-Object -First 1
$cli = $c | Where-Object { $_.client_phone -eq '010-2940-6428' } | Select-Object -First 1

Write-Output "== PROP =="
$prop | ConvertTo-Json
Write-Output "== CLI =="
$cli | ConvertTo-Json
