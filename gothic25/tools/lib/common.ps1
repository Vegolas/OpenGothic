# Shared helpers for gothic25/tools. Dot-source from a tool script:
#   . (Join-Path $PSScriptRoot 'lib/common.ps1')
# Compatible with Windows PowerShell 5.1 and PowerShell 7. Keep this file ASCII-only:
# 5.1 reads BOM-less scripts as ANSI, so non-ASCII text goes through Read-Utf8/Write-Utf8.

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$ModRoot  = (Resolve-Path (Join-Path $PSScriptRoot '..\..')).Path
$RepoRoot = (Resolve-Path (Join-Path $ModRoot '..')).Path
$ModBuild = Join-Path $ModRoot 'build'
# Pinned Daedalus compiler, installed by get-gdc.ps1 (decisions/0001-kompilator-daedalus.md)
$GdcVersion = '0.9.5'
$GdcDir = Join-Path $ModRoot ".tools\gdc-$GdcVersion"
$Utf8NoBom = New-Object System.Text.UTF8Encoding($false)

function Write-Step([string]$Message) {
  Write-Host "==> $Message" -ForegroundColor Cyan
}

function Read-Utf8([string]$Path) {
  return [System.IO.File]::ReadAllText($Path, [System.Text.Encoding]::UTF8)
}

function Write-Utf8([string]$Path, [string]$Text) {
  New-Item -ItemType Directory -Force -Path (Split-Path -Parent $Path) | Out-Null
  [System.IO.File]::WriteAllText($Path, $Text, $Utf8NoBom)
}

function Get-ModManifest {
  return Read-Utf8 (Join-Path $ModRoot 'mod.json') | ConvertFrom-Json
}

function Get-LocalConfig {
  $path = Join-Path $ModRoot 'local.json'
  if(Test-Path $path) {
    return Read-Utf8 $path | ConvertFrom-Json
  }
  return New-Object PSObject
}

# Returns $Object.$Name, or $Default when the property is missing or empty.
function Get-Prop($Object, [string]$Name, $Default = $null) {
  if($null -ne $Object -and $Object.PSObject.Properties[$Name]) {
    $value = $Object.$Name
    if($null -ne $value -and "$value" -ne '') {
      return $value
    }
  }
  return $Default
}

function Resolve-GothicDir([string]$Override) {
  $dir = $Override
  if(-not $dir) { $dir = $env:G25_GOTHIC_DIR }
  if(-not $dir) { $dir = Get-Prop (Get-LocalConfig) 'gothicDir' }
  if(-not $dir) {
    throw "Gothic directory is not set. Pass -GothicDir, set G25_GOTHIC_DIR, or set gothicDir in gothic25/local.json."
  }
  if(-not (Test-Path (Join-Path $dir 'System'))) {
    throw "Not a Gothic directory (no System folder): $dir"
  }
  return (Resolve-Path $dir).Path
}

function Resolve-EngineBuildDir([string]$Override) {
  $dir = $Override
  if(-not $dir) { $dir = Get-Prop (Get-LocalConfig) 'engineBuildDir' }
  if(-not $dir) { $dir = Join-Path $RepoRoot 'build' }
  if(-not [System.IO.Path]::IsPathRooted($dir)) { $dir = Join-Path $RepoRoot $dir }
  return [System.IO.Path]::GetFullPath($dir)
}

function Get-EngineExe([string]$BuildDir) {
  $manifest = Get-ModManifest
  return Join-Path (Join-Path $BuildDir 'opengothic') "$($manifest.engine.target).exe"
}

# Runs a native command and throws when it fails.
function Invoke-Native([string]$Exe, [string[]]$Arguments) {
  & $Exe @Arguments
  if($LASTEXITCODE -ne 0) {
    throw "Command failed with exit code ${LASTEXITCODE}: $Exe $($Arguments -join ' ')"
  }
}

function Invoke-Python([string[]]$Arguments) {
  $python = Get-Prop (Get-LocalConfig) 'python' 'python'
  Invoke-Native $python (@('-I') + $Arguments)
}

# Replaces {{KEY}} placeholders.
function Expand-Template([string]$Text, [hashtable]$Values) {
  foreach($key in $Values.Keys) {
    $Text = $Text.Replace("{{$key}}", [string]$Values[$key])
  }
  return $Text
}

# Mod file layout produced by pack.ps1 and consumed by install.ps1 / publish.ps1.
function Get-ModOutput {
  $manifest = Get-ModManifest
  $game = Join-Path $ModBuild 'game'
  return [pscustomobject]@{
    GameDir = $game
    Archive = Join-Path $game "Data\ModVDF\$($manifest.archive)"
    Ini     = Join-Path $game "System\$($manifest.ini)"
  }
}
