<#
.SYNOPSIS
  Blender steps of the mod animations (spec 004, decisions/0007-zrodla-i-budowanie-animacji-moda.md).
.DESCRIPTION
  Runs tools/blender/*.py in Blender 5.2 without a window (--background --factory-startup), with the
  pinned KrxImpExp from tools/get-krx.ps1 (BLENDER_USER_SCRIPTS, the user's Blender profile is not
  used). Original files come from the game archives into gothic25/build/anims-work/<MODEL>/
  (tools/anim.py extract); they never go to the repository.

    import     original animation -> working .blend with the body, to start a new animation from
    open       source .blend from anims/<MODEL>/ -> working .blend with the body
    export     action of a working .blend -> anims/<MODEL>/<ACTION>.anim and <ACTION>.blend (no game meshes)
    check      every anims/<MODEL>/*.blend matches its .anim
    roundtrip  every original animation of the model: MAN -> Blender -> MAN, byte compare (spec 004 K1)

  Working files go to gothic25/build/anims-work/<MODEL>/blend/. Blender comes from -Blender,
  G25_BLENDER or "blender" in gothic25/local.json.
.EXAMPLE
  tools/anim.ps1 import -Anim S_FISTATTACK
  tools/anim.ps1 import -Anim T_1HATTACKL -Overlay HUMANS_1HST1
  tools/anim.ps1 export -Blend build/anims-work/HUMANS/blend/S_FISTATTACK.blend -Action T_FISTATTACKL
  tools/anim.ps1 open -Blend anims/HUMANS/T_FISTATTACKL.blend
  tools/anim.ps1 check
  tools/anim.ps1 roundtrip
#>
param(
  [Parameter(Mandatory = $true, Position = 0)]
  [ValidateSet('import', 'open', 'export', 'check', 'roundtrip')]
  [string]$Command,
  [string]$Model = 'HUMANS',
  [string]$Anim,
  [string]$Overlay,
  [string]$Blend,
  [string]$Action,
  [string]$Out,
  [string]$Mesh = 'HUM_BODY_NAKED0.MDM',
  [switch]$Refresh,
  [string]$GothicDir,
  [string]$Blender
)

. (Join-Path $PSScriptRoot 'lib/common.ps1')

$Model    = $Model.ToUpperInvariant()
$exe      = Resolve-Blender $Blender
$workDir  = Join-Path $ModBuild "anims-work\$Model"
$blendDir = Join-Path $workDir 'blend'
$srcDir   = Join-Path $ModRoot "anims\$Model"
$scripts  = Join-Path $PSScriptRoot 'blender'

function Assert-Krx {
  $stamp = Join-Path $KrxDir 'KRX_COMMIT.txt'
  if(-not (Test-Path $stamp)) {
    throw "KrxImpExp is not installed in $KrxDir. Run tools/get-krx.ps1."
  }
  $installed = (Read-Utf8 $stamp).Trim()
  if($installed -ne $KrxCommit) {
    throw "KrxImpExp $installed is installed, the tools need $KrxCommit. Run tools/get-krx.ps1."
  }
  if((Get-TreeSha256 $KrxDir) -ne $KrxTreeSha) {
    throw "KrxImpExp in $KrxDir was modified. Run tools/get-krx.ps1 -Force."
  }
}

# Original files of the model; extracted again with -Refresh or when the hierarchy is missing.
function Initialize-WorkDir([switch]$Force) {
  if($Force -or $Refresh -or -not (Test-Path (Join-Path $workDir "$Model.MDH")) -or
     -not (Test-Path (Join-Path $workDir $Mesh))) {
    $gothic = Resolve-GothicDir $GothicDir
    Invoke-Python @((Join-Path $PSScriptRoot 'anim.py'), 'extract', $Model, '--gothic', $gothic,
      '--out', $workDir, '--mesh', $Mesh)
  }
}

function Invoke-Blender([string]$Script, [string[]]$Arguments) {
  $env:BLENDER_USER_SCRIPTS = $BlenderScriptsDir
  try {
    Invoke-Native $exe (@('--background', '--factory-startup', '--python-exit-code', '1',
      '--python', (Join-Path $scripts $Script), '--') + $Arguments)
  } finally {
    Remove-Item Env:BLENDER_USER_SCRIPTS -ErrorAction SilentlyContinue
  }
}

function Resolve-Full([string]$Path) {
  if([System.IO.Path]::IsPathRooted($Path)) { return [System.IO.Path]::GetFullPath($Path) }
  return [System.IO.Path]::GetFullPath((Join-Path (Get-Location).Path $Path))
}

Assert-Krx

switch($Command) {
  'import' {
    if(-not $Anim) { throw "import needs -Anim, e.g. -Anim S_FISTATTACK" }
    Initialize-WorkDir
    $prefix = if($Overlay) { $Overlay.ToUpperInvariant() } else { $Model }
    $man = "$prefix-$($Anim.ToUpperInvariant())"
    if(-not (Test-Path (Join-Path $workDir "$man.MAN"))) {
      throw "No $man.MAN in the game archives (looked in $workDir)."
    }
    $target = if($Out) { Resolve-Full $Out } else { Join-Path $blendDir "$($Anim.ToUpperInvariant()).blend" }
    Invoke-Blender 'rig.py' @('import', $workDir, $Model, $man, $target, '--mesh', $Mesh)
  }
  'open' {
    if(-not $Blend) { throw "open needs -Blend, e.g. -Blend anims/$Model/T_FISTATTACKL.blend" }
    Initialize-WorkDir
    $source = Resolve-Full $Blend
    $target = if($Out) { Resolve-Full $Out } else { Join-Path $blendDir ([System.IO.Path]::GetFileName($source)) }
    if($source -eq $target) { throw "open would overwrite its source: pass -Out" }
    Invoke-Blender 'rig.py' @('open', $source, $workDir, $Model, $target, '--mesh', $Mesh)
  }
  'export' {
    if(-not $Blend) { throw "export needs -Blend, a working .blend from import or open" }
    Initialize-WorkDir
    $target = if($Out) { Resolve-Full $Out } else { $srcDir }
    $arguments = @((Resolve-Full $Blend), $target, $workDir, $Model)
    if($Action) { $arguments += @('--action', $Action) }
    Invoke-Blender 'export.py' $arguments
  }
  'check' {
    Initialize-WorkDir
    $dir = if($Out) { Resolve-Full $Out } else { $srcDir }
    if(-not (Test-Path $dir)) { throw "No source folder $dir" }
    Invoke-Blender 'check.py' @($dir, $workDir, $Model)
  }
  'roundtrip' {
    Initialize-WorkDir -Force
    Invoke-Blender 'rig.py' @('roundtrip', $workDir, $Model)
  }
}
