<#
.SYNOPSIS
  Runs a test scenario in the game and reports the result (spec 003, gothic25/tests/README.md).
.DESCRIPTION
  Packs the mod from the repository (skipped with -NoMod) and starts the engine from
  gothic25/build/test/profile, so settings, saves and logs stay apart from normal play and the game
  folder is not touched. Every run gets its own directory in gothic25/build/test-runs with a copy of
  the scenario, meta.json, scenario.json, fightlog.jsonl, screenshots, the game log and report.md.

  Automatic mode (default): 800x600 window, the game quits after the scenario, real time limit from
  -TimeoutSec or the "# timeout:" header (600 s otherwise). -Manual keeps the game open with the
  usual window and waits until it is closed.

  Exit code 0 when the scenario ended with ok and all its expectations passed.
.EXAMPLE
  tools/test.ps1 -Scenario 001/K1-pal230
  tools/test.ps1 -Scenario 001/K1-pal230 -NoMod
  tools/test.ps1 -Scenario 001/K9-load -Save gothic25/build/testsaves/001-K9-v0.1.0-pal230.sav
  tools/test.ps1 -Scenario dev/start -Manual
#>
param(
  [Parameter(Mandatory = $true)]
  [string]$Scenario,
  [switch]$NoMod,
  [string]$Save,
  [switch]$Manual,
  [switch]$Window,
  [int]$TimeoutSec = 0,
  [string]$GothicDir,
  [string]$BuildDir
)

. (Join-Path $PSScriptRoot 'lib/common.ps1')

$TestsRoot = Join-Path $ModRoot 'tests'

function Resolve-Scenario([string]$Name) {
  if(Test-Path $Name -PathType Leaf) {
    return (Resolve-Path $Name).Path
  }
  foreach($candidate in @((Join-Path $TestsRoot $Name), (Join-Path $TestsRoot "$Name.txt"))) {
    if(Test-Path $candidate -PathType Leaf) {
      return (Resolve-Path $candidate).Path
    }
  }
  throw "Scenario not found: $Name (looked in $TestsRoot)"
}

# 001\K1-pal230.txt in gothic25/tests -> 001-K1-pal230, other files -> their base name
function Get-RunName([string]$Path) {
  $base = [System.IO.Path]::GetFileNameWithoutExtension($Path)
  $root = $TestsRoot.TrimEnd('\') + '\'
  if($Path.StartsWith($root, [System.StringComparison]::OrdinalIgnoreCase)) {
    $rel = $Path.Substring($root.Length)
    $dir = Split-Path -Parent $rel
    if($dir) {
      return ($dir -replace '[\\/]', '-') + "-$base"
    }
  }
  return $base
}

function Get-HeaderTimeout([string]$Path) {
  foreach($line in [System.IO.File]::ReadAllLines($Path)) {
    if($line -match '^\s*#\s*timeout:\s*(\d+)') {
      return [int]$Matches[1]
    }
  }
  return 0
}

# Sets Key=Value in [Section] of ini lines, adding the key or the section when missing.
function Set-IniValue([string[]]$Lines, [string]$Section, [string]$Key, [string]$Value) {
  $out       = New-Object System.Collections.Generic.List[string]
  $inSection = $false
  $found     = $false
  $done      = $false
  foreach($line in $Lines) {
    if($line -match '^\s*\[(.+)\]\s*$') {
      if($inSection -and -not $done) {
        $out.Add("$Key=$Value")
        $done = $true
      }
      $inSection = ($Matches[1].Trim() -eq $Section)
      if($inSection) { $found = $true }
      $out.Add($line)
      continue
    }
    if($inSection -and $line -match ('^\s*' + [regex]::Escape($Key) + '\s*=')) {
      if(-not $done) {
        $out.Add("$Key=$Value")
        $done = $true
      }
      continue
    }
    $out.Add($line)
  }
  if($inSection -and -not $done) {
    $out.Add("$Key=$Value")
    $done = $true
  }
  if(-not $found) {
    $out.Add("[$Section]")
    $out.Add("$Key=$Value")
  }
  return $out.ToArray()
}

function Get-GitState {
  $commit = 'unknown'
  $dirty  = $null
  try {
    $commit = (& git -C $RepoRoot rev-parse HEAD 2>$null)
    $status = @(& git -C $RepoRoot status --porcelain 2>$null)
    $dirty  = ($status.Count -gt 0)
  } catch {
    $commit = 'unknown'
  }
  return [pscustomobject]@{ Commit = "$commit".Trim(); Dirty = $dirty }
}

$gothic       = Resolve-GothicDir $GothicDir
$exe          = Get-EngineExe (Resolve-EngineBuildDir $BuildDir)
$scenarioPath = Resolve-Scenario $Scenario
if(-not (Test-Path $exe)) {
  throw "Engine not found: $exe. Run tools/build-engine.ps1 first."
}
$savePath = $null
if($Save) {
  if(-not (Test-Path $Save -PathType Leaf)) {
    throw "Save file not found: $Save"
  }
  $savePath = (Resolve-Path $Save).Path
}

# mod from the repository, including uncommitted changes; compiler warnings stay out of the test
# output, errors still stop the script
if(-not $NoMod) {
  & (Join-Path $PSScriptRoot 'build-scripts.ps1') -GothicDir $gothic | Out-Null
  & (Join-Path $PSScriptRoot 'pack.ps1') | Out-Null
}
$output = Get-ModOutput

# profile: the working directory of the game, apart from normal play
$profileDir = Join-Path $ModBuild 'test\profile'
New-Item -ItemType Directory -Force -Path $profileDir | Out-Null
$userIni = Join-Path (Split-Path -Parent $exe) 'Gothic.ini'
$iniLines = @()
if(Test-Path $userIni) {
  $iniLines = [System.IO.File]::ReadAllLines($userIni, [System.Text.Encoding]::Default)
}
$iniLines = Set-IniValue $iniLines 'GAME' 'scaleVideos' '-1'
[System.IO.File]::WriteAllLines((Join-Path $profileDir 'Gothic.ini'), $iniLines, [System.Text.Encoding]::Default)
foreach($file in @('log.txt', 'crash.log')) {
  $path = Join-Path $profileDir $file
  if(Test-Path $path) { Remove-Item $path -Force }
}

# run directory
$runName = Get-RunName $scenarioPath
if($NoMod) { $runName += '-nomod' }
$runDir = Join-Path $ModBuild ("test-runs\" + (Get-Date -Format 'yyyyMMdd-HHmmss') + "-$runName")
New-Item -ItemType Directory -Force -Path $runDir | Out-Null
$scenarioCopy = Join-Path $runDir 'scenario.txt'
Copy-Item $scenarioPath $scenarioCopy

$arguments = @('-g', $gothic, '-devmode')
if(-not $NoMod) { $arguments += "-game:$($output.Ini)" }
if($savePath) {
  $arguments += @('-save', $savePath)
} else {
  $arguments += '-nomenu'
}
$arguments += @('-scenario', $scenarioCopy, '-results', $runDir)
if($Manual) {
  if($Window) { $arguments += '-window' }
} else {
  $arguments += @('-window', 'small', '-scenario-exit')
}

if($TimeoutSec -le 0) { $TimeoutSec = Get-HeaderTimeout $scenarioPath }
if($TimeoutSec -le 0) { $TimeoutSec = 600 }

$git = Get-GitState
Write-Utf8 (Join-Path $runDir 'meta.json') (([ordered]@{
  scenario  = $scenarioPath
  mod       = (-not $NoMod)
  save      = $savePath
  manual    = [bool]$Manual
  commit    = $git.Commit
  dirty     = $git.Dirty
  started   = (Get-Date -Format 'yyyy-MM-ddTHH:mm:ss')
  timeout   = $(if($Manual) { $null } else { $TimeoutSec })
  arguments = $arguments
}) | ConvertTo-Json)

# Start-Process joins arguments with spaces, so quote the ones that contain spaces.
$argLine = ($arguments | ForEach-Object { if($_ -match '\s') { '"' + $_ + '"' } else { $_ } }) -join ' '
Write-Step "Run directory: $runDir"
Write-Step "$exe $argLine"
$process  = Start-Process -FilePath $exe -ArgumentList $argLine -WorkingDirectory $profileDir -PassThru
$timedOut = $false
if($Manual) {
  $process.WaitForExit()
} elseif(-not $process.WaitForExit($TimeoutSec * 1000)) {
  $process.Kill()
  $process.WaitForExit()
  $timedOut = $true
}

foreach($file in @('log.txt', 'crash.log')) {
  $path = Join-Path $profileDir $file
  if(Test-Path $path) { Copy-Item $path (Join-Path $runDir $file) }
}

$failures = @()
if($timedOut) {
  $failures += "time limit of $TimeoutSec s reached, the game was closed"
}
$statusFile = Join-Path $runDir 'scenario.json'
if(-not (Test-Path $statusFile)) {
  $failures += 'no scenario.json: the game ended before the scenario was loaded'
} else {
  $status = Read-Utf8 $statusFile | ConvertFrom-Json
  if($status.result -eq 'running') {
    $failures += 'the game ended during the scenario (see log.txt and crash.log)'
  }
}

$checkCode = 1
if(Test-Path (Join-Path $runDir 'fightlog.jsonl')) {
  $python = Get-Prop (Get-LocalConfig) 'python' 'python'
  & $python -I (Join-Path $PSScriptRoot 'fightlog.py') check $runDir --scenario $scenarioCopy
  $checkCode = $LASTEXITCODE
} else {
  $failures += 'no fightlog.jsonl'
}
if($checkCode -ne 0 -and $failures.Count -eq 0) {
  $failures += 'expectations or scenario failed (see report.md)'
}

if($failures.Count -eq 0) {
  Write-Step "PASSED: $runDir"
  exit 0
}
foreach($f in $failures) {
  Write-Host "FAILED: $f" -ForegroundColor Red
}
Write-Host "Results: $runDir" -ForegroundColor Red
exit 1
