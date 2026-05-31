<#
.SYNOPSIS
    合并当前目录下所有 .dist 文件夹的直接子项到 test 文件夹，完成后删除空的 .dist 文件夹。
.DESCRIPTION
    扫描当前目录下所有以 .dist 结尾的文件夹。
    - 对于普通 .dist 文件夹，将其直接子文件/子文件夹（包括隐藏文件）移动到 test 文件夹，
      若目标已存在同名条目则跳过该子项。移动完成后，若该 .dist 文件夹已为空，则将其删除。
    - 对于名为 2.dist 的文件夹，将其整个重命名为 2 后移动到 test 文件夹，
      若目标已存在名为 2 的文件夹则跳过。
.NOTES
    此脚本始终处理 PowerShell 的当前工作目录。
.EXAMPLE
    cd D:\Projects
    .\Merge-DistFolders.ps1
    处理 D:\Projects 下的所有 .dist 文件夹。
#>

param(
    [string]$SourcePath = (Get-Location).Path
)

# 确保源路径存在
if (-not (Test-Path -Path $SourcePath -PathType Container)) {
    Write-Error "Source path '$SourcePath' does not exist or is not a folder."
    exit 1
}

# 定义目标文件夹 test（位于当前目录下）
$targetDir = Join-Path -Path $SourcePath -ChildPath "clickmouse"

$allAllowdNotNoneFolder = $false

# 获取所有 .dist 文件夹（包括隐藏文件夹）
$distFolders = Get-ChildItem -Path $SourcePath -Directory -Force | Where-Object { $_.Name -like "*.dist" }

if ($distFolders.Count -eq 0) {
    Write-Warning "No .dist folders found."
    exit 0
}

# 如果目标文件夹不存在，则创建
if (-not (Test-Path -Path $targetDir)) {
    New-Item -Path $targetDir -ItemType Directory | Out-Null
    Write-Host "Created target folder: $targetDir"
} else {
    Write-Host "Target folder already exists: $targetDir"
    $choice = Read-Host "Do you want to force delete it? (Y/N, default is N)"
    $choice = $choice.Trim().ToUpper()
    if ($choice -eq "Y") {
        Remove-Item -Path $targetDir -Recurse -Force
        Write-Host "Deleted target folder: $targetDir"
        New-Item -Path $targetDir -ItemType Directory | Out-Null
        Write-Host "Created target folder: $targetDir"
    } else {
        Write-Warning "You refused to delete the target folder, which may cause merge conflicts, and the software cannot run."
    }
}

foreach ($folder in $distFolders) {
    Write-Host "Process folder: $($folder.FullName)"

    # 特殊处理 updater.dist
    if ($folder.Name -eq "updater.dist") {
        $destPath = Join-Path -Path $targetDir -ChildPath "updater"
        if (Test-Path -Path $destPath) {
            Write-Warning "Skip move 'updater.dist', because target location already has 'updater' folder."
            Remove-Item -Path $folder.FullName -Force -Recurse -ErrorAction SilentlyContinue
        } else {
            try {
                # 直接移动并重命名
                Move-Item -Path $folder.FullName -Force -Destination $destPath
                Write-Host "'updater.dist' rename to 'updater' and move to 'clickmouse'。"
            } catch {
                Write-Error "Move 'updater.dist' failed: $_"
            }
        }
        continue
    }

    # 处理普通 .dist 文件夹：获取其直接子项（包括隐藏文件和文件夹）
    $items = Get-ChildItem -Path $folder.FullName -Force

    foreach ($item in $items) {
        $destItemPath = Join-Path -Path $targetDir -ChildPath $item.Name

        if (Test-Path -Path $destItemPath) {
            Remove-Item -Path $item.FullName -Force -Recurse -ErrorAction SilentlyContinue
            continue
        }

        try {
            Move-Item -Path $item.FullName -Destination $targetDir -Force
            Write-Host "Moved item: $($item.FullName) -> $targetDir"
        } catch {
            Write-Error "Move '$($item.FullName)' failed: $_"
        }
    }

    # 移动完成后检查 .dist 文件夹是否为空，若为空则删除
    if (-not $allAllowdNotNoneFolder) {
        $remaining = Get-ChildItem -Path $folder.FullName -Force
        if ($remaining.Count -eq 0) {
            try {
                Remove-Item -Path $folder.FullName -Force
                Write-Host "Deleted empty dist folder: $($folder.FullName)"
            } catch {
                Write-Error "Delete dist folder failed: $_"
            }
        } else {
            $choice = Read-Host "Please choose whether to force delete non-empty dist folder '$($folder.FullName)'? (Y/A/N, default is N)"
            $choice = $choice.Trim().ToUpper()
            if ($choice -eq "Y") {
                try {
                    Remove-Item -Path $folder.FullName -Force -Recurse
                    Write-Host "Deleted non-empty dist folder: $($folder.FullName)"
                } catch {
                    Write-Error "Delete dist folder failed: $_"
                }
            } elseif ($choice -eq "A") {
                $allAllowdNotNoneFolder = $true
            } else {
                Write-Warning "Dist folder '$($folder.FullName)' is not empty, skip delete."
            }
        }
    }
}

Write-Host "Done."