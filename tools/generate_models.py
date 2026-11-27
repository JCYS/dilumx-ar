"""Genera modelos GLB en metros, eje Y vertical. Requiere numpy, trimesh, Pillow."""
from pathlib import Path
import numpy as np
import trimesh as tm
from PIL import Image
from trimesh.visual import TextureVisuals
from trimesh.visual.material import PBRMaterial
ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT/'assets/models'; OUT.mkdir(parents=True, exist_ok=True)

def material(name, color, metal=0, rough=.5, texture=None, emissive=None):
    return PBRMaterial(name=name, baseColorFactor=color, metallicFactor=metal,
        roughnessFactor=rough, baseColorTexture=texture, emissiveFactor=emissive, doubleSided=True)

BLACK = material('Aluminio negro satinado', [32,29,26,255], .5,.32)
GOLD = material('Aluminio dorado cepillado', [200,147,64,255], .84,.28)
DARK = material('Casquillo oscuro', [43,38,33,255], .4,.5)
BULB = material('Bombilla opalina (referencial)', [255,226,170,255], 0,.4, emissive=[.55,.30,.10])
LINING = material('Forro textil marfil', [228,200,152,255],0,.93,emissive=[.09,.06,.025])

def cloth(dark):
    rng=np.random.default_rng(23 if dark else 24)
    w,h=512,512; y,x=np.mgrid[0:h,0:w]; u=x/w; v=y/h
    noise=rng.normal(0,1,(h,w)); weave=np.sin(x*2.7)+np.sin(y*2.5)
    glow=np.exp(-((v-.5)/.35)**2)*(.86+.14*np.cos(u*2*np.pi))
    if dark:
        rgb=np.array([30,25,21])+glow[...,None]*np.array([55,31,10])+noise[...,None]*np.array([9,6,4])+weave[...,None]*2
    else:
        rgb=np.array([239,215,167])+glow[...,None]*np.array([10,13,19])+noise[...,None]*2+weave[...,None]*1.8
    return Image.fromarray(np.uint8(np.clip(rgb,0,255)), 'RGB')

SHADE_BLACK=material('Tela negra tejida', [255,255,255,255],0,.95,cloth(True),[.035,.017,.004])
SHADE_IVORY=material('Tela marfil plisada', [255,255,255,255],0,.95,cloth(False),[.16,.11,.045])

# Superficie de revolución con coordenadas UV: cada perfil contiene (radio, altura).
# La ondulación radial periódica representa pliegues físicos, no solo una textura.
def lathe(profile, mat, segments=128, pleats=0, amplitude=0):
    theta=np.linspace(0,2*np.pi,segments+1); vertices=[]; uv=[]; faces=[]
    yvals=[p[1] for p in profile]; lo,hi=min(yvals),max(yvals)
    for radius,height in profile:
        r=np.maximum(0,radius+(amplitude*np.cos(pleats*theta) if pleats else 0))
        vertices.extend(np.column_stack([r*np.cos(theta),np.full_like(theta,height),r*np.sin(theta)]))
        uv.extend(np.column_stack([theta/(2*np.pi),np.full_like(theta,(height-lo)/max(hi-lo,1e-8))]))
    for j in range(len(profile)-1):
        for i in range(segments):
            a=j*(segments+1)+i; b=a+segments+1
            faces.extend([(a,b,a+1),(a+1,b,b+1)])
    mesh=tm.Trimesh(vertices=vertices,faces=faces,process=False)
    mesh.visual=TextureVisuals(uv=np.array(uv),material=mat)
    return mesh

def solid(profile, mat, segments=128):
    # Tapas con radio casi cero evitan triángulos degenerados en el eje.
    return lathe([(0.000001,profile[0][1]),*profile,(0.000001,profile[-1][1])],mat,segments)

def add(scene,name,mesh): scene.add_geometry(mesh,node_name=name,geom_name=name)

def support(scene, bottom, top):
    add(scene,'Casquillo E27',solid([(.014,bottom),(.016,bottom+.004),(.016,top)],DARK,64))
    add(scene,'Bombilla ilustrativa',solid([(.011,top),(.019,top+.011),(.026,top+.027),(.026,top+.042),(.020,top+.052),(.007,top+.059)],BULB,64))

def giselle():
    s=tm.Scene()
    add(s,'Base negra',solid([(.053,0),(.057,.003),(.057,.018),(.054,.022),(.045,.023)],BLACK))
    add(s,'Borde dorado base',solid([(.042,.022),(.042,.025),(.032,.027)],GOLD))
    add(s,'Pie dorado curvo',solid([(.032,.025),(.031,.031),(.025,.036),(.019,.046),(.013,.059),(.010,.080),(.0085,.108),(.0065,.145),(.0058,.184),(.0058,.235)],GOLD))
    add(s,'Varilla negra',solid([(.0058,.235),(.0058,.303)],DARK,64))
    support(s,.285,.315)
    add(s,'Pantalla negra',lathe([(.1025,.278),(.103,.282),(.103,.292),(.100,.31),(.096,.35),(.090,.40),(.083,.45),(.079,.477),(.077,.48)],SHADE_BLACK))
    add(s,'Forro interior',lathe([(.0755,.478),(.0775,.475),(.102,.280)],LINING))
    add(s,'Aro inferior dorado',lathe([(.102,.278),(.105,.278),(.105,.291),(.1045,.292),(.1033,.291),(.1033,.279)],GOLD))
    add(s,'Aro superior oscuro',lathe([(.075,.477),(.078,.477),(.079,.4785),(.0775,.48),(.075,.48),(.075,.477)],BLACK))
    return s

def emilia():
    s=tm.Scene()
    add(s,'Base negra',solid([(.070,0),(.075,.003),(.075,.019),(.072,.024),(.058,.025)],BLACK))
    add(s,'Cuerpo dorado ovalado',solid([(.012,.025),(.021,.030),(.026,.040),(.027,.056),(.027,.130),(.024,.153),(.018,.169),(.009,.176)],GOLD))
    add(s,'Varilla negra',solid([(.008,.175),(.008,.287)],BLACK,64))
    support(s,.266,.296)
    add(s,'Pantalla plisada marfil',lathe([(.102,.259),(.1025,.261),(.098,.281),(.090,.321),(.081,.361),(.071,.401),(.062,.438),(.060,.44)],SHADE_IVORY,256,32,.0025))
    add(s,'Forro interior',lathe([(.058,.439),(.060,.437),(.100,.260)],LINING,128))
    add(s,'Ribete inferior',lathe([(.100,.259),(.1025,.259),(.1025,.262),(.100,.262),(.100,.259)],SHADE_IVORY,256,32,.0025))
    add(s,'Ribete superior',lathe([(.058,.437),(.060,.437),(.060,.44),(.058,.44),(.058,.437)],SHADE_IVORY,256,32,.0025))
    return s

if __name__=='__main__':
    for name,scene in [('giselle',giselle()),('emilia',emilia())]:
        path=OUT/f'{name}.glb'; path.write_bytes(scene.export(file_type='glb'))
        loaded=tm.load(path,force='scene'); print(name, 'metros',loaded.extents.round(4),'bytes',path.stat().st_size)
