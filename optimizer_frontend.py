# =============================================================================

# DESCRIPTION:
# Frontend UI module for Project Zenith.
# Contains the main App class, built with CustomTkinter. This module handles
# all window, widget, and layout creation, and connects UI events to the
# backend logic.
# =============================================================================

import customtkinter
import threading
import queue
import optimizer_backend as backend

class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()

        # --- Basic App Configuration ---
        self.title("Project Zenith MVP")
        self.geometry("1200x800")
        self.resizable(False, False)
        customtkinter.set_appearance_mode("Dark")
        customtkinter.set_default_color_theme("blue")

        # --- State and Threading ---
        self.analysis_results = None
        self.thread_queue = queue.Queue()

        # --- Main Layout ---
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # --- Navigation Frame (Sidebar) ---
        self.navigation_frame = self.create_navigation_frame()
        self.navigation_frame.grid(row=0, column=0, sticky="nsew")

        # --- Content Frames ---
        self.dashboard_frame = self.create_dashboard_frame()
        self.optimizer_frame = self.create_optimizer_frame()
        self.tools_frame = self.create_tools_frame()

        # --- Select default frame and start queue processor ---
        self.select_frame_by_name("dashboard")
        self.after(100, self.process_queue)

    def create_navigation_frame(self):
        frame = customtkinter.CTkFrame(self, corner_radius=0)
        frame.grid_rowconfigure(5, weight=1)

        title = customtkinter.CTkLabel(frame, text="Project Zenith", font=customtkinter.CTkFont(size=20, weight="bold"))
        title.grid(row=0, column=0, padx=20, pady=(20, 10))

        self.dashboard_button = customtkinter.CTkButton(frame, corner_radius=0, height=40, border_spacing=10, text="Dashboard",
                                                       fg_color="transparent", text_color=("gray10", "gray90"), anchor="w",
                                                       command=self.dashboard_button_event)
        self.dashboard_button.grid(row=1, column=0, sticky="ew")

        self.optimizer_button = customtkinter.CTkButton(frame, corner_radius=0, height=40, border_spacing=10, text="Optimizer",
                                                         fg_color="transparent", text_color=("gray10", "gray90"), anchor="w",
                                                         command=self.optimizer_button_event)
        self.optimizer_button.grid(row=2, column=0, sticky="ew")
        
        self.tools_button = customtkinter.CTkButton(frame, corner_radius=0, height=40, border_spacing=10, text="Tools",
                                                   fg_color="transparent", text_color=("gray10", "gray90"), anchor="w",
                                                   command=self.tools_button_event)
        self.tools_button.grid(row=3, column=0, sticky="ew")

        return frame

    def create_dashboard_frame(self):
        frame = customtkinter.CTkFrame(self, corner_radius=0, fg_color="transparent")
        frame.grid_columnconfigure(0, weight=1)
        
        self.status_label = customtkinter.CTkLabel(frame, text="Click 'Analyze System' to check for junk files.",
                                                   font=customtkinter.CTkFont(size=16))
        self.status_label.grid(row=0, column=0, padx=20, pady=(20, 10))

        self.action_button = customtkinter.CTkButton(frame, text="ANALYZE SYSTEM", height=50, 
                                                     font=customtkinter.CTkFont(size=20, weight="bold"),
                                                     command=self.start_analysis)
        self.action_button.grid(row=1, column=0, padx=50, pady=20)
        
        return frame

    def create_optimizer_frame(self):
        frame = customtkinter.CTkFrame(self, corner_radius=0, fg_color="transparent")
        frame.grid_columnconfigure(0, weight=1)
        frame.grid_rowconfigure(1, weight=1)

        title = customtkinter.CTkLabel(frame, text="Startup Manager", font=customtkinter.CTkFont(size=20, weight="bold"))
        title.grid(row=0, column=0, padx=20, pady=(20, 10), sticky="w")
        
        self.startup_scrollable_frame = customtkinter.CTkScrollableFrame(frame, label_text="Programs that start with Windows")
        self.startup_scrollable_frame.grid(row=1, column=0, padx=20, pady=10, sticky="nsew")

        return frame

    def create_tools_frame(self):
        frame = customtkinter.CTkFrame(self, corner_radius=0, fg_color="transparent")
        frame.grid_columnconfigure(0, weight=1)

        title = customtkinter.CTkLabel(frame, text="System Information", font=customtkinter.CTkFont(size=20, weight="bold"))
        title.grid(row=0, column=0, padx=20, pady=(20, 10), sticky="w")
        
        self.sys_info_label = customtkinter.CTkLabel(frame, text="Loading system info...", justify="left",
                                                     font=customtkinter.CTkFont(family="monospace"))
        self.sys_info_label.grid(row=1, column=0, padx=20, pady=10, sticky="w")

        return frame

    def run_in_thread(self, target_func, callback):
        def thread_target():
            result = target_func()
            self.thread_queue.put((callback, result))
        
        thread = threading.Thread(target=thread_target)
        thread.daemon = True
        thread.start()

    def process_queue(self):
        try:
            callback, result = self.thread_queue.get(block=False)
            callback(result)
        except queue.Empty:
            pass
        self.after(100, self.process_queue)

    def start_analysis(self):
        self.action_button.configure(state="disabled", text="ANALYZING...")
        self.run_in_thread(backend.find_temp_files, self.on_analysis_complete)

    def on_analysis_complete(self, results):
        self.analysis_results = results
        size_mb = results.get('total_size_mb', 0)
        
        self.status_label.configure(text=f"Analysis Complete. Found {size_mb} MB of junk files.")
        self.action_button.configure(state="normal", text=f"CLEAN {size_mb} MB NOW", command=self.start_cleaning)

    def start_cleaning(self):
        if not self.analysis_results:
            return
        files_to_clean = self.analysis_results.get('files_to_clean', [])
        
        self.action_button.configure(state="disabled", text="CLEANING...")
        self.run_in_thread(lambda: backend.clean_files(files_to_clean), self.on_cleaning_complete)

    def on_cleaning_complete(self, num_errors):
        if num_errors == 0:
            self.status_label.configure(text="System is clean and optimized!")
        else:
            self.status_label.configure(text=f"Cleaning complete. Could not delete {num_errors} files (likely in use).")
        
        self.action_button.configure(text="ANALYZE SYSTEM", command=self.start_analysis, state="normal")
        self.analysis_results = None

    def populate_startup_list(self):
        for widget in self.startup_scrollable_frame.winfo_children():
            widget.destroy()
        
        loading_label = customtkinter.CTkLabel(self.startup_scrollable_frame, text="Loading startup items...")
        loading_label.pack(pady=10)
        
        self.run_in_thread(backend.get_startup_programs, self.on_startup_list_loaded)
        
    def on_startup_list_loaded(self, programs):
        for widget in self.startup_scrollable_frame.winfo_children():
            widget.destroy()

        if not programs:
            label = customtkinter.CTkLabel(self.startup_scrollable_frame, text="No startup programs found.")
            label.pack(pady=10)
            return

        for program in programs:
            checkbox = customtkinter.CTkCheckBox(self.startup_scrollable_frame, text=program['name'])
            if program.get('enabled', False):
                checkbox.select()
            checkbox.pack(padx=10, pady=5, anchor="w")

    def populate_system_info(self):
        self.sys_info_label.configure(text="Loading system info...")
        self.run_in_thread(backend.get_system_info, self.on_system_info_loaded)

    def on_system_info_loaded(self, info):
        info_text = (
            f"Operating System: {info.get('os', 'N/A')}\n"
            f"CPU Usage:        {info.get('cpu_usage', 'N/A')}%\n"
            f"RAM Usage:        {info.get('ram_usage', 'N/A')}%\n"
            f"Disk Usage:       {info.get('disk_usage', 'N/A')}%"
        )
        self.sys_info_label.configure(text=info_text)

    def select_frame_by_name(self, name):
        # Set button colors
        self.dashboard_button.configure(fg_color=("gray75", "gray25") if name == "dashboard" else "transparent")
        self.optimizer_button.configure(fg_color=("gray75", "gray25") if name == "optimizer" else "transparent")
        self.tools_button.configure(fg_color=("gray75", "gray25") if name == "tools" else "transparent")

        # Hide all frames
        self.dashboard_frame.grid_forget()
        self.optimizer_frame.grid_forget()
        self.tools_frame.grid_forget()

        # Show the selected frame
        if name == "dashboard":
            self.dashboard_frame.grid(row=0, column=1, sticky="nsew")
        elif name == "optimizer":
            self.optimizer_frame.grid(row=0, column=1, sticky="nsew")
        elif name == "tools":
            self.tools_frame.grid(row=0, column=1, sticky="nsew")

    def dashboard_button_event(self):
        self.select_frame_by_name("dashboard")

    def optimizer_button_event(self):
        self.select_frame_by_name("optimizer")
        self.populate_startup_list()
        
    def tools_button_event(self):
        self.select_frame_by_name("tools")
        self.populate_system_info()
