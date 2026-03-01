import os
import re

html_dir = r'd:\zvit4\diplom\frontend\html'

for filename in os.listdir(html_dir):
    if not filename.endswith('.html'): continue
    filepath = os.path.join(html_dir, filename)
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # replace CSS paths
    content = re.sub(r'href="([a-zA-Z0-9_\-]+\.css)"', r'href="/static/css/\1"', content)
    # replace JS paths
    content = re.sub(r'src="([a-zA-Z0-9_\-]+\.js)"', r'src="/static/js/\1"', content)
    # replace internal HTML links - careful with .css/.js
    content = re.sub(r'href="([a-zA-Z0-9_\-]+\.html)([^"]*)"', r'href="/\1\2"', content)
    
    # Inject config.js before the first local script
    if '<script' in content and '/static/js/config.js' not in content:
        content = re.sub(r'(<script src="/static/js/(app|api-client|auth-nav)\.js"></script>)',
                         r'<script src="/static/js/config.js"></script>\n    \1',
                         content, count=1)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)

print('Replacement complete.')
