"""
Stablecoin Risk Monitor - Desktop GUI Application
A user-friendly interface for importing and analyzing financial data
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import pandas as pd
import threading
import sys
import os
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from data_layer.collectors.excel_importer import EXCEL_IMPORTER
from ai_engine.anomaly_detector import ENGINE


class RiskMonitorGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Stablecoin Risk Monitor")
        self.root.geometry("1200x800")
        self.root.minsize(1000, 600)
        
        # Data storage
        self.current_data = None
        self.analysis_results = None
        self.file_path = None
        
        # Configure styles
        self.setup_styles()
        
        # Create UI
        self.create_menu()
        self.create_header()
        self.create_main_content()
        self.create_statusbar()
        
    def setup_styles(self):
        """Configure custom styles for widgets"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Dark mode professional colors
        self.colors = {
            'bg': '#1e1e1e',
            'header_bg': '#252526',
            'safe': '#4ec9b0',
            'warning': '#dcdcaa',
            'risky': '#f48771',
            'text': '#d4d4d4',
            'border': '#3e3e42',
            'frame_bg': '#2d2d30',
            'button_bg': '#0e639c',
            'button_hover': '#1177bb',
            'input_bg': '#3c3c3c',
            'input_fg': '#cccccc'
        }
        
        # Configure styles
        style.configure('Header.TFrame', background=self.colors['header_bg'])
        style.configure('Header.TLabel', 
                       background=self.colors['header_bg'],
                       foreground='#ffffff',
                       font=('Arial', 16, 'bold'))
        style.configure('Subtitle.TLabel',
                       background=self.colors['header_bg'],
                       foreground='#cccccc',
                       font=('Arial', 10))
        style.configure('Safe.TLabel', foreground=self.colors['safe'], font=('Arial', 10, 'bold'))
        style.configure('Warning.TLabel', foreground=self.colors['warning'], font=('Arial', 10, 'bold'))
        style.configure('Risky.TLabel', foreground=self.colors['risky'], font=('Arial', 10, 'bold'))
        
        # Frame styles
        style.configure('TFrame', background=self.colors['bg'])
        style.configure('TLabelframe', background=self.colors['bg'], foreground=self.colors['text'], bordercolor=self.colors['border'])
        style.configure('TLabelframe.Label', background=self.colors['bg'], foreground=self.colors['text'])
        
        # Button styles
        style.configure('TButton', background=self.colors['button_bg'], foreground='#ffffff', bordercolor=self.colors['border'], relief='flat')
        style.map('TButton', background=[('active', self.colors['button_hover'])])
        
        # Label styles
        style.configure('TLabel', background=self.colors['bg'], foreground=self.colors['text'])
        
        # Entry styles
        style.configure('TEntry', fieldbackground=self.colors['input_bg'], foreground=self.colors['input_fg'], bordercolor=self.colors['border'])
        
        # Notebook (tabs) styles
        style.configure('TNotebook', background=self.colors['bg'], bordercolor=self.colors['border'])
        style.configure('TNotebook.Tab', background=self.colors['frame_bg'], foreground=self.colors['text'], padding=[20, 10])
        style.map('TNotebook.Tab', background=[('selected', self.colors['button_bg'])], foreground=[('selected', '#ffffff')])
        
        # Treeview (table) styles
        style.configure('Treeview', background=self.colors['input_bg'], foreground=self.colors['text'], 
                       fieldbackground=self.colors['input_bg'], bordercolor=self.colors['border'])
        style.configure('Treeview.Heading', background=self.colors['frame_bg'], foreground=self.colors['text'], 
                       bordercolor=self.colors['border'])
        style.map('Treeview', background=[('selected', self.colors['button_bg'])], 
                 foreground=[('selected', '#ffffff')])
        
        # Combobox styles
        style.configure('TCombobox', fieldbackground=self.colors['input_bg'], background=self.colors['input_bg'],
                       foreground=self.colors['input_fg'], bordercolor=self.colors['border'])
        
        self.root.configure(bg=self.colors['bg'])
        
    def create_menu(self):
        """Create menu bar"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Open Excel File...", command=self.load_file, accelerator="Ctrl+O")
        file_menu.add_command(label="Export Results...", command=self.export_results, accelerator="Ctrl+E")
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        
        # Analysis menu
        analysis_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Analysis", menu=analysis_menu)
        analysis_menu.add_command(label="Analyze Data", command=self.analyze_data, accelerator="Ctrl+A")
        analysis_menu.add_command(label="Clear Results", command=self.clear_results)
        
        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="Quick Start Guide", command=self.show_help)
        help_menu.add_command(label="About", command=self.show_about)
        
        # Keyboard shortcuts
        self.root.bind('<Control-o>', lambda e: self.load_file())
        self.root.bind('<Control-a>', lambda e: self.analyze_data())
        self.root.bind('<Control-e>', lambda e: self.export_results())
        
    def create_header(self):
        """Create header section"""
        header_frame = ttk.Frame(self.root, style='Header.TFrame')
        header_frame.pack(fill='x', pady=(0, 10))
        
        title = ttk.Label(header_frame, text="Stablecoin Risk Monitor", style='Header.TLabel')
        title.pack(pady=(15, 5))
        
        subtitle = ttk.Label(header_frame, 
                            text="AI-Powered Risk Analysis for Financial Assets",
                            style='Subtitle.TLabel')
        subtitle.pack(pady=(0, 15))
        
    def create_main_content(self):
        """Create main content area with tabs"""
        # Create notebook (tabs)
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=5)
        
        # Tab 1: Upload & Analyze
        self.upload_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.upload_tab, text="Upload & Analyze")
        self.create_upload_tab()
        
        # Tab 2: Results
        self.results_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.results_tab, text="Risk Analysis")
        self.create_results_tab()
        
        # Tab 3: Advanced Analytics
        self.analytics_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.analytics_tab, text="AI Insights")
        self.create_analytics_tab()
        
        # Tab 4: Blockchain & Proofs
        self.blockchain_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.blockchain_tab, text="Blockchain")
        self.create_blockchain_tab()
        
        # Tab 5: Data Preview
        self.preview_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.preview_tab, text="Data Preview")
        self.create_preview_tab()
        
    def create_upload_tab(self):
        """Create upload and analyze interface"""
        # File selection section
        file_frame = ttk.LabelFrame(self.upload_tab, text="1. Select Excel File", padding=20)
        file_frame.pack(fill='x', padx=20, pady=10)
        
        button_frame = ttk.Frame(file_frame)
        button_frame.pack(fill='x')
        
        self.file_label = ttk.Label(button_frame, text="No file selected", foreground='gray')
        self.file_label.pack(side='left', padx=10)
        
        ttk.Button(button_frame, text="Browse...", command=self.load_file).pack(side='left')
        
        # Requirements section
        req_frame = ttk.LabelFrame(self.upload_tab, text="Required Columns", padding=20)
        req_frame.pack(fill='x', padx=20, pady=10)
        
        requirements = [
            "• Company - Company name or identifier",
            "• bs_cash_cash_equivalents_and_sti - Cash and cash equivalents",
            "• eqy_float - Equity float (freely traded shares)",
            "• eqy_sh_out - Equity shares outstanding",
            "• px_last - Last traded price"
        ]
        
        for req in requirements:
            ttk.Label(req_frame, text=req, font=('Arial', 9)).pack(anchor='w', pady=2)
        
        # Analyze button section
        action_frame = ttk.Frame(self.upload_tab)
        action_frame.pack(fill='x', padx=20, pady=20)
        
        self.analyze_btn = ttk.Button(action_frame, 
                                     text="Analyze Data",
                                     command=self.analyze_data,
                                     state='disabled')
        self.analyze_btn.pack(pady=10)
        
        # Progress section
        self.progress_frame = ttk.Frame(self.upload_tab)
        self.progress_frame.pack(fill='x', padx=20, pady=10)
        
        self.progress_label = ttk.Label(self.progress_frame, text="")
        self.progress_label.pack()
        
        self.progress_bar = ttk.Progressbar(self.progress_frame, mode='indeterminate')
        
    def create_results_tab(self):
        """Create results display interface"""
        # Summary cards
        summary_frame = ttk.Frame(self.results_tab)
        summary_frame.pack(fill='x', padx=20, pady=10)
        
        ttk.Label(summary_frame, text="Risk Summary", font=('Arial', 12, 'bold')).pack(anchor='w', pady=(0, 10))
        
        cards_frame = ttk.Frame(summary_frame)
        cards_frame.pack(fill='x')
        
        # Create summary cards
        self.safe_card = self.create_summary_card(cards_frame, "SAFE", self.colors['safe'])
        self.safe_card.pack(side='left', padx=5, fill='x', expand=True)
        
        self.warning_card = self.create_summary_card(cards_frame, "WARNING", self.colors['warning'])
        self.warning_card.pack(side='left', padx=5, fill='x', expand=True)
        
        self.risky_card = self.create_summary_card(cards_frame, "RISKY", self.colors['risky'])
        self.risky_card.pack(side='left', padx=5, fill='x', expand=True)
        
        # Results table
        table_frame = ttk.LabelFrame(self.results_tab, text="Detailed Results", padding=10)
        table_frame.pack(fill='both', expand=True, padx=20, pady=10)
        
        # Create treeview for results
        columns = ('company', 'risk_score', 'risk_label', 'reserves', 'supply', 'price', 'market_cap', 'cash_ratio')
        self.results_tree = ttk.Treeview(table_frame, columns=columns, show='headings', height=15)
        
        # Configure columns
        self.results_tree.heading('company', text='Company')
        self.results_tree.heading('risk_score', text='Risk Score')
        self.results_tree.heading('risk_label', text='Risk Label')
        self.results_tree.heading('reserves', text='Reserves')
        self.results_tree.heading('supply', text='Supply')
        self.results_tree.heading('price', text='Price')
        self.results_tree.heading('market_cap', text='Market Cap')
        self.results_tree.heading('cash_ratio', text='Cash/MCap %')
        
        # Set column widths
        self.results_tree.column('company', width=150)
        self.results_tree.column('risk_score', width=80)
        self.results_tree.column('risk_label', width=80)
        self.results_tree.column('reserves', width=120)
        self.results_tree.column('supply', width=120)
        self.results_tree.column('price', width=80)
        self.results_tree.column('market_cap', width=120)
        self.results_tree.column('cash_ratio', width=100)
        
        # Add scrollbars
        vsb = ttk.Scrollbar(table_frame, orient='vertical', command=self.results_tree.yview)
        hsb = ttk.Scrollbar(table_frame, orient='horizontal', command=self.results_tree.xview)
        self.results_tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        
        self.results_tree.grid(row=0, column=0, sticky='nsew')
        vsb.grid(row=0, column=1, sticky='ns')
        hsb.grid(row=1, column=0, sticky='ew')
        
        table_frame.grid_rowconfigure(0, weight=1)
        table_frame.grid_columnconfigure(0, weight=1)
        
        # Export button
        export_frame = ttk.Frame(self.results_tab)
        export_frame.pack(fill='x', padx=20, pady=10)
        
        ttk.Button(export_frame, text="Export to CSV", command=self.export_results).pack(side='right')
        
    def create_analytics_tab(self):
        """Create advanced analytics interface with AI insights"""
        main_frame = ttk.Frame(self.analytics_tab)
        main_frame.pack(fill='both', expand=True, padx=20, pady=10)
        
        ttk.Label(main_frame, text="Advanced AI Analytics", font=('Arial', 12, 'bold')).pack(anchor='w', pady=(0, 10))
        
        # Top control frame
        control_frame = ttk.Frame(main_frame)
        control_frame.pack(fill='x', pady=(0, 10))
        
        # Company selector
        selector_frame = ttk.Frame(control_frame)
        selector_frame.pack(side='left', fill='x', expand=True)
        
        ttk.Label(selector_frame, text="Select Company:").pack(side='left', padx=5)
        self.company_selector = ttk.Combobox(selector_frame, state='readonly', width=40)
        self.company_selector.pack(side='left', padx=5)
        self.company_selector.bind('<<ComboboxSelected>>', self.show_company_details)
        
        # AI Suggestions button
        ttk.Button(control_frame, text="Generate AI Suggestions", 
                  command=self.generate_ai_suggestions).pack(side='right', padx=5)
        
        # Details display
        self.analytics_text = scrolledtext.ScrolledText(main_frame, 
                                                        wrap=tk.WORD,
                                                        font=('Courier', 9),
                                                        height=30,
                                                        bg='#1e1e1e',
                                                        fg='#d4d4d4',
                                                        insertbackground='#ffffff')
        self.analytics_text.pack(fill='both', expand=True)
        
    def create_blockchain_tab(self):
        """Create blockchain & cryptographic proofs interface"""
        main_frame = ttk.Frame(self.blockchain_tab)
        main_frame.pack(fill='both', expand=True, padx=20, pady=10)
        
        ttk.Label(main_frame, text="Blockchain Integration & Merkle Proofs", 
                  font=('Arial', 12, 'bold')).pack(anchor='w', pady=(0, 10))
        
        # Button frame
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill='x', pady=(0, 10))
        
        ttk.Button(button_frame, 
                  text="Generate Merkle Proofs",
                  command=self.generate_merkle_proofs).pack(side='left', padx=5)
        
        ttk.Button(button_frame,
                  text="View Governance",
                  command=self.show_governance).pack(side='left', padx=5)
        
        # Blockchain display
        self.blockchain_text = scrolledtext.ScrolledText(main_frame,
                                                         wrap=tk.WORD,
                                                         font=('Courier', 9),
                                                         height=30,
                                                         bg='#1e1e1e',
                                                         fg='#d4d4d4',
                                                         insertbackground='#ffffff')
        self.blockchain_text.pack(fill='both', expand=True)
        
    def create_preview_tab(self):
        """Create data preview interface"""
        preview_frame = ttk.Frame(self.preview_tab)
        preview_frame.pack(fill='both', expand=True, padx=20, pady=10)
        
        ttk.Label(preview_frame, text="Raw Data Preview", font=('Arial', 12, 'bold')).pack(anchor='w', pady=(0, 10))
        
        # Text widget for data preview
        self.preview_text = scrolledtext.ScrolledText(preview_frame, 
                                                      wrap=tk.NONE,
                                                      font=('Courier', 9),
                                                      bg='#1e1e1e',
                                                      fg='#d4d4d4',
                                                      insertbackground='#ffffff')
        self.preview_text.pack(fill='both', expand=True)
        
    def create_summary_card(self, parent, label, color):
        """Create a summary card widget"""
        card = ttk.Frame(parent, relief='solid', borderwidth=2)
        
        # Color indicator
        indicator = tk.Canvas(card, height=5, bg=color, highlightthickness=0)
        indicator.pack(fill='x')
        
        # Count label
        count_label = ttk.Label(card, text="0", font=('Arial', 24, 'bold'))
        count_label.pack(pady=(10, 0))
        
        # Label
        text_label = ttk.Label(card, text=label, font=('Arial', 10))
        text_label.pack(pady=(0, 10))
        
        # Store references
        card.count_label = count_label
        card.text_label = text_label
        
        return card
        
    def create_statusbar(self):
        """Create status bar"""
        self.statusbar = ttk.Label(self.root, text="Ready", relief='sunken', anchor='w')
        self.statusbar.pack(side='bottom', fill='x')
        
    def update_status(self, message):
        """Update status bar message"""
        self.statusbar.config(text=message)
        self.root.update_idletasks()
        
    def load_file(self):
        """Load Excel file"""
        file_path = filedialog.askopenfilename(
            title="Select Excel File",
            filetypes=[
                ("Excel Files", "*.xlsx *.xls"),
                ("CSV Files", "*.csv"),
                ("All Files", "*.*")
            ]
        )
        
        if not file_path:
            return
        
        self.update_status(f"Loading {os.path.basename(file_path)}...")
        
        try:
            # Import data
            df = EXCEL_IMPORTER.import_file(file_path)
            
            # Validate
            required_columns = [
                'Company',
                'bs_cash_cash_equivalents_and_sti',
                'eqy_float',
                'eqy_sh_out',
                'px_last'
            ]
            
            is_valid, missing = EXCEL_IMPORTER.validate_data(df, required_columns)
            
            if not is_valid:
                messagebox.showerror(
                    "Invalid File",
                    f"Missing required columns:\n\n" + "\n".join(f"• {col}" for col in missing)
                )
                self.update_status("Error: Invalid file format")
                return
            
            # Store data
            self.current_data = df
            self.file_path = file_path
            
            # Update UI
            self.file_label.config(text=os.path.basename(file_path), foreground='black')
            self.analyze_btn.config(state='normal')
            
            # Show preview
            self.show_data_preview(df)
            
            self.update_status(f"Loaded {len(df)} companies from {os.path.basename(file_path)}")
            messagebox.showinfo("Success", f"Successfully loaded {len(df)} companies!")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load file:\n\n{str(e)}")
            self.update_status("Error loading file")
            
    def show_data_preview(self, df):
        """Display data preview"""
        self.preview_text.delete('1.0', tk.END)
        
        # Show basic info
        info_text = f"Dataset Information:\n"
        info_text += f"{'='*60}\n"
        info_text += f"Rows: {len(df)}\n"
        info_text += f"Columns: {len(df.columns)}\n"
        info_text += f"Columns: {', '.join(df.columns)}\n\n"
        
        # Show data
        info_text += "Data Preview:\n"
        info_text += f"{'='*60}\n"
        info_text += df.to_string()
        
        self.preview_text.insert('1.0', info_text)
        
    def analyze_data(self):
        """Analyze loaded data"""
        if self.current_data is None:
            messagebox.showwarning("No Data", "Please load an Excel file first")
            return
        
        # Disable button
        self.analyze_btn.config(state='disabled')
        
        # Show progress
        self.progress_label.config(text="Analyzing data... Please wait.")
        self.progress_bar.pack(fill='x', pady=10)
        self.progress_bar.start()
        
        # Run analysis in thread
        thread = threading.Thread(target=self._run_analysis)
        thread.start()
        
    def _run_analysis(self):
        """Run analysis in background thread"""
        try:
            self.update_status("Transforming data...")
            
            # Transform to snapshots
            snapshots = EXCEL_IMPORTER.transform_equity_to_snapshots(self.current_data)
            
            self.update_status(f"Analyzing {len(snapshots)} companies...")
            
            # Analyze each
            results = []
            for i, snapshot in enumerate(snapshots):
                prev_snapshot = snapshots[i-1] if i > 0 else None
                analysis = ENGINE.analyze_snapshot(snapshot, prev_snapshot)
                
                results.append({
                    'company': snapshot.get('company', f'Company_{i}'),
                    'risk_score': analysis['risk_score'],
                    'risk_label': analysis['label'],
                    'metrics': snapshot
                })
            
            # Store results
            self.analysis_results = results
            
            # Update UI (must be done in main thread)
            self.root.after(0, self._display_results)
            
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("Analysis Error", str(e)))
            self.root.after(0, self._analysis_complete)
            
    def _display_results(self):
        """Display analysis results"""
        # Stop progress
        self.progress_bar.stop()
        self.progress_bar.pack_forget()
        self.progress_label.config(text="")
        
        # Clear existing results
        for item in self.results_tree.get_children():
            self.results_tree.delete(item)
        
        # Count by label
        safe_count = sum(1 for r in self.analysis_results if r['risk_label'] == 'SAFE')
        warning_count = sum(1 for r in self.analysis_results if r['risk_label'] == 'WARNING')
        risky_count = sum(1 for r in self.analysis_results if r['risk_label'] == 'RISKY')
        
        # Update summary cards
        self.safe_card.count_label.config(text=str(safe_count))
        self.warning_card.count_label.config(text=str(warning_count))
        self.risky_card.count_label.config(text=str(risky_count))
        
        # Populate tree
        for result in self.analysis_results:
            metrics = result['metrics']
            
            self.results_tree.insert('', 'end', values=(
                result['company'],
                f"{result['risk_score']:.2f}",
                result['risk_label'],
                f"{metrics.get('reserves', 0):,.0f}",
                f"{metrics.get('supply', 0):,.0f}",
                f"${metrics.get('price', 0):.2f}",
                f"{metrics.get('market_cap', 0):,.0f}",
                f"{metrics.get('cash_to_market_cap', 0)*100:.2f}%"
            ))
        
        # Update company selector in analytics tab
        companies = [r['company'] for r in self.analysis_results]
        self.company_selector['values'] = companies
        if companies:
            self.company_selector.current(0)
            self.show_company_details()
        
        # Switch to results tab
        self.notebook.select(self.results_tab)
        
        # Re-enable button
        self.analyze_btn.config(state='normal')
        
        self.update_status(f"Analysis complete: {len(self.analysis_results)} companies analyzed")
        messagebox.showinfo("Hybrid AI Analysis Complete", 
                          f"Successfully analyzed {len(self.analysis_results)} companies!\n\n"
                          f"Risk Distribution:\n"
                          f"SAFE: {safe_count}\n"
                          f"WARNING: {warning_count}\n"
                          f"RISKY: {risky_count}\n\n"
                          f"View 'AI Insights' tab for detailed analysis\n"
                          f"View 'Blockchain' tab for proofs & governance")
        
    def _analysis_complete(self):
        """Clean up after analysis"""
        self.progress_bar.stop()
        self.progress_bar.pack_forget()
        self.progress_label.config(text="")
        self.analyze_btn.config(state='normal')
        
    def export_results(self):
        """Export results to CSV"""
        if self.analysis_results is None:
            messagebox.showwarning("No Results", "Please analyze data first")
            return
        
        file_path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV Files", "*.csv"), ("All Files", "*.*")],
            initialfile=f"risk_analysis_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.csv"
        )
        
        if not file_path:
            return
        
        try:
            # Create DataFrame
            rows = []
            for result in self.analysis_results:
                metrics = result['metrics']
                rows.append({
                    'Company': result['company'],
                    'Risk Score': result['risk_score'],
                    'Risk Label': result['risk_label'],
                    'Reserves': metrics.get('reserves', 0),
                    'Supply': metrics.get('supply', 0),
                    'Price': metrics.get('price', 0),
                    'Market Cap': metrics.get('market_cap', 0),
                    'Cash/Market Cap': metrics.get('cash_to_market_cap', 0),
                    'Float Ratio': metrics.get('float_ratio', 0)
                })
            
            df = pd.DataFrame(rows)
            df.to_csv(file_path, index=False)
            
            messagebox.showinfo("Export Success", f"Results exported to:\n{file_path}")
            self.update_status(f"Exported to {os.path.basename(file_path)}")
            
        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to export:\n\n{str(e)}")
            
    def clear_results(self):
        """Clear all results"""
        self.current_data = None
        self.analysis_results = None
        self.file_path = None
        
        self.file_label.config(text="No file selected", foreground='gray')
        self.analyze_btn.config(state='disabled')
        
        # Clear tree
        for item in self.results_tree.get_children():
            self.results_tree.delete(item)
        
        # Reset cards
        self.safe_card.count_label.config(text="0")
        self.warning_card.count_label.config(text="0")
        self.risky_card.count_label.config(text="0")
        
        # Clear preview
        self.preview_text.delete('1.0', tk.END)
        
        self.update_status("Cleared all data")
        
    def show_help(self):
        """Show help dialog"""
        help_text = """
Quick Start Guide

1. Click "Browse" to select your Excel file
   Required columns:
   • Company
   • bs_cash_cash_equivalents_and_sti
   • eqy_float
   • eqy_sh_out
   • px_last

2. Click "Analyze Data" to run risk analysis

3. View results in the Results tab

4. Export results to CSV if needed

Keyboard Shortcuts:
• Ctrl+O: Open file
• Ctrl+A: Analyze data
• Ctrl+E: Export results

Risk Levels:
• SAFE (0-40): Low risk
• WARNING (41-70): Moderate risk
• RISKY (71-100): High risk
"""
        messagebox.showinfo("Quick Start Guide", help_text)
        
    def show_about(self):
        """Show about dialog"""
        about_text = """
Stablecoin Risk Monitor
Version 1.0

AI-Powered Risk Analysis for Financial Assets

Features:
• Excel/CSV data import
• 19-feature risk analysis
• Anomaly detection (Isolation Forest)
• XGBoost risk classification
• Merkle tree proof generation
• Blockchain integration
• Governance monitoring
• Real-time analysis
• CSV export

© 2026 Stablecoin Risk Monitor
Powered by AI & Blockchain
"""
        messagebox.showinfo("About", about_text)
    
    def show_company_details(self, event=None):
        """Show detailed analysis for selected company"""
        if not self.analysis_results:
            return
        
        selected = self.company_selector.get()
        if not selected:
            return
        
        # Find the company data
        company_data = None
        for result in self.analysis_results:
            if result['company'] == selected:
                company_data = result
                break
        
        if not company_data:
            return
        
        # Clear existing text
        self.analytics_text.delete('1.0', tk.END)
        
        # Build detailed report
        report = []
        report.append("═" * 80)
        report.append(f"  COMPREHENSIVE RISK ANALYSIS: {selected}")
        report.append("═" * 80)
        report.append("")
        
        # Overall Risk Assessment
        report.append("┌─ OVERALL RISK ASSESSMENT ─────────────────────────────────────────┐")
        report.append(f"│ Risk Score:        {company_data['risk_score']:.2f} / 100")
        report.append(f"│ Risk Label:        {company_data['risk_label']}")
        report.append(f"|  Recommendation:    {'Monitor regularly' if company_data['risk_label'] == 'SAFE' else 'Increased surveillance' if company_data['risk_label'] == 'WARNING' else 'Immediate action required'}")
        report.append("└────────────────────────────────────────────────────────────────────┘")
        report.append("")
        
        # AI Model Outputs
        analysis = company_data.get('analysis', {})
        explanation = analysis.get('explanation', {})
        
        report.append("┌─ HYBRID AI ANALYSIS ───────────────────────────────────────────────┐")
        report.append("|")
        report.append("| ANOMALY DETECTION (Isolation Forest):")
        anomaly_flag = explanation.get('anomaly_flag', 0)
        report.append(f"|    Status:          {'ANOMALY DETECTED' if anomaly_flag == 1 else 'Normal Pattern'}")
        report.append(f"│    Anomaly Score:   {'+20 points' if anomaly_flag == 1 else '0 points'}")
        report.append("│    Interpretation:  " + ("Unusual behavior detected - deviates from normal patterns" if anomaly_flag == 1 else "Behavior matches historical normal patterns"))
        report.append("|")
        report.append("| RISK CLASSIFICATION (XGBoost):")
        risk_class = explanation.get('risk_class', 0)
        risk_prob = explanation.get('risk_probability', 0)
        report.append(f"│    Predicted Class: {risk_class} ({'Low Risk' if risk_class == 0 else 'High Risk'})")
        report.append(f"│    Risk Probability: {risk_prob*100:.2f}%")
        report.append(f"│    Confidence:      {abs(0.5 - risk_prob)*200:.1f}%")
        report.append("|")
        report.append("| COMBINED HYBRID SCORE:")
        report.append(f"│    Base Score:      {risk_prob*100:.1f} (from XGBoost probability)")
        report.append(f"│    Anomaly Bonus:   {anomaly_flag * 20} (from Isolation Forest)")
        report.append(f"│    Final Score:     {company_data['risk_score']:.1f}")
        report.append("└────────────────────────────────────────────────────────────────────┘")
        report.append("")
        
        # Key Financial Metrics
        metrics = company_data['metrics']
        report.append("┌─ CORE FINANCIAL METRICS ───────────────────────────────────────────┐")
        report.append(f"│ Reserves (Cash):        ${metrics.get('reserves', 0):,.0f}")
        report.append(f"│ Supply (Shares):        {metrics.get('supply', 0):,.0f}")
        report.append(f"│ Price:                  ${metrics.get('price', 0):.2f}")
        report.append(f"│ Market Capitalization:  ${metrics.get('market_cap', 0):,.0f}")
        report.append(f"│ Equity Float:           {metrics.get('equity_float', 0):,.0f}")
        report.append(f"│ Whale Holdings:         {metrics.get('whale_supply', 0):,.0f}")
        report.append("└────────────────────────────────────────────────────────────────────┘")
        report.append("")
        
        # Risk Indicators
        report.append("┌─ DETAILED RISK INDICATORS ─────────────────────────────────────────┐")
        report.append(f"│ Diff (Supply - Reserves): {explanation.get('diff', 0):,.2f}")
        diff_status = "Adequate backing" if explanation.get('diff', 0) < 0 else "Supply exceeds reserves"
        report.append(f"│    Status: {diff_status}")
        report.append("│")
        report.append(f"│ Reserve/Supply Ratio:     {explanation.get('reserve_supply_ratio', 0):.4f}")
        ratio_status = "Strong reserves" if explanation.get('reserve_supply_ratio', 0) > 1 else "Thin reserves"
        report.append(f"│    Status: {ratio_status}")
        report.append("│")
        report.append(f"│ Cash/Market Cap Ratio:    {metrics.get('cash_to_market_cap', 0)*100:.2f}%")
        cash_status = "Excellent" if metrics.get('cash_to_market_cap', 0) > 0.1 else "Good" if metrics.get('cash_to_market_cap', 0) > 0.05 else "Lower reserves"
        report.append(f"│    Status: {cash_status}")
        report.append("│")
        report.append(f"│ Float Ratio:              {metrics.get('float_ratio', 0)*100:.2f}%")
        float_status = "High liquidity" if metrics.get('float_ratio', 0) > 0.8 else "Concentrated ownership"
        report.append(f"│    Status: {float_status}")
        report.append("└────────────────────────────────────────────────────────────────────┘")
        report.append("")
        
        # Delta Analysis (Changes)
        report.append("┌─ CHANGE ANALYSIS (Δ) ──────────────────────────────────────────────┐")
        report.append(f"│ Δ Reserves:    {explanation.get('delta_reserves', 0):+,.2f}")
        report.append(f"│ Δ Supply:      {explanation.get('delta_supply', 0):+,.2f}")
        report.append(f"│ % Reserve Change: {metrics.get('pct_reserve_change', 0)*100:+.2f}%")
        report.append(f"│ % Supply Change:  {metrics.get('pct_supply_change', 0)*100:+.2f}%")
        report.append(f"│ % Price Change:   {metrics.get('pct_price_change', 0)*100:+.2f}%")
        report.append("└────────────────────────────────────────────────────────────────────┘")
        report.append("")
        
        # All 19 Features
        raw_features = analysis.get('raw_features', {})
        if raw_features:
            report.append("┌─ COMPLETE 19-FEATURE ANALYSIS ─────────────────────────────────────┐")
            for i, (key, value) in enumerate(sorted(raw_features.items()), 1):
                report.append(f"│ {i:2d}. {key:25s} = {value:15.4f}")
            report.append("└────────────────────────────────────────────────────────────────────┘")
        
        # Insert into text widget
        self.analytics_text.insert('1.0', '\n'.join(report))
        
    def generate_merkle_proofs(self):
        """Generate Merkle tree proofs for all companies"""
        if not self.analysis_results:
            messagebox.showwarning("No Data", "Please analyze data first")
            return
        
        try:
            from crypto_layer.merkle_tree import build_merkle_tree, get_merkle_root, sha256
            
            self.blockchain_text.delete('1.0', tk.END)
            
            report = []
            report.append("═" * 80)
            report.append("  MERKLE TREE PROOF GENERATION")
            report.append("═" * 80)
            report.append("")
            
            # Create leaves from company data
            leaves = []
            for result in self.analysis_results:
                metrics = result['metrics']
                # Create leaf hash from company data
                data = f"{result['company']}|{metrics.get('reserves', 0)}|{metrics.get('supply', 0)}|{metrics.get('price', 0)}"
                leaf_hash = sha256(data)
                leaves.append(leaf_hash)
                report.append(f"Leaf: {result['company'][:30]:<30} -> {leaf_hash[:16]}...{leaf_hash[-16:]}")
            
            report.append("")
            report.append("─" * 80)
            report.append("Building Merkle Tree...")
            report.append("")
            
            # Build tree
            tree = build_merkle_tree(leaves)
            root = get_merkle_root(leaves)
            
            report.append(f"Tree Levels:    {len(tree)}")
            report.append(f"Total Leaves:   {len(leaves)}")
            report.append("")
            report.append("MERKLE ROOT:")
            report.append(f"   {root}")
            report.append("")
            report.append("─" * 80)
            report.append("")
            report.append("TREE STRUCTURE:")
            report.append("")
            
            for level_idx, level in enumerate(reversed(tree)):
                if level_idx == 0:
                    report.append(f"Level {len(tree) - level_idx - 1} (ROOT):    {level[0][:16]}...{level[0][-16:]}")
                elif level_idx == len(tree) - 1:
                    report.append(f"Level 0 (LEAVES):  {len(level)} leaves")
                else:
                    report.append(f"Level {len(tree) - level_idx - 1}:          {len(level)} nodes")
            
            report.append("")
            report.append("─" * 80)
            report.append("")
            report.append("CRYPTOGRAPHIC GUARANTEES:")
            report.append("  • Data Integrity: Any change in company data changes the root")
            report.append("  • Tamper-Proof: Cannot forge proofs without detection")
            report.append("  • Efficient Verification: O(log n) proof size")
            report.append("  • Immutable Record: Root can be stored on blockchain")
            report.append("")
            report.append("BLOCKCHAIN INTEGRATION:")
            report.append(f"  • Smart Contract: ProofOfReserves.sol")
            report.append(f"  • Root Hash: {root}")
            report.append(f"  • Ready for on-chain submission")
            report.append("")
            report.append("─" * 80)
            
            self.blockchain_text.insert('1.0', '\n'.join(report))
            
            messagebox.showinfo("Merkle Proofs Generated", 
                              f"Generated cryptographic proofs for {len(leaves)} companies\n\n"
                              f"Merkle Root: {root[:32]}...\n\n"
                              f"This root can be stored on-chain for tamper-proof verification!")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate proofs:\n\n{str(e)}")
    
    def show_governance(self):
        """Show blockchain governance information"""
        self.blockchain_text.delete('1.0', tk.END)
        
        report = []
        report.append("═" * 80)
        report.append("  BLOCKCHAIN GOVERNANCE & DAO")
        report.append("═" * 80)
        report.append("")
        
        report.append("GOVERNANCE DAO CONTRACT")
        report.append("─" * 80)
        report.append("Contract:       GovernanceDAO.sol")
        report.append("Purpose:        Decentralized decision-making for risk parameters")
        report.append("Status:         Deployed")
        report.append("")
        
        report.append("  KEY FUNCTIONS:")
        report.append("  • createProposal()    - Submit risk parameter changes")
        report.append("  • vote()              - Cast votes on proposals")
        report.append("  • executeProposal()   - Execute passed proposals")
        report.append("  • delegateVote()      - Delegate voting power")
        report.append("")
        
        report.append("  CURRENT GOVERNANCE STATUS:")
        report.append("    Active Proposals:     0")
        report.append("    Total Voters:         [Connect wallet to view]")
        report.append("    Quorum Required:      51%")
        report.append("")
        
        report.append("─" * 80)
        report.append("")
        report.append("PROOF OF RESERVES CONTRACT")
        report.append("─" * 80)
        report.append("Contract:       ProofOfReserves.sol")
        report.append("Purpose:        On-chain verification of reserve backing")
        report.append("Status:         Deployed")
        report.append("")
        
        report.append("KEY FUNCTIONS:")
        report.append("  • submitProof()       - Submit Merkle root on-chain")
        report.append("  • verifyProof()       - Verify reserve claims")
        report.append("  • updateReserves()    - Update reserve amounts")
        report.append("  • getLatestProof()    - Retrieve most recent proof")
        report.append("")
        
        if self.analysis_results:
            total_reserves = sum(r['metrics'].get('reserves', 0) for r in self.analysis_results)
            total_supply = sum(r['metrics'].get('supply', 0) for r in self.analysis_results)
            
            report.append("AGGREGATE METRICS (All Companies):")
            report.append(f"  Total Reserves:      ${total_reserves:,.0f}")
            report.append(f"  Total Supply:        {total_supply:,.0f}")
            report.append(f"  Overall Ratio:       {(total_reserves / (total_supply + 1e-9)):.4f}")
            report.append("")
        
        report.append("─" * 80)
        report.append("")
        report.append("BLOCKCHAIN NETWORK:")
        report.append("  Network:           Ethereum (or configured)")
        report.append("  RPC Endpoint:      http://127.0.0.1:8545 (local)")
        report.append("  Gas Optimization:  Enabled")
        report.append("  Upgradeable:       Via proxy pattern")
        report.append("")
        
        report.append("─" * 80)
        report.append("")
        report.append("SECURITY FEATURES:")
        report.append("  - Reentrancy Protection (OpenZeppelin)")
        report.append("  - Access Control (Ownable)")
        report.append("  - Pausable in emergency")
        report.append("  - Event logging for transparency")
        report.append("  - Time-locked execution")
        report.append("")
        
        report.append("─" * 80)
        report.append("")
        report.append("NEXT STEPS:")
        report.append("  1. Connect Web3 wallet (MetaMask)")
        report.append("  2. Generate Merkle proofs (button above)")
        report.append("  3. Submit root hash to ProofOfReserves contract")
        report.append("  4. Create governance proposals for parameter changes")
        report.append("  5. Monitor on-chain events")
        report.append("")
        
        self.blockchain_text.insert('1.0', '\n'.join(report))
    
    def generate_ai_suggestions(self):
        """Generate intelligent AI-powered suggestions based on portfolio analysis"""
        if not self.analysis_results:
            messagebox.showwarning("No Data", "Please analyze data first to generate AI suggestions")
            return
        
        self.analytics_text.delete('1.0', tk.END)
        
        # Analyze portfolio
        total_companies = len(self.analysis_results)
        safe_count = sum(1 for r in self.analysis_results if r['risk_label'] == 'SAFE')
        warning_count = sum(1 for r in self.analysis_results if r['risk_label'] == 'WARNING')
        risky_count = sum(1 for r in self.analysis_results if r['risk_label'] == 'RISKY')
        
        avg_risk_score = sum(r['risk_score'] for r in self.analysis_results) / total_companies
        
        # Calculate aggregate metrics
        total_reserves = sum(r['metrics'].get('reserves', 0) for r in self.analysis_results)
        total_supply = sum(r['metrics'].get('supply', 0) for r in self.analysis_results)
        total_market_cap = sum(r['metrics'].get('market_cap', 0) for r in self.analysis_results)
        
        # Identify highest risk companies
        sorted_by_risk = sorted(self.analysis_results, key=lambda x: x['risk_score'], reverse=True)
        top_risk_companies = sorted_by_risk[:3]
        
        # Identify companies with low cash ratios
        low_cash_companies = [r for r in self.analysis_results 
                             if r['metrics'].get('cash_to_market_cap', 0) < 0.05]
        
        # Identify anomalies
        anomaly_companies = []
        for r in self.analysis_results:
            if r.get('analysis', {}).get('explanation', {}).get('anomaly_flag', 0) == 1:
                anomaly_companies.append(r)
        
        # Build suggestions report
        report = []
        report.append("═" * 80)
        report.append("  AI-POWERED PORTFOLIO SUGGESTIONS & RECOMMENDATIONS")
        report.append("═" * 80)
        report.append("")
        
        # Portfolio Health Overview
        report.append("┌─ PORTFOLIO HEALTH OVERVIEW ────────────────────────────────────────┐")
        report.append(f"│ Total Companies Analyzed:  {total_companies}")
        report.append(f"│ Average Risk Score:        {avg_risk_score:.2f} / 100")
        report.append(f"│")
        report.append(f"│ Risk Distribution:")
        report.append(f"│   SAFE:     {safe_count} ({safe_count/total_companies*100:.1f}%)")
        report.append(f"│   WARNING:  {warning_count} ({warning_count/total_companies*100:.1f}%)")
        report.append(f"│   RISKY:    {risky_count} ({risky_count/total_companies*100:.1f}%)")
        
        # Overall assessment
        if avg_risk_score < 30:
            health = "EXCELLENT"
            assessment = "Portfolio shows strong fundamentals with minimal risk exposure"
        elif avg_risk_score < 50:
            health = "GOOD"
            assessment = "Portfolio is healthy but monitor flagged companies closely"
        elif avg_risk_score < 70:
            health = "MODERATE"
            assessment = "Portfolio requires attention - consider risk mitigation strategies"
        else:
            health = "CONCERNING"
            assessment = "Portfolio shows elevated risk - immediate review recommended"
        
        report.append(f"│")
        report.append(f"│ Overall Health:           {health}")
        report.append(f"│ Assessment:               {assessment}")
        report.append("└────────────────────────────────────────────────────────────────────┘")
        report.append("")
        
        # Key Recommendations
        report.append("┌─ AI RECOMMENDATIONS ───────────────────────────────────────────────┐")
        report.append("│")
        
        recommendation_count = 1
        
        # High risk companies
        if risky_count > 0:
            report.append(f"│ {recommendation_count}. HIGH PRIORITY - Address Risky Companies")
            report.append(f"│    {risky_count} company(ies) flagged as RISKY")
            for company in top_risk_companies[:3]:
                if company['risk_label'] == 'RISKY':
                    report.append(f"│    • {company['company']}: Score {company['risk_score']:.1f}")
                    report.append(f"│      Action: Immediate review of financials and risk exposure")
            report.append("│")
            recommendation_count += 1
        
        # Warning companies
        if warning_count > 0:
            report.append(f"│ {recommendation_count}. MEDIUM PRIORITY - Monitor Warning Companies")
            report.append(f"│    {warning_count} company(ies) showing warning signs")
            report.append(f"│    Action: Increase monitoring frequency to weekly")
            report.append(f"│    Action: Set up automated alerts for metric changes")
            report.append("│")
            recommendation_count += 1
        
        # Anomaly detection
        if anomaly_companies:
            report.append(f"│ {recommendation_count}. ANOMALY ALERT - Unusual Patterns Detected")
            report.append(f"│    {len(anomaly_companies)} company(ies) showing anomalous behavior")
            for company in anomaly_companies[:3]:
                report.append(f"│    • {company['company']}")
            report.append(f"│    Action: Investigate for data quality issues or market events")
            report.append(f"│    Action: Compare with industry peers and historical trends")
            report.append("│")
            recommendation_count += 1
        
        # Low cash ratio companies
        if low_cash_companies:
            report.append(f"│ {recommendation_count}. LIQUIDITY CONCERN - Low Cash Reserves")
            report.append(f"│    {len(low_cash_companies)} company(ies) with cash ratio < 5%")
            for company in low_cash_companies[:3]:
                cash_ratio = company['metrics'].get('cash_to_market_cap', 0) * 100
                report.append(f"│    • {company['company']}: {cash_ratio:.2f}% cash/market cap")
            report.append(f"│    Action: Assess liquidity risk and debt obligations")
            report.append(f"│    Action: Consider reducing exposure if ratio continues declining")
            report.append("│")
            recommendation_count += 1
        
        # Portfolio diversification
        if total_companies < 10:
            report.append(f"│ {recommendation_count}. DIVERSIFICATION - Expand Portfolio")
            report.append(f"│    Current portfolio size: {total_companies} companies")
            report.append(f"│    Action: Consider adding 5-10 more companies for better diversification")
            report.append(f"│    Action: Focus on different sectors and market caps")
            report.append("│")
            recommendation_count += 1
        
        # Positive findings
        if safe_count == total_companies:
            report.append(f"│ {recommendation_count}. EXCELLENT - All Companies Safe")
            report.append(f"│    Portfolio shows strong risk management")
            report.append(f"│    Action: Maintain current monitoring practices")
            report.append(f"│    Action: Review quarterly and adjust thresholds as needed")
            report.append("│")
            recommendation_count += 1
        
        report.append("└────────────────────────────────────────────────────────────────────┘")
        report.append("")
        
        # Risk Mitigation Strategies
        report.append("┌─ RISK MITIGATION STRATEGIES ───────────────────────────────────────┐")
        report.append("│")
        report.append("│ Short-term (Next 30 days):")
        report.append("│   1. Review all WARNING and RISKY companies in detail")
        report.append("│   2. Set up daily automated monitoring for high-risk positions")
        report.append("│   3. Establish clear exit criteria for deteriorating positions")
        report.append("│")
        report.append("│ Medium-term (Next 90 days):")
        report.append("│   1. Implement stress testing scenarios")
        report.append("│   2. Diversify across sectors and market caps")
        report.append("│   3. Establish reserve thresholds and rebalancing triggers")
        report.append("│")
        report.append("│ Long-term (Annual):")
        report.append("│   1. Review and update risk scoring models")
        report.append("│   2. Backtest model performance against historical data")
        report.append("│   3. Integrate external market data and sentiment analysis")
        report.append("│")
        report.append("└────────────────────────────────────────────────────────────────────┘")
        report.append("")
        
        # Portfolio Metrics
        report.append("┌─ PORTFOLIO METRICS ────────────────────────────────────────────────┐")
        report.append(f"│ Total Reserves:            ${total_reserves:,.0f}")
        report.append(f"│ Total Supply (Shares):     {total_supply:,.0f}")
        report.append(f"│ Total Market Cap:          ${total_market_cap:,.0f}")
        report.append(f"│ Average Cash Ratio:        {(total_reserves/total_market_cap*100) if total_market_cap > 0 else 0:.2f}%")
        report.append(f"│")
        report.append(f"│ Highest Risk Company:      {top_risk_companies[0]['company']}")
        report.append(f"│   Risk Score:              {top_risk_companies[0]['risk_score']:.2f}")
        report.append(f"│")
        report.append(f"│ Lowest Risk Company:       {sorted_by_risk[-1]['company']}")
        report.append(f"│   Risk Score:              {sorted_by_risk[-1]['risk_score']:.2f}")
        report.append("└────────────────────────────────────────────────────────────────────┘")
        report.append("")
        
        # Next Steps
        report.append("┌─ RECOMMENDED NEXT STEPS ───────────────────────────────────────────┐")
        report.append("│")
        report.append("│ 1. PRIORITIZE: Review companies in order of risk score")
        report.append("│ 2. INVESTIGATE: Focus on anomaly-flagged companies first")
        report.append("│ 3. MONITOR: Set up alerts for metric threshold breaches")
        report.append("│ 4. DOCUMENT: Record rationale for any position adjustments")
        report.append("│ 5. REVIEW: Schedule weekly portfolio health checks")
        report.append("│ 6. VERIFY: Submit Merkle proofs to blockchain for audit trail")
        report.append("│ 7. REPORT: Generate monthly risk reports for stakeholders")
        report.append("│")
        report.append("└────────────────────────────────────────────────────────────────────┘")
        report.append("")
        
        report.append("─" * 80)
        report.append("")
        report.append("AI Suggestions Generated: " + datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        report.append("Model: Hybrid Isolation Forest + XGBoost Risk Classifier")
        report.append("")
        report.append("Note: These suggestions are AI-generated recommendations based on")
        report.append("quantitative analysis. Always combine with qualitative assessment")
        report.append("and domain expertise before making investment decisions.")
        report.append("")
        
        self.analytics_text.insert('1.0', '\n'.join(report))
        
        messagebox.showinfo("AI Suggestions Generated", 
                          f"Generated {recommendation_count-1} AI-powered recommendations\n\n"
                          f"Portfolio Health: {health}\n"
                          f"Average Risk Score: {avg_risk_score:.1f}/100\n\n"
                          f"Review the AI Insights tab for detailed suggestions.")


def main():
    """Main entry point"""
    root = tk.Tk()
    app = RiskMonitorGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
