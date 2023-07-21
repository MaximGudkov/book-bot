import json

with open(r'scripts/storage/Bredberi_Marsianskie_hroniki.json', encoding='utf-8') as f:
    content = json.load(f)
    content_str = json.dumps(content)

query = 'INSERT INTO books (name, content) VALUES (%s, %s)'
values = ('📖 Ray Bradbury `The Martian Chronicles`', content_str)
