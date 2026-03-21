import yaml

# 读取 urls.txt（一行一条）
with open('urls.txt', 'r', encoding='utf-8') as f:
    urls = [line.strip() for line in f if line.strip()]

# 读取现有 config.yml（保留 cookies、database 等设置）
with open('config.yml', 'r', encoding='utf-8') as f:
    config = yaml.safe_load(f) or {}

# 把 link 设成列表 + 强制多行块格式
config['link'] = urls

config.setdefault('database', True)
config.setdefault('thread', 8)
config.setdefault('retry_times', 5)

# 关键：default_flow_style=False 让列表每条换行
with open('config.yml', 'w', encoding='utf-8') as f:
    yaml.dump(config, f, 
              allow_unicode=True, 
              sort_keys=False, 
              default_flow_style=False,   
              width=1000)                 
