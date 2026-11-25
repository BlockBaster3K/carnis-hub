#!/usr/bin/env python3
"""Procedural 64px A3/A6 trial; shared reflected quadrant, no external image.

Usage: timeout 120 python3 -W ignore wave29_tendrils_procedural.py OUTPUT_DIR ATTEMPT
ATTEMPT is 1..4. Only a separately checked and visually accepted trial is a delivery.
"""
from pathlib import Path
import sys
import math
import numpy as np
import cv2
from PIL import Image, ImageDraw, ImageFont

SIZE = 64
PALETTE = np.array([[84,40,54], [104,47,64], [157,80,94], [161,90,96],
                    [179,106,105], [196,126,119], [209,144,130]], dtype=np.uint8)
EDGE = np.array([104,47,64,255], dtype=np.uint8)
CLEAR = np.array([0,0,0,0], dtype=np.uint8)


def common_mask():
    """One common 32x32 quadrant, reflected in X and Y."""
    q = np.zeros((32,32), dtype=np.uint8)
    for c in (8,22):
        cv2.ellipse(q,(c,0),(4,12),0,0,360,255,-1)
        cv2.ellipse(q,(0,c),(12,4),0,0,360,255,-1)
    return np.block([[q,np.fliplr(q)],[np.flipud(q),np.flipud(np.fliplr(q))]])


def stroke(detail, rng):
    """One short curved fleshy stroke, not extending more than half a tile."""
    x,y = rng.uniform(13,51,size=2)
    angle = rng.uniform(0,2*math.pi)
    length = rng.uniform(10,21)
    bend = rng.uniform(-3,3)
    r = int(rng.integers(5,7))
    dx,dy = math.cos(angle),math.sin(angle)
    points=[]
    for part in range(5):
        u=part/4.0
        side=bend*math.sin(math.pi*u)
        points.append((int(round(x+(u-.5)*length*dx-side*dy)),
                       int(round(y+(u-.5)*length*dy+side*dx))))
    for p,q in zip(points[:-1],points[1:]):
        cv2.line(detail,p,q,255,r*2,lineType=cv2.LINE_8)
    for p in (points[0],points[-1]):
        cv2.circle(detail,p,r,255,-1,lineType=cv2.LINE_8)


def variant(common, attempt, number):
    rng=np.random.default_rng(280029+1009*attempt+541*number)
    detail=np.zeros((SIZE,SIZE),np.uint8)
    for index in range((5,6,5,6)[number]):
        stroke(detail,rng)
    detail[0,:]=detail[-1,:]=0
    detail[:,0]=detail[:,-1]=0
    mask=np.maximum(common,detail)
    # A fixed, bounded one-pass closing rounds accidental 1–3px gaps between
    # fleshy fragments. Different strengths are tried in attempts 2, 3 and 4.
    kernel_size={1:3,2:5,3:7,4:9}[attempt]
    kernel=cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(kernel_size,kernel_size))
    mask=cv2.morphologyEx(mask,cv2.MORPH_CLOSE,kernel,iterations=1)
    # The variable layer cannot change the edge. All four edge pixel arrays
    # are exactly the ones created once by mirroring the common quadrant.
    mask[0,:]=common[0,:];mask[-1,:]=common[-1,:]
    mask[:,0]=common[:,0];mask[:,-1]=common[:,-1]
    distance=cv2.distanceTransform((mask>0).astype(np.uint8),cv2.DIST_L2,3)
    noise=cv2.resize(rng.random((8,8),dtype=np.float32),(64,64),interpolation=cv2.INTER_CUBIC)
    band=np.rint(np.clip((noise-.5)*3.3+3.0,0,6)).astype(np.int16)
    band=np.where(distance<1.3,0,np.where(distance<2.6,np.minimum(band,1),band))
    rgba=np.zeros((64,64,4),np.uint8)
    rgba[:,:,:3]=PALETTE[np.clip(band,0,6)]
    rgba[:,:,3]=mask
    rgba[mask==0]=CLEAR
    for side in ((0,slice(None)),(-1,slice(None)),(slice(None),0),(slice(None),-1)):
        rgba[side]=np.where((common[side]>0)[...,None],EDGE,CLEAR)
    return Image.fromarray(rgba,'RGBA')


def pattern(n,seed):
    rows=[]
    for y in range(n):
        row=[]
        for x in range(n):
            a,b=y*16+x,3
            v=(a*0x1F1F1F1F+b*0x9E3779B9+seed*0x85EBCA6B)&0xFFFFFFFF
            v=((v^(v>>15))*0x2545F491)&0xFFFFFFFF
            v=((v^(v>>13))*0x27D4EB2F)&0xFFFFFFFF
            h=((v^(v>>16))&0xFFFFFFFF)/4294967295.0
            row.append(int(h*4)%4)
        rows.append(row)
    return rows


def wall(images,n,seed,tile_size):
    canvas=Image.new('RGBA',(n*tile_size,n*tile_size),(69,58,59,255))
    ids=pattern(n,seed)
    for y in range(n):
        for x in range(n):
            tile=images[ids[y][x]].resize((tile_size,tile_size),Image.Resampling.NEAREST)
            canvas.alpha_composite(tile,(x*tile_size,y*tile_size))
    return canvas.convert('RGB')


def preview(images,path):
    sheet=Image.new('RGB',(1500,1030),(26,23,25));d=ImageDraw.Draw(sheet)
    try:font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',15)
    except OSError:font=ImageFont.load_default()
    d.text((20,8),'Procedural trial: 64px variants and 16px reduction',font=font,fill='white')
    for i,im in enumerate(images):
        x=20+365*i;d.text((x,33),'variant '+str(i),font=font,fill='white')
        p=im.resize((192,192),Image.Resampling.NEAREST);sheet.paste(p,(x,60),p)
        p=im.resize((16,16),Image.Resampling.BOX).resize((96,96),Image.Resampling.NEAREST)
        sheet.paste(p,(x+212,60),p)
    d.text((20,294),'3 x 3, seed 980',font=font,fill='white')
    d.text((410,294),'5 x 5, seed 982',font=font,fill='white')
    d.text((1010,294),'5 x 5, 16px per tile',font=font,fill='white')
    sheet.paste(wall(images,3,980,96),(20,325));sheet.paste(wall(images,5,982,96),(410,325))
    sheet.paste(wall(images,5,982,16).resize((400,400),Image.Resampling.NEAREST),(1010,325))
    d.text((20,920),'Flat preview only; not a Minecraft render or an end/corner test.',font=font,fill='white')
    sheet.save(path)


def main():
    if len(sys.argv)!=3 or sys.argv[2] not in ('1','2','3','4'):
        raise SystemExit('usage: wave29_tendrils_procedural.py OUTPUT_DIR ATTEMPT(1..4)')
    out=Path(sys.argv[1]);attempt=int(sys.argv[2]);out.mkdir(parents=True,exist_ok=True)
    print('Generating attempt',attempt,'of 4; 4 variants',flush=True)
    shared=common_mask();images=[]
    for i in range(4):
        im=variant(shared,attempt,i);im.save(out/f'creeping_tendrils_{i}.png',optimize=True);images.append(im)
    preview(images,out/'preview.png')
    print('Generation complete:',out,flush=True)


if __name__=='__main__':
    main()
