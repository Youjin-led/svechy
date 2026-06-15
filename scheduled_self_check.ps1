<#
.SYNOPSIS
    Авто-запуск full_self_check для проекта ДЗ-1
.DESCRIPTION
    Запускает полную самодиагностику: git статус, GitHub, HuggingFace, npm.
    Результат сохраняется в лог-файл.
#>

param(
    [string]$LogDir = "$PSScriptRoot\logs"
)

# Создаём папку логов если нет
if (-not (Test-Path $LogDir)) {
    New-Item -ItemType Directory -Path $LogDir -Force | Out-Null
}

$timestamp = Get-Date -Format "yyyy-MM-dd_HH-mm-ss"
$logFile = "$LogDir\self_check_$timestamp.log"
$projectDir = "C:\Users\Ардор\OneDrive\Рабочий стол\JS\ДЗ-1"

function Write-Log {
    param([string]$Message)
    $line = "[$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')] $Message"
    Write-Host $line
    Add-Content -Path $logFile -Value $line
}

Write-Log "=== Self-Improvement Check Start ==="
Write-Log "Project: $projectDir"

# 1. Git status
try {
    cd $projectDir
    $gitStatus = git status --short 2>&1
    Write-Log "Git status: OK ($($gitStatus.Count) changes)"
    if ($gitStatus.Count -gt 0) {
        foreach ($line in $gitStatus) {
            Write-Log "  $line"
        }
    }
} catch {
    Write-Log "Git status: ERROR - $_"
}

# 2. GitHub check
try {
    $ghStatus = git fetch origin 2>&1
    $behind = git rev-list --count HEAD..origin/main 2>&1
    $ahead = git rev-list --count origin/main..HEAD 2>&1
    Write-Log "GitHub: OK (behind: $behind, ahead: $ahead)"
} catch {
    Write-Log "GitHub: ERROR - $_"
}

# 3. NPM outdated
try {
    $npmOutdated = npm outdated --json 2>&1
    $npmObj = $npmOutdated | ConvertFrom-Json
    $count = ($npmObj.PSObject.Properties | Measure-Object).Count
    if ($count -eq 0) {
        Write-Log "NPM: OK - all packages up to date"
    } else {
        Write-Log "NPM: $count outdated packages"
        foreach ($pkg in $npmObj.PSObject.Properties) {
            Write-Log "  $($pkg.Name): $($pkg.Value.current) -> $($pkg.Value.latest)"
        }
    }
} catch {
    Write-Log "NPM: ERROR - $_"
}

# 4. HuggingFace check
try {
    $hfDir = "$env:USERPROFILE\.cache\huggingface\hub"
    if (Test-Path $hfDir) {
        $models = Get-ChildItem "$hfDir\models-*" -Directory -ErrorAction SilentlyContinue
        Write-Log "HuggingFace: OK ($($models.Count) cached models)"
    } else {
        Write-Log "HuggingFace: cache not found"
    }
} catch {
    Write-Log "HuggingFace: ERROR - $_"
}

# 5. ChromaDB check
try {
    $chromaDir = "$projectDir\.chroma_db"
    if (Test-Path $chromaDir) {
        $size = (Get-ChildItem $chromaDir -Recurse -File | Measure-Object Length -Sum).Sum
        Write-Log "ChromaDB: OK ($([math]::Round($size/1KB, 1)) KB)"
    } else {
        Write-Log "ChromaDB: not found"
    }
} catch {
    Write-Log "ChromaDB: ERROR - $_"
}

Write-Log "=== Self-Improvement Check Complete ==="
Write-Log "Log saved to: $logFile"
