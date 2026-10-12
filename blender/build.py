import bpy, bmesh, math, sys, numpy as np, os
from mathutils import Vector
OUT=os.path.abspath('.')
N,D=30,3;STEP=2*math.pi/N
R,T,H,GAP,BASE=0.25,0.024,0.152,0.02,0.034;Rc=R-T
TILE=0.05
bpy.ops.wm.read_factory_settings(use_empty=True)
sc=bpy.context.scene
def srgb(h):
    h=h.lstrip('#');c=[int(h[i:i+2],16)/255 for i in(0,2,4)]
    return [((x+0.055)/1.055)**2.4 if x>0.04045 else x/12.92 for x in c]+[1]

# ---------- materiais
def img(name,fn,nc=False):
    i=bpy.data.images.load(os.path.join(OUT,fn));i.name=name
    if nc:i.colorspace_settings.name='Non-Color'
    return i
def mk(name):
    m=bpy.data.materials.new(name);m.use_nodes=True;nt=m.node_tree;nt.nodes.clear()
    out=nt.nodes.new('ShaderNodeOutputMaterial');bs=nt.nodes.new('ShaderNodeBsdfPrincipled')
    nt.links.new(bs.outputs[0],out.inputs[0]);return m,nt,bs
fabric,fnt,fbs=mk('fabric')
ta=fnt.nodes.new('ShaderNodeTexImage');ta.image=img('terry_a','terry_albedo.jpg');ta.extension='REPEAT'
tn=fnt.nodes.new('ShaderNodeTexImage');tn.image=img('terry_n','terry_normal.jpg',True);tn.extension='REPEAT'
nm=fnt.nodes.new('ShaderNodeNormalMap');nm.inputs['Strength'].default_value=2.2
mix=fnt.nodes.new('ShaderNodeMix');mix.data_type='RGBA';mix.blend_type='MULTIPLY';mix.inputs[0].default_value=1
mix.inputs[7].default_value=srgb('#EEE5D7')
fnt.links.new(ta.outputs[0],mix.inputs[6]);fnt.links.new(tn.outputs[0],nm.inputs['Color']);fnt.links.new(nm.outputs[0],fbs.inputs['Normal'])
fnt.links.new(mix.outputs[2],fbs.inputs['Base Color'])
fbs.inputs['Roughness'].default_value=0.95
fbs.inputs['Sheen Weight'].default_value=0.6;fbs.inputs['Sheen Roughness'].default_value=0.5;fbs.inputs['Sheen Tint'].default_value=(1,.97,.92,1)

lac,lnt,lbs=mk('lacquer');lbs.inputs['Base Color'].default_value=srgb('#A64A2B');lbs.inputs['Roughness'].default_value=0.28
lbs.inputs['Coat Weight'].default_value=1;lbs.inputs['Coat Roughness'].default_value=0.12
brass,_,bbs=mk('brass');bbs.inputs['Base Color'].default_value=srgb('#C9AD84');bbs.inputs['Metallic'].default_value=1;bbs.inputs['Roughness'].default_value=0.4
mar,mnt,mbs=mk('marble');tm=mnt.nodes.new('ShaderNodeTexImage');tm.image=img('marble','marble.jpg')
mnt.links.new(tm.outputs[0],mbs.inputs['Base Color']);mbs.inputs['Roughness'].default_value=0.14;mbs.inputs['Coat Weight'].default_value=0.5;mbs.inputs['Coat Roughness'].default_value=0.1
core,_,cbs=mk('core');cbs.inputs['Base Color'].default_value=srgb('#7d7468');cbs.inputs['Roughness'].default_value=1

# ---------- geometria
def make(name,verts,faces,uv=None,mat=None,smooth=True):
    me=bpy.data.meshes.new(name);me.from_pydata(verts,[],faces);me.update()
    if uv is not None:
        l=me.uv_layers.new(name='UVMap')
        for poly in me.polygons:
            for li in poly.loop_indices:l.data[li].uv=uv[me.loops[li].vertex_index]
    if smooth:me.polygons.foreach_set('use_smooth',[True]*len(me.polygons))
    if mat:me.materials.append(mat)
    return me
def rib_mesh(name,uoff,voff):
    U,V=22,60;half=STEP/2*0.99;verts=[];uvs=[]
    for j in range(V+1):
        v=-1+2*j/V
        for i in range(U+1):
            u=-1+2*i/U
            sx=max(0,1-abs(u)**3.6)**(1/3.6);sy=max(0,1-abs(v)**7)**(1/7)
            rad=Rc+T*sx*sy;a=u*half;yy=v*(H/2)*(0.985+0.015*sx)
            verts.append((rad*math.sin(a),-rad*math.cos(a),yy))
            uvs.append((a*Rc/TILE+uoff,yy/TILE+voff))
    faces=[]
    for j in range(V):
        for i in range(U):
            a=j*(U+1)+i;faces.append((a,a+1,a+U+2,a+U+1))
    return make(name,verts,faces,uvs,fabric)
def lathe(profile,seg=96,uvs=False):
    verts=[];faces=[];uv=[]
    for s in range(seg):
        a=2*math.pi*s/seg
        for r,y in profile:verts.append((r*math.cos(a),r*math.sin(a),y));uv.append((a*profile[0][0]/TILE,(y+10)/TILE))
    P=len(profile)
    for s in range(seg):
        s2=(s+1)%seg
        for k in range(P-1):faces.append((s*P+k,s2*P+k,s2*P+k+1,s*P+k+1))
    return (verts,faces,uv) if uvs else (verts,faces)
def band_profile(rOut,h,rIn,cr):
    pts=[(rIn,-h/2)]
    for k in range(7):a=-math.pi/2+k/6*math.pi/2;pts.append((rOut-cr+cr*math.cos(a),-h/2+cr+cr*math.sin(a)))
    for k in range(7):a=k/6*math.pi/2;pts.append((rOut-cr+cr*math.cos(a),h/2-cr+cr*math.sin(a)))
    pts.append((rIn,h/2));return pts
col=bpy.data.collections.new('modelo');sc.collection.children.link(col)
def obj(name,me,parent=None,loc=(0,0,0)):
    o=bpy.data.objects.new(name,me);col.objects.link(o);o.location=loc
    if parent:o.parent=parent
    return o
def empty(name,loc,parent=None):
    o=bpy.data.objects.new(name,None);col.objects.link(o);o.location=loc
    if parent:o.parent=parent
    return o
root=empty('mesa',(0,0,0))
v,f=lathe(band_profile(Rc+0.004,BASE,0.05,0.006));obj('base',make('base',v,f,mat=lac),root,(0,0,BASE/2))
variants=[rib_mesh(f'ribv{k}',np.random.default_rng(k).uniform(),np.random.default_rng(k+50).uniform()) for k in range(6)]
# puxador
def knob_mesh():
    bpy.ops.object.select_all(action='DESELECT');parts=[]
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.0165,segments=40,ring_count=20,location=(0,0,0.004));d=bpy.context.object;d.scale=(1,1,0.85)
    bpy.ops.object.transform_apply(scale=True);parts.append(d)
    bpy.ops.mesh.primitive_torus_add(major_radius=0.0168,minor_radius=0.0018,major_segments=48,minor_segments=10,location=(0,0,0.004));parts.append(bpy.context.object)
    for k in range(28):
        a=k/28*2*math.pi;bpy.ops.mesh.primitive_uv_sphere_add(radius=0.0012,segments=8,ring_count=6,location=(math.cos(a)*0.0188,math.sin(a)*0.0188,0.0045));parts.append(bpy.context.object)
    bpy.ops.mesh.primitive_cylinder_add(radius=0.004,depth=0.01,vertices=16,location=(0,0,0));parts.append(bpy.context.object)
    for p in parts:p.select_set(True)
    bpy.context.view_layer.objects.active=parts[0];bpy.ops.object.join()
    k=bpy.context.object;bpy.ops.object.shade_smooth();me=k.data;bpy.data.objects.remove(k)
    me.materials.append(brass);return me
kme=knob_mesh()
drums=[]
for d in range(D):
    yb=BASE+(D-1-d)*(H+GAP);yc=yb+H/2
    dr=empty(f'drum{d}',(0,0,yc),root);drums.append(dr)
    cv,cf=lathe([(Rc+0.003,-H*0.48),(Rc+0.003,H*0.48)],72);obj(f'core{d}',make('core',cv,cf,mat=core),dr)
    for i in range(N):
        o=obj(f'rib_{d}_{i}',variants[(d*7+i*5+i//3)%6],dr);o.rotation_euler[2]=i*STEP
    k=obj(f'knob{d}',kme,dr,(0,-(R+0.001),0.004));k.rotation_euler[0]=math.pi/2
    if d>0:
        v,f=lathe(band_profile(Rc+0.006,GAP+0.004,0.05,0.004));obj(f'band{d}',make('band',v,f,mat=lac),root,(0,0,yb+H+GAP/2))
    if d==0:
        cv2,cf2,cu2=lathe(band_profile(Rc+0.002,0.011,Rc-0.020,0.005),96,True);obj('colar',make('colar',cv2,cf2,cu2,fabric),dr,(0,0,H/2-0.0035))
        # tampo: disco com UV planar
        verts=[];faces=[];uv=[];seg=96
        verts.append((0,0,0.007));uv.append((0.5,0.5))
        for s in range(seg):
            a=2*math.pi*s/seg;x,y=(Rc-0.016)*math.cos(a),(Rc-0.016)*math.sin(a)
            verts.append((x,y,0.007));uv.append((0.5+x/(2*Rc),0.5+y/(2*Rc)))
        for s in range(seg):faces.append((0,1+s,1+(s+1)%seg))
        for s in range(seg):
            a=2*math.pi*s/seg;x,y=(Rc-0.016)*math.cos(a),(Rc-0.016)*math.sin(a)
            verts.append((x,y,-0.007));uv.append((0.5+x/(2*Rc),0.5+y/(2*Rc)))
        for s in range(seg):
            a1=1+s;a2=1+(s+1)%seg;faces.append((a1,a1+seg,a2+seg,a2))
        # corrigir faces laterais para formar tubo
        me=make('marble',verts,faces,uv,mar);obj('marble',me,dr,(0,0,H/2-0.013))
bpy.context.view_layer.update()

# ---------- cena de render
fl=bpy.data.objects.new('floor',bpy.data.meshes.new('floor'));
bm=bmesh.new();bmesh.ops.create_grid(bm,x_segments=1,y_segments=1,size=8);bm.to_mesh(fl.data);bm.free()
sc.collection.objects.link(fl);fl.is_shadow_catcher=True
def light(name,loc,energy,size,target=(0,0,0.28)):
    l=bpy.data.lights.new(name,'AREA');l.energy=energy;l.size=size;o=bpy.data.objects.new(name,l);sc.collection.objects.link(o);o.location=loc
    d=Vector(target)-Vector(loc);o.rotation_euler=d.to_track_quat('-Z','Y').to_euler();return o
light('key',(-1.4,-1.5,1.8),70,1.6);light('fill',(1.8,-1.2,0.8),22,1.8);light('rim',(1.0,1.6,1.4),35,1.0)
w=bpy.data.worlds.new('w');sc.world=w;w.use_nodes=True;bg=w.node_tree.nodes['Background'];bg.inputs[0].default_value=(0.85,0.82,0.78,1);bg.inputs[1].default_value=0.35
cam=bpy.data.cameras.new('cam');cam.lens=85;co=bpy.data.objects.new('cam',cam);sc.collection.objects.link(co)
cam_pos=Vector((0.95,-2.35,1.35));co.location=cam_pos
co.rotation_euler=(Vector((0,0,0.29))-cam_pos).to_track_quat('-Z','Y').to_euler();sc.camera=co
sc.render.engine='CYCLES';sc.cycles.device='CPU';sc.cycles.samples=int(sys.argv[-2]) if len(sys.argv)>2 else 48
sc.cycles.use_denoising=True;sc.render.film_transparent=True
sc.render.resolution_x,sc.render.resolution_y=1000,1250
sc.view_settings.view_transform='AgX' if 'AgX' in [x.identifier for x in bpy.types.ColorManagedViewSettings.bl_rna.properties['view_transform'].enum_items] else 'Standard'
sc.render.filepath=os.path.join(OUT,'render.png')
if sys.argv[-1]=='render':
    bpy.ops.render.render(write_still=True)

bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT,'mesa.blend'),compress=True)
# ---------- exportar GLB (textura ligada direto à cor base; o site aplica o tecido por cima)
for l in list(fnt.links):
    if l.to_socket==fbs.inputs['Base Color']:fnt.links.remove(l)
fnt.links.new(ta.outputs[0],fbs.inputs['Base Color'])
fbs.inputs['Sheen Weight'].default_value=0
bpy.ops.object.select_all(action='DESELECT')
for o in col.objects:o.select_set(True)
bpy.ops.export_scene.gltf(filepath=os.path.join(OUT,'mesa.glb'),export_format='GLB',use_selection=True,export_image_format='JPEG',export_jpeg_quality=88,export_yup=True,export_apply=False)
print('OK')
