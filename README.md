HR Analytics & Employee Attrition Dashboard Project Overview This project is an interactive web dashboard designed for an HR department to analyze and visualize employee data from the IBM HR Analytics dataset.

It provides key insights into employee demographics, job roles, performance, and attrition.
The dashboard allows for dynamic filtering and includes forms to add new employees or update existing records directly in the database.


Core Technologies Used: 


-Python: For data manipulation and backend logic.

Streamlit: To build and serve the interactive web dashboard.

-Pandas: For data loading, cleaning, and analysis.

-Plotly Express: For creating interactive data visualizations.

-SQLite: As the lightweight, file-based database.

Key FeaturesInteractive Visualizations: Includes multiple charts (bar, pie, scatter plot) that update based on user selections.

Key Performance Indicators: Displays essential metrics like total employees, average income, and attrition rate.


Filter by Department: A dropdown menu in the sidebar allows users to filter the entire dashboard by department.

Add New Employee: A form to add a new employee record to the database.

Update Employee Income: A form to select an existing employee and update their monthly income.

Custom User Interface: A custom-themed interface with a gradient sidebar and coordinated chart colors.

Setup and Installation: Follow these steps to set up the project environment and run the dashboard locally

Prerequisites:

      -Python 3.9+  

      -Conda package manager1.   

Clone the Repository First, clone this repository to your local machine:


    git clone [https://github.com/your-username/hr-analytics-dashboard.git](https://github.com/your-username/hr-analytics-dashboard.git)

    cd hr-analytics-dashboard

 Set Up the Conda Environment & Activate your existing  conda environment:
  
     conda activate [replace with your environment name]

 Install Required Libraries: Install all necessary packages using the requirements.txt file.


This is the fastest way to install everything the project needs.

        pip install -r requirements.txt    

How to Run the Application: The application requires a two-step launch process.

Step 1: Create the DatabaseRun the setup script once to process the raw CSV data and create the SQLite database (hr_database.db).

    python setup_database.py

You should see a message confirming that the database and table were created successfully.

Step 2: Launch the Streamlit Dashboard: Start the Streamlit web server to launch the interactive dashboard.

    streamlit run app.py

The application will automatically open in a new tab in your web browser.

Project File StructureHere is an overview of the key files in this project:hr-analytics-dashboard/

    │    

    ├── WA_Fn-UseC_-HR-Employee-Attrition.csv    # The original, raw dataset.

    ├── setup_database.py                        # Script to clean data and create the SQLite DB.

    ├── app.py                                   # The main Streamlit application script.

    ├── hr_database.db                           # The SQLite database file (created by setup_database.py).

    ├── requirements.txt                         # A list of all required Python libraries.

    └── README.md                                # This instruction and documentation file.




Dataset InformationThis project uses the "IBM HR Analytics Employee Attrition & Performance" dataset.

Source: Kaggle

File Used: WA_Fn-UseC_-HR-Employee-Attrition.csv
