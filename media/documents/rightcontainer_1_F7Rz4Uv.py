import tkinter as tk
from tkinter import filedialog, ttk
from PIL import Image, ImageTk
from pathlib import Path
import webview
import json
import time 


ASSETS_DIR = Path(__file__).parent.parent / "assets"
upload_icon_path = ASSETS_DIR / "upload_icon.png"

def create_right_content(root):
    style = ttk.Style()
    style.theme_use("default")
    style.configure(
        "TNotebook.Tab",
        background="#e9ecef",
        foreground="#333333",
        font=("Arial", 10, "bold"),
        padding=[10, 5],  
    )

    style.map(
        "TNotebook.Tab",
        background=[("selected", "#4f8cf0")],
        foreground=[("selected", "white")]
    )

    style.configure("TNotebook.Tab", focuscolor="none")
    main_frame = tk.Frame(root, bg="white")
    main_frame.pack(side="right", expand=True, fill="both", padx=(0, 10), pady=5)
    upper_frame = tk.Frame(main_frame, bg="white", relief="groove", bd=1)
    upper_frame.pack(side="top", fill="x", padx=5, pady=(5,2))
    title_label = tk.Label(
        upper_frame, text="* Visualizations - Source Path", bg="white", fg="red", font=("Times New Roman", 12, "bold")
    )
    title_label.pack(anchor="w", pady=(5, 2), padx=10)
    def upload_file():
        filedialog.askopenfile(title="Select a ZIP File", filetypes=[("ZIP Files", "*.zip")])
    try:
        icon_image = Image.open(upload_icon_path).resize((20, 20), Image.Resampling.LANCZOS)
        upload_icon = ImageTk.PhotoImage(icon_image)
    except Exception as e:
        print(f"Error loading icon: {e}")
        upload_icon = None
    upload_button = tk.Button(
        upper_frame,
        text="  Upload ZIP File",
        image=upload_icon,
        compound="left",
        bg="#e9ecef",
        fg="black",
        font=("Times New Roman", 10),
        relief="ridge",
        command=upload_file,
    )

    upload_button.image = upload_icon
    upload_button.pack(anchor="w", pady=3, padx=10)
    options_label = tk.Label(upper_frame, text="Targeted BI Destination", bg="white", fg="red", font=("Times New Roman", 12))
    options_label.pack(anchor="w", padx=10, pady=3)
    checkbox_frame = tk.Frame(upper_frame, bg="white")
    checkbox_frame.pack(anchor="w", padx=10, pady=0)
    button_frame = tk.Frame(upper_frame, bg="white")
    button_frame.pack(anchor="w", pady=3, padx=10)
    access_button = tk.Button(
        button_frame,
        text="Assess",
        bg="#4f8cf0",
        fg="white",
        font=("Times New Roman", 12, "bold"),
        relief="ridge",
        width=8,
        height=1,
    )
    access_button.pack(side="left", padx=5)
    migrate_button = tk.Button(
        button_frame,
        text="Migrate",
        bg="#4f8cf0",
        fg="white",
        font=("Times New Roman", 12, "bold"),
        relief="ridge",
        width=8,
        height=1,
    )
    migrate_button.pack(side="left", padx=5)

    lower_frame = tk.Frame(main_frame, bg="white", relief="groove", bd=1)
    lower_frame.pack(side="top", fill="both", expand=True, padx=5, pady=(12,6))
    tab_control = ttk.Notebook(lower_frame)
    assessment_tab = tk.Frame(tab_control, bg="white")
    tab_control.add(assessment_tab, text="Assessment Log")
    assessment_label = tk.Label(
        assessment_tab, text="Assessment Log Content", bg="white", font=("Arial", 10)
    )
    assessment_label.pack(anchor="center", pady=20)
    summary_tab = tk.Frame(tab_control, bg="white")
    tab_control.add(summary_tab, text="Summary")
    summary_label = tk.Label(
        summary_tab, text="Summary Content", bg="white", font=("Arial", 10)
    )
    summary_label.pack(anchor="center", pady=20)

    def load_credentials(file_):
        with open(file_,'r') as file:
            return json.load(file)
    
    def auto_login(window,credentials):
        js_code = f"""
        document.getElementById('username').value = "{credentials['username']}";
        document.getElementById('password').value = "{credentials['password']}";
        document.querySelector('input[type="submit"]').click();
        """
        window.evaluate_js(js_code)
        # time.sleep(2)

        # js_code1 =f"""
        # document.getElementById('site-uri').value = "{credentials['uri']}";
        # document.querySelector('#verify-button').disabled =false;
        # document.querySelector('#verify-button').click();
        # """  
        # window.evaluate_js(js_code1)
        # time.sleep(4)

        # js_code2 = f"""
        # document.getElementById('password').value = "{credentials['password']}";
        # document.querySelector('button[type="submit"]').click();
        # """
        # window.evaluate_js(js_code2)

    def iframe_page(option):

        credentials = load_credentials("D:\\GUI\\tkinter\\tkinter\\src\\config.json")

        iframe_window = webview.create_window(option[0], option[1],height=900,width=1200)

        def on_loaded(window):
            auto_login(iframe_window,credentials)

        webview.start(on_loaded,iframe_window)


    checkboxes = {}
    created_tabs = {}
    def on_checkbox_change(option, var):
        if var.get():  
            if option[0] not in created_tabs: 
                new_tab = tk.Frame(tab_control, bg="white")
                tab_control.add(new_tab, text=option[0])
                created_tabs[option[0]] = new_tab
                view_label = tk.Label(new_tab,text='View',font=("Arial", 10,"underline"),cursor="hand2",fg="blue")
                view_label.pack(anchor="center",pady=10)
                view_label.bind("<Button-1>", lambda event: iframe_page(option))
        else: 
            if option[0] in created_tabs:  
                tab_control.forget(created_tabs[option[0]])
                del created_tabs[option[0]]

    # options = ["Superset", "PowerBI - Paginated Report", "PowerBI - Visualization", "Tableau"]
    options = {"Superset":"https://superset.edtechmarks.com/login", "PowerBI - Paginated Report":"https://app.powerbi.com", "PowerBI - Visualization":"https://app.powerbi.com", "Tableau":"https://sso.online.tableau.com/public/idp/SSO"}
    for option,link in options.items():
        var = tk.BooleanVar()
        var.trace("w", lambda *args, opt=[option,link], v=var: on_checkbox_change(opt, v))
        checkboxes[option] = var
        tk.Checkbutton(checkbox_frame, text=option, bg="white", font=("Arial", 10), variable=var).pack(anchor="w")
    tab_control.pack(expand=True, fill="both")
