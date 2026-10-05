import re

with open('.env', 'r', encoding='utf-8') as f:
    content = f.read()

# Find LLM related settings
for line in content.splitlines():
    if any(k in line for k in ['LLM', 'GOOGLE_API', 'MODEL', 'TOKEN', 'AGENT']):
        print(repr(line[:60]))
