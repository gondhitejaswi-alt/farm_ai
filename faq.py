"""
Farm AI - Farmer FAQ (Telugu / Hindi / English)
===============================================
Deliberately small and conservative. Every answer is general, widely accepted
guidance with no pesticide names, no disease treatments and no fertilizer doses.
Anything outside this list falls back to "ask your agriculture officer / KVK".

To add a question: append an entry to FAQS with q/a in all three languages and
a few keywords (any language). Have a local agriculture officer review new
answers before release.
"""

import re, os
from pathlib import Path

def _load_env():
    candidates = [
        Path(__file__).parent / ".env",
        Path(__file__).parent.parent / ".env",
        Path.cwd() / ".env",
    ]
    for env_path in candidates:
        if env_path.exists():
            for line in env_path.read_text(encoding="utf-8").splitlines():
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    k, v = line.split("=", 1)
                    os.environ.setdefault(k.strip(), v.strip())
            break
_load_env()

KCC_LINE = {
    "en": "Kisan Call Centre: 1800-180-1551 (toll free, 6 AM to 10 PM).",
    "te": "కిసాన్ కాల్ సెంటర్: 1800-180-1551 (ఉచితం, ఉదయం 6 నుండి రాత్రి 10 వరకు).",
    "hi": "किसान कॉल सेंटर: 1800-180-1551 (निःशुल्क, सुबह 6 से रात 10 बजे तक)।",
}

FAQS = [
    {
        "id": "soil_test",
        "q": {"en": "Why should I get my soil tested?",
              "te": "నేల పరీక్ష ఎందుకు చేయించుకోవాలి?",
              "hi": "मिट्टी की जांच क्यों करवानी चाहिए?"},
        "a": {"en": "A soil test shows your soil's pH and nutrient levels. With it you can choose a suitable crop and avoid wasting money on fertilizer your soil does not need. Ask your agriculture office or KVK how to get it done.",
              "te": "నేల పరీక్ష మీ నేల pH మరియు పోషక స్థాయిలను చూపిస్తుంది. దీనితో సరైన పంటను ఎంచుకోవచ్చు మరియు మీ నేలకు అవసరం లేని ఎరువుపై డబ్బు వృథా చేయకుండా ఉండవచ్చు. పరీక్ష ఎలా చేయించుకోవాలో మీ వ్యవసాయ కార్యాలయం లేదా KVK ని అడగండి.",
              "hi": "मिट्टी जांच से आपकी मिट्टी का pH और पोषक तत्वों का स्तर पता चलता है। इससे सही फसल चुन सकते हैं और ऐसी खाद पर पैसा बर्बाद होने से बच सकते हैं जिसकी मिट्टी को ज़रूरत नहीं। जांच कैसे करवाएं, यह अपने कृषि कार्यालय या KVK से पूछें।"},
        "kw": ["soil test", "test", "ph", "నేల పరీక్ష", "పరీక్ష", "मिट्टी जांच", "जांच", "जाँच"],
    },
    {
        "id": "shc",
        "q": {"en": "What is a Soil Health Card?",
              "te": "సాయిల్ హెల్త్ కార్డ్ అంటే ఏమిటి?",
              "hi": "सॉयल हेल्थ कार्ड क्या है?"},
        "a": {"en": "It is a card under a government scheme that gives the results of your soil test for your field. Bring it when you ask for crop or fertilizer advice. Ask your local agriculture office how to get one.",
              "te": "ఇది ప్రభుత్వ పథకం కింద మీ పొలం నేల పరీక్ష ఫలితాలను ఇచ్చే కార్డు. పంట లేదా ఎరువుల సలహా అడిగేటప్పుడు దీన్ని తీసుకెళ్లండి. ఒకటి ఎలా పొందాలో మీ స్థానిక వ్యవసాయ కార్యాలయాన్ని అడగండి.",
              "hi": "यह सरकारी योजना के तहत मिलने वाला कार्ड है जिसमें आपके खेत की मिट्टी जांच के नतीजे होते हैं। फसल या खाद की सलाह लेते समय इसे साथ रखें। कार्ड कैसे मिलेगा, यह अपने स्थानीय कृषि कार्यालय से पूछें।"},
        "kw": ["soil health card", "card", "shc", "సాయిల్ హెల్త్", "కార్డ్", "कार्ड", "हेल्थ कार्ड"],
    },
    {
        "id": "fert_amount",
        "q": {"en": "How much fertilizer should I put?",
              "te": "ఎంత ఎరువు వేయాలి?",
              "hi": "कितनी खाद डालनी चाहिए?"},
        "a": {"en": "The right amount depends on your crop, your soil test and local recommendations, so we cannot give a number here. Take your Soil Health Card to the agriculture office or KVK. Do not apply more than recommended: it wastes money and can harm the crop.",
              "te": "సరైన మోతాదు మీ పంట, నేల పరీక్ష మరియు స్థానిక సిఫార్సులపై ఆధారపడి ఉంటుంది, కాబట్టి ఇక్కడ సంఖ్య చెప్పలేము. మీ సాయిల్ హెల్త్ కార్డ్‌ను వ్యవసాయ కార్యాలయం లేదా KVK కి తీసుకెళ్లండి. సిఫార్సు కంటే ఎక్కువ వేయవద్దు: డబ్బు వృథా అవుతుంది, పంటకు హాని కావచ్చు.",
              "hi": "सही मात्रा आपकी फसल, मिट्टी जांच और स्थानीय सिफारिश पर निर्भर करती है, इसलिए यहाँ कोई संख्या नहीं दे सकते। अपना सॉयल हेल्थ कार्ड कृषि कार्यालय या KVK ले जाएं। सिफारिश से ज़्यादा न डालें: पैसा बर्बाद होता है और फसल को नुकसान हो सकता है।"},
        "kw": ["fertilizer", "fertiliser", "urea", "dap", "dose", "ఎరువు", "ఎరువులు", "యూరియా", "మోతాదు", "खाद", "उर्वरक", "यूरिया", "मात्रा"],
    },
    {
        "id": "irrigation",
        "q": {"en": "When should I water my crop?",
              "te": "పంటకు ఎప్పుడు నీరు పెట్టాలి?",
              "hi": "फसल को पानी कब देना चाहिए?"},
        "a": {"en": "Water needs differ by crop and growth stage, so we do not give exact amounts. A simple habit: check the soil by hand before irrigating, and look at the weather page. If good rain is forecast, you may be able to wait. Ask your agriculture officer for your crop's schedule.",
              "te": "నీటి అవసరం పంట మరియు పెరుగుదల దశను బట్టి మారుతుంది, కాబట్టి ఖచ్చితమైన పరిమాణాలు చెప్పము. సులభమైన అలవాటు: నీరు పెట్టే ముందు చేత్తో నేల తేమ చూడండి, వాతావరణ పేజీ చూడండి. మంచి వర్షం అంచనా ఉంటే ఆగవచ్చు. మీ పంట షెడ్యూల్ కోసం వ్యవసాయ అధికారిని అడగండి.",
              "hi": "पानी की ज़रूरत फसल और उसकी अवस्था के अनुसार बदलती है, इसलिए सटीक मात्रा नहीं बताते। एक आसान आदत: सिंचाई से पहले हाथ से मिट्टी की नमी देखें और मौसम पेज देखें। अच्छी बारिश का पूर्वानुमान हो तो रुक सकते हैं। अपनी फसल के कार्यक्रम के लिए कृषि अधिकारी से पूछें।"},
        "kw": ["water", "irrigation", "irrigate", "నీరు", "నీటి", "సాగునీరు", "పారుదల", "पानी", "सिंचाई"],
    },
    {
        "id": "spray_weather",
        "q": {"en": "What weather is bad for spraying?",
              "te": "పిచికారీకి ఎలాంటి వాతావరణం మంచిది కాదు?",
              "hi": "छिड़काव के लिए कैसा मौसम ठीक नहीं?"},
        "a": {"en": "Avoid spraying when it is windy (the spray drifts) or when rain is likely soon (it washes off). Always follow the label of the product and the advice of your agriculture officer.",
              "te": "గాలి ఎక్కువగా ఉన్నప్పుడు (మందు ఎగిరిపోతుంది) లేదా త్వరలో వర్షం వచ్చే అవకాశం ఉన్నప్పుడు (కొట్టుకుపోతుంది) పిచికారీ చేయవద్దు. ఎల్లప్పుడూ మందు లేబుల్‌ను మరియు వ్యవసాయ అధికారి సలహాను పాటించండి.",
              "hi": "हवा तेज़ हो (छिड़काव उड़ जाता है) या जल्द बारिश की संभावना हो (धुल जाता है) तो छिड़काव न करें। हमेशा उत्पाद के लेबल और कृषि अधिकारी की सलाह मानें।"},
        "kw": ["spray", "spraying", "పిచికారీ", "పిచికారి", "छिड़काव"],
    },
    {
        "id": "forecast_accuracy",
        "q": {"en": "Can I fully trust the weather forecast?",
              "te": "వాతావరణ అంచనాను పూర్తిగా నమ్మవచ్చా?",
              "hi": "क्या मौसम पूर्वानुमान पर पूरा भरोसा कर सकते हैं?"},
        "a": {"en": "No forecast is guaranteed. Use it as a guide, and look again before important work like irrigation, spraying or harvest.",
              "te": "ఏ అంచనాకూ హామీ లేదు. దీన్ని మార్గదర్శిగా వాడండి, నీరు పెట్టడం, పిచికారీ, కోత వంటి ముఖ్యమైన పనుల ముందు మళ్లీ చూడండి.",
              "hi": "कोई भी पूर्वानुमान गारंटी नहीं है। इसे मार्गदर्शन की तरह लें और सिंचाई, छिड़काव या कटाई जैसे ज़रूरी काम से पहले फिर देखें।"},
        "kw": ["forecast", "accurate", "trust", "అంచనా", "నమ్మ", "पूर्वानुमान", "भरोसा"],
    },
    {
        "id": "how_crop_advice",
        "q": {"en": "How does the crop advice work?",
              "te": "పంట సలహా ఎలా పనిచేస్తుంది?",
              "hi": "फसल सलाह कैसे काम करती है?"},
        "a": {"en": "It compares your soil pH, the season and your state with the usual growing conditions of each crop in our crop list. It is a simple guide, not a guarantee. Please confirm with your agriculture officer or KVK.",
              "te": "ఇది మీ నేల pH, కాలం మరియు రాష్ట్రాన్ని మా పంటల జాబితాలోని ప్రతి పంట సాధారణ పెరుగుదల పరిస్థితులతో పోలుస్తుంది. ఇది సులభమైన మార్గదర్శి మాత్రమే, హామీ కాదు. దయచేసి వ్యవసాయ అధికారి లేదా KVK తో నిర్ధారించుకోండి.",
              "hi": "यह आपकी मिट्टी के pH, मौसम और राज्य की तुलना हमारी फसल सूची की हर फसल की सामान्य उगाने की स्थितियों से करती है। यह एक सरल मार्गदर्शन है, गारंटी नहीं। कृपया कृषि अधिकारी या KVK से पुष्टि करें।"},
        "kw": ["advice", "recommend", "how", "work", "సలహా", "ఎలా", "సిఫార్సు", "सलाह", "कैसे", "सिफारिश"],
    },
    {
        "id": "contact",
        "q": {"en": "Who can I call for farming help?",
              "te": "వ్యవసాయ సహాయం కోసం ఎవరికి ఫోన్ చేయాలి?",
              "hi": "खेती की मदद के लिए किसे फ़ोन करें?"},
        "a": {"en": "Call the Kisan Call Centre: 1800-180-1551 (toll free, 6 AM to 10 PM). You can also visit your local agriculture office or Krishi Vigyan Kendra (KVK).",
              "te": "కిసాన్ కాల్ సెంటర్‌కు ఫోన్ చేయండి: 1800-180-1551 (ఉచితం, ఉదయం 6 నుండి రాత్రి 10 వరకు). మీ స్థానిక వ్యవసాయ కార్యాలయం లేదా కృషి విజ్ఞాన కేంద్రాన్ని (KVK) కూడా సందర్శించవచ్చు.",
              "hi": "किसान कॉल सेंटर पर फ़ोन करें: 1800-180-1551 (निःशुल्क, सुबह 6 से रात 10 बजे तक)। आप अपने स्थानीय कृषि कार्यालय या कृषि विज्ञान केंद्र (KVK) भी जा सकते हैं।"},
        "kw": ["call", "phone", "contact", "helpline", "officer", "kvk", "ఫోన్", "అధికారి", "సంప్రదించ", "फ़ोन", "फोन", "अधिकारी", "संपर्क", "हेल्पलाइन"],
    },
]

# Words that mean "pest / disease / pesticide" -> always escalate, never answer ourselves
ESCALATE_KW = [
    "pest", "disease", "insect", "pesticide", "insecticide", "fungus", "fungicide", "worm", "blight", "wilt",
    "పురుగు", "చీడ", "తెగులు", "మందు", "పురుగుమందు", "ఆకు మచ్చ", "వాడిపోవ",
    "कीट", "रोग", "कीड़ा", "कीटनाशक", "फफूंद", "इल्ली", "झुलसा", "मुरझा",
]


def suggested_questions(lang: str):
    return [(f["id"], f["q"].get(lang) or f["q"]["en"]) for f in FAQS]


def get_answer_by_id(faq_id: str, lang: str):
    for f in FAQS:
        if f["id"] == faq_id:
            return f["a"].get(lang) or f["a"]["en"]
    return None


def _norm(s: str) -> str:
    return re.sub(r"\s+", " ", s.lower().strip())


def _has(q: str, key: str) -> bool:
    """Plain keys must match as whole words (so 'ph' does not match 'photo');
    Telugu/Hindi keys are matched as substrings because those scripts have
    suffixes attached to words."""
    key = _norm(key)
    if key.isascii():
        return re.search(r"(?<![a-z0-9])" + re.escape(key) + r"(?![a-z0-9])", q) is not None
    return key in q


def answer_free_text(text: str, lang: str):
    """
    Returns (kind, answer) where kind is one of:
      "faq"       matched a curated FAQ
      "escalate"  pest / disease / pesticide question -> refer to expert
      "fallback"  nothing reliable to say
    """
    q = _norm(text)
    if len(q) < 2:
        return "fallback", None
    if any(_has(q, k) for k in ESCALATE_KW):
        return "escalate", None
    best, best_score = None, 0
    for f in FAQS:
        score = sum(1 for k in f["kw"] if _has(q, k))
        if score and best_score < score:
            best, best_score = f, score
    if best:
        return "faq", best["a"].get(lang) or best["a"]["en"]
    return "fallback", None


def ask_ai_assistant(query: str, lang: str = "te", crop: str = "Rice", state: str = "Telangana") -> dict:
    """
    AI-powered assistant for Indian farmers.
    1. Tries curated FAQ first.
    2. If not matched, calls Gemini AI in requested language (Telugu, Hindi, English).
    3. Falls back gracefully to KVK helpline if offline.
    """
    import os, json, urllib.request, urllib.error
    
    # 1. Curated FAQ check
    kind, ans = answer_free_text(query, lang)
    if kind == "faq" and ans:
        return {"source": "FAQ", "answer": ans, "escalate": False}
    if kind == "escalate":
        esc_msg = {
            "te": "పురుగుమందులు మరియు చీడపీడల నియంత్రణ కోసం, దయచేసి సమీపంలోని వ్యవసాయ అధికారి లేదా కృషి విజ్ఞాన కేంద్రం (KVK) ను సంప్రదించండి. కిసాన్ కాల్ సెంటర్: 1800-180-1551 (ఉచితం).",
            "hi": "कीटनाशक और कीट नियंत्रण के लिए, कृपया नज़दीकी कृषि अधिकारी या कृषि विज्ञान केंद्र (KVK) से संपर्क करें। किसान कॉल सेंटर: 1800-180-1551 (निःशुल्क)।",
            "en": "For pesticides and pest control, please consult your local Agriculture Officer or Krishi Vigyan Kendra (KVK). Kisan Call Centre: 1800-180-1551 (Toll-Free)."
        }.get(lang, "Please consult your local Agriculture Officer or call Kisan Call Centre 1800-180-1551.")
        return {"source": "Escalation", "answer": esc_msg, "escalate": True}

    # 2. Try Gemini AI
    api_key = os.getenv("GEMINI_API_KEY", "").strip()
    if api_key:
        lang_names = {"te": "Telugu (తెలుగు)", "hi": "Hindi (हिन्दी)", "en": "English"}
        target_lang = lang_names.get(lang, "English")
        
        prompt = f"""You are a caring, knowledgeable Krishi Vigyan Kendra (KVK) agricultural expert helping an Indian farmer in {state}.
The farmer is growing {crop} (or asking a general farming question).

Farmer's Question: "{query}"

Instructions:
1. Respond ENTIRELY in {target_lang}. Use clear, natural agricultural terminology easily understood by a village farmer.
2. Keep the answer warm, practical, and concise (3-4 simple sentences).
3. Do NOT recommend banned chemicals. Always recommend safe, eco-friendly farming practices.
4. Conclude with a helpful suggestion or remind them to call Kisan Call Centre (1800-180-1551) for on-ground assistance."""

        payload = json.dumps({
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {"temperature": 0.4, "maxOutputTokens": 350}
        }).encode("utf-8")

        models = ["gemini-flash-lite-latest", "gemini-2.5-flash", "gemini-flash-latest"]
        for m in models:
            try:
                url = f"https://generativelanguage.googleapis.com/v1beta/models/{m}:generateContent?key={api_key}"
                req = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json"}, method="POST")
                with urllib.request.urlopen(req, timeout=15) as resp:
                    data = json.loads(resp.read().decode("utf-8"))
                    text = data["candidates"][0]["content"]["parts"][0]["text"].strip()
                    return {"source": f"Gemini AI ({m})", "answer": text, "escalate": False}
            except Exception:
                continue

    # 3. Fallback
    fb = {
        "te": "క్షమించండి, ప్రస్తుతం దీనికి ప్రత్యక్ష సమాధానం కనుగొనలేకపోయాము. దయచేసి మీ స్థానిక వ్యవసాయ విస్తరణ అధికారి (AEO) ని సంప్రదించండి లేదా కిసాన్ కాల్ సెంటర్: 1800-180-1551 కి కాల్ చేయండి.",
        "hi": "क्षमा करें, अभी इसका सीधा उत्तर नहीं मिल पाया। कृपया अपने स्थानीय कृषि अधिकारी से संपर्क करें या किसान कॉल सेंटर 1800-180-1551 पर कॉल करें।",
        "en": "Sorry, could not find an answer right now. Please contact your local Agriculture Extension Officer or call Kisan Call Centre: 1800-180-1551 (Toll Free)."
    }.get(lang, "Please contact your local Agriculture Officer or call Kisan Call Centre: 1800-180-1551.")
    return {"source": "KVK Guidance", "answer": fb, "escalate": False}
