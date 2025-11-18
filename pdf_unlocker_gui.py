#!/usr/bin/env python3
"""
pdf_unlocker_gui.py
GUI version for easier usage
"""

import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import os
import threading
from pypdf import PdfReader, PdfWriter


class PDFUnlockerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("PDF Password Unlocker")
        self.root.geometry("600x400")
        self.root.resizable(False, False)
        
        # Input file
        tk.Label(root, text="Input PDF:", font=("Arial", 10, "bold")).pack(pady=5)
        frame1 = tk.Frame(root)
        frame1.pack(fill=tk.X, padx=10, pady=5)
        self.input_var = tk.StringVar()
        tk.Entry(frame1, textvariable=self.input_var, width=50).pack(side=tk.LEFT)
        tk.Button(frame1, text="Browse", command=self.select_input).pack(side=tk.LEFT, padx=5)
        
        # Output file
        tk.Label(root, text="Output PDF:", font=("Arial", 10, "bold")).pack(pady=5)
        frame2 = tk.Frame(root)
        frame2.pack(fill=tk.X, padx=10, pady=5)
        self.output_var = tk.StringVar()
        tk.Entry(frame2, textvariable=self.output_var, width=50).pack(side=tk.LEFT)
        tk.Button(frame2, text="Browse", command=self.select_output).pack(side=tk.LEFT, padx=5)
        
        # Password
        tk.Label(root, text="Password:", font=("Arial", 10, "bold")).pack(pady=5)
        self.password_var = tk.StringVar()
        tk.Entry(root, textvariable=self.password_var, show="*", width=50).pack(padx=10, pady=5)
        
        # Progress
        self.progress = ttk.Progressbar(root, mode='indeterminate')
        self.progress.pack(fill=tk.X, padx=10, pady=10)
        
        # Unlock button
        tk.Button(root, text="Unlock PDF", command=self.unlock, 
                 bg="#4CAF50", fg="white", font=("Arial", 11, "bold"), 
                 padx=20, pady=10).pack(pady=10)
        
        # Status
        self.status_var = tk.StringVar(value="Ready")
        tk.Label(root, textvariable=self.status_var, wraplength=550).pack(pady=10)
    
    def select_input(self):
        file = filedialog.askopenfilename(filetypes=[("PDF files", "*.pdf")])
        if file:
            self.input_var.set(file)
    
    def select_output(self):
        file = filedialog.asksaveasfilename(defaultextension=".pdf", 
                                           filetypes=[("PDF files", "*.pdf")])
        if file:
            self.output_var.set(file)
    
    def unlock(self):
        input_pdf = self.input_var.get()
        output_pdf = self.output_var.get()
        password = self.password_var.get()
        
        if not all([input_pdf, output_pdf, password]):
            messagebox.showerror("Error", "Please fill all fields")
            return
        
        # Run in thread to prevent GUI freezing
        thread = threading.Thread(target=self._unlock_thread, 
                                 args=(input_pdf, output_pdf, password))
        thread.start()
    
    def _unlock_thread(self, input_pdf, output_pdf, password):
        try:
            self.progress.start()
            self.status_var.set("Processing...")
            self.root.update()
            
            reader = PdfReader(input_pdf)
            
            if not reader.is_encrypted:
                raise ValueError("PDF is not password-protected")
            
            if not reader.decrypt(password):
                raise ValueError("Incorrect password")
            
            writer = PdfWriter()
            for page in reader.pages:
                writer.add_page(page)
            
            if reader.metadata:
                writer.add_metadata(reader.metadata)
            
            original_size = os.path.getsize(input_pdf)
            
            with open(output_pdf, 'wb') as f:
                writer.write(f)
            
            output_size = os.path.getsize(output_pdf)
            
            self.progress.stop()
            self.status_var.set(
                f"✓ Success!\nOriginal: {original_size:,} bytes | "
                f"Unlocked: {output_size:,} bytes"
            )
            messagebox.showinfo("Success", "PDF unlocked successfully!")
            
        except Exception as e:
            self.progress.stop()
            self.status_var.set(f"✗ Error: {str(e)}")
            messagebox.showerror("Error", str(e))


if __name__ == "__main__":
    root = tk.Tk()
    app = PDFUnlockerGUI(root)
    root.mainloop()