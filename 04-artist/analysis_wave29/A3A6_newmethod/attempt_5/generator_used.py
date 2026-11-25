#!/usr/bin/env python3
"""A3/A6 procedural trial. No image inputs. Run under timeout 120.

Usage: python3 -W ignore wave29_tendrils_procedural.py OUTPUT ATTEMPT
One generation is not an approval: check the unchanged official validator and
visually inspect all grids and the in-game rendering separately.
"""
import math
import sys
from pathlib import Path
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

PAL=np.array([(84,40,54),(104,47,64),(157,80,94),(161,90,96),
              (179,106,105),(196,126,119),(209,144,130)],np.uint8)
SIZE=64
BAND=4


def common_edge():
    # The quadrantal mask is mirrored, and used only in the 4px seam zone.
    q=np.zeros((32,32),np.uint8)
    cv2.rectangle(q,(7,0),(21,13),255,-1)
    cv2.rectangle(q,(0,12),(13,26),255,-1)
    return np.block([[q,np.fliplr(q)],[np.flipud(q),np.flipud(np.fliplr(q))]])


def curve(mask,a,b,bend,r0,r1):
    dx=b[0]-a[0];dy=b[1]-a[1];length=max(math.hypot(dx,dy),1)
    nx=-dy/length;ny=dx/length;pts=[]
    for j in range(7):
        u=j/6;wave=math.sin(math.pi*u)*bend
        pts.append((int(round(a[0]+dx*u+nx*wave)),int(round(a[1]+dy*u+ny*wave))))
    for j in range(6):
        u=(j+.5)/6;r=r0*(1-u)+r1*u
        cv2.line(mask,pts[j],pts[j+1],255,int(round(2*r)),cv2.LINE_8)
    cv2.circle(mask,pts[0],int(round(r0)),255,-1)
    cv2.circle(mask,pts[-1],int(round(r1)),255,-1)


def build(common,attempt,num):
    rng=np.random.default_rng(48111+attempt*1021+num*3779)
    mask=np.zeros((64,64),np.uint8)
    ports=[('t',14),('t',49),('b',14),('b',49),
           ('l',19),('l',44),('r',19),('r',44)]
    for i,(side,c) in enumerate(ports):
        depth=int(rng.integers(12,24));shift=int(rng.integers(-12,13))
        lateral=max(7,min(56,c+shift));bend=float(rng.uniform(-4.5,4.5))
        if side=='t':a=(c,2);b=(lateral,depth)
        elif side=='b':a=(c,61);b=(lateral,63-depth)
        elif side=='l':a=(2,c);b=(depth,lateral)
        else:a=(61,c);b=(63-depth,lateral)
        curve(mask,a,b,bend,7.0,float(rng.uniform(5.2,6.8)))
    # Short interior, predominantly oblique veins. Fixed loop count.
    for j in range(2+(num%2)):
        x,y=rng.uniform(16,48,size=2);angle=rng.uniform(0,math.tau)
        length=float(rng.uniform(11,22));dx=math.cos(angle)*length/2;dy=math.sin(angle)*length/2
        curve(mask,(x-dx,y-dy),(x+dx,y+dy),float(rng.uniform(-4,4)),6.0,5.5)
    mask=cv2.morphologyEx(mask,cv2.MORPH_CLOSE,cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(3,3)))
    # No variant-specific pixels in the shared 4px strip.
    mask[:BAND,:]=common[:BAND,:];mask[-BAND:,:]=common[-BAND:,:]
    mask[:,:BAND]=common[:,:BAND];mask[:,-BAND:]=common[:,-BAND:]
    d=cv2.distanceTransform((mask>0).astype(np.uint8),cv2.DIST_L2,3)
    noise=cv2.resize(rng.random((10,10),dtype=np.float32),(64,64),interpolation=cv2.INTER_CUBIC)
    # Interior quantiles use every flesh tone; dark tones outline the bands.
    valid=(mask>0)&(d>=2.5)
    values=noise[valid]
    thresholds=np.quantile(values,[.17,.42,.68,.90]) if len(values) else [0.2,0.4,0.6,0.8]
    levels=np.digitize(noise,thresholds).astype(np.int16)+2
    levels=np.where(d<1.2,0,np.where(d<2.5,1,levels))
    rgba=np.zeros((64,64,4),np.uint8);rgba[:,:,:3]=PAL[np.clip(levels,0,6)];rgba[:,:,3]=mask
    rgba[mask==0]=(0,0,0,0)
    border=np.zeros((64,64),bool);border[:BAND,:]=border[-BAND:,:]=True;border[:,:BAND]=border[:,-BAND:]=True
    rgba[border&(mask>0)]=(157,80,94,255);rgba[border&(mask==0)]=(0,0,0,0)
    return Image.fromarray(rgba,'RGBA')


def mix(n,seed):
    ids=[]
    for y in range(n):
        row=[]
        for x in range(n):
            v=((y*16+x)*0x1F1F1F1F+3*0x9E3779B9+seed*0x85EBCA6B)&0xffffffff
            v=((v^(v>>15))*0x2545F491)&0xffffffff;v=((v^(v>>13))*0x27D4EB2F)&0xffffffff
            row.append(int(((v^(v>>16))&0xffffffff)/4294967295.*4)%4)
        ids.append(row)
    return ids


def wall(images,n,seed,pixels):
    out=Image.new('RGBA',(n*pixels,n*pixels),(69,58,59,255));ids=mix(n,seed)
    for y in range(n):
        for x in range(n):
            out.alpha_composite(images[ids[y][x]].resize((pixels,pixels),Image.Resampling.NEAREST),(x*pixels,y*pixels))
    return out.convert('RGB')


def preview(images,path):
    page=Image.new('RGB',(1500,1030),(26,23,25));draw=ImageDraw.Draw(page)
    try:font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',15)
    except OSError:font=ImageFont.load_default()
    draw.text((20,8),'Procedural variants: 64px plus 16px BOX',font=font,fill='white')
    for i,im in enumerate(images):
        x=20+i*365;draw.text((x,33),'variant '+str(i),font=font,fill='white')
        pic=im.resize((192,192),Image.Resampling.NEAREST);page.paste(pic,(x,60),pic)
        pic=im.resize((16,16),Image.Resampling.BOX).resize((96,96),Image.Resampling.NEAREST);page.paste(pic,(x+212,60),pic)
    draw.text((20,294),'3x3 seed 980',font=font,fill='white');draw.text((410,294),'5x5 seed 982',font=font,fill='white')
    draw.text((1010,294),'5x5 at 16px per tile',font=font,fill='white')
    page.paste(wall(images,3,980,96),(20,325));page.paste(wall(images,5,982,96),(410,325))
    page.paste(wall(images,5,982,16).resize((400,400),Image.Resampling.NEAREST),(1010,325))
    draw.text((20,920),'Flat diagnostic only; not a Minecraft game render, corner or end test.',font=font,fill='white')
    page.save(path)


def main():
    if len(sys.argv)!=3 or sys.argv[2] not in ('4','5','6','7','8'):
        raise SystemExit('usage: wave29_tendrils_procedural.py OUTPUT ATTEMPT(4..8)')
    out=Path(sys.argv[1]);out.mkdir(parents=True,exist_ok=True);attempt=int(sys.argv[2])
    print('Generating procedural attempt',attempt,'of 8',flush=True)
    common=common_edge();images=[]
    for i in range(4):
        im=build(common,attempt,i);im.save(out/f'creeping_tendrils_{i}.png',optimize=True);images.append(im)
    preview(images,out/'preview.png');print('Generation complete:',out,flush=True)


if __name__=='__main__':main()
