$files = @("manual.html", "deal-register.html", "contacts.html", "admin-tips.html", "profile-edit.html")

foreach ($file in $files) {
    $content = Get-Content -Path $file -Raw -Encoding UTF8
    
    $isDarkMode = $content -match '<nav class="bottom-nav dark-mode">'
    $navClass = if ($isDarkMode) { "bottom-nav dark-mode" } else { "bottom-nav" }
    
    $navTemplate = @"
<nav class="$navClass">
    <a href="deal-register.html" class="nav-item">
        <span class="nav-icon">🏠</span>
        <span>일정</span>
    </a>
    <a href="market.html" class="nav-item">
        <span class="nav-icon">📋</span>
        <span>장부</span>
    </a>
    <a href="contacts.html" class="nav-item">
        <span class="nav-icon">👥</span>
        <span>연락처</span>
    </a>
    <a href="manual.html" class="nav-item">
        <span class="nav-icon">📖</span>
        <span>설명서</span>
    </a>
    <a href="profile-edit.html" class="nav-item">
        <span class="nav-icon">👤</span>
        <span>내정보</span>
    </a>
</nav>
"@
    
    # Active 상태 추가
    if ($file -eq "deal-register.html") { $navTemplate = $navTemplate -replace '"deal-register.html" class="nav-item"', '"deal-register.html" class="nav-item active"' }
    if ($file -eq "contacts.html") { $navTemplate = $navTemplate -replace '"contacts.html" class="nav-item"', '"contacts.html" class="nav-item active"' }
    if ($file -eq "manual.html") { $navTemplate = $navTemplate -replace '"manual.html" class="nav-item"', '"manual.html" class="nav-item active"' }
    if ($file -eq "profile-edit.html") { $navTemplate = $navTemplate -replace '"profile-edit.html" class="nav-item"', '"profile-edit.html" class="nav-item active"' }
    
    # 교체 로직
    $content = $content -replace '(?s)<nav class="bottom-nav[^>]*>.*?</nav>', $navTemplate
    Set-Content -Path $file -Value $content -Encoding UTF8
}
