"""Export per-model responses for GitHub."""
import json
import os

d = json.load(open('.deepeval/.latest_test_run.json'))
cases = d.get('testRunData', {}).get('testCases', [])

# Group by model
by_model = {}
for c in cases:
    name = c.get('name', '')
    parts = name.split('] ', 1)
    category = parts[0].replace('[', '')
    model_prompt = parts[1] if len(parts) > 1 else name
    model = model_prompt.split(' | ')[0]
    prompt = model_prompt.split(' | ', 1)[1] if ' | ' in model_prompt else ''
    
    if model not in by_model:
        by_model[model] = []
    
    by_model[model].append({
        'category': category,
        'prompt': prompt,
        'output': c.get('actualOutput', ''),
        'success': c.get('success', False),
        'metrics': [
            {
                'name': m.get('name', '').replace(' [GEval]', ''),
                'score': m.get('score', 0),
                'success': m.get('success', False),
                'reason': m.get('reason', '')[:200],
            }
            for m in c.get('metricsData', [])
        ],
    })

# Write per-model files
output_dir = 'model_responses'
os.makedirs(output_dir, exist_ok=True)

for model, responses in by_model.items():
    safe_name = model.replace('/', '-').replace('_', '-').replace(' ', '-')
    path = os.path.join(output_dir, f'{safe_name}.json')
    with open(path, 'w') as f:
        json.dump(responses, f, indent=2)
    print(f'{path}: {len(responses)} responses')

print(f'\nTotal: {sum(len(r) for r in by_model.values())} responses across {len(by_model)} models')
