# Intelligent PDF Extractor with LangChain + GPT-4

**Extract specific data from PDFs using AI that understands context and implicit information.**

Unlike traditional PDF extraction tools, this system uses OpenAI's GPT-4 to intelligently understand document content and extract exactly what you need - even when information isn't explicitly labeled.

## 🌟 Features

✨ **AI-Powered Extraction**
- Uses GPT-4 to understand document context
- Extracts implicit information
- Handles complex, unstructured PDFs

📊 **Multiple Export Formats**
- Export to Excel (.xlsx)
- Export to CSV (.csv)
- JSON output

🎯 **Flexible Extraction**
- Define exactly what data you need
- Works with any PDF structure
- Intelligent field detection

🌐 **Multiple Interfaces**
- Web interface (Streamlit)
- Command-line interface
- Python API

📁 **Batch Processing**
- Process multiple PDFs at once
- Consolidated results in single Excel file
- Progress tracking

## 📋 What It Can Do

✅ Invoice extraction (invoice numbers, amounts, dates)  
✅ Contract analysis (parties, terms, obligations)  
✅ Resume parsing (skills, experience, education)  
✅ Form data extraction (across different formats)  
✅ Table extraction and restructuring  
✅ Any custom data extraction task  

## 🚀 Quick Start

### 1. Installation

```bash
# Clone repository
git clone https://github.com/saraawan2588-bit/intelligent-pdf-extractor.git
cd intelligent-pdf-extractor

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure API Key

```bash
# Copy example environment file
cp .env.example .env

# Edit .env and add your OpenAI API key
OPENAI_API_KEY=sk-your-api-key-here
```

Get your API key from: https://platform.openai.com/api-keys

### 3. Run Web Interface

```bash
streamlit run app.py
```

Then open `http://localhost:8501` in your browser.

### 4. Or Use CLI

```bash
# Single PDF
python extract.py single --pdf invoice.pdf --extract "invoice number, total amount, due date" --output result.xlsx

# Batch processing
python extract.py batch --pdfs *.pdf --extract "customer name, amount" --output results.xlsx
```

## 💻 Usage Examples

### Example 1: Using Web Interface

1. Open Streamlit app
2. Enter your OpenAI API key in the sidebar
3. Upload a PDF
4. Specify what to extract: `"Extract customer name, invoice number, and total amount"`
5. Click "Extract Data"
6. Download results as CSV or Excel

### Example 2: Using Python API

```python
from pdf_extractor import IntelligentExtractor

# Initialize extractor
extractor = IntelligentExtractor(api_key="sk-your-key")

# Extract from single PDF
data = extractor.extract(
    pdf_path="invoice.pdf",
    instructions="Extract invoice number, customer name, and total amount"
)

# Export to Excel
extractor.to_excel(data, "output.xlsx")
```

### Example 3: Batch Processing

```python
# Extract from multiple PDFs
results = extractor.batch_extract(
    pdf_paths=["invoice1.pdf", "invoice2.pdf", "invoice3.pdf"],
    instructions="Extract invoice number, amount, and date"
)

# Save all results to Excel
extractor.batch_extract_to_excel(
    pdf_paths=["invoice1.pdf", "invoice2.pdf"],
    instructions="Extract invoice number, amount, date",
    output_path="all_invoices.xlsx"
)
```

### Example 4: Using CLI

```bash
# Show information
python extract.py info

# Extract from single PDF
python extract.py single \
  --pdf contract.pdf \
  --extract "Extract parties, effective date, and termination clause" \
  --output contract_data.xlsx

# Batch extract
python extract.py batch \
  --pdfs resumes/*.pdf \
  --extract "Extract name, email, skills, and experience" \
  --output candidates.xlsx
```

## 📁 Project Structure

```
intelligent-pdf-extractor/
├── app.py                    # Streamlit web interface
├── extract.py               # CLI interface
├── pdf_extractor.py         # Core extraction logic
├── utils.py                 # Utility functions
├── requirements.txt         # Python dependencies
├── .env.example            # Environment template
├── config.yaml             # Configuration file
└── README.md               # This file
```

## ⚙️ Configuration

Edit `config.yaml` to customize behavior:

```yaml
extraction:
  model: "gpt-4"              # AI model to use
  temperature: 0.3            # 0=deterministic, 1=creative
  max_tokens: 2000            # Max response length
  timeout: 300                # Timeout in seconds

pdf:
  max_pages: 50               # Max pages to process
  max_file_size: 50           # Max file size in MB

excel:
  format: "xlsx"
  include_confidence: true    # Add confidence scores
```

## 🔑 API Reference

### IntelligentExtractor Class

```python
from pdf_extractor import IntelligentExtractor

# Initialize
extractor = IntelligentExtractor(
    api_key="sk-...",      # OpenAI API key
    model="gpt-4"          # Model to use
)

# Extract from single PDF
data = extractor.extract(
    pdf_path="file.pdf",           # PDF file path
    instructions="Extract...",     # What to extract
    return_format="dataframe"      # 'dataframe' or 'dict'
)

# Extract from multiple PDFs
results = extractor.batch_extract(
    pdf_paths=["file1.pdf", "file2.pdf"],  # List of PDFs
    instructions="Extract..."
)

# Save to Excel
extractor.to_excel(
    data=data_or_dataframe,
    output_path="output.xlsx"
)

# Batch extract and save
extractor.batch_extract_to_excel(
    pdf_paths=[...],
    instructions="Extract...",
    output_path="results.xlsx"
)
```

## 💡 Tips for Better Extraction

✅ **Be Specific** - "Extract invoice number, customer name, and total amount" works better than "Extract invoice data"  
✅ **Use Examples** - "Extract dates in format MM/DD/YYYY" gives better results  
✅ **Mention Format** - "Extract price as number only (no currency symbol)"  
✅ **Text-Based PDFs** - Works best with PDFs created from documents, not scanned images  
✅ **Clear Instructions** - The more detail, the better the extraction  

## ⚠️ Limitations

🚫 **API Costs** - Each extraction uses OpenAI API credits (monitor your usage)  
🚫 **Scanned PDFs** - May require additional OCR setup for image-based documents  
🚫 **Large Files** - Very large PDFs may exceed token limits  
🚫 **Privacy** - PDFs are sent to OpenAI servers  
🚫 **Text-Based Only** - Works best with extractable text (not scanned images without OCR)  

## 🐛 Troubleshooting

### "Invalid API Key" Error

```bash
# Check your .env file has correct format
OPENAI_API_KEY=sk-xxxxxxxxxx (must start with sk-)

# Verify at https://platform.openai.com/api-keys
```

### "Poor Extraction Quality"

- Make extraction instructions more specific
- Try breaking down complex requests
- Provide examples of expected format
- Check that your PDF has selectable text (not scanned image)

### "PDF Too Large / Timeout"

- Split large PDF into smaller files
- Reduce max_tokens in config.yaml
- Try with a single page first

### "No Data Extracted"

- Check that extraction instructions match your PDF content
- Verify PDF is not corrupted or empty
- Try uploading a different PDF to test

## 📊 Performance

- **Single page PDF**: 2-5 seconds  
- **5-10 page PDF**: 10-30 seconds  
- **50+ page PDF**: 1-3 minutes (may need to split)  

Times vary based on content complexity and API response times.

## 🔐 Security

⚠️ **Important**: Your PDFs are sent to OpenAI's API servers. Don't use with:
- Highly confidential documents
- Personal/financial information you want to keep private
- Protected/proprietary documents

## 🤝 Contributing

Contributions welcome! Please:

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/improvement`
3. Make your changes
4. Commit: `git commit -am 'Add improvement'`
5. Push: `git push origin feature/improvement`
6. Open a Pull Request

## 📄 License

MIT License - see LICENSE file

## 🙏 Acknowledgments

- [LangChain](https://github.com/langchain-ai/langchain) - LLM framework
- [OpenAI GPT-4](https://openai.com/gpt-4/) - AI model
- [Streamlit](https://streamlit.io/) - Web framework
- [pdfplumber](https://github.com/jsvine/pdfplumber) - PDF parsing

## 📞 Support

- 📖 [Documentation](./README.md)
- 🐛 [Issues](https://github.com/saraawan2588-bit/intelligent-pdf-extractor/issues)
- 💬 [Discussions](https://github.com/saraawan2588-bit/intelligent-pdf-extractor/discussions)

---

**⭐ If you find this helpful, please star the repository!**

Made with ❤️ using LangChain, GPT-4, and Streamlit
