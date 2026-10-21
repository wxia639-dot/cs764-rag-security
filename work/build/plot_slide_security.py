from pathlib import Path
import json,argparse
ROOT=Path(__file__).resolve().parents[2]
parser=argparse.ArgumentParser(description="Plot recorded results without model inference.")
parser.add_argument("--output-dir",type=Path,default=ROOT/"work/ieee_report/figures")
args=parser.parse_args()
args.output_dir.mkdir(parents=True,exist_ok=True)
EXP=json.loads((ROOT/"work/expanded/results.json").read_text())
SUP=json.loads((ROOT/"work/revision_detection/results.json").read_text())
MM=EXP["metrics"];DD=SUP["methods"]
LM=json.loads((ROOT/"work/rag/results.json").read_text())["metrics"]
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
names=list(MM);x=np.arange(4)
fig,axs=plt.subplots(1,2,figsize=(10,3.55),layout='constrained')
for ax,key,label in zip(axs,['asr','attacked_accuracy'],['Marker attack success (%)','Accuracy under attack (%)']):
    v=[100*MM[n][key] for n in names]
    ax.bar(x,v,color=['#777777','#A86A17','#4477AA','#087F8C'])
    ax.set_xticks(x,['Unfiltered','Rules','Probe','Combined'],fontsize=11)
    ax.set_ylim(0,100);ax.set_ylabel(label,fontsize=12);ax.tick_params(axis='y',labelsize=11)
    ax.spines[['top','right']].set_visible(False);ax.grid(axis='y',alpha=.2);ax.set_axisbelow(True)
    for j,a in enumerate(v):ax.text(j,a+2,f'{a:.1f}',ha='center',fontsize=12)
fig.savefig(args.output_dir/'slide_security.png',dpi=180,bbox_inches='tight')
