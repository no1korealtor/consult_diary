$files = Get-ChildItem -Path 'd:\부동산업무\antigravity\consult_diary' -Include *.html, *.js -Recurse -File | Where-Object { $_.FullName -notmatch '\\api\\' -and $_.FullName -notmatch '\\ediary\\' -and $_.FullName -notmatch '\\.git\\' }

foreach ($file in $files) {
    $content = Get-Content -Path $file.FullName -Raw
    if ($null -eq $content) { continue }
    $new_content = $content

    $new_content = [regex]::Replace($new_content, "\.eq\(\s*['""]user_id['""]\s*,\s*window\.currentUser\.id\s*\)", ".eq('office_id', window.currentUser.office_id)")
    
    $new_content = [regex]::Replace($new_content, "user_id\s*:\s*window\.currentUser\.id(?!, office_id)", "user_id: window.currentUser.id, office_id: window.currentUser.office_id")
    
    $new_content = [regex]::Replace($new_content, "const isMine = (.*?) === window\.currentUser\.id;", "const isMine = `$1 === window.currentUser.id || window.currentUser.role === 'broker';")

    if ($new_content -cne $content) {
        [IO.File]::WriteAllText($file.FullName, $new_content, [System.Text.Encoding]::UTF8)
        Write-Output "Updated $($file.FullName)"
    }
}
