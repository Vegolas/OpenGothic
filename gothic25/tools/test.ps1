<#
.SYNOPSIS
  Runs test scenarios in the game and reports the result (spec 003, gothic25/tests/README.md).
.DESCRIPTION
  Packs the mod from the repository (skipped with -NoMod) and starts the engine from
  gothic25/build/test/profile, so settings, saves and logs stay apart from normal play and the game
  folder is not touched. Every run gets its own directory in gothic25/build/test-runs with a copy of
  the scenario, meta.json, scenario.json, fightlog.jsonl, screenshots, the game log and report.md.

  -Scenario runs one scenario, -Spec NNN runs every gothic25/tests/NNN/*.txt in name order and
  prints a summary. Scenario headers: "# timeout: <s>" (real time limit, 600 s otherwise),
  "# save: <file>" (load this save, path relative to gothic25/), "# mod: off" (run without the mod).

  Automatic mode (default): 800x600 window, the game quits after the scenario. -Manual (with
  -Scenario only) keeps the game open with the usual window and waits until it is closed.

  Exit code 0 when every scenario ended with ok and all its expectations passed.
.EXAMPLE
  tools/test.ps1 -Scenario 001/K1-pal230
  tools/test.ps1 -Scenario 001/K1-pal230 -NoMod
  tools/test.ps1 -Spec 001
  tools/test.ps1 -Scenario dev/start -Manual
#>
param(
  [string]$Scenario,
  [string]$Spec,
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

# "# key: value" lines of the scenario
function Get-Headers([string]$Path) {
  $ret = @{}
  foreach($line in [System.IO.File]::ReadAllLines($Path)) {
    if($line -match '^\s*#\s*(timeout|save|mod)\s*:\s*(.+?)\s*$') {
      $ret[$Matches[1].ToLower()] = $Matches[2]
    }
  }
  return $ret
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

# Runs one scenario; returns Name, Passed, RunDir, Failures.
function Invoke-Scenario([string]$ScenarioPath) {
  $headers = Get-Headers $ScenarioPath
  $useMod  = (-not $NoMod) -and ($headers['mod'] -ne 'off')

  $savePath = $null
  if($Save) {
    $savePath = (Resolve-Path $Save).Path
  } elseif($headers['save']) {
    $savePath = $headers['save']
    if(-not [System.IO.Path]::IsPathRooted($savePath)) { $savePath = Join-Path $ModRoot $savePath }
  }

  $timeout = $TimeoutSec
  if($timeout -le 0 -and $headers['timeout']) { $timeout = [int]$headers['timeout'] }
  if($timeout -le 0) { $timeout = 600 }

  # profile: the working directory of the game, apart from normal play
  $profileDir = Join-Path $ModBuild 'test\profile'
  New-Item -ItemType Directory -Force -Path $profileDir | Out-Null
  $userIni  = Join-Path (Split-Path -Parent $exe) 'Gothic.ini'
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
  $runName = Get-RunName $ScenarioPath
  if(-not $useMod) { $runName += '-nomod' }
  $runDir = Join-Path $ModBuild ("test-runs\" + (Get-Date -Format 'yyyyMMdd-HHmmss') + "-$runName")
  New-Item -ItemType Directory -Force -Path $runDir | Out-Null
  $scenarioCopy = Join-Path $runDir 'scenario.txt'
  Copy-Item $ScenarioPath $scenarioCopy

  $result = [pscustomobject]@{ Name = $runName; Passed = $false; RunDir = $runDir; Failures = @() }
  if($savePath -and -not (Test-Path $savePath -PathType Leaf)) {
    $result.Failures = @("save file not found: $savePath")
    return $result
  }

  $arguments = @('-g', $gothic, '-devmode')
  if($useMod) { $arguments += "-game:$($output.Ini)" }
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

  $git = Get-GitState
  Write-Utf8 (Join-Path $runDir 'meta.json') (([ordered]@{
    scenario  = $ScenarioPath
    spec      = $(if($Spec) { $Spec } else { $null })
    mod       = $useMod
    save      = $savePath
    manual    = [bool]$Manual
    commit    = $git.Commit
    dirty     = $git.Dirty
    started   = (Get-Date -Format 'yyyy-MM-ddTHH:mm:ss')
    timeout   = $(if($Manual) { $null } else { $timeout })
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
  } elseif(-not $process.WaitForExit($timeout * 1000)) {
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
    $failures += "time limit of $timeout s reached, the game was closed"
  }
  $statusFile = Join-Path $runDir 'scenario.json'
  if(-not (Test-Path $statusFile)) {
    $failures += 'no scenario.json: the game ended before the scenario was loaded'
  } else {
    $status = Read-Utf8 $statusFile | ConvertFrom-Json
    if($status.result -eq 'running') {
      $failures += 'the game ended during the scenario (see log.txt and crash.log)'
    } elseif($status.result -ne 'ok') {
      $failures += "scenario $($status.result) at line $($status.line): $($status.message)"
    }
  }

  $checkCode = 1
  if(Test-Path (Join-Path $runDir 'fightlog.jsonl')) {
    $python = Get-Prop (Get-LocalConfig) 'python' 'python'
    & $python -I (Join-Path $PSScriptRoot 'fightlog.py') check $runDir --scenario $scenarioCopy | Out-Host
    $checkCode = $LASTEXITCODE
  } else {
    $failures += 'no fightlog.jsonl'
  }
  if($checkCode -ne 0 -and $failures.Count -eq 0) {
    $failures += 'expectations or scenario failed (see report.md)'
  }

  $result.Failures = $failures
  $result.Passed   = ($failures.Count -eq 0)
  return $result
}

if([string]::IsNullOrEmpty($Scenario) -eq [string]::IsNullOrEmpty($Spec)) {
  throw "Pass either -Scenario or -Spec."
}
if($Spec -and ($Manual -or $Save)) {
  throw "-Spec runs every scenario automatically: -Manual and -Save work with -Scenario only."
}

$gothic = Resolve-GothicDir $GothicDir
$exe    = Get-EngineExe (Resolve-EngineBuildDir $BuildDir)
if(-not (Test-Path $exe)) {
  throw "Engine not found: $exe. Run tools/build-engine.ps1 first."
}
if($Save -and -not (Test-Path $Save -PathType Leaf)) {
  throw "Save file not found: $Save"
}

if($Spec) {
  $dir = Join-Path $TestsRoot $Spec
  if(-not (Test-Path $dir -PathType Container)) {
    throw "No scenarios for spec ${Spec}: $dir"
  }
  $scenarios = @(Get-ChildItem $dir -Filter '*.txt' -File | Sort-Object Name | ForEach-Object { $_.FullName })
  if($scenarios.Count -eq 0) {
    throw "No scenarios in $dir"
  }
} else {
  $scenarios = @(Resolve-Scenario $Scenario)
}

# mod from the repository, including uncommitted changes, packed once; compiler warnings stay out
# of the test output, errors still stop the script
$needMod = (-not $NoMod) -and @($scenarios | Where-Object { (Get-Headers $_)['mod'] -ne 'off' }).Count -gt 0
if($needMod) {
  & (Join-Path $PSScriptRoot 'build-scripts.ps1') -GothicDir $gothic | Out-Null
  & (Join-Path $PSScriptRoot 'pack.ps1') | Out-Null
}
$output = Get-ModOutput

$results = @()
foreach($path in $scenarios) {
  $r = Invoke-Scenario $path
  $results += $r
  if($r.Passed) {
    Write-Step "PASSED: $($r.Name)"
  } else {
    foreach($f in $r.Failures) {
      Write-Host "FAILED: $($r.Name): $f" -ForegroundColor Red
    }
    Write-Host "Results: $($r.RunDir)" -ForegroundColor Red
  }
}

$passed = @($results | Where-Object { $_.Passed }).Count
if($Spec) {
  Write-Step "Summary of spec ${Spec}: $passed of $($results.Count) passed"
  foreach($r in $results) {
    $state = if($r.Passed) { 'PASSED' } else { 'FAILED' }
    $note  = if($r.Passed) { $r.RunDir } else { "$($r.Failures[0]) ($($r.RunDir))" }
    Write-Host ("  {0}  {1}  {2}" -f $state, $r.Name, $note)
  }
}
if($passed -eq $results.Count) {
  exit 0
}
exit 1
