import json
import os
import hashlib
import tkinter as tk
from tkinter import *
from tkinter import ttk, messagebox

class MedicalSystem:
    def __init__(self, root):
        self.root = root
        self.root.title("Secure Medical System")
        self.root.geometry("1000x700")
        
        self.primary_color = "#4682b4"  
        self.secondary_color = "#5f9ea0"  
        self.accent_color = "#ff7f50"  
        self.danger_color = "#ff6b6b"  

        self.title_font = ("Arial", 16, "bold")
        self.button_font = ("Arial", 12)
        self.text_font = ("Arial", 11)
        
        self.root.configure(bg="#f0f8ff")

        self.users = {}
        self.patients = {}
        self.appointments = []
        self.current_user = None
        
        self.security_questions = [
            "What was your first pet's name?",
            "What city were you born in?",
            "What is your mother's maiden name?"
        ]
        
        self.data_dir = "medical_data"
        os.makedirs(self.data_dir, exist_ok=True)
        self.users_file = os.path.join(self.data_dir, "users.json")
        self.patients_file = os.path.join(self.data_dir, "patients.json") 
        self.appointments_file = os.path.join(self.data_dir, "appointments.json")
        
        self.load_data()
        self.setup_login_screen()  

    def setup_styles(self):
        self.root.configure(bg="#f0f8ff")  
        
        Button(self.root, 
              bg="#4682b4", fg="white", 
              font=("Arial", 12), 
              relief="flat").configure()
        
        Entry(self.root, 
             font=("Arial", 12), 
             bd=2, relief="groove").configure()

    def load_data(self):
        try:
            with open(self.users_file, 'r') as f:
                self.users = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            self.users = {
                "admin": {
                    "password": self.hash_password("admin123"),
                    "role": "admin",
                    "security_question": self.security_questions[0],
                    "security_answer": self.hash_password("Fluffy"),
                    "name": "System Admin"
                }
            }
        
        try:
            with open(self.patients_file, 'r') as f:
                self.patients = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            self.patients = {}
            
        try:
            with open(self.appointments_file, 'r') as f:
                self.appointments = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            self.appointments = []

    def save_data(self):
        with open(self.users_file, 'w') as f:
            json.dump(self.users, f, indent=2)
        with open(self.patients_file, 'w') as f:
            json.dump(self.patients, f, indent=2)
        with open(self.appointments_file, 'w') as f:
            json.dump(self.appointments, f, indent=2)

    def clear_window(self):
        for widget in self.root.winfo_children():
            widget.destroy()
    
    def setup_login_screen(self):
        self.clear_window()
        
        header = Frame(self.root, bg="#4682b4")
        header.pack(fill=X, pady=(0,20))
        Label(header, text="Medical System Login", font=("Arial", 20), 
             bg="#4682b4", fg="white").pack(pady=20)
        
        form_frame = Frame(self.root, bg="#f0f8ff")
        form_frame.pack(pady=20)
        
        Label(form_frame, text="Username:", bg="#f0f8ff").grid(row=0, column=0, sticky=E, pady=5)
        self.username_entry = Entry(form_frame)
        self.username_entry.grid(row=0, column=1, pady=5)
        
        Label(form_frame, text="Password:", bg="#f0f8ff").grid(row=1, column=0, sticky=E, pady=5)
        self.password_entry = Entry(form_frame, show="•")
        self.password_entry.grid(row=1, column=1, pady=5)
        
        button_frame = Frame(self.root, bg="#f0f8ff")
        button_frame.pack(pady=20)
        
        Button(button_frame, text="Login", command=self.authenticate,
              bg="#5f9ea0", fg="white", font=("Arial", 12)).pack(side=LEFT, padx=10)
        
        Button(button_frame, text="Forgot Password", command=self.show_password_recovery,
              bg="#ff7f50", fg="white", font=("Arial", 12)).pack(side=LEFT, padx=10)
        
        Button(button_frame, text="Register", command=self.show_registration,
              bg="#4682b4", fg="white", font=("Arial", 12)).pack(side=LEFT, padx=10)

    def hash_password(self, password):
        return hashlib.sha256(password.encode()).hexdigest()
    
    def authenticate(self):
        username = self.username_entry.get()
        password = self.hash_password(self.password_entry.get())
        
        if username in self.users and self.users[username]["password"] == password:
            self.current_user = username
            self.show_dashboard()
        else:
            messagebox.showerror("Error", "Invalid credentials")
    
    def show_password_recovery(self):
        popup = Toplevel(self.root)
        popup.title("Password Recovery")
        
        Label(popup, text="Username:").pack(pady=5)
        username_entry = Entry(popup)
        username_entry.pack(pady=5)
        
        def verify_user():
            username = username_entry.get()
            if username in self.users:
                user = self.users[username]
                Label(popup, text=f"Question: {user['security_question']}").pack()
                answer_entry = Entry(popup, show="•")
                answer_entry.pack(pady=5)
                
                def check_answer():
                    if self.hash_password(answer_entry.get()) == user["security_answer"]:
                        Label(popup, text="New Password:").pack()
                        new_pass = Entry(popup, show="•")
                        new_pass.pack()
                        
                        Button(popup, text="Reset", 
                              command=lambda: self.reset_password(username, new_pass.get(), popup)).pack()
                    else:
                        messagebox.showerror("Error", "Incorrect answer")
                
                Button(popup, text="Submit Answer", command=check_answer).pack()
            else:
                messagebox.showerror("Error", "User not found")
        
        Button(popup, text="Verify", command=verify_user).pack()
    
    def reset_password(self, username, new_password, popup):
        if len(new_password) < 8:
            messagebox.showerror("Error", "Password must be 8+ characters")
            return
        
        self.users[username]["password"] = self.hash_password(new_password)
        self.save_data()
        messagebox.showinfo("Success", "Password updated")
        popup.destroy()

    def show_registration(self):
        popup = Toplevel(self.root)
        popup.title("Register New Account")
        
        fields = [
            ("Username:", "username"),
            ("Password:", "password"),
            ("Full Name:", "name"),
            ("Role:", "role"),
            ("Security Question:", "question"),
            ("Answer:", "answer")
        ]
        
        entries = {}
        for i, (label, name) in enumerate(fields):
            Label(popup, text=label).grid(row=i, column=0, sticky=E, pady=2)
            if name == "role":
                role_var = StringVar()
                OptionMenu(popup, role_var, *["patient", "nurse", "doctor"]).grid(row=i, column=1)
                entries[name] = role_var
            elif name == "question":
                q_var = StringVar()
                OptionMenu(popup, q_var, *self.security_questions).grid(row=i, column=1)
                entries[name] = q_var
            else:
                entry = Entry(popup, show="•" if "password" in name else None)
                entry.grid(row=i, column=1, pady=2)
                entries[name] = entry
        
        def submit():
            username = entries["username"].get()
            if username in self.users:
                messagebox.showerror("Error", "Username exists")
                return
            
            self.users[username] = {
                "password": self.hash_password(entries["password"].get()),
                "role": entries["role"].get(),
                "name": entries["name"].get(),
                "security_question": entries["question"].get(),
                "security_answer": self.hash_password(entries["answer"].get())
            }
            
            if entries["role"].get() == "patient":
                patient_id = f"p{len(self.patients)+1}"
                self.patients[patient_id] = {
                "name": entries["name"].get(),
                "username": username,
                "dob": "",
                "blood_type": "",
                "allergies": []
            }
            
            self.save_data()
            messagebox.showinfo("Success", "Registration complete")
            popup.destroy()
        
        Button(popup, text="Register", command=submit).grid(row=len(fields), columnspan=2)
    
    def manage_users(self):
        self.clear_window()
        
        header = Frame(self.root, bg="#4682b4")
        header.pack(fill=X)
        Label(header, text="User Management", font=("Arial", 16), 
             bg="#4682b4", fg="white").pack(pady=10)
        
        tree = ttk.Treeview(self.root, columns=("Username", "Role", "Name"), show="headings")
        tree.heading("Username", text="Username")
        tree.heading("Role", text="Role")
        tree.heading("Name", text="Name")
        
        for username, data in self.users.items():
            tree.insert("", "end", values=(username, data["role"], data["name"]))
        tree.pack(fill=BOTH, expand=True, padx=20, pady=10)
        
        btn_frame = Frame(self.root, bg="#f0f8ff")
        btn_frame.pack(pady=10)
        
        Button(btn_frame, text="Delete User", command=lambda: self.delete_user(tree),
              bg="#ff6b6b", fg="white").pack(side=LEFT, padx=5)
        
        Button(btn_frame, text="Back", command=self.show_dashboard,
              bg="#4682b4", fg="white").pack(side=LEFT, padx=5)
        
    def delete_user(self, tree):
        selected = tree.selection()
        if not selected:
            messagebox.showerror("Error", "No user selected")
            return
            
        username = tree.item(selected[0])["values"][0]
        if username == self.current_user:
            messagebox.showerror("Error", "Cannot delete yourself")
            return
            
        if messagebox.askyesno("Confirm", f"Delete user {username}?"):
            del self.users[username]
            self.save_data()
            tree.delete(selected[0])
            
    def manage_patients(self):
        self.clear_window()
        
        tk.Label(self.root, text="Patient Management", font=("Arial", 16), 
                bg="#f0f8ff").pack(pady=10)
        
        tree = ttk.Treeview(self.root, columns=("ID", "Name", "DOB", "Blood Type"), show="headings")
        tree.heading("ID", text="Patient ID")
        tree.heading("Name", text="Name")
        tree.heading("DOB", text="Date of Birth")
        tree.heading("Blood Type", text="Blood Type")
        
        for patient_id, data in self.patients.items():
            tree.insert("", "end", values=(patient_id, data["name"], data["dob"], data["blood_type"]))
        
        tree.pack(fill="both", expand=True, padx=20, pady=10)
        
        tk.Button(self.root, text="Back", command=self.show_dashboard, 
                 bg=self.secondary_color, fg="white", font=self.button_font).pack(pady=10)

    def show_dashboard(self):
        self.clear_window()
        role = self.users[self.current_user]["role"]
        
        header = Frame(self.root, bg="#4682b4")
        header.pack(fill=X, pady=(0,20))
        Label(header, text=f"Welcome, {self.users[self.current_user]['name']}", 
             font=("Arial", 16), bg="#4682b4", fg="white").pack(pady=10)
        
        button_frame = Frame(self.root, bg="#f0f8ff")
        button_frame.pack(pady=20)
        
        common_buttons = [
            ("View Appointments", self.view_appointments, "#5f9ea0"),
            ("Logout", self.setup_login_screen, "#ff7f50")
        ]
        
        role_buttons = {
            "admin": [("Manage Users", self.manage_users, "#4682b4")],
            "doctor": [("My Patients", self.view_my_patients, "#4682b4")],
            "patient": [("Book Appointment", self.book_appointment, "#4682b4")]
        }
        
        for text, cmd, color in common_buttons + role_buttons.get(role, []):
            Button(button_frame, text=text, command=cmd,
                 bg=color, fg="white", font=("Arial", 12), 
                 width=20).pack(pady=5)
    
    def view_appointments(self):
        self.clear_window()
    
        header = Frame(self.root, bg=self.primary_color)
        header.pack(fill=X, pady=(0,20))
        Label(header, text="Your Appointments", font=self.title_font, 
             bg=self.primary_color, fg="white").pack(pady=10)
    
        columns = ("ID", "Patient", "Doctor", "Date", "Time", "Status", "Reason")
        tree = ttk.Treeview(self.root, columns=columns, show="headings", selectmode="browse")
    
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=100, anchor="center")
        tree.column("Reason", width=200)  
    
        for appt in self.appointments:
            if (self.users[self.current_user]['role'] != 'admin' and 
                self.patients.get(appt['patient_id'], {}).get('username') != self.current_user):
                continue
            
            patient_name = self.patients.get(appt['patient_id'], {}).get('name', 'Unknown')
            doctor_name = self.users.get(appt['doctor'], {}).get('name', 'Unknown')
        
            tree.insert("", "end", values=(
                appt['id'],
                patient_name,
                doctor_name,
                appt['date'],
                appt.get('time', ''),
                appt.get('status', 'Scheduled'),
                appt.get('reason', '')
            ))
    
        tree.pack(fill=BOTH, expand=True, padx=20, pady=10)
    
        btn_frame = Frame(self.root, bg="#f0f8ff")
        btn_frame.pack(pady=10)
    
        Button(btn_frame, text="Back", command=self.show_dashboard,
              bg=self.secondary_color, fg="white", font=self.button_font).pack(side=LEFT, padx=10)
    
        if self.users[self.current_user]['role'] in ['patient', 'nurse', 'doctor']:
            Button(btn_frame, text="Cancel Appointment", 
                  command=lambda: self.cancel_appointment(tree),
                  bg=self.danger_color, fg="white", font=self.button_font).pack(side=LEFT, padx=10)
    
    def book_appointment(self):
        self.clear_window()
        
        header = Frame(self.root, bg=self.primary_color)
        header.pack(fill=X, pady=(0,20))
        Label(header, text="Book Appointment", font=self.title_font, 
             bg=self.primary_color, fg="white").pack(pady=10)
        
        form_frame = Frame(self.root, bg="#f0f8ff")
        form_frame.pack(pady=20)
        
        doctors = [un for un, data in self.users.items() if data["role"] == "doctor"]
        if not doctors:
            messagebox.showerror("Error", "No doctors available")
            self.show_dashboard()
            return
            
        Label(form_frame, text="Doctor:", bg="#f0f8ff", font=self.text_font).grid(row=0, column=0, sticky=E, pady=5)
        self.doctor_var = StringVar(value=doctors[0])  
        OptionMenu(form_frame, self.doctor_var, *doctors).grid(row=0, column=1, pady=5)
        
        fields = [
            ("Date (YYYY-MM-DD):", "date"),
            ("Time (HH:MM):", "time"), 
            ("Reason:", "reason")
        ]
        
        self.booking_entries = {}
        for i, (label, name) in enumerate(fields, start=1):
            Label(form_frame, text=label, bg="#f0f8ff", font=self.text_font).grid(row=i, column=0, sticky=E, pady=5)
            entry = Entry(form_frame, font=self.text_font)
            entry.grid(row=i, column=1, pady=5)
            self.booking_entries[name] = entry
        
        button_frame = Frame(self.root, bg="#f0f8ff")
        button_frame.pack(pady=20)
        
        Button(button_frame, text="Submit", command=self.submit_appointment,
              bg=self.primary_color, fg="white", font=self.button_font).pack(side=LEFT, padx=10)
        
        Button(button_frame, text="Back", command=self.show_dashboard,
              bg=self.secondary_color, fg="white", font=self.button_font).pack(side=LEFT, padx=10)


    def submit_appointment(self):
        try:
            patient_id = next(pid for pid, p in self.patients.items() 
                            if p.get("username") == self.current_user)
            
            new_appt = {
                "id": f"apt{len(self.appointments)+1}",
                "patient_id": patient_id,
                "doctor": self.doctor_var.get(),  
                "date": self.booking_entries['date'].get(),
                "time": self.booking_entries['time'].get(),
                "reason": self.booking_entries['reason'].get(),
                "status": "Scheduled"
            }
            
            if not all([new_appt['date'], new_appt['time'], new_appt['reason']]):
                raise ValueError("All fields are required")
                
            self.appointments.append(new_appt)
            self.save_data()
            messagebox.showinfo("Success", "Appointment booked!")
            self.show_dashboard()
            
        except StopIteration:
            messagebox.showerror("Error", "Patient record not found")
        except Exception as e:
            messagebox.showerror("Error", f"Booking failed: {str(e)}")

    def cancel_appointment(self, tree):
        selected = tree.selection()
        if not selected:
            messagebox.showerror("Error", "Please select an appointment first")
            return

        appt_id = tree.item(selected[0])['values'][0]
        appt_status = tree.item(selected[0])['values'][5]  

        if appt_status in ["Cancelled", "Completed"]:
            messagebox.showerror("Error", f"Cannot cancel {appt_status.lower()} appointment")
            return

        if not messagebox.askyesno("Confirm", f"Cancel appointment {appt_id}?"):
            return

        for i, appt in enumerate(self.appointments):
            if appt['id'] == appt_id:
                self.appointments[i]['status'] = "Cancelled"
                self.save_data()
                messagebox.showinfo("Success", "Appointment cancelled")
                self.view_appointments()  
                return

        messagebox.showerror("Error", "Appointment not found in records")
    
    def view_my_patients(self):
        self.clear_window()
        
        tk.Label(self.root, text="My Patients", font=("Arial", 16), 
                bg="#f0f8ff").pack(pady=10)
        
        my_appointments = [a for a in self.appointments if a["doctor"] == self.current_user]
        patient_ids = list(set(a["patient_id"] for a in my_appointments))
        
        if not patient_ids:
            tk.Label(self.root, text="No patients found", bg="#f0f8ff").pack()
            tk.Button(self.root, text="Back", command=self.show_dashboard, 
                     bg=self.secondary_color, fg="white", font=self.button_font).pack(pady=20)
            return
        
        canvas = tk.Canvas(self.root, bg="#f0f8ff")
        scrollbar = ttk.Scrollbar(self.root, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg="#f0f8ff")
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(
                scrollregion=canvas.bbox("all")
            )
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        for i, pid in enumerate(patient_ids):
            patient = self.patients.get(pid, {})
            
            card = tk.Frame(scrollable_frame, bg="white", bd=2, relief="groove", padx=10, pady=10)
            card.grid(row=i, column=0, sticky="ew", padx=20, pady=10)
            
            tk.Label(card, text=patient.get("name", "Unknown"), 
                    font=("Arial", 12, "bold"), bg="white").grid(row=0, column=0, sticky="w")
            
            tk.Label(card, text=f"DOB: {patient.get('dob', '')}", 
                    bg="white").grid(row=1, column=0, sticky="w")
            
            tk.Label(card, text=f"Blood Type: {patient.get('blood_type', '')}", 
                    bg="white").grid(row=2, column=0, sticky="w")
            
            tk.Button(card, text="View Details", 
                     command=lambda p=pid: self.view_patient_details(p),
                     bg=self.secondary_color, fg="white", font=("Arial", 10)).grid(row=3, column=0, pady=5)
        
        tk.Button(scrollable_frame, text="Back", command=self.show_dashboard, 
                 bg=self.secondary_color, fg="white", font=self.button_font).grid(row=len(patient_ids)+1, column=0, pady=20)
    
    def view_patient_details(self, patient_id):
        popup = tk.Toplevel(self.root)
        popup.title("Patient Details")
        popup.geometry("500x400")
        popup.configure(bg="#f0f8ff")
        
        patient = self.patients.get(patient_id, {})
        
        tk.Label(popup, text=patient.get("name", "Unknown"), 
                font=("Arial", 14, "bold"), bg="#f0f8ff").pack(pady=10)
        
        details_frame = tk.Frame(popup, bg="#f0f8ff")
        details_frame.pack(pady=10)
        
        tk.Label(details_frame, text="Patient ID:", bg="#f0f8ff").grid(row=0, column=0, sticky="e", padx=5, pady=5)
        tk.Label(details_frame, text=patient_id, bg="#f0f8ff").grid(row=0, column=1, sticky="w", pady=5)
        
        tk.Label(details_frame, text="Date of Birth:", bg="#f0f8ff").grid(row=1, column=0, sticky="e", padx=5, pady=5)
        tk.Label(details_frame, text=patient.get("dob", ""), bg="#f0f8ff").grid(row=1, column=1, sticky="w", pady=5)
        
        tk.Label(details_frame, text="Blood Type:", bg="#f0f8ff").grid(row=2, column=0, sticky="e", padx=5, pady=5)
        tk.Label(details_frame, text=patient.get("blood_type", ""), bg="#f0f8ff").grid(row=2, column=1, sticky="w", pady=5)

        tk.Label(details_frame, text="Phone:", bg="#f0f8ff").grid(row=3, column=0, sticky="e", padx=5, pady=5)
        tk.Label(details_frame, text=patient.get("phone", ""), bg="#f0f8ff").grid(row=3, column=1, sticky="w", pady=5)
        
        tk.Label(popup, text="Medical History", font=("Arial", 12, "bold"), 
                bg="#f0f8ff").pack(pady=(20,5))
        
        history_frame = tk.Frame(popup, bg="#f0f8ff")
        history_frame.pack(fill="x", padx=20)
        
        history_items = [
            ("Allergies:", patient.get("allergies", "None recorded")),
            ("Conditions:", patient.get("conditions", "None recorded")),
            ("Last Visit:", patient.get("last_visit", "Never")),
            ("Medications:", patient.get("medications", "None"))
        ]
        
        for i, (label, value) in enumerate(history_items):
            tk.Label(history_frame, text=label, bg="#f0f8ff").grid(row=i, column=0, sticky="e", padx=5, pady=2)
            tk.Label(history_frame, text=value, bg="#f0f8ff").grid(row=i, column=1, sticky="w", pady=2)
        
        if self.users[self.current_user]["role"] == "doctor":
            tk.Button(popup, text="Add Prescription", 
                     command=lambda: self.add_prescription(patient_id),
                     bg=self.primary_color, fg="white", font=self.button_font).pack(pady=20)
    
    def add_prescription(self, patient_id):
        popup = tk.Toplevel(self.root)
        popup.title("Add Prescription")
        popup.geometry("400x400")
        popup.configure(bg="#f0f8ff")
        
        tk.Label(popup, text="New Prescription", font=("Arial", 14), 
                bg="#f0f8ff").pack(pady=10)
        
        form_frame = tk.Frame(popup, bg="#f0f8ff")
        form_frame.pack(pady=10)
        
        fields = [
            ("Medication:", "entry_med"),
            ("Dosage:", "entry_dose"),
            ("Instructions:", "entry_inst"),
            ("Duration:", "entry_dur")
        ]
        
        entries = {}
        for i, (label, name) in enumerate(fields):
            tk.Label(form_frame, text=label, bg="#f0f8ff").grid(row=i, column=0, sticky="e", padx=5, pady=5)
            entry = tk.Entry(form_frame, width=25)
            entry.grid(row=i, column=1, pady=5)
            entries[name] = entry
        
        def submit():
            messagebox.showinfo("Success", "Prescription added successfully!")
            popup.destroy()
        
        button_frame = tk.Frame(popup, bg="#f0f8ff")
        button_frame.pack(pady=20)
        
        tk.Button(button_frame, text="Submit", command=submit, 
                 bg=self.primary_color, fg="white", font=self.button_font).pack(side="left", padx=10)
        
        tk.Button(button_frame, text="Cancel", command=popup.destroy, 
                 bg=self.secondary_color, fg="white", font=self.button_font).pack(side="left", padx=10)
        self.save_data()
    
    def view_my_records(self):
        self.clear_window()

        patient_id = None
        patient_data = None
        
        for pid, data in self.patients.items():
            if data.get("name") == self.users[self.current_user].get("name"):
                patient_id = pid
                patient_data = data
                break
        
        if not patient_id:
            tk.Label(self.root, text="No patient record found", bg="#f0f8ff").pack()
            tk.Button(self.root, text="Back", command=self.show_dashboard, 
                     bg=self.secondary_color, fg="white", font=self.button_font).pack(pady=20)
            return
        
        tk.Label(self.root, text="My Medical Records", font=("Arial", 16), 
                bg="#f0f8ff").pack(pady=10)
        
        info_frame = tk.LabelFrame(self.root, text="Personal Information", 
                                 bg="#f0f8ff", padx=10, pady=10)
        info_frame.pack(fill="x", padx=20, pady=10)
        
        info_items = [
            ("Patient ID:", patient_id),
            ("Name:", patient_data.get("name", "")),
            ("Date of Birth:", patient_data.get("dob", "")),
            ("Blood Type:", patient_data.get("blood_type", "")),
            ("Phone:", patient_data.get("phone", ""))
        ]
        
        for i, (label, value) in enumerate(info_items):
            tk.Label(info_frame, text=label, bg="#f0f8ff").grid(row=i, column=0, sticky="e", padx=5, pady=2)
            tk.Label(info_frame, text=value, bg="#f0f8ff").grid(row=i, column=1, sticky="w", pady=2)
        
        history_frame = tk.LabelFrame(self.root, text="Medical History", 
                                    bg="#f0f8ff", padx=10, pady=10)
        history_frame.pack(fill="x", padx=20, pady=10)
        
        history_items = [
            ("Allergies:", patient_data.get("allergies", "None recorded")),
            ("Conditions:", patient_data.get("conditions", "None recorded")),
            ("Last Visit:", patient_data.get("last_visit", "Never")),
            ("Current Medications:", patient_data.get("medications", "None"))
        ]
        
        for i, (label, value) in enumerate(history_items):
            tk.Label(history_frame, text=label, bg="#f0f8ff").grid(row=i, column=0, sticky="e", padx=5, pady=2)
            tk.Label(history_frame, text=value, bg="#f0f8ff").grid(row=i, column=1, sticky="w", pady=2)
        
        appt_frame = tk.LabelFrame(self.root, text="My Appointments", 
                                  bg="#f0f8ff", padx=10, pady=10)
        appt_frame.pack(fill="x", padx=20, pady=10)
        
        patient_appointments = [a for a in self.appointments if a["patient_id"] == patient_id]
        
        if patient_appointments:
            for i, appt in enumerate(patient_appointments):
                tk.Label(appt_frame, 
                        text=f"{appt['date']} at {appt.get('time', '')} with Dr. {self.users[appt['doctor']].get('name', '')}",
                        bg="#f0f8ff").grid(row=i, column=0, sticky="w", pady=2)
                tk.Label(appt_frame, text=f"Reason: {appt['reason']}", 
                        bg="#f0f8ff").grid(row=i, column=1, sticky="w", pady=2)
        else:
            tk.Label(appt_frame, text="No upcoming appointments", bg="#f0f8ff").grid(row=0, column=0)
        
        tk.Button(self.root, text="Back", command=self.show_dashboard, 
                 bg=self.secondary_color, fg="white", font=self.button_font).pack(pady=20)
    
    def clear_window(self):
        for widget in self.root.winfo_children():
            widget.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    
    style = ttk.Style()
    style.theme_use("clam")
    
    style.configure("TFrame", background="#f0f8ff")
    style.configure("TLabel", background="#f0f8ff")
    style.configure("TButton", font=("Arial", 10), padding=5)
    style.map("TButton",
             foreground=[('active', 'white'), ('!active', 'white')],
             background=[('active', '#3a6ea5'), ('!active', '#4682b4')])
    
    app = MedicalSystem(root)
    root.mainloop()
