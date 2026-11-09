from PIL import Image
from pathlib import Path
import io,struct
for n in ['9000','8000','6000']:
 im=Image.open(f'reference/store_charcoal_v1/prx{n}_512.png').convert('RGBA')
 levels=[]
 for size in [512,256,128,64,32,16,8,4,2,1]:
  buf=io.BytesIO(); im.resize((size,size),Image.Resampling.LANCZOS).save(buf,format='DDS',pixel_format='DXT5'); levels.append(buf.getvalue())
 header=bytearray(levels[0][:128]); flags=struct.unpack_from('<I',header,8)[0]; struct.pack_into('<I',header,8,flags|0x20000); struct.pack_into('<I',header,28,10); struct.pack_into('<I',header,108,0x401008)
 out=Path(f'store_prx{n}.dds'); out.write_bytes(header+b''.join(x[128:] for x in levels))
 check=Image.open(out); assert check.size==(512,512); assert out.stat().st_size==349680
 print(out,check.size,'DXT5, 10 mip levels,',out.stat().st_size,'bytes')
