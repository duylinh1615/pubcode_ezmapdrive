import os
import tkinter as tk
from tkinter import ttk, scrolledtext, simpledialog
import subprocess
import string
import ctypes
from tkinter import messagebox
import traceback
import tkinter as tk
from tkinter import messagebox
from tkinter import ttk

def show_guide():
    guide_text = "Hướng dẫn:\n\n"\
                 "- 10.100.x.x - a share scan folder\n"\
                 "- Map folder tổng - để gắn cả folder chung vào máy\n"\
                 "- Map thư mục đã chọn - để gắn từng thư mục vào máy\n"\
                 "- Import Link Folder để dán link ổ chung và map ổ\n"\
                 "- Get Link Folder để copy link ổ chung cho người khác\n"\
                 "- Xem trước Folder để mở thư mục ổ chung trước khi Map ổ\n"\
                 "- Mọi thắc mắc xin liên hệ duylinh1615@gmail.com"\

    messagebox.showinfo("Hướng dẫn", guide_text)
def is_valid_ip(ip):
    parts = ip.split(".")
    if len(parts) != 4:
        return False
    for part in parts:
        try:
            num = int(part)
            if not 0 <= num <= 255:
                return False
        except ValueError:
            return False
    return True

def is_valid_shared_folder(line):
    parts = line.split()
    return (
        len(parts) > 1 and 
        parts[1] == "Disk" and 
        not line.startswith(()) and
        not parts[0].endswith("$")
    )

def ping_ip(ip):
    try:
        subprocess.run(["ping", "-n", "1", ip], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return True
    except subprocess.CalledProcessError:
        return False
def get_shared_paths(ip_address):
    try:
        result = subprocess.check_output(["net", "view", f"\\\\{ip_address}", "/ALL"], text=True)
        shared_paths = [line.split()[0] for line in result.splitlines() if is_valid_shared_folder(line)]
        return shared_paths
    except subprocess.CalledProcessError as e:
        error_message = f"Error: {e}"
        messagebox.showerror("Error", error_message)
        return [error_message]
    except PermissionError:
        error_message = "Access to shared paths is denied. Please check your permissions."
        messagebox.showwarning("Permission Denied", error_message)
        return [error_message]
    except Exception as ex:
        error_message = f"An unexpected error occurred: {ex}\n\n{traceback.format_exc()}"
        messagebox.showerror("Error", error_message)
        return [error_message]

# Modify browse_folders function
def browse_folders(event=None):
    ip = ip_combobox.get()
    folder_name = folder_var.get()
    base_path = fr"\\{ip}\{folder_name}"

    try:
        subfolders = [f for f in os.listdir(base_path) if os.path.isdir(os.path.join(base_path, f))]

        # Filter out "__DFSR_DIAGNOSTICS_TEST_FOLDER__" and "DfsrPrivate"
        subfolders = [folder for folder in subfolders if folder not in ["__DFSR_DIAGNOSTICS_TEST_FOLDER__", "DfsrPrivate","_SYNCAPP"]]

        search_text = search_var.get().lower()
        subfolders = [folder for folder in subfolders if search_text in folder.lower()]

        listbox.delete(0, tk.END)
        for folder in subfolders:
            listbox.insert(tk.END, folder)

        # Enable buttons when valid folders are found
        enable_map_buttons()

    except FileNotFoundError:
        listbox.delete(0, tk.END)
        listbox.insert(tk.END, "Invalid IP or folder not found.")
        # Disable buttons on error
        disable_map_buttons()
    except PermissionError:
        listbox.delete(0, tk.END)
        listbox.insert(tk.END, "Bạn không có quyền truy cập thư mục này.")
        # Disable buttons on error
        disable_map_buttons()
    except Exception as e:
        error_message = f"An unexpected error occurred: {e}\n\n{traceback.format_exc()}"
        messagebox.showerror("Error", error_message)
        listbox.delete(0, tk.END)  # Clear old results
        listbox.insert(tk.END, error_message)
        # Disable buttons on error
        disable_map_buttons()

def disable_map_buttons():
    map_button['state'] = 'disabled'
    odd_map_button['state'] = 'disabled'

def enable_map_buttons():
    map_button['state'] = 'normal'
    odd_map_button['state'] = 'normal'

def show_shared_paths(event=None):
    ip_address = ip_combobox.get()
    folder_combobox['values'] = []

    if ip_address:
        shared_paths = get_shared_paths(ip_address)
        folder_combobox['values'] = shared_paths

        selected_value = folder_combobox.get()
        if selected_value in shared_paths:
            folder_combobox.set(selected_value)
            browse_folders()

            # Set the state of the combobox to readonly unless the default path is selected
            if selected_value != default_shared_path:
                folder_combobox.set("Đã tìm thấy thư mục hãy chọn thư mục")
                folder_combobox['state'] = 'readonly'
            else:
                folder_combobox.set(default_shared_path)
                folder_combobox['state'] = 'readonly'
        else:
            # Reset the message in the dropdown if no valid shared paths are found
            folder_combobox.set("Đã tìm thấy thư mục hãy chọn thư mục")
            folder_combobox['state'] = 'readonly'
    else:
        # Reset the message in the dropdown if no IP address is selected
        folder_combobox.set("Xin hãy chọn server trước")
        folder_combobox['state'] = 'readonly'

def get_available_drive():
    used_drives = set()
    bitmask = ctypes.windll.kernel32.GetLogicalDrives()
    
    for letter in string.ascii_uppercase:
        if bitmask & 1:
            used_drives.add(letter)
        bitmask >>= 1

    available_drives = [drive for drive in string.ascii_uppercase if drive not in used_drives]
    
    return available_drives[0] if available_drives else None

def map_drive():
    ip_address = ip_combobox.get()
    folder_name = folder_var.get()

    if not ip_address or not folder_name:
        # Display an error message or take appropriate action
        return

    selected_value = folder_combobox.get()

    if selected_value == "Đã tìm thấy thư mục hãy chọn thư mục":
        messagebox.showinfo("Thông báo", "Hãy chọn thư mục trước.")
        return

    base_path = fr"\\{ip_address}\{folder_name}"
    available_drive = get_available_drive()

    if available_drive:
        drive_letter = available_drive + ":"
        try:
            subprocess.run(["net", "use", drive_letter, base_path], check=True)
            messagebox.showinfo("Drive Mapped", f"Ô {drive_letter} được Map thành công đường dẫn: {base_path}.")
        except subprocess.CalledProcessError as e:
            messagebox.showerror("Error", f"Failed to map the drive. Error: {e}")
    else:
        messagebox.showwarning("No Available Drive", "No available drive letters to map.")


# Function to be called when the "Map ổ lẻ" button is clicked
def map_odd_drive():
    ip_address = ip_combobox.get()
    folder_name = folder_var.get()
    
    if not ip_address or not folder_name:
        # Display an error message or take appropriate action
        return

    selected_indices = listbox.curselection()

    if not selected_indices:
        messagebox.showinfo("Thông báo", "Hãy chọn thư mục muốn Map hoặc Map cả folder bằng phím Map ổ.")
        return

    selected_folder = listbox.get(selected_indices[0])
    base_path = fr"\\{ip_address}\{folder_name}\{selected_folder}"
    available_drive = get_available_drive()

    if available_drive:
        drive_letter = available_drive + ":"
        try:
            subprocess.run(["net", "use", drive_letter, base_path], check=True)
            messagebox.showinfo("Drive Mapped", f"The drive {drive_letter} is successfully mapped to {base_path}.")
        except subprocess.CalledProcessError as e:
            messagebox.showerror("Error", f"Failed to map the drive. Error: {e}")
    else:
        messagebox.showwarning("No Available Drive", "No available drive letters to map.")

def import_link_function():
    try:
        subprocess.Popen(["importlink.exe"])
    except FileNotFoundError:
        print("Error: Tính năng này đang được phát triển.")
    except Exception as e:
        print(f"Lỗi: An error occurred: {e}")

def export_link_function():
    # Get the selected IP and folder
    selected_ip = ip_combobox.get()
    selected_folder = folder_combobox.get()

    # Get the selected item from the listbox
    selected_indices = listbox.curselection()
    selected_item = listbox.get(selected_indices[0]) if selected_indices else ""

    # Create the base path
    base_path = fr"\\{selected_ip}\{selected_folder}"

    # If a shared path is selected, append it to the base path
    if selected_item:
        base_path = fr"{base_path}\{selected_item}"

    # Create a text-based message with the selected paths
    message = f"Link folder ổ chung:\n{base_path}"

    # Create a new window to display the message
    export_window = tk.Toplevel(window)
    export_window.title("Export Link")

    # Create a scrolled text widget to display the message
    text_widget = scrolledtext.ScrolledText(export_window, wrap=tk.WORD, width=40, height=10)
    text_widget.insert(tk.END, message)
    text_widget.pack(padx=10, pady=10)

def preview_function():
    selected_ip = ip_combobox.get()
    selected_folder = folder_combobox.get()
    selected_indices = listbox.curselection()

    # Check if IP and folder are selected
    if not selected_ip or not selected_folder:
        messagebox.showinfo("Thông báo", "Hãy chọn IP và thư mục để xem trước.")
        return

    base_path = fr"\\{selected_ip}\{selected_folder}"

    # If a shared path is selected, append it to the base path
    if selected_indices:
        selected_item = listbox.get(selected_indices[0])
        base_path = fr"{base_path}\{selected_item}"

    try:
        subprocess.run(["explorer", base_path])
    except subprocess.CalledProcessError as e:
        messagebox.showerror("Error", f"Failed to open Windows Explorer. Error: {e}")



# Create the main window
window = tk.Tk()
window.title("Tìm folder và map ổ")

menu_bar = tk.Menu(window)
window.config(menu=menu_bar)

help_menu = tk.Menu(menu_bar, tearoff=0)
menu_bar.add_cascade(label="Hướng dẫn", command=show_guide)

# Add a search box at the top
search_label = tk.Label(window, text="Tìm kiếm folder/thư mục:")
search_label.grid(row=0, column=0, padx=10, pady=10, sticky=tk.E)

search_var = tk.StringVar()
search_entry = ttk.Entry(window, textvariable=search_var)
search_entry.grid(row=0, column=1, padx=10, pady=10, columnspan=1, sticky=tk.W + tk.E)
search_entry.bind("<KeyRelease>", lambda event: browse_folders())

# Set default values for IP address and shared path
default_ip = "10.100.x.x"
default_shared_path = "Networkshare"
# Add a label for IP address
ip_label = tk.Label(window, text="Chọn IP server:")
ip_label.grid(row=1, column=0, padx=10, pady=10, sticky=tk.E)
# Update the values for ip_combobox to include both fixed IP addresses and "Custom"
ip_combobox = ttk.Combobox(window, values=["", "10.100.x.x", "10.101.x.x", "10.102.x.x", "Nhập IP"], state="readonly", width=40)
ip_combobox.set(default_ip)  # Set the default IP address
ip_combobox.grid(row=1, column=1, padx=10, pady=10)

def handle_ip_combobox(event):
    selected_ip = ip_combobox.get()
    if selected_ip == "Nhập IP":
        # Show a popup to input custom IP
        custom_ip = simpledialog.askstring("Tùy chọn IP", "Nhập IP:")
        if custom_ip:
            if is_valid_ip(custom_ip) and ping_ip(custom_ip):
                ip_combobox.set(custom_ip)
                listbox.delete(0, tk.END)  # Clear the Listbox on IP change
                show_shared_paths()
            else:
                messagebox.showerror("IP Không hợp lệ", "Sai định dạng IP hoặc không thể kết nối. Vui lòng nhập lại.")
                ip_combobox.set(default_ip)
                listbox.delete(0, tk.END)  # Clear the Listbox on IP change
        else:
            # User canceled, reset to default IP
            ip_combobox.set(default_ip)
            listbox.delete(0, tk.END)  # Clear the Listbox on IP change
    else:
        listbox.delete(0, tk.END)  # Clear the Listbox on IP change
        show_shared_paths()

# Add a label for shared path
shared_path_label = tk.Label(window, text="Folder tổng:")
shared_path_label.grid(row=2, column=0, padx=10, pady=10, sticky=tk.E)

# Bind the handle_ip_combobox function to the <<ComboboxSelected>> event
ip_combobox.bind("<<ComboboxSelected>>", handle_ip_combobox)
# Add a label above the listbox
listbox_label = tk.Label(window, text="List thư mục:")
listbox_label.grid(row=3, column=0, columnspan=2, padx=10, pady=5, sticky=tk.W)

listbox = tk.Listbox(window, selectmode=tk.SINGLE)
listbox.grid(row=4, column=0, columnspan=2, padx=10, pady=10, sticky=tk.W + tk.E + tk.N + tk.S)

# Initialize the folder_combobox with the default shared path
folder_var = tk.StringVar()
folder_combobox = ttk.Combobox(window, textvariable=folder_var, width=40)
folder_combobox.grid(row=2, column=1, padx=10, pady=10, sticky=tk.W)
folder_combobox.set(default_shared_path)  # Set the default shared path

folder_combobox.bind("<<ComboboxSelected>>", browse_folders)

listbox = tk.Listbox(window, selectmode=tk.SINGLE)
listbox.grid(row=4, column=0, columnspan=2, padx=10, pady=10, sticky=tk.W + tk.E + tk.N + tk.S)

# Add a "Map ổ" button to the right of the shared paths dropdown
map_button = tk.Button(window, text="Map folder tổng", command=map_drive)
map_button.grid(row=2, column=2, padx=10, pady=10)

# Add a "Map ổ lẻ" button to the right of the result list
odd_map_button = tk.Button(window, text="Map thư mục đã chọn", command=map_odd_drive)
odd_map_button.grid(row=4, column=2, padx=10, pady=10)

# Add a "Import link" button
import_button = tk.Button(window, text="Import link folder", command=import_link_function)
import_button.grid(row=5, column=0, padx=10, pady=10)

# Add a "Export link" button
export_button = tk.Button(window, text="Get link folder", command=export_link_function)
export_button.grid(row=5, column=1, padx=10, pady=10)

# Add a "Xem trước" button
preview_button = tk.Button(window, text="Xem trước folder", command=preview_function)
preview_button.grid(row=5, column=2, padx=10, pady=10)

# Call the show_shared_paths function to update the shared paths initially
show_shared_paths()

window.mainloop()