import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime

class BloodDonorSystem:
    def __init__(self, root):
        self.root = root
        self.root.title("Smart Blood Donor Eligibility System")
        self.root.geometry("600x700")
        
        self.create_widgets()
    
    def create_widgets(self):
        """Create all the GUI widgets"""
      
        main_frame = tk.Frame(self.root, padx=20, pady=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        tk.Label(main_frame, text="Smart Blood Donor Eligibility", font=('Arial', 18, 'bold')).pack()
        tk.Label(main_frame, text="Complete the form to check eligibility").pack(pady=5)
        
        
        form_frame = ttk.LabelFrame(main_frame, text="Donor Information", padding=10)
        form_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
       
        self.name_var = tk.StringVar()
        self.age_var = tk.StringVar()
        self.gender_var = tk.StringVar(value="Male")
        self.blood_type_var = tk.StringVar()
        self.weight_var = tk.StringVar()
        self.last_donation_var = tk.StringVar()
        self.medical_var = tk.StringVar()
        self.medications_var = tk.StringVar()
        self.recent_surgery_var = tk.BooleanVar()
        self.recent_tattoo_var = tk.BooleanVar()
        self.pregnancy_var = tk.BooleanVar()
        self.travel_var = tk.BooleanVar()
        
       
        self.create_form_row(form_frame, "Full Name:", self.name_var, 0)
        self.create_form_row(form_frame, "Age:", self.age_var, 1)
        
        tk.Label(form_frame, text="Gender:").grid(row=2, column=0, sticky='w', pady=5)
        gender_frame = tk.Frame(form_frame)
        gender_frame.grid(row=2, column=1, sticky='w')
        tk.Radiobutton(gender_frame, text="Male", variable=self.gender_var, value="Male").pack(side='left')
        tk.Radiobutton(gender_frame, text="Female", variable=self.gender_var, value="Female").pack(side='left', padx=10)
        
       
        tk.Label(form_frame, text="Blood Type:").grid(row=3, column=0, sticky='w', pady=5)
        ttk.Combobox(form_frame, textvariable=self.blood_type_var, 
                    values=["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"], 
                    state="readonly").grid(row=3, column=1, sticky='w')
        
        self.create_form_row(form_frame, "Weight (kg):", self.weight_var, 4)
        self.create_form_row(form_frame, "Last Donation (YYYY-MM-DD):", self.last_donation_var, 5)
        self.create_form_row(form_frame, "Medical Conditions:", self.medical_var, 6)
        self.create_form_row(form_frame, "Medications:", self.medications_var, 7)
        
      
        risk_frame = ttk.LabelFrame(form_frame, text="Risk Factors", padding=10)
        risk_frame.grid(row=8, column=0, columnspan=2, sticky='ew', pady=10)
        tk.Checkbutton(risk_frame, text="Recent Surgery (6 months)", variable=self.recent_surgery_var).pack(anchor='w')
        tk.Checkbutton(risk_frame, text="Recent Tattoo/Piercing (12 months)", variable=self.recent_tattoo_var).pack(anchor='w')
        tk.Checkbutton(risk_frame, text="Pregnancy/Recent Childbirth", variable=self.pregnancy_var).pack(anchor='w')
        tk.Checkbutton(risk_frame, text="Travel to Disease Area", variable=self.travel_var).pack(anchor='w')
        
    
        button_frame = tk.Frame(main_frame)
        button_frame.pack(fill='x', pady=10)
        tk.Button(button_frame, text="Check Eligibility", command=self.check_eligibility, bg='green', fg='white').pack(side='left', padx=5)
        tk.Button(button_frame, text="Clear Form", command=self.clear_form, bg='gray', fg='white').pack(side='left', padx=5)
        
 
        self.results_frame = tk.Frame(main_frame)
        self.results_frame.pack(fill='both', expand=True)
        self.results_label = tk.Label(self.results_frame, text="Results will appear here", font=('Arial', 12))
        self.results_label.pack(pady=20)
        
     
        self.status_bar = tk.Label(self.root, text="Ready", bd=1, relief='sunken', anchor='w')
        self.status_bar.pack(side='bottom', fill='x')
    
    def create_form_row(self, frame, label_text, variable, row):
        """Helper to create a form row"""
        tk.Label(frame, text=label_text).grid(row=row, column=0, sticky='w', pady=5)
        tk.Entry(frame, textvariable=variable).grid(row=row, column=1, sticky='ew', pady=5)
    
    def check_eligibility(self):
        """Check if donor is eligible"""
        try:
            
            name = self.name_var.get().strip()
            age = self.validate_number(self.age_var.get(), "Age", min_val=18, max_val=65)
            weight = self.validate_number(self.weight_var.get(), "Weight", min_val=50)
            last_donation = self.validate_date(self.last_donation_var.get())
            
            if not name:
                messagebox.showwarning("Warning", "Please enter your name")
                return
            if age is None or weight is None:
                return
            
           
            is_eligible = True
            reasons = []
            
           
            if age < 18:
                is_eligible = False
                reasons.append("Under 18 years old")
            elif age > 65:
                is_eligible = False
                reasons.append("Over 65 years old")
                
            if weight < 50:
                is_eligible = False
                reasons.append("Weight under 50kg")
                
            
            if last_donation:
                days_since = (datetime.now() - last_donation).days
                if days_since < 56:
                    is_eligible = False
                    reasons.append(f"Only {days_since} days since last donation")
            
        
            if self.recent_surgery_var.get():
                is_eligible = False
                reasons.append("Recent surgery")
            if self.recent_tattoo_var.get():
                is_eligible = False
                reasons.append("Recent tattoo/piercing")
            if self.pregnancy_var.get():
                is_eligible = False
                reasons.append("Pregnancy/recent childbirth")
            if self.travel_var.get():
                is_eligible = False
                reasons.append("Travel to disease area")
                
            
            high_risk = ["hepatitis", "hiv", "aids", "cancer", "heart disease"]
            for condition in high_risk:
                if condition in self.medical_var.get().lower():
                    is_eligible = False
                    reasons.append(f"Medical condition: {condition}")
            
            self.show_results(is_eligible, reasons)
            
        except Exception as e:
            messagebox.showerror("Error", str(e))
    
    def validate_number(self, value, field, min_val=None, max_val=None):
        """Validate numeric input"""
        try:
            num = float(value) if '.' in value else int(value)
            if min_val is not None and num < min_val:
                messagebox.showwarning("Warning", f"{field} must be at least {min_val}")
                return None
            if max_val is not None and num > max_val:
                messagebox.showwarning("Warning", f"{field} must be at most {max_val}")
                return None
            return num
        except ValueError:
            messagebox.showwarning("Warning", f"Invalid {field}")
            return None
    
    def validate_date(self, date_str):
        """Validate date input"""
        if not date_str:
            return None
        try:
            return datetime.strptime(date_str, "%Y-%m-%d")
        except ValueError:
            messagebox.showwarning("Warning", "Invalid date format (use YYYY-MM-DD)")
            return None
    
    def show_results(self, is_eligible, reasons):
        """Display eligibility results"""
        for widget in self.results_frame.winfo_children():
            widget.destroy()
            
        color = "green" if is_eligible else "red"
        text = "ELIGIBLE" if is_eligible else "NOT ELIGIBLE"
        
        tk.Label(self.results_frame, text=text, font=('Arial', 16, 'bold'), 
                fg=color).pack(pady=10)
        
        if not is_eligible:
            tk.Label(self.results_frame, text="Reasons:").pack()
            for reason in reasons:
                tk.Label(self.results_frame, text=f"- {reason}").pack()
        
        self.status_bar.config(text=f"Last checked: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    
    def clear_form(self):
        """Clear all form fields"""
        for var in [self.name_var, self.age_var, self.blood_type_var, 
                   self.weight_var, self.last_donation_var, 
                   self.medical_var, self.medications_var]:
            var.set("")
            
        for var in [self.recent_surgery_var, self.recent_tattoo_var, 
                   self.pregnancy_var, self.travel_var]:
            var.set(False)
            
        self.gender_var.set("Male")
        
       
        for widget in self.results_frame.winfo_children():
            widget.destroy()
        self.results_label = tk.Label(self.results_frame, text="Results will appear here")
        self.results_label.pack(pady=20)
        
        self.status_bar.config(text="Form cleared")

if __name__ == "__main__":
    root = tk.Tk()
    app = BloodDonorSystem(root)
    root.mainloop()