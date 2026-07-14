# IQAC Quality Assurance Platform - Administrator & Local Deployment Guide

This document explains the new administrative features added to the DLBC IQA Tool and provides step-by-step instructions for deploying the updated application on a local server.

---

## Part 1: New Administrator Features

The application has been updated to give the system administrator complete control over departments, committees, and reporting forms. All changes are stored securely in the database and propagate to forms, dropdowns, and dashboards instantly without requiring code modifications.

### 1. Tabbed Form Section Management
- **Location**: Go to the sidebar menu, under **System** -> **Manage Form Sections**.
- **Usage**:
  - The page now features two tabs: **Department Forms** and **Committee Forms**.
  - **Department Forms** controls the standard reporting sections (1–22) for academic departments.
  - **Committee Forms** controls the meeting reporting sections (101–104) for committees.
  - Click the **Edit (✏️)** button next to any section to rename it. 
  - Click **Delete (🗑️)** to remove it from all corresponding forms.
  - Click **+ Add New Section** at the top right of the page to add a new question/section.

### 2. Manage Committees & Departments
- **Location**: Go to the sidebar menu, under **System** -> **Manage Org Units**.
- **Usage**:
  - **Manage Academic Departments**: Lists all active academic departments. Click **+ Add Department** to introduce a new one (enter a Code like `IT` and Name like `Information Technology`). You can also edit names or delete departments.
  - **Manage Committees**: Lists all active committees (e.g., SC/ST Committee, R&D). Click **+ Add Committee** to add a new one. You can remove any committee by clicking the **Delete (🗑️)** icon.

### 3. Dynamic Real-Time Dashboards
- When you add, edit, or delete a department, committee, or section, all changes propagate instantly.
- The **Admin Dashboard** automatically updates its KPIs, performance grids, and the Campus Placement Rate overview to reflect the current list of departments and committees.
- Dropdowns for users when submitting monthly reports will dynamically load the updated list of departments and committees.

---

## Part 2: Local Server Deployment Guide

To deploy the application and the new features on a local server (e.g., a Windows or Linux machine in your local network), follow these instructions:

### Prerequisites
Make sure the local server has the following installed:
1. **Python (version 3.9 or higher)**
2. **PostgreSQL Database Server**

---

### Step 1: Database Setup

1. Open your PostgreSQL administration tool (e.g., pgAdmin or psql shell).
2. Create a new database for the application (e.g., `iqac_db`).
3. Restore the database structure and data using the SQL dump file provided in the project folder:
   - Run the following command in your terminal/command prompt:
     ```bash
     psql -U postgres -d iqac_db -f "IQAC DATABASE.sql"
     ```
     *(Replace `postgres` with your PostgreSQL username if it is different).*

---

### Step 2: Environment Configuration

The application uses an environment configuration file to securely connect to the database.
1. Open the project root folder.
2. Edit the `.env` file to point to your local PostgreSQL instance:
   ```env
   DATABASE_URL="postgresql://<username>:<password>@localhost:5432/iqac_db"
   SECRET_KEY="ChooseAStrongRandomStringHere"
   ```
   - Replace `<username>` and `<password>` with your actual PostgreSQL credentials.
   - If your database is hosted on a different machine in the local network, replace `localhost` with its IP address.

---

### Step 3: Python Environment & Dependency Installation

1. Open your terminal or Command Prompt in the project directory.
2. Create a virtual environment (optional but recommended):
   ```bash
   python -m venv venv
   ```
3. Activate the virtual environment:
   - **Windows**:
     ```cmd
     venv\Scripts\activate
     ```
   - **Linux/macOS**:
     ```bash
     source venv/bin/activate
     ```
4. Install all required packages:
   ```bash
   pip install -r requirements.txt
   ```

---

### Step 4: Running the Local Server

#### A. For Development/Testing
To start the Flask development server, run:
```bash
python app.py
```
By default, the server runs on `http://127.0.0.1:5000`. You can access it in your web browser.

#### B. For Production-grade Local Hosting (Recommended)
Since Flask's built-in server is not meant for production traffic, you should run it behind a WSGI server on the local machine:

- **For Windows Servers (using Waitress)**:
  1. Install Waitress:
     ```bash
     pip install waitress
     ```
  2. Run the application:
     ```bash
     waitress-serve --host=0.0.0.0 --port=8080 app:app
     ```
- **For Linux Servers (using Gunicorn)**:
  1. Run the application:
     ```bash
     gunicorn --bind 0.0.0.0:8080 app:app
     ```

Using host `0.0.0.0` ensures the server is reachable by other computers on the same local area network (LAN) using the server's IP address (e.g., `http://192.168.1.50:8080`).

---

### Verification
When the server starts:
1. It automatically runs a check to create the new tables (`departments` and `committees`) and populate the default records if they are empty.
2. Check the command line output. If it outputs `Database initialized successfully.`, the database is correctly connected and updated!
