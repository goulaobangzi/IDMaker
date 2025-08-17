# MakeID Windows Executable v1.0.0

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

```
MakeID_Windows_v1.0.0.zip
├── MakeID.exe          # 主程序（76MB）
├── config.json         # 配置文件
├── README.md           # 详细使用说明
└── Run_MakeID.bat     # 快速启动脚本
```

## 🚀 使用方法

### 基本使用
1. 解压 `MakeID_Windows_v1.0.0.zip` 到任意文件夹
2. 双击 `MakeID.exe` 或 `Run_MakeID.bat`
3. 按照提示操作

### 命令行参数
```bash
# 交互模式
MakeID.exe

# 自动模式
MakeID.exe --auto --template Staff --clean

# 自动模式 + 生成家长证
MakeID.exe --auto --template Student --withparent

# 处理指定目录
MakeID.exe --input "photos/"

# 详细输出
MakeID.exe --verbose
```

## 🔧 系统要求

- **操作系统**: Windows 10 或 Windows 11
- **内存**: 建议 4GB 以上
- **存储**: 至少 100MB 可用空间
- **其他**: 无需安装 Python 或其他依赖

## 📋 更新日志

### v1.0.0 (2025-01-XX)
- ✅ 首次发布 Windows 可执行文件版本
- ✅ 集成 DNN 人脸检测模型
- ✅ 支持多种 ID 卡模板
- ✅ 中文姓名自动转换
- ✅ 交互式和自动模式
- ✅ 递归目录搜索
- ✅ 智能输出目录管理

## 🐛 已知问题

- 首次运行可能需要几秒钟加载 DNN 模型
- 大图片处理时间较长（这是正常现象）

## 🔮 未来计划

- [ ] 图形用户界面 (GUI)
- [ ] 批量配置支持
- [ ] 更多模板样式
- [ ] 云端处理支持

## 📞 支持与反馈

如果遇到问题或有建议，请：
1. 查看 `README.md` 中的故障排除部分
2. 在 GitHub 仓库提交 Issue
3. 检查配置文件设置

## 📄 许可证

本项目采用 MIT 许可证。

---

**享受使用 MakeID Photo Generator！** 🎯✨ 