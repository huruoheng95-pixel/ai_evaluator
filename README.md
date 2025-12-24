# AI问答质量评测智能体

这是一个基于Streamlit的Web应用，可以对问答内容进行质量评估并提供修改建议。系统根据环境变量自动选择模型提供商（OpenAI或国内大模型如通义千问）。

## 功能特性

- 直观的Web界面
- 根据环境变量自动选择模型提供商
- 多维度质量评估
- 生成详细的评测报告
- 支持导出Markdown格式报告

## 快速开始

1. 安装依赖：
   ```bash
   python run_app.py --install
   ```

2. 启动应用：
   ```bash
   python run_app.py
   ```

3. 访问 `http://localhost:8501`

## 项目结构

- `ai_qa_evaluator.py` - 主应用文件
- `requirements.txt` - 依赖包列表
- `.env` - 环境变量配置
- `run_app.py` - 启动脚本
- `USAGE.md` - 详细使用说明

## 配置

在使用前需要配置API密钥，在`.env`文件中设置：

- `OPENAI_API_KEY` - OpenAI API密钥（如果设置，将优先使用OpenAI）
- `CUSTOM_API_BASE_URL` - 国内大模型API的Base URL
- `CUSTOM_API_KEY` - 国内大模型API密钥
- `SELECTED_MODEL` - 选择的模型名称（如qwen-plus）

系统会根据环境变量自动决定使用哪个模型提供商：
- 如果设置了 `OPENAI_API_KEY`，则使用OpenAI模型
- 否则，如果设置了 `CUSTOM_API_KEY`，则使用国内大模型

## 使用方法

1. 配置环境变量
2. 在侧边栏设置评测标准（可编辑默认标准）
3. 输入问题和答案
4. 点击"开始评测"
5. 查看结果并下载报告

更多详情请查看 `USAGE.md`。