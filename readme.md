# 🛡️ USB Access Guard 

**Solusi Whitelist USB Selektif untuk Keamanan Data Perusahaan.**

---

### 💡 Latar Belakang
Berawal dari keresahan di lingkungan kerja (khususnya di sektor pertambangan yang serba ketat), ada kebijakan perusahaan yang melarang penggunaan perangkat penyimpanan eksternal pribadi seperti **Flashdisk (FDD), SSD Eksternal, atau HDD Eksternal**. Tujuannya jelas: mencegah kebocoran data dan serangan malware.

**Masalahnya:** 
Software yang tersedia di internet kebanyakan cuma punya opsi "Nuklir" alias **Blokir Total Port USB**. Padahal, kita tetap butuh colok USB resmi dari kantor untuk operasional. Akhirnya, daripada pusing cari yang nggak ada, saya develop sendiri aplikasi ini!

Aplikasi ini lahir untuk mengisi celah itu: **Blokir yang asing, izinkan yang resmi.**

### ✨ Fitur Utama
*   🔍 **Smart Scanning:** Mendeteksi hardware ID unik dari USB resmi yang sedang tertancap.
*   ✅ **Deep Whitelisting:** Mendaftarkan Instance ID dan Class GUID perangkat secara presisi ke dalam sistem Windows.
*   🚫 **Auto-Block:** Menutup akses bagi perangkat penyimpanan lain yang tidak terdaftar dalam database "kawan".
*   🔄 **Reset Policy:** Mengembalikan pengaturan port USB ke kondisi normal hanya dengan satu klik.
*   🎨 **Modern UI:** Tampilan bersih dan gelap (Dark Mode) menggunakan CustomTkinter agar tetap enak dilihat sambil kerja.

### 🚀 Cara Penggunaan (Gampang Banget!)

1.  **Run as Administrator:** Klik kanan pada file `.exe` atau script, lalu pilih *Run as Administrator* (Wajib, karena kita mainan Registry).
2.  **Scan USB Kantor:** Colokkan USB resmi yang ingin diperbolehkan, lalu klik tombol **1. Scan USB**.
3.  **Aktifkan Proteksi:** Klik tombol **2. Lock Other USB**. Tunggu sampai progress bar 100%. 
4.  **Selesai!** Sekarang coba cabut USB kantor dan colok USB pribadi. Windows akan otomatis menolak perangkat yang tidak terdaftar.
5.  **Buka Blokir:** Mau normal lagi? Cukup klik **3. Reset Policy**.

### 🛠️ Tech Stack
*   **Python 3.x**
*   **CustomTkinter** (UI yang cakep)
*   **WMI Library** (Buat intip hardware ID)
*   **Windows Registry API** (Otak dari segala kebijakan)

### ⚠️ Disclaimer
Aplikasi ini melakukan modifikasi pada *Local Group Policy* dan *Windows Registry*. Pastikan Anda menggunakannya sesuai dengan kebijakan IT di perusahaan masing-masing. *Use it wisely!*

---
Made with 🔥 by **-iamFatur-**
[Visit My Profile](https://github.com/iamFatur13)