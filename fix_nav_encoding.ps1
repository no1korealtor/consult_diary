$files = @("tips-handbook.html", "deal-register.html", "contacts.html", "admin-tips.html", "profile-edit.html", "market.html")
$template = Get-Content -Path "nav_template.txt" -Raw -Encoding UTF8

foreach ($file in $files) {
    if (Test-Path $file) {
        $content = Get-Content -Path $file -Raw -Encoding UTF8
        
        $isDarkMode = $content -match '<nav class="bottom-nav dark-mode">'
        $navClass = if ($isDarkMode) { "bottom-nav dark-mode" } else { "bottom-nav" }
        
        $currentNav = $template -replace '<nav class="bottom-nav">', "<nav class=`"$navClass`">"
        
        if ($file -eq "deal-register.html") { $currentNav = $currentNav -replace '"deal-register.html" class="nav-item"', '"deal-register.html" class="nav-item active"' }
        if ($file -eq "contacts.html") { $currentNav = $currentNav -replace '"contacts.html" class="nav-item"', '"contacts.html" class="nav-item active"' }
        if ($file -eq "tips-handbook.html") { $currentNav = $currentNav -replace '"tips-handbook.html" class="nav-item"', '"tips-handbook.html" class="nav-item active"' }
        if ($file -eq "profile-edit.html") { $currentNav = $currentNav -replace '"profile-edit.html" class="nav-item"', '"profile-edit.html" class="nav-item active"' }
        if ($file -eq "market.html") { $currentNav = $currentNav -replace '"market.html" class="nav-item"', '"market.html" class="nav-item active"' }
        
        $content = $content -replace '(?s)<nav class="bottom-nav[^>]*>.*?</nav>', $currentNav
        Set-Content -Path $file -Value $content -Encoding UTF8
    }
}
