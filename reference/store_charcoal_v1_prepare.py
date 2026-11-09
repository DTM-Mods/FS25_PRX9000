from PIL import Image, ImageDraw
from pathlib import Path
import shutil, io, struct
root=Path('reference/store_charcoal_v1'); root.mkdir(exist_ok=True)
base=Path(r'C:/Users/groov/.codex/generated_images/01a18b0b-fc4a-7ea3-bb6c-51b19fad7df7')
files={'9000':'exec-06e38583-e2a3-4166-a17f-1177a11c30e0.png','8000':'exec-353c9c8f-7e92-4000-95e3-8e5cc0fadcb3.png','6000':'exec-24e6c7f7-96a1-46f5-96d2-9bff1ac311fe.png'}
canvas=Image.new('RGB',(1536,560),(30,32,34)); d=ImageDraw.Draw(canvas)
for i,(n,f) in enumerate(files.items()):
 shutil.copy2(base/f,root/f'prx{n}_charcoal.png')
 shutil.copy2(f'store_prx{n}.dds',root/f'store_prx{n}_original.dds')
 im=Image.open(base/f).convert('RGBA').resize((512,512),Image.Resampling.LANCZOS)
 im.save(root/f'prx{n}_512.png')
 canvas.paste(im,(i*512,48)); d.text((i*512+220,18),'PRX'+n,fill='white')
canvas.save(root/'all_three_charcoal.png')
