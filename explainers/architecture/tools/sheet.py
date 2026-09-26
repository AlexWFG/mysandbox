import sys,glob
from PIL import Image
fs=sorted(glob.glob('out/stills/t_*.jpg')) if len(sys.argv)<3 else sys.argv[2:]
cols=3; w,h=640,360
rows=(len(fs)+cols-1)//cols
sh=Image.new('RGB',(cols*w,rows*h))
for i,f in enumerate(fs):
    im=Image.open(f).resize((w,h),Image.LANCZOS); sh.paste(im,((i%cols)*w,(i//cols)*h))
sh.save(sys.argv[1] if len(sys.argv)>1 else 'out/sheet.jpg',quality=90)
