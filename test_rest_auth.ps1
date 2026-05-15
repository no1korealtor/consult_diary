
$authUrl = "https://yqolkvmrfvumpwlxjimp.supabase.co"
$authKey = "sb_publishable_Y3waCN-Y0LA26BC80eUO-g_Njmuq1Hu"

$response = Invoke-RestMethod -Uri "$authUrl/rest/v1/users?select=*" -Headers @{
    "apikey" = $authKey
    "Authorization" = "Bearer $authKey"
}
Write-Host "TYPE:" $response.GetType()
Write-Host "LENGTH:" $response.Length

