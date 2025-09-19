import langextract as lx  
import textwrap 
import os
import csv
import json
from langextract import factory

# 定义提示和提取规则  
prompt = "提取报告摘要相关信息，包括报告的标题,链接,描述,标签,时间，按照文本中出现的顺序进行提取。"
   
# 提供高质量示例来指导模型  
examples =[
    lx.data.ExampleData(
        text="2025年中国电竞行业研究报告,https://report.iresearch.cn/report/202506/4728.shtml,作为数字经济时代的典型赛道，电竞, 电子竞技,2025/6/27 12:19:29",
        extractions=[
            lx.data.Extraction(extraction_class="标题", extraction_text="2025年中国电竞行业研究报告"),
            lx.data.Extraction(extraction_class="链接", extraction_text="https://report.iresearch.cn/report/202506/4728.shtml"),
            lx.data.Extraction(extraction_class="描述", extraction_text="作为数字经济时代的典型赛道"),
            lx.data.Extraction(extraction_class="标签", extraction_text="电竞, 电子竞技"),
            lx.data.Extraction(extraction_class="时间", extraction_text="2025/6/27 12:19:29")
        ]
    )
]

# 配置模型
config = factory.ModelConfig(
    model_id="qwen3-max-preview",
    provider="OpenAILanguageModel",
    provider_kwargs={
        "api_key": "密钥",
        "base_url": "符合openai标准的接口地址",
        "fence_output": True,
        "use_schema_constraints": False
    }
)

model = factory.create_model(config)

def process_csv_file(csv_file_path):
    """逐行处理CSV文件"""
    all_results = []
    
    print(f"开始处理CSV文件: {csv_file_path}")
    
    with open(csv_file_path, 'r', encoding='utf-8') as file:
        csv_reader = csv.reader(file)
        
        for row_num, row in enumerate(csv_reader, 1):
            if len(row) == 0:
                continue
                
            # 将整行合并为一个文本字符串
            input_text = ','.join(row)
            
            print(f"\n处理第 {row_num} 行文本:")
            print(f"文本内容: {input_text[:100]}...")  # 显示前100个字符
            
            try:
                # 提取信息
                result = lx.extract(
                    text_or_documents=input_text,
                    prompt_description=prompt,
                    examples=examples,
                    model=model,
                )
                
                # 显示提取结果
                print("提取的实体:")
                for entity in result.extractions:
                    position_info = ""
                    if entity.char_interval:
                        start, end = entity.char_interval.start_pos, entity.char_interval.end_pos
                        position_info = f" (pos: {start}-{end})"
                    print(f"• {entity.extraction_class}: {entity.extraction_text}{position_info}")
                
                all_results.append(result)
                
            except Exception as e:
                print(f"处理第 {row_num} 行时出错: {str(e)}")
                continue
    
    return all_results

def save_json_results(results, output_file="result.json"):
    """保存提取结果为JSON文件"""
    json_data = []
    
    for result in results:
        item_data = {
            "original_text": result.text,
            "extractions": []
        }
        
        for entity in result.extractions:
            extraction_data = {
                "class": entity.extraction_class,
                "text": entity.extraction_text,
                "position": None
            }
            
            if entity.char_interval:
                extraction_data["position"] = {
                    "start": entity.char_interval.start_pos,
                    "end": entity.char_interval.end_pos
                }
            
            item_data["extractions"].append(extraction_data)
        
        json_data.append(item_data)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(json_data, f, ensure_ascii=False, indent=2)
    
    print(f"\nJSON结果已保存到: {output_file}")
    return json_data

def generate_batch_html_visualization(json_data, output_file="result.html"):
    """生成批量处理的HTML可视化文件"""
    html_content = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>批量信息提取结果 - 可视化</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }}
        
        .container {{
            max-width: 1400px;
            margin: 0 auto;
            background: white;
            border-radius: 16px;
            box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
            overflow: hidden;
        }}
        
        .header {{
            background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
            color: white;
            padding: 24px 32px;
            text-align: center;
        }}
        
        .header h1 {{
            font-size: 28px;
            font-weight: 600;
            margin-bottom: 8px;
        }}
        
        .header p {{
            opacity: 0.9;
            font-size: 16px;
        }}
        
        .content {{
            padding: 32px;
        }}
        
        .result-item {{
            background: #f8f9fa;
            border-radius: 12px;
            padding: 24px;
            margin-bottom: 24px;
            border: 1px solid #e9ecef;
        }}
        
        .result-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 16px;
            padding-bottom: 12px;
            border-bottom: 2px solid #dee2e6;
        }}
        
        .result-title {{
            font-size: 18px;
            font-weight: 600;
            color: #495057;
        }}
        
        .result-index {{
            background: #007bff;
            color: white;
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 14px;
            font-weight: 500;
        }}
        
        .original-text {{
            background: white;
            border: 2px solid #e9ecef;
            border-radius: 8px;
            padding: 16px;
            margin-bottom: 16px;
            font-family: 'JetBrains Mono', 'Fira Code', monospace;
            font-size: 14px;
            line-height: 1.6;
            max-height: 100px;
            overflow-y: auto;
            white-space: pre-wrap;
        }}
        
        .extractions-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 16px;
        }}
        
        .extraction-card {{
            background: white;
            border-radius: 8px;
            padding: 16px;
            border-left: 4px solid #007bff;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        }}
        
        .extraction-class {{
            font-size: 12px;
            font-weight: 600;
            color: #6c757d;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            margin-bottom: 8px;
        }}
        
        .extraction-text {{
            font-size: 14px;
            color: #495057;
            line-height: 1.5;
            word-break: break-word;
        }}
        
        .extraction-position {{
            font-size: 12px;
            color: #adb5bd;
            margin-top: 8px;
        }}
        
        .stats-summary {{
            background: white;
            border-radius: 12px;
            padding: 24px;
            margin-bottom: 24px;
            text-align: center;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
        }}
        
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 20px;
            margin-top: 16px;
        }}
        
        .stat-item {{
            text-align: center;
        }}
        
        .stat-number {{
            font-size: 24px;
            font-weight: 600;
            color: #007bff;
            margin-bottom: 4px;
        }}
        
        .stat-label {{
            font-size: 14px;
            color: #6c757d;
        }}
        
        @media (max-width: 768px) {{
            .content {{
                padding: 20px;
            }}
            
            .extractions-grid {{
                grid-template-columns: 1fr;
            }}
            
            .stats-grid {{
                grid-template-columns: repeat(2, 1fr);
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📊 批量信息提取结果</h1>
            <p>CSV文件逐行处理的可视化展示</p>
        </div>
        
        <div class="content">
            <div class="stats-summary">
                <h2>处理统计</h2>
                <div class="stats-grid">
                    <div class="stat-item">
                        <div class="stat-number">{len(json_data)}</div>
                        <div class="stat-label">总处理行数</div>
                    </div>
                    <div class="stat-item">
                        <div class="stat-number">{sum(len(item['extractions']) for item in json_data)}</div>
                        <div class="stat-label">总提取实体数</div>
                    </div>
                    <div class="stat-item">
                        <div class="stat-number">{len(set(entity['class'] for item in json_data for entity in item['extractions']))}</div>
                        <div class="stat-label">实体类型数</div>
                    </div>
                    <div class="stat-item">
                        <div class="stat-number">{round(sum(len(item['extractions']) for item in json_data) / len(json_data), 1)}</div>
                        <div class="stat-label">平均每行实体数</div>
                    </div>
                </div>
            </div>
"""
    
    # 为每个结果项生成HTML
    for idx, item in enumerate(json_data):
        html_content += f"""
            <div class="result-item">
                <div class="result-header">
                    <div class="result-title">第 {idx + 1} 行处理结果</div>
                    <div class="result-index">#{idx + 1}</div>
                </div>
                
                <div class="original-text">{item['original_text']}</div>
                
                <div class="extractions-grid">
        """
        
        for entity in item['extractions']:
            position_info = f"位置: [{entity['position']['start']}-{entity['position']['end']}]" if entity['position'] else ""
            
            html_content += f"""
                    <div class="extraction-card">
                        <div class="extraction-class">{entity['class']}</div>
                        <div class="extraction-text">{entity['text']}</div>
                        <div class="extraction-position">{position_info}</div>
                    </div>
            """
        
        html_content += """
                </div>
            </div>
        """
    
    html_content += """
        </div>
    </div>
</body>
</html>
    """
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"批量可视化HTML已保存到: {output_file}")

# 主处理流程
if __name__ == "__main__":
    csv_file_path = "test.csv"  # CSV文件路径
    
    # 处理CSV文件
    results = process_csv_file(csv_file_path)
    
    if results:
        # 保存JSON结果
        json_data = save_json_results(results, "result.json")
        
        # 生成批量可视化HTML
        generate_batch_html_visualization(json_data, "result.html")
        
        print(f"\n✅ 处理完成！共处理了 {len(results)} 行数据")
        print("📁 生成的文件:")
        print("   - result.json (提取结果)")
        print("   - result.html (可视化展示)")
    else:
        print("❌ 没有成功处理任何数据")