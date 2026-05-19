$Url = "https://yqolkvmrfvumpwlxjimp.supabase.co/rest/v1/users?select=id,name,phone,office_address,role,user_groups(group_id,status,group_role,groups(name))&order=name"
$Headers = @{
    "apikey" = "sb_publishable_Y3waCN-Y0LA26BC80eUO-g_Njmuq1Hu"
    "Authorization" = "Bearer sb_publishable_Y3waCN-Y0LA26BC80eUO-g_Njmuq1Hu"
}

try {
    $Response = Invoke-RestMethod -Uri $Url -Headers $Headers -Method Get
    Write-Host "Success! Count: $($Response.Count)"
} catch {
    Write-Host "Error: $($_.Exception.Message)"
    if ($_.ErrorDetails) {
        Write-Host "Details: $($_.ErrorDetails.Message)"
    }
}
