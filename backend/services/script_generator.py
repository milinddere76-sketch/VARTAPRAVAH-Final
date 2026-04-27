from groq import Groq
import os
from backend import config
from backend.utils.logger import logger

client = Groq(api_key=config.GROQ_API_KEY or os.getenv("GROQ_API_KEY"))

def generate_script(news_content):
    """
    Uses Groq (Llama 3.1) to generate a high-quality Marathi news script.
    Strictly enforces:
    - Pure Marathi language (no English/Transliteration)
    - Professional TV Anchor tone
    - Correct Grammar
    """
    try:
        if isinstance(news_content, list):
            news_content = "\n".join(news_content)
            
        if not news_content or str(news_content).strip() == "":
            return "नमस्कार, वार्ता प्रवाह मधे आपले स्वागत आहे. सध्या कोणतीही नवीन बातमी उपलब्ध नाही."
            
        system_prompt = """
        तुम्ही 'वार्ता प्रवाह' या प्रतिष्ठित न्यूज चॅनेलचे मुख्य न्यूज अँकर आहात.
        खालील बातमीच्या मुद्द्यांचे एका व्यावसायिक टीव्ही न्यूज बुलेटिन स्क्रिप्टमध्ये रूपांतर करा.
        
        कडक नियम:
        १. केवळ शुद्ध मराठी भाषा वापरा.
        २. कोणताही इंग्रजी शब्द (उदा. 'Live', 'Update', 'News', 'Break') वापरू नका. त्याऐवजी 'थेट प्रक्षेपण', 'ताज्या घडामोडी', 'वृत्तविशेष' असे मराठी पर्याय वापरा.
        ३. भाषा अत्यंत सुसंस्कृत, अधिकृत आणि व्याकरणदृष्ट्या अचूक असावी.
        ४. शैली: अत्यंत वेगवान, लक्ष वेधून घेणारी आणि टीव्ही अँकर सारखी 'ब्रेकिंग न्यूज' शैली असावी.
        ५. इंग्रजी शब्दांचे मराठीत लिप्यंतरण (Transliteration) करू नका, तर शुद्ध मराठी शब्द शोधा.
        """
        
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile", # Updated to latest supported 70B model
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"खालील बातम्यांवर आधारित न्यूज बुलेटिन तयार करा:\n\n{news_content}"}
            ],
            temperature=0.7,
            max_tokens=1500
        )
        return response.choices[0].message.content
    except Exception as e:
        logger.error(f"Groq Script Generation Error: {e}")
        return _generate_with_gemini(news_content)

def _generate_with_gemini(news_content):
    """Fallback to Gemini if Groq fails."""
    logger.info("📡 [FALLBACK] Using Gemini for script generation...")
    try:
        import google.generativeai as genai
        genai.configure(api_key=config.GEMINI_API_KEY)
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        prompt = f"तुम्ही एक अनुभवी मराठी न्यूज अँकर आहात. खालील बातम्यांवर आधारित एक आकर्षक न्यूज बुलेटिन तयार करा:\n\n{news_content}\n\nनियम:\n१. फक्त मराठीत लिहा.\n२. 'नमस्कार, मी आपली अँकर...' ने सुरुवात करा.\n३. प्रत्येक बातमी सविस्तर लिहा."
        
        response = model.generate_content(prompt)
        if response.text:
            logger.info("✅ [GEMINI] Script generated successfully.")
            return response.text
    except Exception as e:
        logger.error(f"❌ [GEMINI] Error: {e}")
        
    # Ultimate Fallback: Just read the raw news items if all AI script generation fails
    fallback_script = "ताज्या घडामोडी: " + str(news_content).replace('---', '')
    return fallback_script

class ScriptGenerator:
    def generate_marathi_script(self, news_items):
        return generate_script(news_items)
