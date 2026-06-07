import streamlit as st
from google.cloud import firestore
from datetime import datetime
import base64

# --- 1. SAYFA VE ARKA PLAN AYARLARI ---
st.set_page_config(page_title="Kancalarija ", page_icon="💬", layout="centered")

IMAGE_FILE = "arkaplan.jpg" 

def get_base64_of_bin_file(bin_file):
    with open(bin_file, 'rb') as f:
        data = f.read()
    return base64.b64encode(data).decode()

def set_png_as_page_bg(png_file):
    try:
        bin_str = get_base64_of_bin_file(png_file)
        page_bg_img = f'''
        <style>
        .stApp {{
            background-image: url("data:image/png;base64,{bin_str}");
            background-size: cover;
            background-position: center;
            background-repeat: no-repeat;
            background-attachment: fixed;
        }}
        /* Yazıların fotoğraf üzerinde okunabilmesi için gölge ayarı */
        .stMarkdown, .stSubheader, .stTitle, p, span {{
            text-shadow: 1px 1px 3px rgba(0,0,0,0.8);
        }}
        </style>
        '''
        st.markdown(page_bg_img, unsafe_allow_html=True)
    except FileNotFoundError:
        pass

# Arka planı yükle
set_png_as_page_bg(IMAGE_FILE)


# --- 2. FIREBASE BAĞLANTISI ---
@st.cache_resource
def get_db():
    try:
        return firestore.Client.from_service_account_json("firebase_key.json")
    except Exception as e:
        return None

db = get_db()

if db is None:
    st.error("Firebase bağlantı dosyası (firebase_key.json) bulunamadı! Lütfen klasöre ekleyin.")
    st.stop()


# --- 3. ÖZEL GİRİŞ SİSTEMİ ---
USER_CREDENTIALS = {
    "bennur": "alperen",     # Kız arkadaşının giriş bilgileri
    "alperen": "bennur"      # Senin giriş bilgilerin
}

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.username = ""

if not st.session_state.logged_in:
    st.title("❤️ Kancalarija'a Giriş")
    username = st.text_input("Kullanıcı Adı:").lower().strip()
    password = st.text_input("Şifre:", type="password")
    
    if st.button("Giriş Yap"):
        if username in USER_CREDENTIALS and USER_CREDENTIALS[username] == password:
            st.session_state.logged_in = True
            st.session_state.username = username
            st.rerun()
        else:
            st.error("Kullanıcı adı veya şifre hatalı!")
    st.stop()


# --- 4. GİRİŞ BAŞARILI OLMUŞSA ÇALIŞACAK KISIM ---

# Yan Menüye Müzik ve Çıkış Butonunu Koyuyoruz
with st.sidebar:
    st.write(f"❤️ Kullanıcı: **{st.session_state.username.capitalize()}**")
    st.write("---")
    
    st.write("🎵 Arka Plan Müziği")
    try:
        with open("kafa.mp3", "rb") as f:
            audio_bytes = f.read()
        st.audio(audio_bytes, format="audio/mp3", autoplay=True, loop=True)
    except FileNotFoundError:
        st.warning("kafa.mp3 dosyası klasörde bulunamadı, müzik yüklenemedi.")

    st.write("---")
    if st.button("Çıkış Yap"):
        st.session_state.logged_in = False
        st.session_state.username = ""
        st.rerun()

# Ana Sayfa Başlıkları (Senin yazdığın yeni metinler)
st.title(f"💬 Hi bitch, {st.session_state.username.capitalize()}! ❤️")
st.caption("selam ben yazi yazmasini ogrendim")


# --- 5. MESAJ GÖNDERME SİSTEMİ (SUNUCU UYUMLU) ---
st.subheader("Mesaj Gönder")

# İnternet sunucusunda takılma yapmayan kararlı text_input yapısı
user_msg = st.text_input("Mesajını yaz ve Gönder'e bas...", placeholder="Seni seviyorum...", key="msg_input")

if st.button("Gönder ✨"):
    if user_msg.strip():
        # Sunucu saat farklarını ezmek için doğrudan yerel zamanı gönderiyoruz
        current_time = datetime.now()
        
        db.collection("messages").add({
            "user": st.session_state.username,
            "text": user_msg,
            "timestamp": current_time
        })
        st.rerun()

st.write("---")


# --- 6. MESAJLARI EKRENA YAZDIRMA (SUNUCU UYUMLU) ---
st.subheader("Mesaj Geçmişi")

messages_ref = db.collection("messages").order_by("timestamp", direction=firestore.Query.DESCENDING).limit(50)

try:
    messages = messages_ref.stream()
    
    for msg in messages:
        data = msg.to_dict()
        sender = data.get("user", "Bilinmeyen")
        text = data.get("text", "")
        time = data.get("timestamp")
        
        # Zaman damgasını güvenli bir şekilde string'e çeviriyoruz
        if time:
            time_str = time.strftime("%H:%M")
        else:
            time_str = datetime.now().strftime("%H:%M")
        
        if sender == st.session_state.username:
            # Senin veya o an giriş yapanın mesajları (Sağda, Yeşil Balon)
            st.markdown(
                f"""
                <div style='text-align: right; margin-bottom: 10px;'>
                    <div style='background-color: #dcf8c6; color: black; display: inline-block; padding: 10px; border-radius: 15px; max-width: 70%; text-align: left;'>
                        <b>Sen</b> <small style='color: gray; font-size: 10px;'>{time_str}</small><br>{text}
                    </div>
                </div>
                """, unsafe_allow_html=True
            )
        else:
            # Karşı tarafın mesajları (Solda, Gri Balon)
            st.markdown(
                f"""
                <div style='text-align: left; margin-bottom: 10px;'>
                    <div style='background-color: #f0f2f5; color: black; display: inline-block; padding: 10px; border-radius: 15px; max-width: 70%;'>
                        <b>{sender.capitalize()}</b> <small style='color: gray; font-size: 10px;'>{time_str}</small><br>{text}
                    </div>
                </div>
                """, unsafe_allow_html=True
            )
except Exception as e:
    st.error(f"Mesajlar yüklenirken bir hata oluştu: {e}")

# Manuel yenileme buronu
if st.button("Mesajları Yenile 🔄"):
    st.rerun()
