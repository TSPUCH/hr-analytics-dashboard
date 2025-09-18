# =====================================================================================
#
#  Database Setup Script
#
#  Purpose: This script is designed to be run only ONCE. Its job is to:
#           1. Read the raw employee data from the CSV file.
#           2. Clean up the column names to make them database-friendly.
#           3. Create a new, clean SQLite database file.
#           4. Load the cleaned data into a table inside that database.
#
# =====================================================================================

# --- Step 1: Import Necessary Libraries ---
# We need a few tools to make this script work.
#
# pandas: This is the most popular library in Python for working with data.
#         We use it to read the CSV file and handle the data like a spreadsheet.
#
# sqlite3: This library lets Python talk to SQLite databases. We use it to
#          verify that our data was inserted correctly.
#
# sqlalchemy: This is a powerful library that helps pandas write data
#             directly into a SQL database. It's the engine that connects
#             our pandas DataFrame to our SQLite database.
#
# re: This is Python's "regular expressions" library. It's a tool for
#     finding and replacing patterns in text, which we use for cleaning
#     our column names.
#
import pandas as pd
import sqlite3
from sqlalchemy import create_engine
import re

# --- Step 2: Configuration Settings ---
# We put all our filenames and settings here at the top. This makes it
# easy to change them later without having to hunt through the code.
#
CSV_FILE_PATH = 'WA_Fn-UseC_-HR-Employee-Attrition.csv'     # The name of the raw data file.
DB_FILE_PATH = 'hr_database.db'                             # The name of the database file we will create.
TABLE_NAME = 'employees'                                    # The name of the table inside our database.

# --- Step 3: Define a Helper Function for Cleaning ---
# This function's job is to clean up the column names from the CSV file.
# Database table columns can't have spaces or weird symbols, so we fix that here.
#
def clean_col_names(df):
    """
    Cleans the column names of a pandas DataFrame to be safe for a database.
    For example, a column named "Monthly Income ($)" would become "MonthlyIncome".
    """
    # Get the current list of column names ↓
    cols = df.columns
    # Create an empty list to hold the new, cleaned column names
    new_cols = []
    # Loop through each column name one by one
    for col in cols:
        # Use a regular expression (re.sub) to remove any character that is NOT
        # a number, a letter, or an underscore.
        new_col = re.sub(r'[^0-9a-zA-Z_]', '', col)
        # Check if the column name is not empty after cleaning ↓
        if new_col:
            # If it's not empty, add it to our list of new columns ↓
            new_cols.append(new_col)
    # Replace the old column names in the DataFrame with our new, clean list ↓
    df.columns = new_cols
    # Return the DataFrame with the cleaned column names ↓
    return df

# --- Step 4: Define the Main Function for Setting Up the Database ---
# This is the main function that does all the heavy lifting. It calls our
# cleaning function and performs all the steps in order.
#
def setup_database():
    """
    This is the main function that reads data from the CSV, cleans it,
    and then loads it all into a brand new SQLite database file.
    """
    # The "try...except" block is for error handling.
    # It will "try" to run the code inside. If any error happens, لا سمح الله
    # it will jump to the "except" block and print a helpful message
    # instead of just crashing. :D
    try:
        # --- Task 1: Load the Dataset from the CSV File ---
        print(f"Loading data from '{CSV_FILE_PATH}'...")
        # pd.read_csv() is the pandas function that reads our CSV file.
        # The data is loaded into a variable called 'df' (short for DataFrame).
        df = pd.read_csv(CSV_FILE_PATH)
        print("Data loaded successfully.")

        # --- Task 2: Add a Unique ID ---
        # It's good practice for every row in a database table to have a unique ID.
        # We check if an 'EmployeeID' column already exists. If not, we create one.
        if 'EmployeeID' not in df.columns:
            # df.insert() adds a new column at a specific position.
            # We add it at the beginning (position 0).
            df.insert(0, 'EmployeeID', range(1, 1 + len(df)))
        
        # --- NEW DATA CLEANING STEP ---
        # Here we handle missing values in the data itself before saving to the database.
        # For 'YearsAtCompany', we will fill any missing values (NaN) with the median of the column.
        if 'YearsAtCompany' in df.columns and df['YearsAtCompany'].isnull().any():
            median_years = df['YearsAtCompany'].median()
            df['YearsAtCompany'].fillna(median_years, inplace=True)
            print(f"Missing 'YearsAtCompany' values filled with median value: {median_years}")

        # --- Task 3: Clean the Column Names ---
        # Here we call our helper function from Step 3 to clean up the column names.
        df = clean_col_names(df)
        print("Column names cleaned.")

        # --- Task 4: Connect to the Database ---
        # We create a database "engine". Think of this as the connection pipeline
        # that allows pandas to talk to our SQLite database file.  
        engine = create_engine(f'sqlite:///{DB_FILE_PATH}')
        print(f"Connecting to database '{DB_FILE_PATH}'...")

        # --- Task 5: Insert Data into the Database Table ---
        # This takes all the data from our DataFrame and writes it to a SQL table.
        df.to_sql(TABLE_NAME, engine, if_exists='replace', index=False)
        print(f"Data successfully inserted into '{TABLE_NAME}' table.")

        # --- Task 6: Verify Everything Worked ---
        # To be extra sure, we will connect to the database directly and count the rows.
        # First, we establish a connection.
        conn = sqlite3.connect(DB_FILE_PATH)
        # A "cursor" is an object that lets you execute SQL commands.
        cursor = conn.cursor()
        # We execute a simple SQL query to count all rows (*) in our table.
        cursor.execute(f"SELECT COUNT(*) FROM {TABLE_NAME}")
        # cursor.fetchone() fetches the first (and in this case, only) result.
        # The [0] gets the actual number from the result.
        count = cursor.fetchone()[0]
        # It's very important to close the connection when you're done. ;)
        conn.close()
        # Finally, we print a success message with the number of records we found.
        print(f"Verification: Found {count} records in '{TABLE_NAME}' table.")
        print("\nDatabase setup is complete! You can now run the 'app.py' file.")

    # This 'except' block will catch the error if the CSV file is missing.
    except FileNotFoundError:
        print(f"Error: The file '{CSV_FILE_PATH}' was not found.")
        print("Please make sure you have downloaded it from Kaggle and placed it in the same folder as this script.")
    # This 'except' block will catch any other unexpected errors that might happen. o7
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

# --- Step 5: Run the Main Function ---
# This is a standard Python practice. The line below checks if the script is
# being run directly (and not imported by another script). If it is, then it
# will call our main setup_database() function to kick everything off.
#
if __name__ == '__main__':
    setup_database()


