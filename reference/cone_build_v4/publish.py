from pathlib import Path
import shutil,hashlib,json
p=Path(__file__).parent
lib=p.parents[2]/'Library'/'_FS25_SiloMachinery'
dest=lib/'cone_details_v4'
assert (p/'roofFill/roofFill.i3d.shapes').stat().st_size>1000
assert not dest.exists(), 'Preserve existing versions'
shutil.copytree(p,dest,ignore=shutil.ignore_patterns('*.blend1','publish.py'))
shutil.copy2(p.parent/'cone_rivets_hatch_mockup_v1.png',dest/'Approved_Cone_Mockup.png')
for src in p.rglob('*'):
    if src.is_file() and src.name!='publish.py' and src.suffix!='.blend1':
        assert hashlib.sha256(src.read_bytes()).digest()==hashlib.sha256((dest/src.relative_to(p)).read_bytes()).digest()
current=lib/'CURRENT_MODELS.md'
current.write_text(current.read_text(encoding='utf-8')+'\n\n2026-10-29 (Codex): Approved cone rivets and visible hinged access hatch BUILT. Current roofFill is now cone_details_v4/roofFill/roofFill.blend and roofFill.i3d; use cone_details_v4/textures alongside it. Other three parts remain fine_details_v3. Earlier versions preserved. Actual previews: cone_details_v4/roofFill/roofFill_preview.png and roofFill_cone_detail.png. Separate reusable part, not fitted into silo.\n',encoding='utf-8')
knowledge=lib.parent/'_FS25Knowledge/FS25_Universal_Knowledge.md'
with knowledge.open('a',encoding='utf-8') as f:
    f.write('\n- 2026-10-29 (Codex): User approved cone_rivets_hatch_mockup_v1 and said BUILD IT. RoofFill current reusable model is Library/_FS25_SiloMachinery/cone_details_v4/roofFill, other three parts remain fine_details_v3. Built real round rivets on 12 raised radial seams and neck/base rows; cone-following trapezoid hatch with gasket, two hinges, latch and grab handle facing preview camera (+X,+Y). Prior v3 hatch faced opposite camera; do not repeat invisible far-side placement. VERIFIED actual Blender renders, centered geometry, binary I3D converter and resource checks, SHA256 library copy readback. New version UNTESTED in GIANTS Editor/game. Existing silo assembly unchanged; no ZIP/install/upload.\n')
print('SAVED_AND_HASH_VERIFIED',dest)
