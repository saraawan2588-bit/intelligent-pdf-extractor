import streamlit as st
import os
from pathlib import Path
import pandas as pd
from pdf_extractor import IntelligentExtractor
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Page configuration
st.set_page_config(
    page_title="Intelligent PDF Extractor",
    page_icon="🔤",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .main {
        padding-top: 2rem;
    }
    .stTabs [data-baseweb="tab-list"] button {
        font-size: 18px;
    }
    </style>
    """, unsafe_allow_html=True)

# Title and description
st.title("🤖 Intelligent PDF Extractor")
st.markdown("""
Extract specific data from PDFs using **AI (Gemini or GPT-4)** that understands context and implicit information.

✨ **FREE**: Uses Google Gemini API (no credit card required!)
""")

# Sidebar
with st.sidebar:
    st.header("⚙️ Configuration")
    
    provider = st.radio(
        "Choose AI Provider",
        ["Auto-detect", "Google Gemini (FREE)", "OpenAI GPT-4"],
        help="Auto-detect will use Gemini if available, otherwise OpenAI"
    )
    
    # Determine provider and get API key
    if provider == "Google Gemini (FREE)":
        selected_provider = "gemini"
        api_key = st.text_input(
            "Google Gemini API Key",
            value=os.getenv("GEMINI_API_KEY", ""),
            type="password",
            help="Get free API key from: https://makersuite.google.com/app/apikey"
        )
        model = st.selectbox(
            "Model",
            ["gemini-pro"],
            help="Google Gemini Pro"
        )
    elif provider == "OpenAI GPT-4":
        selected_provider = "openai"
        api_key = st.text_input(
            "OpenAI API Key",
            value=os.getenv("OPENAI_API_KEY", ""),
            type="password",
            help="Your OpenAI API key"
        )
        model = st.selectbox(
            "Model",
            ["gpt-4", "gpt-3.5-turbo"],
            help="Select OpenAI model"
        )
    else:  # Auto-detect
        selected_provider = "auto"
        gemini_key = os.getenv("GEMINI_API_KEY", "")
        openai_key = os.getenv("OPENAI_API_KEY", "")
        
        if gemini_key:
            api_key = gemini_key
            st.success("✅ Using Gemini API (auto-detected)")
        elif openai_key:
            api_key = openai_key
            st.info("ℹ️ Using OpenAI API (auto-detected)")
        else:
            api_key = st.text_input(
                "API Key (Gemini or OpenAI)",
                type="password",
                help="Gemini: https://makersuite.google.com/app/apikey | OpenAI: https://platform.openai.com/api-keys"
            )
        model = "auto"
    
    temperature = st.slider(
        "Temperature",
        0.0, 1.0, 0.3,
        help="Lower = more deterministic, Higher = more creative"
    )
    
    max_tokens = st.number_input(
        "Max Tokens",
        min_value=500,
        max_value=4000,
        value=2000,
        help="Maximum tokens in AI response"
    )

# Main content
tabs = st.tabs(["📄 Single File", "📁 Batch Processing", "📚 Examples", "ℹ️ Help"])

# Tab 1: Single File Extraction
with tabs[0]:
    st.header("Extract from Single PDF")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("1. Upload PDF")
        uploaded_file = st.file_uploader(
            "Choose a PDF file",
            type="pdf",
            help="Maximum 50MB"
        )
    
    with col2:
        st.subheader("2. Define Extraction")
        extraction_instructions = st.text_area(
            "What data should be extracted?",
            placeholder="Example: Extract customer name, invoice number, total amount, and due date",
            height=100,
            help="Be specific about what information you need"
        )
    
    # Processing button
    if st.button("🚀 Extract Data", type="primary", use_container_width=True):
        if not api_key:
            st.error("❌ Please provide an API key (Gemini or OpenAI)")
        elif not uploaded_file:
            st.error("❌ Please upload a PDF file")
        elif not extraction_instructions:
            st.error("❌ Please specify what data to extract")
        else:
            try:
                # Save uploaded file temporarily
                temp_pdf_path = f"temp_{uploaded_file.name}"
                with open(temp_pdf_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())
                
                # Initialize extractor
                with st.spinner("🔄 Initializing AI..."):
                    extractor = IntelligentExtractor(
                        api_key=api_key,
                        model=model,
                        provider=selected_provider
                    )
                
                # Extract data
                with st.spinner("📖 Reading PDF and extracting data..."):
                    result_df = extractor.extract(
                        pdf_path=temp_pdf_path,
                        instructions=extraction_instructions,
                        return_format="dataframe"
                    )
                
                # Display results
                st.success("✅ Extraction completed successfully!")
                st.markdown(f"**Provider**: {extractor.provider.upper()} | **Model**: {extractor.model}")
                
                st.subheader("📊 Extracted Data")
                st.dataframe(result_df, use_container_width=True)
                
                # Download button
                csv_data = result_df.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="📥 Download as CSV",
                    data=csv_data,
                    file_name=f"extracted_{Path(uploaded_file.name).stem}.csv",
                    mime="text/csv"
                )
                
                # Excel export
                excel_path = f"extracted_{Path(uploaded_file.name).stem}.xlsx"
                extractor.to_excel(result_df, excel_path)
                
                with open(excel_path, "rb") as f:
                    st.download_button(
                        label="📥 Download as Excel",
                        data=f.read(),
                        file_name=excel_path,
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )
                
                # Cleanup
                if os.path.exists(temp_pdf_path):
                    os.remove(temp_pdf_path)
            
            except Exception as e:
                st.error(f"❌ Error during extraction: {str(e)}")
                if os.path.exists(temp_pdf_path):
                    os.remove(temp_pdf_path)

# Tab 2: Batch Processing
with tabs[1]:
    st.header("Batch Process Multiple PDFs")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("1. Upload PDFs")
        uploaded_files = st.file_uploader(
            "Choose multiple PDF files",
            type="pdf",
            accept_multiple_files=True,
            help="Select multiple PDF files to process at once"
        )
    
    with col2:
        st.subheader("2. Define Extraction")
        batch_instructions = st.text_area(
            "What data should be extracted from each PDF?",
            placeholder="Example: Extract customer name, amount, date",
            height=100
        )
    
    if st.button("🚀 Process All PDFs", type="primary", use_container_width=True):
        if not api_key:
            st.error("❌ Please provide an API key")
        elif not uploaded_files:
            st.error("❌ Please upload PDF files")
        elif not batch_instructions:
            st.error("❌ Please specify extraction instructions")
        else:
            # Save files temporarily
            temp_paths = []
            for uploaded_file in uploaded_files:
                temp_path = f"temp_{uploaded_file.name}"
                with open(temp_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())
                temp_paths.append(temp_path)
            
            try:
                with st.spinner("🔄 Initializing AI..."):
                    extractor = IntelligentExtractor(
                        api_key=api_key,
                        model=model,
                        provider=selected_provider
                    )
                
                with st.spinner(f"📖 Processing {len(temp_paths)} PDFs..."):
                    extractor.batch_extract_to_excel(
                        pdf_paths=temp_paths,
                        instructions=batch_instructions,
                        output_path="batch_extraction_results.xlsx"
                    )
                
                st.success("✅ Batch extraction completed!")
                st.markdown(f"**Provider**: {extractor.provider.upper()} | **Model**: {extractor.model}")
                
                # Read and display results
                results_df = pd.read_excel("batch_extraction_results.xlsx")
                st.subheader("📊 All Results")
                st.dataframe(results_df, use_container_width=True)
                
                # Download button
                with open("batch_extraction_results.xlsx", "rb") as f:
                    st.download_button(
                        label="📥 Download Results as Excel",
                        data=f.read(),
                        file_name="batch_extraction_results.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )
            
            except Exception as e:
                st.error(f"❌ Error during batch processing: {str(e)}")
            
            finally:
                # Cleanup
                for temp_path in temp_paths:
                    if os.path.exists(temp_path):
                        os.remove(temp_path)

# Tab 3: Examples
with tabs[2]:
    st.header("📚 Usage Examples")
    
    st.subheader("Example 1: Invoice Extraction")
    with st.expander("Click to see"):
        st.write("""
        **Extraction Instructions:**
        ```
        Extract the following from the invoice:
        - Invoice Number
        - Customer Name and Address
        - Invoice Date and Due Date
        - Item descriptions and quantities
        - Total amount
        - Payment terms
        ```
        
        This will intelligently extract invoice data even if the format varies.
        """)
    
    st.subheader("Example 2: Contract Analysis")
    with st.expander("Click to see"):
        st.write("""
        **Extraction Instructions:**
        ```
        Extract from the contract:
        - Parties involved
        - Contract effective date
        - Payment terms and schedule
        - Termination conditions
        - Key obligations of each party
        - Renewal terms
        ```
        
        The AI will understand context and extract implicit information.
        """)
    
    st.subheader("Example 3: Resume Parsing")
    with st.expander("Click to see"):
        st.write("""
        **Extraction Instructions:**
        ```
        Extract from the resume:
        - Full name and contact information
        - Professional summary
        - Key skills (list all)
        - Work experience (company, position, duration, achievements)
        - Education (degree, institution, graduation year)
        - Certifications
        ```
        """)

# Tab 4: Help
with tabs[3]:
    st.header("❓ Help & Documentation")
    
    st.subheader("🎯 Getting Started")
    st.write("""
    ### Option 1: Google Gemini (FREE - RECOMMENDED)
    1. Visit: https://makersuite.google.com/app/apikey
    2. Click "Create API Key"
    3. Copy the key and paste in the sidebar
    4. No credit card required!
    
    ### Option 2: OpenAI (Requires Payment)
    1. Visit: https://platform.openai.com/api-keys
    2. Create a new API key
    3. Paste in the sidebar
    """)
    
    st.subheader("💡 Tips for Better Extraction")
    st.write("""
    - ✅ Be specific about what you need
    - ✅ Use clear, descriptive language
    - ✅ Mention context if needed
    - ✅ For best results, use text-based PDFs (not scanned images)
    - ✅ Longer instructions = better results
    """)
    
    st.subheader("⚠️ Limitations")
    st.info("""
    - **Gemini**: Free tier, some rate limits may apply
    - **OpenAI**: API calls cost money (monitor your usage)
    - Works best with text-based PDFs
    - Large PDFs may take longer
    - Your PDF data is sent to the AI service
    """)
    
    st.subheader("🐛 Troubleshooting")
    st.write("""
    **Problem**: "Invalid API Key"
    - Double-check your API key is correct
    - Ensure you're using the right provider's key
    
    **Problem**: "Poor extraction quality"
    - Make extraction instructions more specific
    - Try breaking down complex requests
    
    **Problem**: "PDF too large"
    - Split your PDF into smaller files
    - Try with a smaller section first
    """)

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center'>
    <p>Made with ❤️ using Streamlit, LangChain & AI (Gemini/GPT-4)</p>
    <p><small>GitHub: <a href='https://github.com/saraawan2588-bit/intelligent-pdf-extractor'>intelligent-pdf-extractor</a></small></p>
    <p><small>💚 Free option available with Google Gemini API</small></p>
</div>
""", unsafe_allow_html=True)
