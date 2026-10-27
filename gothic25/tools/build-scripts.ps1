<#
.SYNOPSIS
  Compiles the Daedalus sources from content/Scripts into gothic25/build/scripts.
.DESCRIPTION
  For every entry in mod.json -> scripts whose .src exists, runs the compiler configured in
  local.json -> scriptCompiler. Entries marked "ou": true also get scriptCompiler.ouArgs
  (dialogue output units). Argument placeholders: {src} {dat} {ou} {out} {gothic}.
  Output layout mirrors _work/Data/Scripts: _compiled/*.DAT, Content/Cutscene/OU.*
  Without sources this is a no-op. Compiler choice: decisions/0001-kompilator-daedalus.md.
#>
param(
  [string]$GothicDir
)

. (Join-Path $PSScriptRoot 'lib/common.ps1')

$manifest = Get-ModManifest
$srcRoot  = Join-Path $ModRoot 'content\Scripts'
$outRoot  = Join-Path $ModBuild 'scripts'
$datDir   = Join-Path $outRoot '_compiled'
$ouDir    = Join-Path $outRoot 'Content\Cutscene'

$jobs = @($manifest.scripts | Where-Object { Test-Path (Join-Path $srcRoot $_.src) })
if($jobs.Count -eq 0) {
  Write-Step "No Daedalus sources in content/Scripts, nothing to compile"
  return
}

$compiler = Get-Prop (Get-LocalConfig) 'scriptCompiler'
$command  = Get-Prop $compiler 'command'
if(-not $command) {
  throw "Daedalus sources found, but scriptCompiler.command is not set in gothic25/local.json (see decisions/0001-kompilator-daedalus.md)."
}
$argTemplate = @(Get-Prop $compiler 'args' @('{src}', '{dat}'))
$ouTemplate  = @(Get-Prop $compiler 'ouArgs' @())
$gothic = ''
if((($argTemplate + $ouTemplate) -join ' ') -like '*{gothic}*') {
  $gothic = Resolve-GothicDir $GothicDir
}

if(Test-Path $outRoot) { Remove-Item -Recurse -Force $outRoot }
New-Item -ItemType Directory -Force -Path $datDir, $ouDir | Out-Null

foreach($job in $jobs) {
  $values = @{
    src    = Join-Path $srcRoot $job.src
    dat    = Join-Path $datDir $job.dat
    ou     = $ouDir
    out    = $outRoot
    gothic = $gothic
  }
  $template = $argTemplate
  if(Get-Prop $job 'ou' $false) { $template = $template + $ouTemplate }
  $arguments = foreach($a in $template) {
    $s = [string]$a
    foreach($k in $values.Keys) { $s = $s.Replace("{$k}", $values[$k]) }
    $s
  }
  Write-Step "Compiling $($job.src) -> $($job.dat)"
  Invoke-Native $command @($arguments)
  if(-not (Test-Path $values.dat)) {
    throw "Compiler finished but $($values.dat) was not produced"
  }
}
