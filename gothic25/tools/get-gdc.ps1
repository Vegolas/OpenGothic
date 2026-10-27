<#
.SYNOPSIS
  Downloads the pinned Daedalus compiler (gdc) with its builtin externals and verifies SHA-256.
.DESCRIPTION
  Installs into gothic25/.tools/gdc-<version>/ (ignored by git). build-scripts.ps1 uses it when
  local.json does not set scriptCompiler.command. The single-file release does not embed the
  builtin externals, so DaedalusBuiltins/ is fetched from the same tag and placed next to the exe.
  gdc is framework-dependent and needs the .NET 8 runtime. See decisions/0001-kompilator-daedalus.md.
.EXAMPLE
  tools/get-gdc.ps1
  tools/get-gdc.ps1 -Force
#>
param(
  [switch]$Force
)

. (Join-Path $PSScriptRoot 'lib/common.ps1')

$repo  = 'dzieje-khorinis/DaedalusCompiler'
$raw   = "https://raw.githubusercontent.com/$repo/v$GdcVersion/src/DaedalusCompiler/DaedalusBuiltins"
$files = @(
  @{ Path = 'gdc-windows-x64.exe'
     Url  = "https://github.com/$repo/releases/download/v$GdcVersion/gdc-windows-x64.exe"
     Sha  = 'a85fd199099fb39e1eb07aeec8bed8a82e8cdc13c8b7df86bbfd36c8e3252345' },
  @{ Path = 'DaedalusBuiltins\gothic.d'
     Url  = "$raw/gothic.d"
     Sha  = '71fc487e898238450316fafdb74ad5f6cb154d9336f63a30c3148df4fb8f8f0a' },
  @{ Path = 'DaedalusBuiltins\menu.d'
     Url  = "$raw/menu.d"
     Sha  = 'd6bed4d748e7fa918ca3b71601903b4f32d5a8ae8c7e127c12a8418c8490da99' }
)

function Get-Sha256([string]$Path) {
  return (Get-FileHash -Algorithm SHA256 $Path).Hash.ToLowerInvariant()
}

# Windows PowerShell 5.1 defaults to TLS 1.0 and renders a slow progress bar
[Net.ServicePointManager]::SecurityProtocol = [Net.ServicePointManager]::SecurityProtocol -bor [Net.SecurityProtocolType]::Tls12
$ProgressPreference = 'SilentlyContinue'

foreach($file in $files) {
  $target = Join-Path $GdcDir $file.Path
  if(-not $Force -and (Test-Path $target) -and (Get-Sha256 $target) -eq $file.Sha) {
    Write-Step "Up to date: $($file.Path)"
    continue
  }
  Write-Step "Downloading $($file.Url)"
  New-Item -ItemType Directory -Force -Path (Split-Path -Parent $target) | Out-Null
  $part = "$target.part"
  Invoke-WebRequest -UseBasicParsing -Uri $file.Url -OutFile $part
  $actual = Get-Sha256 $part
  if($actual -ne $file.Sha) {
    Remove-Item -Force $part
    throw "SHA-256 mismatch for $($file.Path): expected $($file.Sha), got $actual"
  }
  Move-Item -Force $part $target
}

$exe = Join-Path $GdcDir 'gdc-windows-x64.exe'
$runtimes = $null
if(Get-Command dotnet -ErrorAction SilentlyContinue) {
  $runtimes = & dotnet --list-runtimes 2>$null
}
if(-not ($runtimes -match '^Microsoft\.NETCore\.App 8\.')) {
  Write-Warning "gdc needs the .NET 8 runtime: https://dotnet.microsoft.com/download/dotnet/8.0"
} else {
  $version = (& $exe --version).Trim()
  Write-Step "gdc $version ready: $exe"
}
