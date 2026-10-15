"""
Farm AI - Local illustrations (additive module)
===============================================
Small original SVG illustrations drawn in code, so the interface needs NO
internet for pictures and no image licences. Each has meaningful alt text.
Real photographs of Telangana / AP farmers can be dropped into
dashboard/assets/ later and shown with st.image().
"""
import base64

_G, _O, _L, _B = "#2E7D32", "#E65100", "#A5D6A7", "#1976D2"

_SVG = {
    "crop": f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64"><rect width="64" height="64" rx="14" fill="#E8F5E9"/>'
            f'<path d="M32 54V30" stroke="{_G}" stroke-width="4" stroke-linecap="round"/>'
            f'<path d="M32 34C20 34 14 26 14 16c12 0 18 7 18 18z" fill="{_G}"/>'
            f'<path d="M32 28c0-10 6-16 18-16 0 10-6 16-18 16z" fill="#66BB6A"/><rect x="14" y="52" width="36" height="4" rx="2" fill="#8D6E63"/></svg>',
    "fert": f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64"><rect width="64" height="64" rx="14" fill="#FFF3E0"/>'
            f'<path d="M20 22h24l4 30H16z" fill="{_O}"/><path d="M26 22l3-8h6l3 8" fill="#FFB74D"/>'
            f'<circle cx="32" cy="38" r="7" fill="#fff"/><path d="M28 38h8M32 34v8" stroke="{_O}" stroke-width="3" stroke-linecap="round"/></svg>',
    "weather": f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64"><rect width="64" height="64" rx="14" fill="#E3F2FD"/>'
               f'<circle cx="24" cy="24" r="9" fill="#FFB300"/><path d="M20 46a9 9 0 0 1 2-17 12 12 0 0 1 23 3 7 7 0 0 1-1 14z" fill="#fff" stroke="{_B}" stroke-width="2"/></svg>',
    "help": f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64"><rect width="64" height="64" rx="14" fill="#F3E5F5"/>'
            f'<path d="M12 16h40v26H30l-10 9v-9h-8z" fill="#7B1FA2"/><circle cx="24" cy="29" r="3" fill="#fff"/><circle cx="32" cy="29" r="3" fill="#fff"/><circle cx="40" cy="29" r="3" fill="#fff"/></svg>',
}

_ALT = {
    "crop": {"en": "Green seedling illustration", "te": "పచ్చని మొలక చిత్రం", "hi": "हरे अंकुर का चित्र"},
    "fert": {"en": "Fertilizer bag illustration", "te": "ఎరువుల సంచి చిత్రం", "hi": "खाद की बोरी का चित्र"},
    "weather": {"en": "Sun and cloud illustration", "te": "సూర్యుడు మరియు మేఘం చిత్రం", "hi": "सूरज और बादल का चित्र"},
    "help": {"en": "Chat bubble illustration", "te": "చాట్ బబుల్ చిత్రం", "hi": "चैट बबल का चित्र"},
}


def icon_html(kind: str, lang: str = "en", size: int = 56) -> str:
    svg = _SVG.get(kind)
    if not svg:
        return ""
    b64 = base64.b64encode(svg.encode("utf-8")).decode("ascii")
    alt = _ALT.get(kind, {}).get(lang) or _ALT.get(kind, {}).get("en", "")
    return f'<img src="data:image/svg+xml;base64,{b64}" alt="{alt}" width="{size}" height="{size}" style="border-radius:12px;"/>'
