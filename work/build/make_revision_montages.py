from pathlib import Path
from PIL import Image,ImageOps,ImageDraw
R=Path(__file__).resolve().parents[2];B=R/'work/build'
for folder,pattern,cols,width in [('revised_pdf_pages','page-*.png',3,430),('revised_word_pages','page-*.png',3,430),('revised_slides','slide-*.png',3,500)]:
    paths=sorted((B/folder).glob(pattern));thumbs=[]
    for p in paths:
        im=Image.open(p).convert('RGB');im.thumbnail((width,720));canvas=Image.new('RGB',(width+20,im.height+35),'#E2E7EC');canvas.paste(im,((width+20-im.width)//2,25));ImageDraw.Draw(canvas).text((8,5),p.stem,fill='black');thumbs.append(canvas)
    hh=max(im.height for im in thumbs);sheet=Image.new('RGB',((width+20)*cols,hh*((len(thumbs)+cols-1)//cols)),'#E2E7EC')
    for i,im in enumerate(thumbs):sheet.paste(im,((i%cols)*(width+20),(i//cols)*hh))
    sheet.save(B/(folder+'_montage.png'))
