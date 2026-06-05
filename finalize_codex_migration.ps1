$ErrorActionPreference = "Stop"
$ts = Get-Date -Format "yyyyMMdd_HHmmss"

$oldCodex = "C:\Users\navka\.codex"
$newCodex = "C:\Users\navka\navakanth001\.codex"
$oldAgents = "C:\Users\navka\.agents"
$newAgents = "C:\Users\navka\navakanth001\.agents"

function Ensure-Junction {
    param(
        [string]$OldPath,
        [string]$NewPath,
        [string]$BackupPrefix
    )

    if (-not (Test-Path -LiteralPath $NewPath)) {
        throw "Target path does not exist: $NewPath"
    }

    if (-not (Test-Path -LiteralPath $OldPath)) {
        cmd /c mklink /J "$OldPath" "$NewPath" | Out-Null
        Write-Output "Created junction: $OldPath -> $NewPath"
        return
    }

    $item = Get-Item -LiteralPath $OldPath -Force
    if ($item.Attributes -band [IO.FileAttributes]::ReparsePoint) {
        Write-Output "Already a junction/symlink: $OldPath"
        return
    }

    $backup = "${OldPath}_${BackupPrefix}_$ts"
    Rename-Item -LiteralPath $OldPath -NewName (Split-Path -Leaf $backup)
    cmd /c mklink /J "$OldPath" "$NewPath" | Out-Null
    Write-Output "Backed up $OldPath to $backup"
    Write-Output "Created junction: $OldPath -> $NewPath"
}

Ensure-Junction -OldPath $oldCodex -NewPath $newCodex -BackupPrefix "backup"
Ensure-Junction -OldPath $oldAgents -NewPath $newAgents -BackupPrefix "backup"

Write-Output "Migration finalization complete."
