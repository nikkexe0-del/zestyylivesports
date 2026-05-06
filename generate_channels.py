import os
import re
import requests
import json
import shutil

# Configuration
M3U_URL = "https://raw.githubusercontent.com/rkdyiptv/Playlist/refs/heads/main/Playlist/Cricket.m3u/index.html"
OUTPUT_DIR = "Channel"

# Ensure output directory exists and is empty
if os.path.exists(OUTPUT_DIR):
    shutil.rmtree(OUTPUT_DIR)
os.makedirs(OUTPUT_DIR)

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{CHANNEL_TITLE} | ZestyyMedia</title>
<meta name="referrer" content="no-referrer">
<script src="https://cdn.jsdelivr.net/npm/shaka-player@4.16.2/dist/shaka-player.ui.min.js"></script>
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/shaka-player@4.16.2/dist/controls.css"/>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap" rel="stylesheet">
<style>
:root{
  --primary:#ff3c3c;
  --border:rgba(255,255,255,0.08);
  --footer-h:72px;
}
*{margin:0;padding:0;box-sizing:border-box}
html,body{width:100%;height:100%;background:#000;overflow:hidden;font-family:'Inter',sans-serif}

/* kill shaka spinner dot */
.shaka-spinner-container,.shaka-spinner{display:none!important}

.shaka-video-container{
  position:fixed;
  inset:0 0 var(--footer-h) 0;
  background:#000;
  display:flex;align-items:center;justify-content:center;
}
video{width:100%;height:100%;object-fit:contain;background:#000;}

/* watermark */
.zesty-watermark{
  position:absolute;
  top:50%;right:5%;
  transform:translateY(-50%);
  z-index:40;pointer-events:none;
  font-size:11px;font-weight:700;letter-spacing:3px;
  color:rgba(255,255,255,0.12);text-transform:uppercase;
  writing-mode:vertical-rl;text-orientation:mixed;
}

/* block overlay */
.block-overlay{
  position:fixed;inset:0;z-index:99999;
  display:flex;align-items:center;justify-content:center;
  background:radial-gradient(circle at center,#111 0%,#000 100%);
  text-align:center;
}
.block-box{
  padding:40px;max-width:480px;width:90%;
  background:#0d0d0d;border-radius:16px;
  border:1px solid var(--border);
  box-shadow:0 24px 60px rgba(0,0,0,0.6);
  animation:fadeInUp 0.6s ease-out;
}
@keyframes fadeInUp{from{opacity:0;transform:translateY(30px)}to{opacity:1;transform:translateY(0)}}
.block-title{font-size:28px;font-weight:800;color:#fff;text-transform:uppercase;letter-spacing:-0.5px;margin-bottom:12px;text-shadow:0 0 10px rgba(255,0,0,0.3);}
.block-sub{font-size:13px;font-weight:500;color:rgba(255,255,255,0.5);line-height:1.7;}
.block-icon,.block-note{display:none}

/* footer */
.zesty-footer{
  position:fixed;bottom:0;left:0;right:0;
  height:var(--footer-h);
  background:#0a0a0a;border-top:1px solid var(--border);
  display:flex;align-items:center;padding:0 18px;gap:10px;z-index:200;
}
.footer-brand{display:flex;align-items:center;gap:8px;margin-right:4px;flex-shrink:0;}
.footer-brand-name{font-size:12px;font-weight:700;color:#fff;letter-spacing:0.5px;}
.footer-brand-dot{width:4px;height:4px;border-radius:2px;background:var(--primary);flex-shrink:0;}
.footer-divider{width:1px;height:32px;background:var(--border);flex-shrink:0;}
.footer-bento{display:flex;align-items:center;gap:8px;flex:1;}
.footer-pill{
  display:inline-flex;align-items:center;gap:6px;
  padding:0 13px;height:36px;border-radius:10px;
  border:1px solid var(--border);background:rgba(255,255,255,0.03);
  font-size:11px;font-weight:500;color:rgba(255,255,255,0.55);
  white-space:nowrap;flex-shrink:0;
}
.footer-pill .pill-label{font-weight:600;color:rgba(255,255,255,0.9);}
.footer-link{
  display:inline-flex;align-items:center;gap:6px;
  padding:0 13px;height:36px;border-radius:10px;
  border:1px solid var(--border);background:rgba(255,255,255,0.03);
  font-size:11px;font-weight:500;color:rgba(255,255,255,0.55);
  text-decoration:none;white-space:nowrap;flex-shrink:0;transition:all 0.2s;
}
.footer-link:hover{background:rgba(255,255,255,0.07);border-color:rgba(255,255,255,0.18);color:#fff;}
.footer-link .pill-label{font-weight:600;color:rgba(255,255,255,0.9);}
.footer-link svg{flex-shrink:0;opacity:0.6;}

@media(max-width:700px){
  :root{--footer-h:60px;}
  .footer-pill:nth-child(n+3){display:none;}
  .footer-brand-name{font-size:11px;}
  .block-title{font-size:22px}.block-box{padding:25px}.block-sub{font-size:12px}
}
</style>
</head>

<body>

<div class="shaka-video-container" id="player-container">
<video id="video" autoplay muted playsinline preload="metadata"></video>
<div class="zesty-watermark">ZESTYYMEDIA</div>
</div>

<script>
(function(){
  
  function isSandboxedEnv(){
    try {
      if (window.self === window.top) return false;
      if (window.frameElement && window.frameElement.hasAttribute("sandbox")) {
        return true;
      }
      try {
        document.domain = document.domain;
        if (window.frameElement && !window.frameElement.getAttribute("sandbox")) {
             return false;
        }
      } catch (e) {
         return true;
      }
      return false;
    } catch(e) {
      return true;
    }
  }
  function triggerBlockScreen(title, message){
    const container = document.getElementById("player-container");
    const video = document.getElementById("video");
    
    try {
      video.pause();
      video.removeAttribute('src');
      video.load();
    } catch(e){}

    const overlay = document.createElement("div");
    overlay.className = "block-overlay";
    overlay.id = "sandbox-block-display";
    overlay.innerHTML = `
      <div class="block-box">
        <div class="block-title">${title}</div>
        <div class="block-sub">${message}</div>
      </div>
    `;
    document.body.appendChild(overlay);
    container.style.display = 'none';
  }
  if(isSandboxedEnv()){

    triggerBlockScreen('Disable Sandbox', 'Opening Chrome Browser Only & Disable Ad blocker');
    return;
  }
  const CONFIG={
    streamUrl:"{STREAM_URL}",
    keyId:"{KEY_ID}",
    key:"{KEY}",
    cookie:"{COOKIE}",
    cookieUrl:"https://sayan10-sportlink-cookies.pages.dev/api/cookie.json"
  };

  document.addEventListener("DOMContentLoaded",async()=>{

    shaka.polyfill.installAll();
    if(!shaka.Player.isBrowserSupported()) return;

    const video=document.getElementById("video");
    const container=document.getElementById("player-container");

    video.muted=true;

    const player=new shaka.Player();
    await player.attach(video);

    const ui=new shaka.ui.Overlay(player,container,video);

    ui.configure({
  addBigPlayButton: true,
  controlPanelElements: [
    "mute",           // First - volume/mute button
    "play_pause",     // Second - play/pause button  
    "time_and_duration", // Third - timeline timings (00:00 / 00:00)
    "spacer",
    "quality",
    "picture_in_picture",
    "fullscreen"
  ],
  seekBarColors: {
    base: "white",
    buffered: "red", 
    played: "green"
  }
});

    const drmConfig = (CONFIG.keyId && CONFIG.key) ? {clearKeys:{[CONFIG.keyId]:CONFIG.key}} : {};
    player.configure({
      drm: drmConfig,
      manifest:{defaultPresentationDelay:5},
      streaming:{
        lowLatencyMode:true,
        bufferingGoal:10,
        rebufferingGoal:2,
        safeSeekOffset:5
      }
    });

    let cookieValue=CONFIG.cookie || "";

    if(!cookieValue){
        try{
          const response=await fetch(CONFIG.cookieUrl,{cache:"no-store"});
          const data=await response.json();
          cookieValue=data.cookie||"";
        }catch(e){}
    }

    if(cookieValue){
      player.getNetworkingEngine().registerRequestFilter((type,request)=>{
        request.headers["Referer"]="https://www.jiotv.com/";
        request.headers["User-Agent"]="plaYtv/7.1.5 (Linux;Android 13) ExoPlayerLib/2.11.6";
        request.headers["Cookie"]=cookieValue;

        let urlCookie=cookieValue.startsWith("__hdnea__=")?cookieValue.substring(10):cookieValue;

        if((type===shaka.net.NetworkingEngine.RequestType.MANIFEST||
        type===shaka.net.NetworkingEngine.RequestType.SEGMENT)&&
        !request.uris[0].includes("__hdnea__")){
          const sep=request.uris[0].includes("?")?"&":"?";
          request.uris[0]+=sep+"__hdnea__="+urlCookie;
        }
      });
    }

    try{
      await player.load(CONFIG.streamUrl);
      video.play().catch(()=>{});
    }catch(e){}

    video.addEventListener("play",()=>{
      video.muted=false;
    });

  });
})();
</script>
  <footer class="zesty-footer">
    <div class="footer-brand">
      <span class="footer-brand-name">ZestyyMedia</span>
      <div class="footer-brand-dot"></div>
    </div>
    <div class="footer-divider"></div>
    <div class="footer-bento">
      <div class="footer-pill">Dev <span class="pill-label">Nikshep Doggalli</span></div>
      <a href="https://instagram.com/nikkk.exe" target="_blank" class="footer-link">
        <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="2" y="2" width="20" height="20" rx="5" ry="5"/><circle cx="12" cy="12" r="4"/><circle cx="17.5" cy="6.5" r="1" fill="currentColor" stroke="none"/></svg>
        <span class="pill-label">nikkk.exe</span>
      </a>
      <a href="https://zestyyflix.vercel.app" target="_blank" class="footer-link">
        <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"/><polyline points="15 3 21 3 21 9"/><line x1="10" y1="14" x2="21" y2="3"/></svg>
        More from ZestyyTeam
      </a>
    </div>
  </footer>

</body>
</html>"""

def generate():
    print(f"Fetching playlist from {M3U_URL}...")
    try:
        response = requests.get(M3U_URL)
        response.raise_for_status()
        content = response.text
    except Exception as e:
        print(f"Failed to fetch playlist: {e}")
        return

    lines = content.splitlines()
    channels = []
    
    current_key_id = ""
    current_key = ""
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        # Match license key (KODIPROP format)
        if 'adaptive.license_key=' in line:
            parts = line.split('adaptive.license_key=')
            if len(parts) > 1:
                keys = parts[1].strip()
                if ':' in keys:
                    kparts = keys.split(':')
                    current_key_id = kparts[0]
                    current_key = kparts[1]
        
        # Match stream URL (JioTV MPD format)
        elif line.startswith("https://") and ".mpd" in line:
            # Extract URL and optional cookie
            parts = line.split('|cookie=')
            clean_url = parts[0].strip()
            cookie = parts[1].strip() if len(parts) > 1 else ""
            
            # Extract channel name from URL
            match = re.search(r'/bpk-tv/([^/]+)/', clean_url)
            if match:
                ch_name = match.group(1)
            else:
                ch_name = clean_url.split('/')[-2] if '/' in clean_url else "Channel"
            
            # Map logo
            # Strategy: Strip _BTS and check if a .png exists in logos/
            base_name = ch_name.replace('_BTS', '')
            logo_path = ""
            
            # Specific mappings for tricky names
            if ch_name == "Star_Sports_Select_HD_1_BTS":
                logo_path = "logos/Star_Sports_Select_1.png"
            
            if not logo_path:
                if os.path.exists(f"logos/{base_name}.png"):
                    logo_path = f"logos/{base_name}.png"
                elif os.path.exists(f"logos/{ch_name}.png"):
                    logo_path = f"logos/{ch_name}.png"
            
            channels.append({
                "name": ch_name, 
                "url": clean_url, 
                "keyId": current_key_id, 
                "key": current_key, 
                "cookie": cookie,
                "logo": logo_path
            })

    print(f"Found {len(channels)} channels. Starting generation...")

    for ch in channels:
        safe_name = ch['name'].replace(' ', '_')
        file_path = os.path.join(OUTPUT_DIR, f"{safe_name}.html")
        
        # Format title
        title = ch['name'].replace('_', ' ')
        
        content = HTML_TEMPLATE.replace("{CHANNEL_TITLE}", title) \
                               .replace("{STREAM_URL}", ch['url']) \
                               .replace("{KEY_ID}", ch['keyId']) \
                               .replace("{KEY}", ch['key']) \
                               .replace("{COOKIE}", ch['cookie'])
        
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
            
    print(f"Successfully generated {len(channels)} files in {OUTPUT_DIR}/")

    # Generate channels.json for the dashboard
    json_path = os.path.join(OUTPUT_DIR, "channels.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(channels, f, indent=2)
    print(f"Generated {json_path}")

if __name__ == "__main__":
    generate()


