# How to Run Autoposter

Follow these steps to run the script and post to your social media platforms.

## Step 1: Open Terminal and Navigate to the Project Folder
Open PowerShell or your command prompt and navigate to the `autoposter` directory:
```powershell
cd "c:\Users\KIIT\Desktop\New folder (3)\One-Click-Automation\autoposter"
```

## Step 2: Activate the Virtual Environment (If using one)
If you are using a Python virtual environment, activate it:
* **PowerShell**:
  ```powershell
  .venv\Scripts\Activate.ps1
  ```
* **Command Prompt**:
  ```cmd
  .venv\Scripts\activate.bat
  ```

## Step 3: Check Configuration
Before posting, check if your `.env` variables are loaded and recognized by running:
```powershell
$env:PYTHONIOENCODING="utf-8"
python main.py check-config
```

## Step 4: Post Content
Put your image (JPEG or PNG) into the `post` directory and run the command:

### Standard Command:
```powershell
$env:PYTHONIOENCODING="utf-8"
python main.py post --image post/3.png --description "First Automated post"
```

*Replace `post/3.png` with the actual path to your image, and `"First Automated post"` with the caption you want to publish.*

---

## Troubleshooting & Common Errors

### Error: `ModuleNotFoundError: No module named 'platforms.instagram'`
* **Why this happened**: The file `instagram.py` was deleted or missing from your `platforms` folder. When `main.py` tried to run, it couldn't find the Instagram code.
* **How it was fixed**: We restored the `platforms/instagram.py` file. If this happens again, make sure `instagram.py` is present in the `platforms` folder.

### Error: `Invalid value for '--image': Path 'post/3.png' does not exist`
* **Why this happens**: The image file name is not exactly `3.png` inside the `post` folder, or the file is missing.
* **How to fix**: Run `dir post` to see the exact name of the file inside your `post` folder, and write that filename in the `--image` argument.
