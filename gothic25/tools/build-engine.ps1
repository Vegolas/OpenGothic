<#
.SYNOPSIS
  Builds the OpenGothic engine (CMake + Ninja + MSVC).
.DESCRIPTION
  Imports the Visual Studio developer environment (via vswhere) when cl.exe is not on PATH,
  configures the build directory when needed and builds the engine target from mod.json.
.EXAMPLE
  tools/build-engine.ps1
  tools/build-engine.ps1 -BuildDir ../build-release -BuildType Release -Clean
#>
param(
  [string]$BuildDir,
  [ValidateSet('Debug', 'RelWithDebInfo', 'Release')]
  [string]$BuildType,
  [string[]]$Targets,
  [switch]$Clean
)

. (Join-Path $PSScriptRoot 'lib/common.ps1')

function Import-VsDevEnvironment {
  if(Get-Command cl.exe -ErrorAction SilentlyContinue) {
    return
  }
  $vswhere = Join-Path ${env:ProgramFiles(x86)} 'Microsoft Visual Studio\Installer\vswhere.exe'
  if(-not (Test-Path $vswhere)) {
    throw "cl.exe is not on PATH and vswhere.exe was not found. Run from a Developer PowerShell for Visual Studio."
  }
  $vs = & $vswhere -latest -prerelease -products * `
          -requires Microsoft.VisualStudio.Component.VC.Tools.x86.x64 -property installationPath
  if(-not $vs) {
    throw "No Visual Studio installation with the C++ x64 toolset was found."
  }
  $vcvars = Join-Path $vs 'VC\Auxiliary\Build\vcvars64.bat'
  Write-Step "Importing MSVC environment from $vs"
  $lines = & cmd.exe /s /c "`"$vcvars`" >nul && set"
  if($LASTEXITCODE -ne 0) {
    throw "vcvars64.bat failed"
  }
  foreach($line in $lines) {
    $eq = $line.IndexOf('=')
    if($eq -gt 0) {
      [Environment]::SetEnvironmentVariable($line.Substring(0, $eq), $line.Substring($eq + 1), 'Process')
    }
  }
}

# Tempest takes the Vulkan headers from $ENV{VULKAN_SDK} at configure time; a stale value
# in the current process would be baked into the build directory.
function Resolve-VulkanSdk {
  $candidates = @($env:VULKAN_SDK,
                  [Environment]::GetEnvironmentVariable('VULKAN_SDK', 'User'),
                  [Environment]::GetEnvironmentVariable('VULKAN_SDK', 'Machine'))
  foreach($sdk in $candidates) {
    if($sdk -and (Test-Path (Join-Path $sdk 'Include\vulkan\vulkan.h'))) {
      if($sdk -ne $env:VULKAN_SDK) {
        Write-Warning "VULKAN_SDK '$env:VULKAN_SDK' has no Include\vulkan\vulkan.h, using $sdk"
        $env:VULKAN_SDK = $sdk
      }
      return
    }
  }
  throw "Vulkan SDK not found. Install it from https://vulkan.lunarg.com and set VULKAN_SDK."
}

$manifest = Get-ModManifest
$BuildDir = Resolve-EngineBuildDir $BuildDir
if(-not $BuildType) { $BuildType = Get-Prop (Get-LocalConfig) 'engineBuildType' 'RelWithDebInfo' }
if(-not $Targets)   { $Targets = @($manifest.engine.target) }

Import-VsDevEnvironment
Resolve-VulkanSdk

if($Clean -and (Test-Path $BuildDir)) {
  Write-Step "Removing $BuildDir"
  Remove-Item -Recurse -Force $BuildDir
}

Write-Step "Configuring $BuildDir ($BuildType)"
Invoke-Native 'cmake' @('-S', $RepoRoot, '-B', $BuildDir, '-G', 'Ninja', "-DCMAKE_BUILD_TYPE=$BuildType")

Write-Step "Building $($Targets -join ', ')"
Invoke-Native 'cmake' (@('--build', $BuildDir, '--target') + $Targets)

$exe = Get-EngineExe $BuildDir
if(-not (Test-Path $exe)) {
  throw "Build finished but $exe is missing"
}
Write-Step "Engine ready: $exe"
