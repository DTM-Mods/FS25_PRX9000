"""Original reusable PRX machinery. Blender Z up; dimensions in metres.
Build: blender -b --factory-startup -P build_realistic.py -- PART
Actual textured geometry is used both for renders and the exported I3D.
"""
import bpy, bmesh, math, sys, os, json, addon_utils
from pathlib import Path
from mathutils import Vector
from xml.etree import ElementTree as ET
P=Path(__file__).parent; PART=sys.argv[sys.argv.index('--')+1]
OUT=P/PART; OUT.mkdir(exist_ok=True)
bpy.ops.wm.read_factory_settings(use_empty=True)
names=['galv','blue','yellow','dark','bolt','rubber']; mats=[]
for name in names:
    m=bpy.data.materials.new('mach_'+name); m.use_nodes=True
    nd=m.node_tree.nodes; lk=m.node_tree.links; bs=nd.get('Principled BSDF')
    def tex(suffix):
        t=nd.new('ShaderNodeTexImage'); t.image=bpy.data.images.load(str(P/'textures'/f'{name}_{suffix}.png')); return t
    d=tex('diffuse'); lk.new(d.outputs['Color'],bs.inputs['Base Color'])
    no=tex('normal'); no.image.colorspace_settings.name='Non-Color'; nn=nd.new('ShaderNodeNormalMap'); lk.new(no.outputs['Color'],nn.inputs['Color']); lk.new(nn.outputs[0],bs.inputs['Normal'])
    sp=tex('specular'); sp.image.colorspace_settings.name='Non-Color'; sep=nd.new('ShaderNodeSeparateColor'); lk.new(sp.outputs[0],sep.inputs[0]); inv=nd.new('ShaderNodeMath'); inv.operation='SUBTRACT'; inv.inputs[0].default_value=1; lk.new(sep.outputs[0],inv.inputs[1]); lk.new(inv.outputs[0],bs.inputs['Roughness']); lk.new(sep.outputs[2],bs.inputs['Metallic'])
    mats.append(m)

V=[]; F=[]; MI=[]; SM=[]
def face(ids,mat='galv',smooth=False): F.append(ids); MI.append(names.index(mat)); SM.append(smooth)
def box(c,s,mat='galv'):
    k=len(V); cx,cy,cz=c; sx,sy,sz=[q/2 for q in s]
    V.extend([(cx+a*sx,cy+b*sy,cz+d*sz) for a,b,d in [(-1,-1,-1),(1,-1,-1),(1,1,-1),(-1,1,-1),(-1,-1,1),(1,-1,1),(1,1,1),(-1,1,1)]])
    for f in [(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)]: face(tuple(k+i for i in f),mat)
def cylinder(a,b,r,mat='galv',n=24,r2=None):
    a,b=Vector(a),Vector(b); z=(b-a).normalized(); u=z.cross(Vector((0,1,0)) if abs(z.y)<.9 else Vector((1,0,0))).normalized(); w=z.cross(u); k=len(V)
    for c,rr in [(a,r),(b,r if r2 is None else r2)]:
        for i in range(n): V.append(tuple(c+rr*(u*math.cos(i*2*math.pi/n)+w*math.sin(i*2*math.pi/n))))
    face(tuple(k+i for i in reversed(range(n))),mat); face(tuple(k+n+i for i in range(n)),mat)
    for i in range(n): j=(i+1)%n; face((k+i,k+j,k+n+j,k+n+i),mat,True)
def ring(c,r,thick,axis='z',mat='galv',n=64):
    k=len(V); c=Vector(c)
    for i in range(n):
        a=i*2*math.pi/n
        for j in range(8):
            b=j*2*math.pi/8; rr=r+thick*math.cos(b); v=(rr*math.cos(a),rr*math.sin(a),thick*math.sin(b)); v=(v[0],v[2],v[1]) if axis=='y' else v
            V.append(tuple(c+Vector(v)))
    for i in range(n):
        for j in range(8): face((k+i*8+j,k+((i+1)%n)*8+j,k+((i+1)%n)*8+(j+1)%8,k+i*8+(j+1)%8),mat,True)
def bolt(c,axis=(0,0,1),radius=.014):
    a=Vector(c); v=Vector(axis); cylinder(a-v*.003,a+v*.003,radius*1.55,'bolt',12); cylinder(a+v*.003,a+v*.014,radius,'bolt',6)
def flange(z,r,pipe=.29):
    tube(z-.012,z+.012,r,pipe-.012)
    for i in range(16):
        a=i*2*math.pi/16; bolt(((r-.035)*math.cos(a),(r-.035)*math.sin(a),z+.014))
def tube(z1,z2,r1,inner,r2=None):
    r2=r1 if r2 is None else r2; k=len(V); n=64
    for z,r in [(z1,r1),(z2,r2),(z1,inner),(z2,inner if r1==r2 else r2-.018)]:
        for i in range(n): a=i*2*math.pi/n; V.append((r*math.cos(a),r*math.sin(a),z))
    for i in range(n):
        j=(i+1)%n
        for f in [(i,j,n+j,n+i),(2*n+j,2*n+i,3*n+i,3*n+j),(n+i,n+j,3*n+j,3*n+i),(j,i,2*n+i,2*n+j)]: face(tuple(k+t for t in f),'galv',True)
def foot(x,y,z=0):
    box((x,y,z+.015),(.25,.25,.03))
    for dx in [-.085,.085]:
        for dy in [-.085,.085]: bolt((x+dx,y+dy,z+.032))
def beam(a,b,r=.035,mat='galv'): cylinder(a,b,r,mat,8)
def motor(c,axis='y',scale=1):
    # Finned TEFC motor, end shields, terminal box and mounting feet.
    x,y,z=c; s=scale
    def pt(t): return (x,y+t*s,z) if axis=='y' else (x+t*s,y,z)
    cylinder(pt(-.28),pt(.28),.20*s,'blue',40)
    for j in range(12): cylinder(pt(-.22+j*.04),pt(-.211+j*.04),.224*s,'blue',40)
    cylinder(pt(.28),pt(.36),.225*s,'blue',40); cylinder(pt(-.32),pt(-.28),.22*s,'blue',40)
    for i in range(12):
        a=i*math.pi/6
        p=(x+.15*s*math.cos(a),y+.362*s,z+.15*s*math.sin(a)) if axis=='y' else (x+.362*s,y+.15*s*math.cos(a),z+.15*s*math.sin(a))
        bolt(p,(0,1,0) if axis=='y' else (1,0,0),.009*s)
    box((x,y,z+.235*s),(.22*s,.22*s,.11*s),'blue')
    for q in [-1,1]: box((x+q*.20*s,y,z-.215*s),(.11*s,.42*s,.05*s),'blue')
    box((x,y,z-.265*s),(.62*s,.7*s,.05*s))
def guard(c,w=.58,h=.78):
    x,y,z=c
    # Open lattice face with a closed perimeter and back: no painted solid rectangle.
    for dx in [-w/2,w/2]: box((x+dx,y,z),(.022,.11,h),'yellow')
    for dz in [-h/2,h/2]: box((x,y,z+dz),(w,.11,.022),'yellow')
    for i in range(1,int(w/.028)):
        box((x-w/2+i*.028,y-.057,z),(.007,.009,h),'yellow')
    for j in range(1,int(h/.028)):
        box((x,y-.058,z-h/2+j*.028),(w,.009,.007),'yellow')
    for dx in [-w/2+.035,w/2-.035]:
        for dz in [-h/2+.035,h/2-.035]: bolt((x+dx,y-.066,z+dz),(0,-1,0),.009)
def hatch(c,s,axis='y'):
    x,y,z=c; box(c,s)
    if axis=='y':
        for dx in [-s[0]*.4,s[0]*.4]:
            for dz in [-s[2]*.4,s[2]*.4]: bolt((x+dx,y-s[1]/2-.002,z+dz),(0,-1,0))
        beam((x-.055,y-.05,z),(x+.055,y-.05,z),.012,'dark')
def grate(x1,x2,y1,y2,z):
    box(((x1+x2)/2,y1,z), (x2-x1,.035,.06)); box(((x1+x2)/2,y2,z),(x2-x1,.035,.06))
    count=int((x2-x1)/.075)
    for i in range(count+1): box((x1+(x2-x1)*i/max(count,1),(y1+y2)/2,z),(.009,y2-y1,.03))
    for j in range(1,6): box(((x1+x2)/2,y1+j*(y2-y1)/6,z-.012),(x2-x1,.008,.02))
def rail(a,b,z):
    x1,y1=a; x2,y2=b; length=math.hypot(x2-x1,y2-y1); count=max(1,math.ceil(length/1.6))
    for i in range(count+1):
        t=i/count; x=x1+(x2-x1)*t; y=y1+(y2-y1)*t; beam((x,y,z),(x,y,z+1.1),.021)
    for h in [.55,1.1]: beam((x1,y1,z+h),(x2,y2,z+h),.021)
    beam((x1,y1,z+.08),(x2,y2,z+.08),.045)

def aerationBlower():
    # Function and mounting origin preserved: silo wall x=0, positive X points outward.
    for yy in [-.59,.59]: box((1.45,yy,.16),(2.1,.12,.16)); foot(.48,yy,.04); foot(2.38,yy,.04)
    box((.36,0,.90),(.72,.77,.66))
    for xx in [.025,.70]:
        box((xx,0,.90),(.025,.85,.74))
        for yy in [-.36,0,.36]:
            for zz in [.57,1.23]: bolt((xx-.015,yy,zz),(-1,0,0))
    # Volute expands around impeller, unlike the old plain cylinder.
    cx,cz=1.48,1.17; k=len(V); n=80
    for yy in [-.30,.30]:
        for i in range(n):
            a=i*2*math.pi/n; rr=.57+.20*i/(n-1); V.append((cx+rr*math.cos(a),yy,cz+rr*math.sin(a)))
    for i in range(n):
        j=(i+1)%n; face((k+i,k+j,k+n+j,k+n+i),'galv',True)
    for off,yy,reverse in [(0,-.30,True),(n,.30,False)]:
        center=len(V); V.append((cx,yy,cz))
        for i in range(n):
            j=(i+1)%n; face((center,k+off+j,k+off+i) if reverse else (center,k+off+i,k+off+j))
    box((.96,0,1.48),(.64,.58,.42))
    for yy in [-.315,.315]:
        ring((cx,yy,cz),.555,.018,'y')
        for i in range(20):
            a=i*math.pi/10; bolt((cx+.54*math.cos(a),yy,cz+.54*math.sin(a)),(0,-1 if yy<0 else 1,0))
    cylinder((cx,-.34,cz),(cx,-.37,cz),.43,'dark',64); ring((cx,-.38,cz),.445,.022,'y')
    # Intake screen geometry, laid over dark recessed aperture.
    for i in range(-13,14):
        d=i*.03; half=math.sqrt(max(0,.41**2-d*d))
        beam((cx+d,-.395,cz-half),(cx+d,-.395,cz+half),.0035)
        beam((cx-half,-.396,cz+d),(cx+half,-.396,cz+d),.0035)
    motor((2.05,.98,.69),'y',1.1); box((2.05,.98,.34),(.78,.85,.30))
    cylinder((cx,.31,cz),(cx,.73,cz),.035,'dark',16)
    cylinder((cx,.55,cz),(cx,.59,cz),.20,'dark',32)
    cylinder((2.05,.55,.69),(2.05,.59,.69),.09,'dark',24)
    beam((cx,.57,cz+.17),(2.05,.57,.77),.018,'rubber'); beam((cx,.57,cz-.17),(2.05,.57,.61),.018,'rubber')
    guard((1.80,.42,.99),.90,1.13)
    for xx in [1.20,1.75]: box((xx,0,.42),(.10,.55,.38))

def roofFill():
    # Origin: middle of FLAT crown; no roof surface exported as part of this collar.
    flange(.035,.91,pipe=.81); tube(.06,.70,.85,.83,r2=.30)
    flange(.71,.36); tube(.72,1.80,.29,.272)
    for z in [1.23,1.78]: flange(z,.35)
    hatch((0,-.59,.36),(.25,.03,.25))
    for i in range(8):
        a=i*math.pi/4; beam((.78*math.cos(a),.78*math.sin(a),.09),(.34*math.cos(a),.34*math.sin(a),.63),.025)
    for x in [-2.0,1.35]:
        for y in [-1.25,.35]: foot(x,y); box((x,y,.87),(.085,.085,1.70))
        box((x,-.45,1.75),(.14,2.0,.12))
        beam((x,-1.25,.20),(x,.35,1.62),.029)
        for y in [-1.25,.35]:
            box((x,y,1.62),(.12,.15,.20)); bolt((x-.065,y,1.63),(-1,0,0))
    # Lengthwise bracing kept clear of central pipe.
    for y in [-1.25,.35]: beam((-2.0,y,.25),(-.65,y,1.7),.024); beam((1.35,y,.25),(.65,y,1.7),.024)

def conveyor():
    L=16.; end=1.5
    box((-7.25,0,.36),(17.5,.70,.72))
    for x in [-16+i*2 for i in range(9)]:
        box((x,0,.37),(.035,.78,.79)); box((x,0,.785),(1.94,.79,.045))
        for y in [-.39,.39]:
            for z in [.08,.36,.67]: bolt((x,y,z),(0,-1 if y<0 else 1,0))
        for y in [-.32,.32]: bolt((x-.04,y,.815))
    for i in range(9):
        x=-15.0+2*i
        for y in [-.34,.34]:
            for dx in [-.72,0,.72]: bolt((x+dx,y,.815),radius=.010)
        beam((x-.10,-.08,.86),(x+.10,-.08,.86),.012)
        for dx in [-.10,.10]: beam((x+dx,-.08,.81),(x+dx,-.08,.86),.012)
    box((1.2,0,.41),(.68,.86,.87)); hatch((1.2,-.449,.41),(.44,.025,.46))
    box((1.2,.60,.44),(.43,.35,.43),'blue'); cylinder((1.2,.40,.44),(1.2,.80,.44),.065,'dark',24)
    motor((1.2,1.14,.48),'y',.9); guard((1.64,.68,.46),.37,.72)
    # Discharge opening is underneath at x=0, aligns with roofFill's pipe.
    cylinder((0,0,-.14),(0,0,0),.29); ring((0,0,-.12),.34,.02)
    grate(-16,1.65,-1.29,-.47,-.05); rail((-16,-1.29),(1.65,-1.29),-.03)
    for i in range(10):
        x=-16+i*1.9; box((x,-.40,-.22),(.12,1.90,.13)); beam((x,.28,-.62),(x,-1.20,-.15),.03)
    rail((-16,-1.29),(-16,-.47),-.03); rail((1.65,-1.29),(1.65,-.47),-.03)

def bucketElevator():
    H=40.11
    for y in [-.35,.35]:
        box((0,y,(H+1)/2),(.55,.45,H-1))
        for i in range(1,21):
            z=1+i*(H-1)/20
            box((0,y,z),(.63,.53,.035))
            for xx in [-.27,.27]:
                for yy in [y-.20,y+.20]: bolt((xx,yy,z+.018),radius=.012)
    for xx in [-.70,.70]: box((xx,0,.08),(.12,1.8,.16)); foot(xx,-.7); foot(xx,.7)
    box((0,0,.96),(1.32,1.48,1.65)); hatch((0,-.76,.74),(.87,.03,.75))
    for x in [-.54,.54]:
        box((x,-.78,1.37),(.10,.12,.55),'dark'); bolt((x,-.86,1.40),(0,-1,0),.025)
    # Sloped open receiving hopper, not a closed solid slab.
    k=len(V); V.extend([( .65,-.37,.50),(.65,.37,.50),(1.75,.65,1.12),(1.75,-.65,1.12),(.65,-.37,.29),(.65,.37,.29),(1.75,.65,.70),(1.75,-.65,.70)])
    for f in [(0,3,7,4),(1,5,6,2),(2,6,7,3),(4,7,6,5)]: face(tuple(k+i for i in f))
    for a,b in [(V[k],V[k+3]),(V[k+3],V[k+2]),(V[k+2],V[k+1])]: beam(a,b,.022)
    # Curved head hood, axis Y, lower sides squared off.
    # One continuous extruded arched hood: overlapping cylinder/box caps flicker.
    profile=[(-.61,H-.04),(.61,H-.04)]
    profile += [(.61*math.cos(i*math.pi/32),H+.82+.61*math.sin(i*math.pi/32)) for i in range(33)]
    k=len(V); count=len(profile)
    for yy in [-.72,.72]: V.extend((xx,yy,zz) for xx,zz in profile)
    face(tuple(k+i for i in range(count))); face(tuple(k+count+i for i in reversed(range(count))))
    for i in range(count):
        j=(i+1)%count; face((k+i,k+j,k+count+j,k+count+i),'galv',i>=2 and i<count-1)
    for y in [-.735,.735]:
        for i in range(11):
            a=i*math.pi/10; bolt((.54*math.cos(a),y,H+.82+.54*math.sin(a)),(0,-1 if y<0 else 1,0))
    hatch((0,-.75,H+.42),(.80,.03,.55))
    box((0,.84,H+.62),(.48,.25,.48),'blue'); motor((0,1.37,H+.65),'y',1.15); guard((.44,.98,H+.68),.45,.83)
    cylinder((0,.6,H+.60),(0,1.08,H+.60),.06,'dark')
    # Descending enclosed rectangular outlet toward conveyor feed.
    beam((.45,0,H+.32),(1.18,0,H-.60),.30)
    grate(-1.25,1.25,-1.15,1.95,H-.65)
    rail((-1.25,-1.15),(1.25,-1.15),H-.65); rail((-1.25,-1.15),(-1.25,1.95),H-.65); rail((-1.25,1.95),(1.25,1.95),H-.65); rail((1.25,1.95),(1.25,-1.15),H-.65)
    for y in [-.95,1.75]:
        beam((-.2,y,H-2.1),(-1.15,y,H-.70),.035); beam((.2,y,H-2.1),(1.15,y,H-.70),.035)
    # Access ladder on side; hoops, rungs and intermediate rest platforms.
    for x in [-.29,.29]: beam((x,-.98,.30),(x,-.98,H+.35),.025)
    for i in range(int(H/.30)): beam((-.29,-.98,.45+i*.30),(.29,-.98,.45+i*.30),.014)
    for z in [2.5+i*.9 for i in range(43)]:
        # Cage bows project out from ladder, leaving access side at trunk.
        k=len(V); coords=[]
        for i in range(21):
            a=i*math.pi/20; coords.append((.39*math.cos(a),-1.00-.65*math.sin(a),z))
        for a,b in zip(coords,coords[1:]): beam(a,b,.012)
    for a in [0,math.pi/4,math.pi/2,3*math.pi/4,math.pi]: beam((.39*math.cos(a),-1-.65*math.sin(a),2.5),(.39*math.cos(a),-1-.65*math.sin(a),H+.15),.012)
    for z in [10,20,30]:
        grate(-.9,.9,-1.85,-.70,z); rail((-.9,-1.85),(.9,-1.85),z); rail((-.9,-1.85),(-.9,-.7),z); rail((.9,-1.85),(.9,-.7),z)
    for deg in [40,160,280]:
        a=math.radians(deg); ax,ay=9*math.cos(a),9*math.sin(a)
        beam((0,0,H-2),(ax,ay,.15),.012,'dark'); cylinder((ax,ay,.08),(ax,ay,.30),.055,'bolt',12)

exec((P/'fine_geometry.py').read_text(),globals())
globals()[PART]()
mesh=bpy.data.meshes.new(PART+'_mesh'); mesh.from_pydata(V,[],F); mesh.update()
bm=bmesh.new(); bm.from_mesh(mesh); bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces)); bm.to_mesh(mesh); bm.free(); mesh.update()
obj=bpy.data.objects.new(PART+'_vis',mesh); bpy.context.collection.objects.link(obj)
for m in mats: mesh.materials.append(m)
for i,poly in enumerate(mesh.polygons): poly.material_index=MI[i]; poly.use_smooth=SM[i]
# Planar UVs in real metres, separate per face, preserving material grain scale.
uv=mesh.uv_layers.new(name='UVMap')
for f in mesh.polygons:
    n=f.normal; ax=max(range(3),key=lambda k:abs(n[k])); ab=[k for k in range(3) if k!=ax]
    shifts=[math.floor(sum(mesh.vertices[vi].co[a] for vi in f.vertices)/len(f.vertices)) for a in ab]
    for li in f.loop_indices:
        co=mesh.vertices[mesh.loops[li].vertex_index].co; uv.data[li].uv=(co[ab[0]]-shifts[0],co[ab[1]]-shifts[1])
mesh.uv_layers.new(name='UVMap2',do_init=True)
root=bpy.data.objects.new(PART,None); bpy.context.collection.objects.link(root); obj.parent=root
obj['i3D_collision']=False
bpy.context.view_layer.objects.active=obj; obj.select_set(True)
# Bevel substantial sheet/box edges, not every microscopic bolt and cage wire.
adj={tuple(sorted(e.vertices)):[] for e in mesh.edges}
for poly in mesh.polygons:
    ids=list(poly.vertices)
    for a,b in zip(ids,ids[1:]+ids[:1]): adj[tuple(sorted((a,b)))].append(poly)
weights=mesh.attributes.new('bevel_weight_edge','FLOAT','EDGE')
for edge in mesh.edges:
    faces=adj[tuple(sorted(edge.vertices))]; length=(mesh.vertices[edge.vertices[0]].co-mesh.vertices[edge.vertices[1]].co).length
    if length>.08 and len(faces)==2 and all(not f.use_smooth for f in faces) and faces[0].normal.dot(faces[1].normal)<.8: weights.data[edge.index].value=1
bev=obj.modifiers.new('Manufactured edge highlights','BEVEL'); bev.width=.0025; bev.segments=2; bev.limit_method='WEIGHT'
bpy.ops.object.modifier_apply(modifier=bev.name)
try:
    no=obj.modifiers.new('Face weighted normals','WEIGHTED_NORMAL'); no.keep_sharp=True; bpy.ops.object.modifier_apply(modifier=no.name)
except Exception: pass
mesh=obj.data
stats={'part':PART,'vertices':len(mesh.vertices),'triangles':sum(len(p.vertices)-2 for p in mesh.polygons),'uv_layers':len(mesh.uv_layers),'materials':len(mesh.materials),'dimensions_m':list(obj.dimensions),'collision':False}
(OUT/'geometry_report.json').write_text(json.dumps(stats,indent=2))
print('GEOMETRY',stats)

# Save editable Blender source with textures still on the same material nodes.
sc=bpy.context.scene; sc.render.engine='CYCLES'; sc.cycles.samples=24; sc.cycles.use_denoising=True
sc.render.resolution_percentage=100; sc.render.image_settings.file_format='PNG'
sc.world=bpy.data.worlds.new('Studio world'); sc.world.use_nodes=True; sc.world.node_tree.nodes['Background'].inputs[0].default_value=(.12,.15,.20,1); sc.world.node_tree.nodes['Background'].inputs[1].default_value=.45
lo=Vector((min(v.co.x for v in mesh.vertices),min(v.co.y for v in mesh.vertices),min(v.co.z for v in mesh.vertices)))
hi=Vector((max(v.co.x for v in mesh.vertices),max(v.co.y for v in mesh.vertices),max(v.co.z for v in mesh.vertices)))
mid=(lo+hi)/2
bpy.ops.mesh.primitive_plane_add(size=2000,location=(0,0,lo.z-.04)); ground=bpy.context.object; ground.name='PREVIEW_ground'
gm=bpy.data.materials.new('PREVIEW_floor'); gm.use_nodes=True; gm.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value=(.025,.032,.045,1); gm.node_tree.nodes['Principled BSDF'].inputs['Roughness'].default_value=.7; ground.data.materials.append(gm)
for loc,energy,size in [((4,-7,10),2200,7),((-6,-2,7),1800,6),((2,8,10),3000,5)]:
    bpy.ops.object.light_add(type='AREA',location=loc); light=bpy.context.object; light.data.energy=energy; light.data.shape='DISK'; light.data.size=size; light.rotation_euler=(mid-light.location).to_track_quat('-Z','Y').to_euler()
if PART=='bucketElevator':
    bpy.ops.object.light_add(type='SUN',rotation=(.3,-.5,-.8)); bpy.context.object.data.energy=.8
    for o in bpy.data.objects:
        if o.type=='LIGHT' and o.data.type=='AREA': o.location.z+=28; o.data.energy*=1.7
if PART=='roofFill':
    # Flat crown for context only: deliberately excluded from exported part.
    bpy.ops.mesh.primitive_cylinder_add(vertices=128,radius=2.5,depth=.04,location=(0,0,-.025)); disk=bpy.context.object; disk.name='PREVIEW_flat_roof_crown'; disk.data.materials.append(mats[0])
    # Context conveyor uses the same actual conveyor geometry, not an illustrative substitute.
    V=[]; F=[]; MI=[]; SM=[]; conveyor()
    cm=bpy.data.meshes.new('PREVIEW_conveyor_mesh'); cm.from_pydata(V,[],F); cm.update()
    bm=bmesh.new(); bm.from_mesh(cm); bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces)); bm.to_mesh(cm); bm.free(); cm.update()
    co=bpy.data.objects.new('PREVIEW_conveyor_context',cm); bpy.context.collection.objects.link(co); co.location.z=1.80
    for m in mats: cm.materials.append(m)
    cuv=cm.uv_layers.new(name='UVMap')
    for i,f in enumerate(cm.polygons):
        f.material_index=MI[i]; f.use_smooth=SM[i]; ax=max(range(3),key=lambda k:abs(f.normal[k])); ab=[k for k in range(3) if k!=ax]
        for li in f.loop_indices:
            c=cm.vertices[cm.loops[li].vertex_index].co; cuv.data[li].uv=(c[ab[0]],c[ab[1]])
    cm.uv_layers.new(name='UVMap2',do_init=True)
bpy.ops.object.camera_add(); cam=bpy.context.object; sc.camera=cam
def view(label,loc,target,scale,rx=1400,ry=1100):
    cam.location=loc; cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler(); cam.data.type='ORTHO'; cam.data.ortho_scale=scale; sc.render.resolution_x=rx; sc.render.resolution_y=ry; sc.render.filepath=str(OUT/(PART+'_'+label+'.png')); bpy.ops.render.render(write_still=True)
# Save includes cameras and studio objects as PREVIEW context; export excludes them.
cam.location=mid+Vector((6,-9,5)); cam.rotation_euler=(mid-cam.location).to_track_quat('-Z','Y').to_euler()
if PART=='aerationBlower': view('preview',(5,-7,4),(1.3,0,1),4.3)
elif PART=='roofFill':
    view('preview',(6,8,5),(0,0,1.05),6.3)
    view('cone_detail',(3.6,4.8,2.7),(0,0,.38),2.3,1400,1100)
    co.hide_render=True
    view('center_top',(0,0,12),(0,0,0),5.7,1400,1400)
    co.hide_render=False
elif PART=='conveyor':
    view('preview',(7,-8,4),(-4.2,-.2,.35),18)
    view('drive_detail',(5,5,3),(.7,.2,.4),4.0)
else:
    view('preview',(55,-75,38),(0,0,20),48,1100,1600)
    view('head_detail',(5,7,43),(0,.4,40.6),5.2)
    view('boot_detail',(5,-6,4),(.4,-.2,1.0),4.7)
for im in bpy.data.images:
    if im.source=='FILE':
        im.pack(); im.filepath='//../textures/'+Path(im.filepath).name
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/(PART+'.blend')),relative_remap=False)
# Strip stage only after .blend and renders are saved.
for o in list(bpy.data.objects):
    if o not in (obj,root): bpy.data.objects.remove(o,do_unlink=True)
for i,m in enumerate(mats):
    # Prevent exporter collapsing materials by shared textures/constant colours.
    for node in list(m.node_tree.nodes):
        if node.type=='TEX_IMAGE': m.node_tree.nodes.remove(node)
    m.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value=((i+1)/10,.2,.3,1)
addon_utils.enable('io_export_i3d',default_set=False)
from io_export_i3d import i3d_export
from io_export_i3d.dcc import dccBlender as d
import io_export_i3d.dcc as dc
d.isNodeVisible=lambda n:bpy.data.objects[n].visible_get(); dc.isNodeVisible=d.isNodeVisible
dest=OUT/(PART+'.i3d'); d.UISetAttrBool('i3D_exportUseSoftwareFileName',False); d.UISetAttrString('i3D_exportFileLocation',str(dest)); i3d_export.I3DExportAll()
from io_export_i3d.util import logUtil
print('EXPORTLOG',logUtil.ActionLog.message)
if not dest.exists(): raise RuntimeError('Exporter did not create I3D')
tree=ET.parse(dest); rt=tree.getroot(); files=rt.find('Files')
if files is None: files=ET.SubElement(rt,'Files')
ET.SubElement(files,'File',fileId='901',filename='$data/shaders/buildingShader.xml')
for material in rt.find('Materials'):
    name=material.get('name','').removeprefix('mach_')
    if name not in names: raise RuntimeError('Unexpected material '+name)
    material.attrib={k:v for k,v in material.attrib.items() if k in ('name','materialId')}; material.set('customShaderId','901')
    for ch in list(material): material.remove(ch)
    for j,(suffix,tag) in enumerate([('diffuse','Texture'),('normal','Normalmap'),('specular','Glossmap')]):
        fid=str(910+names.index(name)*3+j); ET.SubElement(files,'File',fileId=fid,filename='../textures/'+name+'_'+suffix+'.dds'); ET.SubElement(material,tag,fileId=fid)
ET.indent(tree); tree.write(dest,encoding='utf-8',xml_declaration=True)
print('FINISHED_FINE_DETAILS_V3',PART)
