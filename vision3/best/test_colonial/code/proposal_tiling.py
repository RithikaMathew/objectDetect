"""Full-frame plus overlapping tiles for independent detector audits."""
import numpy as np


def origins(length, size, overlap):
    if size <= 0 or not 0 <= overlap < 1: raise ValueError('invalid tile size/overlap')
    if length <= size: return [0]
    step = max(1, round(size*(1-overlap)))
    return sorted(set([*range(0,length-size+1,step),length-size]))


def tiled_proposals(image, infer, size=320, overlap=.25, iou_threshold=.5):
    """Return class-aware NMS union; PIL crops mapped back to source pixels."""
    width,height=image.size
    results=[(0,0,infer(image))]
    if width > size or height > size:
        for y in origins(height,size,overlap):
            for x in origins(width,size,overlap):
                crop=image.crop((x,y,min(x+size,width),min(y+size,height)))
                results.append((x,y,infer(crop)))
    boxes=[];scores=[];labels=[]
    for x,y,r in results:
        for box,score,label in zip(r['boxes'],r['scores'],r['text_labels']):
            b=np.asarray(box,dtype=float).copy()+[x,y,x,y]
            b[[0,2]]=np.clip(b[[0,2]],0,width);b[[1,3]]=np.clip(b[[1,3]],0,height)
            if b[2]<=b[0] or b[3]<=b[1]:continue
            boxes.append(b);scores.append(float(score));labels.append(label)
    boxes=np.asarray(boxes,dtype=float).reshape(-1,4);scores=np.asarray(scores)
    keep=[]
    for i in np.argsort(-scores,kind='stable'):
        duplicate=False
        for j in keep:
            if labels[i]!=labels[j]:continue
            lo=np.maximum(boxes[i,:2],boxes[j,:2]);hi=np.minimum(boxes[i,2:],boxes[j,2:])
            inter=np.maximum(0,hi-lo).prod()
            union=np.prod(boxes[i,2:]-boxes[i,:2])+np.prod(boxes[j,2:]-boxes[j,:2])-inter
            if union>0 and inter/union>iou_threshold:duplicate=True;break
        if not duplicate:keep.append(i)
    return dict(boxes=boxes[keep],scores=scores[keep],text_labels=[labels[i] for i in keep])
