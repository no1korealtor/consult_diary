$body = '{"name":"Test User","phone":"01012345678"}'
$key = 'sb_publishable_Y3waCN-Y0LA26BC80eUO-g_Njmuq1Hu'
$headers = @{
    "apikey" = $key
    "Authorization" = "Bearer $key"
    "Content-Type" = "application/json"
    "Prefer" = "return=representation"
}
Invoke-RestMethod -Uri "https://yqolkvmrfvumpwlxjimp.supabase.co/rest/v1/customers" -Method Post -Headers $headers -Body $body
