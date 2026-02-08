# Import necessary modules for the GUI application
import json  # For reading/writing JSON files where the employee data is stored
import tkinter as tk  # Main GUI library for creating windows and widgets
from tkinter import scrolledtext  # Special text widgets because I like to have the ability to scroll back to what I had done earlier
from tkinter import ttk  # Themed tkinter widgets for better appearance

# Main class that encapsulates all of the GUI's functionality and employee data management
# This class follows object-oriented programming principles to organize related functions
class EmployeeDatabaseGUI:
    # Constructor method - automatically called when creating a new instance of the class
    # The 'self' parameter refers to the specific instance being created
    # The 'root' parameter is the main tkinter window passed from the main() function
    def __init__(self, root):
        # Store the reference to the main window so other methods can access it
        # 'self.root' becomes an instance attribute accessible throughout the class, otherwise other methods wouldn't 
        # be able to reference the main window
        self.root = root
        
        # Configure the main window properties
        self.root.title("Employee Database Test")  # Sets the window's title text
        self.root.state('zoomed')  # Open window in full screen so the buttons are all fully visible
        
        # Dictionary to normalize user input field names to resolve case sensativity issues
        # This allows users to type "name", "NAME", or "Name" and get the same result
        self.field_mapping = {
            'NAME': 'Name',  # Maps uppercase input to proper case, later in the program .upper is used to normalize user input
            'AGE': 'Age', 
            'YEARS WITH COMPANY': 'Years with company',
            'SALARY': 'Salary',
            'SALES': 'Sales'
        }
        
        # Initialize empty dictionary to store employee data loaded from JSON file
        self.example_dict = {}
        
        # Attempt to load existing employee data from JSON file
        try:
            # Open file in read mode and parse JSON into Python dictionary
            with open('employees.json', 'r') as file:
                self.example_dict = json.load(file)
        except FileNotFoundError:
            # If file doesn't exist, display a message in the output area
            self.display_output("Warning: employees.json file not found! Starting with empty database.")
        
        # Call method to create and arrange all GUI elements
        # This separates the initialization logic from the GUI creation logic
        self.setup_gui()
        
    # Method to create and configure all GUI elements
    # The 'self' parameter allows this method to:
    # 1. Access the root window (self.root)
    # 2. Create instance attributes (self.output_text, self.output_frame, etc.)
    # 3. Call other instance methods (self.display_output)
    # 4. Reference other instance data (self.view_all_employees, etc.)
    def setup_gui(self):
        # Create and configure the title label at the top of the window
        title_label = tk.Label(self.root, text="Employee Database Test", 
                              font=("Arial", 16, "bold"))  # Set font family, size, and style
        title_label.pack(pady=10)  # Add the label to window with 10 pixels padding above/below
        
        # Create a frame container for the scrolling text output area
        # Frames are invisible containers used to organize widgets
        self.output_frame = tk.Frame(self.root)
        # Pack with fill=BOTH (expand horizontally and vertically) and expand=True (take extra space)
        self.output_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
        
        # Create a scrollable text widget for displaying program output
        # This replaces the console output from the original command-line version
        # state='disabled' makes it read-only for users but we can still write to it programmatically
        self.output_text = scrolledtext.ScrolledText(self.output_frame, 
                                                   wrap=tk.WORD,  # Wrap text at word boundaries
                                                   height=20,     # Height in text lines
                                                   width=80,      # Width in characters
                                                   state='disabled')  # Read-only for users
        self.output_text.pack(fill=tk.BOTH, expand=True)  # Fill all available space
        
        # Create a frame to hold all the action buttons horizontally
        buttons_frame = tk.Frame(self.root)
        buttons_frame.pack(pady=10)  # Add vertical padding around the button frame
        
        # Define button configurations as a list of tuples
        # Each tuple contains (display_text, function_to_call_when_clicked)
        # The 'self.' prefix allows you to reference methods within this class instance
        buttons = [
            ("1. View All Employees", self.view_all_employees),    # Calls self.view_all_employees when clicked
            ("2. View Employee by ID", self.view_employee_by_id),  # Calls self.view_employee_by_id when clicked
            ("3. Edit Employee Data", self.edit_employee_data),    # And so on...
            ("4. Delete Employee Data", self.delete_employee_data),
            ("5. Add Employee", self.add_employee),
            ("6. Save and Exit", self.save_and_exit),
            ("7. Exit without Saving", self.exit_without_saving),
            ("8. Clear Screen", self.clear_output)                 # Clears the output display area
        ]
        
        # Create and place buttons using a loop for efficiency
        # enumerate() gives us both the index (i) and the tuple (text, command)
        for i, (text, command) in enumerate(buttons):
            # Create a button with the specified text and command function
            btn = tk.Button(buttons_frame, text=text, command=command, 
                          width=18, height=2)  # Consistent button sizing
            # Use grid layout to place buttons horizontally in a single row
            # row=0 (all in first row), column=i (spread across columns), padx=2 (small horizontal spacing)
            btn.grid(row=0, column=i, padx=2)
        
        # Create a frame for the input area at the bottom
        input_frame = tk.Frame(self.root)
        input_frame.pack(pady=10, padx=10, fill=tk.X)  # fill=X means expand horizontally only
        
        # Add a label to identify the input field
        tk.Label(input_frame, text="Input:").pack(side=tk.LEFT)  # Align to left side of frame
        
        # Create an entry widget for user text input
        self.input_entry = tk.Entry(input_frame, width=50)
        # Pack to left side with padding, fill remaining horizontal space
        self.input_entry.pack(side=tk.LEFT, padx=(5, 0), fill=tk.X, expand=True)
        
        # Bind Enter key to process input
        self.input_entry.bind('<Return>', self.process_input)
        
        # Add a Submit button next to the input field, redundant but nice to have incase someone has a broken enter key
        submit_btn = tk.Button(input_frame, text="Submit", command=self.process_input,
                             width=10, height=1)
        submit_btn.pack(side=tk.RIGHT, padx=(5, 0))
        
        # Variables to track input state for multi-step operations
        self.current_operation = None
        self.operation_step = 0
        self.temp_data = {}
        
        # Display welcome message in the output area when GUI starts
        self.display_output("Welcome to the Employee Database Viewer!\nClick any button below to perform an action.\n")

    # Utility method to standardize employee ID format
    # This ensures consistent ID format regardless of how user enters the ID
    def normalize_employee_id(self, emp_id_input):
        #Convert employee ID input to the proper 3-digit format
        # Remove any leading/trailing whitespace from user input
        emp_id = emp_id_input.strip()
        
        # Check if the input contains only digits (is a valid number)
        if emp_id.isdigit():
            # zfill(3) pads the string with leading zeros to make it exactly 3 characters
            # Example: "1" becomes "001", "45" becomes "045", "123" stays "123"
            emp_id = emp_id.zfill(3)
        return emp_id
    
    # Utility method to display text in the GUI output area
    # This replaces the print() statements from the original command-line version
    def display_output(self, text):
        #Display text in the output area
        # Temporarily enable the text widget so we can insert text
        self.output_text.config(state='normal')
        
        # Insert text at the end of the scrolling text widget
        # tk.END is a constant representing the end of the text
        self.output_text.insert(tk.END, text + '\n')
        
        # Automatically scroll to show the most recent output
        # This ensures users always see the latest information
        self.output_text.see(tk.END)
        
        # Disable the text widget again to prevent user input
        self.output_text.config(state='disabled')
        
    # Utility method to clear all text from the output area
    # Can be used to start fresh or clean up the display
    def clear_output(self):
        '''Clear the output area'''
        # Temporarily enable the text widget so we can clear it
        self.output_text.config(state='normal')
        
        # Delete all text from position 1.0 (line 1, character 0) to END
        # In tkinter, text positions are specified as "line.character"
        self.output_text.delete(1.0, tk.END)
        
        # Disable the text widget again to prevent user input
        self.output_text.config(state='disabled')
        
    # Method to get user input from the text entry field
    def get_user_input(self):
        #Get text from input field and clear it
        user_input = self.input_entry.get().strip()
        self.input_entry.delete(0, tk.END)  # Clear the input field
        return user_input
        
    # Method to handle input processing for multi-step operations
    def process_input(self, event=None):
        #Process user input based on current operation state
        user_input = self.get_user_input()
        
        if not user_input:
            return
            
        # Handle different operations based on current state
        if self.current_operation == "view_by_id":
            self.handle_view_by_id_input(user_input)
        elif self.current_operation == "edit":
            self.handle_edit_input(user_input)
        elif self.current_operation == "delete":
            self.handle_delete_input(user_input)
        elif self.current_operation == "add":
            self.handle_add_input(user_input)
        else:
            self.display_output(f"No active operation. Input received: {user_input}")
            
    # Reset operation state
    def reset_operation_state(self):
        #Reset the operation tracking variables
        self.current_operation = None
        self.operation_step = 0
        self.temp_data = {}
        
    # Employee management method - Display all employees in the database
    # This method is called when button "1. View All Employees" is clicked
    def view_all_employees(self):
        #Display all employees
        # Add a header to clearly separate this operation's output
        self.display_output("=== All Employees ===")
        
        # Iterate through the employee dictionary
        # .items() returns key-value pairs: emp_id (key) and emp_data (value dictionary)
        for emp_id, emp_data in self.example_dict.items():
            # Format and display each employee's information in a readable format
            # Uses f-string formatting to insert variables into the string
            self.display_output(f"ID: {emp_id}, Name: {emp_data['Name']}, Age: {emp_data['Age']}, "
                              f"Years with company: {emp_data['Years with company']}, "
                              f"Salary: {emp_data['Salary']}, Sales: {emp_data['Sales']}")
        
        # Add spacing after the output for better readability
        self.display_output("")
        
    # Employee management method - Display single employee by ID
    # This method is called when button "2. View Employee by ID" is clicked
    def view_employee_by_id(self):
        #View employee by ID
        self.current_operation = "view_by_id"
        self.operation_step = 0
        self.display_output("Enter the employee ID in the input box below and press Submit:")
        
    def handle_view_by_id_input(self, emp_id_input):
        #Handle input for view employee by ID operation
        emp_id = self.normalize_employee_id(emp_id_input)
        
        # Check if the employee ID exists in our database dictionary
        if emp_id in self.example_dict:
            # Retrieve the employee data dictionary for this ID
            emp_data = self.example_dict[emp_id]
            
            # Display employee information with header
            self.display_output(f"=== Employee {emp_id} ===")
            self.display_output(f"ID: {emp_id}, Name: {emp_data['Name']}, Age: {emp_data['Age']}, "
                              f"Years with company: {emp_data['Years with company']}, "
                              f"Salary: {emp_data['Salary']}, Sales: {emp_data['Sales']}")
        else:
            # Employee not found - display error message
            self.display_output(f"Employee {emp_id} not found.")
        
        # Add spacing for readability and reset operation
        self.display_output("")
        self.reset_operation_state()
        
    # Employee management method - Edit existing employee data
    # This method is called when button "3. Edit Employee Data" is clicked
    def edit_employee_data(self):
        #Edit employee data
        self.current_operation = "edit"
        self.operation_step = 0
        self.temp_data = {}
        self.display_output("Enter the employee ID to edit in the input box below and press Submit:")
        
    def handle_edit_input(self, user_input):
        #Handle input for edit employee operation
        if self.operation_step == 0:
            # First step: get employee ID
            emp_id = self.normalize_employee_id(user_input)
            
            if emp_id in self.example_dict:
                self.temp_data['emp_id'] = emp_id
                emp_data = self.example_dict[emp_id]
                self.display_output(f"Current data for ID {emp_id}: {emp_data}")
                self.display_output("Enter the field to edit (Name, Age, Years with company, Salary, Sales):")
                self.operation_step = 1
            else:
                self.display_output(f"Employee {emp_id} not found.")
                self.reset_operation_state()
                
        elif self.operation_step == 1:
            # Second step: get field to edit
            field_key = user_input.strip().upper()
            
            if field_key in self.field_mapping:
                self.temp_data['field'] = self.field_mapping[field_key]
                self.display_output(f"Enter the new value for {self.temp_data['field']}:")
                self.operation_step = 2
            else:
                self.display_output("Invalid field. Please enter: Name, Age, Years with company, Salary, or Sales")
                
        elif self.operation_step == 2:
            # Third step: get new value
            emp_id = self.temp_data['emp_id']
            field = self.temp_data['field']
            
            # Update the employee's data
            self.example_dict[emp_id][field] = user_input
            self.display_output(f"Updated data for ID {emp_id}: {self.example_dict[emp_id]}")
            self.display_output("")
            self.reset_operation_state()
        
    # Employee management method - Delete employee from database
    # This method is called when button "4. Delete Employee Data" is clicked
    def delete_employee_data(self):
        #Delete employee data
        self.current_operation = "delete"
        self.operation_step = 0
        self.display_output("Enter the employee ID to delete in the input box below and press Submit:")
        
    def handle_delete_input(self, user_input):
        #Handle input for delete employee operation
        emp_id = self.normalize_employee_id(user_input)
        
        # Check if employee exists
        if emp_id in self.example_dict:
            # Delete the employee from the dictionary
            del self.example_dict[emp_id]
            self.display_output(f"Employee with ID {emp_id} has been deleted.")
        else:
            # Employee not found
            self.display_output(f"Employee {emp_id} not found.")
        
        self.display_output("")  # Add spacing
        self.reset_operation_state()
        
    # Employee management method - Add new employee to database
    # This method is called when button "5. Add Employee" is clicked
    def add_employee(self):
        #Add new employee
        self.current_operation = "add"
        self.operation_step = 0
        self.temp_data = {}
        self.display_output("Enter the new employee ID in the input box below and press Submit:")
        
    def handle_add_input(self, user_input):
        #Handle input for add employee operation
        if self.operation_step == 0:
            # Step 1: Get employee ID
            emp_id = self.normalize_employee_id(user_input)
            
            if emp_id in self.example_dict:
                self.display_output("Employee ID already exists.")
                self.reset_operation_state()
                return
            
            self.temp_data['emp_id'] = emp_id
            self.display_output("Enter the employee's name:")
            self.operation_step = 1
            
        elif self.operation_step == 1:
            # Step 2: Get name
            self.temp_data['name'] = user_input
            self.display_output("Enter the employee's age:")
            self.operation_step = 2
            
        elif self.operation_step == 2:
            # Step 3: Get age
            self.temp_data['age'] = user_input
            self.display_output("Enter the employee's years with company:")
            self.operation_step = 3
            
        elif self.operation_step == 3:
            # Step 4: Get years with company
            self.temp_data['years'] = user_input
            self.display_output("Enter the employee's salary:")
            self.operation_step = 4
            
        elif self.operation_step == 4:
            # Step 5: Get salary
            self.temp_data['salary'] = user_input
            self.display_output("Enter the employee's sales:")
            self.operation_step = 5
            
        elif self.operation_step == 5:
            # Step 6: Get sales and create employee
            self.temp_data['sales'] = user_input
            
            # Create new employee record
            emp_id = self.temp_data['emp_id']
            self.example_dict[emp_id] = {
                "Name": self.temp_data['name'],
                "Age": self.temp_data['age'],
                "Years with company": self.temp_data['years'],
                "Salary": self.temp_data['salary'],
                "Sales": self.temp_data['sales']
            }
            
            self.display_output(f"Employee with ID {emp_id} has been added.")
            self.display_output("")
            self.reset_operation_state()
        
    # Application management method - Save data and exit program
    # This method is called when button "6. Save and Exit" is clicked
    def save_and_exit(self):
        #Save data and exit
        try:
            # Inform user that saving is in progress
            self.display_output("Saving updated data to employees.json...")
            
            # Open JSON file in write mode ('w') which overwrites existing content
            with open('employees.json', 'w') as file:
                # Convert Python dictionary to JSON format and write to file
                # indent=4 makes the JSON file human-readable with proper formatting
                json.dump(self.example_dict, file, indent=4)
            
            # Confirm successful save operation
            self.display_output("Data saved successfully. Exiting program...")
            
            # Close the application window and exit the program
            # quit() terminates the mainloop() and closes the GUI
            self.root.quit()
            
        except Exception as e:
            # Handle any file writing errors (permissions, disk full, etc.)
            # str(e) converts the exception object to a readable error message
            self.display_output(f"Error: Failed to save data: {str(e)}")
            
    # Application management method - Exit without saving changes
    # This method is called when button "7. Exit without Saving" is clicked
    def exit_without_saving(self):
        #Exit without saving
        # Display confirmation message
        self.display_output("Exiting without saving...")
        
        # Close the application without saving
        self.root.quit()


# Main function to initialize and start the GUI application
# This function sets up the tkinter environment and starts the program
def main():
    # Create the root window - this is the main application window
    # tk.Tk() creates the primary window that will contain all other widgets
    root = tk.Tk()
    
    # Create an instance of our EmployeeDatabaseGUI class
    # Pass the root window to the class so it can create widgets inside it
    # The __init__ method will be called automatically, setting up the entire GUI
    app = EmployeeDatabaseGUI(root)
    
    # Start the GUI event loop
    # mainloop() keeps the window open and responsive to user interactions
    # This method blocks (waits) until the window is closed or quit() is called
    # It handles all button clicks, window events, and user interactions
    root.mainloop()


# Python idiom to ensure main() only runs when script is executed directly
# If this file is imported as a module, this block won't execute
# __name__ == "__main__" is True only when the script is run directly
if __name__ == "__main__":
    main()  # Start the application