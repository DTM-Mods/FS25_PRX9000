import bpy,bmesh,sys,math,json,addon_utils
from mathutils import Vector
from pathlib import Path
from xml.etree import ElementTree as ET
P=Path(__file__).parent; PART=sys.argv[sys.argv.index('--')+1]; OUT=P/PART
bpy.ops.wm.open_mainfile(filepath=str(OUT/(PART+'.blend')))
names=['galv','blue','yellow','dark','bolt','rubber']; mats=[bpy.data.materials['mach_'+n] for n in names]
obj=bpy.data.objects[PART+'_vis']; root=bpy.data.objects[PART]
for ob in bpy.data.objects:
    if ob.type!='MESH' or ob.name=='PREVIEW_ground': continue
    me=ob.data
    bm=bmesh.new(); bm.from_mesh(me); bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces)); bm.to_mesh(me); bm.free(); me.update()
    if not me.uv_layers: me.uv_layers.new(name='UVMap')
    uv=me.uv_layers[0]
    for f in me.polygons:
        ax=max(range(3),key=lambda k:abs(f.normal[k])); ab=[k for k in range(3) if k!=ax]
        coords=[me.vertices[me.loops[li].vertex_index].co for li in f.loop_indices]
        shifts=[math.floor(sum(c[a] for c in coords)/len(coords)) for a in ab]
        for li in f.loop_indices:
            c=me.vertices[me.loops[li].vertex_index].co; uv.data[li].uv=(c[ab[0]]-shifts[0],c[ab[1]]-shifts[1])
    if len(me.uv_layers)<2: me.uv_layers.new(name='UVMap2')
    for a,b in zip(me.uv_layers[0].data,me.uv_layers[1].data): b.uv=a.uv
    assert all(abs(q)<31 for p in uv.data for q in p.uv),'UV exceeds GIANTS exporter range'
sc=bpy.context.scene; cam=sc.camera; sc.cycles.samples=32
mid=sum((Vector(c) for c in obj.bound_box),Vector())/8
if PART=='roofFill': co=bpy.data.objects['PREVIEW_conveyor_context']
source=(P/'build_realistic.py').read_text(); exec(source[source.index('def view('):],globals())
print('FINALIZED_UV_RANGE_SAFE',PART)
