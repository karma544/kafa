import streamlit as st
import sqlite3
from datetime import datetime
import base64

# --- 1. SAYFA VE ARKA PLAN AYARLARI ---
st.set_page_config(page_title="B ❤️", page_icon="💬", layout="centered")

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
        .stMarkdown, .stSubheader, .stTitle, p, h1, h2, h3, h4, span, label {{
            text-shadow: 1px 1px 3px rgba(0,0,0,0.8) !important;
        }}
        /* WhatsApp Sohbet Balonları Tasarımı */
        .chat-bubble-container {{
            display: flex;
            flex-direction: column;
            gap: 8px;
            margin-bottom: 15px;
            width: 100%;
        }}
        .bubble {{
            display: inline-block;
            padding: 10px 14px;
            border-radius: 14px;
            max-width: 75%;
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
            font-size: 15px;
            line-height: 1.4;
            box-shadow: 0px 1px 1px rgba(0,0,0,0.2);
            text-shadow: none !important;
        }}
        .bubble-sender {{
            background-color: #dcf8c6;
            color: #111b21;
            align-self: flex-end;
            text-align: left;
            border-bottom-right-radius: 2px;
        }}
        .bubble-receiver {{
            background-color: #f0f2f5;
            color: #111b21;
            align-self: flex-start;
            text-align: left;
            border-bottom-left-radius: 2px;
        }}
        .bubble-title {{
            font-weight: bold;
            font-size: 12px;
            margin-bottom: 2px;
            display: block;
        }}
        .bubble-sender .bubble-title {{ color: #008069; }}
        .bubble-receiver .bubble-title {{ color: #53bdeb; }}
        .bubble-time {{
            font-size: 10px;
            color: #667781;
            float: right;
            margin-top: 5px;
            margin-left: 10px;
        }}
        /* Alt kısımdaki giriş kutusunun gölgesini sıfırlama */
        div[data-testid="stChatInput"] {{
            text-shadow: none !important;
        }}
        </style>
        '''
        st.markdown(page_bg_img, unsafe_allow_html=True)
    except FileNotFoundError:
        pass

# Arka planı yükle
set_png_as_page_bg(IMAGE_FILE)


# --- 2. SQLITE VERİTABANI SİSTEMİ ---
DB_NAME = "chat.db"

def init_db():
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user TEXT NOT NULL,
                text TEXT NOT NULL,
                timestamp DATETIME NOT NULL
            )
        """)
        conn.commit()

def save_message(user, text):
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO messages (user, text, timestamp) VALUES (?, ?, ?)",
            (user, text, datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        )
        conn.commit()

def get_last_50_messages():
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT user, text, timestamp FROM messages ORDER BY timestamp DESC LIMIT 50"
        )
        rows = cursor.fetchall()
        return rows[::-1] # Eskiden yeniye sıralama

init_db()


# --- 3. GİRİŞ SİSTEMİ ---
USER_CREDENTIALS = {
    "bennur": "alperen",
    "alperen": "bennur"
}

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.username = ""

if not st.session_state.logged_in:
    st.title("❤️ Keje Giriş")
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


# --- 4. GİRİŞ SONRASI SIDEBAR VE BAŞLIK ---
with st.sidebar:
    st.write(f"❤️ Kullanıcı: **{st.session_state.username.capitalize()}**")
    st.write("---")
    st.write("🎵 Arka Plan Müziği")
    try:
        with open("kafa.mp3", "rb") as f:
            audio_bytes = f.read()
        st.audio(audio_bytes, format="audio/mp3", autoplay=True, loop=True)
    except FileNotFoundError:
        st.warning("kafa.mp3 dosyası klasörde bulunamadı.")

    st.write("---")
    if st.button("Çıkış Yap"):
        st.session_state.logged_in = False
        st.session_state.username = ""
        st.rerun()

st.title(f"💬 Hi bitch, {st.session_state.username.capitalize()}! ❤️")
st.caption("✨ ozeloda.")
st.write("---")


# --- 5. OTOMATİK YENİLENEN MESAJ ALANI ---
# st.fragment sayesinde sadece bu alan 3 saniyede bir veritabanını kontrol edip güncellenir.
@st.fragment(run_every=3)
def show_messages_live():
    messages = get_last_50_messages()
    
    for sender, text, msg_time in messages:
        try:
            time_str = datetime.strptime(msg_time, "%Y-%m-%d %H:%M:%S").strftime("%H:%M")
        except ValueError:
            time_str = msg_time
        
        if sender == st.session_state.username:
            st.markdown(
                f"""
                <div class="chat-bubble-container">
                    <div class="bubble bubble-sender">
                        <span class="bubble-title">Sen</span>
                        {text}
                        <span class="bubble-time">{time_str}</span>
                    </div>
                </div>
                """, unsafe_allow_html=True
            )
        else:
            st.markdown(
                f"""
                <div class="chat-bubble-container">
                    <div class="bubble bubble-receiver">
                        <span class="bubble-title">{sender.capitalize()}</span>
                        {text}
                        <span class="bubble-time">{time_str}</span>
                    </div>
                </div>
                """, unsafe_allow_html=True
            )

# Mesajları yukarıya yerleştiriyoruz
show_messages_live()


# --- 6. EN ALTTA SABİT SOHBET GİRİŞİ ---
# st.chat_input, yapısı gereği sayfanın en altına yapışık durur.
user_msg = st.chat_input("Seni seviyorum...")

if user_msg:
    if user_msg.strip():
        save_message(st.session_state.username, user_msg.strip())
        st.rerun()
