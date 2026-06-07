import streamlit as st
from google.cloud import firestore
from datetime import datetime
import base64

# --- 1. SAYFA VE ARKA PLAN AYARLARI ---
st.set_page_config(page_title="Kancalarija ❤️", page_icon="💬", layout="centered")

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
        .stMarkdown, .stSubheader, .stTitle, p, span {{
            text-shadow: 1px 1px 3px rgba(0,0,0,0.8);
        }}
        </style>
        '''
        st.markdown(page_bg_img, unsafe_allow_html=True)
    except FileNotFoundError:
        pass

set_png_as_page_bg(IMAGE_FILE)


# --- 2. FIREBASE BAĞLANTISI (KOD İÇİNE GÖMÜLÜ) ---
@st.cache_resource
def get_db():
    firebase_info = {
        "type": "service_account",
        "project_id": "kafa-11312",
        "private_key_id": "7d51aaef32a9ee733545209628a728c68264cb01",
        # .replace() ekledik ki sunucuda alt satırlar bozulmasın
        "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvgIBADANBgkqhkiG9w0BAQEFAASCBKgwggSkAgEAAoIBAQCnO7Y2ThPX7Dzp\nnugtKPsfFlyZdfulm6Ctufpf4+rr4t/p4du9X4TYvHpktUUIF8cddiUKkYsu4Med\nzbu+UlfIQ0AV3Br4/g9gbzT/e0x2spS4nVqF7aDPx0jZisp5O/cPt1M716MQSfbk\ntaQ2rtoeJND8NvrvM1KoOPoglN1US8gQjg8C3IUgz84REBxzGwP2amcIJoY59p2Q\nUxR8weG3LZdjPlmnF9oAkLPZbfl4oSPuq/15lMGSP7ZqH/VBMUiRcnS7RKwauvFs\nclXalIMGriMOZSo9SN+u5clRlackTvvZAfkZQbYabFLeJQnjA57JLZkEkSvV/Dp6\nfUySWzNLAgMBAAECggEABuuBwtgS0UZZ9AzV/vBkwFr9z+6vdKFKGz0Rk6A1LaVS\n934qEXAj+9fx4k5dWMH0RJiJpdkFWl9gwzJ0CH3wEWKjlPGyiAdg/hSy0Epo1gNo\nTOGk2kkEhutd/1guwF+BkBdZeoEoNTUO4jAqi88B3Gm+cly9xJj8XHld87Uwq/bw\niM4W5F9c2EC24ZsKIARcIziY6vq0pO45XFoJEPtGTbm/fS35ZLXI7huSaeANsTtt\nbwYQ5gai4AK2wQsoCF5hrioYhVzpZpoVT7td4FKxz3iAChCb7zqSAGSsUmj8lhnP\nm18swhoy5kRUlS9ReG/dVDIamdI+50SQhqExFjNA4QKBgQDSa4MxfER1cPZwh9SM\nCyCVEir6gLTG8dFsm8/ZDE6a6i9nV5xd1LUdeTEYY0dpUZi8MMn79tphqEBVRAnv\nbwA1ytLLFOCo5vQXKVyStmSp5bzt35CBSLE9V6oNmCpx3ypTKkDJkKy/wK+fLUQz\ngGi9iwdPz1m7GLF9wGzFJrphOwKBgQDLdVoVDpLgL5nLXFwMudhMtE3QSF3WWY3o\nVX3hHC+lRLbsFYcsghoHPIwusnt0zao5r43jnhgVP/Q/vZEBbdh3o2EsJhLIfaIL\nb2Ao4VMZzeGR8ENWbKmI81Wqk3e8l2HbnVMdvyLDyfiGgWd/i+ux8Us6qe/NmCKO\nQASpTNJVMQKBgQCc8UWj9izVb5DP8++rGG2P4kIeHzs2m4x5Nmm7WLuUPhFnQehF\n7+26cvcUWpAb1JlX3Af7H25YonaBYkMKy77bYFEC2aqLL99lGxuJ7fJ86faVcUdF\ntmND/ou+of0ee7YE26IA9SBz0RLsZYXV5/O3U+f7NguWSd+wjIJUNgOTmwKBgQCg\nObOOX6LFUFdCcmK/VuADT/7zpvnXI0GBFUqDq+nNsjaH51BDedW7mzAeWkqlKo4C\nzcDk3wzCN1JHnCcExBez6ANPfFBQebfSX4yPxRrneF5KyraM6hf9FPyCz419BI55\nIAVjqLFdFMJWUrRKGsurn4WKFmgWNdgIxFunZCtEEQKBgDsgFR282I8KKqCioH2A\nh4ayyRzKA3KQqnXjDP4OmwksdyT/7h+13Lpg3ax7iV83D1N/xTVNo61JlM9lNulO\nJ+3gnHAPhWsRgt7sTtRHBo0u/Nk4nyeU7k1RTxqIGgQcqoAvPIwu32eNn3JHrX0S\nGExvtzQml+j2tnSq3ha5ODP4\n-----END PRIVATE KEY-----\n".replace("\\n", "\n"),
        "client_email": "firebase-adminsdk-fbsvc@kafa-11312.iam.gserviceaccount.com",
        "client_id": "103935323611794625062",
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
        "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
        "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/firebase-adminsdk-fbsvc%40kafa-11312.iam.gserviceaccount.com",
        "universe_domain": "googleapis.com"
    }
    try:
        return firestore.Client.from_service_account_info(firebase_info)
    except Exception as e:
        st.error(f"Firebase bağlantı hatası: {e}")
        return None

db = get_db()

if db is None:
    st.stop()


# --- 3. ÖZEL GİRİŞ SİSTEMİ ---
USER_CREDENTIALS = {
    "bennur": "alperen",     
    "alperen": "bennur"      
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
with st.sidebar:
    st.write(f"❤️ Kullanıcı: **{st.session_state.username.capitalize()}**")
    st.write("---")
    st.write("🎵 Arka Plan Müziği")
    try:
        with open("kafa.mp3", "rb") as f:
            audio_bytes = f.read()
        st.audio(audio_bytes, format="audio/mp3", autoplay=True, loop=True)
    except FileNotFoundError:
        st.warning("kafa.mp3 dosyası bulunamadı.")

    st.write("---")
    if st.button("Çıkış Yap"):
        st.session_state.logged_in = False
        st.session_state.username = ""
        st.rerun()

st.title(f"💬 Hi bitch, {st.session_state.username.capitalize()}! ❤️")
st.caption("selam ben yazi yazmasini ogrendim")


# --- 5. MESAJ GÖNDERME SİSTEMİ ---
st.subheader("Mesaj Gönder")
user_msg = st.text_input("Mesajını yaz ve Gönder'e bas...", placeholder="Seni seviyorum...", key="msg_input")

if st.button("Gönder ✨"):
    if user_msg.strip():
        current_time = datetime.now()
        db.collection("messages").add({
            "user": st.session_state.username,
            "text": user_msg,
            "timestamp": current_time
        })
        st.rerun()

st.write("---")


# --- 6. MESAJLARI EKRANA YAZDIRMA ---
st.subheader("Mesaj Geçmişi")
messages_ref = db.collection("messages").order_by("timestamp", direction=firestore.Query.DESCENDING).limit(50)

try:
    messages = messages_ref.stream()
    for msg in messages:
        data = msg.to_dict()
        sender = data.get("user", "Bilinmeyen")
        text = data.get("text", "")
        time = data.get("timestamp")
        
        if time:
            time_str = time.strftime("%H:%M")
        else:
            time_str = datetime.now().strftime("%H:%M")
        
        if sender == st.session_state.username:
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

if st.button("Mesajları Yenile 🔄"):
    st.rerun()
