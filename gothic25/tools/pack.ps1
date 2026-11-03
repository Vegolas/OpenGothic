<#
.SYNOPSIS
  Packs content/ and compiled scripts into the mod archive and renders the mod .ini.
.DESCRIPTION
  Output (game folder layout, ready for install.ps1 and publish.ps1):
    gothic25/build/game/Data/ModVDF/<archive>
    gothic25/build/game/System/<ini>
  content/                -> _WORK/DATA
  build/scripts/          -> _WORK/DATA/SCRIPTS            (overrides content/ on name clashes)
  build/anims/_COMPILED/  -> _WORK/DATA/ANIMS/_COMPILED    (tools/anim.py build from anims/)

  The animations are built first. With a Gothic folder (-GothicDir, G25_GOTHIC_DIR or local.json)
  their definitions are also checked against the game; without one those checks are skipped.
  -AnimExtra adds source folders, e.g. local test data that never goes into the repository.
.EXAMPLE
  tools/pack.ps1
  tools/pack.ps1 -AnimExtra build/anims-fixtures
#>
param(
  [string]$GothicDir,
  [string[]]$AnimExtra
)

. (Join-Path $PSScriptRoot 'lib/common.ps1')

$manifest = Get-ModManifest
$output   = Get-ModOutput

$animArgs = @((Join-Path $PSScriptRoot 'anim.py'), 'build')
try {
  $animArgs += @('--gothic', (Resolve-GothicDir $GothicDir))
} catch {
  Write-Warning "No Gothic folder: animation definitions are not checked against the game."
}
foreach($extra in $AnimExtra) {
  if(-not $extra) { continue }
  if(-not [System.IO.Path]::IsPathRooted($extra)) { $extra = Join-Path (Get-Location).Path $extra }
  $animArgs += @('--extra', $extra)
}
Write-Step "Building animations"
Invoke-Python $animArgs

$arguments = @(
  (Join-Path $PSScriptRoot 'vdf.py'), 'pack', $output.Archive,
  '--map', "$(Join-Path $ModRoot 'content')=_WORK/DATA",
  '--map', "$(Join-Path $ModBuild 'scripts')=_WORK/DATA/SCRIPTS",
  '--map', "$(Join-Path $ModBuild 'anims\_COMPILED')=_WORK/DATA/ANIMS/_COMPILED",
  '--comment', "$($manifest.title) $($manifest.version)"
)
foreach($pattern in $manifest.pack.exclude) {
  $arguments += @('--exclude', $pattern)
}

Write-Step "Packing $($manifest.archive)"
Invoke-Python $arguments

Write-Step "Writing $($manifest.ini)"
$ini = Expand-Template (Read-Utf8 (Join-Path $ModRoot "system\$($manifest.ini)")) @{
  TITLE   = $manifest.title
  VERSION = $manifest.version
  AUTHORS = $manifest.authors
  ARCHIVE = $manifest.archive
  PLAYER  = $manifest.ini_values.player
  WORLD   = $manifest.ini_values.world
}
# Gothic reads .ini files as ANSI with CRLF line endings
$ini = ($ini -replace "`r?`n", "`r`n")
New-Item -ItemType Directory -Force -Path (Split-Path -Parent $output.Ini) | Out-Null
[System.IO.File]::WriteAllText($output.Ini, $ini, [System.Text.Encoding]::GetEncoding(1250))

Write-Step "Done: $($output.GameDir)"
