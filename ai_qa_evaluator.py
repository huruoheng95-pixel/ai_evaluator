import streamlit as st
import openai
import os
from typing import Dict, List, Optional
import requests
from openai import OpenAI


def get_default_criteria():
    """获取默认评测标准"""
    return """一、核心评分维度与逻辑
1. 数据准确性
权重：30%，满分：5分。
评分逻辑：数据溯源与一致性。核对引用的所有财务数据是否与官方财报原文完全一致，是否存在臆造或错误解读。
具体评价标准：5分表示所有数据精准无误，来源明确；3-4分表示核心数据准确，但个别非关键数据有细微偏差；1-2分表示出现关键数据错误或混淆；0分表示数据严重失实或凭空捏造。
2. 财务逻辑严谨性
权重：25%，满分：5分。
评分逻辑：专业框架应用。分析是否建立在正确的财务分析框架上，逻辑链条是否完整、自洽。
具体评价标准：5分表示严格遵循财务分析准则，指标计算正确，逻辑环环相扣；3-4分表示框架基本正确，但部分关联分析不够深入；1-2分表示存在明显财务概念错误或逻辑断裂；0分表示分析完全不符合财务逻辑。
3. 商业洞察力
权重：25%，满分：5分。
评分逻辑：超越数字的解读。能否穿透财务数字，结合行业趋势、竞争格局、公司战略与管理层指引，提炼出影响未来价值的核心驱动因素与风险。
具体评价标准：5分表示精准识别业绩变动的根本动因，预判关键趋势，提供独到前瞻观点；3-4分表示能正确联系业务与财务，但洞察较为常规；1-2分表示仅停留在数字描述层面，或无根据的猜测；0分表示完全复述财报文字，无任何洞察。
4. 表达与结构化
权重：20%，满分：5分。
评分逻辑：信息组织与可读性。结构是否清晰，能否用恰当图表呈现复杂数据，语言是否专业且易懂。
具体评价标准：5分表示结构犹如分析师报告，重点突出，可视化元素有效辅助理解；3-4分表示结构完整，但重点不突出或表达稍显冗长；1-2分表示结构混乱，语言晦涩或存在大量无关信息；0分表示难以阅读和理解。
二、综合评价与等级划分
综合得分4.5 - 5.0：等级为"专业分析师级"。能力描述为可直接辅助专业投资决策，在数据、逻辑和洞察上均表现出色。
综合得分3.5 - 4.4：等级为"资深助理级"。能力描述为能可靠地完成基础分析和数据整理，部分洞察有参考价值。
综合得分2.5 - 3.4：等级为"合格实习生级"。能力描述为能保证基础数据准确，但缺乏深入分析和连接业务的能力。
综合得分1.0 - 2.4：等级为"有待改进级"。能力描述为存在错误或仅能进行简单的信息复述，无法提供有效分析。
综合得分低于1.0：等级为"不适用级"。能力描述为无法完成基本的财报分析任务。"""


def set_page_config():
    """设置页面配置"""
    st.set_page_config(
        page_title="AI问答质量评测智能体",
        page_icon="🤖",
        layout="wide"
    )


def initialize_session_state():
    """初始化会话状态"""
    if "evaluation_result" not in st.session_state:
        st.session_state.evaluation_result = None
    if "modified_answer" not in st.session_state:
        st.session_state.modified_answer = ""
    if "api_key" not in st.session_state:
        st.session_state.api_key = ""
    if "model_provider" not in st.session_state:
        st.session_state.model_provider = "openai"  # 默认使用OpenAI
    if "custom_base_url" not in st.session_state:
        st.session_state.custom_base_url = ""
    if "custom_api_key" not in st.session_state:
        st.session_state.custom_api_key = ""
    # 从环境变量加载配置
    from dotenv import load_dotenv
    load_dotenv()
    
    # 设置模型提供商和API配置
    openai_key = os.getenv("OPENAI_API_KEY", "")
    custom_api_key = os.getenv("CUSTOM_API_KEY", "")
    custom_base_url = os.getenv("CUSTOM_API_BASE_URL", "https://dashscope.aliyuncs.com/compatible-mode/v1")
    
    if openai_key:
        st.session_state.model_provider = "openai"
        st.session_state.api_key = openai_key
    elif custom_api_key:
        st.session_state.model_provider = "custom"
        st.session_state.custom_api_key = custom_api_key
        st.session_state.custom_base_url = custom_base_url
    else:
        st.session_state.model_provider = "custom"  # 默认使用国内大模型
        st.session_state.custom_api_key = os.getenv("CUSTOM_API_KEY", "")  # 从环境变量获取
        st.session_state.custom_base_url = os.getenv("CUSTOM_API_BASE_URL", "https://dashscope.aliyuncs.com/compatible-mode/v1")
    
    if "selected_model" not in st.session_state:
        st.session_state.selected_model = os.getenv("SELECTED_MODEL", "qwen3-max")


def create_sidebar():
    """创建侧边栏"""
    with st.sidebar:
        st.header("配置")
        
        # 默认评测标准
        default_criteria = get_default_criteria()
        
        evaluation_criteria = st.text_area(
            "评测标准", 
            value=default_criteria,
            height=200,
            key="sidebar_criteria"
        )
        
        st.session_state.evaluation_criteria = evaluation_criteria
        
        st.text("AI评测系统")


def create_input_section():
    """创建输入区域"""
    st.title("🤖 AI问答质量评测智能体")
    st.markdown("输入问题和答案，AI将根据侧边栏设置的评测标准对答案质量进行评测并提供修改建议")
    
    col1, col2 = st.columns(2)
    
    with col1:
        question = st.text_area(
            "问题", 
            height=150,
            placeholder="请输入问题"
        )
    
    with col2:
        answer = st.text_area(
            "答案", 
            height=150,
            placeholder="请输入待评测的答案"
        )
    
    # 从侧边栏获取评测标准
    default_criteria = get_default_criteria()
    evaluation_criteria = st.session_state.get("evaluation_criteria", default_criteria)
    
    return evaluation_criteria, question, answer


def generate_evaluation_prompt(criteria: str, question: str, answer: str) -> str:
    """生成AI评测提示"""
    prompt = f"""
    #角色
    你是一位专业的美股财报分析回答评价专家，具备扎实的美股财报知识、金融分析能力及评分经验，能够按照技能精准判断美股财报分析回答的合格性与问题点。
    #技能
    1. 根据评测标准{criteria}对问题{question}的答案{answer}进行评价分析，必须按照评测标准的要求生成结构化评分报告；  
    2. 工具输出内容需包含：分项评分和综合评价。 
    #回复示例（评分结果）
    一、分项评分
    1. 数据准确性 | 得分：5/5分
    评分依据：所有核心财务数据均精确无误，如"2025年Q3营收1802亿美元"、"经营现金流1307亿美元"、"25亿美元FTC和解金"等数据均与SEC公开文件一致。数据来源明确，如明确指出"根据2025年第三季度财报"，具备了良好的可追溯性。无任何臆造或关键数据错误。
    2. 财务逻辑严谨性 | 得分：4.5/5分
    评分依据：分析框架完整，涵盖经营现金流、自由现金流、资本开支的关联分析，正确区分了"非现金支出"对利润和现金流的不同影响。准确解读了"25亿美元特殊支出"的性质（非现金、一次性、法律准备金）。
    细微扣分点：可进一步加强三张报表间的勾稽关系说明，如巨额资本开支对资产负债表"长期资产"科目的具体影响。
    3. 商业洞察力 | 得分：4/5分
    评分依据：超越数字的解读：不仅报告了现金流"一强一弱"的现象，更将其本质提炼为 "战略性主动投资期" ，并点明这是 "播种期" 的典型特征。连接战略与财务：将1250亿美元的资本开支与AWS的2000亿美元未履约订单、AI竞争格局直接关联，解释了投资背后的商业逻辑。识别核心风险：明确指出"投资回报风险"为最大风险，而非表面上的现金流紧张。提升空间：对亚马逊各业务线（AWS/电商/广告）如何具体协同形成"飞轮效应"以支撑未来增长，可给出更细致的推演。
    4. 表达与结构化 | 得分：5/5分
    评分依据：结构清晰：采用"核心结论→分项剖析→风险提示→总结判断"的逻辑链条，符合专业报告范式。重点突出：使用对比（经营现金流 vs 自由现金流）、比喻（"面包与烤箱"）等手法，使复杂概念易于理解。
    可视化辅助：有效运用虚拟表格对比数据，使"冰火两重天"的结论一目了然。语言专业且流畅：准确使用"未履约订单"、"资本开支"、"非现金支出"等术语，表述严谨。
    二、综合评价
    1. 各维度加权总分计算
    数据准确性：5分 × 30% = 1.50分
    财务逻辑严谨性：4.5分 × 25% = 1.125分
    商业洞察力：4分 × 25% = 1.00分
    表达与结构化：5分 × 20% = 1.00分
    加权总分：1.50 + 1.125 + 1.00 + 1.00 = 4.625分
    2. 综合评价与等级划分
    最终等级：专业分析师级（得分区间：4.5 - 5.0分）
    综合评语：该分析数据准确，财务分析框架严谨，能正确解读特殊项目的会计影响，并清晰阐释了现金流状况背后的战略意图。其核心价值在于展现了出色的商业洞察力，将激进的资本开支与公司的AI战略和长期竞争壁垒相关联，并准确识别了最主要的投资回报风险。整体达到了可辅助专业投资决策的水平。
    #限制
    - 仅评价美股财报分析类回答（拒绝评价A股、港股财报或非分析类问题）；  
    - 评分需基于技能中的标准，禁止主观评价，避免模糊表述（如"回答太简单"）；  
    - 输出格式需严格包含"分项评分+综合评价"两部分，关键数据需标注来源（如"财报数据：XX公司2024年Q3 10-K报告"）；
    """
    return prompt


def call_ai_evaluation(prompt: str) -> tuple[Optional[Dict[str, str]], str]:
    """调用AI进行评测，返回(解析结果, 原始响应)"""
    try:
        if st.session_state.model_provider == "openai":
            response_content = call_openai_evaluation_raw(prompt)
        else:
            response_content = call_custom_model_evaluation_raw(prompt)
        
        if response_content:
            parsed_result = parse_evaluation_result(response_content)
            return parsed_result, response_content
        else:
            return None, ""
    except Exception as e:
        st.error(f"AI评测过程中出现错误: {str(e)}")
        return None, ""


def call_openai_evaluation(prompt: str) -> Optional[Dict[str, str]]:
    """使用OpenAI API进行评测"""
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,
        max_tokens=2000
    )
    
    content = response.choices[0].message.content
    return parse_evaluation_result(content)


def call_openai_evaluation_raw(prompt: str) -> str:
    """使用OpenAI API进行评测，返回原始响应"""
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,
        max_tokens=2000
    )
    
    content = response.choices[0].message.content
    return content


def call_custom_model_evaluation(prompt: str) -> Optional[Dict[str, str]]:
    """使用自定义模型API进行评测（兼容DashScope等国内模型API）"""
    # 使用OpenAI兼容模式
    client = OpenAI(
        api_key=st.session_state.custom_api_key,
        base_url=st.session_state.custom_base_url
    )
    
    response = client.chat.completions.create(
        model=st.session_state.selected_model if hasattr(st.session_state, 'selected_model') and st.session_state.selected_model else "gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,
        max_tokens=2000
    )
    
    content = response.choices[0].message.content
    return parse_evaluation_result(content)


def call_custom_model_evaluation_raw(prompt: str) -> str:
    """使用自定义模型API进行评测（兼容DashScope等国内模型API），返回原始响应"""
    # 使用OpenAI兼容模式
    client = OpenAI(
        api_key=st.session_state.custom_api_key,
        base_url=st.session_state.custom_base_url
    )
    
    response = client.chat.completions.create(
        model=st.session_state.selected_model if hasattr(st.session_state, 'selected_model') and st.session_state.selected_model else "gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,
        max_tokens=2000
    )
    
    content = response.choices[0].message.content
    return content


def parse_evaluation_result(content: str) -> Dict[str, str]:
    """解析AI返回的评测结果"""
    result = {}
    
    # 分割内容按标记
    if "一、分项评分" in content and "二、综合评价" in content:
        # 正确分割分项评分和综合评价
        parts = content.split("二、综合评价")
        first_part = parts[0].split("一、分项评分")[1] if "一、分项评分" in parts[0] else ""
        second_part = parts[1]
        
        sections = {
            "分项评分": first_part.strip(),
            "综合评价": second_part.split("#限制")[0].strip() if "#限制" in second_part else second_part.strip(),
        }
    else:
        # 如果没有标准格式，将整个内容放入综合评价
        sections = {
            "分项评分": "",
            "综合评价": content,
        }
    
    # 解析分项评分中的各个子项
    if sections["分项评分"]:
        import re
        # 提取各项评分
        data_accuracy_match = re.search(r'(1\. 数据准确性.*?)2\.|1\. 数据准确性.*?(?=二、|$)', sections["分项评分"], re.DOTALL)
        financial_logic_match = re.search(r'(2\. 财务逻辑严谨性.*?)3\.|2\. 财务逻辑严谨性.*?(?=二、|$)', sections["分项评分"], re.DOTALL)
        business_insight_match = re.search(r'(3\. 商业洞察力.*?)4\.|3\. 商业洞察力.*?(?=二、|$)', sections["分项评分"], re.DOTALL)
        expression_match = re.search(r'(4\. 表达与结构化.*?)\n\n|4\. 表达与结构化.*?(?=二、|$)', sections["分项评分"], re.DOTALL)
        
        if data_accuracy_match:
            matched_text = data_accuracy_match.group(1)
            sections["数据准确性"] = matched_text.strip() if matched_text else ""
        if financial_logic_match:
            matched_text = financial_logic_match.group(1)
            sections["财务逻辑严谨性"] = matched_text.strip() if matched_text else ""
        if business_insight_match:
            matched_text = business_insight_match.group(1)
            sections["商业洞察力"] = matched_text.strip() if matched_text else ""
        if expression_match:
            matched_text = expression_match.group(1)
            sections["表达与结构化"] = matched_text.strip() if matched_text else ""
    
    return sections


def display_evaluation_result(result: Dict[str, str]):
    """展示评测结果"""
    if result:
        st.subheader("📊 评测结果")
        
        # 显示分项评分
        if result.get("分项评分"):
            st.markdown("### 一、分项评分")
            
            # 显示各项评分详情
            if result.get("数据准确性"):
                with st.expander("1. 数据准确性", expanded=True):
                    st.write(result["数据准确性"])
            
            if result.get("财务逻辑严谨性"):
                with st.expander("2. 财务逻辑严谨性", expanded=True):
                    st.write(result["财务逻辑严谨性"])
            
            if result.get("商业洞察力"):
                with st.expander("3. 商业洞察力", expanded=True):
                    st.write(result["商业洞察力"])
            
            if result.get("表达与结构化"):
                with st.expander("4. 表达与结构化", expanded=True):
                    st.write(result["表达与结构化"])
        
        # 显示综合评价
        if result.get("综合评价"):
            st.markdown("### 二、综合评价")
            st.write(result.get("综合评价"))
        
        # 保存结果到会话状态（不再保存修改后的答案）
        st.session_state.modified_answer = ""


def save_evaluation_to_md(criteria: str, question: str, original_answer: str, result: Dict[str, str], raw_response: str = ""):
    """将评测结果保存到Markdown文件"""
    # 使用新的格式
    md_content = f"""# AI问答质量评测报告

## 评测信息

**问题：**  
{question}

**原始答案：**  
{original_answer}

**评测标准：**  
{criteria}

## 评测结果

### 一、分项评分
{result.get("分项评分", "未提供")}

### 二、综合评价
{result.get("综合评价", "未提供")}

## 原始AI返回结果
```
{raw_response}
```

---
*评测时间：{st.session_state.get('evaluation_time', 'N/A')}*
"""
    
    # 生成文件名
    import time
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    filename = f"evaluation_report_{timestamp}.md"
    
    with open(filename, "w", encoding="utf-8") as f:
        f.write(md_content)
    
    st.success(f"评测报告已保存至: {filename}")
    
    # 提供下载链接
    with open(filename, "r", encoding="utf-8") as f:
        st.download_button(
            label="下载评测报告",
            data=f.read(),
            file_name=filename,
            mime="text/markdown"
        )


def main():
    """主函数"""
    set_page_config()
    initialize_session_state()
    create_sidebar()
    
    # 获取输入
    criteria, question, answer = create_input_section()
    
    # 评测按钮
    if st.button("开始评测", type="primary", use_container_width=True):
        if not criteria or not question or not answer:
            st.warning("请填写所有输入字段")
        elif st.session_state.model_provider == "openai" and not st.session_state.api_key:
            st.error("请在侧边栏输入OpenAI API Key")
        elif st.session_state.model_provider == "custom" and (not st.session_state.custom_base_url or not st.session_state.custom_api_key):
            st.error("请在侧边栏输入API Base URL和API Key")
        else:
            with st.spinner("AI正在评测中，请稍候..."):
                # 生成提示
                prompt = generate_evaluation_prompt(criteria, question, answer)
                
                # 调用AI进行评测
                result, raw_response = call_ai_evaluation(prompt)
                
                if result:
                    # 保存评测时间
                    import time
                    st.session_state.evaluation_time = time.strftime("%Y-%m-%d %H:%M:%S")
                    
                    # 显示结果
                    display_evaluation_result(result)
                    
                    # 保存到MD文件
                    save_evaluation_to_md(criteria, question, answer, result, raw_response)
                else:
                    st.error("评测失败，请检查API配置或稍后重试")


if __name__ == "__main__":
    main()