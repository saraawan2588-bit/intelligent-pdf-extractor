# Windows Installation & Troubleshooting Guide

## Quick Fix for Common Issues

### Issue 1: Pandas Installation Error on Windows

**Error:**
```
ERROR: Could not find C:\Program Files (x86)\Microsoft Visual Studio\Installer\vswhere.exe
```

**Solution:**
```bash
# The requirements.txt already handles this with flexible versions
pip install -r requirements.txt --upgrade

# If still issues, upgrade pip first
python -m pip install --upgrade pip
pip install -r requirements.txt
```

---

### Issue 2: Gemini Model Error (gemini-pro not found)

**Error:**
```
404 models/gemini-pro is not found for API version v1beta
```

**Solution:**
The code now uses the latest `gemini-1.5-pro` model. Just update:

```bash
pip install --upgrade google-generativeai langchain-google-genai
```

---

### Issue 3: Import Errors

**Error:**
```
ModuleNotFoundError: No module named 'langchain_google_genai'
```

**Solution:**
```bash
pip install langchain-google-genai google-generativeai
```

---

## Complete Windows Setup (Step by Step)

### Step 1: Create Virtual Environment
```bash
cd intelligent-pdf-extractor
python -m venv venv
venv\Scripts\activate
```

### Step 2: Upgrade pip
```bash
python -m pip install --upgrade pip
```

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

If you get pandas errors, try:
```bash
pip install pandas openpyxl --upgrade
pip install -r requirements.txt
```

### Step 4: Set Up API Key

**Get Free Gemini API Key:**
1. Go to: https://makersuite.google.com/app/apikey
2. Click "Create API Key"
3. Copy the key
4. Create `.env` file:
   ```
   GEMINI_API_KEY=your-key-here
   ```

### Step 5: Run the Application

```bash
streamlit run app.py
```

Then open: `http://localhost:8501`

---

## Verify Installation

```bash
# Test if all packages installed correctly
python -c "import streamlit, pandas, pdfplumber, langchain; print('✅ All packages installed!')"

# Test Gemini
python -c "from langchain_google_genai import ChatGoogleGenerativeAI; print('✅ Gemini available!')"
```

---

## Still Having Issues?

### Clean Reinstall

```bash
# Remove virtual environment
rmdir /s venv

# Create fresh environment
python -m venv venv
venv\Scripts\activate

# Upgrade pip
python -m pip install --upgrade pip setuptools wheel

# Install all requirements
pip install -r requirements.txt
```

### Try Individual Package Installation

```bash
pip install langchain
pip install langchain-google-genai
pip install google-generativeai
pip install python-dotenv
pip install pdfplumber
pip install pandas
pip install openpyxl
pip install streamlit
```

---

## Windows Specific Notes

✅ Use `venv\Scripts\activate` (not `source venv/bin/activate`)  
✅ Use backslashes for paths: `C:\Users\...`  
✅ Make sure PowerShell execution policy allows scripts:  
   ```powershell
   Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
   ```

---

## API Key Troubleshooting

### Gemini API Key Issues

1. **Key not found:**
   - Make sure `.env` file exists in project root
   - Check key is correct: `GEMINI_API_KEY=your-key`

2. **API quota exceeded:**
   - Free tier has usage limits
   - Wait a bit or create new key

3. **Invalid API key error:**
   - Copy key directly from https://makersuite.google.com/app/apikey
   - Don't add extra spaces

---

## Performance Tips

- Small PDFs (1-2 pages): ~2-5 seconds ⚡
- Medium PDFs (5-10 pages): ~10-30 seconds ⏱️
- Large PDFs (50+ pages): Split into smaller files for better results 📚

---

## What's New

✅ Uses latest Gemini model (gemini-1.5-pro)  
✅ Windows-compatible dependencies  
✅ Better error messages  
✅ Auto-detects API provider  
✅ Fallback from Gemini to OpenAI  

---

Need more help? Check the main [README.md](README.md)
