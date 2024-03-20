import os
import tkinter as tk
from tkinter import ttk, simpledialog,messagebox,filedialog
import ast

import os,sys
from functools import reduce

# from PhD_database.PhD_database import settings

currentdir = os.getcwd()
parentdir = os.path.dirname(currentdir)
gparentdir = os.path.dirname(parentdir)
ggparentdir = os.path.dirname(gparentdir)

sys.path.insert(0, '/'.join([gparentdir,'prototyping'])) 
sys.path.insert(0, '/'.join([gparentdir,'minions'])) 
sys.path.insert(0, '/'.join([gparentdir])) 

from Functions.WorkFlow import run_workflow

import json


class PopupWindow:
    def __init__(self, parent):
        top = self.top = tk.Toplevel(parent)
        top.title("Add Values")
        self.myLabel = tk.Label(top, text="Enter the radius (float), the number of spheres (2^n) and the  your values separated by commas")
        self.myLabel.pack()
        self.myEntryBox = tk.Entry(top, width=50)
        self.myEntryBox.pack()
        self.mySubmitButton = tk.Button(top, text='Submit', command=self.send)
        self.mySubmitButton.pack()
        self.values = []

    def send(self):
        input_values = self.myEntryBox.get()
        self.values = [value.strip() for value in input_values.split(',')]
        self.top.destroy()

class WorkflowAssistant:

    def __init__(self) -> None:
        # Initialize your nested dictionary       
        self.workflow = {} 
        # Initialize settings dictionary
        self.settings = {'Path': '', 'Folder': ''}  

        workflow_template_file = ''.join(['workflow_templates.json'])
                                # "/".join([path,
                                # folder,
                                # ''.join(['workflow_templates.json'])
                                # ])


        # Opening JSON file
        with open(workflow_template_file) as handle:
            self.templates = json.loads(handle.read())

        # Initialize templates dictionary        
        # self.templates = json.load(f)  
        
        # {
        #     'GMAO':{  'name':'GMAO',
        #             'procedure': 'GigaMesh', 
        #             'stage':'',
        #             'method':'',
        #             'parameters':'',
        #             'variables': '',                         
        #             'processed':'_GMAO',
        #             'metadata':['']},
        #     'GMCF':{ 'name':'GMCF',
        #             'procedure': 'GigaMesh', 
        #             'stage':'',
        #             'method':'gigamesh-clean', 
        #             'variables': {},             
        #             'parameters':'-m "original, lithic"',
        #             'processed':'_GMCF',
        #             'metadata':['mesh_polish']},    
        #     'MSII':{'name':'MSII',
        #         'procedure': 'GigaMesh', 
        #         'stage':'{}',
        #         'method':'gigamesh-featurevectors',
        #         'variables': {'r':1.00,'n':4,'v':256},                 
        #         'parameters':'-r 1.00 -n 4 -l 256',
        #         'processed':'_r1.00_n4_v256',
        #         'metadata':['info','normal','surface','volume']}} 

        # Initialize the main Tkinter window
        self.root = tk.Tk()
        self.root.title("Workflow Assistant for Processing Artifacts")

        # Configure the grid layout manager
        # Configures 2 columns to have equal weight
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_columnconfigure(1, weight=1)  
        # Configures a 3. column to have doublr the weight
        self.root.grid_columnconfigure(2, weight=2)

        self.create_widgets()

        self.place_widgets_in_grid()

        # Initial display update
        self.update_display()


    # Start the Tkinter event loop
    def run_GUI(self):
        
        self.root.mainloop()

    def create_widgets (self):

        # Path entry and browse button
        self.path_label = tk.Label(self.root, text="Path:")
        self.path_var = tk.StringVar()
        self.path_entry = tk.Entry(self.root, width=50, textvariable=self.path_var)
        self.browse_button = tk.Button(self.root, text="Browse...", command=self.browse_path)
        self.path_var.trace_add("write", self.update_path)

        # Combobox for selecting a subfolder
        self.subfolder_label = tk.Label(self.root, text="Select Subfolder:")
        self.subfolder_var = tk.StringVar()
        self.subfolder_combobox = ttk.Combobox(self.root, width=47, textvariable=self.subfolder_var)
        self.subfolder_combobox.bind('<<ComboboxSelected>>', self.on_subfolder_selection)
        self.subfolder_var.trace_add("write", self.update_subfolder)


        # Combobox for selecting the main key
        key_options = [1, 2, 3]  
        self.key_combobox = ttk.Combobox(self.root, values=key_options)

        # Combobox for selecting the subkey
        subkey_options = ['subkey1', 'subkey2', 'subkey3']  # Example subkeys
        self.subkey_combobox = ttk.Combobox(self.root, values=subkey_options)

        # Text widget to display the dictionary
        self.import_text = tk.Text(self.root, height=15, width=50)

        # Text widget to display the dictionary
        self.display_text = tk.Text(self.root, height=15, width=50)

        # Button to add a new key-value pair
        # self.add_single_entry_button = tk.Button(self.root, text="Add Single Entry", command=self.add_entry)

        # Button to print dictionary
        # self.print_dictionary_button = tk.Button(self.root, text="Print Dictionary", command=self.print_dictionary)

        # Button to update workflow from display_text content
        self.update_button = tk.Button(self.root, text="Update Dictionary from Display", command=self.update_dict_from_import_text)

        # Dropdown menu for selecting a dictionary template
        self.template_combobox_label = tk.Label(self.root, text="Select Template:")
        self.template_combobox = ttk.Combobox(self.root, values=list(self.templates.keys()))
        self.template_combobox.bind('<<ComboboxSelected>>', lambda event: self.update_import_from_template())

        # Button to open the popup window for the selected template
        self.var_btn = tk.Button(self.root, text="Edit Variabels of Template", command=lambda: self.update_template_values(self.template_combobox.get()))

        self.run_worfkflow_btn = tk.Button(self.root, text="Run Workflow", command=lambda: self.run_workflow_event())

           
    def place_widgets_in_grid(self):

        # Place widgets using grid layout
        self.path_label.grid(row=0, column=0, sticky="ew")
        self.path_entry.grid(row=0, column=1, sticky="ew")
        self.browse_button.grid(row=1, column=1, sticky="ew")
        self.subfolder_label.grid(row=2, column=0, sticky="ew")
        self.subfolder_combobox.grid(row=2, column=1, sticky="ew")
        # self.add_single_entry_button.grid(row=3, column=0, sticky="ew")
        # self.print_dictionary_button.grid(row=3, column=1, sticky="ew")
        self.template_combobox_label.grid(row=3, column=0, sticky="ew")
        self.template_combobox.grid(row=3, column=1, sticky="ew")
          
        self.import_text.grid(row=4, column=0, columnspan=2, sticky="ew")
        self.var_btn.grid(row=5, column=0, padx=10, pady=5)   
        self.update_button.grid(row=5, column=1, sticky="ew")
        self.run_worfkflow_btn.grid(row=0, column=2, sticky="ew")
        self.display_text.grid(row=1, column=2, rowspan=6, sticky="ew")

    def add_entry(self):
        key = self.key_combobox.get()
        if not key:
            # No key selected, do nothing
            return  

        if key not in self.workflow:
            self.workflow[key] = {}

        subkey = self.subkey_combobox.get()
        if not subkey:
            # No subkey selected, do nothing
            return  

        value = simpledialog.askstring("Input", "Enter value for '{} > {}':".format(key, subkey), parent=self.root)
        # Only add if value is not empty
        if value:  
            self.workflow[key][subkey] = value
            self.update_display()

    # Function to display the current state of the dictionary
    def update_display(self):
        self.display_text.delete(1.0, tk.END)  # Clear current text
        self.display_text.insert(tk.END, str(self.workflow))  # Display updated dictionary

    def retrieve_input(self):
        return self.root.myText_Box.get("1.0",'end-1c')
    
    #############
    # Update path and subfolder in settings 

    def update_path (self,*args):

        self.settings ['Path'] = self.path_var.get()

    def update_subfolder (self,*args):

        """
        Update the label with the value of the entry_var.
        """
        # The get() method retrieves the current value of entry_var
        self.settings ['Folder'] = self.subfolder_var.get()        

    # def print_dictionary(self):
    #     print(self.workflow)

    def update_import_from_template(self):
        # Get the name of the selected template
        self.selected_template_name = self.template_combobox.get()
        # Find the corresponding dictionary template
        self.selected_template = self.templates.get(self.selected_template_name, {})
        # Update the display_text widget
        self.import_text.delete(1.0, tk.END)  # Clear current content
        self.import_text.insert(tk.END, str(self.selected_template))  # Insert the selected template

    def update_display_from_template_with_values(self):
        selected_template_name = self.template_combobox.get()
        selected_template = self.templates.get(selected_template_name, {})
        
        # Launch the popup window for input
        popup = PopupWindow(self.root)
        self.root.wait_window(popup.top)
        
        # Here, adjust the code below to fit where you want to insert the values in your template
        # Example: Inserting values directly if the template is a list
        if isinstance(selected_template, list):
            selected_template.extend(popup.values)
        elif isinstance(selected_template, dict):
            # Example: Adding values to a specific key in the dictionary
            key_to_update = 'your_specific_key'
            selected_template[key_to_update] = popup.values
        
        self.import_text.delete(1.0, tk.END)
        self.import_text.insert(tk.END, str(selected_template))

    def update_dict_from_import_text(self):
        try:
            # Attempt to safely evaluate the text content as a Python literal
            updated_dict = ast.literal_eval(self.import_text.get(1.0, tk.END))
            if isinstance(updated_dict, dict):
                self.workflow.update({int(updated_dict['stage']):updated_dict}) 
                messagebox.showinfo("Success", "Dictionary updated successfully.")
                self.update_display()
            else:
                messagebox.showerror("Error", "The content is not a valid dictionary.")
        except ValueError as e:
            messagebox.showerror("Error", "Invalid content. Please ensure it's a valid dictionary format.")             

    def update_dict_from_display(self):
        try:
            # Attempt to safely evaluate the text content as a Python literal
            updated_dict = ast.literal_eval(self.display_text.get(1.0, tk.END))
            if isinstance(updated_dict, dict):
                self.workflow.update(updated_dict) 
                messagebox.showinfo("Success", "Dictionary updated successfully.")
                self.update_display()
            else:
                messagebox.showerror("Error", "The content is not a valid dictionary.")
        except ValueError as e:
            messagebox.showerror("Error", "Invalid content. Please ensure it's a valid dictionary format.")     

    ################################################
    # select path and subfolder

    # Function to browse for a directory path
    def browse_path(self):
        directory = filedialog.askdirectory()
        if directory:  # Ensure a directory was selected
            self.path_entry.delete(0, tk.END)
            self.path_entry.insert(0, directory)
            self.settings['Path'] = directory 
            self.update_subfolders(directory)

    

    # Function to update the subfolder dropdown based on the selected path
    def update_subfolders(self,directory):
        subfolders = [f.name for f in os.scandir(directory) if f.is_dir()]
        self.subfolder_combobox['values'] = subfolders
        if subfolders:
            self.subfolder_combobox.current(0)  # Automatically select the first subfolder

    ################################################
    # Event update subfolder
    def on_subfolder_selection(self,event):
        self.settings['Folder'] = self.subfolder_combobox.get()

    def on_subfolder_selection(self,event):
        self.settings['Folder'] = self.subfolder_combobox.get()

    def update_template_values(self,template_name):
        
        def save_values():
            # Special handling for nested 'variables' dictionary
            for var_key in self.templates[template_name]['variables'].keys():

                self.templates[template_name]['variables'][var_key] = variable_entries[var_key].get()
                
            self.templates[template_name]['stage'] = stage.get()
            self.update_import_from_template()
            popup.destroy()

        popup = tk.Toplevel()
        popup.title(f"Update Values for {template_name}")

        variable_entries = {}
        stage = 0

        # Create entry widgets for template fields
        row = 0
        # Special handling for Stage variable
        tk.Label(popup, text="Stage").grid(row=row, column=0)

        row += 1 

        entry = tk.Entry(popup)
        # Pre-fill current value
        entry.insert(0, self.templates[template_name]['stage']) 
        entry.grid(row=row, column=1)
        stage = entry        

        row += 1        

        # Special handling for 'variables' nested dictionary
        tk.Label(popup, text="Variables").grid(row=row, column=0)
        row += 1
        for key in self.templates[template_name]['variables'].keys():
            tk.Label(popup, text=key).grid(row=row, column=0)
            entry = tk.Entry(popup)
            # Pre-fill current value
            entry.insert(0, self.templates[template_name]['variables'][key]) 
            entry.grid(row=row, column=1)
            variable_entries[key] = entry
            row += 1

        # Save button
        save_btn = tk.Button(popup, text="Save", command=save_values)
        save_btn.grid(row=row, column=0, columnspan=2)

    def run_workflow_event (self):
        
        self.update_dict_from_display()
        print(1)
        run_workflow (self.settings['Path'],self.settings['Folder'],self.workflow)
        print(1)        
