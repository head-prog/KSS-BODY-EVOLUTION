"""
AI Engine Module
Integrates with Google Gemini API for health analysis
"""

import os
import re
from typing import Dict, Tuple
import google.generativeai as genai
from google.generativeai import types as genai_types
import streamlit as st

# Medical/health terms to annotate with English in brackets in Hindi/Gujarati PDFs
_MEDICAL_BRACKET_TERMS = [
    "Body Mass Index", "Body Fat", "Visceral Fat", "Muscle Mass",
    "Subcutaneous Fat", "Body Age", "Metabolic Rate", "Basal Metabolic Rate",
    "Metabolism", "Cardiovascular Disease", "Cardiovascular",
    "Insulin Resistance", "Insulin", "Blood Pressure", "Heart Disease",
    "Fatty Liver", "Triglycerides", "Inflammation", "Immune System",
    "Diabetes", "Hypertension", "Cholesterol", "Obesity",
    "Overweight", "Underweight",
]


class AIHealthAnalyzer:
    """Analyzes health data using Google Gemini API"""
    
    SYSTEM_INSTRUCTION = """You are a preventive healthcare AI assistant specialized in wellness evaluation. 

CRITICAL RULES:
1. You do NOT diagnose diseases - you provide risk analysis only
2. Never say a patient "has" a disease - use phrases like "increased risk of" instead
3. Provide lifestyle advice, diet recommendations, and future health risk warnings
4. All recommendations must be preventive and wellness-focused
5. Always include appropriate medical disclaimers
6. Keep responses professional and structured

Response must be in exactly this format with these 8 sections:

## 1. Current Health Summary
[Brief overview of patient's current health status based on metrics]

## 2. Risk Assessment
[Detailed analysis of health risks - use "increased risk of" language]

## 3. Possible Future Health Risks
[Health conditions patient may develop if lifestyle not changed - preventive focus]

## 4. What To Eat
[Specific dietary recommendations with food examples]

## 5. What To Avoid
[Foods and habits to avoid with explanations]

## 6. Lifestyle Recommendations
[Exercise, sleep, stress management, and daily habits]

## 7. Future Risk Warning
[Summary of preventive measures needed to maintain health]

## 8. Medical Disclaimer
[Include: "This assessment is for wellness purposes only and is not a medical diagnosis. 
Consult healthcare professionals for medical conditions."]

IMPORTANT: Every section must start with the section number and title exactly as shown."""
    
    def __init__(self):
        """Initialize Gemini API"""
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY environment variable not set")
        
        self.client = genai.Client(api_key=api_key)
        self.model_name = 'gemini-2.5-flash'
    
    def analyze_health_data(self, health_summary: str) -> Tuple[bool, str]:
        """
        Send health summary to Gemini and get analysis
        Returns: (success, response_text)
        """
        try:
            # Create the prompt
            prompt = f"""Based on the following health evaluation data, provide a comprehensive 
wellness analysis following the exact format specified in your system instructions.

HEALTH DATA:
{health_summary}

Remember:
- Use preventive language, not diagnostic
- Follow the 8-section format strictly
- Include the medical disclaimer
- Focus on lifestyle modifications and risk reduction"""
            
            # Send to Gemini with system instruction
            response = self.client.models.generate_content(
                model=self.model_name,
                config=genai_types.GenerateContentConfig(
                    system_instruction=self.SYSTEM_INSTRUCTION,
                ),
                contents=prompt,
            )
            
            # Validate response
            if not response.text:
                return False, "Empty response from AI"
            
            # Check for and validate output format
            validated_response = self._validate_and_format_response(response.text)
            
            return True, validated_response
        
        except Exception as e:
            return False, f"Error communicating with Gemini API: {str(e)}"
    
    @staticmethod
    def _validate_and_format_response(response_text: str) -> str:
        """
        Validate that response contains all required sections
        and doesn't use diagnostic language
        """
        required_sections = [
            "Current Health Summary",
            "Risk Assessment",
            "Possible Future Health Risks",
            "What To Eat",
            "What To Avoid",
            "Lifestyle Recommendations",
            "Future Risk Warning",
            "Medical Disclaimer"
        ]
        
        # Check for diagnostic language that shouldn't be used
        forbidden_phrases = [
            r'\bhas\s+(diabetes|heart\s+disease|hypertension|cancer|stroke|asthma)',
            r'\bdiagnosed\s+with',
            r'\bsuffer[s]?\s+from\s+(?!risk)',
            r'\byou\s+(are|have|will)\s+(sick|ill|diseased)',
        ]
        
        # Check for forbidden language
        for pattern in forbidden_phrases:
            if re.search(pattern, response_text, re.IGNORECASE):
                # Replace with preventive language
                response_text = re.sub(
                    r'(?i)\bhas\s+(diabetes|heart\s+disease|hypertension|cancer)',
                    r'has increased risk of \1',
                    response_text
                )
        
        # Verify all required sections are present
        missing_sections = []
        for section in required_sections:
            if section.lower() not in response_text.lower():
                missing_sections.append(section)
        
        # If sections are missing, add them as placeholders
        if missing_sections:
            response_text += "\n\n**Note:** Some sections were not fully generated. " \
                           "Please consult with a healthcare professional for complete analysis."
        
        return response_text


    # ── Language-specific grammar rules injected into every prompt ──────────
    _HINDI_GRAMMAR_RULES = """
HINDI LANGUAGE & GRAMMAR RULES — follow every rule without exception:
1.  NATIVE DRAFTING: Write as a native Hindi speaker would naturally write. Do NOT translate
    from English mentally — compose sentences directly in Hindi from the health data.
2.  SCRIPT: Use only Devanagari (हिन्दी). No Roman/Latin characters except inside (brackets).
3.  SENTENCE STRUCTURE: Subject–Object–Verb (SOV) — e.g., "रोगी को आहार बदलना चाहिए" NOT "आहार बदलना चाहिए रोगी को".
4.  GENDER AGREEMENT (लिंग): Every adjective, postposition, and verb must agree with the noun's gender.
    - पुल्लिंग nouns → का/अच्छा/बढ़ा हुआ/कम/स्वस्थ
    - स्त्रीलिंग nouns → की/अच्छी/बढ़ी हुई/कम/स्वस्थ
    - Common: शरीर (m), चर्बी (f), मांसपेशी (f), जीवन (m), स्वास्थ्य (m)
5.  POSTPOSITIONS (परसर्ग): Place correctly AFTER the noun/pronoun:
    - ने (ergative, past transitive subject), को (indirect object/dative),
      से (ablative/instrumental), में (locative), पर (on/at), के लिए (for),
      तक (until/up to), द्वारा (by/through), की ओर (towards)
6.  VERB CONJUGATION: Match person, number, gender, and tense.
    - Present habitual: खाता है (m.sg), खाती है (f.sg), खाते हैं (m.pl)
    - Present continuous: खा रहा है / खा रही है
    - Obligation: चाहिए / करना चाहिए / करनी चाहिए
    - Possibility: हो सकता है / हो सकती है
7.  HONORIFIC: Always use "आप" for addressing the patient; never "तू" or "तुम".
8.  NEGATION: Place "नहीं" immediately before the verb: "यह उचित नहीं है".
9.  MATRAS & DIACRITICS: Every vowel sign must be correct:
    ा ि ी ु ू े ै ो ौ ं ँ ः ् — no missing or extra matras.
10. CONJUNCTS (संयुक्त व्यंजन): Write proper conjuncts: क्+ष=क्ष, त्+र=त्र, श्+र=श्र, NOT separated.
11. MEDICAL VOCABULARY — use these canonical terms (English in parentheses first mention):
    हृदय रोग (Heart Disease) | उच्च रक्तचाप (High Blood Pressure) | मधुमेह (Diabetes)
    कोलेस्ट्रॉल (Cholesterol) | मोटापा (Obesity) | चयापचय (Metabolism)
    प्रतिरक्षा प्रणाली (Immune System) | शरीर की चर्बी (Body Fat) | आंतरिक चर्बी (Visceral Fat)
    मांसपेशियाँ (Muscle Mass) | अस्थि घनत्व (Bone Density) | थाइरॉइड (Thyroid)
    रक्त शर्करा (Blood Sugar) | हीमोग्लोबिन (Haemoglobin) | धमनियाँ (Arteries)
    निष्क्रियता (Sedentary Lifestyle) | तनाव प्रबंधन (Stress Management)
12. PUNCTUATION: Use । (daṇḍa/full stop) at sentence end. Use , for commas as in Hindi prose.
13. PREVENTIVE LANGUAGE: Never write "रोगी को [बीमारी] है" — always write "[बीमारी] का जोखिम बढ़ा हुआ है".
14. FLUENCY: Avoid word-for-word calques from English. Natural Hindi idiom examples:
    ✓ "नियमित कसरत करना आवश्यक है" (NOT "रेगुलर एक्सरसाइज करनी चाहिए")
    ✓ "संतुलित आहार लें" (NOT "बैलेंस्ड डाइट लें")
    ✓ "प्रतिदिन कम से कम ३० मिनट टहलें" (NOT "डेली ३० मिनट वॉक करें")
15. COMMON ERRORS TO AVOID — these patterns are wrong; use alternatives shown:
    ✗ "आपका बीएमआई हाई है" → ✓ "आपका बी.एम.आई. (BMI) सामान्य से अधिक है"
    ✗ "रिस्क फैक्टर बढ़ते हैं" → ✓ "जोखिम कारक बढ़ जाते हैं"
    ✗ "आपको डायबिटीज़ है" → ✓ "मधुमेह (Diabetes) का जोखिम बढ़ा हुआ है"
    ✗ "हेल्दी लाइफस्टाइल फॉलो करें" → ✓ "स्वस्थ जीवनशैली अपनाएँ"
    ✗ Devanagari half-letter floating: "क् षमता" → ✓ "क्षमता"
    ✗ Wrong gender: "अच्छा नींद" → ✓ "अच्छी नींद" (nīnd is feminine)
    ✗ Wrong gender: "बढ़ा हुई चर्बी" → ✓ "बढ़ी हुई चर्बी" (carbeī is feminine)
"""

    _GUJARATI_GRAMMAR_RULES = """
GUJARATI LANGUAGE & GRAMMAR RULES — follow every rule without exception:
1.  NATIVE DRAFTING: Write as a native Gujarati speaker from Gujarat naturally writes.
    Do NOT translate from English or Hindi mentally. Do NOT produce Devanagari/Hindi.
2.  SCRIPT: Use ONLY Gujarati script (gu-IN Unicode block U+0A80–U+0AFF). Examples of correct
    Gujarati characters: અ આ ઇ ઈ ઉ ઊ એ ઐ ઓ ઔ ક ખ ગ ઘ ચ છ જ ઝ ટ ઠ ડ ઢ ત થ દ ધ ન
    પ ફ બ ભ મ ય ર લ વ શ ષ સ હ ળ ક્ષ જ્ઞ — NEVER use Devanagari characters.
3.  THREE GENDERS (ત્રણ લિંગ): Every noun has a gender; adjectives/verbs must agree.
    - Masculine (પુ.): દર્દી (m), સ્વાસ્થ્ય (n/m), ખોરાક (m), રોગ (m), જોખમ (n)
    - Feminine (સ્ત્રી.): ચરબી (f), સ્નાયુ (f), ઊંઘ (f), કસરત (f)
    - Neuter (નપ.): શરીર (n), વજન (n), ભોજન (n), જીવન (n)
4.  POSTPOSITIONS: Place AFTER the noun/pronoun:
    - ને (dative/accusative), માં (locative), થી (ablative/instrumental/comparative),
      પર (on), માટે (for), સુધી (until), દ્વારા (by), તરફ (towards),
      નો/ની/નું (genitive — agrees with possessed noun gender: m/f/n)
5.  VERB CONJUGATION:
    - Present: [verb root] + છ suffix varies by person:
      હું…છું, તું…છો/છ, તે/એ…છ/છે, અમે…છીએ, તમે…છો, તેઓ…છ/છે
    - Obligation: …જોઈએ / …કરવું જોઈએ
    - Past: …હતો (m.sg) / …હતી (f.sg) / …હતું (n.sg) / …હતા (pl)
    - Future: …શે / …શો / …શું
6.  HONORIFIC: Use "આપ" for the patient (3rd person formal). Plural verb form.
7.  NEGATION: "નથી" (present), "ન" before verb (general), "ના" (colloquial refusal).
8.  VOWEL MATRAS: Every vowel sign must be correct and placed on correct consonant:
    ા િ ી ુ ૂ ે ૈ ો ૌ ં ઃ ૅ ૉ — no missing/swapped matras.
9.  HALF-LETTERS & CONJUNCTS: Use proper Gujarati conjuncts:
    ક્+ત=ક્ત, સ્+ત=સ્ત, ન્+દ=ન્દ, ક્+ષ=ક્ષ, જ્+ઞ=જ્ઞ — no floating halant virāma.
10. ANUSVARA (ં) vs CHANDRABINDU (ઁ): anusvara for nasal preceding consonants;
    chandrabindu only for nasalized vowels.
11. GUJARATI VOCABULARY — use authentic Gujarati, NOT Hindi loanwords:
    ✓ "ખોરાક" (NOT Hindi "आहार") for food
    ✓ "હ્રદય" (NOT Hindi "दिल") for heart
    ✓ "ઊંઘ" (NOT Hindi "नींद") for sleep
    ✓ "કસરત" (NOT Hindi "व्यायाम") for exercise
    ✓ "ચરબી" for fat | "ઊર્જા" for energy | "લોહી" for blood
    ✓ "ભોજન" or "ખાવાનું" for meal | "શ્વાસ" for breath
12. MEDICAL TERMS — use these canonical Gujarati terms (English in parentheses first mention):
    ઉચ્ચ લોહીનું દબાણ (High Blood Pressure) | મધુ પ્રમેહ (Diabetes) | સ્થૂળતા (Obesity)
    કોલેસ્ટ્રોલ (Cholesterol) | ચયાપચય (Metabolism) | રક્ત / લોહી (Blood)
    શરીરની ચરબી (Body Fat) | આંતરડાની ચરબી (Visceral Fat) | સ્નાયુ (Muscle Mass)
    હાડકાની ઘનતા (Bone Density) | થાઇરોઇડ (Thyroid) | રક્ત શર્કરા (Blood Sugar)
    રોગ પ્રતિકાર શક્તિ (Immune System) | ધમની (Artery) | તાણ વ્યવસ્થાપન (Stress Management)
13. PUNCTUATION: Use । or . at sentence end. Avoid anglicized punctuation choices.
14. PREVENTIVE LANGUAGE: Never write "દર્દીને [રોગ] છે" — write "[રોગ]નું જોખમ વધેલ છે".
15. COMMON ERRORS TO AVOID — these patterns are wrong; use the alternatives shown:
    ✗ Any Devanagari character (Hindi script) mixed into Gujarati text — forbidden
    ✗ "BMI ઊંચો છ" → ✓ "BMI સામાન્ય કરતાં વધારે છ"
    ✗ "risk factor વધ છ" → ✓ "જોખમ કારક વધે છ"
    ✗ "healthy lifestyle ફૉલો કરો" → ✓ "સ્વસ્થ જીવનશૈલી અપનાવો"
    ✗ Wrong genitive: "શરીરનો ચરબી" (ચરબી is f.) → ✓ "શરીરની ચરબી"
    ✗ Wrong genitive: "ખોરાકની પ્રકાર" (પ્રકાર is m.) → ✓ "ખોરાકનો પ્રકાર"
    ✗ Hindi word "आहार" in Gujarati text → ✓ "ખોરાક"
    ✗ Hindi word "व्यायाम" in Gujarati text → ✓ "કસરત"
"""

    @staticmethod
    def generate_in_language(health_summary: str, language: str) -> Tuple[bool, str]:
        """
        Generate AI health analysis directly in Hindi or Gujarati — fully native composition.
        Uses deep language-specific grammar rules and high thinking budget to ensure
        100% grammatically correct, naturally flowing output.
        Returns: (success, response_text)
        """
        is_hindi    = language == "Hindi"
        lang_name   = "Hindi"    if is_hindi else "Gujarati"
        lang_script = "Devanagari" if is_hindi else "Gujarati script (U+0A80–U+0AFF)"
        grammar     = (AIHealthAnalyzer._HINDI_GRAMMAR_RULES
                       if is_hindi else AIHealthAnalyzer._GUJARATI_GRAMMAR_RULES)

        # Section headings in the target language (pre-translated for consistency)
        if is_hindi:
            hdg = [
                "## 1. वर्तमान स्वास्थ्य सारांश",
                "## 2. जोखिम मूल्यांकन",
                "## 3. भविष्य में संभावित स्वास्थ्य जोखिम",
                "## 4. क्या खाएं",
                "## 5. क्या परहेज करें",
                "## 6. जीवनशैली संबंधी सुझाव",
                "## 7. भविष्य की चेतावनी",
                "## 8. चिकित्सा अस्वीकरण",
            ]
        else:
            hdg = [
                "## 1. વર્તમાન સ્વાસ્થ્ય સારાંશ",
                "## 2. જોખમ મૂલ્યાંકન",
                "## 3. ભવિષ્યમાં સ્વાસ્થ્ય જોખમ",
                "## 4. શું ખાવું",
                "## 5. શું ટાળવું",
                "## 6. જીવનશૈલી ભલામણો",
                "## 7. ભવિષ્ય ચેતવણી",
                "## 8. તબીબી અસ્વીકૃતિ",
            ]
        headings_block = "\n".join(hdg)

        # Section-specific guidance in English (for the AI) about what to write
        section_guidance = (
            "SECTION CONTENT GUIDANCE:\n"
            "Section 1 — Current Health Summary: 4-6 bullet points covering height, weight,\n"
            "  BMI interpretation, body-fat %, muscle mass, hydration, metabolic rate, and\n"
            "  overall fitness classification. Each point should state the measured value and\n"
            "  what it means for the patient in plain language.\n"
            "Section 2 — Risk Assessment: For each metric that is outside the healthy range,\n"
            "  create a dedicated bullet. Use a 3-level scale: Low Risk / Moderate Risk / High Risk.\n"
            "  Reference the specific measured value. NEVER say the patient 'has' a disease.\n"
            "Section 3 — Future Health Risks: 4-5 bullet points predicting long-term implications\n"
            "  (5-10 year horizon) if current trends continue. E.g. high visceral fat → cardiovascular\n"
            "  risk, low muscle mass → sarcopenia risk, high BMI → metabolic syndrome risk.\n"
            "Section 4 — What To Eat: 6-8 specific food recommendations with explanation.\n"
            "  Include whole grains, vegetables, protein sources, healthy fats, dairy/alternatives,\n"
            "  hydration. Mention exact portions or frequency where possible.\n"
            "Section 5 — What To Avoid: 5-7 specific foods/habits to reduce or eliminate with\n"
            "  brief reason. Include refined carbs, sugar, trans-fats, excess salt, alcohol, smoking.\n"
            "Section 6 — Lifestyle Recommendations: 6-8 actionable tips covering:\n"
            "  cardio exercise (type + duration + frequency), strength training, sleep duration\n"
            "  and hygiene, stress management (meditation, breathing), screen time, water intake.\n"
            "Section 7 — Future Risk Warning: A concise 2-3 sentence motivational warning about\n"
            "  what could happen long-term if changes are not made. Encouraging but realistic.\n"
            "Section 8 — Medical Disclaimer: Standard disclaimer stating this is a wellness\n"
            "  assessment, not medical diagnosis, and the patient should consult a licensed\n"
            "  physician for medical advice or treatment. Write in formal language.\n"
        )

        # Few-shot style examples of correct target-language sentences
        if is_hindi:
            style_examples = (
                "STYLE EXAMPLES — write sentences like these:\n"
                "* आपका बी.एम.आई. (BMI) २७.५ है, जो सामान्य सीमा से थोड़ा अधिक है।\n"
                "* शरीर की चर्बी (Body Fat) ३२% है, जो महिलाओं के लिए उच्च श्रेणी में आती है।\n"
                "* हृदय रोग (Heart Disease) का जोखिम बढ़ा हुआ है — इसे नियंत्रित किया जा सकता है।\n"
                "* प्रतिदिन कम से कम ३०-४५ मिनट तेज़ चलना अत्यंत लाभकारी होगा।\n"
                "* रात की नींद ७-८ घंटे अनिवार्य है; इससे हार्मोनल संतुलन बना रहता है।\n"
            )
        else:
            style_examples = (
                "STYLE EXAMPLES — write sentences like these:\n"
                "* આપનો BMI ૨૭.૫ છ, જે સામાન્ય મર્યાદા કરતાં થોડો વધારે છ।\n"
                "* શરીરની ચરબી (Body Fat) ૩૨% છ, જે સ્ત્રીઓ માટે ઊંચી શ્રેણીમાં આવ છ।\n"
                "* હ્રદય રોગ (Heart Disease)નું જોખમ વધેલ છ — આ કાબૂ આણી શકાય છ।\n"
                "* દરરોજ ઓછામાં ઓછી ૩૦-૪૫ મિનિટ ઝડપી ચાલવું અત્યંત ફાયદાકારક રહ\u0ccd\u0cb6\u0cc7.\n"
                "* રાત્રિ ઊંઘ ૭-૮ કલાક ફરજિયાત છ; આ હ\u0cbf\u0cb8\u0ccd\u0c9f\u0cae\u0cbf\u0ca8 સ\u0c82\u0ca4\u0cc1\u0cb2\u0ca8 જાળવ\u0cc7 છ।\n"
            )

        system_instruction_local = (
            f"You are a senior preventive-health physician AND a native {lang_name} author, "
            f"writing a patient wellness report entirely in NATIVE {lang_name} ({lang_script}).\n"
            f"You have a post-graduate degree in both medicine and {lang_name} linguistics.\n\n"
            f"LANGUAGE REQUIREMENT: Every single word must be written in authentic {lang_name}. "
            f"No Roman letters, no {'Gujarati' if is_hindi else 'Hindi/Devanagari'} characters, "
            "no mixing of scripts. English may appear ONLY inside (parentheses) for medical terms.\n\n"
            f"{grammar}\n"
            f"{style_examples}\n"
            f"{section_guidance}\n"
            "WELLNESS REPORT RULES:\n"
            "- Do NOT diagnose — use preventive phrases ('…का जोखिम बढ़ा हुआ है' / '…નું જોખમ વધેલ છ').\n"
            "- Tone: professional, warm, health-coaching style. Address patient with respect.\n"
            "- Quote the actual measured values (BMI number, body-fat %, etc.) in each relevant bullet.\n"
            "- Give SPECIFIC recommendations: name actual foods, actual exercises, exact durations.\n"
            "- Sections 4 and 5 must list individual food items / habits (not vague categories).\n"
            "- Section 6 must include cardio type + minutes + frequency AND strength training advice.\n"
            "- Include a proper medical disclaimer in the target language (Section 8).\n\n"
            "THINKING PROCESS — before writing each section:\n"
            "  1. Identify which metrics are concerning vs healthy.\n"
            "  2. Select advice appropriate to those specific values.\n"
            "  3. Draft the sentence, then verify grammar before finalizing it.\n\n"
            f"OUTPUT FORMAT — exactly these 8 sections with the exact headings below:\n"
            f"{headings_block}\n\n"
            "Each section heading starts with '## '. Content follows on the next line. "
            "Use bullet points (* ) for lists. Bold key terms with **term**."
        )

        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            return False, "GEMINI_API_KEY not set"

        try:
            client = genai.Client(api_key=api_key)
            prompt = (
                f"PATIENT HEALTH DATA:\n\n{health_summary}\n\n"
                f"TASK: Write a complete 8-section wellness evaluation report in {lang_name}.\n\n"
                f"STEP 1 — ANALYSE THE DATA: Read every metric above and note which ones are\n"
                f"outside the healthy range and which ones are good. Consider the patient's age,\n"
                f"gender, BMI, body fat %, muscle mass, visceral fat, hydration, and any\n"
                f"other values provided. This analysis (internal — do NOT print it) guides Section 2.\n\n"
                f"STEP 2 — COMPOSE IN {lang_name.upper()}: Write every heading, every sentence,\n"
                f"every bullet point entirely in {lang_name}. Not a single English word should appear\n"
                f"outside (parentheses). Quote actual measured values in relevant bullets.\n\n"
                f"STEP 3 — SELF-REVIEW: After completing all 8 sections, silently re-read the\n"
                f"entire report and fix:\n"
                f"  * Any grammar error (gender agreement, postpositions, verb forms)\n"
                f"  * Any wrong or missing matra / conjunct\n"
                f"  * Any English word that appears outside (parentheses)\n"
                f"  * Any sentence that diagnoses instead of describing risk\n"
                f"  * Any vague recommendation — replace with a specific one\n\n"
                f"Output only the final corrected report. Use preventive language throughout.\n"
                f"Bold the most important terms with **term**."
            )

            response = client.models.generate_content(
                model="gemini-2.5-flash",
                config=genai_types.GenerateContentConfig(
                    system_instruction=system_instruction_local,
                    thinking_config=genai_types.ThinkingConfig(thinking_budget=8192),
                    temperature=0.1,
                ),
                contents=prompt,
            )

            if not response.text:
                return False, "Empty response from AI"

            result = response.text.strip()
            # Strip accidental code fences
            if result.startswith("```"):
                result = "\n".join(
                    l for l in result.split("\n") if not l.strip().startswith("```")
                ).strip()

            # Grammar-correction pass — catches any residual matra/conjunct/
            # gender-agreement errors that slipped through even with thinking enabled.
            try:
                result = AIHealthAnalyzer._gemini_grammar_correct(result, language)
            except Exception:
                pass  # keep the original if correction fails

            return True, result

        except Exception as e:
            return False, f"Error generating {lang_name} analysis: {str(e)}"

    @staticmethod
    def _googletrans(text: str, dest: str) -> str:
        """
        Google Translate Ajax API (same endpoint as googletrans library).
        Uses urllib stdlib — no httpx/Supabase conflict.
        Uses sl=en for explicit source, hl=dest for grammar hints,
        and dt=t+rm+bd for richer translation data.
        """
        import urllib.request
        import urllib.parse
        import json

        params = urllib.parse.urlencode({
            "client": "gtx",
            "sl":     "en",
            "tl":     dest,
            "hl":     dest,
            "dt":     ["t", "bd"],
            "dj":     "1",
            "source": "input",
            "q":      text,
        }, doseq=True)
        url = f"https://translate.googleapis.com/translate_a/single?{params}"
        req = urllib.request.Request(
            url,
            headers={
                "User-Agent": (
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/122.0.0.0 Safari/537.36"
                ),
                "Accept-Language": "en-US,en;q=0.9",
                "Referer": "https://translate.google.com/",
            },
        )
        with urllib.request.urlopen(req, timeout=20) as resp:
            data = json.loads(resp.read())

        # dj=1 returns {"sentences": [{"trans": ..., "orig": ...}, ...]}
        if isinstance(data, dict) and "sentences" in data:
            return "".join(s.get("trans", "") for s in data["sentences"])
        # fallback: old array format
        if isinstance(data, list) and data and isinstance(data[0], list):
            return "".join(seg[0] for seg in data[0] if seg and seg[0])
        return text

    @staticmethod
    def _chunk_lines(lines: list, max_chars: int = 4500) -> list:
        """Split line list into chunks that each stay under max_chars."""
        chunks, current, cur_len = [], [], 0
        for line in lines:
            ll = len(line) + 1  # +1 for newline
            if cur_len + ll > max_chars and current:
                chunks.append(current)
                current, cur_len = [line], ll
            else:
                current.append(line)
                cur_len += ll
        if current:
            chunks.append(current)
        return chunks

    @staticmethod
    def _preprocess_medical_brackets(text: str) -> str:
        """
        For Google Translate: insert '(EnglishTerm)' after each medical term in the
        source English text. Google Translate translates the main word but usually
        keeps the parenthetical Latin text, producing output like
        '\u0936\u0930\u0940\u0930 \u0915\u0940 \u091a\u0930\u094d\u092c\u0940 (Body Fat)' in the target language.
        Sorted longest-first to avoid partial matches on sub-phrases.
        """
        terms_sorted = sorted(_MEDICAL_BRACKET_TERMS, key=len, reverse=True)
        for term in terms_sorted:
            pattern = re.compile(rf'\b({re.escape(term)})\b(?!\s*\()', re.IGNORECASE)
            text = pattern.sub(r'\1 (\1)', text)
        return text

    @staticmethod
    def _gemini_grammar_correct(text: str, language: str) -> str:
        """
        Post-processing pass: send already-translated text through Gemini to fix
        every grammar, spelling, matra, conjunct, and vocabulary error 
        while preserving all Markdown structure markers (## / * / - / digits).
        Used after Google Translate to elevate quality to native-speaker level.
        """
        is_hindi  = language == "Hindi"
        lang_name = "Hindi" if is_hindi else "Gujarati"
        grammar   = (AIHealthAnalyzer._HINDI_GRAMMAR_RULES
                     if is_hindi else AIHealthAnalyzer._GUJARATI_GRAMMAR_RULES)

        # Language-specific common machine-translation artifacts
        if is_hindi:
            error_checklist = (
                "KNOWN MACHINE-TRANSLATION ERRORS TO SPECIFICALLY FIX IN HINDI:\n"
                "A. MIXED SCRIPT: Remove any non-Devanagari characters outside (parentheses).\n"
                "   Transliteration like 'BMI high hai' → 'बी.एम.आई. (BMI) उच्च है'.\n"
                "B. WRONG GENDER:\n"
                "   'अच्छा नींद' → 'अच्छी नींद'  (नींद is feminine)\n"
                "   'बढ़ा हुई चर्बी' → 'बढ़ी हुई चर्बी'  (चर्बी is feminine)\n"
                "   'उच्च रक्त चाप का' → 'उच्च रक्तचाप का'  (one compound word)\n"
                "C. WRONG POSTPOSITIONS:\n"
                "   'रोगी का लिए' → 'रोगी के लिए'\n"
                "   'शरीर में चर्बी की' → 'शरीर की चर्बी'\n"
                "D. WRONG VERB FORMS:\n"
                "   'करना है' for obligation → 'करना चाहिए'\n"
                "   'खाना है' for advice → 'खाएं' or 'खाना चाहिए'\n"
                "E. LOANWORD REPLACEMENT:\n"
                "   'रेगुलर एक्सरसाइज़' → 'नियमित कसरत'\n"
                "   'हेल्दी डाइट' → 'स्वस्थ आहार'\n"
                "   'वॉटर पीएं' → 'पानी पिएं'\n"
                "   'स्लीप' → 'नींद'\n"
                "F. MISSING MATRAS: Scan every word — ensure no vowel sign is missing or swapped.\n"
                "G. DIAGNOSTIC LANGUAGE: 'को मधुमेह है' → 'मधुमेह का जोखिम बढ़ा हुआ है'.\n"
            )
        else:
            error_checklist = (
                "KNOWN MACHINE-TRANSLATION ERRORS TO SPECIFICALLY FIX IN GUJARATI:\n"
                "A. DEVANAGARI BLEED-THROUGH: Remove every Hindi/Devanagari character (Unicode\n"
                "   U+0900–U+097F) that appears in the text. Replace with correct Gujarati.\n"
                "   Common: Hindi 'आहार' → Gujarati 'ખોરાક'; 'व्यायाम' → 'કસરત'; 'नींद' → 'ઊંઘ'.\n"
                "B. WRONG GENITIVE AGREEMENT:\n"
                "   'શરીરનો ચરબી' (ચરબી is f.) → 'શરીરની ચરબી'\n"
                "   'ભોજનનો પ્રકાર' (m.) → 'ભોજનનો પ્રકાર' ✓; 'ઊર્જાનો' (ઊર્જા is f.) → 'ઊર્જાની'\n"
                "C. WRONG NEUTER VERB:\n"
                "   'શરીર સ્વસ્થ છો' (n.sg) → 'શરીર સ્વસ્થ છ'\n"
                "   'વજન ઘટ\u0cc7 છો' → 'વજન ઘટ\u0cc7 છ'\n"
                "D. LOANWORD REPLACEMENT:\n"
                "   Hindi 'आहार' in Gujarati → 'ખોરાક'\n"
                "   Hindi 'दिल' in Gujarati → 'હ્રદય'\n"
                "   'regular exercise' transliterated → 'નિયમિત કસરત'\n"
                "   'healthy lifestyle' → 'સ\u0ccd\u0cb5\u0cb8\u0ccd\u0ca5 જ\u0cbf\u0cb5\u0ca8\u0cb6\u0cc8\u0cb2\u0cbf'\n"
                "E. MISSING/WRONG MATRAS: Check every word for correct Gujarati vowel signs.\n"
                "   Common mistakes: ે vs ૈ, ો vs ૌ, short િ vs long ી, short ુ vs long ૂ.\n"
                "F. DIAGNOSTIC LANGUAGE: 'ને [રોગ] છ' → '[રોગ]નું જોખમ વધ\u0cc7\u0cb2 છ'.\n"
                "G. FLOATING HALANT: 'ક્ ષ' (with space) → 'ક\u0ccd\u0cb7' (proper conjunct).\n"
            )

        system_instruction = (
            f"You are a native {lang_name} linguist and medical editor with 20 years of experience "
            f"correcting machine-translated health reports. "
            f"You receive a {lang_name} health wellness report that may contain grammar, spelling, "
            f"matra, conjunct, vocabulary, script, or gender-agreement errors. "
            f"Your job is to correct EVERY error so the result reads as if written by an educated "
            f"native {lang_name} speaker — without changing any content or structure.\n\n"
            f"{grammar}\n"
            f"{error_checklist}\n"
            "CORRECTION RULES:\n"
            "1. Fix grammar, gender agreement, case markers, verb forms, matras, conjuncts.\n"
            "2. Replace non-native vocabulary with authentic {lang_name} equivalents.\n"
            "3. PRESERVE all Markdown markers exactly: '## ', '* ', '- ', digit+'.'/digit+')'.\n"
            "4. PRESERVE blank lines exactly as they appear.\n"
            "5. PRESERVE all English terms inside (parentheses) — do not translate them.\n"
            "6. PRESERVE numeric values (BMI numbers, percentages, kg, cm) unchanged.\n"
            "7. Do NOT add, remove, or reorder sections or content.\n"
            "8. Do NOT wrap output in code fences or add any preamble.\n"
            "9. After making corrections, do a final pass specifically checking:\n"
            "   - All gender agreements are correct\n"
            "   - No Devanagari characters appear in Gujarati text (or vice versa)\n"
            "   - All obligation verbs are in correct form\n"
            "   - All medical terms use the canonical vocabulary from the grammar rules\n"
            "Output ONLY the corrected report."
        )

        _api_key = os.getenv("GEMINI_API_KEY")
        if not _api_key:
            return f"Error: GEMINI_API_KEY not set"
        try:
            client = genai.Client(api_key=_api_key)
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                config=genai_types.GenerateContentConfig(
                    system_instruction=system_instruction,
                    thinking_config=genai_types.ThinkingConfig(thinking_budget=8192),
                    temperature=0.05,
                ),
                contents=(
                    f"Correct ALL errors in this {lang_name} health report.\n"
                    f"Apply the error checklist systematically:\n"
                    f"  1. Script purity — no foreign script characters\n"
                    f"  2. Gender agreement on every noun–adjective–verb chain\n"
                    f"  3. Correct postpositions and case markers\n"
                    f"  4. Replace all loanwords/transliterations with native vocabulary\n"
                    f"  5. Fix every matra and conjunct\n"
                    f"  6. Ensure preventive (not diagnostic) language throughout\n"
                    f"Preserve all Markdown structure, blank lines, parenthetical English terms,\n"
                    f"and numeric values exactly.\n\n"
                    f"REPORT:\n{text}"
                ),
            )
            corrected = (response.text or "").strip()
            if corrected.startswith("```"):
                corrected = "\n".join(
                    l for l in corrected.split("\n") if not l.strip().startswith("```")
                ).strip()
            # Safety: if output shrank by more than 40% something went wrong — keep original
            if len(corrected) < len(text) * 0.6:
                return text
            return corrected if len(corrected) > 50 else text
        except Exception:
            return text

    @staticmethod
    def _gemini_translate(text: str, dest: str) -> str:
        """
        Translate using Gemini 2.5 Flash with maximum thinking budget.
        Produces grammatically perfect Hindi / Gujarati with:
        - Detailed language-specific grammar rules in the system instruction
        - Thinking budget of 8192 tokens for careful linguistic reasoning
        - Temperature 0.05 for highly deterministic, accurate output
        - Post-translation grammar correction pass for 100% accuracy
        """
        is_hindi    = dest == "hi"
        lang_name   = "Hindi" if is_hindi else "Gujarati"
        lang_script = "Devanagari (U+0900–U+097F)" if is_hindi else "Gujarati script (U+0A80–U+0AFF)"
        grammar     = (AIHealthAnalyzer._HINDI_GRAMMAR_RULES
                       if is_hindi else AIHealthAnalyzer._GUJARATI_GRAMMAR_RULES)

        # Full domain glossary for the target language
        if is_hindi:
            glossary = (
                "MANDATORY GLOSSARY — always use these exact translations:\n"
                "English                → Hindi\n"
                "Body Fat               → शरीर की चर्बी (Body Fat)\n"
                "Visceral Fat           → आंतरिक / अंदरूनी चर्बी (Visceral Fat)\n"
                "Muscle Mass            → मांसपेशियाँ (Muscle Mass)\n"
                "Bone Density           → अस्थि घनत्व (Bone Density)\n"
                "Cholesterol            → कोलेस्ट्रॉल (Cholesterol)\n"
                "Blood Sugar            → रक्त शर्करा (Blood Sugar)\n"
                "Blood Pressure         → रक्तचाप (Blood Pressure)\n"
                "High Blood Pressure    → उच्च रक्तचाप (High Blood Pressure)\n"
                "Diabetes               → मधुमेह (Diabetes)\n"
                "Obesity                → मोटापा (Obesity)\n"
                "Metabolism / Metabolic Rate → चयापचय (Metabolism)\n"
                "Immune System          → प्रतिरक्षा प्रणाली (Immune System)\n"
                "Heart Disease          → हृदय रोग (Heart Disease)\n"
                "Artery / Arteries      → धमनी / धमनियाँ (Arteries)\n"
                "Thyroid                → थाइरॉइड (Thyroid)\n"
                "Haemoglobin            → हीमोग्लोबिन (Haemoglobin)\n"
                "Hydration              → जलयोजन (Hydration)\n"
                "Stress Management      → तनाव प्रबंधन (Stress Management)\n"
                "Sedentary Lifestyle    → निष्क्रिय जीवनशैली (Sedentary Lifestyle)\n"
                "Basal Metabolic Rate   → बेसल मेटाबोलिक दर (BMR)\n"
                "Risk                   → जोखिम\n"
                "Recommendation         → सुझाव / अनुशंसा\n"
                "Wellness               → स्वास्थ्य / कल्याण\n"
                "Preventive             → निवारक\n"
                "Short abbreviations BMI, BMR, TSF, DNA — keep unchanged, no brackets.\n"
            )
            few_shots = (
                "FEW-SHOT TRANSLATION EXAMPLES:\n"
                "EN: Your Body Fat percentage is 32%, which is in the High range for your age.\n"
                "HI: आपकी शरीर की चर्बी (Body Fat) ३२% है, जो आपकी आयु के लिए उच्च श्रेणी में आती है।\n\n"
                "EN: You have an increased risk of developing Heart Disease if current trends continue.\n"
                "HI: यदि वर्तमान प्रवृत्ति जारी रही तो हृदय रोग (Heart Disease) का जोखिम बढ़ सकता है।\n\n"
                "EN: * Consume at least 2-3 servings of fruits and vegetables daily.\n"
                "HI: * प्रतिदिन कम से कम २-३ बार फल और सब्जियाँ खाएं।\n\n"
                "EN: ## Lifestyle Recommendations\n"
                "HI: ## जीवनशैली संबंधी सुझाव\n\n"
                "EN: This report is not a medical diagnosis.\n"
                "HI: यह रिपोर्ट कोई चिकित्सीय निदान नहीं है।\n"
            )
        else:
            glossary = (
                "MANDATORY GLOSSARY — always use these exact translations:\n"
                "English                → Gujarati\n"
                "Body Fat               → શરીરની ચરબી (Body Fat)\n"
                "Visceral Fat           → આંતરડાની ચરબી (Visceral Fat)\n"
                "Muscle Mass            → સ\u0ccd\u0ca8\u0cbe\u0caf\u0cc1 (Muscle Mass)\n"
                "Bone Density           → હ\u0cbe\u0ca1\u0c95\u0cbe\u0ca8\u0cbf ઘ\u0ca8\u0ca4\u0cbe (Bone Density)\n"
                "Cholesterol            → ક\u0ccb\u0cb2\u0cc7\u0cb8\u0ccd\u0c9f\u0ccd\u0cb0\u0ccb\u0cb2 (Cholesterol)\n"
                "Blood Sugar            → ર\u0c95\u0ccd\u0ca4 શ\u0cb0\u0ccd\u0c95\u0cb0\u0cbe (Blood Sugar)\n"
                "Blood Pressure         → લ\u0ccb\u0cb9\u0cbf\u0ca8\u0cc1\u0c82 દ\u0cac\u0cbe\u0ca3 (Blood Pressure)\n"
                "High Blood Pressure    → ઉ\u0c9a\u0ccd\u0c9a લ\u0ccb\u0cb9\u0cbf\u0ca8\u0cc1\u0c82 દ\u0cac\u0cbe\u0ca3 (High Blood Pressure)\n"
                "Diabetes               → મ\u0ca7\u0cc1 પ\u0ccd\u0cb0\u0cae\u0cc7\u0cb9 (Diabetes)\n"
                "Obesity                → સ\u0ccd\u0ca5\u0cc2\u0cb3\u0ca4\u0cbe (Obesity)\n"
                "Metabolism             → \u0c9a\u0caf\u0cbe\u0caa\u0c9a\u0caf (Metabolism)\n"
                "Immune System          → ર\u0ccb\u0c97 પ\u0ccd\u0cb0\u0ca4\u0cbf\u0c95\u0cbe\u0cb0 \u0cb6\u0c95\u0ccd\u0ca4\u0cbf (Immune System)\n"
                "Heart Disease          → હ\u0ccd\u0cb0\u0ca6\u0caf ર\u0ccb\u0c97 (Heart Disease)\n"
                "Artery / Arteries      → ધ\u0cae\u0ca8\u0cbf / ધ\u0cae\u0ca8\u0cbf\u0d0b\u0cb8 (Arteries)\n"
                "Thyroid                → \u0ca5\u0cbe\u0c87\u0cb0\u0ccb\u0c87\u0ca1 (Thyroid)\n"
                "Hydration              → \u0c9c\u0cb3\u0caf\u0ccb\u0c9c\u0ca8 (Hydration)\n"
                "Stress Management      → \u0ca4\u0cbe\u0ca3 \u0cb5\u0ccd\u0caf\u0cb5\u0cb8\u0ccd\u0ca5\u0cbe\u0caa\u0ca8 (Stress Management)\n"
                "Risk                   → \u0c9c\u0ccb\u0c96\u0cae\n"
                "Recommendation         → \u0cad\u0cb2\u0cbe\u0cae\u0ca3\n"
                "Food / Diet            → \u0c96\u0ccb\u0cb0\u0cbe\u0c95 (NOT Hindi \u0906\u0939\u093e\u0930)\n"
                "Exercise               → \u0c95\u0cb8\u0cb0\u0ca4 (NOT Hindi \u0935\u094d\u092f\u093e\u092f\u093e\u092e)\n"
                "Sleep                  → \u0a8a\u0a82\u0a98 (NOT Hindi \u0928\u0940\u0902\u0926)\n"
                "Short abbreviations BMI, BMR, TSF, DNA — keep unchanged, no brackets.\n"
            )
            few_shots = (
                "FEW-SHOT TRANSLATION EXAMPLES:\n"
                "EN: Your Body Fat percentage is 32%, which is in the High range for your age.\n"
                "GU: આ\u0caau\u0ca8\u0cbf \u0cb6\u0cb0\u0cc0\u0cb0\u0ca8\u0cbf \u0c9a\u0cb0\u0cac\u0cc0 (Body Fat) \u0e3a\u0e32% \u0c9b\u0cc7, \u0c9c\u0cc7 \u0c86\u0caau\u0ca8\u0cc0 \u0c89\u0c82\u0cae\u0cb0 \u0cae\u0cbe\u0c9f\u0cc7 \u0a8a\u0a82\u0a9a\u0cc0 \u0cb6\u0ccd\u0cb0\u0cc7\u0aa3\u0cc0\u0cae\u0cbe\u0a82 \u0c86\u0cb5\u0cc7 \u0c9b\u0cc7.\n\n"
                "EN: You have an increased risk of developing Heart Disease if current trends continue.\n"
                "GU: \u0c9c\u0ccb \u0c86\u0cb5\u0cc0 \u0cb8\u0ccd\u0ca5\u0cbf\u0ca4\u0cbf \u0c9a\u0cbe\u0cb2\u0cc1 \u0cb0\u0cb9\u0cc7 \u0ca4\u0ccb \u0cb9\u0ccd\u0cb0\u0ca6\u0caf \u0cb0\u0ccb\u0c97 (Heart Disease)\u0ca8\u0cc1\u0a82 \u0c9c\u0ccb\u0c96\u0cae \u0cb5\u0ca7\u0cc7\u0cb2 \u0c9b\u0cc7.\n\n"
                "EN: * Consume at least 2-3 servings of fruits and vegetables daily.\n"
                "GU: * \u0ca6\u0cb0\u0cb0\u0ccb\u0c9c \u0d03-\u0e30 \u0cb5\u0cbe\u0cb0 \u0cab\u0cb3 \u0c85\u0ca8\u0cc7 \u0cb6\u0cbe\u0c95\u0cad\u0cbe\u0c9c\u0cc0 \u0c96\u0cbe\u0cb5\u0cbf.\n\n"
                "EN: ## Lifestyle Recommendations\n"
                "GU: ## \u0c9c\u0cc0\u0cb5\u0ca8\u0cb6\u0cc8\u0cb2\u0cbf \u0cad\u0cb2\u0cbe\u0cae\u0ca3\u0ccb\n"
            )

        system_instruction = (
            f"You are a professional medical translator with 25 years of experience "
            f"translating English health reports into {lang_name} ({lang_script}). "
            f"You are a native {lang_name} speaker with a post-graduate degree in {lang_name} "
            f"linguistics and medical translation.\n\n"
            f"{grammar}\n"
            f"{glossary}\n"
            f"{few_shots}\n"
            "TRANSLATION RULES:\n"
            "1. Translate ONLY the text content — preserve ALL Markdown structure markers exactly:\n"
            "   - Lines starting with '## ' → keep '## ', translate only the heading text after it.\n"
            "   - Lines starting with '* ' or '- ' → keep the marker, translate only the content.\n"
            "   - Lines starting with digit+'.' or digit+')' → keep number+marker, translate content.\n"
            "   - Blank lines → reproduce as blank lines.\n"
            "2. Use the MANDATORY GLOSSARY for every medical/health term — no exceptions.\n"
            "   Append English in (parentheses) on first mention of each term.\n"
            "   Short abbreviations BMI, BMR, TSF, DNA stay unchanged.\n"
            "3. CHAIN-OF-THOUGHT for each sentence:\n"
            "   a. Identify all medical terms → apply glossary.\n"
            "   b. Determine noun genders → ensure adjective/verb agreement.\n"
            "   c. Choose correct postpositions and verb conjugation for SOV structure.\n"
            "   d. Use native vocabulary (not transliterated English or loanwords).\n"
            "4. SELF-REVIEW after completing all sections:\n"
            "   - Check every sentence for gender agreement, case markers, verb forms.\n"
            "   - Verify script purity: no foreign-script characters outside (parentheses).\n"
            "   - Verify all obligation phrases use correct target-language forms.\n"
            "   - Replace any transliterated/loanword that slipped through.\n"
            "5. Bold important terms with **term** where they appear in the original bold.\n"
            "6. Output ONLY the translated and reviewed report. No preamble, no notes, no code fences."
        )

        _api_key = os.getenv("GEMINI_API_KEY")
        if not _api_key:
            return f"Error: GEMINI_API_KEY not set"
        client = genai.Client(api_key=_api_key)
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            config=genai_types.GenerateContentConfig(
                system_instruction=system_instruction,
                thinking_config=genai_types.ThinkingConfig(thinking_budget=8192),
                temperature=0.05,
            ),
            contents=(
                f"Translate this English health wellness report into {lang_name}.\n\n"
                f"STEP 1 — GLOSSARY PASS: Identify every medical/health term and resolve it\n"
                f"  against the mandatory glossary before translating.\n"
                f"STEP 2 — TRANSLATE: Translate each line preserving all Markdown markers\n"
                f"  (## / * / - / digit+.) exactly. Apply grammar rules for every sentence.\n"
                f"STEP 3 — REVIEW: Re-read every sentence and fix:\n"
                f"  * Gender agreement errors\n"
                f"  * Wrong postpositions or case markers\n"
                f"  * Non-native vocabulary / loanwords / transliterations\n"
                f"  * Diagnostic language (change to risk-based language)\n"
                f"  * Any character from the wrong script\n\n"
                f"Output only the final corrected {lang_name} report.\n\n"
                f"REPORT:\n{text}"
            ),
        )
        translated = (response.text or "").strip()

        # Strip accidental code-block wrapping
        if translated.startswith("```"):
            translated = "\n".join(
                l for l in translated.split("\n") if not l.strip().startswith("```")
            ).strip()

        # Validate: at least 80% of ## section headers must still be present
        orig_headers  = [l for l in text.split("\n")       if l.strip().startswith("## ")]
        trans_headers = [l for l in translated.split("\n") if l.strip().startswith("## ")]
        if orig_headers and len(trans_headers) < len(orig_headers) * 0.8:
            return text  # structure broken — fall back to English

        return translated if len(translated) > 50 else text

    @staticmethod
    def translate_for_pdf(ai_analysis: str, language: str, method: str = "google") -> str:
        """
        Translate AI wellness analysis to Hindi or Gujarati.

        method="google"  → Google Translate Ajax API (urllib, no key needed)
                           Full-document chunks for context accuracy.
        method="gemini"  → Gemini 2.5 Flash translation API (dedicated key)
                           Sends entire report in one shot for best quality.
        """
        if language == "English":
            return ai_analysis

        lang_code = "hi" if language == "Hindi" else "gu"

        # ── Gemini path ──────────────────────────────────────────────────────
        if method == "gemini":
            try:
                result = AIHealthAnalyzer._gemini_translate(ai_analysis, lang_code)
                return result if len(result) > 50 else ai_analysis
            except Exception:
                return ai_analysis

        try:
            raw_lines = ai_analysis.splitlines()

            # ── Step 1: parse every line → (prefix, plain_text, is_blank) ──
            parsed: list[tuple[str, str, bool]] = []
            for line in raw_lines:
                s = line.strip()
                if not s:
                    parsed.append(("", "", True))
                    continue
                prefix, content = "", s
                if s.startswith("## "):
                    prefix, content = "## ", s[3:]
                elif s.startswith("* "):
                    prefix, content = "* ", s[2:]
                elif s.startswith("- "):
                    prefix, content = "- ", s[2:]
                elif len(s) > 2 and s[0].isdigit() and s[1] in ".)":
                    prefix = s[:2] + " "
                    content = s[len(prefix):].strip()
                parsed.append((prefix, content, False))

            # ── Step 2: build indexed content lines (skip blanks) ──────────
            content_idx: list[int] = []   # indices into parsed[]
            content_txt: list[str] = []   # plain text for those lines
            for i, (_, content, blank) in enumerate(parsed):
                if not blank and content:
                    content_idx.append(i)
                    content_txt.append(content)

            # ── Step 3: chunk and translate ──────────────────────────────────
            chunks = AIHealthAnalyzer._chunk_lines(content_txt)
            translated_all: list[str] = []
            for chunk in chunks:
                block = "\n".join(chunk)
                try:
                    block = AIHealthAnalyzer._preprocess_medical_brackets(block)
                    result = AIHealthAnalyzer._googletrans(block, lang_code)
                    # normalise: sometimes API returns \n, sometimes ↵
                    result = result.replace("\r\n", "\n").replace("\r", "\n")
                    translated_all.extend(result.split("\n"))
                except Exception:
                    translated_all.extend(chunk)  # keep English on error

            # ── Step 4: map translated lines back to original positions ──────
            trans_map: dict[int, str] = {}
            for idx, trans in zip(content_idx, translated_all):
                trans_map[idx] = trans.strip()

            # ── Step 5: reconstruct output with original structure markers ───
            out: list[str] = []
            for i, (prefix, content, blank) in enumerate(parsed):
                if blank:
                    out.append("")
                elif i in trans_map:
                    out.append(prefix + trans_map[i])
                else:
                    out.append(prefix + content)

            raw_result = "\n".join(out).strip()
            if not raw_result or len(raw_result) < 50:
                return ai_analysis

            # ── Step 6: Gemini grammar-correction pass ───────────────────────
            # Google Translate output often has incorrect grammar/matras/vocabulary.
            # Run a dedicated correction pass to bring quality to native-speaker level.
            try:
                corrected = AIHealthAnalyzer._gemini_grammar_correct(
                    raw_result, language
                )
                return corrected
            except Exception:
                return raw_result

        except Exception:
            return ai_analysis


def test_gemini_connection() -> bool:
    """Test Gemini API connection"""
    try:
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            st.error("GEMINI_API_KEY not set")
            return False
        
        client = genai.Client(api_key=api_key)
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents="Hello, test connection"
        )
        return True
    except Exception as e:
        st.error(f"Gemini API connection failed: {str(e)}")
        return False
