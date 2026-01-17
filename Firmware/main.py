import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import json
import os

class HackpadConfigGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("⛏ Skyboard Key Config")
        self.root.geometry("1000x725")
        
        # Minecraft-inspired color scheme
        self.bg_color = "#c6d8af"  # Light greenish background
        self.frame_color = "#a8ba8e"  # Darker green for frames
        self.button_color = "#7a9b5f"  # Green for buttons
        self.button_hover = "#669944"  # Darker green on hover
        self.text_color = "#2d4a1e"  # Dark green text
        self.entry_bg = "#e8f5d8"  # Very light green for entries
        
        self.root.configure(bg=self.bg_color)
        
        # Try to use a pixelated/retro font similar to Minecraft
        # Falls back to Courier if custom font not available
        self.title_font = ("Courier New", 20, "bold")
        self.label_font = ("Courier New", 11, "bold")
        self.text_font = ("Courier New", 10)
        self.small_font = ("Courier New", 8)
        
        # Preset Minecraft keybinds
        self.presets = {
            "F3+C - Copy Coordinates": ["F3", "C"],
            "F3+G - Show Chunk Boundaries": ["F3", "G"],
            "F3+A - Reload Chunks": ["F3", "A"],
            "F3+B - Show Hitboxes": ["F3", "B"],
            "F3+ESC - Pause Without Menu": ["F3", "ESCAPE"],
            "F3+Q - Show F3+Q Menu": ["F3", "Q"],
            "F3+F - Increase Render Distance": ["F3", "F"],
            "SHIFT+F3+F - Decrease Render Distance": ["SHIFT", "F3", "F"],
            "SHIFT+F3 - Show Debug Piechart": ["SHIFT", "F3"]
        }
        
        # Store key configurations
        self.key_configs = []
        self.num_keys = 6  # Default number of keys
        
        self.setup_styles()
        self.create_widgets()
        self.load_config()
        
    def setup_styles(self):
        style = ttk.Style()
        style.theme_use('clam')
        
        # Configure colors for ttk widgets
        style.configure('TFrame', background=self.bg_color)
        style.configure('TLabel', background=self.bg_color, foreground=self.text_color, 
                       font=self.text_font)
        style.configure('Title.TLabel', background=self.bg_color, foreground=self.text_color,
                       font=self.title_font)
        style.configure('TLabelframe', background=self.frame_color, foreground=self.text_color,
                       borderwidth=3, relief='raised')
        style.configure('TLabelframe.Label', background=self.frame_color, 
                       foreground=self.text_color, font=self.label_font)
        
        style.configure('TEntry', fieldbackground=self.entry_bg, foreground=self.text_color,
                       borderwidth=2)
        style.configure('TCombobox', fieldbackground=self.entry_bg, 
                       background=self.entry_bg, foreground=self.text_color,
                       borderwidth=2, arrowcolor=self.text_color)
        style.map('TCombobox', fieldbackground=[('readonly', self.entry_bg)])
        style.map('TCombobox', selectbackground=[('readonly', self.button_color)])
        style.map('TCombobox', selectforeground=[('readonly', 'white')])
        
        style.configure('TSpinbox', fieldbackground=self.entry_bg, 
                       background=self.entry_bg, foreground=self.text_color,
                       borderwidth=2, arrowcolor=self.text_color)
        
    def create_widgets(self):
        # Main container
        main_frame = tk.Frame(self.root, bg=self.bg_color, padx=20, pady=20)
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Title with Minecraft-style decoration
        title_frame = tk.Frame(main_frame, bg=self.bg_color)
        title_frame.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        tk.Label(title_frame, text="⛏ Skyboard ⛏", 
                font=self.title_font, bg=self.bg_color, fg=self.text_color).pack()
        tk.Label(title_frame, text="Skyboard Config", 
                font=self.label_font, bg=self.bg_color, fg=self.text_color).pack()
        
        # Number of keys selector with custom styling
        key_count_frame = tk.Frame(main_frame, bg=self.frame_color, 
                                   relief='raised', borderwidth=3, padx=15, pady=10)
        key_count_frame.grid(row=1, column=0, columnspan=3, pady=(0, 15), sticky=(tk.W, tk.E))
        
        tk.Label(key_count_frame, text="⌨ Number of Keys:", 
                font=self.label_font, bg=self.frame_color, fg=self.text_color).pack(side=tk.LEFT, padx=5)
        
        self.num_keys_var = tk.IntVar(value=self.num_keys)
        num_keys_spin = ttk.Spinbox(key_count_frame, from_=1, to=20, 
                                    textvariable=self.num_keys_var, width=5,
                                    command=self.update_key_count, font=self.text_font)
        num_keys_spin.pack(side=tk.LEFT, padx=5)
        
        # Scrollable frame for key configurations
        canvas_frame = tk.Frame(main_frame, bg=self.bg_color, relief='sunken', borderwidth=3)
        canvas_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 15))
        
        canvas = tk.Canvas(canvas_frame, height=400, bg=self.bg_color, 
                          highlightthickness=0, borderwidth=0)
        scrollbar = tk.Scrollbar(canvas_frame, orient="vertical", command=canvas.yview,
                                bg=self.button_color, troughcolor=self.frame_color,
                                activebackground=self.button_hover, width=16)
        self.scrollable_frame = tk.Frame(canvas, bg=self.bg_color)
        
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Create initial key configuration widgets
        self.create_key_configs()
        
        # Button frame with custom styled buttons
        button_frame = tk.Frame(main_frame, bg=self.bg_color)
        button_frame.grid(row=3, column=0, columnspan=3, pady=(0, 10))
        
        self.create_mc_button(button_frame, "💾 Save Config", self.save_config).pack(side=tk.LEFT, padx=5)
        self.create_mc_button(button_frame, "📤 Export Firmware", self.export_firmware).pack(side=tk.LEFT, padx=5)
        self.create_mc_button(button_frame, "📁 Load Config", self.load_config_file).pack(side=tk.LEFT, padx=5)
        
        # Footer
        footer = tk.Label(main_frame, text="Be faster with Skyboard!", 
                         font=self.small_font, bg=self.bg_color, fg=self.text_color)
        footer.grid(row=4, column=0, columnspan=3)
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(2, weight=1)
    
    def create_mc_button(self, parent, text, command):
        """Create a Minecraft-style button"""
        btn = tk.Button(parent, text=text, command=command,
                       font=self.label_font, bg=self.button_color, fg='white',
                       activebackground=self.button_hover, activeforeground='white',
                       relief='raised', borderwidth=4, padx=15, pady=8,
                       cursor='hand2')
        
        # Add hover effects
        btn.bind('<Enter>', lambda e: btn.config(bg=self.button_hover))
        btn.bind('<Leave>', lambda e: btn.config(bg=self.button_color))
        
        return btn
        
    def create_key_configs(self):
        # Clear existing widgets
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
        
        self.key_configs = []
        
        for i in range(self.num_keys):
            row = i // 2  # Integer division for row
            col = i % 2   # Modulo for column (0 or 1)
            self.create_key_box(i, row, col)
    
    def create_key_box(self, index, row, col):
        frame = tk.LabelFrame(self.scrollable_frame, text=f"  🔑 Key {index + 1}  ", 
                             bg=self.frame_color, fg=self.text_color,
                             font=self.label_font, relief='raised', borderwidth=4,
                             padx=15, pady=12)
        frame.grid(row=row, column=col, sticky=(tk.W, tk.E, tk.N, tk.S), padx=8, pady=6)
        
        # Preset selector
        preset_label = tk.Label(frame, text="📋 Preset:", bg=self.frame_color, 
                               fg=self.text_color, font=self.label_font)
        preset_label.grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        
        preset_var = tk.StringVar(value="Custom")
        preset_combo = ttk.Combobox(frame, textvariable=preset_var, 
                                    values=["Custom"] + list(self.presets.keys()),
                                    width=30, state="readonly", font=self.text_font)
        preset_combo.grid(row=0, column=1, padx=5, pady=5, sticky=(tk.W, tk.E))
        preset_combo.bind("<<ComboboxSelected>>", 
                         lambda e, idx=index: self.preset_selected(idx))
        
        # Custom keybind entry
        custom_label = tk.Label(frame, text="⌨ Custom:", bg=self.frame_color,
                               fg=self.text_color, font=self.label_font)
        custom_label.grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        
        custom_var = tk.StringVar()
        custom_entry = tk.Entry(frame, textvariable=custom_var, width=35,
                               bg=self.entry_bg, fg=self.text_color,
                               font=self.text_font, relief='sunken', borderwidth=2,
                               insertbackground=self.text_color)
        custom_entry.grid(row=1, column=1, padx=5, pady=5, sticky=(tk.W, tk.E))
        
        hint_label = tk.Label(frame, text='💡 Use "+", e.g. F3+C', 
                             font=self.small_font, bg=self.frame_color, fg=self.text_color)
        hint_label.grid(row=2, column=0, columnspan=2, sticky=tk.W, padx=5)
        
        frame.columnconfigure(1, weight=1)
        
        # Make the columns in the main grid equal width
        self.scrollable_frame.columnconfigure(0, weight=1, uniform="keys")
        self.scrollable_frame.columnconfigure(1, weight=1, uniform="keys")
        
        # Store references
        self.key_configs.append({
            'frame': frame,
            'preset_var': preset_var,
            'preset_combo': preset_combo,
            'custom_var': custom_var,
            'custom_entry': custom_entry
        })
    
    def preset_selected(self, index):
        config = self.key_configs[index]
        preset_name = config['preset_var'].get()
        
        if preset_name != "Custom" and preset_name in self.presets:
            keys = self.presets[preset_name]
            config['custom_var'].set("+".join(keys))
    
    def update_key_count(self):
        new_count = self.num_keys_var.get()
        if new_count != self.num_keys:
            self.num_keys = new_count
            self.create_key_configs()
    
    def save_config(self):
        config_data = {
            'num_keys': self.num_keys,
            'keys': []
        }
        
        for i, config in enumerate(self.key_configs):
            custom_keys = config['custom_var'].get().strip()
            if custom_keys:
                keys = [k.strip().upper() for k in custom_keys.split('+')]
                config_data['keys'].append({
                    'key_number': i + 1,
                    'keybind': keys
                })
        
        try:
            with open('hackpad_config.json', 'w') as f:
                json.dump(config_data, f, indent=2)
            messagebox.showinfo("✓ Success", "Configuration saved to hackpad_config.json",
                               icon='info')
        except Exception as e:
            messagebox.showerror("✗ Error", f"Failed to save configuration: {str(e)}")
    
    def load_config(self):
        if os.path.exists('hackpad_config.json'):
            try:
                with open('hackpad_config.json', 'r') as f:
                    config_data = json.load(f)
                
                self.num_keys = config_data.get('num_keys', 6)
                self.num_keys_var.set(self.num_keys)
                self.create_key_configs()
                
                for key_data in config_data.get('keys', []):
                    idx = key_data['key_number'] - 1
                    if idx < len(self.key_configs):
                        keybind = '+'.join(key_data['keybind'])
                        self.key_configs[idx]['custom_var'].set(keybind)
            except Exception as e:
                messagebox.showwarning("⚠ Warning", f"Failed to load configuration: {str(e)}")
    
    def load_config_file(self):
        filename = filedialog.askopenfilename(
            title="Load Configuration",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        if filename:
            try:
                with open(filename, 'r') as f:
                    config_data = json.load(f)
                
                self.num_keys = config_data.get('num_keys', 6)
                self.num_keys_var.set(self.num_keys)
                self.create_key_configs()
                
                for key_data in config_data.get('keys', []):
                    idx = key_data['key_number'] - 1
                    if idx < len(self.key_configs):
                        keybind = '+'.join(key_data['keybind'])
                        self.key_configs[idx]['custom_var'].set(keybind)
                
                messagebox.showinfo("✓ Success", "Configuration loaded successfully")
            except Exception as e:
                messagebox.showerror("✗ Error", f"Failed to load configuration: {str(e)}")
    
    def export_firmware(self):
        # Generate firmware code
        firmware_code = self.generate_firmware_code()
        
        filename = filedialog.asksaveasfilename(
            title="Export Firmware",
            defaultextension=".py",
            filetypes=[("Python files", "*.py"), ("All files", "*.*")],
            initialfile="code.py"
        )
        
        if filename:
            try:
                with open(filename, 'w') as f:
                    f.write(firmware_code)
                messagebox.showinfo("✓ Success", 
                    f"Firmware exported to {filename}\n\n"
                    "Copy this file as 'code.py' to your CircuitPython device.")
            except Exception as e:
                messagebox.showerror("✗ Error", f"Failed to export firmware: {str(e)}")
    
    def generate_firmware_code(self):
        # Map common key names to Keycode strings used in CircuitPython
        key_mapping = {
            'F1': 'F1', 'F2': 'F2', 'F3': 'F3', 'F4': 'F4', 'F5': 'F5',
            'F6': 'F6', 'F7': 'F7', 'F8': 'F8', 'F9': 'F9', 'F10': 'F10',
            'F11': 'F11', 'F12': 'F12', 'ESCAPE': 'ESCAPE', 'ESC': 'ESCAPE',
            'TAB': 'TAB', 'SHIFT': 'SHIFT', 'CTRL': 'CONTROL', 'CONTROL': 'CONTROL',
            'ALT': 'ALT', 'SPACE': 'SPACE', 'ENTER': 'ENTER', 'RETURN': 'ENTER',
            'BACKSPACE': 'BACKSPACE'
        }
        
        hackpad_pins = ["board.D0", "board.D1", "board.D2", 
                        "board.D3", "board.D4", "board.D5"]
        
        pins_list = []
        keybinds_list = []

        for i, config in enumerate(self.key_configs):
            # Only process if we have a pin defined for this key index
            if i < len(hackpad_pins):
                pins_list.append(f"    {hackpad_pins[i]},  # Key {i+1}")
                
                custom_keys = config['custom_var'].get().strip()
                if custom_keys:
                    keys = [k.strip().upper() for k in custom_keys.split('+')]
                    keycode_list = []
                    for key in keys:
                        if key in key_mapping:
                            keycode_list.append(f"Keycode.{key_mapping[key]}")
                        else:
                            # Default to assuming it's a single letter/number
                            keycode_list.append(f"Keycode.{key}")
                    
                    keybinds_list.append(f"    [{', '.join(keycode_list)}],")
                else:
                    keybinds_list.append("    [], # Unconfigured")

        firmware = f'''import time
import board
import digitalio
import usb_hid
from adafruit_hid.keyboard import Keyboard
from adafruit_hid.keycode import Keycode

# Initialize keyboard
kbd = Keyboard(usb_hid.devices)

# Define physical pins for 3x2 Hackpad
KEY_PINS = [
{chr(10).join(pins_list)}
]

# Keybinds from Configurator
KEYBINDS = [
{chr(10).join(keybinds_list)}
]

# Setup Pins
keys = []
for pin in KEY_PINS:
    k = digitalio.DigitalInOut(pin)
    k.direction = digitalio.Direction.INPUT
    k.pull = digitalio.Pull.UP
    keys.append(k)

key_states = [False] * len(keys)

print("Skyboard Ready!")

while True:
    for i, key in enumerate(keys):
        # Button is pressed (False because of Pull.UP)
        if not key.value and not key_states[i]:
            key_states[i] = True
            if i < len(KEYBINDS) and KEYBINDS[i]:
                kbd.press(*KEYBINDS[i])
        
        # Button is released (True)
        elif key.value and key_states[i]:
            key_states[i] = False
            if i < len(KEYBINDS) and KEYBINDS[i]:
                kbd.release(*KEYBINDS[i])
                
    time.sleep(0.01)
'''
        return firmware

if __name__ == "__main__":
    root = tk.Tk()
    app = HackpadConfigGUI(root)
    root.mainloop()