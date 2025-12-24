# AI问答质量评测智能体使用说明

## 项目概述

这是一个基于Streamlit的Web应用，允许用户输入评测标准、问题和答案，然后使用AI模型对答案质量进行评测，并提供修改建议。系统根据环境变量自动选择模型提供商（OpenAI或国内大模型）。

## 功能特性

- 用户友好的Web界面
- 根据环境变量自动选择模型提供商
- 多维度评测（准确性、完整性、相关性、可读性等）
- 详细的评分和修改建议
- 评测结果导出为Markdown文件

## 系统要求

- Python 3.8+
- pip包管理器

## 安装步骤

1. 克隆或下载项目文件
2. 安装依赖包：
   ```bash
   python -m pip install -r requirements.txt
   ```
   或者使用启动脚本安装：
   ```bash
   python run_app.py --install
   ```

## 配置说明

### 环境变量配置

复制 `.env` 文件并填入相应的API密钥：

```bash
# OpenAI API密钥（如果配置此项，将优先使用OpenAI）
OPENAI_API_KEY=your_openai_api_key_here

# 自定义模型API配置（当未配置OpenAI API时使用）
CUSTOM_API_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1
CUSTOM_API_KEY=your_custom_api_key_here
SELECTED_MODEL=qwen-plus

# 其他配置项
OPENAI_API_BASE=
STREAMLIT_PORT=8501
STREAMLIT_HOST=0.0.0.0
```

**注意**：系统会根据环境变量自动决定使用哪个模型提供商：
- 如果设置了 `OPENAI_API_KEY`，则使用OpenAI模型
- 否则，如果设置了 `CUSTOM_API_KEY`，则使用国内大模型
- 如果两者都没有设置，默认使用OpenAI（但会因缺少API密钥而失败）

## 使用方法

1. 启动应用：
   ```bash
   python run_app.py
   ```

2. 在浏览器中打开 `http://localhost:8501`

3. 在侧边栏设置评测标准（可编辑默认标准）
4. 在主界面输入：
   - 问题：待评测的问题内容
   - 答案：待评测的答案内容

4. 点击"开始评测"按钮

5. 查看评测结果并下载Markdown报告

## 评测维度

系统将从以下维度对答案进行评测：

- **准确性**：答案是否正确
- **完整性**：答案是否全面
- **相关性**：答案是否切题
- **可读性**：答案是否清晰易懂
- **整体评分**：综合评分（1-10分）
- **修改建议**：具体的改进意见
- **修改后的答案**：优化后的答案

## 输出结果

评测完成后，系统会显示：

1. 各维度的详细评估
2. 整体评分（1-10分）
3. 具体修改建议
4. 修改后的答案
5. 下载评测报告的选项

## 常见问题

### API密钥错误
- 检查API密钥是否正确
- 确认API服务是否可用

### 网络连接问题
- 检查网络连接
- 确认API URL是否正确

### 评测结果不满意
- 尝试调整评测标准