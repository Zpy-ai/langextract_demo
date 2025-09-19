![webpage]([C:\Users\zpy\Desktop\GitHub_provider\langextract_demo\images\webpage.png](https://github.com/Zpy-ai/langextract_demo/blob/main/images/webpage.png))



# 一、信息提取规则

程序会提取以下五类信息：

1. **标题** - 文档或报告的标题
2. **链接** - 相关的URL链接
3. **描述** - 文本的主要描述内容
4. **标签** - 关键词或标签信息
5. **时间** - 发布或创建时间
# 二、环境准备
```bash
# 拉取代码
git clone https://github.com/google/langextract.git

cd langextract

# 创建虚拟环境
conda create -n langextract python=3.12

# 激活虚拟环境
conda activate langextract
# 用于基础安装:
pip install -e .

# 我使用的openai标准的阿里模型，需要下载依赖
pip install langextract[openai]
```

# 三、文件说明

- `test.py` - 主程序文件，包含读取CSV、提取信息、保存JSON、生成HTML等功能
- `test.csv` - 输入的CSV文件，包含待处理的文本数据
- `result.json` - 输出的JSON文件，包含所有提取结果（打标签）
- `result.html` - 输出的HTML文件，用于可视化展示提取结果

# 四、运行程序

```bash
python aliyun.py
```

# 五、代码配置说明

## 1. 设计提示词

```python
prompt = "提取报告摘要相关信息，包括报告的标题,链接,描述,标签,时间，按照文本中出现的顺序进行提取。"
```

根据需要修改这个提示词来提取不同类型的信息。

## 2. 构建标准示例数据供大模型学习

```python
examples = [
    lx.data.ExampleData(
        text="示例文本内容",
        extractions=[
            lx.data.Extraction(extraction_class="标题", extraction_text="提取的标题"),
            // ... 其他提取示例
        ]
    )
]
```

通过提供高质量的示例，可以指导AI模型更准确地提取信息。

## 3. 配置openai标准接口模型参数

```python
config = factory.ModelConfig(
    model_id="qwen3-max-preview",
    provider="OpenAILanguageModel",
    provider_kwargs={
        "api_key": "你的密钥",
        "base_url": "openai标准接口地址",
        "fence_output": True,
        "use_schema_constraints": False
    }
)

model = factory.create_model(config)
```

# 六、处理流程

1. **读取CSV文件** - 逐行读取CSV文件内容
2. **文本预处理** - 将每行数据合并为完整文本字符串
3. **AI信息提取** - 使用配置的语言模型提取结构化信息
4. **结果保存** - 将提取结果保存为JSON文件（result.json）
5. **可视化生成** - 创建HTML可视化报告（result.html）

# 七、输出文件

## result.json
包含所有提取结果的JSON文件，格式如下：

```json
[
  {
    "original_text": "原始文本内容...",
    "extractions": [
      {
        "class": "标题",
        "text": "提取的标题内容",
        "position": {"start": 0, "end": 15}
      },
      // ... 其他提取结果
    ]
  }
]
```

## result.html
美观的HTML可视化报告，包含：
- 处理统计信息（总行数、总实体数、实体类型数等）
- 每行文本的详细提取结果
- 响应式设计，支持移动端查看



