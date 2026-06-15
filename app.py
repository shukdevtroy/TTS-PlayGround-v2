import os
import gradio as gr
from groq import Groq
import tempfile
import requests
import json
import base64
from pathlib import Path
import time
import sys
import platform
from collections import defaultdict

# Available English voices for different providers
groq_voices = [
    "Arista-PlayAI", "Atlas-PlayAI", "Basil-PlayAI", "Briggs-PlayAI",
    "Calum-PlayAI", "Celeste-PlayAI", "Cheyenne-PlayAI", "Chip-PlayAI",
    "Cillian-PlayAI", "Deedee-PlayAI", "Fritz-PlayAI", "Gail-PlayAI",
    "Indigo-PlayAI", "Mamaw-PlayAI", "Mason-PlayAI", "Mikail-PlayAI",
    "Mitch-PlayAI", "Quinn-PlayAI", "Thunder-PlayAI"
]

# OpenAI voices (if user has OpenAI API key)
openai_voices = ["alloy", "ash", "coral", "sage", "echo", "fable", "onyx", "nova", "shimmer"]

# Edge TTS voices (free, no API key required)
edge_voices = [
    "af-ZA-AdriNeural",
    "af-ZA-WillemNeural",
    "sq-AL-AnilaNeural",
    "sq-AL-IlirNeural",
    "am-ET-AmehaNeural",
    "am-ET-MekdesNeural",
    "ar-DZ-AminaNeural",
    "ar-DZ-IsmaelNeural",
    "ar-BH-AliNeural",
    "ar-BH-LailaNeural",
    "ar-EG-SalmaNeural",
    "ar-EG-ShakirNeural",
    "ar-IQ-BasselNeural",
    "ar-IQ-RanaNeural",
    "ar-JO-SanaNeural",
    "ar-JO-TaimNeural",
    "ar-KW-FahedNeural",
    "ar-KW-NouraNeural",
    "ar-LB-LaylaNeural",
    "ar-LB-RamiNeural",
    "ar-LY-ImanNeural",
    "ar-LY-OmarNeural",
    "ar-MA-JamalNeural",
    "ar-MA-MounaNeural",
    "ar-OM-AbdullahNeural",
    "ar-OM-AyshaNeural",
    "ar-QA-AmalNeural",
    "ar-QA-MoazNeural",
    "ar-SA-HamedNeural",
    "ar-SA-ZariyahNeural",
    "ar-SY-AmanyNeural",
    "ar-SY-LaithNeural",
    "ar-TN-HediNeural",
    "ar-TN-ReemNeural",
    "ar-AE-FatimaNeural",
    "ar-AE-HamdanNeural",
    "ar-YE-MaryamNeural",
    "ar-YE-SalehNeural",
    "az-AZ-BabekNeural",
    "az-AZ-BanuNeural",
    "bn-BD-NabanitaNeural",
    "bn-BD-PradeepNeural",
    "bn-IN-BashkarNeural",
    "bn-IN-TanishaaNeural",
    "bs-BA-GoranNeural",
    "bs-BA-VesnaNeural",
    "bg-BG-BorislavNeural",
    "bg-BG-KalinaNeural",
    "my-MM-NilarNeural",
    "my-MM-ThihaNeural",
    "ca-ES-EnricNeural",
    "ca-ES-JoanaNeural",
    "zh-HK-HiuGaaiNeural",
    "zh-HK-HiuMaanNeural",
    "zh-HK-WanLungNeural",
    "zh-CN-XiaoxiaoNeural",
    "zh-CN-XiaoyiNeural",
    "zh-CN-YunjianNeural",
    "zh-CN-YunxiNeural",
    "zh-CN-YunxiaNeural",
    "zh-CN-YunyangNeural",
    "zh-CN-liaoning-XiaobeiNeural",
    "zh-TW-HsiaoChenNeural",
    "zh-TW-YunJheNeural",
    "zh-TW-HsiaoYuNeural",
    "zh-CN-shaanxi-XiaoniNeural",
    "hr-HR-GabrijelaNeural",
    "hr-HR-SreckoNeural",
    "cs-CZ-AntoninNeural",
    "cs-CZ-VlastaNeural",
    "da-DK-ChristelNeural",
    "da-DK-JeppeNeural",
    "nl-BE-ArnaudNeural",
    "nl-BE-DenaNeural",
    "nl-NL-ColetteNeural",
    "nl-NL-FennaNeural",
    "nl-NL-MaartenNeural",
    "en-AU-NatashaNeural",
    "en-AU-WilliamNeural",
    "en-CA-ClaraNeural",
    "en-CA-LiamNeural",
    "en-HK-SamNeural",
    "en-HK-YanNeural",
    "en-IN-NeerjaNeural",
    "en-IN-PrabhatNeural",
    "en-IE-ConnorNeural",
    "en-IE-EmilyNeural",
    "en-KE-AsiliaNeural",
    "en-KE-ChilembaNeural",
    "en-NZ-MitchellNeural",
    "en-NZ-MollyNeural",
    "en-NG-AbeoNeural",
    "en-NG-EzinneNeural",
    "en-PH-JamesNeural",
    "en-PH-RosaNeural",
    "en-SG-LunaNeural",
    "en-SG-WayneNeural",
    "en-ZA-LeahNeural",
    "en-ZA-LukeNeural",
    "en-TZ-ElimuNeural",
    "en-TZ-ImaniNeural",
    "en-GB-LibbyNeural",
    "en-GB-MaisieNeural",
    "en-GB-RyanNeural",
    "en-GB-SoniaNeural",
    "en-GB-ThomasNeural",
    "en-US-AriaNeural",
    "en-US-AnaNeural",
    "en-US-ChristopherNeural",
    "en-US-EricNeural",
    "en-US-GuyNeural",
    "en-US-JennyNeural",
    "en-US-MichelleNeural",
    "en-US-RogerNeural",
    "en-US-SteffanNeural",
    "et-EE-AnuNeural",
    "et-EE-KertNeural",
    "fil-PH-AngeloNeural",
    "fil-PH-BlessicaNeural",
    "fi-FI-HarriNeural",
    "fi-FI-NooraNeural",
    "fr-BE-CharlineNeural",
    "fr-BE-GerardNeural",
    "fr-CA-AntoineNeural",
    "fr-CA-JeanNeural",
    "fr-CA-SylvieNeural",
    "fr-FR-DeniseNeural",
    "fr-FR-EloiseNeural",
    "fr-FR-HenriNeural",
    "fr-CH-ArianeNeural",
    "fr-CH-FabriceNeural",
    "gl-ES-RoiNeural",
    "gl-ES-SabelaNeural",
    "ka-GE-EkaNeural",
    "ka-GE-GiorgiNeural",
    "de-AT-IngridNeural",
    "de-AT-JonasNeural",
    "de-DE-AmalaNeural",
    "de-DE-ConradNeural",
    "de-DE-KatjaNeural",
    "de-DE-KillianNeural",
    "de-CH-JanNeural",
    "de-CH-LeniNeural",
    "el-GR-AthinaNeural",
    "el-GR-NestorasNeural",
    "gu-IN-DhwaniNeural",
    "gu-IN-NiranjanNeural",
    "he-IL-AvriNeural",
    "he-IL-HilaNeural",
    "hi-IN-MadhurNeural",
    "hi-IN-SwaraNeural",
    "hu-HU-NoemiNeural",
    "hu-HU-TamasNeural",
    "is-IS-GudrunNeural",
    "is-IS-GunnarNeural",
    "id-ID-ArdiNeural",
    "id-ID-GadisNeural",
    "ga-IE-ColmNeural",
    "ga-IE-OrlaNeural",
    "it-IT-DiegoNeural",
    "it-IT-ElsaNeural",
    "it-IT-IsabellaNeural",
    "ja-JP-KeitaNeural",
    "ja-JP-NanamiNeural",
    "jv-ID-DimasNeural",
    "jv-ID-SitiNeural",
    "kn-IN-GaganNeural",
    "kn-IN-SapnaNeural",
    "kk-KZ-AigulNeural",
    "kk-KZ-DauletNeural",
    "km-KH-PisethNeural",
    "km-KH-SreymomNeural",
    "ko-KR-InJoonNeural",
    "ko-KR-SunHiNeural",
    "lo-LA-ChanthavongNeural",
    "lo-LA-KeomanyNeural",
    "lv-LV-EveritaNeural",
    "lv-LV-NilsNeural",
    "lt-LT-LeonasNeural",
    "lt-LT-OnaNeural",
    "mk-MK-AleksandarNeural",
    "mk-MK-MarijaNeural",
    "ms-MY-OsmanNeural",
    "ms-MY-YasminNeural",
    "ml-IN-MidhunNeural",
    "ml-IN-SobhanaNeural",
    "mt-MT-GraceNeural",
    "mt-MT-JosephNeural",
    "mr-IN-AarohiNeural",
    "mr-IN-ManoharNeural",
    "mn-MN-BataaNeural",
    "mn-MN-YesuiNeural",
    "ne-NP-HemkalaNeural",
    "ne-NP-SagarNeural",
    "nb-NO-FinnNeural",
    "nb-NO-PernilleNeural",
    "ps-AF-GulNawazNeural",
    "ps-AF-LatifaNeural",
    "fa-IR-DilaraNeural",
    "fa-IR-FaridNeural",
    "pl-PL-MarekNeural",
    "pl-PL-ZofiaNeural",
    "pt-BR-AntonioNeural",
    "pt-BR-FranciscaNeural",
    "pt-PT-DuarteNeural",
    "pt-PT-RaquelNeural",
    "ro-RO-AlinaNeural",
    "ro-RO-EmilNeural",
    "ru-RU-DmitryNeural",
    "ru-RU-SvetlanaNeural",
    "sr-RS-NicholasNeural",
    "sr-RS-SophieNeural",
    "si-LK-SameeraNeural",
    "si-LK-ThiliniNeural",
    "sk-SK-LukasNeural",
    "sk-SK-ViktoriaNeural",
    "sl-SI-PetraNeural",
    "sl-SI-RokNeural",
    "so-SO-MuuseNeural",
    "so-SO-UbaxNeural",
    "es-AR-ElenaNeural",
    "es-AR-TomasNeural",
    "es-BO-MarceloNeural",
    "es-BO-SofiaNeural",
    "es-CL-CatalinaNeural",
    "es-CL-LorenzoNeural",
    "es-CO-GonzaloNeural",
    "es-CO-SalomeNeural",
    "es-CR-JuanNeural",
    "es-CR-MariaNeural",
    "es-CU-BelkysNeural",
    "es-CU-ManuelNeural",
    "es-DO-EmilioNeural",
    "es-DO-RamonaNeural",
    "es-EC-AndreaNeural",
    "es-EC-LuisNeural",
    "es-SV-LorenaNeural",
    "es-SV-RodrigoNeural",
    "es-GQ-JavierNeural",
    "es-GQ-TeresaNeural",
    "es-GT-AndresNeural",
    "es-GT-MartaNeural",
    "es-HN-CarlosNeural",
    "es-HN-KarlaNeural",
    "es-MX-DaliaNeural",
    "es-MX-JorgeNeural",
    "es-MX-LorenzoEsCLNeural",
    "es-NI-FedericoNeural",
    "es-NI-YolandaNeural",
    "es-PA-MargaritaNeural",
    "es-PA-RobertoNeural",
    "es-PY-MarioNeural",
    "es-PY-TaniaNeural",
    "es-PE-AlexNeural",
    "es-PE-CamilaNeural",
    "es-PR-KarinaNeural",
    "es-PR-VictorNeural",
    "es-ES-AlvaroNeural",
    "es-ES-ElviraNeural",
    "es-ES-ManuelEsCUNeural",
    "es-US-AlonsoNeural",
    "es-US-PalomaNeural",
    "es-UY-MateoNeural",
    "es-UY-ValentinaNeural",
    "es-VE-PaolaNeural",
    "es-VE-SebastianNeural",
    "su-ID-JajangNeural",
    "su-ID-TutiNeural",
    "sw-KE-RafikiNeural",
    "sw-KE-ZuriNeural",
    "sw-TZ-DaudiNeural",
    "sw-TZ-RehemaNeural",
    "sv-SE-MattiasNeural",
    "sv-SE-SofieNeural",
    "ta-IN-PallaviNeural",
    "ta-IN-ValluvarNeural",
    "ta-MY-KaniNeural",
    "ta-MY-SuryaNeural",
    "ta-SG-AnbuNeural",
    "ta-SG-VenbaNeural",
    "ta-LK-KumarNeural",
    "ta-LK-SaranyaNeural",
    "te-IN-MohanNeural",
    "te-IN-ShrutiNeural",
    "th-TH-NiwatNeural",
    "th-TH-PremwadeeNeural",
    "tr-TR-AhmetNeural",
    "tr-TR-EmelNeural",
    "uk-UA-OstapNeural",
    "uk-UA-PolinaNeural",
    "ur-IN-GulNeural",
    "ur-IN-SalmanNeural",
    "ur-PK-AsadNeural",
    "ur-PK-UzmaNeural",
    "uz-UZ-MadinaNeural",
    "uz-UZ-SardorNeural",
    "vi-VN-HoaiMyNeural",
    "vi-VN-NamMinhNeural",
    "cy-GB-AledNeural",
    "cy-GB-NiaNeural",
    "zu-ZA-ThandoNeural",
    "zu-ZA-ThembaNeural"
]

# Country code to country name mapping
country_mapping = {
    'ZA': 'South Africa', 'AL': 'Albania', 'ET': 'Ethiopia', 'DZ': 'Algeria', 'BH': 'Bahrain',
    'EG': 'Egypt', 'IQ': 'Iraq', 'JO': 'Jordan', 'KW': 'Kuwait', 'LB': 'Lebanon', 'LY': 'Libya',
    'MA': 'Morocco', 'OM': 'Oman', 'QA': 'Qatar', 'SA': 'Saudi Arabia', 'SY': 'Syria',
    'TN': 'Tunisia', 'AE': 'United Arab Emirates', 'YE': 'Yemen', 'AZ': 'Azerbaijan',
    'BD': 'Bangladesh', 'IN': 'India', 'BA': 'Bosnia and Herzegovina', 'BG': 'Bulgaria',
    'MM': 'Myanmar', 'ES': 'Spain', 'HK': 'Hong Kong', 'CN': 'China', 'TW': 'Taiwan',
    'HR': 'Croatia', 'CZ': 'Czech Republic', 'DK': 'Denmark', 'BE': 'Belgium', 'NL': 'Netherlands',
    'AU': 'Australia', 'CA': 'Canada', 'IE': 'Ireland', 'KE': 'Kenya', 'NZ': 'New Zealand',
    'NG': 'Nigeria', 'PH': 'Philippines', 'SG': 'Singapore', 'TZ': 'Tanzania', 'GB': 'United Kingdom',
    'US': 'United States', 'EE': 'Estonia', 'FI': 'Finland', 'FR': 'France', 'CH': 'Switzerland',
    'GE': 'Georgia', 'AT': 'Austria', 'DE': 'Germany', 'GR': 'Greece', 'GU': 'India',  # Gujarati
    'IL': 'Israel', 'HU': 'Hungary', 'IS': 'Iceland', 'ID': 'Indonesia', 'IT': 'Italy',
    'JP': 'Japan', 'KN': 'India',  # Kannada
    'KZ': 'Kazakhstan', 'KH': 'Cambodia', 'KR': 'South Korea', 'LA': 'Laos', 'LV': 'Latvia',
    'LT': 'Lithuania', 'MK': 'North Macedonia', 'MY': 'Malaysia', 'ML': 'India',  # Malayalam
    'MT': 'Malta', 'MR': 'India',  # Marathi
    'MN': 'Mongolia', 'NP': 'Nepal', 'NO': 'Norway', 'AF': 'Afghanistan', 'IR': 'Iran',
    'PL': 'Poland', 'BR': 'Brazil', 'PT': 'Portugal', 'RO': 'Romania', 'RU': 'Russia',
    'RS': 'Serbia', 'LK': 'Sri Lanka', 'SK': 'Slovakia', 'SI': 'Slovenia', 'SO': 'Somalia',
    'AR': 'Argentina', 'BO': 'Bolivia', 'CL': 'Chile', 'CO': 'Colombia', 'CR': 'Costa Rica',
    'CU': 'Cuba', 'DO': 'Dominican Republic', 'EC': 'Ecuador', 'SV': 'El Salvador',
    'GQ': 'Equatorial Guinea', 'GT': 'Guatemala', 'HN': 'Honduras', 'MX': 'Mexico',
    'NI': 'Nicaragua', 'PA': 'Panama', 'PY': 'Paraguay', 'PE': 'Peru', 'PR': 'Puerto Rico',
    'UY': 'Uruguay', 'VE': 'Venezuela', 'SU': 'Indonesia',  # Sundanese
    'KE': 'Kenya', 'SE': 'Sweden', 'TA': 'India',  # Tamil
    'LK': 'Sri Lanka',  # Tamil
    'SG': 'Singapore',  # Tamil
    'MY': 'Malaysia',  # Tamil
    'TE': 'India',  # Telugu
    'TH': 'Thailand', 'TR': 'Turkey', 'UA': 'Ukraine', 'PK': 'Pakistan', 'UZ': 'Uzbekistan',
    'VN': 'Vietnam', 'CY': 'Wales', 'ZU': 'South Africa'  # Zulu
}

# Create a dictionary to group voices by country
voices_by_country = defaultdict(list)
for voice in edge_voices:
    country_code = voice.split('-')[1]
    country_name = country_mapping.get(country_code, country_code)
    voices_by_country[country_name].append(voice)

# Function to display voices for selected country
def display_voices(country):
    voices = voices_by_country.get(country, [])
    if not voices:
        return "No voices available for this country."
    return "\n".join(voices)

def check_internet_connection():
    """Check if internet connection is available"""
    try:
        import socket
        socket.create_connection(("8.8.8.8", 53), timeout=3)
        return True
    except OSError:
        return False

def chunk_text(text, max_length=4000):
    """Split text into chunks to avoid rate limits"""
    if len(text) <= max_length:
        return [text]
    
    chunks = []
    words = text.split()
    current_chunk = []
    current_length = 0
    
    for word in words:
        if current_length + len(word) + 1 <= max_length:
            current_chunk.append(word)
            current_length += len(word) + 1
        else:
            if current_chunk:
                chunks.append(" ".join(current_chunk))
                current_chunk = [word]
                current_length = len(word)
    
    if current_chunk:
        chunks.append(" ".join(current_chunk))
    
    return chunks

def try_groq_tts(api_key, text, voice):
    """Try Groq TTS with chunking and retry logic"""
    try:
        if not check_internet_connection():
            return None, "❌ No internet connection available for Groq TTS"
            
        client = Groq(api_key=api_key)
        
        # Check if text needs chunking
        chunks = chunk_text(text, 3500)  # Leave some buffer
        
        if len(chunks) == 1:
            # Single chunk - direct call
            response = client.audio.speech.create(
                model="playai-tts",
                voice=voice,
                input=text,
                response_format="wav"
            )
            
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
                response.write_to_file(temp_file.name)
                return temp_file.name, "✅ Speech generated successfully with Groq PlayAI!"
        else:
            # Multiple chunks - process separately and inform user
            return None, f"⚠️ Text too long for single request ({len(text)} chars). Try shorter text or use Edge TTS for longer content."
            
    except Exception as e:
        error_msg = str(e)
        if "rate_limit_exceeded" in error_msg:
            return None, "🔄 Groq rate limit reached. Switching to alternative providers..."
        elif "429" in error_msg:
            return None, "🔄 Groq rate limit reached. Switching to alternative providers..."
        else:
            return None, f"❌ Groq error: {error_msg}"

def try_openai_tts(api_key, text, voice):
    """Try OpenAI TTS as fallback"""
    try:
        if not check_internet_connection():
            return None, "❌ No internet connection available for OpenAI TTS"
            
        import openai
        client = openai.OpenAI(api_key=api_key)
        
        response = client.audio.speech.create(
            model="tts-1",
            voice=voice,
            input=text[:4096]  # OpenAI limit
        )
        
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
            response.stream_to_file(temp_file.name)
            return temp_file.name, "✅ Speech generated successfully with OpenAI TTS!"
            
    except ImportError:
        return None, "❌ OpenAI library not installed. Install with: pip install openai"
    except Exception as e:
        return None, f"❌ OpenAI error: {str(e)}"

def try_edge_tts(text, voice="en-US-JennyNeural"):
    """Try Microsoft Edge TTS as free fallback"""
    try:
        if not check_internet_connection():
            return None, "❌ No internet connection available for Edge TTS"
            
        import edge_tts
        import asyncio
        
        async def generate_edge_speech():
            communicate = edge_tts.Communicate(text, voice)  # No character limit for Edge TTS
            with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as temp_file:
                async for chunk in communicate.stream():
                    if chunk["type"] == "audio":
                        temp_file.write(chunk["data"])
                return temp_file.name
        
        # Run async function
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
        audio_file = loop.run_until_complete(generate_edge_speech())
        
        return audio_file, "✅ Speech generated successfully with Microsoft Edge TTS (Free & High Quality)!"
        
    except ImportError:
        return None, "❌ Edge TTS not installed. Install with: pip install edge-tts"
    except Exception as e:
        return None, f"❌ Edge TTS error: {str(e)}"

def try_pyttsx3_fallback(text):
    """Ultimate fallback using pyttsx3 (offline)"""
    try:
        import pyttsx3
        
        # Initialize the engine
        engine = pyttsx3.init()
        
        # Get available voices and set a good one
        voices = engine.getProperty('voices')
        if voices:
            # Try to find a female English voice first, then any English voice
            english_voice = None
            for voice in voices:
                voice_id = voice.id.lower()
                voice_name = voice.name.lower() if hasattr(voice, 'name') else ""
                
                # Look for English voices
                if any(keyword in voice_id or keyword in voice_name 
                       for keyword in ['english', 'en-us', 'en_us', 'zira', 'hazel', 'eva']):
                    english_voice = voice.id
                    if any(female_keyword in voice_name 
                           for female_keyword in ['zira', 'hazel', 'eva', 'female']):
                        break  # Prefer female voices
            
            if english_voice:
                engine.setProperty('voice', english_voice)
        
        # Set properties for better quality
        engine.setProperty('rate', 180)    # Speed of speech (words per minute)
        engine.setProperty('volume', 0.9)  # Volume level (0.0 to 1.0)
        
        # Create temporary file
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
            temp_path = temp_file.name
        
        # Limit text length for stability and split into sentences for better processing
        limited_text = text[:2000]  # Limit for stability
        
        # Use the save_to_file method correctly
        engine.save_to_file(limited_text, temp_path)
        engine.runAndWait()
        
        # Check if file was created and has content
        if os.path.exists(temp_path) and os.path.getsize(temp_path) > 0:
            return temp_path, "✅ Speech generated with offline TTS! (No internet required)"
        else:
            # If save_to_file didn't work, try alternative method
            return try_alternative_offline_tts(limited_text)
            
    except ImportError:
        return None, "❌ pyttsx3 not installed. Install with: pip install pyttsx3"
    except Exception as e:
        # Try alternative offline method if pyttsx3 fails
        return try_alternative_offline_tts(text[:2000])

def try_alternative_offline_tts(text):
    """Alternative offline TTS using system commands"""
    try:
        system = platform.system().lower()
        
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
            temp_path = temp_file.name
        
        if system == "windows":
            # Windows SAPI TTS
            try:
                import win32com.client
                speaker = win32com.client.Dispatch("SAPI.SpVoice")
                
                # Save to file
                file_stream = win32com.client.Dispatch("SAPI.SpFileStream")
                file_stream.Open(temp_path, 3)
                speaker.AudioOutputStream = file_stream
                speaker.Speak(text)
                file_stream.Close()
                
                if os.path.exists(temp_path) and os.path.getsize(temp_path) > 0:
                    return temp_path, "✅ Speech generated with Windows SAPI TTS (Offline)!"
            except ImportError:
                pass
                
        elif system == "darwin":  # macOS
            # Use macOS 'say' command
            import subprocess
            try:
                subprocess.run(['say', '-o', temp_path, '--data-format=LEF32@22050', text], 
                             check=True, timeout=30)
                if os.path.exists(temp_path) and os.path.getsize(temp_path) > 0:
                    return temp_path, "✅ Speech generated with macOS TTS (Offline)!"
            except (subprocess.CalledProcessError, subprocess.TimeoutExpired, FileNotFoundError):
                pass
                
        elif system == "linux":
            # Try espeak or festival on Linux
            import subprocess
            try:
                # Try espeak first
                subprocess.run(['espeak', '-w', temp_path, text], 
                             check=True, timeout=30)
                if os.path.exists(temp_path) and os.path.getsize(temp_path) > 0:
                    return temp_path, "✅ Speech generated with espeak TTS (Offline)!"
            except (subprocess.CalledProcessError, subprocess.TimeoutExpired, FileNotFoundError):
                try:
                    # Try festival as backup
                    subprocess.run(['text2wave', '-o', temp_path], 
                                 input=text, text=True, check=True, timeout=30)
                    if os.path.exists(temp_path) and os.path.getsize(temp_path) > 0:
                        return temp_path, "✅ Speech generated with Festival TTS (Offline)!"
                except (subprocess.CalledProcessError, subprocess.TimeoutExpired, FileNotFoundError):
                    pass
        
        return None, f"❌ No offline TTS available for {system}. Install: pip install pyttsx3"
        
    except Exception as e:
        return None, f"❌ Alternative offline TTS error: {str(e)}"

# Main function with multiple provider fallback
def generate_speech(groq_api_key, openai_api_key, text, voice_provider, voice):
    if not text:
        return None, "⚠️ Please enter some text to generate speech."

    # Apply 10,000 character limit for providers other than Edge TTS
    if voice_provider != "Edge TTS (Free)" and len(text) > 10000:
        return None, "🚫 Text input exceeds 10,000 character limit for this provider. Try Edge TTS for unlimited text length."

    # Check internet connection
    has_internet = check_internet_connection()
    internet_status = "🌐 Internet: Connected" if has_internet else "📴 Internet: Offline"
    
    # Status message
    status_msg = f"🔄 Generating speech...\n{internet_status}\n"
    
    # If no internet and user selected online provider, inform them
    if not has_internet and voice_provider in ["Groq (PlayAI)", "OpenAI TTS", "Edge TTS (Free)"]:
        status_msg += "⚠️ No internet connection. Using offline TTS...\n"
        audio_file, message = try_pyttsx3_fallback(text)
        if audio_file:
            return audio_file, status_msg + message
        else:
            return None, status_msg + message
    
    # Try providers in order based on selection
    if voice_provider == "Groq (PlayAI)" and groq_api_key and has_internet:
        status_msg += "🎯 Using Groq PlayAI...\n"
        audio_file, message = try_groq_tts(groq_api_key, text, voice)
        if audio_file:
            return audio_file, message
        else:
            status_msg += f"❌ Groq failed: {message}\n"
    
    # Fallback to OpenAI if available
    if openai_api_key and voice_provider in ["OpenAI TTS", "Auto (Try All)"] and has_internet:
        status_msg += "🔄 Trying OpenAI TTS...\n"
        openai_voice = voice if voice in openai_voices else "alloy"
        audio_file, message = try_openai_tts(openai_api_key, text, openai_voice)
        if audio_file:
            return audio_file, message
        else:
            status_msg += f"❌ OpenAI failed: {message}\n"
    
    # Try Edge TTS (Free) - Only if internet available
    if voice_provider in ["Edge TTS (Free)", "Auto (Try All)"] and (has_internet or not groq_api_key):
        if has_internet:
            status_msg += "🔄 Using Edge TTS (Free & High Quality)...\n"
            edge_voice = voice if voice in edge_voices else "en-US-JennyNeural"
            audio_file, message = try_edge_tts(text, edge_voice)
            if audio_file:
                return audio_file, message
            else:
                status_msg += f"❌ Edge TTS failed: {message}\n"
        else:
            status_msg += "❌ Edge TTS requires internet connection\n"
    
    # Ultimate fallback - pyttsx3 (offline) - ALWAYS TRY THIS IF OTHERS FAIL
    status_msg += "🔄 Using offline TTS (works without internet)...\n"
    audio_file, message = try_pyttsx3_fallback(text)
    if audio_file:
        return audio_file, status_msg + message
    else:
        status_msg += f"❌ Offline TTS failed: {message}\n"
    
    return None, status_msg + "❌ All TTS providers failed. Please check your setup or try shorter text."

def update_voice_options(provider):
    """Update voice dropdown based on selected provider"""
    if provider == "Groq (PlayAI)":
        return gr.Dropdown(choices=groq_voices, value="Fritz-PlayAI", visible=True)
    elif provider == "OpenAI TTS":
        return gr.Dropdown(choices=openai_voices, value="alloy", visible=True)
    elif provider == "Edge TTS (Free)":
        return gr.Dropdown(choices=edge_voices, value="en-US-JennyNeural", visible=True)
    elif provider == "Offline TTS":
        return gr.Dropdown(choices=["Default System Voice"], value="Default System Voice", visible=True)
    else:  # Auto
        return gr.Dropdown(choices=groq_voices, value="Fritz-PlayAI", visible=True, label="🎭 Voice (Auto mode will try best match)")

# Custom CSS (unchanged)
custom_css = """
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
* {
    box-sizing: border-box;
}
:root {
    --primary-gradient: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    --secondary-gradient: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
    --accent-gradient: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
    --dark-bg: linear-gradient(135deg, #0c0c0c 0%, #1a1a2e 50%, #16213e 100%);
    --glass-bg: rgba(255, 255, 255, 0.08);
    --glass-border: rgba(255, 255, 255, 0.15);
    --text-primary: #ffffff;
    --text-secondary: rgba(255, 255, 255, 0.7);
    --shadow-primary: 0 8px 32px rgba(0, 0, 0, 0.4);
    --shadow-hover: 0 12px 48px rgba(0, 0, 0, 0.6);
    --border-radius: 16px;
}

body, .gradio-container {
    background: var(--dark-bg) !important;
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
    color: var(--text-primary) !important;
    overflow-x: hidden;
}

.gradio-container {
    max-width: 1400px !important;
    margin: 40px auto !important;
    padding: 0 20px !important;
    min-height: 100vh;
}

.gradio-container > div {
    background: var(--glass-bg) !important;
    backdrop-filter: blur(20px) !important;
    border: 1px solid var(--glass-border) !important;
    border-radius: var(--border-radius) !important;
    padding: 40px !important;
    box-shadow: var(--shadow-primary) !important;
    position: relative;
    overflow: hidden;
}

h1 {
    text-align: center !important;
    font-size: clamp(2.5rem, 5vw, 4rem) !important;
    font-weight: 700 !important;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
    -webkit-background-clip: text !important;
    -webkit-text-fill-color: transparent !important;
    background-clip: text !important;
    margin: 0 0 50px 0 !important;
    animation: glow 3s ease-in-out infinite alternate;
}

@keyframes glow {
    0% { filter: drop-shadow(0 0 20px rgba(102, 126, 234, 0.3)); }
    100% { filter: drop-shadow(0 0 30px rgba(118, 75, 162, 0.5)); }
}

#generate-btn {
    background: linear-gradient(135deg, #00f2fe 0%, #4facfe 100%) !important;
    border: 2px solid #4facfe !important;
    color: #ffffff !important;
    font-weight: bold !important;
    box-shadow: 0 0 12px rgba(0, 242, 254, 0.5) !important;
    transition: all 0.3s ease !important;
    margin-top: 8.5px !important;
}

#generate-btn:hover {
    background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%) !important;
    transform: scale(1.03) !important;
    box-shadow: 0 0 18px rgba(0, 242, 254, 0.7) !important;
}

.gr-textbox, .gr-dropdown {
    background: var(--glass-bg) !important;
    border: 2px solid transparent !important;
    border-radius: 12px !important;
    position: relative;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
    backdrop-filter: blur(10px) !important;
}

.gr-textbox textarea, .gr-textbox input, .gr-dropdown select {
    background: transparent !important;
    color: var(--text-primary) !important;
    border: none !important;
    font-size: 16px !important;
    font-weight: 400 !important;
    padding: 16px !important;
}

.gr-input-label, .gr-output-label {
    color: var(--text-primary) !important;
    font-weight: 600 !important;
    font-size: 14px !important;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    margin-bottom: 12px !important;
    background: var(--accent-gradient);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}

.gr-button {
    background: var(--primary-gradient) !important;
    border: none !important;
    color: white !important;
    font-weight: 600 !important;
    font-size: 16px !important;
    padding: 16px 32px !important;
    border-radius: 12px !important;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    box-shadow: 0 4px 20px rgba(102, 126, 234, 0.3) !important;
    margin-top: 20px !important;
}

.gr-button:hover {
    transform: translateY(-2px) !important;
    box-shadow: var(--shadow-hover) !important;
    filter: brightness(1.1);
}

.gr-audio {
    background: var(--glass-bg) !important;
    border: 1px solid var(--glass-border) !important;
    border-radius: 12px !important;
    padding: 20px !important;
    backdrop-filter: blur(10px) !important;
    transition: all 0.3s ease !important;
}

.info-box {
    background: rgba(0, 242, 254, 0.1) !important;
    border: 1px solid rgba(0, 242, 254, 0.3) !important;
    border-radius: 12px !important;
    padding: 20px !important;
    margin: 20px 0 !important;
    backdrop-filter: blur(10px) !important;
}

.info-box,
.info-box * {
    color: white !important;
}

.warning-box,
.warning-box * {
    color: white !important;
}

.no-api-box {
    background: rgba(46, 204, 113, 0.1) !important;
    border: 1px solid rgba(46, 204, 113, 0.3) !important;
    border-radius: 12px !important;
    padding: 20px !important;
    margin: 20px 0 !important;
    backdrop-filter: blur(10px) !important;
}

.no-api-box,
.no-api-box * {
    color: white !important;
}

.warning-box {
    background: rgba(255, 193, 7, 0.1) !important;
    border: 1px solid rgba(255, 193, 7, 0.3) !important;
    border-radius: 12px !important;
    padding: 15px !important;
    margin: 15px 0 !important;
    backdrop-filter: blur(10px) !important;
}

.offline-box {
    background: rgba(255, 87, 34, 0.1) !important;
    border: 1px solid rgba(255, 87, 34, 0.3) !important;
    border-radius: 12px !important;
    padding: 20px !important;
    margin: 20px 0 !important;
    backdrop-filter: blur(10px) !important;
}

.offline-box,
.offline-box * {
    color: white !important;
}

#voice-selector-header h3{
    text-align: center !important;
    font-size: 1.5rem !important;
    font-weight: 600 !important;
    margin-bottom: 20px !important;
    color: white !important;
}

"""

custom_html = """
<div style="text-align: center; margin-bottom: 20px;">
    <div style="font-size: 3rem;">🎙️</div>
    <h1>Advanced Multi-Provider TTS Studio</h1>
    <p style="color: rgba(255, 255, 255, 0.7); font-size: 18px; margin: 0; font-weight: 300;">
        Transform your text into natural-sounding speech with multiple AI-powered voice providers
    </p>
    
    <div class="offline-box">
        <h3>📴 No Internet? No Problem!</h3>
        <p><strong>Select "Offline TTS" to use system TTS without any internet connection!</strong></p>
        <p>✅ Works completely offline but in local pc not in HF space env • ✅ No API keys needed • ✅ Always available as fallback • 🚫 10,000 char limit</p>
    </div>
    
    <div class="no-api-box">
        <h3>🆓 No API Key? Multiple Free Options!</h3>
        <p><strong>Select "Edge TTS (Free)" for online high-quality TTS with no character limit or "Offline TTS" for no internet!</strong></p>
        <p>✅ Edge TTS: High quality voices with internet, unlimited text and various language support • ✅ Offline TTS: Basic quality, works anywhere, 10,000 char limit</p>
    </div>
    
    <div class="info-box">
        <p><strong>🔄 Multiple Providers Available:</strong> Groq PlayAI, OpenAI TTS, Microsoft Edge TTS (Free), Offline TTS</p>
        <p><strong>🛡️ Smart Fallback System:</strong> If one provider fails, automatically tries the next available</p>
        <p><strong>💡 Recommended:</strong> Use "Auto (Try All)" for maximum reliability or specific providers based on your needs</p>
        <p><strong>📏 Text Limits:</strong> Edge TTS (Unlimited), Groq/OpenAI/Offline (10,000 chars)</p>
    </div>
</div>
"""

# Gradio interface
with gr.Blocks(css=custom_css, theme="ocean") as demo:
    gr.HTML(custom_html)

    # Warning box for users without API keys
    gr.HTML("""
    <div class="warning-box">
        <p><strong>⚠️ Important:</strong> If you don't have API keys or internet, you have multiple options:</p>
        <ul>
            <li><strong>With Internet:</strong> Select "Edge TTS (Free)" - High quality, no API key needed, unlimited text</li>
            <li><strong>Without Internet:</strong> Select "Offline TTS" - Basic quality, works completely offline, 10,000 char limit</li>
            <li><strong>Best Experience:</strong> Use "Auto (Try All)" to automatically use the best available option</li>
        </ul>
    </div>
    """)

    # API Keys section
    with gr.Row():
        with gr.Column():
            groq_api_key = gr.Textbox(
                label="🔐 Groq API Key (Optional)",
                placeholder="Optional: Paste your Groq API key here for PlayAI voices...",
                type="password",
                lines=1
            )
        with gr.Column():
            openai_api_key = gr.Textbox(
                label="🔐 OpenAI API Key (Optional)",
                placeholder="Optional: OpenAI API key for premium TTS voices...",
                type="password",
                lines=1
            )

    with gr.Row():
        with gr.Column(scale=3):
            text_input = gr.Textbox(
                label="📝 Enter Your Text",
                placeholder="Type or paste your text here... (Edge TTS: Unlimited, Others: Max 10,000 characters)",
                lines=8,
                max_lines=12
            )

            with gr.Row():
                provider_dropdown = gr.Dropdown(
                    choices=["Auto (Try All)", "Edge TTS (Free)", "Offline TTS", "Groq (PlayAI)", "OpenAI TTS"],
                    label="🔧 TTS Provider",
                    value="Auto (Try All)",
                    scale=1
                )
                voice_dropdown = gr.Dropdown(
                    choices=groq_voices,
                    label="🎭 Select Voice",
                    value="Fritz-PlayAI",
                    scale=2
                )
                generate_button = gr.Button("🚀 Generate Speech", scale=1, elem_id="generate-btn")

        with gr.Column(scale=2):
            audio_output = gr.Audio(
                label="🔊 Generated Audio",
                type="filepath"
            )
            status_output = gr.Textbox(
                label="📊 Status & Progress",
                placeholder="Ready to generate speech... 'Auto' mode will use the best available provider!",
                interactive=False,
                lines=6
            )
    
    gr.Markdown("### Voice Selector by Country", elem_id="voice-selector-header")
    country_dropdown = gr.Dropdown(
        choices=sorted(voices_by_country.keys()),
        label="Select Country (Applicable for Edge TTS voices)",
    )
    voice_output = gr.Textbox(label="Available Voices", lines=10)
    country_dropdown.change(fn=display_voices, inputs=country_dropdown, outputs=voice_output)

    # Event handlers
    generate_button.click(
        fn=generate_speech,
        inputs=[groq_api_key, openai_api_key, text_input, provider_dropdown, voice_dropdown],
        outputs=[audio_output, status_output]
    )

    # Update voice options when provider changes
    provider_dropdown.change(
        fn=update_voice_options,
        inputs=[provider_dropdown],
        outputs=[voice_dropdown]
    )

    # Character counter with dynamic recommendations
    def update_status_text(text):
        char_count = len(text) if text else 0
        base_msg = f"Characters: {char_count}"
        
        if char_count == 0:
            return base_msg + " • Ready to generate speech!"
        elif char_count > 10000:
            return base_msg + " • Use 'Edge TTS' for unlimited text length! Other providers limited to 10,000 chars."
        elif char_count > 3000:
            return base_msg + " • For long texts, 'Edge TTS' or 'Offline TTS' work best!"
        else:
            return base_msg + " • All providers available for this text length!"
    
    text_input.change(
        fn=update_status_text,
        inputs=[text_input],
        outputs=[status_output]
    )

    # Installation and usage instructions
    gr.HTML("""
    <div class="info-box" style="margin-top: 30px;">        
        <h3>🎯 Usage Options:</h3>
        <div style="margin: 15px 0;">
            <p><strong>📴 Offline Option (Always Works):</strong></p>
            <ul>
                <li>Select <strong>"Offline TTS"</strong> - No internet or API key needed!</li>
                <li>Uses your system's built-in TTS engine</li>
                <li>Works on Windows, macOS, and Linux</li>
                <li>Basic quality but always reliable</li>
                <li>🚫 Limited to 10,000 characters</li>
            </ul>
        </div>
        
        <div style="margin: 15px 0;">
            <p><strong>🆓 Free Online Option (High Quality):</strong></p>
            <ul>
                <li>Select <strong>"Edge TTS (Free)"</strong> - No API key needed!</li>
                <li>High-quality Microsoft voices</li>
                <li>✅ Unlimited text length</li>
                <li>Multiple English voice options</li>
                <li>Requires internet connection</li>
            </ul>
        </div>
        
        <div style="margin: 15px 0;">
            <p><strong>🔑 Premium Options (Optional):</strong></p>
            <ul>
                <li><strong>Groq PlayAI:</strong> Get free API key at <a href="https://console.groq.com" target="_blank">console.groq.com</a> (10,000 char limit but usually works in short length text)</li>
                <li><strong>OpenAI TTS:</strong> Get API key at <a href="https://platform.openai.com" target="_blank">platform.openai.com</a> (10,000 char limit but usually works in short length text)</li>
            </ul>
        </div>
        
        <div style="margin: 15px 0;">
            <p><strong>🚀 Smart Auto Mode:</strong></p>
            <ul>
                <li>Select <strong>"Auto (Try All)"</strong> for maximum reliability</li>
                <li>Automatically detects internet connection</li>
                <li>Uses premium APIs if available, falls back to free options</li>
                <li>Always tries offline TTS as final fallback</li>
            </ul>
        </div>
        
        <div style="margin: 15px 0;">
            <p><strong>💡 Tips:</strong></p>
            <ul>
                <li>No internet? Use <strong>"Offline TTS"</strong> - it always works! (10,000 char limit but usually works in short length text)</li>
                <li>Want quality without API keys? Use <strong>"Edge TTS (Free)"</strong> - unlimited text</li>
                <li>For maximum reliability, use <strong>"Auto (Try All)"</strong></li>
                <li>App automatically detects your connection status</li>
            </ul>
        </div>
        <p style="margin-top: 15px;">Enjoy generating high-quality speech with ease! 🎤</p>
    </div>
    """)

# Run the app
if __name__ == "__main__":
    demo.launch(share=True)
