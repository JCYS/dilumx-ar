"""Vista previa estática del GLB mediante rasterizado simple (sin motor AR)."""
from pathlib import Path
import numpy as np
import trimesh as tm
from PIL import Image, ImageDraw, ImageFilter
ROOT=Path(__file__).resolve().parents[1]
N=1000

def unit(x): return x/np.linalg.norm(x)
def render(name):
    scene=tm.load(ROOT/'assets/models'/f'{name}.glb',force='scene')
    view=unit(np.array([.42,.20,1.])); right=unit(np.cross([0,1,0],view)); up=np.cross(view,right)
    center=np.array([0,scene.extents[1]/2,0]); scale=1500
    canvas=Image.new('RGBA',(N,N)); shadow=Image.new('RGBA',(N,N)); d=ImageDraw.Draw(shadow)
    base_y=N/2+center[1]*up[1]*scale
    d.ellipse((N/2-130,base_y-16,N/2+130,base_y+24),fill=(43,32,19,70));canvas.alpha_composite(shadow.filter(ImageFilter.GaussianBlur(18)))
    triangles=[]
    for mesh in scene.geometry.values():
        v=mesh.vertices-center; p=np.column_stack([v@right*scale+N/2,-v@up*scale+N/2]); z=v@view
        f=mesh.faces; normals=mesh.vertex_normals[f].mean(axis=1); normals/=np.maximum(np.linalg.norm(normals,axis=1)[:,None],1e-8)
        mat=mesh.visual.material; color=np.array(mat.baseColorFactor[:3],dtype=float)
        if color.max()<=1: color*=255
        rgb=np.tile(color,(len(f),1)); tex=mat.baseColorTexture
        if tex is not None:
            t=np.asarray(tex.convert('RGB').filter(ImageFilter.GaussianBlur(8))); uv=mesh.visual.uv[f].mean(axis=1); x=np.clip((uv[:,0]*(t.shape[1]-1)).astype(int),0,t.shape[1]-1); y=np.clip(((1-uv[:,1])*(t.shape[0]-1)).astype(int),0,t.shape[0]-1);rgb*=t[y,x]/255
        diffuse=np.clip(normals@unit(np.array([-.5,.8,1.])),0,1); fill=np.clip(normals@unit(np.array([1,.4,-.4])),0,1)
        lighting=.63+.42*diffuse+.16*fill
        rgb*=lighting[:,None]
        if (mat.metallicFactor or 0)>.7:
            az=np.arctan2(normals[:,0],normals[:,2]); highlight=np.exp(-((az+.55)/.25)**2)+.5*np.exp(-((az-1.1)/.35)**2)
            rgb=rgb*(.65+.25*diffuse[:,None])+highlight[:,None]*np.array([100,83,52])
        emissive=mat.emissiveFactor
        if emissive is not None:rgb+=np.asarray(emissive)*55
        rgb=np.clip(rgb,0,255).astype(int)
        for i,face in enumerate(f):
            if (normals[i]@view)<-.15 and mat.baseColorTexture is None: continue
            triangles.append((z[face].mean(),p[face],tuple(rgb[i])+ (255,)))
    d=ImageDraw.Draw(canvas)
    for _,poly,col in sorted(triangles,key=lambda x:x[0]): d.polygon([tuple(x) for x in poly],fill=col)
    canvas.resize((650,650),Image.Resampling.LANCZOS).save(ROOT/'assets/images'/f'{name}-preview.png')
for name in ['giselle','emilia']:render(name)
