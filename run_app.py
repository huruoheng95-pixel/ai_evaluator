import os
import sys
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()


def run_streamlit_app():
    """运行Streamlit应用"""
    import subprocess
    
    # 构建运行命令
    cmd = [
        sys.executable, "-m", "streamlit", "run", 
        "ai_qa_evaluator.py",
        "--server.port", "8501",
        "--server.address", "0.0.0.0"
    ]
    
    # 从环境变量获取端口配置
    port = os.getenv("STREAMLIT_PORT", "8501")
    host = os.getenv("STREAMLIT_HOST", "0.0.0.0")
    
    cmd = [
        sys.executable, "-m", "streamlit", "run", 
        "ai_qa_evaluator.py",
        "--server.port", port,
        "--server.address", host
    ]
    
    print("启动AI问答质量评测智能体...")
    print(f"访问地址: http://{host}:{port}")
    
    # 运行Streamlit应用
    result = subprocess.run(cmd)
    
    if result.returncode != 0:
        print(f"应用启动失败，错误代码: {result.returncode}")
        sys.exit(result.returncode)


def install_dependencies():
    """安装依赖包"""
    import subprocess
    
    print("正在安装依赖包...")
    result = subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], shell=True)
    
    if result.returncode != 0:
        print(f"依赖安装失败，错误代码: {result.returncode}")
        sys.exit(result.returncode)
    else:
        print("依赖包安装成功")


if __name__ == "__main__":
    # 检查是否需要安装依赖
    if "--install" in sys.argv:
        install_dependencies()
    
    run_streamlit_app()