import os,sys,base64,requests
from io import BytesIO
from datetime import datetime
from dotenv import load_dotenv
from PIL import Image
from prompts import ALL_CATEGORIES

load_dotenv()
GEMINI_KEY=os.environ.get("GEMINI_API_KEY")
OPENAI_KEY=os.environ.get("OPENAI_API_KEY")
PRIMARY_API="gemini"
OUTPUT_DIR="capcut_assets"
LOG_FILE=os.path.join(OUTPUT_DIR,"_run_log.txt")
ASPECT_MAP={(1024,576):"16:9",(576,1024):"9:16",(1024,1024):"1:1"}

def gemini_generate(prompt,neg,w,h,n):
    url=f"https://generativelanguage.googleapis.com/v1beta/models/imagen-4.0-generate-001:predict?key={GEMINI_KEY}"
    r=requests.post(url,json={"instances":[{"prompt":prompt}],"parameters":{"sampleCount":n,"aspectRatio":ASPECT_MAP.get((w,h),"16:9"),"negativePrompt":neg}},timeout=120)
    if r.status_code!=200: raise RuntimeError(f"Gemini {r.status_code}: {r.text[:300]}")
    return [p["bytesBase64Encoded"] for p in r.json().get("predictions",[])]

def openai_generate(prompt,neg,w,h,n):
    full=prompt+(f". Avoid: {neg}" if neg else "")
    r=requests.post(
        "https://api.openai.com/v1/images/generations",
        headers={"Authorization":f"Bearer {OPENAI_KEY}"},
        json={"model":"gpt-image-1","prompt":full,"n":n,"size":"1024x1024"},
        timeout=120)
    if r.status_code!=200: raise RuntimeError(f"OpenAI {r.status_code}: {r.text[:300]}")
    result=[]
    for i in r.json().get("data",[]):
        if "b64_json" in i:
            result.append(i["b64_json"])
        else:
            result.append(base64.b64encode(requests.get(i["url"]).content).decode())
    return result

def generate(prompt,neg,w,h,n,api):
    if api=="gemini":
        if not GEMINI_KEY: raise RuntimeError("GEMINI_API_KEY not in .env")
        return gemini_generate(prompt,neg,w,h,n)
    if not OPENAI_KEY: raise RuntimeError("OPENAI_API_KEY not in .env")
    return openai_generate(prompt,neg,w,h,n)

def remove_bg(img_bytes):
    try:
        from rembg import remove
        out=remove(Image.open(BytesIO(img_bytes)).convert("RGB"))
        buf=BytesIO(); out.save(buf,"PNG"); return buf.getvalue()
    except ImportError:
        print("\n  [WARN] rembg not installed"); return img_bytes

def save(b64,folder,prefix,do_rembg=False):
    data=base64.b64decode(b64)
    if do_rembg: data=remove_bg(data)
    ts=datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:-3]
    path=os.path.join(folder,f"{prefix}_{ts}.png")
    with open(path,"wb") as f: f.write(data)
    return path

def run_category(name,cfg,api):
    folder=os.path.join(OUTPUT_DIR,name)
    os.makedirs(folder,exist_ok=True)
    w,h=cfg["dimensions"]
    is_lt=(name=="lower_thirds")
    saved=[]
    print(f"\n{'='*40}")
    print(f"  {name.upper()}  |  {api.upper()}  |  {w}x{h}")
    print(f"{'='*40}")
    if is_lt: print("  [AUTO] Background removal ON")
    for i,prompt in enumerate(cfg["prompts"],1):
        print(f"\n  Prompt {i}/{len(cfg['prompts'])}: {prompt[:60]}...")
        print(f"  Generating {cfg['variations']} image(s)...",end=" ",flush=True)
        try:
            for b64 in generate(prompt,cfg["negative"],w,h,cfg["variations"],api):
                p=save(b64,folder,f"p{i:02d}",do_rembg=is_lt)
                saved.append(p)
                print("OK",end=" ",flush=True)
        except RuntimeError as e:
            print(f"\n  [ERROR] {e}")
    print(f"\n  Saved {len(saved)} images")
    return saved

def main():
    args=sys.argv[1:]
    api=PRIMARY_API
    if "--api" in args:
        idx=args.index("--api")
        api=args[idx+1]
        args=[a for i,a in enumerate(args) if i not in (idx,idx+1)]
    cats={k:v for k,v in ALL_CATEGORIES.items() if k in args} if args else ALL_CATEGORIES
    if not cats: print("No valid categories."); sys.exit(1)
    print(f"\n  CapCut Pipeline | {api.upper()} | {list(cats.keys())}")
    summary={}
    for name,cfg in cats.items():
        summary[name]=run_category(name,cfg,api)
    done=sum(len(v) for v in summary.values())
    print(f"\n  DONE — {done} images in ./{OUTPUT_DIR}/\n")
    os.makedirs(OUTPUT_DIR,exist_ok=True)
    with open(LOG_FILE,"a") as f:
        f.write(f"Run: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | {api} | {done} images\n")

if __name__=="__main__":
    main()