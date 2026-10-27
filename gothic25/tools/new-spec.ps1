<#
.SYNOPSIS
  Creates the next numbered spec (specs/NNN-slug/spec.md) or ADR (decisions/NNNN-slug.md).
.DESCRIPTION
  Fills the template, appends a row to the index (specs/README.md or decisions/README.md)
  and prints the path of the new document.
.EXAMPLE
  tools/new-spec.ps1 -Title "Skradanie: widocznosc zalezna od swiatla" -Layer silnik
  tools/new-spec.ps1 -Adr -Title "Format plikow zdarzen"
#>
param(
  [Parameter(Mandatory = $true)]
  [string]$Title,
  [string]$Slug,
  [string]$Layer = 'do ustalenia',
  [switch]$Adr
)

. (Join-Path $PSScriptRoot 'lib/common.ps1')

function ConvertTo-Slug([string]$Text) {
  # strip diacritics; the Polish l-stroke does not decompose, so map it explicitly
  $s = $Text.Replace([string][char]0x0142, 'l').Replace([string][char]0x0141, 'L')
  $s = $s.Normalize([System.Text.NormalizationForm]::FormD)
  $s = -join ($s.ToCharArray() | Where-Object {
    [System.Globalization.CharUnicodeInfo]::GetUnicodeCategory($_) -ne 'NonSpacingMark' })
  $s = ($s.ToLowerInvariant() -replace '[^a-z0-9]+', '-').Trim('-')
  if($s.Length -gt 40) { $s = $s.Substring(0, 40).Trim('-') }
  return $s
}

if(-not $Slug) { $Slug = ConvertTo-Slug $Title }
if(-not $Slug) { throw "Cannot derive a slug from the title, pass -Slug" }

if($Adr) {
  $dir = Join-Path $ModRoot 'decisions'
  $digits = 4
  $existing = Get-ChildItem -File $dir -Filter '*.md' | Where-Object { $_.Name -match '^\d{4}-' }
} else {
  $dir = Join-Path $ModRoot 'specs'
  $digits = 3
  $existing = Get-ChildItem -Directory $dir | Where-Object { $_.Name -match '^\d{3}-' }
}

$next = 1
foreach($item in $existing) {
  $n = [int]$item.Name.Substring(0, $digits)
  if($n -ge $next) { $next = $n + 1 }
}
$number = $next.ToString("D$digits")
$values = @{ NUMBER = $number; TITLE = $Title; LAYER = $Layer; DATE = (Get-Date -Format 'yyyy-MM-dd') }
$index = Join-Path $dir 'README.md'

if($Adr) {
  $doc = Join-Path $dir "$number-$Slug.md"
  Write-Utf8 $doc (Expand-Template (Read-Utf8 (Join-Path $ModRoot 'sdd\templates\adr.md')) $values)
  $row = "| [$number]($number-$Slug.md) | $Title | Proponowana |"
} else {
  $doc = Join-Path $dir "$number-$Slug\spec.md"
  Write-Utf8 $doc (Expand-Template (Read-Utf8 (Join-Path $ModRoot 'sdd\templates\spec.md')) $values)
  $row = "| [$number]($number-$Slug/spec.md) | $Title | $Layer | Szkic |"
}

$text = (Read-Utf8 $index).TrimEnd("`r", "`n") + "`n" + $row + "`n"
Write-Utf8 $index $text

Write-Output $doc
