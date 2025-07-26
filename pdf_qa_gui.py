import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
import shutil
import os
import glob

from module1 import answer_question, load_index
from PDFAI import extract_texts, chunk_texts, build_faiss_index
from DB import connect_to_db, close_connection, fetch_query

current_username = None

def show_login_window(logout=False):
    if logout:
        messagebox.showinfo("Logged out", "You were logged out.")

    def attempt_login():
        EmployeeID = entry_user.get().strip()
        password = entry_pass.get().strip()

        if not EmployeeID or not password:
            messagebox.showwarning("Missing Info", "Please enter both EmployeeID and password.")
            return

        conn = connect_to_db()
        query = "SELECT * FROM Employees WHERE EmployeeID=" + str(EmployeeID) + " AND EmployeePassWord='" + password + "'"
        result = fetch_query(conn, query)

        if result:
            login_window.destroy()
            show_main_window(EmployeeID)
        else:
            messagebox.showerror("Login Failed", "Invalid credentials.")

    login_window = tk.Tk()
    login_window.title("Login")
    login_window.geometry("300x200")

    tk.Label(login_window, text="Login to ClarifAI", font=("Arial", 14)).pack(pady=10)
    tk.Label(login_window, text="EmployeeID:").pack()
    entry_user = tk.Entry(login_window)
    entry_user.pack()

    tk.Label(login_window, text="Password:").pack()
    entry_pass = tk.Entry(login_window, show="*")
    entry_pass.pack()
    entry_pass.bind("<Return>", lambda event: attempt_login())

    tk.Button(login_window, text="Login", command=attempt_login).pack(pady=10)

    login_window.mainloop()

def show_main_window(username):
    index_built = False

    def logout():
        global current_username
        if messagebox.askyesno("Logout", "Are you sure you want to log out?"):
            current_username = None
            main_root.destroy()
            show_login_window(True)

    def upload_pdfs():
        nonlocal index_built

        files = filedialog.askopenfilenames(filetypes=[("PDF Files", "*.pdf")])
        if not files:
            return

        os.makedirs("data", exist_ok=True)
        os.makedirs("index", exist_ok=True)

        # Clear old files
        uploaded_files_list.delete(0, tk.END)
        for old_file in glob.glob("data/*.pdf"):
            os.remove(old_file)

        # Clear old index
        for idx_file in ["index/faiss_index.index", "index/faiss_index.pkl"]:
            if os.path.exists(idx_file):
                os.remove(idx_file)

        for file in files:
            dest_path = os.path.join("data", os.path.basename(file))
            shutil.copy(file, dest_path)
            uploaded_files_list.insert(tk.END, os.path.basename(file))

        messagebox.showinfo("Success", "PDFs uploaded.")
        status_text.set("Processing PDFs and building index...")
        main_root.update()

        docs = extract_texts("data")
        chunks = chunk_texts(docs)
        build_faiss_index(chunks)
        load_index()
        status_text.set("Index built. You can now ask questions.")
        index_built = True

    def ask_question():
        if not index_built:
            messagebox.showwarning("No PDFs", "Please upload PDFs before asking questions.")
            return

        q = question_entry.get().strip()
        if not q:
            messagebox.showwarning("Input Error", "Please enter a question.")
            return


        status_text.set("Thinking...")
        main_root.update()
        answer = answer_question(q)
        output_box.delete(1.0, tk.END)
        output_box.insert(tk.END, answer)
        status_text.set("Answer ready.")

    main_root = tk.Tk()
    main_root.title(f"PDF Information Assistant - Logged in as {username}")
    main_root.geometry("700x600")

    top_frame = tk.Frame(main_root)
    top_frame.pack(fill="x", anchor="n")
    tk.Button(top_frame, text="Log Out", command=logout, width=10, fg="red").pack(side="left", padx=10, pady=5)

    center_frame = tk.Frame(main_root)
    center_frame.pack(pady=10)

    tk.Label(center_frame, text="\U0001F4C4 ClarifAI", font=("Helvetica", 16, "bold")).grid(row=0, column=0, columnspan=2, pady=10)
    tk.Button(center_frame, text="Upload PDFs", command=upload_pdfs, width=30).grid(row=1, column=0, columnspan=2, pady=5)

    tk.Label(center_frame, text="Uploaded PDFs:").grid(row=2, column=0, sticky="w", padx=10)
    global uploaded_files_list
    uploaded_files_list = tk.Listbox(center_frame, height=6, width=60)
    uploaded_files_list.grid(row=3, column=0, columnspan=2, padx=10, pady=5)

    tk.Label(center_frame, text="Ask a question:").grid(row=4, column=0, sticky="w", padx=10)
    question_entry = tk.Entry(center_frame, width=60)
    question_entry.grid(row=5, column=0, columnspan=2, padx=10, pady=5)
    question_entry.bind("<Return>", lambda event: ask_question())

    tk.Button(center_frame, text="Get Answer", command=ask_question, width=20).grid(row=6, column=0, columnspan=2, pady=10)

    global output_box
    output_box = scrolledtext.ScrolledText(center_frame, height=10, wrap=tk.WORD, width=80)
    output_box.grid(row=7, column=0, columnspan=2, padx=10, pady=5)

    global status_text
    status_text = tk.StringVar(value="Ready.")
    tk.Label(main_root, textvariable=status_text, anchor="w").pack(fill="x", padx=10, pady=5)

    main_root.mainloop()

if __name__ == "__main__":
    show_login_window()