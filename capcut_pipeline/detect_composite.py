import os,sys,base64,requests,time,io
from datetime import datetime
from dotenv import load_dotenv
from PIL import Image,ImageChops,ImageEnhance,ImageFilter

load_dotenv()
GEMINI_KEY=os.environ.get("GEMINI_API_KEY")
OPENAI_KEY=os.environ.get("OPENAI_API_KEY")
IMAGES={".jpg",".jpeg",".png",".webp",".bmp",".tiff"}
MAX_RETRIES=3
RETRY_DELAY=5
ELA_QUALITY=95
ELA_AMPLIFY=20
ELA_THRESHOLD=25
GEMINI_MODEL="gemini-2.5-flash"

GEMINI_PROMPT=("You are a digital forensics expert. Given TWO images: "
"(1) original, (2) ELA heatmap where bright=different compression=possible manipulation. "
"Analyse across 9 components: 1.LIGHTING DIRECTION 2.SHADOW COHERENCE 3.EDGE BOUNDARIES "
"4.TEXTURE FORENSICS 5.REFLECTION CONSISTENCY 6.NOISE PATTERN "
"7.DEPTH OF FIELD 8.COLOR TEMPERATURE 9.ELA ANALYSIS. "
"Respond EXACTLY: VERDICT: Real OR Composite OR Fully AI-Generated | "
"CONFIDENCE: 0-100% | MANIPULATION TYPE: face swap/object insertion/background replacement/inpainting/none/unknown | "
"SUSPICIOUS REGIONS: describe or none detected | "
"COMPONENT SCORES: Lighting Pass/Fail reason, Shadows Pass/Fail reason, "
"Edges Pass/Fail reason, Texture Pass/Fail reason, Reflections Pass/Fail reason, "
"Noise Pass/Fail reason, Depth of field Pass/Fail reason, "
"Color temperature Pass/Fail reason, ELA Pass/Fail reason | "
"SUMMARY: 2-3 sentence conclusion. You MUST give a definitive verdict.")

GPT4O_PROMPT=("Examine this image. Determine if it is a real photograph, "
"a composite with manipulated elements, or fully AI-generated. "
"Look for lighting inconsistencies, edge artifacts, texture mismatches, "
"unnatural blending, uneven noise, impossible shadows. "
"Respond EXACTLY: VERDICT: Real OR Composite OR Fully AI-Generated | "
"CONFIDENCE: 0-100% | "
"MANIPULATION TYPE: face swap/object insertion/background replacement/inpainting/none/unknown | "
"SUSPICIOUS REGIONS: describe or none detected | "
"KEY INDICATORS: list 3 observations. You MUST commit to a verdict.")

def run_ela(image_path,save_heatmap=False):
    original=Image.open(image_path).convert("RGB")
    buf=io.BytesIO()
    original.save(buf,format="JPEG",quality=ELA_QUALITY)
    buf.seek(0)
    resaved=Image.open(buf).convert("RGB")
    diff=ImageChops.difference(original,resaved)
    amplified=diff.point(lambda p:min(p*ELA_AMPLIFY,255))
    amplified=ImageEnhance.Contrast(amplified).enhance(2.0)
    amplified=amplified.filter(ImageFilter.GaussianBlur(radius=1))
    heatmap_path=None
    if save_heatmap:
        heatmap_path=image_path.rsplit(".",1)[0]+"_ela.png"
        amplified.save(heatmap_path)
    pixels=list(amplified.convert("L").getdata())
    ela_score=sum(pixels)/len(pixels)
    ela_max=max(pixels)
    return amplified,ela_score,ela_max,heatmap_path

def encode_pil(pil_img,max_px=1024):
    if pil_img.width>max_px or pil_img.height>max_px:
        pil_img=pil_img.copy()
        pil_img.thumbnail((max_px,max_px),Image.LANCZOS)
    buf=io.BytesIO()
    pil_img.convert("RGB").save(buf,format="JPEG",quality=85)
    return base64.b64encode(buf.getvalue()).decode()

def encode_file(path,max_px=1024):
    return encode_pil(Image.open(path),max_px=max_px)

def analyse_gemini(image_path,ela_image):
    if not GEMINI_KEY: raise RuntimeError("GEMINI_API_KEY not in .env")
    orig_b64=encode_file(image_path)
    ela_b64=encode_pil(ela_image)
    url=f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_MODEL}:generateContent?key={GEMINI_KEY}"
    payload={"contents":[{"parts":[{"inline_data":{"mime_type":"image/jpeg","data":orig_b64}},{"inline_data":{"mime_type":"image/jpeg","data":ela_b64}},{"text":GEMINI_PROMPT}]}],"generationConfig":{"maxOutputTokens":1024}}
    for attempt in range(1,MAX_RETRIES+1):
        try:
            r=requests.post(url,json=payload,timeout=60)
            if r.status_code==200: return r.json()["candidates"][0]["content"]["parts"][0]["text"]
            if r.status_code==429: time.sleep(int(r.headers.get("Retry-After",20)));continue
            raise RuntimeError(f"Gemini {r.status_code}: {r.text[:200]}")
        except requests.exceptions.Timeout:
            if attempt<MAX_RETRIES: time.sleep(RETRY_DELAY);continue
            raise RuntimeError("Gemini timed out")
        except requests.exceptions.ConnectionError:
            if attempt<MAX_RETRIES: time.sleep(RETRY_DELAY);continue
            raise RuntimeError("Gemini connection failed")
    raise RuntimeError("Gemini: all attempts failed")

def analyse_gpt4o(image_path):
    if not OPENAI_KEY: raise RuntimeError("OPENAI_API_KEY not in .env")
    b64=encode_file(image_path)
    for attempt in range(1,MAX_RETRIES+1):
        try:
            r=requests.post("https://api.openai.com/v1/chat/completions",headers={"Authorization":f"Bearer {OPENAI_KEY}"},json={"model":"gpt-4o","messages":[{"role":"user","content":[{"type":"image_url","image_url":{"url":f"data:image/jpeg;base64,{b64}"}},{"type":"text","text":GPT4O_PROMPT}]}],"max_tokens":600},timeout=60)
            if r.status_code==200: return r.json()["choices"][0]["message"]["content"]
            if r.status_code==429: time.sleep(int(r.headers.get("Retry-After",20)));continue
            raise RuntimeError(f"GPT-4o {r.status_code}: {r.text[:200]}")
        except requests.exceptions.Timeout:
            if attempt<MAX_RETRIES: time.sleep(RETRY_DELAY);continue
            raise RuntimeError("GPT-4o timed out")
        except requests.exceptions.ConnectionError:
            if attempt<MAX_RETRIES: time.sleep(RETRY_DELAY);continue
            raise RuntimeError("GPT-4o connection failed")
    raise RuntimeError("GPT-4o: all attempts failed")

def parse_result(text):
    verdict,confidence,manip_type="?",0,"unknown"
    # Handle both newline and pipe-separated formats
    parts = []
    for line in text.splitlines():
        parts.extend(line.split(" | "))
    for part in parts:
        s=part.strip()
        su=s.upper()
        if su.startswith("VERDICT"):
            val=s.split(":",1)[-1].strip().lower()
            if any(x in val for x in ["composite","deepfake","manipulat"]): verdict="COMPOSITE"
            elif any(x in val for x in ["ai-generated","ai generated","fully ai","synthetic"]): verdict="AI"
            elif any(x in val for x in ["real","authentic","genuine"]): verdict="REAL"
        elif su.startswith("CONFIDENCE"):
            try: confidence=int("".join(c for c in s.split(":",1)[-1] if c.isdigit())[:3])
            except: pass
        elif su.startswith("MANIPULATION TYPE"):
            manip_type=s.split(":",1)[-1].strip()
    return verdict,confidence,manip_type

def combine_verdicts(g_v,p_v,ela_score):
    if g_v==p_v: return g_v,"HIGH - both engines agree"
    ela_flag=ela_score>ELA_THRESHOLD
    if "COMPOSITE" in (g_v,p_v): return "COMPOSITE","MEDIUM - one engine + "+("elevated ELA" if ela_flag else "low ELA")
    if "AI" in (g_v,p_v): return "AI","MEDIUM - one engine flagged"
    return "REAL","LOW - engines disagree, defaulting Real"

def analyse_file(path,save_ela=False):
    fname=os.path.basename(path)
    size_kb=os.path.getsize(path)//1024
    print(f"\n  File : {fname}  ({size_kb} KB)")
    print("  [1/3] ELA...",end=" ",flush=True)
    ela_img,ela_score,ela_max=None,0,0
    try:
        ela_img,ela_score,ela_max,hmap=run_ela(path,save_heatmap=save_ela)
        flag="ELEVATED" if ela_score>ELA_THRESHOLD else "normal"
        print(f"score={ela_score:.1f}  max={ela_max}  [{flag}]")
        if hmap: print(f"         Heatmap: {hmap}")
    except Exception as e: print(f"FAILED: {e}")
    print("  [2/3] Gemini 1.5 Flash...",end=" ",flush=True)
    gemini_text,gemini_v,gemini_conf,gemini_manip="","?",0,"unknown"
    try:
        ela_to_send=ela_img if ela_img else Image.open(path)
        gemini_text=analyse_gemini(path,ela_to_send)
        gemini_v,gemini_conf,gemini_manip=parse_result(gemini_text)
        icon="🔀" if gemini_v=="COMPOSITE" else "🤖" if gemini_v=="AI" else "📷" if gemini_v=="REAL" else "?"
        print(f"{icon} {gemini_v} ({gemini_conf}%)")
    except RuntimeError as e: print(f"SKIP: {e}")
    print("  [3/3] GPT-4o...",end=" ",flush=True)
    gpt_text,gpt_v,gpt_conf,gpt_manip="","?",0,"unknown"
    try:
        gpt_text=analyse_gpt4o(path)
        gpt_v,gpt_conf,gpt_manip=parse_result(gpt_text)
        icon="🔀" if gpt_v=="COMPOSITE" else "🤖" if gpt_v=="AI" else "📷" if gpt_v=="REAL" else "?"
        print(f"{icon} {gpt_v} ({gpt_conf}%)")
    except RuntimeError as e: print(f"SKIP: {e}")
    final_v,conf_note=combine_verdicts(gemini_v,gpt_v,ela_score)
    manip=gemini_manip if gemini_manip!="unknown" else gpt_manip
    print("\n  " + "="*52)
    icon="🔀 COMPOSITE" if final_v=="COMPOSITE" else "🤖 FULLY AI" if final_v=="AI" else "📷 REAL" if final_v=="REAL" else "? UNKNOWN"
    print(f"  FINAL VERDICT : {icon}")
    print(f"  Confidence    : {conf_note}")
    print(f"  Manipulation  : {manip}")
    ela_note="elevated" if ela_score>ELA_THRESHOLD else "normal"
    print(f"  ELA score     : {ela_score:.1f} ({ela_note})")
    if gemini_text:
        print("\n  -- Gemini --")
        for line in gemini_text.strip().splitlines(): print(f"  {line}")
    if gpt_text:
        print("\n  -- GPT-4o --")
        for line in gpt_text.strip().splitlines(): print(f"  {line}")
    print("  " + "="*52)
    return {"file":fname,"final":final_v,"confidence_note":conf_note,"manipulation":manip,"ela_score":round(ela_score,1),"gemini":gemini_v,"gpt4o":gpt_v,"gemini_text":gemini_text,"gpt_text":gpt_text,"error":None}

def run_folder(folder,save_ela=False):
    files=sorted([os.path.join(folder,f) for f in os.listdir(folder) if os.path.splitext(f)[1].lower() in IMAGES])
    if not files: print(f"\n  No images in: {folder}\n");sys.exit(1)
    print("\n  " + "="*55)
    print("  Composite and Deepfake Detector")
    print(f"  Folder: {folder} | Files: {len(files)}")
    print(f"  Started: {datetime.now().strftime('%H:%M:%S')}")
    print("  " + "="*55)
    results=[]
    try:
        for i,path in enumerate(files,1):
            print(f"\n  [{i}/{len(files)}]",end="")
            results.append(analyse_file(path,save_ela=save_ela))
    except KeyboardInterrupt: print("\n\n  [STOPPED]")
    finally:
        if results: save_log(results,folder);print_summary(results)

def print_summary(results):
    real=sum(1 for r in results if r["final"]=="REAL")
    comp=sum(1 for r in results if r["final"]=="COMPOSITE")
    ai=sum(1 for r in results if r["final"]=="AI")
    unk=sum(1 for r in results if r["final"]=="?")
    print("\n  " + "="*55)
    print(f"  {'File':<30} {'ELA':>5} {'Gemini':<10} {'GPT4o':<10} Final")
    print("  " + "-"*55)
    for r in results:
        icon="🔀" if r["final"]=="COMPOSITE" else "🤖" if r["final"]=="AI" else "📷" if r["final"]=="REAL" else "?"
        print(f"  {r['file'][:30]:<30} {r['ela_score']:>5} {r['gemini']:<10} {r['gpt4o']:<10} {icon}")
    print("  " + "-"*55)
    print(f"  Real:{real}  Composite:{comp}  AI:{ai}  Unknown:{unk}")
    print("  " + "="*55 + "\n")

def save_log(results,folder):
    log=os.path.join(folder,"_composite_log.txt")
    with open(log,"w",encoding="utf-8") as f:
        f.write(f"Composite Detection\nRun: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        for r in results:
            f.write(f"FILE: {r['file']}\nFINAL: {r['final']}\nELA: {r['ela_score']}\n")
            f.write(f"GEMINI:\n{r.get('gemini_text','')}\nGPT4O:\n{r.get('gpt_text','')}\n---\n")
    print(f"  Log -> {log}\n")

if __name__=="__main__":
    args=[a for a in sys.argv[1:] if not a.startswith("--")]
    save_ela="--save-ela" in sys.argv
    if not args:
        print("\n  USAGE:\n    py detect_composite.py image.jpg\n    py detect_composite.py folder/\n    py detect_composite.py image.jpg --save-ela")
        sys.exit(1)
    target=args[0]
    if not os.path.exists(target): print(f"\n  [ERROR] Not found: {target}\n");sys.exit(1)
    if os.path.isdir(target): run_folder(target,save_ela=save_ela)
    else:
        ext=os.path.splitext(target)[1].lower()
        if ext not in IMAGES: print(f"\n  [ERROR] Unsupported: {ext}\n");sys.exit(1)
        analyse_file(target,save_ela=save_ela)
