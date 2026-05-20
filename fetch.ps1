$ErrorActionPreference = 'Stop'
[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
$wc = New-Object System.Net.WebClient
$wc.Headers.Add('apikey', 'sb_publishable_Y3waCN-Y0LA26BC80eUO-g_Njmuq1Hu')
$wc.Headers.Add('Authorization', 'Bearer sb_publishable_Y3waCN-Y0LA26BC80eUO-g_Njmuq1Hu')

$p_json = $wc.DownloadString('https://yqolkvmrfvumpwlxjimp.supabase.co/rest/v1/properties?select=*&deposit=eq.1000&monthly_rent=eq.40')
$c_json = $wc.DownloadString('https://yqolkvmrfvumpwlxjimp.supabase.co/rest/v1/clients?select=*&client_phone=eq.010-2940-6428')

$p_json | Out-File 'p.json'
$c_json | Out-File 'c.json'
