from pathlib import Path
from xml.etree import ElementTree as E
import json,hashlib
from PIL import Image,ImageOps,ImageDraw
p=Path(__file__).parent; asset=p/'roofFill/roofFill.i3d'
r=E.parse(asset).getroot()
for node in r.find('Files'):
    name=node.get('filename')
    target=Path('G:/SteamLibrary/steamapps/common/Farming Simulator 25/data')/name[6:] if name.startswith('$data/') else asset.parent/name
    assert target.exists(),target
assert (asset.parent/r.find('Shapes').get('externalShapesFile')).stat().st_size>1000
assert not r.findall('.//Camera') and not r.findall('.//Light')
stats=json.loads((asset.parent/'geometry_report.json').read_text()); assert stats['uv_layers']==2
center=json.loads((asset.parent/'centering_report.json').read_text()); assert center['offset_m']==0
log=(p/'finalize.log').read_bytes().decode('utf-16',errors='replace')
assert 'Error: UVs out' not in log
(p/'validation.json').write_text(json.dumps({'status':'PASS','checks':['resource paths','binary shapes','no preview objects exported','two UV sets','zero centering offset','converter load/save'],'geometry':stats,'game':'UNTESTED'},indent=2))
old=p.parents[2]/'Library/_FS25_SiloMachinery/fine_details_v3/roofFill/roofFill_preview.png'
board=Image.new('RGB',(1800,760),'#222832'); d=ImageDraw.Draw(board)
for i,(name,f) in enumerate([('BEFORE',old),('BUILT CONE: RIVETS + HATCH',asset.parent/'roofFill_preview.png')]):
    im=ImageOps.contain(Image.open(f).convert('RGB'),(900,710)); board.paste(im,(900*i+(900-im.width)//2,45)); d.text((900*i+25,16),name,fill='white',font_size=22)
board.save(p/'Cone_Built_Before_After.png')
print('PASS',stats)
