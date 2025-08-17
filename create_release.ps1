# GitHub Release Creator Script
# 使用方法: 需要先设置 GitHub 个人访问令牌

param(
    [Parameter(Mandatory=$true)]
    [string]$GitHubToken,
    
    [Parameter(Mandatory=$false)]
    [string]$TagVersion = "v1.0.0",
    
    [Parameter(Mandatory=$false)]
    [string]$ReleaseTitle = "MakeID Windows Executable v1.0.0"
)

# GitHub 仓库信息
$owner = "goulaobangzi"
$repo = "IDMaker"

# Release 描述
$releaseDescription = @"
## 🎉 发布说明

这是 MakeID Photo Generator 的第一个 Windows 可执行文件版本！

## ✨ 新功能

### 🚀 完全独立的 Windows 可执行文件
- **无需安装 Python** - 直接双击运行
- **包含所有依赖** - DNN模型、模板、字体等资源已打包
- **跨机器兼容** - 可在任何 Windows 10/11 机器上运行

### 🎯 增强的用户体验
- **交互式工作流** - 友好的用户引导和确认步骤
- **自动模式** - 支持完全自动化的批量处理
- **进度显示** - 清晰的进度条和状态反馈

### 🔧 强大的功能特性
- **智能人脸检测** - 基于 DNN 的准确人脸识别
- **多模板支持** - Student, Staff, Parent, Resident, Contractor
- **中文姓名转换** - 自动转换为英文拼音
- **递归搜索** - 自动处理子目录中的照片

## 📦 包含文件

- **MakeID.exe** - 主程序（76MB）
- **config.json** - 配置文件
- **README.md** - 详细使用说明
- **Run_MakeID.bat** - 快速启动脚本

## 🚀 使用方法

1. 解压 ZIP 文件到任意文件夹
2. 双击 `MakeID.exe` 或 `Run_MakeID.bat`
3. 按照提示操作

## 🔧 系统要求

- **操作系统**: Windows 10 或 Windows 11
- **内存**: 建议 4GB 以上
- **存储**: 至少 100MB 可用空间
- **其他**: 无需安装 Python 或其他依赖

## 📄 许可证

本项目采用 MIT 许可证。

---

**享受使用 MakeID Photo Generator！** 🎯✨
"@

# 创建 release 的 JSON 数据
$releaseData = @{
    tag_name = $TagVersion
    name = $ReleaseTitle
    body = $releaseDescription
    draft = $false
    prerelease = $false
} | ConvertTo-Json

Write-Host "正在创建 GitHub Release..." -ForegroundColor Green
Write-Host "Tag: $TagVersion" -ForegroundColor Yellow
Write-Host "标题: $ReleaseTitle" -ForegroundColor Yellow

# 创建 release
$createReleaseUrl = "https://api.github.com/repos/$owner/$repo/releases"
$headers = @{
    "Authorization" = "token $GitHubToken"
    "Accept" = "application/vnd.github.v3+json"
    "User-Agent" = "MakeID-Release-Creator"
}

try {
    Write-Host "发送创建 release 请求..." -ForegroundColor Blue
    $response = Invoke-RestMethod -Uri $createReleaseUrl -Method Post -Headers $headers -Body $releaseData -ContentType "application/json"
    
    Write-Host "✅ Release 创建成功！" -ForegroundColor Green
    Write-Host "Release ID: $($response.id)" -ForegroundColor Yellow
    Write-Host "Release URL: $($response.html_url)" -ForegroundColor Yellow
    
    # 上传发布文件
    $uploadUrl = $response.upload_url -replace "\{\?name,label\}", ""
    $zipFile = "MakeID_Windows_v1.0.0.zip"
    
    if (Test-Path $zipFile) {
        Write-Host "正在上传发布文件: $zipFile" -ForegroundColor Blue
        
        $uploadHeaders = @{
            "Authorization" = "token $GitHubToken"
            "Accept" = "application/vnd.github.v3+json"
            "User-Agent" = "MakeID-Release-Creator"
        }
        
        $uploadUrl = "$uploadUrl?name=$zipFile"
        $fileContent = [System.IO.File]::ReadAllBytes($zipFile)
        
        $uploadResponse = Invoke-RestMethod -Uri $uploadUrl -Method Post -Headers $uploadHeaders -Body $fileContent -ContentType "application/zip"
        
        Write-Host "✅ 文件上传成功！" -ForegroundColor Green
        Write-Host "文件大小: $($uploadResponse.size) bytes" -ForegroundColor Yellow
        Write-Host "下载 URL: $($uploadResponse.browser_download_url)" -ForegroundColor Yellow
    } else {
        Write-Host "❌ 发布文件未找到: $zipFile" -ForegroundColor Red
    }
    
} catch {
    Write-Host "❌ 创建 release 失败:" -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Red
    
    if ($_.Exception.Response) {
        $statusCode = $_.Exception.Response.StatusCode
        $statusDescription = $_.Exception.Response.StatusDescription
        Write-Host "HTTP 状态: $statusCode - $statusDescription" -ForegroundColor Red
    }
}

Write-Host "`n完成！" -ForegroundColor Green 