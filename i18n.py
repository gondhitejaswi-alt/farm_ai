"""
Farm AI - Localization
======================
One place for every farmer-facing string, in Telugu (te), Hindi (hi), English (en).

Usage:
    from i18n import t
    t("nav_home", "te")
    t("greeting", "hi", name="Raju")

Fallback order: requested language -> English -> the key itself (never a crash,
never a Python/ML error shown to a farmer).

NOTE: Telugu and Hindi wording here should be reviewed by a native speaker /
local agriculture extension officer before real-world release.
"""

LANGUAGES = {"te": "తెలుగు", "hi": "हिन्दी", "en": "English"}
DEFAULT_LANG = "te"

STRINGS = {
    # ── App / navigation ───────────────────────────────────
    "app_title": {"en": "Farm AI", "te": "ఫార్మ్ AI", "hi": "फार्म AI"},
    "app_tagline": {
        "en": "Simple farming help in your language",
        "te": "మీ భాషలో సులభమైన వ్యవసాయ సహాయం",
        "hi": "आपकी भाषा में आसान खेती सहायता",
    },
    "greeting": {
        "en": "Namaste, {name}!",
        "te": "నమస్కారం, {name}!",
        "hi": "नमस्ते, {name}!",
    },
    "language": {"en": "Language", "te": "భాష", "hi": "भाषा"},
    "nav_home": {"en": "Home", "te": "హోమ్", "hi": "होम"},
    "nav_crop": {"en": "Crop Advice", "te": "పంట సలహా", "hi": "फसल सलाह"},
    "nav_soil": {"en": "Soil & Fertilizer", "te": "నేల & ఎరువులు", "hi": "मिट्टी और खाद"},
    "nav_weather": {"en": "Weather", "te": "వాతావరణం", "hi": "मौसम"},
    "nav_help": {"en": "Ask for Help", "te": "సహాయం అడగండి", "hi": "मदद पूछें"},
    "nav_history": {"en": "My History", "te": "నా చరిత్ర", "hi": "मेरा इतिहास"},
    "nav_settings": {"en": "Settings", "te": "సెట్టింగ్స్", "hi": "सेटिंग्स"},

    # ── Home ───────────────────────────────────────────────
    "home_what_today": {
        "en": "What would you like to do today?",
        "te": "ఈ రోజు మీరు ఏమి చేయాలనుకుంటున్నారు?",
        "hi": "आज आप क्या करना चाहते हैं?",
    },
    "qa_crop": {"en": "Which crop to grow?", "te": "ఏ పంట వేయాలి?", "hi": "कौन सी फसल लगाएं?"},
    "qa_soil": {"en": "Check my soil", "te": "నా నేల చూడండి", "hi": "मेरी मिट्टी देखें"},
    "qa_weather": {"en": "Today's weather", "te": "ఈ రోజు వాతావరణం", "hi": "आज का मौसम"},
    "qa_help": {"en": "Ask a question", "te": "ప్రశ్న అడగండి", "hi": "सवाल पूछें"},
    "open": {"en": "Open", "te": "తెరవండి", "hi": "खोलें"},
    "alerts_title": {"en": "Farming alerts", "te": "వ్యవసాయ హెచ్చరికలు", "hi": "खेती की चेतावनियाँ"},
    "no_alerts": {
        "en": "No special alerts right now.",
        "te": "ప్రస్తుతం ప్రత్యేక హెచ్చరికలు లేవు.",
        "hi": "अभी कोई विशेष चेतावनी नहीं है।",
    },
    "alerts_need_weather": {
        "en": "Alerts need live weather, which is not available right now.",
        "te": "హెచ్చరికలకు ప్రత్యక్ష వాతావరణ సమాచారం కావాలి, అది ఇప్పుడు అందుబాటులో లేదు.",
        "hi": "चेतावनियों के लिए ताज़ा मौसम जानकारी चाहिए, जो अभी उपलब्ध नहीं है।",
    },

    # ── Common ─────────────────────────────────────────────
    "location": {"en": "Your place", "te": "మీ ప్రాంతం", "hi": "आपका स्थान"},
    "state": {"en": "State", "te": "రాష్ట్రం", "hi": "राज्य"},
    "state_telangana": {"en": "Telangana", "te": "తెలంగాణ", "hi": "तेलंगाना"},
    "state_ap": {"en": "Andhra Pradesh", "te": "ఆంధ్రప్రదేశ్", "hi": "आंध्र प्रदेश"},
    "your_name": {"en": "Your name", "te": "మీ పేరు", "hi": "आपका नाम"},
    "default_name": {"en": "Farmer", "te": "రైతు గారు", "hi": "किसान भाई"},
    "season": {"en": "Season", "te": "కాలం", "hi": "मौसम (सीज़न)"},
    "season_kharif": {"en": "Kharif (June–October)", "te": "ఖరీఫ్ (జూన్–అక్టోబర్)", "hi": "खरीफ (जून–अक्टूबर)"},
    "season_rabi": {"en": "Rabi (November–March)", "te": "రబీ (నవంబర్–మార్చి)", "hi": "रबी (नवंबर–मार्च)"},
    "season_summer": {"en": "Summer (April–May)", "te": "వేసవి (ఏప్రిల్–మే)", "hi": "गर्मी (अप्रैल–मई)"},
    "loading": {"en": "Please wait...", "te": "దయచేసి వేచి ఉండండి...", "hi": "कृपया प्रतीक्षा करें..."},
    "something_wrong": {
        "en": "Sorry, something went wrong. Please try again.",
        "te": "క్షమించండి, ఏదో తప్పు జరిగింది. దయచేసి మళ్లీ ప్రయత్నించండి.",
        "hi": "क्षमा करें, कुछ गड़बड़ हुई। कृपया फिर से कोशिश करें।",
    },
    "disclaimer": {
        "en": "This is a general estimate, not a guarantee. Please also check with your local agriculture officer or Krishi Vigyan Kendra (KVK).",
        "te": "ఇది సాధారణ అంచనా మాత్రమే, హామీ కాదు. దయచేసి మీ స్థానిక వ్యవసాయ అధికారి లేదా కృషి విజ్ఞాన కేంద్రం (KVK) తో కూడా సంప్రదించండి.",
        "hi": "यह सामान्य अनुमान है, गारंटी नहीं। कृपया अपने स्थानीय कृषि अधिकारी या कृषि विज्ञान केंद्र (KVK) से भी सलाह लें।",
    },

    # ── Crop advice ────────────────────────────────────────
    "crop_title": {"en": "Which crop is suitable?", "te": "ఏ పంట అనుకూలం?", "hi": "कौन सी फसल उपयुक्त है?"},
    "crop_intro": {
        "en": "Tell us about your soil and season. We will suggest crops that suit them.",
        "te": "మీ నేల మరియు కాలం గురించి చెప్పండి. వాటికి సరిపోయే పంటలను సూచిస్తాము.",
        "hi": "अपनी मिट्टी और मौसम के बारे में बताएं। हम उनके अनुसार फसलें सुझाएंगे।",
    },
    "ph_label": {"en": "Soil pH (from soil test)", "te": "నేల pH (నేల పరీక్ష నుండి)", "hi": "मिट्टी का pH (मिट्टी जांच से)"},
    "ph_help": {
        "en": "pH tells how acidic or salty-alkaline the soil is. Scale 0–14, no unit. Most crops like 6 to 7.5. It is printed on your Soil Health Card.",
        "te": "pH అంటే నేల ఎంత ఆమ్లంగా లేదా క్షారంగా ఉందో తెలిపే సంఖ్య. 0–14 స్కేలు, యూనిట్ లేదు. చాలా పంటలకు 6 నుండి 7.5 మంచిది. ఇది మీ సాయిల్ హెల్త్ కార్డ్‌లో ఉంటుంది.",
        "hi": "pH बताता है कि मिट्टी कितनी अम्लीय या क्षारीय है। पैमाना 0–14, कोई इकाई नहीं। ज़्यादातर फसलों के लिए 6 से 7.5 अच्छा है। यह आपके सॉयल हेल्थ कार्ड पर लिखा होता है।",
    },
    "get_crop": {"en": "Show suitable crops", "te": "అనుకూల పంటలు చూపండి", "hi": "उपयुक्त फसलें दिखाएं"},
    "best_crop": {"en": "Most suitable crop", "te": "అత్యంత అనుకూలమైన పంట", "hi": "सबसे उपयुक्त फसल"},
    "other_crops": {"en": "Other crops that can also suit", "te": "సరిపోయే ఇతర పంటలు", "hi": "अन्य उपयुक्त फसलें"},
    "why_crop": {"en": "Why this crop?", "te": "ఈ పంట ఎందుకు?", "hi": "यह फसल क्यों?"},
    "why_ph": {
        "en": "Your soil pH ({ph}) is inside the range this crop usually grows well in ({lo}–{hi}).",
        "te": "మీ నేల pH ({ph}) ఈ పంట సాధారణంగా బాగా పెరిగే పరిధిలో ({lo}–{hi}) ఉంది.",
        "hi": "आपकी मिट्टी का pH ({ph}) उस सीमा ({lo}–{hi}) में है जिसमें यह फसल आमतौर पर अच्छी उगती है।",
    },
    "why_season": {
        "en": "It is normally grown in the {season} season.",
        "te": "ఇది సాధారణంగా {season} కాలంలో పండిస్తారు.",
        "hi": "यह आमतौर पर {season} मौसम में उगाई जाती है।",
    },
    "why_region": {
        "en": "It is commonly grown in your state.",
        "te": "ఇది మీ రాష్ట్రంలో సాధారణంగా పండిస్తారు.",
        "hi": "यह आपके राज्य में आमतौर पर उगाई जाती है।",
    },
    "crop_facts": {"en": "General growing information", "te": "సాధారణ సాగు సమాచారం", "hi": "सामान्य खेती जानकारी"},
    "fact_duration": {"en": "Usual crop duration: about {d} days", "te": "సాధారణ పంట కాలం: సుమారు {d} రోజులు", "hi": "सामान्य फसल अवधि: लगभग {d} दिन"},
    "fact_ph": {"en": "Comfortable soil pH: {lo} to {hi}", "te": "అనుకూల నేల pH: {lo} నుండి {hi}", "hi": "उपयुक्त मिट्टी pH: {lo} से {hi}"},
    "next_steps": {"en": "What to do next", "te": "తర్వాత ఏమి చేయాలి", "hi": "आगे क्या करें"},
    "step_1": {
        "en": "Meet your local agriculture officer or KVK and confirm this crop for your village.",
        "te": "మీ స్థానిక వ్యవసాయ అధికారిని లేదా KVK ని కలిసి, మీ గ్రామానికి ఈ పంట సరిపోతుందో నిర్ధారించుకోండి.",
        "hi": "अपने स्थानीय कृषि अधिकारी या KVK से मिलकर पुष्टि करें कि यह फसल आपके गांव के लिए ठीक है।",
    },
    "step_2": {
        "en": "Check the weather page before sowing.",
        "te": "విత్తే ముందు వాతావరణ పేజీ చూడండి.",
        "hi": "बुवाई से पहले मौसम पेज देखें।",
    },
    "step_3": {
        "en": "Use the Soil & Fertilizer page and your Soil Health Card to plan fertilizer.",
        "te": "ఎరువుల ప్రణాళిక కోసం నేల & ఎరువులు పేజీని మరియు మీ సాయిల్ హెల్త్ కార్డ్‌ను చూడండి.",
        "hi": "खाद की योजना के लिए मिट्टी और खाद पेज तथा अपना सॉयल हेल्थ कार्ड देखें।",
    },
    "no_crop_found": {
        "en": "We could not find a suitable crop for these values. Please check the numbers or ask your agriculture officer.",
        "te": "ఈ విలువలకు సరిపోయే పంట కనబడలేదు. దయచేసి సంఖ్యలను సరిచూడండి లేదా మీ వ్యవసాయ అధికారిని అడగండి.",
        "hi": "इन मानों के लिए कोई उपयुक्त फसल नहीं मिली। कृपया संख्याएँ जाँचें या अपने कृषि अधिकारी से पूछें।",
    },
    "bad_ph": {
        "en": "Soil pH must be between 3 and 10. Please check your soil test.",
        "te": "నేల pH 3 మరియు 10 మధ్య ఉండాలి. దయచేసి మీ నేల పరీక్షను చూడండి.",
        "hi": "मिट्टी का pH 3 से 10 के बीच होना चाहिए। कृपया अपनी मिट्टी जांच देखें।",
    },
    "no_soil_test": {
        "en": "Don't have a soil test? Ask your agriculture office how to get a Soil Health Card. Without it, the advice below is only rough.",
        "te": "నేల పరీక్ష లేదా? సాయిల్ హెల్త్ కార్డ్ ఎలా పొందాలో మీ వ్యవసాయ కార్యాలయాన్ని అడగండి. అది లేకుండా కింది సలహా అంచనా మాత్రమే.",
        "hi": "मिट्टी जांच नहीं है? सॉयल हेल्थ कार्ड कैसे मिलेगा, यह अपने कृषि कार्यालय से पूछें। उसके बिना नीचे की सलाह केवल मोटा अंदाज़ा है।",
    },

    # ── Soil & fertilizer ──────────────────────────────────
    "soil_title": {"en": "Soil & Fertilizer", "te": "నేల & ఎరువులు", "hi": "मिट्टी और खाद"},
    "soil_intro": {
        "en": "Enter the numbers from your Soil Health Card. We show whether each nutrient looks low, fine or high for your crop.",
        "te": "మీ సాయిల్ హెల్త్ కార్డ్‌లోని సంఖ్యలను నమోదు చేయండి. మీ పంటకు ప్రతి పోషకం తక్కువ, సరిపడా లేదా ఎక్కువగా ఉందో చూపిస్తాము.",
        "hi": "अपने सॉयल हेल्थ कार्ड की संख्याएँ डालें। हम बताएंगे कि आपकी फसल के लिए हर पोषक तत्व कम, ठीक या ज़्यादा है।",
    },
    "pick_crop": {"en": "Your crop", "te": "మీ పంట", "hi": "आपकी फसल"},
    "nitrogen": {"en": "Nitrogen (N)", "te": "నత్రజని (N)", "hi": "नाइट्रोजन (N)"},
    "phosphorus": {"en": "Phosphorus (P)", "te": "భాస్వరం (P)", "hi": "फास्फोरस (P)"},
    "potassium": {"en": "Potassium (K)", "te": "పొటాష్ (K)", "hi": "पोटाश (K)"},
    "unit_kgha": {"en": "kg per hectare", "te": "కిలోలు / హెక్టారు", "hi": "किलो / हेक्टेयर"},
    "check_soil": {"en": "Check my soil", "te": "నా నేల చూడండి", "hi": "मेरी मिट्టी जाँचें"},
    "level_low": {"en": "Low", "te": "తక్కువ", "hi": "कम"},
    "level_ok": {"en": "Fine", "te": "సరిపడా", "hi": "ठीक"},
    "level_high": {"en": "High", "te": "ఎక్కువ", "hi": "ज़्यादा"},
    "level_low_msg": {
        "en": "{n} looks low compared with what {crop} usually needs.",
        "te": "{crop} సాధారణంగా కోరే స్థాయికి {n} తక్కువగా ఉంది.",
        "hi": "{crop} को आमतौर पर जितना चाहिए, उसकी तुलना में {n} कम है।",
    },
    "level_ok_msg": {
        "en": "{n} looks fine for {crop}.",
        "te": "{crop} కు {n} సరిపడా ఉంది.",
        "hi": "{crop} के लिए {n} ठीक है।",
    },
    "level_high_msg": {
        "en": "{n} is already high. Do not add more of it.",
        "te": "{n} ఇప్పటికే ఎక్కువగా ఉంది. దీన్ని ఇంకా వేయకండి.",
        "hi": "{n} पहले से ज़्यादा है। इसे और न डालें।",
    },
    "fert_no_dose_title": {"en": "How much fertilizer to apply?", "te": "ఎంత ఎరువు వేయాలి?", "hi": "कितनी खाद डालें?"},
    "fert_no_dose": {
        "en": "We cannot give an exact fertilizer amount from this app. The right amount depends on your crop, soil test and local recommendation. Please take your Soil Health Card to the agriculture office or KVK and ask for the dose for your field.",
        "te": "ఈ యాప్ ఖచ్చితమైన ఎరువు మోతాదు చెప్పలేదు. సరైన మోతాదు మీ పంట, నేల పరీక్ష మరియు స్థానిక సిఫార్సుపై ఆధారపడి ఉంటుంది. దయచేసి మీ సాయిల్ హెల్త్ కార్డ్‌ను వ్యవసాయ కార్యాలయం లేదా KVK కి తీసుకెళ్లి మీ పొలానికి మోతాదు అడగండి.",
        "hi": "यह ऐप खाद की सटीक मात्रा नहीं बता सकता। सही मात्रा आपकी फसल, मिट्टी जांच और स्थानीय सिफारिश पर निर्भर करती है। कृपया अपना सॉयल हेल्थ कार्ड कृषि कार्यालय या KVK ले जाकर अपने खेत की मात्रा पूछें।",
    },
    "fert_warning": {
        "en": "More fertilizer is not always better. Too much wastes money, can harm the crop and pollutes water.",
        "te": "ఎక్కువ ఎరువు ఎప్పుడూ మంచిది కాదు. ఎక్కువైతే డబ్బు వృథా, పంటకు హాని, నీరు కలుషితం అవుతుంది.",
        "hi": "ज़्यादा खाद हमेशा बेहतर नहीं होती। ज़्यादा डालने से पैसा बेकार जाता है, फसल को नुकसान हो सकता है और पानी प्रदूषित होता है।",
    },
    "soil_ph_low_msg": {
        "en": "Your soil is acidic. Ask your agriculture officer whether lime is needed for your field.",
        "te": "మీ నేల ఆమ్లంగా ఉంది. మీ పొలానికి సున్నం అవసరమా అని వ్యవసాయ అధికారిని అడగండి.",
        "hi": "आपकी मिट्टी अम्लीय है। अपने कृषि अधिकारी से पूछें कि खेत में चूने की ज़रूरत है या नहीं।",
    },
    "soil_ph_high_msg": {
        "en": "Your soil is alkaline. Ask your agriculture officer how to manage it for your field.",
        "te": "మీ నేల క్షారంగా ఉంది. మీ పొలంలో దీన్ని ఎలా సరిచేయాలో వ్యవసాయ అధికారిని అడగండి.",
        "hi": "आपकी मिट्टी क्षारीय है। अपने कृषि अधिकारी से पूछें कि खेत में इसे कैसे सुधारें।",
    },
    "soil_ph_ok_msg": {
        "en": "Your soil pH is in a comfortable range for this crop.",
        "te": "మీ నేల pH ఈ పంటకు అనుకూల పరిధిలో ఉంది.",
        "hi": "आपकी मिट्टी का pH इस फसल के लिए उपयुक्त सीमा में है।",
    },
    "estimate_note": {
        "en": "These Low/Fine/High labels compare your numbers with general typical values for the crop. They are not a laboratory recommendation.",
        "te": "ఈ తక్కువ/సరిపడా/ఎక్కువ లేబుళ్లు మీ సంఖ్యలను పంటకు సాధారణ విలువలతో పోల్చినవి మాత్రమే. ఇవి ప్రయోగశాల సిఫార్సు కాదు.",
        "hi": "ये कम/ठीक/ज़्यादा लेबल आपकी संख्याओं की फसल के सामान्य मानों से तुलना हैं। यह प्रयोगशाला की सिफारिश नहीं है।",
    },

    # ── Weather ────────────────────────────────────────────
    "weather_title": {"en": "Weather", "te": "వాతావరణం", "hi": "मौसम"},
    "temperature": {"en": "Temperature", "te": "ఉష్ణోగ్రత", "hi": "तापमान"},
    "humidity": {"en": "Humidity", "te": "తేమ", "hi": "नमी"},
    "wind": {"en": "Wind", "te": "గాలి", "hi": "हवा"},
    "high_low": {"en": "Today high / low", "te": "ఈ రోజు గరిష్ఠ / కనిష్ఠ", "hi": "आज अधिकतम / न्यूनतम"},
    "rain_chance": {"en": "Chance of rain today", "te": "ఈ రోజు వర్షం అవకాశం", "hi": "आज बारिश की संभावना"},
    "last_updated": {"en": "Last updated", "te": "చివరిగా నవీకరించినది", "hi": "आख़िरी अपडेट"},
    "weather_unavailable": {
        "en": "Weather is not available right now. Please check your internet and try again later. We do not show guessed numbers.",
        "te": "వాతావరణ సమాచారం ఇప్పుడు అందుబాటులో లేదు. దయచేసి ఇంటర్నెట్ చూసి కొంత సేపటి తర్వాత ప్రయత్నించండి. అంచనా సంఖ్యలను చూపము.",
        "hi": "मौसम की जानकारी अभी उपलब्ध नहीं है। कृपया इंटरनेट जाँचें और बाद में फिर कोशिश करें। हम अंदाज़े के आँकड़े नहीं दिखाते।",
    },
    "weather_not_configured": {
        "en": "Weather is switched off because no weather key is set up. (Admin: add OPENWEATHER_API_KEY to .env)",
        "te": "వాతావరణ కీ సెట్ చేయలేదు కాబట్టి వాతావరణం ఆఫ్‌లో ఉంది. (అడ్మిన్: .env లో OPENWEATHER_API_KEY జోడించండి)",
        "hi": "मौसम कुंजी सेट नहीं है, इसलिए मौसम बंद है। (एडमिन: .env में OPENWEATHER_API_KEY जोड़ें)",
    },
    "weather_old": {
        "en": "This weather is more than {m} minutes old and may have changed.",
        "te": "ఈ వాతావరణ సమాచారం {m} నిమిషాల కంటే పాతది, మారి ఉండవచ్చు.",
        "hi": "यह मौसम जानकारी {m} मिनट से ज़्यादा पुरानी है और बदल गई हो सकती है।",
    },
    "weather_forecast_note": {
        "en": "Forecasts can be wrong. Please use them only as a guide.",
        "te": "అంచనాలు తప్పు కావచ్చు. వీటిని మార్గదర్శిగా మాత్రమే వాడండి.",
        "hi": "पूर्वानुमान गलत भी हो सकते हैं। इन्हें केवल मार्गदर्शन के रूप में लें।",
    },
    "weather_credit": {"en": "Weather data: OpenWeatherMap", "te": "వాతావరణ సమాచారం: OpenWeatherMap", "hi": "मौसम डेटा: OpenWeatherMap"},
    "next_days": {"en": "Next few days", "te": "రాబోయే రోజులు", "hi": "अगले कुछ दिन"},
    "refresh": {"en": "Refresh", "te": "రిఫ్రెష్", "hi": "रीफ्रेश"},
    "choose_place": {"en": "Choose your district", "te": "మీ జిల్లాను ఎంచుకోండి", "hi": "अपना ज़िला चुनें"},

    # weather summary building blocks
    "ws_temp_hot": {"en": "It is hot today", "te": "ఈ రోజు చాలా వేడిగా ఉంది", "hi": "आज बहुत गर्मी है"},
    "ws_temp_warm": {"en": "It is warm today", "te": "ఈ రోజు వెచ్చగా ఉంది", "hi": "आज गर्मी है"},
    "ws_temp_mild": {"en": "The weather is pleasant today", "te": "ఈ రోజు వాతావరణం ఆహ్లాదకరంగా ఉంది", "hi": "आज मौसम सुहावना है"},
    "ws_temp_cool": {"en": "It is cool today", "te": "ఈ రోజు చల్లగా ఉంది", "hi": "आज ठंड है"},
    "ws_rain_likely": {
        "en": "there is a good chance of rain",
        "te": "వర్షం పడే అవకాశం ఎక్కువగా ఉంది",
        "hi": "बारिश की अच्छी संभावना है",
    },
    "ws_rain_possible": {
        "en": "there is some chance of rain",
        "te": "కొంత వర్షం అవకాశం ఉంది",
        "hi": "थोड़ी बारिश की संभावना है",
    },
    "ws_rain_none": {
        "en": "rain is not expected",
        "te": "వర్షం పడే అవకాశం కనిపించలేదు",
        "hi": "बारिश की संभावना नहीं दिखती",
    },
    "ws_advice_rain": {
        "en": "Please check the forecast again before irrigating or spraying.",
        "te": "నీరు పెట్టే ముందు లేదా పిచికారీ చేసే ముందు మళ్లీ వాతావరణం చూడండి.",
        "hi": "सिंचाई या छिड़काव से पहले मौसम फिर से देख लें।",
    },
    "ws_advice_hot": {
        "en": "Work in the early morning or evening and drink enough water.",
        "te": "ఉదయం లేదా సాయంత్రం పని చేయండి మరియు తగినంత నీరు తాగండి.",
        "hi": "सुबह या शाम को काम करें और पर्याप्त पानी पिएं।",
    },
    "ws_advice_wind": {
        "en": "It is windy, so spraying may drift. Better to spray when the wind is calmer.",
        "te": "గాలి ఎక్కువగా ఉంది, పిచికారీ మందు ఎగిరిపోవచ్చు. గాలి తక్కువగా ఉన్నప్పుడు పిచికారీ చేయడం మంచిది.",
        "hi": "हवा तेज़ है, छिड़काव उड़ सकता है। हवा कम होने पर छिड़काव करना बेहतर है।",
    },
    "ws_advice_default": {
        "en": "Check the forecast again before irrigation or spraying.",
        "te": "నీరు పెట్టే ముందు లేదా పిచికారీ చేసే ముందు వాతావరణం మళ్లీ చూడండి.",
        "hi": "सिंचाई या छिड़काव से पहले मौसम फिर से देख लें।",
    },
    "alert_heavy_rain": {
        "en": "Heavy rain is forecast in the next few days. Avoid spraying and think about drainage in your field.",
        "te": "రాబోయే కొన్ని రోజుల్లో భారీ వర్షం అంచనా. పిచికారీ చేయవద్దు, పొలంలో నీరు పోయే మార్గం గురించి ఆలోచించండి.",
        "hi": "अगले कुछ दिनों में भारी बारिश का पूर्वानुमान है। छिड़काव न करें और खेत में पानी निकासी के बारे में सोचें।",
    },
    "alert_heat": {
        "en": "Very high temperature is forecast. Take care of yourself and your crop; ask your agriculture officer about heat protection.",
        "te": "చాలా ఎక్కువ ఉష్ణోగ్రత అంచనా. మీరు మరియు మీ పంట జాగ్రత్త; వేడి నుండి రక్షణ గురించి వ్యవసాయ అధికారిని అడగండి.",
        "hi": "बहुत अधिक तापमान का पूर्वानुमान है। अपना और फसल का ध्यान रखें; गर्मी से बचाव के बारे में कृषि अधिकारी से पूछें।",
    },
    "alert_wind": {
        "en": "Strong wind is forecast. Avoid spraying while it is windy.",
        "te": "బలమైన గాలి అంచనా. గాలి ఉన్నప్పుడు పిచికారీ చేయవద్దు.",
        "hi": "तेज़ हवा का पूर्वानुमान है। हवा चलते समय छिड़काव न करें।",
    },

    # ── Help / FAQ ─────────────────────────────────────────
    "help_title": {"en": "Ask for Help", "te": "సహాయం అడగండి", "hi": "मदद पूछें"},
    "help_intro": {
        "en": "Tap a question, or type your own below.",
        "te": "ఒక ప్రశ్నను నొక్కండి, లేదా కింద మీ ప్రశ్నను టైప్ చేయండి.",
        "hi": "किसी सवाल पर टैप करें, या नीचे अपना सवाल लिखें।",
    },
    "help_type": {"en": "Type your question", "te": "మీ ప్రశ్నను టైప్ చేయండి", "hi": "अपना सवाल लिखें"},
    "help_ask": {"en": "Ask", "te": "అడగండి", "hi": "पूछें"},
    "help_fallback": {
        "en": "Sorry, I do not have a reliable answer to that. Please ask your local agriculture officer, or call the Kisan Call Centre on 1800-180-1551 (toll free).",
        "te": "క్షమించండి, దీనికి నా దగ్గర నమ్మదగిన సమాధానం లేదు. దయచేసి మీ స్థానిక వ్యవసాయ అధికారిని అడగండి, లేదా కిసాన్ కాల్ సెంటర్ 1800-180-1551 (ఉచితం) కు ఫోన్ చేయండి.",
        "hi": "क्षमा करें, इसका मेरे पास भरोसेमंद उत्तर नहीं है। कृपया अपने स्थानीय कृषि अधिकारी से पूछें, या किसान कॉल सेंटर 1800-180-1551 (निःशुल्क) पर फ़ोन करें।",
    },
    "help_escalate": {
        "en": "For pest, disease or pesticide questions, please show the affected plant to your agriculture officer or KVK before spraying anything.",
        "te": "చీడపీడలు, తెగుళ్లు లేదా పురుగుమందుల ప్రశ్నలకు, ఏదైనా పిచికారీ చేసే ముందు దెబ్బతిన్న మొక్కను వ్యవసాయ అధికారికి లేదా KVK కి చూపించండి.",
        "hi": "कीट, रोग या कीटनाशक के सवालों के लिए, कुछ भी छिड़कने से पहले प्रभावित पौधा अपने कृषि अधिकारी या KVK को दिखाएं।",
    },
    "help_voice_note": {
        "en": "Voice input is not available yet. Please type your question.",
        "te": "వాయిస్ ఇన్‌పుట్ ఇంకా అందుబాటులో లేదు. దయచేసి మీ ప్రశ్నను టైప్ చేయండి.",
        "hi": "वॉइस इनपुट अभी उपलब्ध नहीं है। कृपया अपना सवाल लिखें।",
    },

    # ── History ────────────────────────────────────────────
    "history_title": {"en": "My earlier advice", "te": "నా మునుపటి సలహాలు", "hi": "मेरी पिछली सलाह"},
    "history_empty": {
        "en": "Nothing here yet. When you ask for crop advice it will show here.",
        "te": "ఇక్కడ ఇంకా ఏమీ లేదు. మీరు పంట సలహా అడిగితే ఇక్కడ కనిపిస్తుంది.",
        "hi": "यहाँ अभी कुछ नहीं है। फसल सलाह लेने पर वह यहाँ दिखेगी।",
    },
    "history_note": {
        "en": "This list is kept only while this page is open. It is not saved on any server.",
        "te": "ఈ జాబితా ఈ పేజీ తెరిచి ఉన్నంత వరకే ఉంటుంది. ఏ సర్వర్‌లోనూ భద్రపరచబడదు.",
        "hi": "यह सूची केवल तब तक रहती है जब तक यह पेज खुला है। यह किसी सर्वर पर सेव नहीं होती।",
    },
    "clear": {"en": "Clear list", "te": "జాబితా తొలగించండి", "hi": "सूची साफ़ करें"},

    # ── Settings ───────────────────────────────────────────
    "settings_title": {"en": "Settings", "te": "సెట్టింగ్స్", "hi": "सेटिंग्स"},
    "bigger_text": {"en": "Larger text", "te": "పెద్ద అక్షరాలు", "hi": "बड़े अक्षर"},
    "saved": {"en": "Saved", "te": "భద్రపరచబడింది", "hi": "सेव हो गया"},

    # ── Resources ──────────────────────────────────────────
    "resources_title": {"en": "Official help", "te": "అధికారిక సహాయం", "hi": "आधिकारिक सहायता"},
    "res_kisan": {
        "en": "Kisan Call Centre: 1800-180-1551 (toll free)",
        "te": "కిసాన్ కాల్ సెంటర్: 1800-180-1551 (ఉచితం)",
        "hi": "किसान कॉल सेंटर: 1800-180-1551 (निःशुल्क)",
    },
    "res_shc": {"en": "Soil Health Card portal", "te": "సాయిల్ హెల్త్ కార్డ్ పోర్టల్", "hi": "सॉयल हेल्थ कार्ड पोर्टल"},
    "res_kvk": {"en": "Find your Krishi Vigyan Kendra (ICAR)", "te": "మీ కృషి విజ్ఞాన కేంద్రం కనుగొనండి (ICAR)", "hi": "अपना कृषि विज्ञान केंद्र खोजें (ICAR)"},

    # ── Tabs & Agent Navigation ────────────────────────────
    "tab_daily_plan": {"en": "📋 Daily Plan", "te": "📋 రోజువారీ ప్రణాళిక", "hi": "📋 दैनिक योजना"},
    "tab_soil": {"en": "🧪 Soil Health", "te": "🧪 నేల ఆరోగ్యం", "hi": "🧪 मिट्टी स्वास्थ्य"},
    "tab_water": {"en": "💧 Irrigation", "te": "💧 నీటిపారుదల", "hi": "💧 सिंचाई"},
    "tab_pests": {"en": "🐛 Pest Alert", "te": "🐛 చీడపీడల హెచ్చరిక", "hi": "🐛 कीट चेतावनी"},
    "tab_yield": {"en": "📈 Yield Forecast", "te": "📈 దిగుబడి అంచనా", "hi": "📈 उपज का अनुमान"},
    "tab_fertilizer": {"en": "🧬 Fertilizer Plan", "te": "🧬 ఎరువుల ప్రణాళిక", "hi": "🧬 खाद योजना"},
    "tab_harvest": {"en": "🌾 Harvest Guide", "te": "🌾 పంట కోత మార్గదర్శి", "hi": "🌾 कटाई गाइड"},
    "tab_market": {"en": "💰 Mandi Prices", "te": "💰 మార్కెట్ ధరలు", "hi": "💰 मंडी भाव"},
    "tab_leaf_scan": {"en": "📸 Leaf Scan", "te": "📸 ఆకు స్కాన్", "hi": "📸 पत्ती स्कैन"},
    "tab_what_if": {"en": "🔮 What-If Simulator", "te": "🔮 ఏమి జరుగుతుంది సిమ్యులేటర్", "hi": "🔮 'अगर ऐसा हो' सिम्युलेटर"},
    "tab_help": {"en": "💬 Farmer Help & FAQs", "te": "💬 రైతు సహాయం & ప్రశ్నలు", "hi": "💬 किसान सहायता और सवाल"},
    "tab_calendar": {"en": "📅 Crop Calendar", "te": "📅 పంట క్యాలెండర్", "hi": "📅 फसल कैलेंडर"},
    "tab_schemes": {"en": "🏛️ Govt Schemes", "te": "🏛️ ప్రభుత్వ పథకాలు", "hi": "🏛️ सरकारी योजनाएं"},
    "tab_history": {"en": "📜 Farming History", "te": "📜 వ్యవసాయ చరిత్ర", "hi": "📜 खेती का इतिहास"},
    "tab_analytics": {"en": "📊 Analytics & ML", "te": "📊 విశ్లేషణ & ML వివరాలు", "hi": "📊 विश्लेषण और ML"},

    # ── Metrics & Card Labels ──────────────────────────────
    "water_needed": {"en": "Water Needed", "te": "అవసరమైన నీరు", "hi": "ज़रूरी पानी"},
    "pump_hours": {"en": "Pump Hours", "te": "మోటార్ నడిచే గంటలు", "hi": "पंप चलने के घंटे"},
    "pump_cost": {"en": "Cost Today", "te": "ఈ రోజు ఖర్చు", "hi": "आज का खर्च"},
    "money_saved": {"en": "Saved Today", "te": "ఆదా అయిన మొత్తం", "hi": "आज की बचत"},
    "yield_per_acre": {"en": "Yield per Acre", "te": "ఎకరాకు దిగుబడి", "hi": "प्रति एकड़ उपज"},
    "total_yield": {"en": "Total Yield", "te": "మొత్తం దిగుబడి", "hi": "कुल उपज"},
    "expected_revenue": {"en": "Expected Revenue", "te": "ఆశించే ఆదాయం", "hi": "अनुमानित आय"},
    "storage_needed": {"en": "Storage Needed", "te": "నిల్వ సామర్థ్యం", "hi": "ज़रूरी भंडारण"},
    "best_mandi": {"en": "Best Mandi", "te": "అత్యుత్తమ మార్కెట్", "hi": "सर्वश्रेष्ठ मंडी"},
    "best_price": {"en": "Best Price", "te": "ఉత్తమ ధర", "hi": "सर्वश्रेष्ठ भाव"},
    "vs_msp": {"en": "vs MSP", "te": "కనీస మద్దతు ధరతో పోలిస్తే", "hi": "MSP की तुलना में"},
    "urea_dose": {"en": "Urea needed", "te": "అవసరమైన యూరియా", "hi": "ज़रूरी यूरिया"},
    "dap_dose": {"en": "DAP needed", "te": "అవసరమైన డీఏపీ", "hi": "ज़रूरी डीएपी"},
    "mop_dose": {"en": "MOP needed", "te": "అవసరమైన ఎంఓపీ (పొటాష్)", "hi": "ज़रूरी एमओपी"},
    "total_cost": {"en": "Total Fertilizer Cost", "te": "మొత్తం ఎరువుల ఖర్చు", "hi": "कुल खाद खर्च"},
    "cost_without_ai": {"en": "Without AI (Guessing)", "te": "అంచనా వేస్తే ఖర్చు", "hi": "अंदाजे से खर्च"},
    "you_save_ai": {"en": "You Save with AI", "te": "AI తో మీరు ఆదా చేసే మొత్తం", "hi": "AI से आपकी बचत"},
    "days_to_harvest": {"en": "Days to Harvest", "te": "కోతకు మిగిలిన రోజులు", "hi": "कटाई के बाकी दिन"},
    "mandi_price": {"en": "Mandi Price", "te": "మార్కెట్ ధర", "hi": "मंडी भाव"},
    "msp_price": {"en": "MSP (Min Support Price)", "te": "కనీస మద్దతు ధర (MSP)", "hi": "न्यूनतम समर्थन मूल्य (MSP)"},
    "soil_health_score": {"en": "Soil Health Score", "te": "నేల ఆరోగ్య స్కోరు", "hi": "मिट्टी स्वास्थ्य स्कोर"},
    "soil_ph_label": {"en": "Soil pH", "te": "నేల pH", "hi": "मिट्टी pH"},
    "organic_matter_lbl": {"en": "Organic Matter", "te": "సేంద్రీయ పదార్థం", "hi": "जैविक पदार्थ"},

    # ── Voice Assistant ────────────────────────────────────
    "voice_mic_btn": {"en": "🎤 Tap to Ask by Voice", "te": "🎤 వాయిస్ ద్వారా అడగండి", "hi": "🎤 बोलकर पूछें"},
    "voice_speak_now": {"en": "🎤 Speak now... I am listening", "te": "🎤 ఇప్పుడు మాట్లాడండి... నేను వింటున్నాను", "hi": "🎤 अब बोलिए... मैं सुन रहा हूँ"},
    "voice_read_aloud": {"en": "🔊 Listen to Advice", "te": "🔊 సలహాను వినండి", "hi": "🔊 सलाह सुनें"},
    "voice_stop": {"en": "⏹️ Stop Audio", "te": "⏹️ ఆపండి", "hi": "⏹️ रोकें"},
    "voice_unsupported": {"en": "Voice is not supported in this browser. Please type your query.", "te": "ఈ బ్రౌజర్‌లో వాయిస్ పని చేయదు. దయచేసి టైప్ చేయండి.", "hi": "इस ब्राउज़र में वॉइस काम नहीं करता। कृपया लिखकर पूछें।"},

    # ── Quick Actions ──────────────────────────────────────
    "qa_crop_rec": {"en": "🌾 Crop Advice", "te": "🌾 పంట సలహా", "hi": "🌾 फसल सलाह"},
    "qa_fert_guide": {"en": "🧬 Fertilizer Plan", "te": "🧬 ఎరువుల ప్రణాళిక", "hi": "🧬 खाद योजना"},
    "qa_weather_rep": {"en": "🌤️ Weather", "te": "🌤️ వాతావరణం", "hi": "🌤️ मौसम"},
    "qa_leaf_doctor": {"en": "📸 Leaf Doctor", "te": "📸 ఆకు డాక్టర్", "hi": "📸 पत्ती डॉक्टर"},
    "qa_ask_expert": {"en": "💬 Ask Expert", "te": "💬 నిపుణుడిని అడగండి", "hi": "💬 विशेषज्ञ से पूछें"},
}


def t(key: str, lang: str = DEFAULT_LANG, **kwargs) -> str:
    """Translate `key` into `lang`, with safe fallbacks. Never raises."""
    entry = STRINGS.get(key)
    if not entry:
        return key
    text = entry.get(lang) or entry.get("en") or key
    if kwargs:
        try:
            return text.format(**kwargs)
        except (KeyError, IndexError, ValueError):
            return text
    return text


def crop_name(crop: str, lang: str, crops_db: dict) -> str:
    """Crop name in the chosen language, using the existing crop database."""
    if lang == "en":
        return crop
    info = crops_db.get(crop, {})
    return info.get("telugu" if lang == "te" else "hindi") or crop


def missing_keys():
    """Developer helper: keys missing a translation in any language."""
    return {k: [l for l in LANGUAGES if not v.get(l)] for k, v in STRINGS.items()
            if any(not v.get(l) for l in LANGUAGES)}


# ══════════════════════════════════════════════════════════════
#  v11 additions (appended — nothing above was changed or removed)
#  New screens: Weather, My Farming History, Settings, API Status
# ══════════════════════════════════════════════════════════════
STRINGS.update({
    "tab_weather": {"en": "🌤️ Weather", "te": "🌤️ వాతావరణం", "hi": "🌤️ मौसम"},
    "tab_my_history": {"en": "📜 My Farming History", "te": "📜 నా వ్యవసాయ చరిత్ర", "hi": "📜 मेरी खेती का इतिहास"},
    "tab_settings": {"en": "⚙️ Settings", "te": "⚙️ సెట్టింగ్‌లు", "hi": "⚙️ सेटिंग्स"},
    "tab_api_status": {"en": "🔌 API Status", "te": "🔌 API స్థితి", "hi": "🔌 API स्थिति"},

    # Quick actions (home)
    "x_quick_title": {"en": "What do you want to do?", "te": "మీరు ఏమి చేయాలనుకుంటున్నారు?", "hi": "आप क्या करना चाहते हैं?"},
    "x_qa_crop": {"en": "Which crop to grow?", "te": "ఏ పంట వేయాలి?", "hi": "कौन सी फसल बोएँ?"},
    "x_qa_fert": {"en": "How much fertilizer?", "te": "ఎంత ఎరువు వేయాలి?", "hi": "कितनी खाद डालें?"},
    "x_qa_weather": {"en": "Today's weather", "te": "ఈ రోజు వాతావరణం", "hi": "आज का मौसम"},
    "x_qa_help": {"en": "Ask for help", "te": "సహాయం అడగండి", "hi": "मदद माँगें"},
    "x_qa_open_tab": {"en": "Open the tab", "te": "ఈ ట్యాబ్ తెరవండి", "hi": "यह टैब खोलें"},

    # Weather screen
    "x_wx_now": {"en": "Right now", "te": "ప్రస్తుతం", "hi": "अभी"},
    "x_wx_high": {"en": "Today's high", "te": "ఈ రోజు గరిష్ఠం", "hi": "आज का अधिकतम"},
    "x_wx_low": {"en": "Today's low", "te": "ఈ రోజు కనిష్ఠం", "hi": "आज का न्यूनतम"},
    "x_wx_wind": {"en": "Wind", "te": "గాలి వేగం", "hi": "हवा की गति"},
    "x_wx_forecast": {"en": "Next days forecast", "te": "రాబోయే రోజుల అంచనా", "hi": "आने वाले दिनों का अनुमान"},
    "x_wx_date": {"en": "Date", "te": "తేదీ", "hi": "तारीख"},
    "x_wx_rain_mm": {"en": "Rain (mm)", "te": "వర్షం (మి.మీ)", "hi": "बारिश (मि.मी)"},
    "x_wx_unavailable": {
        "en": "Weather is not available right now. Please check your internet and try again. No guessed numbers are shown.",
        "te": "ప్రస్తుతం వాతావరణ సమాచారం అందుబాటులో లేదు. ఇంటర్నెట్ చూసి మళ్లీ ప్రయత్నించండి. ఊహించిన సంఖ్యలు చూపించబడవు.",
        "hi": "अभी मौसम की जानकारी उपलब्ध नहीं है। कृपया इंटरनेट जाँचकर फिर कोशिश करें। अनुमानित आँकड़े नहीं दिखाए जाते।",
    },
    "x_wx_stale": {
        "en": "This is OLD weather data from {m} minutes ago (internet problem). Do not treat it as live.",
        "te": "ఇది {m} నిమిషాల క్రితం నాటి పాత వాతావరణ సమాచారం (ఇంటర్నెట్ సమస్య). దీన్ని ప్రత్యక్ష సమాచారంగా భావించవద్దు.",
        "hi": "यह {m} मिनट पुराना मौसम डेटा है (इंटरनेट की समस्या)। इसे लाइव न समझें।",
    },
    "x_wx_not_config": {
        "en": "Weather key is not set. Add OPENWEATHER_API_KEY in the .env file.",
        "te": "వాతావరణ కీ సెట్ చేయలేదు. .env ఫైల్‌లో OPENWEATHER_API_KEY జోడించండి.",
        "hi": "मौसम की कुंजी सेट नहीं है। .env फ़ाइल में OPENWEATHER_API_KEY जोड़ें।",
    },
    "x_wx_refresh": {"en": "🔄 Refresh weather", "te": "🔄 వాతావరణం రిఫ్రెష్ చేయండి", "hi": "🔄 मौसम रीफ़्रेश करें"},
    "x_wx_credit": {
        "en": "Weather data: OpenWeatherMap. Forecasts are estimates, not guarantees.",
        "te": "వాతావరణ సమాచారం: OpenWeatherMap. అంచనాలు కేవలం అంచనాలే, హామీ కాదు.",
        "hi": "मौसम डेटा: OpenWeatherMap। पूर्वानुमान केवल अनुमान हैं, गारंटी नहीं।",
    },
    "x_unavailable": {"en": "Not available", "te": "అందుబాటులో లేదు", "hi": "उपलब्ध नहीं"},

    # History screen
    "x_hist_intro": {
        "en": "Your earlier farm advice is saved on this computer, so it is still here after you close the app.",
        "te": "మీ గత వ్యవసాయ సలహాలు ఈ కంప్యూటర్‌లో భద్రపరచబడతాయి, యాప్ మూసినా అవి ఇక్కడే ఉంటాయి.",
        "hi": "आपकी पिछली खेती की सलाह इस कंप्यूटर में सुरक्षित रहती है, ऐप बंद करने पर भी यहीं मिलेगी।",
    },
    "x_hist_empty": {
        "en": "No saved advice yet. Your first farm advice will appear here.",
        "te": "ఇంకా సలహాలు ఏవీ భద్రపరచలేదు. మీ మొదటి సలహా ఇక్కడ కనిపిస్తుంది.",
        "hi": "अभी कोई सलाह सुरक्षित नहीं है। आपकी पहली सलाह यहाँ दिखेगी।",
    },
    "x_hist_download": {"en": "⬇️ Download history (CSV)", "te": "⬇️ చరిత్రను డౌన్‌లోడ్ చేయండి (CSV)", "hi": "⬇️ इतिहास डाउनलोड करें (CSV)"},
    "x_hist_clear": {"en": "🗑️ Delete all my saved history", "te": "🗑️ నా చరిత్ర మొత్తం తొలగించండి", "hi": "🗑️ मेरा पूरा इतिहास हटाएँ"},
    "x_hist_confirm": {"en": "Yes, I am sure", "te": "అవును, నాకు ఖచ్చితంగా తెలుసు", "hi": "हाँ, मुझे पक्का पता है"},
    "x_hist_cleared": {"en": "History deleted.", "te": "చరిత్ర తొలగించబడింది.", "hi": "इतिहास हटा दिया गया।"},
    "x_hist_total": {"en": "Saved entries", "te": "భద్రపరచిన నమోదులు", "hi": "सुरक्षित प्रविष्टियाँ"},

    # Settings screen
    "x_set_intro": {"en": "Choose how the app looks and works for you. Your choices are remembered.",
                    "te": "యాప్ మీకు ఎలా కనిపించాలో ఎంచుకోండి. మీ ఎంపికలు గుర్తుంచుకోబడతాయి.",
                    "hi": "ऐप आपको कैसा दिखे यह चुनें। आपकी पसंद याद रखी जाएगी।"},
    "x_set_lang": {"en": "Language", "te": "భాష", "hi": "भाषा"},
    "x_set_large": {"en": "Bigger text", "te": "పెద్ద అక్షరాలు", "hi": "बड़े अक्षर"},
    "x_set_contrast": {"en": "High contrast (easier to read in sunlight)", "te": "అధిక కాంట్రాస్ట్ (ఎండలో చదవడానికి సులభం)", "hi": "उच्च कंट्रास्ट (धूप में पढ़ना आसान)"},
    "x_set_dev": {"en": "Developer view (show model accuracy numbers)", "te": "డెవలపర్ వీక్షణ (మోడల్ ఖచ్చితత్వ సంఖ్యలు చూపండి)", "hi": "डेवलपर व्यू (मॉडल सटीकता के आँकड़े दिखाएँ)"},
    "x_set_saved": {"en": "Saved ✔", "te": "భద్రపరచబడింది ✔", "hi": "सुरक्षित ✔"},
    "x_set_privacy": {
        "en": "Privacy: your history and settings stay only in the folder data/user_data on this computer.",
        "te": "గోప్యత: మీ చరిత్ర మరియు సెట్టింగ్‌లు ఈ కంప్యూటర్‌లోని data/user_data ఫోల్డర్‌లో మాత్రమే ఉంటాయి.",
        "hi": "गोपनीयता: आपका इतिहास और सेटिंग्स केवल इस कंप्यूटर के data/user_data फ़ोल्डर में रहती हैं।",
    },

    # API status screen
    "x_api_intro": {
        "en": "This checks whether each online service is really answering (not just whether a key is typed in).",
        "te": "ప్రతి ఆన్‌లైన్ సేవ నిజంగా స్పందిస్తోందా అని ఇది తనిఖీ చేస్తుంది (కేవలం కీ ఉందా అని కాదు).",
        "hi": "यह जाँचता है कि हर ऑनलाइन सेवा सच में जवाब दे रही है या नहीं (सिर्फ़ कुंजी होना काफ़ी नहीं)।",
    },
    "x_api_check": {"en": "🔍 Check all 3 APIs now", "te": "🔍 3 APIలను ఇప్పుడే తనిఖీ చేయండి", "hi": "🔍 तीनों API अभी जाँचें"},
    "x_api_not_checked": {"en": "Not checked yet. Press the button.", "te": "ఇంకా తనిఖీ చేయలేదు. బటన్ నొక్కండి.", "hi": "अभी जाँच नहीं हुई। बटन दबाएँ।"},
    "x_api_working": {"en": "Working", "te": "పని చేస్తోంది", "hi": "काम कर रहा है"},
    "x_api_not_working": {"en": "Not working", "te": "పని చేయడం లేదు", "hi": "काम नहीं कर रहा"},
})

# ── v12 UI redesign strings (appended) ─────────────────────────
STRINGS.update({
    "sec_farm": {"en": "🚜 My Farm Tools", "te": "🚜 నా వ్యవసాయ పనిముట్లు", "hi": "🚜 मेरे खेत के औज़ार"},
    "sec_more": {"en": "⚙️ More & Settings", "te": "⚙️ మరిన్ని & సెట్టింగ్‌లు", "hi": "⚙️ और भी & सेटिंग्स"},
    "x_howto_title": {"en": "How to use this app (3 easy steps)", "te": "ఈ యాప్ ఎలా వాడాలి (3 సులభమైన దశలు)", "hi": "इस ऐप का उपयोग कैसे करें (3 आसान चरण)"},
    "x_howto_1": {"en": "Fill your farm details in the left panel (tap the arrow ›  at top-left on a phone).",
                  "te": "ఎడమ వైపు ప్యానెల్‌లో మీ పొలం వివరాలు నింపండి (ఫోన్‌లో పైన ఎడమవైపు ›  బాణం నొక్కండి).",
                  "hi": "बाएँ पैनल में अपने खेत की जानकारी भरें (फ़ोन में ऊपर बाईं ओर › तीर दबाएँ)।"},
    "x_howto_2": {"en": "Read today's plan on this page. Use the big tabs above for more details.",
                  "te": "ఈ పేజీలో ఈ రోజు ప్రణాళిక చదవండి. మరిన్ని వివరాలకు పైన ఉన్న పెద్ద ట్యాబ్‌లు వాడండి.",
                  "hi": "इस पेज पर आज की योजना पढ़ें। और जानकारी के लिए ऊपर के बड़े टैब इस्तेमाल करें।"},
    "x_howto_3": {"en": "Need help? Open 💬 Help and ask in your language, or call Kisan Call Centre 1800-180-1551.",
                  "te": "సహాయం కావాలా? 💬 సహాయం తెరిచి మీ భాషలో అడగండి, లేదా కిసాన్ కాల్ సెంటర్ 1800-180-1551 కి కాల్ చేయండి.",
                  "hi": "मदद चाहिए? 💬 सहायता खोलें और अपनी भाषा में पूछें, या किसान कॉल सेंटर 1800-180-1551 पर कॉल करें।"},
    "x_side_farm": {"en": "My farm", "te": "నా పొలం", "hi": "मेरा खेत"},
    "x_side_soil": {"en": "Soil details (from Soil Health Card)", "te": "నేల వివరాలు (సాయిల్ హెల్త్ కార్డ్ నుండి)", "hi": "मिट्टी की जानकारी (सॉयल हेल्थ कार्ड से)"},
    "x_side_crop": {"en": "Crop condition today", "te": "ఈ రోజు పంట పరిస్థితి", "hi": "आज फसल की स्थिति"},
})
