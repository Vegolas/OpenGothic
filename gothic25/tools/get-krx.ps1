<#
.SYNOPSIS
  Fetches the pinned KrxImpExp Blender add-on and verifies its SHA-256.
.DESCRIPTION
  Installs the dev-branch commit $KrxCommit (tools/lib/common.ps1) into
  gothic25/.tools/blender-scripts/addons/krximpexp/ (ignored by git). anim.ps1 starts Blender with
  BLENDER_USER_SCRIPTS pointing to gothic25/.tools/blender-scripts, so the add-on never touches the
  user's Blender profile. The files come from git (GitLab serves web archives only to browsers),
  exported without line ending conversion, and the hash covers the files (Get-TreeSha256).
  See decisions/0007-zrodla-i-budowanie-animacji-moda.md.
.EXAMPLE
  tools/get-krx.ps1
  tools/get-krx.ps1 -Force
#>
param(
  [switch]$Force
)

. (Join-Path $PSScriptRoot 'lib/common.ps1')

$repo  = 'https://gitlab.com/Patrix9999/krximpexp.git'
$stamp = Join-Path $KrxDir 'KRX_COMMIT.txt'

if(-not $Force -and (Test-Path $stamp) -and (Read-Utf8 $stamp).Trim() -eq $KrxCommit) {
  $actual = Get-TreeSha256 $KrxDir
  if($actual -ne $KrxTreeSha) {
    throw "KrxImpExp in $KrxDir was modified: SHA-256 $actual, expected $KrxTreeSha. Run tools/get-krx.ps1 -Force."
  }
  Write-Step "Up to date: KrxImpExp $KrxCommit"
  return
}

$work = Join-Path $ModRoot '.tools\krximpexp-download'
if(Test-Path $work) { Remove-Item -Recurse -Force $work }
New-Item -ItemType Directory -Force -Path $work | Out-Null
try {
  $clone = Join-Path $work 'repo'
  $zip   = Join-Path $work 'krximpexp.zip'
  Write-Step "Fetching $repo at $KrxCommit"
  Invoke-Native 'git' @('clone', '--quiet', '--filter=blob:none', '--no-checkout', $repo, $clone)
  # no autocrlf: the files must have the bytes stored in git on every machine
  Invoke-Native 'git' @('-C', $clone, '-c', 'core.autocrlf=false', '-c', 'core.eol=lf', 'archive',
    '--format=zip', "--prefix=krximpexp-$KrxCommit/", '-o', $zip, $KrxCommit)
  Expand-Archive -Path $zip -DestinationPath $work
  $src = Join-Path $work "krximpexp-$KrxCommit"
  if(-not (Test-Path (Join-Path $src '__init__.py'))) {
    throw "Unexpected layout, no __init__.py in KrxImpExp $KrxCommit"
  }
  $actual = Get-TreeSha256 $src
  if($actual -ne $KrxTreeSha) {
    throw "SHA-256 mismatch for KrxImpExp ${KrxCommit}: expected $KrxTreeSha, got $actual"
  }
  if(Test-Path $KrxDir) { Remove-Item -Recurse -Force $KrxDir }
  New-Item -ItemType Directory -Force -Path (Split-Path -Parent $KrxDir) | Out-Null
  Move-Item $src $KrxDir
  Write-Utf8 $stamp "$KrxCommit`n"
} finally {
  if(Test-Path $work) { Remove-Item -Recurse -Force $work }
}

Write-Step "KrxImpExp $KrxCommit ready: $KrxDir"
