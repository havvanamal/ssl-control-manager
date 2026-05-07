import streamlit as st
import requests
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
import os

st.set_page_config(
    page_title="SSL Control Manager",
    page_icon="🔒",
    layout="wide",
    initial_sidebar_state="expanded"
)

API_URL = os.getenv("BACKEND_URL", "http://localhost:9000")

# --- Professional Light Theme CSS ---
st.markdown("""
<style>
    /* Global Base */
    .stApp {
        background-color: #f8f9fa;
        color: #212529;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
    }
    
    /* Headers */
    h1, h2, h3, h4, h5, h6 {
        color: #2c3e50;
        font-weight: 600;
    }
    
    /* Login Form */
    [data-testid="stForm"] {
        background-color: #ffffff;
        padding: 2rem;
        border-radius: 12px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05), 0 1px 3px rgba(0, 0, 0, 0.1);
        border: 1px solid #e9ecef;
    }
    
    /* Metric Cards */
    div[data-testid="stMetricValue"] {
        font-size: 2rem;
        font-weight: 700;
        color: #2c3e50;
    }
    div[data-testid="stMetricLabel"] {
        font-size: 1rem;
        color: #6c757d;
        font-weight: 500;
    }
    
    /* Buttons */
    .stButton>button {
        border-radius: 6px;
        font-weight: 500;
        transition: all 0.2s ease-in-out;
    }
    
    /* DataFrame */
    [data-testid="stDataFrame"] {
        background-color: #ffffff;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.02);
        border: 1px solid #e9ecef;
    }
    
    /* Sidebar */
    [data-testid="stSidebar"] {
        background-color: #ffffff;
        border-right: 1px solid #e9ecef;
    }
    
    .status-badge {
        display: inline-block;
        padding: 0.25em 0.6em;
        font-size: 75%;
        font-weight: 700;
        line-height: 1;
        text-align: center;
        white-space: nowrap;
        vertical-align: baseline;
        border-radius: 0.25rem;
    }
    .status-success { background-color: #28a745; color: white; }
    .status-error { background-color: #dc3545; color: white; }
</style>
""", unsafe_allow_html=True)

# --- State Initialization ---
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'username' not in st.session_state:
    st.session_state.username = None

# --- Login Screen ---
if not st.session_state.logged_in:
    st.markdown("<h1 style='text-align: center; margin-top: 5vh; color: #2c3e50;'>SSL Control Manager</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #6c757d;'>Sisteme erişmek için lütfen giriş yapın</p>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 1.2, 1])
    with col2:
        with st.form("login_form"):
            st.subheader("Oturum Aç")
            username = st.text_input("Kullanıcı Adı")
            password = st.text_input("Şifre", type="password")
            st.markdown("<br>", unsafe_allow_html=True)
            submit = st.form_submit_button("Giriş Yap", type="primary", use_container_width=True)
            
            if submit:
                with st.spinner("Doğrulanıyor..."):
                    try:
                        res = requests.post(f"{API_URL}/api/auth/login", json={"username": username, "password": password}, timeout=5)
                        if res.status_code == 200:
                            st.session_state.logged_in = True
                            st.session_state.username = username
                            st.rerun()
                        else:
                            st.error(f"Giriş başarısız: {res.json().get('error', 'Geçersiz bilgiler')}")
                    except Exception as e:
                        st.error("Sunucuya bağlanılamadı. Lütfen backend servisinin çalıştığından emin olun.")
    st.stop()

# --- Caching ---
@st.cache_data(ttl=60)
def fetch_certificates():
    try:
        response = requests.get(f"{API_URL}/api/certificates", timeout=10)
        if response.status_code == 200:
            return response.json()
    except Exception:
        pass
    return None

# --- Sidebar Navigation ---
with st.sidebar:
    st.title("Kontrol Paneli")
    st.markdown(f"**Aktif Kullanıcı:** `{st.session_state.username}`")
    st.markdown("---")
    
    page = st.radio(
        "Menü",
        ["📋 Sertifikalar", "📈 İstatistikler", "⚙️ Ayarlar"],
        label_visibility="collapsed"
    )
    
    st.markdown("---")
    
    try:
        test_response = requests.get(f"{API_URL}/", timeout=3)
        if test_response.status_code == 200:
            st.markdown("Sistem Durumu: <span class='status-badge status-success'>Online</span>", unsafe_allow_html=True)
        else:
            st.markdown("Sistem Durumu: <span class='status-badge status-error'>Hata</span>", unsafe_allow_html=True)
    except Exception:
        st.markdown("Sistem Durumu: <span class='status-badge status-error'>Offline</span>", unsafe_allow_html=True)
        
    st.markdown("---")
    
    st.markdown("<div style='height: 30vh;'></div>", unsafe_allow_html=True)
    
    if st.button("🚪 Çıkış Yap", use_container_width=True):
        st.session_state.logged_in = False
        st.session_state.username = None
        fetch_certificates.clear()
        st.rerun()

# --- Main Content Area ---
st.header(page[2:])
st.markdown("---")

colA, colB, colC, colD = st.columns(4)
with colA:
    if st.button("🔄 Tümünü Kontrol Et", type="primary", use_container_width=True):
        with st.spinner("Sertifikalar taranıyor..."):
            try:
                response = requests.post(f"{API_URL}/api/check", timeout=10)
                if response.status_code == 200:
                    st.success("Kontrol başarıyla başlatıldı.")
                    fetch_certificates.clear()
                    st.rerun()
                else:
                    st.error("Kontrol başlatılamadı.")
            except Exception as e:
                st.error(f"Hata: {str(e)}")
with colB:
    if st.button("↻ Verileri Yenile", use_container_width=True):
        fetch_certificates.clear()
        st.rerun()

st.markdown("<br>", unsafe_allow_html=True)

# --- Pages ---
if page == "📋 Sertifikalar":
    certs = fetch_certificates()
    
    if certs is not None:
        if certs:
            valid_count = len([c for c in certs if c.get('status') == 'valid'])
            warning_count = len([c for c in certs if c.get('status') == 'warning'])
            critical_count = len([c for c in certs if c.get('status') == 'critical'])
            
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Toplam Domain", len(certs))
            c2.metric("Geçerli", valid_count)
            c3.metric("Yaklaşan (Uyarı)", warning_count)
            c4.metric("Kritik", critical_count)
            
            st.subheader("Sertifika Listesi")
            
            data = []
            for cert in certs:
                if cert.get('error'):
                    data.append({
                        "Domain": cert['domain'],
                        "Durum": "❌ Bağlantı Hatası",
                        "Kalan Gün": "-",
                        "Bitiş Tarihi": "-",
                        "Sertifika Sağlayıcı": "-",
                        "Hata Detayı": str(cert.get('error', 'Bilinmeyen Hata'))[:50]
                    })
                else:
                    status_emoji = {
                        'valid': '✅',
                        'warning': '⚠️',
                        'critical': '🔴',
                        'expired': '❌'
                    }.get(cert.get('status', ''), '❓')
                    
                    data.append({
                        "Domain": cert['domain'],
                        "Durum": f"{status_emoji} {cert.get('status', 'Bilinmiyor').upper()}",
                        "Kalan Gün": cert.get('days_left', 0),
                        "Bitiş Tarihi": cert.get('not_after', 'Belirsiz'),
                        "Sertifika Sağlayıcı": str(cert.get('issuer', 'Belirsiz'))[:30]
                    })
            
            df = pd.DataFrame(data)
            st.dataframe(df, use_container_width=True, hide_index=True)
            
        else:
            st.info("Sistemde henüz kayıtlı bir domain bulunmuyor.")
    else:
        st.error("Veriler alınamadı. Backend bağlantısını kontrol edin.")

    st.markdown("---")
    st.subheader("Yeni Domain Ekle")
    
    with st.form("add_domain_form"):
        col1, col2 = st.columns(2)
        with col1:
            new_domain = st.text_input("Domain Adı (Örn: example.com)")
            server_type = st.selectbox("Sunucu Tipi", ["linux", "windows"])
        with col2:
            server_ip = st.text_input("Sunucu IP Adresi (Opsiyonel)")
            
        submitted = st.form_submit_button("Domaini Kaydet", type="primary")
        if submitted and new_domain:
            try:
                domain_data = {
                    "domain": new_domain,
                    "type": server_type,
                    "server": server_ip,
                    "ssh_user": "root",
                    "service": "nginx"
                }
                response = requests.post(f"{API_URL}/api/domains", json=domain_data, timeout=10)
                if response.status_code == 200:
                    st.success(f"Domain başarıyla eklendi: {new_domain}")
                    fetch_certificates.clear()
                    st.rerun()
                else:
                    st.error("Domain eklenirken bir hata oluştu.")
            except Exception as e:
                st.error(f"Bağlantı hatası: {str(e)}")

    st.markdown("---")
    st.subheader("Domain Sil")
    try:
        if certs:
            domains = [c['domain'] for c in certs]
            col_del1, col_del2 = st.columns([3, 1])
            with col_del1:
                domain_to_delete = st.selectbox("Kaldırılacak Domaini Seçin", domains)
            with col_del2:
                st.write("") 
                st.write("")
                if st.button("Seçili Domaini Sil", use_container_width=True):
                    try:
                        response = requests.delete(f"{API_URL}/api/domains/{domain_to_delete}", timeout=5)
                        if response.status_code == 200:
                            st.success(f"Domain silindi: {domain_to_delete}")
                            fetch_certificates.clear()
                            st.rerun()
                        else:
                            st.error("Silme işlemi başarısız oldu.")
                    except Exception as e:
                        st.error(f"Hata: {str(e)}")
    except:
        pass



elif page == "📈 İstatistikler":
    certs = fetch_certificates()
    
    if certs and len(certs) > 0:
        domains = []
        days_left = []
        status_colors = []
        
        for cert in certs:
            if not cert.get('error'):
                domains.append(cert['domain'])
                days_left.append(cert.get('days_left', 0))
                
                status = cert.get('status', '')
                if status == 'valid':
                    status_colors.append('#28a745')
                elif status == 'warning':
                    status_colors.append('#ffc107')
                elif status == 'critical':
                    status_colors.append('#dc3545')
                else:
                    status_colors.append('#6c757d')
        
        col1, col2 = st.columns(2)
        
        with col1:
            if domains and days_left:
                st.subheader("Sertifika Geçerlilik Süreleri")
                fig_bar = go.Figure(data=[go.Bar(
                    x=domains,
                    y=days_left,
                    marker_color=status_colors,
                    text=days_left,
                    textposition='auto',
                    hovertemplate='<b>%{x}</b><br>Kalan Gün: %{y}<extra></extra>'
                )])
                fig_bar.update_layout(
                    xaxis_title="Domain",
                    yaxis_title="Kalan Gün",
                    height=400,
                    showlegend=False,
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)"
                )
                st.plotly_chart(fig_bar, use_container_width=True)
                
        with col2:
            st.subheader("Sertifika Durum Dağılımı")
            valid_count = len([c for c in certs if c.get('status') == 'valid'])
            warning_count = len([c for c in certs if c.get('status') == 'warning'])
            critical_count = len([c for c in certs if c.get('status') == 'critical'])
            expired_count = len([c for c in certs if c.get('status') == 'expired'])
            error_count = len([c for c in certs if c.get('error')])
            
            pie_labels, pie_values, pie_colors = [], [], []
            
            if valid_count > 0:
                pie_labels.append('Geçerli'); pie_values.append(valid_count); pie_colors.append('#28a745')
            if warning_count > 0:
                pie_labels.append('Uyarı'); pie_values.append(warning_count); pie_colors.append('#ffc107')
            if critical_count > 0:
                pie_labels.append('Kritik'); pie_values.append(critical_count); pie_colors.append('#dc3545')
            if expired_count > 0:
                pie_labels.append('Süresi Dolmuş'); pie_values.append(expired_count); pie_colors.append('#6c757d')
            if error_count > 0:
                pie_labels.append('Hatalı'); pie_values.append(error_count); pie_colors.append('#17a2b8')
            
            if pie_values:
                fig_pie = go.Figure(data=[go.Pie(
                    labels=pie_labels,
                    values=pie_values,
                    marker=dict(colors=pie_colors),
                    hole=0.4,
                    textinfo='label+percent'
                )])
                fig_pie.update_layout(
                    height=400,
                    showlegend=True,
                    paper_bgcolor="rgba(0,0,0,0)"
                )
                st.plotly_chart(fig_pie, use_container_width=True)

        st.subheader("Risk Altındaki Domainler")
        risk_certs = [c for c in certs if c.get('status') in ['warning', 'critical'] and not c.get('error')]
        
        if risk_certs:
            risk_data = []
            for cert in risk_certs:
                risk_data.append({
                    "Domain": cert['domain'],
                    "Kalan Gün": cert['days_left'],
                    "Durum": "🔴 Kritik" if cert['status'] == 'critical' else "⚠️ Uyarı",
                    "Bitiş Tarihi": cert['not_after'][:10] if cert.get('not_after') else 'Belirsiz'
                })
            risk_df = pd.DataFrame(risk_data)
            st.warning(f"Dikkat: {len(risk_certs)} adet sertifikanın süresi yakında doluyor!")
            st.dataframe(risk_df, use_container_width=True, hide_index=True)
        else:
            st.success("Tüm sertifikaların geçerlilik süresi güvenli aralıkta.")
    else:
        st.info("İstatistik oluşturmak için yeterli veri bulunmuyor.")

elif page == "⚙️ Ayarlar":
    current_settings = {}
    try:
        resp = requests.get(f"{API_URL}/api/settings", timeout=3)
        if resp.status_code == 200:
            current_settings = resp.json()
    except:
        pass

    st.subheader("SMTP (E-posta) Konfigürasyonu")
    with st.expander("E-posta Sunucu Ayarları", expanded=True):
        col1, col2 = st.columns(2)
        
        with col1:
            smtp_server = st.text_input("SMTP Sunucu Adresi", value=current_settings.get("SMTP_SERVER", "smtp.gmail.com"))
            smtp_port = st.number_input("SMTP Port Numarası", value=int(current_settings.get("SMTP_PORT", 587)))
            smtp_user = st.text_input("E-posta Adresi", value=current_settings.get("SMTP_USER", ""))
        
        with col2:
            smtp_password = st.text_input("Parola / Uygulama Şifresi", value=current_settings.get("SMTP_PASSWORD", ""), type="password")
            alert_emails = st.text_input("Bildirim Alacak Adresler", value=current_settings.get("ALERT_EMAILS", ""), help="Birden fazla ise virgülle ayırın")
            
        c1, c2 = st.columns(2)
        with c1:
            if st.button("💾 SMTP Ayarlarını Kaydet", type="primary", use_container_width=True):
                try:
                    payload = {
                        "SMTP_SERVER": smtp_server,
                        "SMTP_PORT": smtp_port,
                        "SMTP_USER": smtp_user,
                        "SMTP_PASSWORD": smtp_password,
                        "ALERT_EMAILS": alert_emails
                    }
                    response = requests.post(f"{API_URL}/api/settings", json=payload, timeout=5)
                    if response.status_code == 200:
                        st.success("Ayarlar başarıyla güncellendi.")
                    else:
                        st.error("Ayarlar kaydedilirken bir sorun oluştu.")
                except Exception as e:
                    st.error(f"Hata: {str(e)}")
        with c2:
            if st.button("✉️ Test E-postası Gönder", use_container_width=True):
                with st.spinner("E-posta gönderiliyor..."):
                    try:
                        res = requests.get(f"{API_URL}/api/test/warning", timeout=15)
                        if res.status_code == 200:
                            st.success(res.json().get("message", "Test e-postası başarıyla gönderildi."))
                        else:
                            st.error(f"Gönderim hatası: {res.json().get('error')}")
                    except Exception as e:
                        st.error(f"Hata: {str(e)}")

    st.subheader("Sistem Ayarları")
    with st.expander("Otomatik Kontrol Zamanlayıcısı ve Eşikler", expanded=True):
        col1, col2 = st.columns(2)
        with col1:
            interval_options = [1, 3, 6, 12, 24]
            current_interval = int(current_settings.get("CHECK_INTERVAL_HOURS", 6))
            if current_interval not in interval_options:
                interval_options.append(current_interval)
            
            check_interval = st.selectbox(
                "Kontrol Sıklığı (Saat)",
                options=sorted(interval_options),
                index=sorted(interval_options).index(current_interval),
                help="Sistem sertifikaları ne sıklıkla kontrol edecek?"
            )
        with col2:
            warning_days = st.number_input("Uyarı Eşiği (Kalan Gün)", value=int(current_settings.get("WARNING_DAYS", 30)), min_value=1)
            critical_days = st.number_input("Kritik Eşik (Kalan Gün)", value=int(current_settings.get("CRITICAL_DAYS", 7)), min_value=1)
            
        if st.button("💾 Sistem Ayarlarını Kaydet"):
            try:
                payload = {
                    "CHECK_INTERVAL_HOURS": check_interval,
                    "WARNING_DAYS": warning_days,
                    "CRITICAL_DAYS": critical_days
                }
                payload.update({k: v for k, v in current_settings.items() if k not in payload})
                response = requests.post(f"{API_URL}/api/settings", json=payload, timeout=5)
                if response.status_code == 200:
                    st.success("Sistem ayarları güncellendi.")
                    fetch_certificates.clear()
            except Exception as e:
                st.error(f"Hata: {str(e)}")

    st.subheader("Kullanıcı Yönetimi")
    with st.expander("Sistem Yöneticileri", expanded=True):
        users = []
        try:
            res_users = requests.get(f"{API_URL}/api/users", timeout=5)
            if res_users.status_code == 200:
                users = [u['username'] for u in res_users.json()]
        except:
            pass
            
        ucol1, ucol2 = st.columns(2)
        
        with ucol1:
            st.markdown("#### Yeni Kullanıcı Ekle")
            with st.form("add_user_form"):
                new_username = st.text_input("Kullanıcı Adı")
                new_password = st.text_input("Parola", type="password")
                if st.form_submit_button("Kullanıcı Oluştur"):
                    try:
                        r = requests.post(f"{API_URL}/api/users", json={"username": new_username, "password": new_password})
                        if r.status_code == 200:
                            st.success("Kullanıcı başarıyla eklendi.")
                            st.rerun()
                        else:
                            st.error(r.json().get("error"))
                    except:
                        st.error("Beklenmeyen bir hata oluştu.")
        
        with ucol2:
            st.markdown("#### Parola Güncelle")
            with st.form("change_pw_form"):
                target_user = st.selectbox("Kullanıcı Seçin", users) if users else st.text_input("Kullanıcı Adı")
                new_pw = st.text_input("Yeni Parola", type="password")
                if st.form_submit_button("Parolayı Değiştir"):
                    try:
                        r = requests.put(f"{API_URL}/api/users/{target_user}/password", json={"new_password": new_pw})
                        if r.status_code == 200:
                            st.success("Parola güncellendi.")
                        else:
                            st.error(r.json().get("error"))
                    except:
                        st.error("Beklenmeyen bir hata oluştu.")

        st.markdown("---")
        st.markdown("#### Kullanıcı Sil")
        del_user = st.selectbox("Silinecek Kullanıcı", users, key="del_user_select") if users else None
        if st.button("Kullanıcıyı Sil"):
            if del_user:
                try:
                    r = requests.delete(f"{API_URL}/api/users/{del_user}")
                    if r.status_code == 200:
                        st.success("Kullanıcı silindi.")
                        st.rerun()
                    else:
                        st.error(r.json().get("error"))
                except:
                    st.error("Beklenmeyen bir hata oluştu.")

st.markdown("<br><hr><center><span style='color:#6c757d; font-size: 0.9em;'>SSL Control Manager v2.1 &copy; 2026</span></center>", unsafe_allow_html=True)
