# -*- coding: utf-8 -*-
from flask import Flask, request, jsonify, render_template
import re, time, json, os

app = Flask(__name__)

# ── Word Map ──
WORD_MAP = {
    "lessee":"renter","lessor":"landlord","indemnify":"pay for",
    "indemnification":"payment for damages","pursuant to":"according to",
    "aforementioned":"mentioned above","hereinafter":"from now on",
    "herein":"in this document","thereof":"of that","therein":"in that",
    "whereby":"by which","notwithstanding":"despite","forthwith":"immediately",
    "henceforth":"from this point on","heretofore":"until now",
    "in accordance with":"following","null and void":"invalid",
    "force majeure":"unexpected event beyond control","bona fide":"genuine",
    "inter alia":"among other things","prima facie":"at first glance",
    "de facto":"in practice","ab initio":"from the beginning",
    "covenant":"agreement","tort":"wrongful act",
    "plaintiff":"person who filed the case","defendant":"person being accused",
    "affidavit":"written sworn statement","subpoena":"legal order to appear",
    "injunction":"court order to stop something","litigation":"legal dispute in court",
    "arbitration":"settling dispute outside court","jurisdiction":"legal authority",
    "statute":"written law","adjudicate":"make a legal decision",
    "indictment":"formal criminal charge","acquittal":"being found not guilty",
    "restitution":"repayment for harm done","liability":"legal responsibility",
    "negligence":"failure to take proper care","breach":"violation",
    "remedy":"solution or compensation","damages":"money paid for harm",
    "waiver":"giving up a right","collateral":"property used as loan security",
    "default":"failure to meet obligation","fiduciary":"person trusted to act for another",
    "warranty":"guarantee of quality","disclosure":"sharing of information",
    "rescind":"cancel an agreement","void":"not legally valid",
    "consideration":"something of value exchanged in a contract",
    "stipulation":"specific requirement","obligation":"duty",
    "penalty":"punishment or fine","sanction":"official penalty",
    "compliance":"following the rules","violation":"breaking a rule",
    "premises":"property","dwelling":"home","occupancy":"use of a property",
    "eviction":"legally removing a tenant","tenancy":"renting arrangement",
}

ABBREVIATIONS = {"mr","mrs","ms","dr","prof","sr","jr","vs","etc","no","art","sec"}

# ── Amharic Word Map ──
WORD_MAP_AM = {
    "ተከራዩ": "ቤቱን የሚከራይ ሰው",
    "አከራዩ": "ቤቱን ያከራየ ባለቤት",
    "ኢንደምኒፋይ": "ካሳ መክፈል",
    "ኢንደምኒፊኬሽን": "የካሳ ክፍያ",
    "ዋስትና": "የብድር ዋስ",
    "ኪሳራ": "ጉዳት",
    "ሕጋዊ ኃላፊነት": "ሕጋዊ ግዴታ",
    "ቅጣት": "የሕግ ቅጣት",
    "ማስረጃ": "ማስረጃ ሰነድ",
    "ውል": "ስምምነት",
    "ፍርድ ቤት": "ፍርድ ቤት",
    "ይግባኝ": "ይግባኝ ጥያቄ",
    "ጥሰት": "ሕግ መጣስ",
    "ፍቃድ": "ፈቃድ",
    "ማስጠንቀቂያ": "ቅድሚያ ማሳወቂያ",
    "ስምምነት": "ዋጋ ያለው ልውውጥ",
    "ፍርድ": "ፍርድ ውሳኔ",
    "ሕጋዊ": "በሕግ የተደነገገ",
    "አዋጅ": "ሕጋዊ አዋጅ",
    "ሕገ መንግሥት": "የሀገር ዋና ሕግ",
}

# ── Afaan Oromo Word Map ──
WORD_MAP_OR = {
    "kireeffataa": "namni mana kireeffate",
    "kireessaa": "abbaa manaa",
    "beenyaa": "kaffalti miidhaa",
    "waliigaltee": "waliigaltee seera qabeessa",
    "adabbii": "adabbii seeraa",
    "mirga": "mirga seeraan kenname",
    "dhorkaa": "seeraan dhorkaame",
    "labsii": "labsii mootummaa",
    "heera": "heera mootummaa",
    "mana murtii": "mana murtii",
    "iyyannoo": "iyyannoo dhiyeessuu",
    "beeksisa": "beeksisa duraa",
    "seera": "seera biyyaa",
    "ragaa": "ragaa ragachiisaa",
    "waligaltee": "waligaltee haqaa qabu",
    "himatamaa": "namni himatame",
    "himattuu": "namni himatichi",
    "murtii": "murtii mana murtii",
    "hidhaa": "mana hidhaatti erguu",
    "bilisummaa": "bilisummaa dhuunfaa",
}

RULES = [
    {"keywords":["landlord","enter","room","permission"],"topic":"Tenant Rights – Landlord Entry",
     "law":"Ethiopian Civil Code",
     "answer":"Your landlord CANNOT enter your rented space without your permission, except in emergencies.\n\n• They must give you advance notice (24–48 hours).\n• Entering without notice may be considered trespass.\n• You have the right to peaceful enjoyment of your rented space.\n\nLaw: Ethiopian Civil Code"},
    {"keywords":["break","contract"],"topic":"Contract Breach",
     "law":"Ethiopian Civil Code Art.1678",
     "answer":"Breaking a contract (breach) has legal consequences.\n\n• The other party may demand compensation.\n• They may take you to court.\n• The contract may be cancelled.\n\nLaw: Ethiopian Civil Code Art.1678-1690"},
    {"keywords":["traffic","fine","ticket"],"topic":"Traffic Fine & Appeal",
     "law":"Traffic Proclamation No.1151/2019",
     "answer":"You have the right to appeal a traffic fine.\n\n• File your appeal within the deadline on the notice.\n• Under Traffic Proclamation No. 1151/2019 you have the right to contest.\n• Keep copies of all documents.\n\nLaw: Ethiopian Traffic Proclamation No.1151/2019"},
    {"keywords":["suspend","suspension","school","university","student"],"topic":"Student Suspension Rights",
     "law":"Higher Education Proclamation No.1152/2019",
     "answer":"You cannot be suspended without a fair hearing.\n\n• You must receive written notice of the charges.\n• You have the right to present your defence.\n• Due process must be followed.\n\nLaw: Higher Education Proclamation No.1152/2019"},
    {"keywords":["deposit","landlord","keep","return","refund"],"topic":"Security Deposit",
     "law":"Ethiopian Civil Code",
     "answer":"Your landlord must return your deposit unless there is a valid reason.\n\n• Valid reasons: unpaid rent, damage beyond normal wear.\n• They must provide a written explanation for deductions.\n• You can take the matter to court if they refuse unfairly.\n\nLaw: Ethiopian Civil Code"},
    {"keywords":["right","arrest","police","detained"],"topic":"Rights When Arrested",
     "law":"Ethiopian Constitution Art.19",
     "answer":"Under Article 19 of the Ethiopian Constitution:\n\n• You must be told why you are being arrested.\n• You have the right to remain silent.\n• You have the right to a lawyer.\n• You must be brought before a court within 48 hours.\n• Torture is prohibited under Article 18.\n\nLaw: Ethiopian Constitution Art.19, Art.18"},
    {"keywords":["contract","sign","agreement","terms"],"topic":"Signing a Contract",
     "law":"Ethiopian Civil Code Art.1678",
     "answer":"Before signing any contract:\n\n• Read every clause carefully.\n• Never sign under pressure.\n• A contract is legally binding once signed.\n• You can request changes before signing.\n\nLaw: Ethiopian Civil Code Art.1678-1690"},
    {"keywords":["evict","eviction","kicked out"],"topic":"Eviction Rights",
     "law":"Ethiopian Civil Code",
     "answer":"A landlord cannot evict you without following proper legal process.\n\n• They must give written notice with a reason.\n• You have the right to contest the eviction.\n• Illegal eviction (changing locks, removing belongings) is not allowed.\n\nLaw: Ethiopian Civil Code"},
    {"keywords":["constitution","rights","freedom","liberty"],"topic":"Constitutional Rights",
     "law":"Ethiopian Constitution 1995",
     "answer":"The Ethiopian Constitution guarantees fundamental rights:\n\n• Right to life and liberty (Art.14, Art.17)\n• Right to equality (Art.25)\n• Right to freedom of expression (Art.29)\n• Right to education (Art.41)\n• Right to a fair trial (Art.20)\n\nLaw: Ethiopian Constitution 1995"},
    {"keywords":["wage","salary","pay","employer","employee","work"],"topic":"Employment Rights",
     "law":"Labour Proclamation No.1156/2019",
     "answer":"Under Labour Proclamation No. 1156/2019:\n\n• Your employer must pay you on time.\n• You are entitled to a written employment contract.\n• Unfair dismissal without notice can be challenged.\n• Safe working conditions are your right.\n\nLaw: Labour Proclamation No.1156/2019"},
    {"keywords":["loan","debt","borrow","repay","interest"],"topic":"Loans & Debt",
     "law":"Ethiopian Civil Code",
     "answer":"When taking a loan:\n\n• You must repay the amount plus agreed interest.\n• Defaulting can lead to legal action or seizure of collateral.\n• You have the right to a clear written loan agreement.\n\nLaw: Ethiopian Civil Code"},
    {"keywords":["marriage","marry","wedding","spouse"],"topic":"Marriage Law",
     "law":"Revised Family Code 2000",
     "answer":"Under the Ethiopian Revised Family Code 2000:\n\n• Minimum legal age of marriage is 18 for both men and women.\n• Child marriage is illegal and punishable.\n• Both parties must give free and full consent.\n\nLaw: Revised Family Code 2000, Criminal Code Art.648"},
    {"keywords":["divorce","separation","custody"],"topic":"Divorce & Family Law",
     "law":"Revised Family Code 2000",
     "answer":"Under the Ethiopian Revised Family Code 2000:\n\n• Either spouse may file for divorce.\n• The court divides marital property fairly.\n• Child custody is decided in the best interest of the child.\n• Maintenance may be ordered by the court.\n\nLaw: Revised Family Code 2000"},
    {"keywords":["theft","steal","stolen"],"topic":"Theft – Criminal Law",
     "law":"Ethiopian Criminal Code Art.665",
     "answer":"Under the Ethiopian Criminal Code Art.665:\n\n• Simple theft: up to 3 years imprisonment.\n• Aggravated theft (with weapons or organised): up to 15 years.\n• You have the right to report theft to the police.\n\nLaw: Ethiopian Criminal Code Art.665"},
    # ── AMHARIC RULES ──
    {"keywords":["አከራዩ","ክፍሌ","ፈቃድ","ሊገባ"],"topic":"የተከራይ መብት – አከራዩ መግባት",
     "law":"የኢትዮጵያ የፍትሐ ብሔር ሕግ",
     "answer":"አከራዩ ያለ ፈቃድዎ ሊገባ አይችልም፣ ድንገተኛ አደጋ ካልሆነ በስተቀር።\n\n• ቅድሚያ ማስጠንቀቂያ (24-48 ሰዓት) መስጠት አለበት።\n• ያለ ፈቃድ መግባት ሕገ ወጥ ነው።\n• ሰላምና ጸጥታ የማግኘት መብት አለዎት።\n\nሕግ፡ የኢትዮጵያ የፍትሐ ብሔር ሕግ"},
    {"keywords":["ትራፊክ","ቅጣት","ይግባኝ"],"topic":"የትራፊክ ቅጣት ይግባኝ",
     "law":"የትራፊክ አዋጅ ቁጥር 1151/2019",
     "answer":"የትራፊክ ቅጣት ይግባኝ ማለት ይቻላል።\n\n• ይግባኙን በማስጠንቀቂያ ወረቀቱ ላይ በተጠቀሰው ቀነ ገደብ ማቅረብ አለብዎት።\n• አዋጅ ቁጥር 1151/2019 ቅጣቱን የመቃወም መብት ይሰጣል።\n• ሁሉንም ሰነዶች ቅጂ ያስቀምጡ።\n\nሕግ፡ የትራፊክ አዋጅ ቁጥር 1151/2019"},
    {"keywords":["ከተያዝኩ","ፖሊስ","መብቶች","መታሰር"],"topic":"ሲታሰሩ ያሉዎት መብቶች",
     "law":"የኢትዮጵያ ሕገ መንግሥት አንቀጽ 19",
     "answer":"በኢትዮጵያ ሕገ መንግሥት አንቀጽ 19 መሠረት:\n\n• ምክንያቱ ወዲያውኑ መነገር አለበት።\n• ዝም የማለት መብት አለዎት።\n• ጠበቃ የማግኘት መብት አለዎት።\n• በ48 ሰዓት ውስጥ ፍርድ ቤት መቅረብ አለብዎት።\n\nሕግ፡ የኢትዮጵያ ሕገ መንግሥት አንቀጽ 19"},
    {"keywords":["ሠራተኛ","ሥራ","ደሞዝ","ቀጣሪ","ሊያሰናብት"],"topic":"የሠራተኛ መብቶች",
     "law":"የሠራተኛ አዋጅ ቁጥር 1156/2019",
     "answer":"በሠራተኛ አዋጅ ቁጥር 1156/2019 መሠረት:\n\n• ቀጣሪው ደሞዝ በወቅቱ መክፈል አለበት።\n• የጽሑፍ የሥራ ውል የማግኘት መብት አለዎት።\n• ፍትሃዊ ያልሆነ ሥራ ማቋረጥ ሊቃወሙ ይችላሉ።\n\nሕግ፡ የሠራተኛ አዋጅ ቁጥር 1156/2019"},
    {"keywords":["ተማሪ","ዩኒቨርሲቲ","ታገደ","ሊታገድ"],"topic":"የተማሪ መብቶች",
     "law":"የከፍተኛ ትምህርት አዋጅ ቁጥር 1152/2019",
     "answer":"ያለ ፍትሃዊ ችሎት ሊታገዱ አይችሉም።\n\n• ክሱ በጽሑፍ ሊነገርዎት ይገባል።\n• ጉዳዩን የማቅረብ ዕድል አለዎት።\n• ፍርድ ቤቱ ፍትሃዊ ሂደት መጠቀም አለበት።\n\nሕግ፡ የከፍተኛ ትምህርት አዋጅ ቁጥር 1152/2019"},
    {"keywords":["ዋስትና","ኪራይ","አከራዩ","ይዞ"],"topic":"የዋስትና ክፍያ",
     "law":"የኢትዮጵያ የፍትሐ ብሔር ሕግ",
     "answer":"አከራዩ ዋስትናዎን ሊይዝ የሚችለው ለልዩ ምክንያቶች ብቻ ነው።\n\n• ያልተከፈለ ኪራይ ወይም ከተለመደ ጉዳት በላይ ለሆነ ጉዳት ብቻ።\n• ለምን እንደያዘ በጽሑፍ ማስረዳት አለበት።\n• ካልተስማሙ ወደ ፍርድ ቤት ሊሄዱ ይችላሉ።\n\nሕግ፡ የኢትዮጵያ የፍትሐ ብሔር ሕግ"},
    # ── AFAAN OROMO RULES ──
    {"keywords":["kireessaa","seenuu","hayyama","kutaa"],"topic":"Mirga Kireeffataa – Seenuu Abbaa Manaa",
     "law":"Seeraa Sivil Itiyoophiyaa",
     "answer":"Abbaan manaa hayyama kee malee seenuu hin danda'u, yeroo balaa hatattamaa malee.\n\n• Beeksisa duraa (sa'aatii 24-48) kennuu qaba.\n• Hayyama malee seenuun seeraan ala dha.\n• Nageenya fi tasgabbii mana keetii mirga qabda.\n\nSeera: Seeraa Sivil Itiyoophiyaa"},
    {"keywords":["tiraafikaa","adabbii","iyyannoo"],"topic":"Adabbii Tiraafikaa fi Iyyannoo",
     "law":"Labsii Tiraafikaa Lak.1151/2019",
     "answer":"Adabbii tiraafikaa mormuun ni danda'ama.\n\n• Iyyannoo kee beeksisa irratti ibsame yeroo keessatti dhiyeessuu qabda.\n• Labsii 1151/2019 adabbii mormuuf mirga kenna.\n• Galmee hundaa koopiifi kuusi.\n\nSeera: Labsii Tiraafikaa Lak.1151/2019"},
    {"keywords":["qabame","poolisii","mirga","hidhame"],"topic":"Mirga Yeroo Qabamte",
     "law":"Heera Mootummaa Itiyoophiyaa Kw.19",
     "answer":"Heera Mootummaa Itiyoophiyaa Keewwata 19 jalatti:\n\n• Sababi siif himamuu qaba.\n• Mirga callisuu qabda.\n• Mirga abukaatoo argachuu qabda.\n• Sa'aatii 48 keessatti mana murtii dura dhihaachuu qabda.\n\nSeera: Heera Mootummaa Kw.19"},
    {"keywords":["hojjetaa","hojii","mindaa","qacaraa","kaasuu"],"topic":"Mirga Hojjetaa",
     "law":"Labsii Hojii Lak.1156/2019",
     "answer":"Labsii Hojii Lak.1156/2019 jalatti:\n\n• Qacaraan mindaa yeroon kaffaluu qaba.\n• Waliigaltee hojii barreeffamaa argachuuf mirga qabda.\n• Haqaan ala hojii irraa kaasuu mormuun ni danda'ama.\n\nSeera: Labsii Hojii Lak.1156/2019"},
    {"keywords":["barataa","yuunivarsiitii","uggurame","ugguramu"],"topic":"Mirga Barataa",
     "law":"Labsii Barnootaa Ol'aanaa Lak.1152/2019",
     "answer":"Dhaggeettii haqaa malee ugguramuu hin dandeessu.\n\n• Himatni kee barreeffamaan siif beeksifamuu qaba.\n• Deebii kennachuuf carraa argachuu qabda.\n• Mana murtiin haqaa qabeessa ta'uu qaba.\n\nSeera: Labsii Barnootaa Ol'aanaa Lak.1152/2019"},
    {"keywords":["kireessaa","kuusaa","kireeffannaa","deebi"],"topic":"Kuusaa Kireeffannaa",
     "law":"Seeraa Sivil Itiyoophiyaa",
     "answer":"Abbaan manaa kuusaa kee sababa haqaa qabuuf qofa qabachuu danda'a.\n\n• Kireeffannaa hin kaffalamne ykn miidhaa caalanaa rakkoo idilee.\n• Maaliif akka qabate barreeffamaan ibsuu qaba.\n• Yoo waliigaluu baattan mana murtiitti dhiyaachuu ni danda'ama.\n\nSeera: Seeraa Sivil Itiyoophiyaa"},
]

FALLBACK = "I'm sorry, I don't have a specific answer for that question.\n\nFor this legal matter I recommend:\n• Consulting a qualified lawyer.\n• Visiting the Ethiopian Legal Information Institute at ethlii.org.\n• Contacting your local court or legal aid office.\n\nRemember: LawPal provides general information only — not professional legal advice."

def split_sentences(text):
    parts = re.split(r'(?<=[.!?])\s+', text)
    merged, i = [], 0
    while i < len(parts):
        part = parts[i]
        last_word = part.rstrip('.').split('.')[-1].lower()
        if last_word in ABBREVIATIONS and i + 1 < len(parts):
            parts[i+1] = part + ' ' + parts[i+1]
        else:
            merged.append(part)
        i += 1
    return merged

def detect_lang(text):
    """Detect if text is Amharic, Afaan Oromo, or English."""
    amharic_chars = sum(1 for c in text if '\u1200' <= c <= '\u137f')
    if amharic_chars > 3:
        return 'am'
    oromo_keywords = ['kireeffataa','kireessaa','mana','beenyaa','labsii','heera','mirga','seera','waliigaltee']
    if any(w in text.lower() for w in oromo_keywords):
        return 'or'
    return 'en'

def simplify(text):
    start  = time.time()
    result = text
    lang   = detect_lang(text)

    # Pick correct word map
    if lang == 'am':
        wmap = WORD_MAP_AM
    elif lang == 'or':
        wmap = WORD_MAP_OR
    else:
        wmap = WORD_MAP

    # Replace terms (longest first)
    for phrase in sorted(wmap.keys(), key=len, reverse=True):
        pattern = re.compile(re.escape(phrase), re.IGNORECASE)
        repl    = wmap[phrase]
        result  = pattern.sub(
            lambda m, r=repl: r[0].upper() + r[1:] if m.group(0)[0].isupper() else r,
            result
        )

    # Clean formal openers (English)
    result = re.sub(r'^\s*(It is hereby|Be it known that|Know all men by these presents that)\s*', '', result, flags=re.IGNORECASE)

    sentences = [s.strip() for s in split_sentences(result) if s.strip()]
    result    = '\n'.join(sentences)

    return result, round(time.time() - start, 4)

def is_question(text):
    text = text.strip()
    if text.endswith('?'): return True
    return bool(re.match(r'^(what|how|can|could|do|does|is|are|will|should|who|when|where|why|am|has|have)\b', text, re.IGNORECASE))

def answer(text):
    start = time.time()
    tl = text.lower()
    best_score, best_rule = 0, None
    for rule in RULES:
        score = sum(1 for kw in rule["keywords"] if kw in tl)
        if score > best_score:
            best_score, best_rule = score, rule
    elapsed = round(time.time()-start, 4)
    if best_rule and best_score >= 1:
        return best_rule["topic"], best_rule["answer"], best_rule["law"], elapsed
    return "No Match", FALLBACK, "N/A", elapsed

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/simplify", methods=["POST"])
def api_simplify():
    data = request.get_json()
    text = data.get("text","").strip()
    if not text:
        return jsonify({"error":"No text provided"}), 400
    result, elapsed = simplify(text)
    return jsonify({"result": result, "elapsed": elapsed,
                    "words_in": len(text.split()), "words_out": len(result.split())})

@app.route("/api/ask", methods=["POST"])
def api_ask():
    data = request.get_json()
    text = data.get("text","").strip()
    if not text:
        return jsonify({"error":"No question provided"}), 400
    topic, ans, law, elapsed = answer(text)
    return jsonify({"topic": topic, "answer": ans, "law": law, "elapsed": elapsed})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=False, host="0.0.0.0", port=port)
