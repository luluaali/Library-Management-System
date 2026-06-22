# Library Management System

A simple Python-based Library Management System developed to manage books, members, and borrowing/return operations using file and CSV handling.

## Features

- Add and view books
- Add and manage members
- Issue books to members
- Return borrowed books
- Store records using CSV files
- Validate basic user input and record operations
- Track transactions and returned books
- View library data through a Gradio-based interface

## Technologies Used

- Python
- Gradio
- Pandas
- CSV / File Handling

## Project Purpose

This project was built to practice core Python programming concepts such as functions, control flow, data handling, validation logic, and file management through a real-world library management system.

## Project Files

- `library_management_system.py` - Main Python application file
- `Library_Books_Collection.csv` - Stores book records
- `Library_Members.csv` - Stores member records
- `transactions.csv` - Stores issued book transactions
- `returns.csv` - Stores returned book records

## How to Run

1. Make sure Python is installed on your system.
2. Clone or download this repository.
3. Open the project folder in VS Code, PyCharm, or terminal.
4. Install the required libraries:

```bash
pip install gradio pandas
```

5. Run the program:

```bash
python library_management_system.py
```

6. Open the local Gradio link shown in the terminal or browser to use the application.

Gradio apps are run as Python scripts, and good README practice is to show exact install and run commands in fenced code blocks. [web:78][web:81][web:94]

## Usage

Use the system to:

- Add and manage book records
- Add and manage member records
- Issue books to members
- Return books and update availability
- Track issued and returned transactions
- View records and reports through the interface

## Data Storage

This project uses CSV files to store and manage data. The CSV files act as a lightweight storage solution for books, members, transactions, and returns.

## Future Improvements

- Add search and sorting options
- Improve validation and error handling
- Add due-date reminders and advanced fine calculations
- Move storage from CSV files to SQLite or another database
- Add authentication for admin access
- Improve the interface design and reporting features

## Author

**LULUA CHAKKIWALA**  
BCA in Artificial Intelligence  
Symbiosis International University, Dubai
