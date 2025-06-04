import re
import os
import requests
import yaml

def extract_urls(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 使用正则表达式匹配括号中的URL
    pattern = r'\((https://[^)]+)\)'
    urls = re.findall(pattern, content)
    return urls

def fetch_api_content(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.text
    except requests.RequestException as e:
        print(f"获取 {url} 失败: {str(e)}")
        return None

def extract_yaml_content(content):
    """提取完整的YAML内容并解析"""
    if not content:
        return None
    
    try:
        # 使用正则表达式匹配完整的YAML内容
        pattern = r'openapi: 3\.0\.1.*?security: \[\]'
        match = re.search(pattern, content, re.DOTALL)
        if match:
            yaml_content = match.group(0)
            return yaml.safe_load(yaml_content)
    except Exception as e:
        print(f"解析YAML失败: {str(e)}")
    return None

def merge_apis(apis):
    """合并多个API文档"""
    merged_api = {
        'openapi': '3.0.1',
        'info': {
            'title': 'Merged API Documentation',
            'description': 'Combined API documentation',
            'version': '1.0.0'
        },
        'paths': {},
        'security': []
    }
    
    # 用于检测重复路径
    path_mapping = {}
    total_paths = 0
    
    for i, api in enumerate(apis, 1):
        if not api or 'paths' not in api:
            print(f"跳过第 {i} 个API，因为它是空的或没有paths字段")
            continue
            
        current_paths = 0
        for path, path_content in api['paths'].items():
            # 获取原始路径的最后部分
            base_path = path.split('BASE_URL')[-1]
            
            # 如果路径已存在，添加编号以区分
            if base_path in path_mapping:
                path_mapping[base_path] += 1
                new_path = f"{base_path}_variant_{path_mapping[base_path]}"
            else:
                path_mapping[base_path] = 0
                new_path = base_path
                
            merged_api['paths'][new_path] = path_content
            current_paths += 1
            print(f"添加路径: {new_path} (原始路径: {path})")
        
        total_paths += current_paths
        print(f"处理第 {i} 个API文档，添加了 {current_paths} 个接口")
    
    print(f"最终合并了总计 {total_paths} 个接口")
    print("路径映射情况:")
    for path, count in path_mapping.items():
        if count > 0:
            print(f"路径 {path} 有 {count + 1} 个变体")
            
    return merged_api

def main():
    # 创建输出目录
    if not os.path.exists('api_files'):
        os.makedirs('api_files')
    
    # 读取并处理 api_docs.txt
    urls = extract_urls('api_docs.txt')
    
    apis = []
    
    # 为每个URL获取内容并处理
    for i, url in enumerate(urls, 1):
        print(f"正在处理 URL {i}: {url}")
        
        # 获取API内容
        content = fetch_api_content(url)
        if content:
            api_content = extract_yaml_content(content)
            if api_content:
                apis.append(api_content)
    
    merged_api = merge_apis(apis)
    
    # 保存合并后的文件
    with open('api_files/merged_api.yaml', 'w', encoding='utf-8') as f:
        yaml.dump(merged_api, f, allow_unicode=True, sort_keys=False)
    print("已生成合并的API文档: api_files/merged_api.yaml")

if __name__ == "__main__":
    main()