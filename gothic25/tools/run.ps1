<#
.SYNOPSIS
  Starts the OpenGothic build with the mod (-game:<ini>).
.EXAMPLE
  tools/run.ps1 -Dev
  tools/run.ps1 -Pack -World addonworld.zen -Window
  tools/run.ps1 -EngineArgs '-save','q'
#>
param(
  [string]$GothicDir,
  [string]$BuildDir,
  [string]$World,
  [switch]$Dev,
  [switch]$Window,
  [switch]$Pack,
  [switch]$Wait,
  [string[]]$EngineArgs
)

. (Join-Path $PSScriptRoot 'lib/common.ps1')

$manifest = Get-ModManifest
$gothic   = Resolve-GothicDir $GothicDir
$exe      = Get-EngineExe (Resolve-EngineBuildDir $BuildDir)
if(-not (Test-Path $exe)) {
  throw "Engine not found: $exe. Run tools/build-engine.ps1 first."
}

if($Pack) {
  & (Join-Path $PSScriptRoot 'pack.ps1')
  & (Join-Path $PSScriptRoot 'install.ps1') -GothicDir $gothic
}
if(-not (Test-Path (Join-Path $gothic "System\$($manifest.ini)"))) {
  throw "$($manifest.ini) is not installed in $gothic. Run tools/install.ps1 (or pass -Pack)."
}

$arguments = @('-g', $gothic, "-game:$($manifest.ini)")
if($Dev)    { $arguments += '-devmode' }
if($Window) { $arguments += '-window' }
if($World)  { $arguments += @('-w', $World) }
if($EngineArgs) { $arguments += $EngineArgs }

# Start-Process joins arguments with spaces, so quote the ones that contain spaces.
$argLine = ($arguments | ForEach-Object { if($_ -match '\s') { '"' + $_ + '"' } else { $_ } }) -join ' '
Write-Step "$exe $argLine"
$process = Start-Process -FilePath $exe -ArgumentList $argLine -WorkingDirectory (Split-Path -Parent $exe) -PassThru
if($Wait) {
  $process.WaitForExit()
  exit $process.ExitCode
}
