"""Fine-detail geometry overrides, executed in the shared builder namespace."""
old_blower=aerationBlower; old_conveyor=conveyor; old_elevator=bucketElevator

def transform_added(start,origin,axis='y',angle=0):
    c,s=math.cos(angle),math.sin(angle)
    for i in range(start,len(V)):
        x,y,z=V[i]; x,z=x*c-z*s,x*s+z*c
        p=(x,y,z) if axis=='y' else (y,x,z)
        V[i]=tuple(Vector(p)+Vector(origin))

def channel(c,length,width=.14,height=.20,axis='x'):
    x,y,z=c; t=.012
    if axis=='x':
        box((x,y,z),(length,t,height)); box((x,y+width/2,z-height/2),(length,width,t)); box((x,y+width/2,z+height/2),(length,width,t))
    else:
        box((x,y,z),(t,length,height)); box((x+width/2,y,z-height/2),(width,length,t)); box((x+width/2,y,z+height/2),(width,length,t))

def triangular_plate(a,b,c,thickness=.009,mat='galv'):
    a,b,c=Vector(a),Vector(b),Vector(c); normal=(b-a).cross(c-a).normalized()*thickness/2; k=len(V)
    V.extend(tuple(p+normal*s) for s in [-1,1] for p in [a,b,c])
    for f in [(0,2,1),(3,4,5),(0,1,4,3),(1,2,5,4),(2,0,3,5)]: face(tuple(k+i for i in f),mat)

def perforated_panel(w,h,y,R=.024,mat='yellow',circle=None):
    # Hexagonal cells tile into a true perforated metal sheet, including hole walls.
    dx=math.sqrt(3)*R; dz=1.5*R; thick=.003
    for row in range(-math.ceil(h/dz),math.ceil(h/dz)+1):
        z=row*dz
        for col in range(-math.ceil(w/dx),math.ceil(w/dx)+1):
            x=(col+(.5 if row%2 else 0))*dx
            if abs(x)>w/2-R or abs(z)>h/2-R: continue
            if circle and math.hypot(x,z)>circle-R: continue
            k=len(V)
            for yy in [y,y+thick]:
                for rad in [R,R*.62]:
                    for j in range(6):
                        a=math.pi/6+j*math.pi/3; V.append((x+rad*math.cos(a),yy,z+rad*math.sin(a)))
            for j in range(6):
                q=(j+1)%6
                for f in [(j,q,6+q,6+j),(12+q,12+j,18+j,18+q),(6+j,6+q,18+q,18+j)]: face(tuple(k+i for i in f),mat)

def guard(c,w=.58,h=.78):
    # Fully formed rounded enclosure, replacing the flat yellow wire fence.
    start=len(V); depth=.17; rad=min(.10,w*.20,h*.17)
    profile=[]
    for cx,cz,aa in [(w/2-rad,h/2-rad,0),(-w/2+rad,h/2-rad,90),(-w/2+rad,-h/2+rad,180),(w/2-rad,-h/2+rad,270)]:
        for j in range(7):
            a=math.radians(aa+j*15); profile.append((cx+rad*math.cos(a),cz+rad*math.sin(a)))
    k=len(V); n=len(profile)
    for yy in [-depth/2,depth/2]: V.extend((x,yy,z) for x,z in profile)
    for i in range(n):
        j=(i+1)%n; face((k+i,k+j,k+n+j,k+n+i),'yellow',True)
    # Fine punched sheet covers the front; enclosure wraps along the entire perimeter.
    perforated_panel(w-.016,h-.016,-depth/2-.003,R=min(.024,w/12))
    for zz in [-h/2+.02,h/2-.02]: box((0,-depth/2,zz),(w-rad,.012,.04),'yellow')
    for xx in [-w/2+.02,w/2-.02]: box((xx,-depth/2,0),(.04,.012,h-rad),'yellow')
    for xx in [-w/2+.05,w/2-.05]:
        for zz in [-h/2+.05,h/2-.05]: bolt((xx,-depth/2-.012,zz),(0,-1,0),.011)
    transform_added(start,c)

def motor(c,axis='y',scale=1):
    # Axial cooling fins, real ventilated fan shroud, end shields and terminal cover.
    start=len(V); s=scale
    cylinder((0,-.30,0),(0,.30,0),.19,'blue',48)
    for i in range(28):
        a=i*2*math.pi/28; xx,zz=.212*math.cos(a),.212*math.sin(a)
        st=len(V); box((.212,0,0),(.053,.48,.009),'blue')
        for j in range(st,len(V)):
            x,y,z=V[j]; V[j]=(x*math.cos(a)-z*math.sin(a),y,x*math.sin(a)+z*math.cos(a))
    for yy in [-.285,.285]:
        cylinder((0,yy-.014,0),(0,yy+.014,0),.216,'blue',48)
        for i in range(8):
            a=i*math.pi/4; bolt((.177*math.cos(a),yy+(.018 if yy>0 else -.018),.177*math.sin(a)),(0,1 if yy>0 else -1,0),.012)
    cylinder((0,.31,0),(0,.40,0),.225,'blue',48)
    cylinder((0,.405,0),(0,.412,0),.199,'dark',48)
    # Front face of cap is holes over a dark recessed fan cavity.
    st=len(V); perforated_panel(.40,.40,-.423,R=.017,mat='blue',circle=.195)
    for j in range(st,len(V)): x,y,z=V[j]; V[j]=(x,-y,z)
    ring((0,.426,0),.207,.016,'y','blue')
    box((0,-.04,.251),(.24,.25,.10),'blue'); box((0,-.04,.308),(.26,.27,.017),'blue')
    for x in [-.096,.096]:
        for y in [-.13,.05]: bolt((x,y,.321),radius=.009)
    cylinder((.145,-.05,.26),(.20,-.05,.26),.023,'dark',16)
    for x in [-.18,.18]:
        box((x,0,-.22),(.10,.44,.035),'blue')
        for y in [-.16,.16]: bolt((x,y,-.197),radius=.014)
    ring((0,-.08,.37),.043,.012,'y','bolt',32)
    # Small screwed identification plate, no invented branding.
    box((-.15,-.03,.15),(.12,.20,.008),'bolt')
    box((0,0,-.26),(.60,.67,.045))
    for j in range(start,len(V)): V[j]=tuple(Vector(V[j])*s)
    transform_added(start,c,axis)

def bearing(c,axis='y'):
    x,y,z=c; st=len(V)
    box((0,0,0),(.26,.10,.23),'blue'); cylinder((0,-.07,0),(0,-.12,0),.085,'blue',32)
    cylinder((0,-.122,0),(0,-.133,0),.047,'dark',24)
    for xx in [-.095,.095]:
        for zz in [-.075,.075]: bolt((xx,-.065,zz),(0,-1,0),.010)
    transform_added(st,c,axis)

def aerationBlower():
    old_blower()
    # Peripheral volute joining strip follows the original expanding scroll.
    cx,cz=1.48,1.17
    for yy in [-.319,.319]:
        for i in range(36):
            a=i*2*math.pi/36; r=.57+.20*i/35
            b=(i+1)*2*math.pi/36; rr=.57+.20*(i+1)/35
            if i<35: beam((cx+r*math.cos(a),yy,cz+r*math.sin(a)),(cx+rr*math.cos(b),yy,cz+rr*math.sin(b)),.015)
            if i%2==0: bolt((cx+(r-.032)*math.cos(a),yy,cz+(r-.032)*math.sin(a)),(0,-1 if yy<0 else 1,0),.015)
    for xx in [.03,.70]:
        for yy in [-.42,.42]:
            box((xx,yy,.90),(.052,.045,.77))
            for zz in [.57,.73,.90,1.07,1.23]: bolt((xx-.032,yy,zz),(-1,0,0),.014)
    # Fabricated channel structure, adjustable mounting slots and motor pedestal gussets.
    for yy in [-.62,.62]: channel((1.45,yy,.22),2.10,.14,.22)
    for xx in [.50,2.34]: channel((xx,0,.24),1.4,.12,.20,'y')
    for xx in [1.70,2.34]:
        triangular_plate((xx,.61,.35),(xx,.61,.61),(xx,1.20,.35))
        box((xx,.95,.515),(.16,.42,.012))
        for yy in [.81,1.06]:
            box((xx,yy,.523),(.045,.11,.003),'dark'); bolt((xx,yy,.529),radius=.017)
    ring((1.52,0,1.995),.055,.015,'y','bolt',40)
    # Rolled skin seam across the hood.
    for i in range(12):
        a=.25+i*.19; r=.66
        if i<11: beam((cx+r*math.cos(a),-.02,cz+r*math.sin(a)),(cx+r*math.cos(a+.19),-.02,cz+r*math.sin(a+.19)),.009)

def roofFill():
    start=len(V)
    flange(.035,.94,pipe=.80)
    tube(.055,.70,.85,.832,r2=.30)
    # Flanges and cone are generated around exactly X=0,Y=0, no visual offset.
    cone_vertices=V[start:]; lo=[min(v[a] for v in cone_vertices) for a in [0,1]]; hi=[max(v[a] for v in cone_vertices) for a in [0,1]]
    center=[(lo[i]+hi[i])/2 for i in [0,1]]
    assert max(abs(v) for v in center)<1e-6
    (OUT/'centering_report.json').write_text(json.dumps({'coordinate_system':'Blender XY horizontal, Z up','cone_center_xy_m':center,'flat_crown_center_xy_m':[0,0],'offset_m':math.hypot(*center),'crown_radius_m':2.5,'cone_base_radius_m':.85,'verified_by':'actual cone/base flange geometry bounds; direct top-view render'},indent=2))
    for z in [.71,1.23,1.78]: flange(z,.36)
    tube(.72,1.80,.29,.273)
    # Approved v4 cone: raised radial lap seams and round rivets.
    slope=.55/.645
    def surf(theta,z,offset=0):
        r=.85-(z-.055)*slope
        n=Vector((math.cos(theta),math.sin(theta),slope)).normalized()
        return Vector((r*math.cos(theta),r*math.sin(theta),z))+n*offset,n
    def rivet(pos,normal,r=.012):
        cylinder(pos-normal*.002,pos+normal*.003,r*1.3,'bolt',12)
        cylinder(pos+normal*.003,pos+normal*.009,r,'bolt',12,r2=r*.70)
    for j in range(12):
        theta=j*2*math.pi/12
        a,n=surf(theta,.085,.003); b,n=surf(theta,.665,.003)
        beam(a,b,.004)
        for k in range(8):
            pos,n=surf(theta,.10+k*.076,.007); rivet(pos,n)
    for z,count in [(.092,48),(.66,24)]:
        for j in range(count):
            pos,n=surf((j+.5)*2*math.pi/count,z,.007); rivet(pos,n)
    # Curved trapezoid hatch follows the cone surface; no buried corners.
    theta=math.atan2(8,6)
    def panel(zlo,zhi,halfangle,offset,mat):
        k=len(V); steps=16
        for off in [offset,offset+.012]:
            for z in [zlo,zhi]:
                for j in range(steps+1):
                    pos,n=surf(theta-halfangle+2*halfangle*j/steps,z,off)
                    V.append(tuple(pos))
        row=steps+1
        for j in range(steps):
            face((k+j,k+j+1,k+row+j+1,k+row+j),mat,True)
            face((k+2*row+j,k+3*row+j,k+3*row+j+1,k+2*row+j+1),mat,True)
            for q in [0,1]:
                i=k+q*row+j; face((i,i+2*row,i+2*row+1,i+1),mat)
        for j in [0,steps]: face((k+j,k+row+j,k+3*row+j,k+2*row+j),mat)
    panel(.145,.575,.30,.012,'galv')
    panel(.160,.560,.278,.027,'rubber')
    panel(.170,.550,.261,.034,'galv')
    tangent=Vector((-math.sin(theta),math.cos(theta),0))
    # Two functional-looking hinge barrels and mounting leaves.
    for z in [.255,.465]:
        pos,n=surf(theta-.28,z,.058)
        vertical=Vector((-slope*math.cos(theta),-slope*math.sin(theta),1)).normalized()
        cylinder(pos-vertical*.043,pos+vertical*.043,.018,'bolt',20)
        for side in [-1,1]:
            pp=pos+tangent*side*.027
            cylinder(pp-n*.006,pp+n*.003,.025,'galv',8)
            rivet(pp+n*.005,n,.008)
    pos,n=surf(theta+.275,.36,.062)
    cylinder(pos-tangent*.045,pos+tangent*.045,.015,'bolt',12)
    for z in [.30,.43]:
        pp,n=surf(theta+.34,z,.045)
        beam(pp,pp+n*.060,.012,'bolt')
    a,n=surf(theta+.34,.30,.105); b,n=surf(theta+.34,.43,.105)
    beam(a,b,.012,'bolt')
    for x in [-2.0,1.35]:
        for y in [-1.25,.35]:
            foot(x,y); box((x,y,.87),(.095,.095,1.70));
            for dx in [-.06,.06]: triangular_plate((x+dx,y,.045),(x+dx,y,.27),(x+dx,y+.13,.045))
        channel((x,-.45,1.74),2.0,.12,.12,'y')
        beam((x,-1.25,.20),(x,.35,1.62),.029)
        for y in [-1.25,.35]:
            box((x,y,1.60),(.15,.15,.25))
            for z in [1.52,1.66]: bolt((x-.08,y,z),(-1,0,0),.015)
    # End at the actual cross beams rather than mid-air near the inlet pipe.
    for y in [-1.25,.35]:
        beam((-2,y,.24),(1.35,y,1.65),.027)
        for x,z in [(-2,.24),(1.35,1.65)]:
            box((x,y,z),(.16,.018,.22)); bolt((x,y-.015,z),(0,-1,0),.014)

def conveyor():
    old_conveyor()
    for x in [-16+i*2 for i in range(9)]:
        for yy in [-.403,.403]:
            box((x,yy,.38),(.105,.025,.80))
            for zz in [.05,.22,.39,.56,.73]: bolt((x,yy+(-.02 if yy<0 else .02),zz),(0,-1 if yy<0 else 1,0),.014)
        # Folded lid skirts.
        for yy in [-.385,.385]: box((x,yy,.758),(1.94,.025,.06))
    for y in [-.46,-1.30]: box((-7.15,y,.035),(17.7,.018,.13))
    for i in range(10):
        x=-16+i*1.9
        triangular_plate((x-.06,-.42,-.22),(x-.06,-.42,-.49),(x-.06,-.93,-.22))
        for yy in [-1.18,-.52]: bolt((x,yy,-.125),(0,1,0),.014)
    bearing((1.2,-.48,.42)); bearing((-15.85,-.41,.39))
    cylinder((1.2,-.48,.42),(1.2,-.64,.42),.042,'dark',24)
    # Head access and joint fasteners.
    for x in [.90,1.5]:
        for z in [.10,.31,.55,.76]: bolt((x,-.445,z),(0,-1,0),.014)
    for y in [.88,1.35]:
        for x in [.96,1.44]: bolt((x,y,.23),radius=.016)

def bucketElevator():
    old_elevator(); H=40.11
    # Twin-trunk longitudinal rolled seams and removable modular flanges.
    for yy in [-.35,.35]:
        for x in [-.286,.286]: box((x,yy,H/2+.5),(.025,.49,H-1))
        for i in range(1,21):
            z=1+i*(H-1)/20
            for x in [-.315,.315]:
                for y in [yy-.20,yy,yy+.20]: bolt((x,y,z),(1 if x>0 else -1,0,0),.014)
    # Fine seams, clamps, access hinges and bearing frames on the head.
    for yy in [-.738,.738]:
        for z in [H+.04,H+.77]:
            box((0,yy,z),(1.21,.024,.045))
            for x in [-.53,-.27,0,.27,.53]: bolt((x,yy+(-.015 if yy<0 else .015),z),(0,-1 if yy<0 else 1,0),.015)
        for x in [-.59,.59]: box((x,yy,H+.40),(.045,.025,.80))
    bearing((0,-.80,H+.63))
    for xx in [-.46,.46]:
        for zz in [H+.22,H+.60]: bolt((xx,-.779,zz),(0,-1,0),.014)
    ring((0,0,H+1.53),.062,.014,'y','bolt',40)
    # Boot cleanout latches, take-up jacks and fabricated base flanges.
    for x in [-.54,.54]:
        cylinder((x,-.89,1.10),(x,-.89,1.80),.018,'bolt',16)
        for z in [1.13,1.65]: cylinder((x,-.89,z-.018),(x,-.89,z+.018),.037,'bolt',6)
    for x in [-.69,.69]:
        for y in [-.62,-.31,0,.31,.62]: bolt((x,y,.20),radius=.018)
    for x in [-.56,-.28,0,.28,.56]:
        for z in [.17,1.77]: bolt((x,-.76,z),(0,-1,0),.016)
    for yy in [-.65,.65]:
        for t in [0,.33,.66,1]: bolt((1.0+t*.70,yy,.73+t*.33),(0,-1 if yy<0 else 1,0),.013)
    # Cable conduit attached to trunk, and service platform brackets.
    beam((.36,.08,1.4),(.36,.08,H+.5),.012,'dark')
    for z in range(2,40,2): box((.36,.08,z),(.055,.07,.035))
    for x in [-1.16,1.16]:
        for y in [-1.05,1.83]:
            triangular_plate((x,y,H-.68),(x,y,H-.95),(x-.22 if x>0 else x+.22,y,H-.68))
            bolt((x,y,H-.615),radius=.016)
    # Turnbuckles on the three guy-wire ground ends.
    for deg in [40,160,280]:
        a=math.radians(deg); ax,ay=9*math.cos(a),9*math.sin(a)
        beam((ax,ay,.30),(ax*.98,ay*.98,1.12),.027,'bolt')
