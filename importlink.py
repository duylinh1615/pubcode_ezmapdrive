import tkinter as tk
from tkinter import scrolledtext
import subprocess
import string
import ctypes
from tkinter import messagebox

def get_available_drive():
    used_drives = set()
    bitmask = ctypes.windll.kernel32.GetLogicalDrives()
    
    for letter in string.ascii_uppercase:
        if bitmask & 1:
            used_drives.add(letter)
        bitmask >>= 1

    available_drives = [drive for drive in string.ascii_uppercase if drive not in used_drives]
    
    return available_drives[0] if available_drives else None

def map_network_drive():
    available_drive = get_available_drive()
    network_path = entry.get("1.0", "end-1c")  # Get the text from the Text widget
    if available_drive:
        drive_letter = available_drive + ":"
        try:
            subprocess.run(["net", "use", drive_letter, network_path], check=True)
            messagebox.showinfo("Drive Mapped", f"Drive {drive_letter} mapped successfully to {network_path}.")
        except subprocess.CalledProcessError as e:
            messagebox.showerror("Error", f"Failed to map the drive. Error: {e}")
    else:
        messagebox.showwarning("No Available Drive", "No available drive letters to map.")

# Create the main window
window = tk.Tk()
window.title("Map ổ")

# Create and place widgets in the window
label = tk.Label(window, text="Dán Link vào ô dưới để map ổ \n(Link có dạng \\\\10.100.x.x\\folder1\\folder2 \n Hoặc \\\\hostname\\folder1\\folder2):")
label.pack(pady=20)

entry = scrolledtext.ScrolledText(window, width=60, height=1, wrap=tk.WORD)
entry.pack(pady=20)

submit_button = tk.Button(window, text="Map ổ", command=map_network_drive)
submit_button.pack(pady=20)

result_label = tk.Label(window, text="")
result_label.pack(pady=20)

window.mainloop()