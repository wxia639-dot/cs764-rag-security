"""Stream the official public safetensors checkpoint into this workspace."""
from pathlib import Path
import urllib.request, time
p=Path('work/models/qwen-0.5b/model.safetensors');tmp=p.with_suffix('.download')
u='https://huggingface.co/Qwen/Qwen2.5-0.5B-Instruct/resolve/main/model.safetensors'
begin=time.monotonic();n=0
with urllib.request.urlopen(u,timeout=60) as src,tmp.open('wb') as dst:
    while True:
        b=src.read(8*1024*1024)
        if not b:break
        dst.write(b);n+=len(b)
        if n%(64*1024*1024)==0:print(f'{n/1024**2:.0f} MiB downloaded',flush=True)
if n!=988097824:raise RuntimeError(f'Unexpected checkpoint size: {n}')
tmp.replace(p);print(f'Completed {n} bytes in {time.monotonic()-begin:.1f}s',flush=True)
