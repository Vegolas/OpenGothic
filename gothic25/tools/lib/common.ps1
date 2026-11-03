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
# Pinned KrxImpExp Blender add-on (dev branch), installed by get-krx.ps1 into an own scripts
# directory that Blender gets through BLENDER_USER_SCRIPTS (decisions/0007-zrodla-i-budowanie-animacji-moda.md).
# The hash covers the add-on files as stored in git (Get-TreeSha256, LF line endings).
$KrxCommit  = '5be176c4e87f3a1db209009c06a0b6f1a2293796'
$KrxTreeSha = 'cfb83ecb531ca9700d061bb460c39b9db2ec860dacdb80231ec94e8f297bc114'
$BlenderScriptsDir = Join-Path $ModRoot '.tools\blender-scripts'
$KrxDir = Join-Path $BlenderScriptsDir 'addons\krximpexp'
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

function Resolve-Blender([string]$Override) {
  $exe = $Override
  if(-not $exe) { $exe = $env:G25_BLENDER }
  if(-not $exe) { $exe = Get-Prop (Get-LocalConfig) 'blender' }
  if(-not $exe) {
    throw "Blender is not set. Pass -Blender, set G25_BLENDER, or set blender in gothic25/local.json (Blender 5.2)."
  }
  if(-not (Test-Path $exe -PathType Leaf)) {
    throw "Blender not found: $exe. Fix blender in gothic25/local.json (or G25_BLENDER)."
  }
  return (Resolve-Path $exe).Path
}

# SHA-256 of a directory tree: one "<sha256> <relative/path>" line per file in ordinal order.
# Python bytecode caches and KRX_COMMIT.txt are skipped, so a used add-on keeps its hash.
function Get-TreeSha256([string]$Dir) {
  $root  = (Resolve-Path $Dir).Path.TrimEnd('\')
  $lines = New-Object System.Collections.Generic.List[string]
  foreach($file in Get-ChildItem -LiteralPath $root -Recurse -File -Force) {
    $rel = $file.FullName.Substring($root.Length + 1).Replace('\', '/')
    if($rel -match '(^|/)__pycache__/' -or $rel -eq 'KRX_COMMIT.txt') {
      continue
    }
    $lines.Add((Get-FileHash -Algorithm SHA256 -LiteralPath $file.FullName).Hash.ToLowerInvariant() + ' ' + $rel)
  }
  $sorted = $lines.ToArray()
  [Array]::Sort($sorted, [System.StringComparer]::Ordinal)
  $bytes = $Utf8NoBom.GetBytes(($sorted -join "`n") + "`n")
  $sha   = [System.Security.Cryptography.SHA256]::Create()
  return (($sha.ComputeHash($bytes) | ForEach-Object { $_.ToString('x2') }) -join '')
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
