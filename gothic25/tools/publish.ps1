<#
.SYNOPSIS
  Builds a release: engine, scripts, mod archive, zip packages and SHA-256 sums.
.DESCRIPTION
  Output in gothic25/dist/<version>/:
    <id>-<version>-mod.zip           Data/ModVDF/<archive>, System/<ini>, NOTICE, GothicMOD license
    <id>-<version>-engine-win64.zip  OpenGothic/<engine files>, launcher, OpenGothic license
    SHA256SUMS.txt
  The release engine is built in <repo>/build-release (Release), separate from the dev build.
  The archive timestamp is the last commit time, so the same commit gives the same .mod.
.EXAMPLE
  tools/publish.ps1
  tools/publish.ps1 -SkipEngine -AllowDirty -Force
#>
param(
  [string]$BuildDir,
  [ValidateSet('RelWithDebInfo', 'Release')]
  [string]$BuildType = 'Release',
  [switch]$SkipEngine,
  [switch]$AllowDirty,
  [switch]$Force,
  [switch]$Tag
)

. (Join-Path $PSScriptRoot 'lib/common.ps1')

function New-ZipFromDirectory([string]$Dir, [string]$ZipPath) {
  Add-Type -AssemblyName System.IO.Compression, System.IO.Compression.FileSystem
  if(Test-Path $ZipPath) { Remove-Item -Force $ZipPath }
  $zip = [System.IO.Compression.ZipFile]::Open($ZipPath, 'Create')
  try {
    $root = (Resolve-Path $Dir).Path.TrimEnd('\') + '\'
    foreach($file in Get-ChildItem -Recurse -File $Dir | Sort-Object FullName) {
      $entry = $file.FullName.Substring($root.Length).Replace('\', '/')
      [System.IO.Compression.ZipFileExtensions]::CreateEntryFromFile($zip, $file.FullName, $entry, 'Optimal') | Out-Null
    }
  }
  finally {
    $zip.Dispose()
  }
}

$manifest = Get-ModManifest
$version  = $manifest.version
$name     = "$($manifest.id)-$version"
$dist     = Join-Path $ModRoot "dist\$version"
if(-not $BuildDir) { $BuildDir = Join-Path $RepoRoot 'build-release' }

Write-Step "Publishing $($manifest.title) $version"

# Preconditions
$dirty = & git -C $RepoRoot status --porcelain
if($dirty -and -not $AllowDirty) {
  throw "Working tree is not clean. Commit your changes or pass -AllowDirty."
}
if((Test-Path $dist) -and -not $Force) {
  throw "$dist already exists. Bump version in mod.json or pass -Force."
}
$changelog = Read-Utf8 (Join-Path $ModRoot 'CHANGELOG.md')
if($changelog -notmatch "(?m)^## \[$([regex]::Escape($version))\]") {
  Write-Warning "CHANGELOG.md has no section '## [$version]'"
}

$commit = (& git -C $RepoRoot rev-parse --short HEAD).Trim()

# Build
if(-not $SkipEngine) {
  & (Join-Path $PSScriptRoot 'build-engine.ps1') -BuildDir $BuildDir -BuildType $BuildType
}
& (Join-Path $PSScriptRoot 'build-scripts.ps1')
$env:SOURCE_DATE_EPOCH = (& git -C $RepoRoot log -1 --format=%ct).Trim()
try {
  & (Join-Path $PSScriptRoot 'pack.ps1')
}
finally {
  Remove-Item Env:SOURCE_DATE_EPOCH -ErrorAction SilentlyContinue
}

# Stage
if(Test-Path $dist) { Remove-Item -Recurse -Force $dist }
$stage = Join-Path $ModBuild 'publish'
if(Test-Path $stage) { Remove-Item -Recurse -Force $stage }

Write-Step "Assembling packages in $dist"
New-Item -ItemType Directory -Force -Path $dist | Out-Null
$output = Get-ModOutput
# GothicMOD Lizenz 6(a): every release carries the licence text (constitution, rule 9)
Copy-Item (Join-Path $ModRoot 'NOTICE.txt') $output.GameDir
Copy-Item (Join-Path $ModRoot 'content\Scripts\LICENSE-GothicMOD.txt') $output.GameDir
New-ZipFromDirectory $output.GameDir (Join-Path $dist "$name-mod.zip")

$engineSrc = Join-Path (Resolve-EngineBuildDir $BuildDir) 'opengothic'
if(Test-Path (Join-Path $engineSrc "$($manifest.engine.target).exe")) {
  $engineStage = Join-Path $stage 'engine\OpenGothic'
  New-Item -ItemType Directory -Force -Path $engineStage | Out-Null
  foreach($file in $manifest.engine.files) {
    $path = Join-Path $engineSrc $file
    if(-not (Test-Path $path)) { throw "Engine file missing: $path" }
    Copy-Item $path $engineStage
  }
  Copy-Item (Join-Path $RepoRoot 'LICENSE') (Join-Path $engineStage 'LICENSE-OpenGothic.txt')
  Copy-Item (Join-Path $ModRoot 'NOTICE.txt') $engineStage
  $launcher = "@echo off`r`nrem $($manifest.title) $version ($commit)`r`nrem Add -g ""<path to Gothic II>"" if the game is not detected automatically.`r`nstart """" ""%~dp0$($manifest.engine.target).exe"" -game:$($manifest.ini) %*`r`n"
  [System.IO.File]::WriteAllText((Join-Path $engineStage "$($manifest.id).bat"), $launcher, [System.Text.Encoding]::ASCII)
  New-ZipFromDirectory (Join-Path $stage 'engine') (Join-Path $dist "$name-engine-win64.zip")
}
elseif($SkipEngine) {
  Write-Warning "No engine build in $engineSrc, publishing the mod package only"
}
else {
  throw "Engine executable missing in $engineSrc"
}

# Checksums
$sums = Get-ChildItem -File $dist -Filter '*.zip' | Sort-Object Name | ForEach-Object {
  "$((Get-FileHash -Algorithm SHA256 $_.FullName).Hash.ToLowerInvariant())  $($_.Name)"
}
Write-Utf8 (Join-Path $dist 'SHA256SUMS.txt') (($sums -join "`n") + "`n")

if($Tag) {
  $tagName = "$($manifest.id)-v$version"
  Invoke-Native 'git' @('-C', $RepoRoot, 'tag', '-a', $tagName, '-m', "$($manifest.title) $version")
  Write-Step "Created local tag $tagName (not pushed)"
}

Write-Step "Release $version ($commit) ready:"
Get-ChildItem -File $dist | ForEach-Object { Write-Host ("    {0,-40} {1,10:N1} MiB" -f $_.Name, ($_.Length / 1MB)) }
