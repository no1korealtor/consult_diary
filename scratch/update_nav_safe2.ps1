$files = @("admin-center.html", "admin-tips.html", "contacts.html", "deal-register.html", "login.html", "manual.html", "market.html", "profile-edit.html", "nav_template.txt", "update_nav.ps1")

foreach ($f in $files) {
    if (Test-Path $f) {
        $text = [System.IO.File]::ReadAllText((Join-Path (Get-Location) $f), [System.Text.Encoding]::UTF8)
        $text = $text -replace '<a href="tips-handbook.html"', '<a href="manual.html"'
        $text = $text -replace '<span>편람</span>', '<span>매뉴얼</span>'
        $text = $text -replace '<span class="nav-icon">📚</span>', '<span class="nav-icon">📖</span>'
        [System.IO.File]::WriteAllText((Join-Path (Get-Location) $f), $text, (New-Object System.Text.UTF8Encoding($false)))
    }
}
