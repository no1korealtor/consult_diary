$files = @("admin-center.html", "admin-tips.html", "contacts.html", "deal-register.html", "login.html", "manual.html", "market.html", "profile-edit.html")

foreach ($f in $files) {
    if (Test-Path $f) {
        $text = [System.IO.File]::ReadAllText((Join-Path (Get-Location) $f), [System.Text.Encoding]::UTF8)
        $text = $text -replace '<a href="tips-handbook.html"', '<a href="manual.html"'
        $text = $text -replace '(?s)<span class="nav-icon">[📚📖]</span>\s*<span>편람</span>', '<span class="nav-icon">📖</span>`n        <span>매뉴얼</span>'
        [System.IO.File]::WriteAllText((Join-Path (Get-Location) $f), $text, (New-Object System.Text.UTF8Encoding($false)))
    }
}
