import requests
import json
import os
import sys

# ====== 这里填你的API Key ======
API_KEY = "sk-你的API"  
API_URL = "https://api.deepseek.com/v1/chat/completions"  

def read_pdf(file_path):
    """读取PDF文件内容"""
    try:
        import PyPDF2
        with open(file_path, 'rb') as f:
            reader = PyPDF2.PdfReader(f)
            text = ""
            for page in reader.pages:
                text += page.extract_text()
            return text
    except ImportError:
        print("💡 正在尝试为您自动安装 PDF 解析依赖...")
        os.system(f"{sys.executable} -m pip install pypdf2 -q")
        try:
            import PyPDF2
            with open(file_path, 'rb') as f:
                reader = PyPDF2.PdfReader(f)
                text = ""
                for page in reader.pages:
                    text += page.extract_text()
                return text
        except:
            return None

def optimize_resume(resume_text, jd_text):
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    
    prompt = f"""你是一名资深的HR和简历优化专家。
请你根据下面的「目标岗位JD」和「原始简历」，进行分析并输出以下三部分内容：
 
1. **匹配度分析**：逐条对比JD中的要求与简历中的匹配情况，标记出「匹配」「部分匹配」「不匹配」。
2. **优化建议**：针对不匹配或描述不清晰的部分，提出具体修改建议。
3. **优化后的简历**：基于原始简历，按照目标岗位JD进行重写，输出一份完整优化的简历（保持真实，不造假）。
 
目标岗位JD：
{jd_text}
 
原始简历：
{resume_text}
"""
    
    data = {
        "model": "deepseek-chat",
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.7
    }
    
    print("⏳ 正在请求 DeepSeek AI，请稍候...")
    
    try:
        response = requests.post(API_URL, headers=headers, json=data, timeout=60)
        
        if response.status_code == 200:
            result = response.json()
            # ✅ 修复：choices 必须用 [0] 索引取值
            if "choices" in result and len(result["choices"]) > 0:
                return result["choices"][0]["message"]["content"]
            else:
                return "⚠️ AI返回格式异常，未找到choices字段"
        else:
            return f"❌ 请求失败: {response.status_code}\n{response.text}"
    
    except requests.exceptions.Timeout:
        return "❌ 请求超时，大模型生成内容较长，请稍后重试"
    except requests.exceptions.ConnectionError:
        return "❌ 网络连接失败，请检查网络"
    except Exception as e:
        return f"❌ 未知错误: {str(e)}"

def get_multi_line_input(prompt_text):
    print(prompt_text)
    print("(请输入或粘贴内容，完成后在全新的一行输入 'EOF' 或直接连续按两次回车结束)：")
    lines = []
    while True:
        try:
            line = input()
            if line.strip() == "EOF":
                break
            if line == "" and len(lines) > 0 and lines[-1] == "":
                break
            lines.append(line)
        except EOFError:
            break
    return "\n".join(lines).strip()

def main():
    print("=" * 50)
    print("🎯 AI简历优化助手（DeepSeek 版）")
    print("=" * 50)
    
    print("\n📄 选择简历输入方式：")
    print("1. 从PDF文件读取")
    print("2. 手动粘贴文本")
    choice = input("请输入选择（1或2）：").strip()
    
    resume = ""
    
    if choice == "1":
        pdf_path = input("\n请将PDF文件拖拽到终端，或输入完整路径：").strip()
        pdf_path = pdf_path.strip("'\"")
        
        if not os.path.exists(pdf_path):
            print(f"❌ 文件不存在：{pdf_path}")
            return
        
        resume = read_pdf(pdf_path)
        if resume:
            print(f"✅ 成功读取PDF，共 {len(resume)} 个字符")
        else:
            print("❌ 无法读取PDF文件，请确保PDF不是扫描件/图片，或尝试使用手动粘贴。")
            return
    
    elif choice == "2":
        resume = get_multi_line_input("\n📄 请粘贴你的简历内容（纯文本）：")
    else:
        print("❌ 无效选择")
        return
    
    if not resume:
        print("❌ 简历内容为空！")
        return
    
    jd = get_multi_line_input("\n💼 请粘贴目标岗位JD：")
    
    if not jd:
        print("❌ JD内容为空！")
        return
    
    output = optimize_resume(resume, jd)
    
    print("\n" + "=" * 50)
    print("📊 AI优化结果：")
    print("=" * 50)
    print(output)
    
    try:
        desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
        filename = os.path.join(desktop_path, "optimized_resume.txt")
        with open(filename, "w", encoding="utf-8") as f:
            f.write(output)
        print(f"\n✅ 结果已成功保存到桌面：{filename}")
    except Exception as e:
        print(f"\n⚠️ 结果保存到桌面失败，但已输出如上。错误: {e}")

if __name__ == "__main__":
    main()
