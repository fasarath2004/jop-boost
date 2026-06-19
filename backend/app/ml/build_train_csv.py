from pathlib import Path
from pypdf import PdfReader
import csv
import random

source_base = Path(r'c:\Users\ASUS\Downloads\archive\data\data')
output_dir = Path(r'c:\Users\ASUS\Desktop\jop-boost\backend\data')
output_dir.mkdir(parents=True, exist_ok=True)
output_path = output_dir / 'train.csv'

categories = sorted([p for p in source_base.iterdir() if p.is_dir()])
category_names = [c.name for c in categories]

examples = []
for category in categories:
    job_desc = f"{category.name.replace('-', ' ')} specialist role requiring demonstrated experience in {category.name.replace('-', ' ').title()} and related functions."
    files = sorted([p for p in category.glob('*.pdf')])
    for p in files:
        try:
            reader = PdfReader(str(p))
            text = ''
            for page in reader.pages[:2]:
                t = page.extract_text()
                if t:
                    text += t + '\n'
            text = text.strip()
            if not text:
                continue
            examples.append((text, job_desc, 90.0, category.name))
        except Exception as e:
            print('skip', p.name, e)

mismatch_examples = []
for text, _, _, orig_cat in random.sample(examples, min(1200, len(examples))):
    other_categories = [c for c in category_names if c != orig_cat]
    if not other_categories:
        continue
    mismatch_cat = random.choice(other_categories)
    mismatch_job_desc = f"{mismatch_cat.replace('-', ' ')} specialist role requiring demonstrated experience in {mismatch_cat.replace('-', ' ').title()} and related functions."
    mismatch_examples.append((text, mismatch_job_desc, 20.0))

with open(output_path, 'w', newline='', encoding='utf-8') as f:
    writer = csv.writer(f)
    writer.writerow(['cv_text', 'job_desc', 'match_score'])
    for text, job_desc, score, _ in examples:
        writer.writerow([text, job_desc, score])
    for text, job_desc, score in mismatch_examples:
        writer.writerow([text, job_desc, score])

print('wrote', output_path, 'examples=', len(examples) + len(mismatch_examples))
