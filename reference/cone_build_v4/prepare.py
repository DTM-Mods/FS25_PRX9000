from pathlib import Path
p=Path(__file__).parent
f=p/'fine_geometry.py'
s=f.read_text()
a=s.index('    # Radial triangular gussets')
b=s.index('    for x in [-2.0,1.35]:',a)
s=s[:a]+'''    # Approved v4 cone: raised radial lap seams and round rivets.
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
''' +s[b:]
f.write_text(s)
b=p/'build_realistic.py'; s=b.read_text().replace('sc.cycles.samples=48','sc.cycles.samples=24')
s=s.replace("    co.hide_render=True\n    view('center_top'", "    view('cone_detail',(3.6,4.8,2.7),(0,0,.38),2.3,1400,1100)\n    co.hide_render=True\n    view('center_top'")
b.write_text(s)
