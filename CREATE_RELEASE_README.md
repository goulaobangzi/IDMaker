# 创建 GitHub Release 指南

## 🚀 自动创建 Release

我已经创建了一个 PowerShell 脚本来自动创建 GitHub release。

## 📋 准备工作

### 1. 创建 GitHub 个人访问令牌

1. **登录 GitHub** 并访问 [Settings > Developer settings > Personal access tokens](https://github.com/settings/tokens)

2. **点击 "Generate new token (classic)"**

3. **设置令牌权限**:
   - ✅ `repo` - 完整的仓库访问权限
   - ✅ `write:packages` - 上传包文件权限

4. **生成令牌** 并复制保存（注意：令牌只显示一次！）

## 🔧 运行脚本

### 方法 1: 使用 PowerShell 脚本（推荐）

```powershell
# 运行脚本，需要提供 GitHub 令牌
.\create_release.ps1 -GitHubToken "your_github_token_here"

# 或者使用默认版本号
.\create_release.ps1 -GitHubToken "your_github_token_here" -TagVersion "v1.0.0"
```

### 方法 2: 手动在 GitHub 网页上创建

1. 访问 [https://github.com/goulaobangzi/IDMaker](https://github.com/goulaobangzi/IDMaker)

2. 点击 "Releases" 或 "Create a new release"

3. 填写信息：
   - **Tag version**: `v1.0.0`
   - **Release title**: `MakeID Windows Executable v1.0.0`
   - **Description**: 复制 `RELEASE_NOTES.md` 的内容

4. 上传 `MakeID_Windows_v1.0.0.zip` 文件

5. 点击 "Publish release"

## 📦 Release 内容

- **MakeID.exe** - Windows 可执行文件（76MB）
- **config.json** - 配置文件
- **README.md** - 使用说明
- **Run_MakeID.bat** - 启动脚本

## 🔒 安全提醒

- **不要**将 GitHub 令牌提交到代码仓库
- **不要**在公共场合分享令牌
- 令牌具有仓库访问权限，请妥善保管

## 🎯 下一步

创建 release 后，用户就可以：
1. 下载 Windows 可执行文件
2. 在 Windows 机器上直接运行
3. 无需安装 Python 或其他依赖

---

**选择你喜欢的创建方式即可！** 🎉 