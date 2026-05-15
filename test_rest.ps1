
$dbUrl = "https://clzrbyplzjdrrscctcsl.supabase.co"
$dbKey = "sb_publishable_SqGXeBJseIB_4hjHB6GZ8g_rF_tv11k"

$response = Invoke-RestMethod -Uri "$dbUrl/rest/v1/users?select=*" -Headers @{
    "apikey" = $dbKey
    "Authorization" = "Bearer $dbKey"
}
$response | ConvertTo-Json -Depth 5

