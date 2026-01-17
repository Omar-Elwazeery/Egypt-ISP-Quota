import customtkinter as ctk
import threading
from tkinter import messagebox
from account_manager import AccountManager
from quota_manager import QuotaManager

# --- Configuration ---
ctk.set_appearance_mode("Dark")  # Modes: "System" (standard), "Dark", "Light"
ctk.set_default_color_theme("dark-blue")  # Themes: "blue" (standard), "green", "dark-blue"

class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Managers
        self.account_manager = AccountManager()
        # QuotaManager will be instantiated per check or re-used. 
        # Modifying QuotaManager to accept headless param dynamically is better, 
        # but for now we can rely on passing it in get_quota or re-init.
        # Let's pass it in get_quota.
        self.quota_manager = QuotaManager()
        self.current_account = None
        self.check_thread = None
        self.stop_check = False  # Flag to signal stopping the check

        # Window Setup
        self.title("Egypt ISP Quota Checker")
        self.geometry("900x600")

        # Grid Layout
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Debug Mode Var
        self.debug_mode = ctk.BooleanVar(value=False)
        
        # Bind window close to cleanup
        self.protocol("WM_DELETE_WINDOW", self._on_closing)



        # --- Sidebar (Account List) ---
        self.sidebar_frame = ctk.CTkFrame(self, width=250, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(2, weight=1)

        self.logo_label = ctk.CTkLabel(self.sidebar_frame, text="ISP Quota", font=ctk.CTkFont(size=24, weight="bold"))
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 10))

        self.add_account_btn = ctk.CTkButton(self.sidebar_frame, text="+ Add Account", command=self.show_add_account_view)
        self.add_account_btn.grid(row=1, column=0, padx=20, pady=10)

        self.accounts_list_frame = ctk.CTkScrollableFrame(self.sidebar_frame, label_text="Accounts")
        self.accounts_list_frame.grid(row=2, column=0, padx=20, pady=10, sticky="nsew")

        # Debug Toggle
        self.debug_switch = ctk.CTkSwitch(self.sidebar_frame, text="Debug Mode (Show Browser)", variable=self.debug_mode)
        self.debug_switch.grid(row=3, column=0, padx=20, pady=(10, 5))



        # --- Main Area ---
        self.main_frame = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.main_frame.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)
        
        # We will dynamically pack content into main_frame
        # Start by showing placeholder or first account
        self.refresh_account_list()
        
        # Load first account if exists
        accounts = self.account_manager.get_accounts()
        if accounts:
            self.select_account(accounts[0])
        else:
            self.show_add_account_view()

    def refresh_account_list(self):
        # Clear existing buttons
        for widget in self.accounts_list_frame.winfo_children():
            widget.destroy()

        accounts = self.account_manager.get_accounts()
        for acc in accounts:
            btn = ctk.CTkButton(
                self.accounts_list_frame, 
                text=acc['name'], 
                fg_color="transparent", 
                border_width=1,
                command=lambda a=acc: self.select_account(a)
            )
            btn.pack(pady=5, padx=5, fill="x")

    def clear_main_frame(self):
        for widget in self.main_frame.winfo_children():
            widget.destroy()

    def show_add_account_view(self):
        self.clear_main_frame()
        self.current_account = None

        # Title
        ctk.CTkLabel(self.main_frame, text="Add New Account", font=ctk.CTkFont(size=24)).pack(pady=20)

        # Form
        entry_frame = ctk.CTkFrame(self.main_frame)
        entry_frame.pack(pady=10, padx=20, fill="x")

        ctk.CTkLabel(entry_frame, text="Account Name (Alias)").pack(anchor="w", padx=10, pady=(10,0))
        name_entry = ctk.CTkEntry(entry_frame)
        name_entry.pack(fill="x", padx=10, pady=5)

        ctk.CTkLabel(entry_frame, text="Service Number").pack(anchor="w", padx=10, pady=(10,0))
        num_entry = ctk.CTkEntry(entry_frame)
        num_entry.pack(fill="x", padx=10, pady=5)

        ctk.CTkLabel(entry_frame, text="Password").pack(anchor="w", padx=10, pady=(10,0))
        
        # Password field with show/hide toggle
        pass_frame = ctk.CTkFrame(entry_frame, fg_color="transparent")
        pass_frame.pack(fill="x", padx=10, pady=5)
        
        pass_entry = ctk.CTkEntry(pass_frame, show="*")
        pass_entry.pack(side="left", fill="x", expand=True)
        
        def toggle_password():
            if pass_entry.cget("show") == "*":
                pass_entry.configure(show="")
                show_pass_btn.configure(text="Hide")
            else:
                pass_entry.configure(show="*")
                show_pass_btn.configure(text="Show")
        
        show_pass_btn = ctk.CTkButton(pass_frame, text="Show", width=60, command=toggle_password)
        show_pass_btn.pack(side="right", padx=(10, 0))

        ctk.CTkLabel(entry_frame, text="Service Type").pack(anchor="w", padx=10, pady=(10,0))
        type_var = ctk.StringVar(value="Internet")
        type_menu = ctk.CTkOptionMenu(entry_frame, variable=type_var, values=["Internet", "4G"])
        type_menu.pack(fill="x", padx=10, pady=5)

        def save():
            name = name_entry.get()
            number = num_entry.get()
            password = pass_entry.get()
            svc_type = type_var.get()

            if not name or not number or not password:
                return

            self.account_manager.add_account(name, number, password, svc_type)
            self.refresh_account_list()
            # Select the newly created account
            new_acc = self.account_manager.get_accounts()[-1]
            self.select_account(new_acc)

        ctk.CTkButton(self.main_frame, text="Save Account", command=save, height=40).pack(pady=20)


    def select_account(self, account):
        self.current_account = account
        self.clear_main_frame()

        # Update sidebar styling eventually to show selected? (skip for simplicity now)

        # --- Account Details View ---
        
        # Header
        header = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        header.pack(fill="x", pady=10)
        
        ctk.CTkLabel(header, text=account['name'], font=ctk.CTkFont(size=32, weight="bold")).pack(side="left")
        
        def delete():
            self.account_manager.delete_account(account['id'])
            self.refresh_account_list()
            accounts = self.account_manager.get_accounts()
            if accounts:
                self.select_account(accounts[0])
            else:
                self.show_add_account_view()

        ctk.CTkButton(header, text="Delete", fg_color="red", width=60, command=delete).pack(side="right")

        # Usage Display
        self.status_label = ctk.CTkLabel(self.main_frame, text="Ready to check quota", text_color="gray")
        self.status_label.pack(pady=10)

        # Large Quota Display
        self.quota_display = ctk.CTkLabel(self.main_frame, text="-- GB", font=ctk.CTkFont(size=64, weight="bold"))
        self.quota_display.pack(pady=30)
        
        # Buttons Frame
        btn_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        btn_frame.pack(pady=20, fill="x", padx=40)
        
        # Check Button
        self.check_btn = ctk.CTkButton(btn_frame, text="Check Quota Now", height=50, font=ctk.CTkFont(size=18), command=self.start_quota_check)
        self.check_btn.pack(side="left", fill="x", expand=True)
        
        # Stop Button (initially hidden)
        self.stop_btn = ctk.CTkButton(btn_frame, text="Stop", height=50, width=80, fg_color="red", hover_color="darkred", font=ctk.CTkFont(size=18), command=self.stop_quota_check)
        # Don't pack stop button initially - will be shown when checking starts

        # Info Box
        info_frame = ctk.CTkFrame(self.main_frame)
        info_frame.pack(fill="x", padx=40, pady=20)
        
        ctk.CTkLabel(info_frame, text=f"Number: {account['number']}").pack(anchor="w", padx=10, pady=5)
        ctk.CTkLabel(info_frame, text=f"Service Type: {account['service_type']}").pack(anchor="w", padx=10, pady=5)


    def start_quota_check(self):
        if not self.current_account:
            return
        
        self.stop_check = False  # Reset stop flag
        self.check_btn.configure(state="disabled", text="Checking...")
        self.stop_btn.pack(side="right", padx=(10, 0))  # Show stop button
        self.status_label.configure(text="Logging in... (This takes a few seconds)", text_color="yellow")
        
        # Run in thread to not freeze UI
        self.check_thread = threading.Thread(target=self._run_check_quota)
        self.check_thread.start()

    def stop_quota_check(self):
        """Stop the ongoing quota check"""
        self.stop_check = True
        self.status_label.configure(text="Stopping...", text_color="orange")
        
        # Force close the browser if running
        if self.quota_manager.driver:
            try:
                self.quota_manager.driver.quit()
            except:
                pass
            self.quota_manager.driver = None
        
        self._reset_check_ui("Check stopped by user")

    def _run_check_quota(self):
        try:
            # Get verify SSL setting
            # debug_mode = self.debug_mode.get() == 1
            # For now force debug mode if desired, or read from switch
            is_debug = bool(self.debug_mode.get())
            
            username = self.current_account["number"] # Changed from "username" to "number" based on existing code
            password = self.current_account["password"]
            
            # Pass stop_check check to manager? 
            # Ideally manager checks it, but for now we just kill driver on stop.
            
            quota = self.quota_manager.get_quota(
                username, 
                password, 
                service_type=self.current_account['service_type'], # Use actual service type from account
                debug_mode=is_debug
            )
            
            if self.stop_check:
                return # Check was stopped
                
            # Update UI on main thread
            self.after(0, lambda: self._update_quota_success(quota))
            
        except Exception as e:
            if self.stop_check:
                return
            err_msg = str(e)
            self.after(0, lambda: self._update_quota_error(err_msg))

    def _update_quota_success(self, quota):
        self.quota_display.configure(text=f"{quota}")
        self.status_label.configure(text="Updated just now", text_color="green")
        self._reset_check_ui()

    def _update_quota_error(self, error):
        self.status_label.configure(text=f"Error: {error}", text_color="red")
        self._reset_check_ui()

    def _reset_check_ui(self, status_text=None):
        """Reset the check UI to ready state"""
        self.check_btn.configure(state="normal", text="Check Quota Now")
        try:
            self.stop_btn.pack_forget()  # Hide stop button
        except:
            pass
        if status_text:
            self.status_label.configure(text=status_text, text_color="orange")

    def _on_closing(self):
        """Clean up browser and close app"""
        print("[DEBUG] App closing, cleaning up...")
        if self.quota_manager.driver:
            try:
                self.quota_manager.driver.quit()
                print("[DEBUG] Browser closed successfully")
            except:
                pass
        self.destroy()


if __name__ == "__main__":
    app = App()
    app.mainloop()
