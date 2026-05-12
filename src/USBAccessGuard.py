

import os
import winreg
import subprocess
import wmi
import ctypes
import time
import customtkinter as ctk
from tkinter import messagebox

# Set tema
ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

class USBGuardFinal(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("USB Access Guard")
        self.geometry("800x620")
        
        # UI Layout
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Sidebar
        self.sidebar = ctk.CTkFrame(self, width=180, corner_radius=0)
        self.sidebar.grid(row=0, column=0, rowspan=2, sticky="nsew")
        
        ctk.CTkLabel(self.sidebar, text="USB Access Guard V0.1", font=("Arial", 18, "bold")).pack(pady=20)
        
        self.btn_scan = ctk.CTkButton(self.sidebar, text="Scan USB", command=self.scan_usb)
        self.btn_scan.pack(pady=10, padx=20)
        
        self.btn_lock = ctk.CTkButton(self.sidebar, text="Lock Other USB", fg_color="#2ecc71", hover_color="#27ae60", command=self.apply_lock)
        self.btn_lock.pack(pady=10, padx=20)
        
        self.btn_reset = ctk.CTkButton(self.sidebar, text="Reset Policy", fg_color="#e74c3c", hover_color="#c0392b", command=self.reset_policy)
        self.btn_reset.pack(pady=10, padx=20)

        # Help & Credit Section
        self.btn_help = ctk.CTkButton(self.sidebar, text="Help & Tutorial", fg_color="gray", command=self.show_help)
        self.btn_help.pack(side="bottom", pady=(10, 20), padx=20)
        
        self.credit_label = ctk.CTkLabel(self.sidebar, text="-iamFatur13-", font=("Arial", 11, "italic"), cursor="hand2", text_color="#3498db")
        self.credit_label.pack(side="bottom", pady=0)
        self.credit_label.bind("<Button-1>", lambda e: os.startfile("https://github.com/iamFatur13"))

        # Main Content
        self.display = ctk.CTkTextbox(self, font=("Consolas", 12))
        self.display.grid(row=0, column=1, padx=20, pady=(20, 10), sticky="nsew")

        # Progress Bar
        self.progress_bar = ctk.CTkProgressBar(self, orientation="horizontal")
        self.progress_bar.grid(row=1, column=1, padx=20, pady=(0, 20), sticky="ew")
        self.progress_bar.set(0)

    def is_admin(self):
        try:
            return ctypes.windll.shell32.IsUserAnAdmin() != 0
        except:
            return False

    def update_bar(self, val):
        """Update progress bar tanpa threading agar tetap sinkron dengan sistem"""
        self.progress_bar.set(val)
        self.update_idletasks() # Memaksa GUI update meski sedang sibuk

    def scan_usb(self):
        self.display.delete("1.0", "end")
        self.update_bar(0.2)
        self.display.insert("end", "[*] Scanning connected USB devices...\n")
        
        try:
            local_wmi = wmi.WMI()
            found_disks = local_wmi.Win32_DiskDrive(InterfaceType="USB")
            
            self.update_bar(0.6)
            if not found_disks:
                self.display.insert("end", "\n[!] No USB storage detected.")
            else:
                for disk in found_disks:
                    self.display.insert("end", f"✓ {disk.Model}\n  ID: {disk.PNPDeviceID}\n{'-'*30}\n")
                self.display.insert("end", f"\n[OK] {len(found_disks)} devices found.")
            
            self.update_bar(1.0)
        except Exception as e:
            self.display.insert("end", f"\n[ERROR] {str(e)}")

    def apply_lock(self):
        if not self.is_admin():
            messagebox.showerror("Admin Required", "Run as Admin!")
            return

        self.display.insert("end", "\n[*] MEMULAI KALIBRASI ID USB")
        self.update_bar(0.1)
        
        try:
            # 1. Reset awal agar bersih
            self.reset_policy_silent()
            
            # 2. Path Registry
            path = r"Software\Policies\Microsoft\Windows\DeviceInstall\Restrictions"
            key = winreg.CreateKey(winreg.HKEY_LOCAL_MACHINE, path)
            
            # Aktifkan blokir untuk yang tidak terdaftar
            winreg.SetValueEx(key, "DenyUnspecified", 0, winreg.REG_DWORD, 1)
            # Berikan izin untuk sub-perangkat agar drive letter muncul
            winreg.SetValueEx(key, "AllowInstallUndetermined", 0, winreg.REG_DWORD, 1)

            self.update_bar(0.3)
            
            # 3. Whitelist ID menggunakan Instance ID
            # Ini adalah ID paling unik yang dikenali Windows
            id_key = winreg.CreateKey(winreg.HKEY_LOCAL_MACHINE, path + r"\AllowDeviceIDs")
            count = 1
            
            local_wmi = wmi.WMI()
            for disk in local_wmi.Win32_DiskDrive(InterfaceType="USB"):
                # Kita ambil PNPDeviceID (Ini adalah kunci utamanya)
                pnp_id = disk.PNPDeviceID
                
                # Masukkan format Full ID
                winreg.SetValueEx(id_key, str(count), 0, winreg.REG_SZ, pnp_id)
                count += 1
                
                # Masukkan format Generic ID (Tanpa Instance ID di belakang)
                # Contoh: USB\VID_0781&PID_5581
                generic_id = "\\".join(pnp_id.split("\\")[:2])
                winreg.SetValueEx(id_key, str(count), 0, winreg.REG_SZ, generic_id)
                count += 1

            self.update_bar(0.6)

            # 4. Whitelist Class GUID (Daftar VIP)
            # Menjamin hardware dasar (Hub, Disk, Volume) tidak ikut terblokir
            c_key = winreg.CreateKey(winreg.HKEY_LOCAL_MACHINE, path + r"\AllowDeviceClasses")
            classes = [
                "{4d36e967-e325-11ce-bfc1-08002be10318}", # Disk Drives
                "{71a27cdd-812a-11d0-bec7-08002be2092f}", # Storage Volumes
                "{36fc9e60-c465-11cf-8056-444553540000}"  # USB Hubs
            ]
            for i, guid in enumerate(classes):
                winreg.SetValueEx(c_key, str(i+1), 0, winreg.REG_SZ, guid)

            self.update_bar(0.8)
            
            # 5. Eksekusi gpupdate
            subprocess.run("gpupdate /force", shell=True, capture_output=True)
            
            self.update_bar(1.0)
            self.display.insert("end", "\n[SUCCESS] Proteksi Diperbarui.")
            messagebox.showinfo("Success", "USB Whitelist Aktif!")
            
        except Exception as e:
            self.display.insert("end", f"\n[ERROR] {str(e)}")



    def reset_policy_silent(self):
        """Helper untuk membersihkan registry tanpa popup"""
        try:
            cmd1 = r'reg delete "HKLM\Software\Policies\Microsoft\Windows\DeviceInstall\Restrictions" /f'
            cmd2 = r'reg delete "HKLM\Software\Policies\Microsoft\Windows\RemovableStorageDevices" /f'
            subprocess.run(cmd1, shell=True, capture_output=True)
            subprocess.run(cmd2, shell=True, capture_output=True)
        except:
            pass

    def reset_policy(self):
        self.display.insert("end", "\n[*] MENGHAPUS SEMUA PEMBATASAN...")
        self.update_bar(0.3)
        try:
            # Hapus semua key kebijakan yang kita buat
            cmd1 = r'reg delete "HKLM\Software\Policies\Microsoft\Windows\DeviceInstall\Restrictions" /f'
            cmd2 = r'reg delete "HKLM\Software\Policies\Microsoft\Windows\RemovableStorageDevices" /f'
            subprocess.run(cmd1, shell=True, capture_output=True)
            subprocess.run(cmd2, shell=True, capture_output=True)
            
            self.update_bar(0.7)
            subprocess.run("gpupdate /force", shell=True, capture_output=True)
            self.update_bar(1.0)
            self.display.insert("end", "\n[RESET] Port USB kembali normal.")
            messagebox.showinfo("Reset", "Semua proteksi telah dilepas.")
        except:
            self.display.insert("end", "\n[!] Bersih.")

    def show_help(self):
        help_window = ctk.CTkToplevel(self)
        help_window.title("Documentation Apps")
        help_window.geometry("500x400")
        help_window.attributes("-topmost", True)
        
        help_text = (
            "--- CARA PENGGUNAAN ---\n\n"
            "1. SCAN USB:\n"
            "   Colokkan USB kantor yang diperbolehkan.\n"
            "   Klik 'Scan USB' hingga data muncul di layar.\n\n"
            "2. LOCK OTHER USB:\n"
            "   Klik tombol ini. Semua USB yang tidak terdaftar saat ini\n"
            "   akan diblokir secara otomatis oleh Windows.\n\n"
            "3. RESET POLICY:\n"
            "   Gunakan untuk membuka kembali semua blokir port USB.\n\n"
            "--- PENTING ---\n"
            "- Jalankan aplikasi dengan akses ADMINISTRATOR.\n"
            "- Jika USB resmi tidak muncul, cabut dan colok kembali.\n\n"
            "Created by: -iamFatur13- (@iamFatur13)"
        )
        label = ctk.CTkLabel(help_window, text=help_text, justify="left", font=("Arial", 12))
        label.pack(padx=20, pady=20)

if __name__ == "__main__":
    app = USBGuardFinal()
    app.mainloop()


#add comment
#add comment lagi
''' Script di bawah ini Sudah berjalan dengan Baik 
import os
import winreg
import subprocess
import wmi
import ctypes
import customtkinter as ctk
from tkinter import messagebox

class USBGuardFinal(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("IT Support - USB Access Guard")
        self.geometry("750x550")
        self.wmi_service = wmi.WMI()
        self.allowed_serials = [] # Kita gunakan Serial Number, lebih unik & stabil

        # UI Setup
        self.grid_columnconfigure(1, weight=1)
        self.sidebar = ctk.CTkFrame(self, width=160)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        
        ctk.CTkLabel(self.sidebar, text="USB GUARD V3", font=("Arial", 16, "bold")).pack(pady=20)
        ctk.CTkButton(self.sidebar, text="1. Scan USB", command=self.scan_usb).pack(pady=10, padx=10)
        ctk.CTkButton(self.sidebar, text="2. Lock Other USB", fg_color="green", command=self.apply_lock).pack(pady=10, padx=10)
        ctk.CTkButton(self.sidebar, text="3. Reset Policy", fg_color="red", command=self.reset_policy).pack(pady=10, padx=10)

        self.display = ctk.CTkTextbox(self, font=("Consolas", 12))
        self.display.grid(row=0, column=1, padx=20, pady=20, sticky="nsew")

    def is_admin(self):
        return ctypes.windll.shell32.IsUserAnAdmin() != 0

    def scan_usb(self):
        """Mencari Serial Number unik dari USB yang dicolokkan"""
        self.display.delete("1.0", "end")
        self.allowed_serials = []
        
        # Mengambil Disk Drive yang koneksinya USB
        for disk in self.wmi_service.Win32_DiskDrive(InterfaceType="USB"):
            # Serial number adalah identitas paling valid
            sn = disk.SerialNumber.strip()
            if sn:
                self.allowed_serials.append(sn)
                self.display.insert("end", f"Ditemukan: {disk.Model}\nSerial: {sn}\n{'-'*30}\n")
        
        if not self.allowed_serials:
            self.display.insert("end", "Tidak ada USB terdeteksi.")
        else:
            self.display.insert("end", f"\n[OK] {len(self.allowed_serials)} USB terdaftar sebagai 'Authorized'.")

    def apply_lock(self):
        """Metode baru: Menggunakan Deny_Read/Write untuk Mass Storage"""
        if not self.is_admin():
            messagebox.showerror("Admin Required", "Jalankan sebagai Admin!")
            return

        try:
            # Path Registry untuk Storage Device Policies
            base_path = r"Software\Policies\Microsoft\Windows\RemovableStorageDevices"
            
            # 1. Buat Key Global
            key = winreg.CreateKey(winreg.HKEY_LOCAL_MACHINE, base_path)
            
            # 2. Tambahkan pengecualian untuk Serial Number tertentu (Whitelist)
            # Karena Windows Registry standar sulit melakukan whitelist Serial per user,
            # kita gunakan metode 'Deny_All' tapi mengizinkan 'Device Installation' untuk ID tertentu.
            
            install_path = r"Software\Policies\Microsoft\Windows\DeviceInstall\Restrictions"
            i_key = winreg.CreateKey(winreg.HKEY_LOCAL_MACHINE, install_path)
            
            # Kunci utama: Jangan gunakan 'DenyUnspecified' jika hardware ID sering gagal.
            # Kita gunakan 'Prevent installation of devices not described by other policy settings'
            winreg.SetValueEx(i_key, "DenyUnspecified", 0, winreg.REG_DWORD, 1)
            
            # Masukkan Hardware IDs (Gunakan ID yang paling pendek/umum dari hasil scan)
            allow_id_path = install_path + r"\AllowDeviceIDs"
            id_key = winreg.CreateKey(winreg.HKEY_LOCAL_MACHINE, allow_id_path)
            
            # Ambil Hardware ID secara otomatis dari WMI PnP
            count = 1
            for disk in self.wmi_service.Win32_DiskDrive(InterfaceType="USB"):
                pnp_id = disk.PNPDeviceID
                # Ambil bagian depan ID saja agar lebih fleksibel (VID & PID)
                short_id = "\\".join(pnp_id.split("\\")[:2]) 
                winreg.SetValueEx(id_key, str(count), 0, winreg.REG_SZ, short_id)
                count += 1
                # Tambahkan juga ID lengkapnya
                winreg.SetValueEx(id_key, str(count), 0, winreg.REG_SZ, pnp_id)
                count += 1

            # 3. WAJIB: Izinkan Class GUID untuk 'Storage' secara total
            # Agar tidak terjadi 'Forbidden' saat proses mounting volume
            class_path = install_path + r"\AllowDeviceClasses"
            c_key = winreg.CreateKey(winreg.HKEY_LOCAL_MACHINE, class_path)
            classes = [
                "{4d36e967-e325-11ce-bfc1-08002be10318}", # Disk Drives
                "{71a27cdd-812a-11d0-bec7-08002be2092f}", # Storage Volumes
                "{36fc9e60-c465-11cf-8056-444553540000}", # USB Hub
                "{4d36e96b-e325-11ce-bfc1-08002be10318}", # Keyboard
                "{4d36e96f-e325-11ce-bfc1-08002be10318}", # Mouse
            ]
            for i, guid in enumerate(classes):
                winreg.SetValueEx(c_key, str(i+1), 0, winreg.REG_SZ, guid)

            # 4. Refresh Policy
            subprocess.run("gpupdate /force", shell=True, capture_output=True)
            messagebox.showinfo("Success", "Kebijakan diterapkan! Restart USB untuk melihat hasil.")
            
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def reset_policy(self):
        try:
            cmd = r'reg delete "HKLM\Software\Policies\Microsoft\Windows\DeviceInstall\Restrictions" /f'
            subprocess.run(cmd, shell=True)
            subprocess.run("gpupdate /force", shell=True)
            messagebox.showinfo("Reset", "Kebijakan dihapus.")
        except:
            pass

if __name__ == "__main__":
    app = USBGuardFinal()
    app.mainloop()

'''