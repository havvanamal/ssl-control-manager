import streamlit as st
import requests
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
import time
import traceback
import os

st.set_page_config(
    page_title="SSL Yönetim Sistemi",
    page_icon="🔒",
    layout="wide"
)


API_URL = os.getenv("BACKEND_URL", "http://localhost:9000")



st.sidebar.write(f"🔗 API URL: {API_URL}")

st.title("🔒 SSL Sertifika Yönetim ve Takip Sistemi")
st.markdown("---")

# Sidebar
with st.sidebar:
    st.header("🎮 Kontrol Paneli")
    
    # Backend durumunu kontrol et
    try:
        test_response = requests.get(f"{API_URL}/", timeout=3)
        if test_response.status_code == 200:
            st.success("✅ Backend bağlantısı OK")
        else:
            st.error(f"❌ Backend hatası: {test_response.status_code}")
    except Exception as e:
        st.error(f"❌ Backend'e bağlanılamıyor!")
    
    st.markdown("---")
    
    # BUTON 1: Tüm sertifikaları kontrol et
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔄 Tümünü Kontrol Et", use_container_width=True, type="primary"):
            with st.spinner("Sertifikalar kontrol ediliyor..."):
                try:
                    response = requests.post(f"{API_URL}/api/check", timeout=10)
                    if response.status_code == 200:
                        st.success("✅ Kontrol başlatıldı!")
                        st.rerun()
                    else:
                        st.error("❌ Kontrol başlatılamadı!")
                except Exception as e:
                    st.error(f"Hata: {str(e)}")
    
    with col2:
        if st.button("🔄 Yenile", use_container_width=True):
            st.rerun()
    
    st.markdown("---")
    
    # BUTON 2
    st.subheader("🔧 Domain İşlemleri")
    
    # Domain seçme (domain listesinden)
    try:
        cert_response = requests.get(f"{API_URL}/api/certificates", timeout=5)
        if cert_response.status_code == 200:
            certs = cert_response.json()
            domains = [c.get('domain') for c in certs if not c.get('error')]
            
            if domains:
                selected_domain = st.selectbox("Domain Seçin", domains)
                
                if st.button("🔄 Seçili Domaini Yenile", use_container_width=True):
                    with st.spinner(f"Sertifika yenileniyor: {selected_domain}"):
                        try:
                            response = requests.post(f"{API_URL}/api/renew/{selected_domain}", timeout=10)
                            if response.status_code == 200:
                                st.success(f"✅ Yenileme başlatıldı: {selected_domain}")
                                st.rerun()
                            else:
                                st.error(f"❌ Yenileme başlatılamadı!")
                        except Exception as e:
                            st.error(f"Hata: {str(e)}")
    except:
        pass
    
    st.markdown("---")
    st.header("📝 Domain Ekle")
    
    with st.form("add_domain"):
        new_domain = st.text_input("Domain Adı")
        server_type = st.selectbox("Sunucu Tipi", ["linux", "windows"])
        server_ip = st.text_input("Sunucu IP")
        
        submitted = st.form_submit_button("Domain Ekle")
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
                    st.success(f"✅ Domain eklendi: {new_domain}")
                    st.rerun()
                else:
                    st.error(f"❌ Domain eklenemedi!")
            except Exception as e:
                st.error(f"Hata: {str(e)}")

# Ana içerik
tab1, tab2, tab3 = st.tabs(["📋 Sertifikalar", "📈 İstatistikler", "⚙️ Ayarlar"])

with tab1:
    st.header("SSL Sertifika Durumları")
    
    try:
        st.info(f"API'den veri çekiliyor: {API_URL}/api/certificates")
        response = requests.get(f"{API_URL}/api/certificates", timeout=10)
        
        st.write(f"Response status: {response.status_code}")
        
        if response.status_code == 200:
            certs = response.json()
            st.write(f"✅ {len(certs)} sertifika bulundu")
            
            if certs:
                # Tablo
                data = []
                for cert in certs:
                    if cert.get('error'):
                        data.append({
                            "Domain": cert['domain'],
                            "Durum": "❌ HATA",
                            "Kalan Gün": "-",
                            "Son Kullanma": "-",
                            "Issuer": "-",
                            "Hata": cert.get('error', 'Bilinmeyen hata')[:50]
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
                            "Durum": f"{status_emoji} {cert.get('status', 'unknown').upper()}",
                            "Kalan Gün": cert.get('days_left', 0),
                            "Son Kullanma": cert.get('not_after', 'N/A'),
                            "Issuer": cert.get('issuer', 'N/A')[:30]
                        })
                
                df = pd.DataFrame(data)
                st.dataframe(df, use_container_width=True)
                
                # İstatistik özeti
                col1, col2, col3, col4 = st.columns(4)
                valid_count = len([c for c in certs if c.get('status') == 'valid'])
                warning_count = len([c for c in certs if c.get('status') == 'warning'])
                critical_count = len([c for c in certs if c.get('status') == 'critical'])
                error_count = len([c for c in certs if c.get('error')])
                
                with col1:
                    st.metric("Toplam", len(certs))
                with col2:
                    st.metric("✅ Geçerli", valid_count)
                with col3:
                    st.metric("⚠️ Uyarı", warning_count)
                with col4:
                    st.metric("🔴 Kritik", critical_count)
            else:
                st.warning("Sertifika bulunamadı")
        else:
            st.error(f"API hatası: {response.status_code}")
            st.code(response.text)
            
    except requests.exceptions.ConnectionError as e:
        st.error(f"❌ Bağlantı hatası: {str(e)}")
        st.info(f"Backend URL: {API_URL}")
        st.info("Backend'in çalıştığını doğrulayın: docker-compose ps")
    except Exception as e:
        st.error(f"Hata: {str(e)}")
        st.code(traceback.format_exc())

with tab2:
    st.header("📈 Grafiksel Analiz")
    
    try:
        response = requests.get(f"{API_URL}/api/certificates", timeout=10)
        if response.status_code == 200:
            certs = response.json()
            
            if certs and len(certs) > 0:
                # Verileri hazırla
                domains = []
                days_left = []
                status_colors = []
                
                for cert in certs:
                    if not cert.get('error'):
                        domains.append(cert['domain'])
                        days_left.append(cert.get('days_left', 0))
                        
                        # Duruma göre renk
                        status = cert.get('status', '')
                        if status == 'valid':
                            status_colors.append('#28a745')  # Yeşil
                        elif status == 'warning':
                            status_colors.append('#ffc107')  # Sarı
                        elif status == 'critical':
                            status_colors.append('#dc3545')  # Kırmızı
                        else:
                            status_colors.append('#6c757d')  # Gri
                
                # 1. Çubuk Grafiği - Kalan Günler
                if domains and days_left:
                    st.subheader("📊 Sertifika Kalan Günler")
                    fig_bar = go.Figure(data=[go.Bar(
                        x=domains,
                        y=days_left,
                        marker_color=status_colors,
                        text=days_left,
                        textposition='auto',
                        hovertemplate='<b>%{x}</b><br>Kalan Gün: %{y}<extra></extra>'
                    )])
                    fig_bar.update_layout(
                        title="Sertifika Kalan Günler",
                        xaxis_title="Domain",
                        yaxis_title="Kalan Gün",
                        height=400,
                        showlegend=False
                    )
                    st.plotly_chart(fig_bar, use_container_width=True)
                
                # 2. Pasta Grafiği - Durum Dağılımı
                st.subheader("🥧 Sertifika Durum Dağılımı")
                valid_count = len([c for c in certs if c.get('status') == 'valid'])
                warning_count = len([c for c in certs if c.get('status') == 'warning'])
                critical_count = len([c for c in certs if c.get('status') == 'critical'])
                expired_count = len([c for c in certs if c.get('status') == 'expired'])
                error_count = len([c for c in certs if c.get('error')])
                
                pie_labels = []
                pie_values = []
                pie_colors = []
                
                if valid_count > 0:
                    pie_labels.append('✅ Geçerli')
                    pie_values.append(valid_count)
                    pie_colors.append('#28a745')
                if warning_count > 0:
                    pie_labels.append('⚠️ Uyarı')
                    pie_values.append(warning_count)
                    pie_colors.append('#ffc107')
                if critical_count > 0:
                    pie_labels.append('🔴 Kritik')
                    pie_values.append(critical_count)
                    pie_colors.append('#dc3545')
                if expired_count > 0:
                    pie_labels.append('❌ Süresi Dolmuş')
                    pie_values.append(expired_count)
                    pie_colors.append('#6c757d')
                if error_count > 0:
                    pie_labels.append('❗ Hata')
                    pie_values.append(error_count)
                    pie_colors.append('#17a2b8')
                
                if pie_values:
                    fig_pie = go.Figure(data=[go.Pie(
                        labels=pie_labels,
                        values=pie_values,
                        marker=dict(colors=pie_colors),
                        hole=0.3,
                        textinfo='label+percent',
                        hovertemplate='<b>%{label}</b><br>Sayı: %{value}<br>Oran: %{percent}<extra></extra>'
                    )])
                    fig_pie.update_layout(
                        title="Sertifika Durum Dağılımı",
                        height=450,
                        showlegend=True
                    )
                    st.plotly_chart(fig_pie, use_container_width=True)
                else:
                    st.info("Grafik gösterimi için yeterli veri yok")
                
                # 3. İstatistik Kartları
                st.subheader("📊 Özet İstatistikler")
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    avg_days = sum(days_left) // len(days_left) if days_left else 0
                    st.metric("Ortalama Kalan Gün", f"{avg_days} gün")
                
                with col2:
                    min_days = min(days_left) if days_left else 0
                    st.metric("En Az Kalan Gün", f"{min_days} gün", delta="Kritik" if min_days < 30 else None)
                
                with col3:
                    max_days = max(days_left) if days_left else 0
                    st.metric("En Çok Kalan Gün", f"{max_days} gün")
                
                with col4:
                    total_certs = len([c for c in certs if not c.get('error')])
                    st.metric("Toplam Geçerli Sertifika", total_certs)
                
                # 4. Risk Analizi
                st.subheader("⚠️ Risk Analizi")
                risk_certs = [c for c in certs if c.get('status') in ['warning', 'critical'] and not c.get('error')]
                
                if risk_certs:
                    risk_data = []
                    for cert in risk_certs:
                        risk_data.append({
                            "Domain": cert['domain'],
                            "Kalan Gün": cert['days_left'],
                            "Durum": "🔴 Kritik" if cert['status'] == 'critical' else "⚠️ Uyarı",
                            "Son Kullanma": cert['not_after'][:10] if cert.get('not_after') else 'N/A'
                        })
                    risk_df = pd.DataFrame(risk_data)
                    st.warning(f"🚨 {len(risk_certs)} sertifika risk altında!")
                    st.dataframe(risk_df, use_container_width=True)
                else:
                    st.success("✅ Risk altında olan sertifika bulunmuyor!")
                
            else:
                st.info("📭 Henüz sertifika verisi yok. Lütfen domain ekleyin.")
        else:
            st.error(f"❌ API hatası: {response.status_code}")
            
    except requests.exceptions.ConnectionError:
        st.error("❌ Backend API'ye bağlanılamıyor!")
        st.info(f"Backend URL: {API_URL}")
    except Exception as e:
        st.error(f"Hata: {str(e)}")
 
with tab3:
    st.header("⚙️ Sistem Ayarları")
    
    # Settings fetching
    current_settings = {}
    try:
        resp = requests.get(f"{API_URL}/api/settings", timeout=3)
        if resp.status_code == 200:
            current_settings = resp.json()
    except:
        pass

    # 1. Bölüm: SMTP Ayarları (E-posta Bildirimleri)
    st.subheader("📧 E-posta Bildirim Ayarları")
    
    with st.expander("SMTP Ayarlarını Yapılandır", expanded=True):
        col1, col2 = st.columns(2)
        
        with col1:
            smtp_server = st.text_input("SMTP Sunucu", value=current_settings.get("SMTP_SERVER", "smtp.gmail.com"), help="Örnek: smtp.gmail.com, smtp.office365.com")
            smtp_port = st.number_input("SMTP Port", value=int(current_settings.get("SMTP_PORT", 587)), help="Genelde 587 (TLS) veya 465 (SSL)")
            smtp_user = st.text_input("SMTP Kullanıcı (E-posta)", value=current_settings.get("SMTP_USER", ""))
        
        with col2:
            smtp_password = st.text_input("SMTP Şifre / Uygulama Şifresi", value=current_settings.get("SMTP_PASSWORD", ""), type="password", help="Gmail için uygulama şifresi kullanın")
            alert_emails = st.text_input("Bildirim Alacak E-postalar", value=current_settings.get("ALERT_EMAILS", ""), help="Virgülle ayırarak birden fazla yazabilirsiniz")
        
        if st.button("💾 SMTP Ayarlarını Kaydet", type="primary"):
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
                    st.success("✅ SMTP ayarları API'ye kaydedildi!")
                else:
                    st.error("❌ Ayarlar kaydedilemedi.")
            except Exception as e:
                st.error(f"❌ Kaydedilemedi: {str(e)}")
    
    # 2. Bölüm: SSL Yenileme Ayarları
    st.subheader("🔄 SSL Sertifika Yenileme Ayarları")
    
    with st.expander("Yenileme Ayarlarını Yapılandır", expanded=True):
        col1, col2 = st.columns(2)
        
        with col1:
            # slider expects int
            renew_val = int(current_settings.get("RENEW_DAYS_BEFORE", 30))
            if renew_val < 7: renew_val = 7
            if renew_val > 90: renew_val = 90
            renew_days_before = st.slider(
                "Yenileme Tetikleme Günü",
                min_value=7,
                max_value=90,
                value=renew_val,
                help="Sertifika bitimine kaç gün kala otomatik yenileme başlatılsın"
            )
        
        with col2:
            interval_options = [1, 3, 6, 12, 24]
            current_interval = int(current_settings.get("CHECK_INTERVAL_HOURS", 6))
            if current_interval not in interval_options:
                interval_options.append(current_interval)
            
            check_interval = st.selectbox(
                "Kontrol Aralığı (Saat)",
                options=sorted(interval_options),
                index=sorted(interval_options).index(current_interval),
                help="SSL sertifikaları kaç saatte bir kontrol edilsin"
            )
        
        st.info(f"📋 Mevcut ayarlar: {renew_days_before} gün kala uyarı/yenileme başlatılacak, her {check_interval} saatte bir kontrol yapılacak.")
        
        if st.button("💾 Yenileme Ayarlarını Kaydet"):
            try:
                payload = {
                    "RENEW_DAYS_BEFORE": renew_days_before,
                    "CHECK_INTERVAL_HOURS": check_interval
                }
                response = requests.post(f"{API_URL}/api/settings", json=payload, timeout=5)
                if response.status_code == 200:
                    st.success("✅ Yenileme ayarları API'ye kaydedildi!")
                else:
                    st.error("❌ Ayarlar kaydedilemedi.")
            except Exception as e:
                st.error(f"❌ Kaydedilemedi: {str(e)}")
    
    # 3. Bölüm: Domain Yönetimi
    st.subheader("🌐 Domain Yönetimi")
    
    with st.expander("Kayıtlı Domainler", expanded=True):
        try:
            response = requests.get(f"{API_URL}/api/domains", timeout=5)
            if response.status_code == 200:
                domains = response.json()
                if domains:
                    domain_data = []
                    for d in domains:
                        domain_data.append({
                            "Domain": d.get('domain', 'N/A'),
                            "Sunucu Tipi": d.get('type', 'N/A'),
                            "Sunucu IP": d.get('server', 'N/A'),
                            "SSH Kullanıcı": d.get('ssh_user', 'N/A')
                        })
                    df_domains = pd.DataFrame(domain_data)
                    st.dataframe(df_domains, use_container_width=True)
                    
                    # Domain silme
                    st.markdown("---")
                    st.subheader("🗑️ Domain Sil")
                    domain_to_delete = st.selectbox("Silinecek Domain Seçin", [d.get('domain') for d in domains])
                    if st.button("🗑️ Domain Sil", type="secondary"):
                        try:
                            response = requests.delete(f"{API_URL}/api/domains/{domain_to_delete}", timeout=5)
                            if response.status_code == 200:
                                st.success(f"✅ Domain silindi: {domain_to_delete}")
                                st.rerun()
                            else:
                                st.error("❌ Domain silinemedi!")
                        except Exception as e:
                            st.error(f"Hata: {str(e)}")
                else:
                    st.info("📭 Henüz kayıtlı domain yok. Sol menüden domain ekleyin.")
            else:
                st.error("❌ Domain listesi alınamadı!")
        except Exception as e:
            st.error(f"❌ API bağlantı hatası: {str(e)}")
    
    # 4. Bölüm: Sistem Durumu
    st.subheader("📊 Sistem Durumu")
    
    with st.expander("Sistem Bilgileri", expanded=True):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            try:
                response = requests.get(f"{API_URL}/", timeout=3)
                if response.status_code == 200:
                    st.metric("Backend API", "✅ Çalışıyor")
                else:
                    st.metric("Backend API", "❌ Çalışmıyor")
            except:
                st.metric("Backend API", "❌ Bağlantı yok")
        
        with col2:
            try:
                response = requests.get(f"{API_URL}/api/certificates", timeout=3)
                if response.status_code == 200:
                    certs = response.json()
                    st.metric("Sertifika Sayısı", len(certs))
                else:
                    st.metric("Sertifika Sayısı", "Hata")
            except:
                st.metric("Sertifika Sayısı", "?")
        
        with col3:
            st.metric("Sistem Zamanı", datetime.now().strftime('%H:%M:%S'))
    
    # 5. Bölüm: Loglar ve Hata Ayıklama
    st.subheader("🐛 Hata Ayıklama (Debug)")
    
    with st.expander("Son API Yanıtları", expanded=False):
        try:
            response = requests.get(f"{API_URL}/api/certificates", timeout=5)
            st.json(response.json() if response.status_code == 200 else {"error": "Veri alınamadı"})
        except Exception as e:
            st.error(f"Hata: {str(e)}")
    
    # 6. Bölüm: Sistem Aksiyonları
    st.subheader("🛠️ Sistem Aksiyonları")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🔄 Tüm Kontrolü Başlat", use_container_width=True):
            try:
                response = requests.post(f"{API_URL}/api/check", timeout=5)
                if response.status_code == 200:
                    st.success("✅ Kontrol başlatıldı!")
                else:
                    st.error("❌ Kontrol başlatılamadı!")
            except Exception as e:
                st.error(f"Hata: {str(e)}")
    
    with col2:
        if st.button("📧 Test Maili Gönder", use_container_width=True):
            try:
                response = requests.get(f"{API_URL}/api/test/warning", timeout=10)
                if response.status_code == 200:
                    st.success("✅ Test maili gönderildi! Emailinizi kontrol edin.")
                else:
                    st.error("❌ Mail gönderilemedi!")
            except:
                st.error("❌ Test endpoint'i bulunamadı! (Backend'de /api/test/warning olmalı)")
    
    with col3:
        if st.button("🔄 Sayfayı Yenile", use_container_width=True):
            st.rerun()
    
    # Footer
    st.markdown("---")
    st.caption("💡 İpucu: Ayarları değiştirdikten sonra değişikliklerin etkili olması için backend'i yeniden başlatmanız gerekebilir.")

# Footer
st.markdown("---")
st.caption(f"SSL Yönetim Sistemi v1.0 | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
