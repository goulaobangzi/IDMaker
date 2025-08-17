# MakeID Photo Generator

[English](#english) | [中文](#中文)

---

## English

### Overview

A complete ID card generation system that integrates three core modules:
- **PhotoCropper** (`crop_photo.py`) - Photo cropping and face detection
- **IDCardGenerator** (`make_id.py`) - ID card generation
- **Chinese Name Converter** (`py_to_en.py`) - Chinese name conversion to Pinyin

### Features

- **Smart Face Detection**: DNN-based face detection and intelligent cropping
- **Multiple Templates**: Student, Staff, Parent, Resident, Contractor
- **Chinese Name Support**: Automatic conversion to English Pinyin
- **Interactive Workflow**: User-friendly prompts and confirmations
- **Auto Mode**: Fully automated batch processing
- **Recursive Search**: Process photos in subdirectories automatically

### Quick Start

```bash
# Interactive mode
python main.py

# Auto mode
python main.py --auto --template Staff --clean

# Process specific directory
python main.py --input "photos/"
```

### Detailed Usage

#### Basic Usage

```bash
# Process all photos in current directory
python main.py

# Process specified directory
python main.py --input "photos/"

# Process single file
python main.py --input "photo.jpg"

# Recursive processing (enabled by default)
python main.py --input "photos/"

# Disable recursive search
python main.py --input "photos/" --no-recursive

# Clean output directories before processing
python main.py --input "photos/" --clean
```

#### Command Line Parameters

| Parameter | Description | Default |
|-----------|-------------|---------|
| `--input` | Input directory or file path | Current directory (`.`) |
| `--no-recursive` | Disable recursive search | False (recursive enabled by default) |
| `--template` | ID card template type | Student |
| `--config` | Configuration file path | config.json |
| `--clean` | Clean output directories | False |
| `--verbose` | Verbose output mode | False |
| `--auto` | Auto mode (skip interactions) | False |
| `--withparent` | Generate parent cards (Student template only) | False |

#### Supported Template Types

- `Student` - Student ID template
- `Staff` - Staff ID template  
- `Parent` - Parent ID template
- `Resident` - Resident ID template
- `Contractor` - Contractor ID template

### Output Directory Structure

The script dynamically creates output directories based on input paths:

#### Processing Single Files
```
photos/
├── photo1.jpg
├── photo2.jpg
├── crop/           # Cropped photos
│   ├── photo1.jpg
│   └── photo2.jpg
└── ID/             # Generated ID cards
    ├── Student_photo1.jpg
    └── Student_photo2.jpg
```

#### Processing Directories
```
input_directory/
├── photo1.jpg
├── photo2.jpg
├── crop/           # Cropped photos
│   ├── photo1.jpg
│   └── photo2.jpg
└── ID/             # Generated ID cards
    ├── Student_photo1.jpg
    └── Student_photo2.jpg
```

### Workflow

1. **Initialization Phase**
   - Load DNN face detection model
   - Load ID card templates and fonts
   - Create output directories

2. **Photo Discovery Phase**
   - Scan input paths (files or directories)
   - Recursive search of all subdirectories by default
   - Can be disabled with `--no-recursive`
   - Filter supported image formats
   - Automatically exclude program directories (id_template, dnn_models, crop, ID)

3. **Photo Cropping Phase**
   - Face detection and positioning
   - Intelligent cropping algorithm
   - Chinese filename conversion
   - Avoid naming conflicts

4. **User Review Phase** (non-auto mode)
   - Prompt user to review cropping results
   - Wait for user confirmation to continue
   - Ensure cropping quality meets requirements

5. **Template Selection Phase** (non-auto mode)
   - Interactive ID card template selection
   - Support for Student, Staff, Contractor, Resident
   - User-friendly selection interface

6. **ID Card Generation Phase**
   - Load selected template
   - Composite photos and names
   - Save in specified format

7. **Parent Card Generation Phase** (optional)
   - If Student template is selected, ask about generating parent cards
   - Automatically generate parent cards for all photos

8. **Statistical Summary**
   - Total processing statistics
   - Success/failure counts
   - Output directory information

### Auto Mode

Use the `--auto` parameter to enable fully automatic mode:

```bash
# Auto mode example
python main.py --auto --template Staff --clean

# Auto mode + generate parent cards
python main.py --auto --template Student --withparent
```

**Auto Mode Features**:
- Skip naming requirement confirmation
- Skip post-cropping user review
- Skip template selection (use `--template` parameter)
- Automatically close window

### Configuration System

#### Unified Configuration File

The system supports a unified configuration file `config.json` containing:

- **Photo Cropping Parameters**: Output dimensions, face detection, cropping algorithms, etc.
- **ID Card Generation Parameters**: Templates, photo positions, text positions, fonts, etc.
- **Name Conversion Parameters**: Pinyin styles, name formats, fallback options, etc.

#### Configuration Loading Priority

1. **Command Line Parameters** > **Configuration File** > **Default Values**
2. Configuration file parameters are deeply merged with default values
3. Missing configuration items use default values

### Requirements

- **Python**: 3.6+
- **OpenCV** (cv2)
- **NumPy**
- **Pillow** (PIL)
- **pypinyin**
- **pathlib**

### Troubleshooting

#### Common Issues

1. **"DNN face detection model not loaded"**
   - Check if `dnn_models/` directory exists
   - Confirm model files are complete

2. **"Template not loaded"**
   - Check `id_template/` directory
   - Confirm template files exist

3. **"Font not loaded"**
   - Check `font.otf` file
   - Confirm font file is accessible

### Notes

- Ensure sufficient disk space for output files
- Chinese filename conversion is based on Pinyin and may require manual verification
- Re-running will directly overwrite existing files without filename conflicts
- Test with small batches before processing large numbers of files
- Output directories are automatically created on each run
- Configuration file changes take effect immediately without restart
- Using `--clean` parameter completely deletes output directories
- Program automatically excludes `crop/` and `ID/` directories to avoid processing output files

---

## 中文

### 概述

这是一个完整的ID卡生成系统，整合了三个核心模块：
- **PhotoCropper** (`crop_photo.py`) - 照片裁剪和人脸检测
- **IDCardGenerator** (`make_id.py`) - ID卡生成
- **Chinese Name Converter** (`py_to_en.py`) - 中文姓名转换为拼音

### 功能特性

- **智能人脸检测**: 基于DNN的人脸检测和智能裁剪
- **多模板支持**: Student, Staff, Parent, Resident, Contractor
- **中文姓名支持**: 自动转换为英文拼音
- **交互式工作流**: 用户友好的提示和确认
- **自动模式**: 完全自动化的批量处理
- **递归搜索**: 自动处理子目录中的照片

### 快速开始

```bash
# 交互模式
python main.py

# 自动模式
python main.py --auto --template Staff --clean

# 处理指定目录
python main.py --input "photos/"
```

### 详细使用方法

#### 基本用法

```bash
# 处理当前目录下的所有照片
python main.py

# 处理指定目录
python main.py --input "photos/"

# 处理单个文件
python main.py --input "photo.jpg"

# 递归处理子目录（默认启用）
python main.py --input "photos/"

# 禁用递归搜索
python main.py --input "photos/" --no-recursive

# 清理输出目录后处理
python main.py --input "photos/" --clean
```

#### 命令行参数

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `--input` | 输入目录或文件路径 | 当前目录 (`.`) |
| `--no-recursive` | 禁用递归搜索 | False（默认启用递归搜索） |
| `--template` | ID卡模板类型 | Student |
| `--config` | 配置文件路径 | config.json |
| `--clean` | 清理输出目录 | False |
| `--verbose` | 详细输出模式 | False |
| `--auto` | 自动模式（跳过交互） | False |
| `--withparent` | 生成家长证（仅Student模板） | False |

#### 支持的模板类型

- `Student` - 学生证模板
- `Staff` - 员工证模板  
- `Parent` - 家长证模板
- `Resident` - 居民证模板
- `Contractor` - 承包商证模板

### 输出目录结构

脚本会根据输入路径动态创建输出目录：

#### 处理单个文件时
```
photos/
├── photo1.jpg
├── photo2.jpg
├── crop/           # 裁剪后的照片
│   ├── photo1.jpg
│   └── photo2.jpg
└── ID/             # 生成的ID卡
    ├── Student_photo1.jpg
    └── Student_photo2.jpg
```

#### 处理目录时
```
input_directory/
├── photo1.jpg
├── photo2.jpg
├── crop/           # 裁剪后的照片
│   ├── photo1.jpg
│   └── photo2.jpg
└── ID/             # 生成的ID卡
    ├── Student_photo1.jpg
    └── Student_photo2.jpg
```

### 工作流程

1. **初始化阶段**
   - 加载DNN人脸检测模型
   - 加载ID卡模板和字体
   - 创建输出目录

2. **照片发现阶段**
   - 扫描输入路径（文件或目录）
   - 默认递归搜索所有子目录
   - 可通过 `--no-recursive` 禁用递归搜索
   - 过滤支持的图片格式
   - 自动排除程序必要目录（id_template, dnn_models, crop, ID）

3. **照片裁剪阶段**
   - 人脸检测和定位
   - 智能裁剪算法
   - 中文文件名转换
   - 避免重名冲突

4. **用户检查阶段**（非自动模式）
   - 提示用户检查裁剪结果
   - 等待用户确认后继续
   - 确保裁剪质量满足要求

5. **模板选择阶段**（非自动模式）
   - 交互式选择ID卡模板
   - 支持 Student, Staff, Contractor, Resident
   - 用户友好的选择界面

6. **ID卡生成阶段**
   - 加载选定模板
   - 合成照片和姓名
   - 保存为指定格式

7. **家长证生成阶段**（可选）
   - 如果选择Student模板，询问是否生成家长证
   - 自动为所有照片生成家长证

8. **统计汇总**
   - 处理总数统计
   - 成功/失败数量
   - 输出目录信息

### 自动模式

使用 `--auto` 参数可以启用完全自动模式：

```bash
# 自动模式示例
python main.py --auto --template Staff --clean

# 自动模式 + 生成家长证
python main.py --auto --template Student --withparent
```

**自动模式特性**:
- 跳过命名要求确认
- 跳过裁剪后用户检查
- 跳过模板选择（使用 `--template` 参数）
- 自动关闭窗口

### 配置系统

#### 统一配置文件

系统支持统一的配置文件 `config.json`，包含：

- **照片裁剪参数**: 输出尺寸、人脸检测、裁剪算法等
- **ID卡生成参数**: 模板、照片位置、文字位置、字体等  
- **姓名转换参数**: 拼音样式、姓名格式、回退选项等

#### 配置加载优先级

1. **命令行参数** > **配置文件** > **默认值**
2. 配置文件中的参数会与默认值进行深度合并
3. 缺失的配置项会使用默认值

### 依赖要求

- **Python**: 3.6+
- **OpenCV** (cv2)
- **NumPy**
- **Pillow** (PIL)
- **pypinyin**
- **pathlib**

### 故障排除

#### 常见问题

1. **"DNN face detection model not loaded"**
   - 检查 `dnn_models/` 目录是否存在
   - 确认模型文件完整

2. **"Template not loaded"**
   - 检查 `id_template/` 目录
   - 确认模板文件存在

3. **"Font not loaded"**
   - 检查 `font.otf` 文件
   - 确认字体文件可访问

### 注意事项

- 确保有足够的磁盘空间存储输出文件
- 中文文件名转换基于拼音，可能需要人工检查
- 重复运行时会直接覆盖现有文件，无需担心文件名冲突
- 建议在处理大量文件前先测试小批量
- 输出目录会在每次运行时自动创建
- 配置文件修改后立即生效，无需重启程序
- 使用 `--clean` 参数会完全删除输出目录
- 程序会自动排除 `crop/` 和 `ID/` 目录，避免处理输出文件

---

## System Requirements

- **Python**: 3.6+
- **OS**: Windows 10/11, macOS, Linux
- **Dependencies**: OpenCV, NumPy, Pillow, pypinyin

## Installation

```bash
git clone https://github.com/goulaobangzi/IDMaker.git
cd IDMaker
pip install -r requirements.txt
```

## License

This project is licensed under the MIT License.

---

## 系统要求

- **Python**: 3.6+
- **操作系统**: Windows 10/11, macOS, Linux
- **依赖**: OpenCV, NumPy, Pillow, pypinyin

## 安装

```bash
git clone https://github.com/goulaobangzi/IDMaker.git
cd IDMaker
pip install -r requirements.txt
```

## 许可证

本项目采用 MIT 许可证。
