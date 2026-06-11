# Run Backend

Follow these steps to run the FastAPI backend.

## Prerequisites
1. Make sure you have **Python 3.10+** installed.
2. Fill in your credentials inside `.env` (copy `.env.example` to `.env` if not done already).

---

## Run the Backend API Server

1. Open a terminal (PowerShell or Command Prompt) and navigate to the `backend` folder:
   ```powershell
   cd "c:\Users\KIIT\Desktop\New folder (3)\One-Click-Automation\backend"
   ```
2. Activate the virtual environment (if using one):
   * **PowerShell**:
     ```powershell
     ..\venv\Scripts\Activate.ps1
     ```
   * **Command Prompt**:
     ```cmd
     ..\venv\Scripts\activate.bat
     ```
3. Start the FastAPI backend server with Uvicorn:
   ```powershell
   uvicorn app:app --reload --port 8000
   ```
   *(Alternatively: `python main.py serve`)*
   
   *The backend will be running at [http://localhost:8000](http://localhost:8000).*

---

## Run via Command Line Interface (CLI)

#### Post to all platforms (one-click)

```bash
python main.py post \
  --image photo.jpg \
  --description "Just launched our new product — months of work finally live!"
```

Or with short options:

```bash
python main.py post -i photo.jpg -d "Your caption here"
```

---

## API Endpoints Reference

* **Connection Status Check**: `GET http://localhost:8000/api/config`
* **Publish Social Media Post**: `POST http://localhost:8000/api/post` (Accepts multipart/form-data with fields: `caption`, `platforms`, optional `image_url` or file upload `image`).
