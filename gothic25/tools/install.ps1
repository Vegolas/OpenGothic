<#
.SYNOPSIS
  Copies the packed mod into a Gothic II installation (or removes it with -Uninstall).
.DESCRIPTION
  <gothic>/Data/ModVDF/<archive> and <gothic>/System/<ini>. Run pack.ps1 first.
#>
param(
  [string]$GothicDir,
  [switch]$Uninstall
)

. (Join-Path $PSScriptRoot 'lib/common.ps1')

$manifest = Get-ModManifest
$output   = Get-ModOutput
$gothic   = Resolve-GothicDir $GothicDir

$targets = @(
  @{ Source = $output.Archive; Target = Join-Path $gothic "Data\ModVDF\$($manifest.archive)" },
  @{ Source = $output.Ini;     Target = Join-Path $gothic "System\$($manifest.ini)" }
)

foreach($t in $targets) {
  if($Uninstall) {
    if(Test-Path $t.Target) {
      Remove-Item -Force $t.Target
      Write-Step "Removed $($t.Target)"
    }
    continue
  }
  if(-not (Test-Path $t.Source)) {
    throw "Missing $($t.Source). Run tools/pack.ps1 first."
  }
  New-Item -ItemType Directory -Force -Path (Split-Path -Parent $t.Target) | Out-Null
  Copy-Item -Force $t.Source $t.Target
  Write-Step "Installed $($t.Target)"
}
