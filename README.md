# ID Card Generation System

## 概述

这是一个完整的ID卡生成系统，整合了三个核心模块：
- **PhotoCropper** (`crop_photo.py`) - 照片裁剪
- **IDCardGenerator** (`make_id.py`) - ID卡生成
- **Chinese Name Converter** (`py_to_en.py`) - 中文姓名转换

## 功能特性

### 1. 照片裁剪阶段
- 自动检测照片中的人脸
- 智能裁剪，避免切头或切下巴
- 支持多种图片格式：`.jpg`, `.jpeg`, `.png`, `.bmp`
- 统一输出为 `.jpg` 格式到 `crop/` 目录

### 2. 中文姓名转换
- 自动检测中文文件名
- 转换为英文拼音格式：`GivenName Surname`（名 姓）
- 重复运行时直接覆盖现有文件

### 3. ID卡生成阶段
- 支持多种模板：Student, Staff, Parent, Resident, Contractor
- 自动加载对应的模板和字体
- 生成带照片和姓名的完整ID卡
- 输出到 `ID/` 目录

### 4. 健壮性特性
- DNN模型加载检查
- 详细的错误处理和日志
- 进度显示和统计汇总
- 支持递归遍历子目录

## 使用方法

### 基本用法

```bash
# 处理当前目录下的所有照片
python main.py

# 处理指定目录
python main.py -i "photos/"

# 处理单个文件
python main.py -i "photo.jpg"

# 递归处理子目录
python main.py -i "photos/" -r

# 清理输出目录后处理
python main.py -i "photos/" --clean
```

**注意**: 模板选择现在是交互式的，不再需要通过命令行参数指定。

### 命令行参数

| 参数 | 简写 | 说明 | 默认值 |
|------|------|------|--------|
| `--input` | `-i` | 输入目录或文件路径 | 当前目录 (`.`) |
| `--no-recursive` | `-n` | 禁用递归搜索 | False（默认启用递归搜索） |
| `--template` | `-t` | ID卡模板类型（已弃用，现在交互式选择） | Student |
| `--config` | `-c` | 统一配置文件 | config.json |
| `--clean` | - | 清理输出目录 | False |

### 支持的模板类型

- `Student` - 学生证模板
- `Staff` - 员工证模板  
- `Parent` - 家长证模板
- `Resident` - 居民证模板
- `Contractor` - 承包商证模板

## 输出目录结构

脚本会根据输入路径动态创建输出目录：

### 处理单个文件时
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

### 处理目录时
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

### 处理当前目录时
```
current_directory/
├── main.py
├── photo1.jpg
├── photo2.jpg
├── crop/           # 裁剪后的照片
│   ├── photo1.jpg
│   └── photo2.jpg
└── ID/             # 生成的ID卡
    ├── Student_photo1.jpg
    └── Student_photo2.jpg
```

## 工作流程

1. **初始化阶段**
   - 加载DNN人脸检测模型
   - 加载ID卡模板和字体
   - 创建输出目录

2. **照片发现阶段**
   - 扫描输入路径（文件或目录）
   - 默认递归搜索所有子目录
   - 可通过 --no-recursive (-n) 禁用递归搜索
   - 过滤支持的图片格式
   - 自动排除程序必要目录（id_template, dnn_models）

3. **照片裁剪阶段**
   - 人脸检测和定位
   - 智能裁剪算法
   - 中文文件名转换
   - 避免重名冲突

4. **用户检查阶段**
   - 提示用户检查裁剪结果
   - 等待用户确认后继续
   - 确保裁剪质量满足要求

5. **模板选择阶段**
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

9. **完成确认**
   - 显示完成状态
   - 等待用户按回车关闭窗口

## 退出码

| 退出码 | 说明 |
|--------|------|
| 0 | 成功完成 |
| 1 | 未发现图片文件 |
| 2 | DNN模型未加载 |
| 3 | 全部照片裁剪失败 |
| 4 | ID卡生成失败 |
| 5 | 模板选择失败 |

## 示例场景

### 场景1：处理当前目录照片
```bash
python main.py
```
- 自动搜索当前目录下的所有照片
- 自动检测中文文件名（如 `余勇.jpg`）
- 转换为英文拼音（`Yong Yu`）
- 裁剪照片并生成学生证
- 交互式选择模板

**注意**: 默认启用递归搜索，系统会自动搜索所有子目录中的照片文件。

### 场景2：处理指定目录照片
```bash
python main.py -i "cn photo/"
```
- 处理指定目录下的所有照片
- 交互式选择模板
- 默认递归搜索所有子目录

### 场景3：禁用递归搜索
```bash
python main.py -i "photos/" --no-recursive
```
- 只搜索指定目录，不搜索子目录
- 交互式选择模板
- 处理指定目录中的照片

## 智能文件过滤

### 自动排除程序目录
系统会自动排除以下程序必要的目录，避免处理其中的图片文件：
- `id_template/` - ID卡模板文件
- `dnn_models/` - 人脸检测模型文件

这些目录中的图片文件不会被处理，确保程序正常运行。

## 交互式功能

### 用户检查阶段
在照片裁剪完成后，系统会暂停并提示用户检查裁剪结果：
- 显示裁剪照片的保存位置
- 等待用户手动检查质量
- 按回车键继续下一步

### 模板选择
系统提供友好的模板选择界面：
```
Please select ID card template:
1. Student
2. Staff
3. Contractor
4. Resident

Enter your choice (1-4):
```

### 家长证生成
当选择Student模板时，系统会询问是否同时生成家长证：
- 自动为所有照片生成家长证
- 使用相同的裁剪照片
- 提高工作效率

### 完成确认
工作流程完成后，窗口不会自动关闭：
- 显示完成状态和统计信息
- 等待用户按回车键关闭
- 避免错过重要信息

## 配置系统

### 统一配置文件

现在所有模块都支持统一的配置文件系统，用户可以通过修改配置文件来调整各种参数，而不需要修改源代码。

**主要配置文件**: `config.json`

**配置内容**:
- **照片裁剪参数**: 输出尺寸、人脸检测、裁剪算法、头发估算等
- **ID卡生成参数**: 模板、照片位置、文字位置、字体等  
- **姓名转换参数**: 拼音样式、姓名格式、回退选项等
- **工作流参数**: 默认模板、输出目录、支持格式等

**使用方法**:
```bash
# 使用默认配置
python main.py -i "photos/"

# 使用自定义配置
python main.py -i "photos/" --config my_config.json
```

### 配置结构

```json
{
  "photo_cropping": {
    "output_dimensions": {
      "width": 360,
      "height": 450
    },
    "face_detection": {
      "method": "dnn",
      "confidence_threshold": 0.5,
      "model_path": "dnn_models/res10_300x300_ssd_iter_140000.caffemodel",
      "prototxt_path": "dnn_models/deploy.prototxt"
    },
    "quality": 95,
    "debug": false,
    "cropping_parameters": {
      "target_head_ratio": 0.75,
      "target_top_margin": 0.08,
      "chin_extra_ratio": 0.12,
      "hair_ratio": {
        "base": 0.25,
        "min": 0.15,
        "max": 0.35,
        "small_face_multiplier": 1.1,
        "large_face_multiplier": 0.6,
        "top_position_multiplier": 0.6,
        "bottom_position_multiplier": 1.0
      }
    }
  },
  "id_card_generation": {
    "template_directory": "id_template",
    "templates": {
      "contractor": "Contractor.png",
      "resident": "Resident.png",
      "staff": "Staff.png",
      "student": "Student.png",
      "parent": "Parent.png"
    },
    "photo_position": {"x": 175, "y": 659, "width": 288, "height": 350},
    "text_position": {
      "name_origin": [175, 1040],
      "max_width": 450,
      "font_size": 42,
      "line_spacing": 16
    },
    "font": {"path": "font.otf", "color": [17, 26, 65]},
    "output_format": "jpg",
    "quality": 95
  },
  "name_conversion": {
    "pinyin_style": "normal",
    "name_format": "givenname_surname",
    "fallback_to_original": true
  },
  "main_workflow": {
    "default_template": "Student",
    "output_directories": {
      "crop": "crop",
      "id": "ID"
    },
    "supported_formats": [".jpg", ".jpeg", ".png", ".bmp"],
    "recursive_search": false,
    "auto_clean": false
  }
}
```

### 配置参数详解

#### 1. 照片裁剪模块 (`photo_cropping`)

##### 输出尺寸 (`output_dimensions`)
- `width`: 裁剪后照片的宽度（像素）
- `height`: 裁剪后照片的高度（像素）

##### 人脸检测 (`face_detection`)
- `method`: 检测方法（目前支持 "dnn"）
- `confidence_threshold`: 置信度阈值（0.0-1.0）
- `model_path`: DNN模型文件路径
- `prototxt_path`: DNN配置文件路径

##### 裁剪参数 (`cropping_parameters`)
- `target_head_ratio`: 头部在裁剪框中的目标比例（0.75 = 75%）
- `target_top_margin`: 顶部留白比例（0.08 = 8%）
- `chin_extra_ratio`: 下巴额外空间比例（0.12 = 12%）

##### 头发比例参数 (`hair_ratio`)
- `base`: 基础头发高度比例
- `min`: 最小头发高度比例
- `max`: 最大头发高度比例
- `small_face_multiplier`: 小脸时的倍数
- `large_face_multiplier`: 大脸时的倍数
- `top_position_multiplier`: 脸部靠近顶部时的倍数
- `bottom_position_multiplier`: 脸部靠近底部时的倍数

##### 其他参数
- `quality`: JPEG输出质量（1-100）
- `debug`: 是否生成调试图像

#### 2. ID卡生成模块 (`id_card_generation`)

##### 模板配置
- `template_directory`: 模板文件目录
- `templates`: 各种模板的映射关系

##### 照片位置 (`photo_position`)
- `x`, `y`: 照片在ID卡上的位置
- `width`, `height`: 照片的尺寸

##### 文字位置 (`text_position`)
- `name_origin`: 姓名文字的起始位置 [x, y]
- `max_width`: 文字最大宽度
- `font_size`: 字体大小
- `line_spacing`: 行间距

##### 字体配置 (`font`)
- `path`: 字体文件路径
- `color`: 字体颜色 [R, G, B]

##### 输出配置
- `output_format`: 输出格式（jpg, png等）
- `quality`: 输出质量

#### 3. 姓名转换模块 (`name_conversion`)

##### 拼音样式 (`pinyin_style`)
- `"normal"`: 标准拼音
- `"first_letter"`: 首字母
- `"tone"`: 带声调
- `"tone2"`: 数字声调

##### 姓名格式 (`name_format`)
- `"givenname_surname"`: 名 姓（默认）
- `"surname_givenname"`: 姓 名

##### 回退选项 (`fallback_to_original`)
- `true`: 转换失败时返回原中文名
- `false`: 转换失败时返回空字符串

#### 4. 主工作流模块 (`main_workflow`)

##### 默认设置
- `default_template`: 默认模板类型
- `output_directories`: 输出目录名称
- `supported_formats`: 支持的图片格式
- `recursive_search`: 是否递归搜索
- `auto_clean`: 是否自动清理

### 配置使用方法

#### 1. 使用配置文件

```bash
python main.py -i "input_folder" -t Staff --config config.json
```

#### 2. 不使用配置文件（使用默认值）

```bash
python main.py -i "input_folder" -t Staff
```

#### 3. 修改配置参数

1. 复制 `config.json` 为 `my_config.json`
2. 修改需要的参数
3. 使用 `--config my_config.json` 运行

### 配置优先级

1. **命令行参数** > **配置文件** > **默认值**
2. 配置文件中的参数会与默认值进行深度合并
3. 缺失的配置项会使用默认值

### 示例配置修改

#### 调整裁剪参数

```json
{
  "photo_cropping": {
    "cropping_parameters": {
      "target_head_ratio": 0.80,
      "target_top_margin": 0.05
    }
  }
}
```

#### 修改姓名格式

```json
{
  "name_conversion": {
    "name_format": "surname_givenname"
  }
}
```

#### 调整ID卡照片位置

```json
{
  "id_card_generation": {
    "photo_position": {
      "x": 200,
      "y": 700,
      "width": 300,
      "height": 400
    }
  }
}
```

## 依赖要求

- Python 3.6+
- OpenCV (cv2)
- NumPy
- Pillow (PIL)
- pypinyin
- pathlib

## 故障排除

### 常见问题

1. **"DNN face detection model not loaded"**
   - 检查 `dnn_models/` 目录是否存在
   - 确认模型文件完整

2. **"Template not loaded"**
   - 检查 `id_template/` 目录
   - 确认模板文件存在

3. **"Font not loaded"**
   - 检查 `font.otf` 文件
   - 确认字体文件可访问

### 调试模式

在 `config.json` 中设置 `"debug": true` 可以启用调试模式，生成带标记的调试图片。

## 性能优化

- 批量处理比单个处理效率更高
- 递归选项会增加处理时间
- 大图片会显著增加处理时间

## 注意事项

- 确保有足够的磁盘空间存储输出文件
- 中文文件名转换基于拼音，可能需要人工检查
- 重复运行时会直接覆盖现有文件，无需担心文件名冲突
- 建议在处理大量文件前先测试小批量
- 输出目录会在每次运行时自动创建
- **配置文件修改后立即生效，无需重启程序**

## 配置系统特性

### 智能配置加载

每个模块都实现了智能配置加载：

```python
def load_config(self, config_file):
    # 1. 定义默认配置
    default_config = { ... }
    
    try:
        # 2. 尝试加载用户配置文件
        with open(config_file, 'r', encoding='utf-8') as f:
            user_config = json.load(f)
            # 3. 深度合并用户配置和默认配置
            return self._merge_config(default_config, user_config)
    except Exception as e:
        # 4. 如果加载失败，使用默认配置
        print(f"Warning: Could not load config file '{config_file}': {e}")
        print("Using default configuration")
        return default_config
```

### 深度配置合并

系统支持深度合并用户配置和默认配置，确保所有参数都有合理的默认值。

### 配置文件验证

系统会自动验证配置参数的有效性，无效参数会回退到默认值。

### 热重载支持

修改配置文件后，重新运行程序即可生效，无需重启。 