from pathlib import Path
import json
from huggingface_hub import snapshot_download
R=Path(__file__).resolve().parents[1]
snapshot_download('bert-base-uncased',allow_patterns=['*.json','model.safetensors','vocab.txt'])
snapshot_download('Qwen/Qwen2.5-0.5B-Instruct',revision='7ae557604adf67be50417f59c2c2f167def9a775',local_dir=R/'work/models/qwen-0.5b',allow_patterns=['*.json','*.txt','*.safetensors','*.model','LICENSE','README.md'])
p=R/'work/models/protectai';sha='90c9989b1a342275dd0d1a95aad283c04e075671'
snapshot_download('protectai/deberta-v3-base-prompt-injection-v2',revision=sha,local_dir=p,allow_patterns=['*.json','spm.model','model.safetensors','README.md','LICENSE'])
(p/'revision.json').write_text(json.dumps({'repo':'protectai/deberta-v3-base-prompt-injection-v2','revision':sha},indent=2))
