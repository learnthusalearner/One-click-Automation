# How to Run One-Click Social Poster

Follow these steps to run both the FastAPI backend and the React frontend.

## Prerequisites
1. Make sure you have **Python 3.10+** and **NodeJS 18+** installed.
2. Fill in your credentials inside `backend/.env` (copy `backend/.env.example` to `backend/.env` if not done already).

---

## Step 1: Run the Backend API

1. Open a terminal (PowerShell or Command Prompt) and navigate to the project folder:
   ```powershell
   cd "c:\Users\KIIT\Desktop\New folder (3)\One-Click-Automation"
   ```
2. Activate the virtual environment:
   * **PowerShell**:
     ```powershell
     .\venv\Scripts\Activate.ps1
     ```
   * **Command Prompt**:
     ```cmd
     .\venv\Scripts\activate.bat
     ```
3. Start the FastAPI backend server with Uvicorn:
   ```powershell
   uvicorn backend.app:app --reload --port 8000
   ```
   *The backend will be running at [http://localhost:8000](http://localhost:8000).*

---

## Step 2: Run the React Frontend

1. Open a **new** terminal window and navigate to the `frontend` folder:
   ```powershell
   cd "c:\Users\KIIT\Desktop\New folder (3)\One-Click-Automation\frontend"
   ```
2. Run the Vite development server:
   ```powershell
   npm run dev
   ```
3. Open your browser and navigate to the URL shown in the console (usually [http://localhost:5173](http://localhost:5173)).

---

## API Endpoints Reference

* **Connection Status Check**: `GET http://localhost:8000/api/config`
* **Publish Social Media Post**: `POST http://localhost:8000/api/post` (Accepts multipart/form-data with fields: `caption`, `platforms`, optional `image_url` or file upload `image`).
