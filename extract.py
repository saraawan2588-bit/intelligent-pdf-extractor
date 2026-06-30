#!/usr/bin/env python3
"""
Command-line interface for Intelligent PDF Extractor

Usage:
    python extract.py --pdf input.pdf --extract "customer name, amount, date" --output output.xlsx
    python extract.py --batch *.pdf --extract "key information" --output results.xlsx
"""

import click
import os
from pathlib import Path
from pdf_extractor import IntelligentExtractor
from dotenv import load_dotenv

load_dotenv()


@click.group()
def cli():
    """Intelligent PDF Extractor CLI"""
    pass


@cli.command()
@click.option('--pdf', required=True, type=click.Path(exists=True), help='Path to PDF file')
@click.option('--extract', required=True, help='What data to extract from the PDF')
@click.option('--output', required=True, help='Output Excel file path')
@click.option('--api-key', default=None, help='OpenAI API key (uses env var if not provided)')
@click.option('--model', default='gpt-4', help='AI model to use')
def single(pdf, extract, output, api_key, model):
    """Extract data from a single PDF file"""
    
    click.echo(f"📄 PDF File: {pdf}")
    click.echo(f"🎯 Extraction: {extract}")
    click.echo(f"💾 Output: {output}")
    click.echo("-" * 50)
    
    api_key = api_key or os.getenv('OPENAI_API_KEY')
    if not api_key:
        click.echo("❌ Error: OpenAI API key not found")
        raise click.Abort()
    
    try:
        click.echo("🔄 Initializing extractor...")
        extractor = IntelligentExtractor(api_key=api_key, model=model)
        
        click.echo("📖 Extracting data...")
        result_df = extractor.extract(
            pdf_path=pdf,
            instructions=extract,
            return_format="dataframe"
        )
        
        click.echo("💾 Saving to Excel...")
        extractor.to_excel(result_df, output)
        
        click.echo("\n" + "="*50)
        click.echo("✅ Extraction completed successfully!")
        click.echo(f"📊 Results saved to: {output}")
        click.echo("="*50)
        
        # Display preview
        click.echo("\n📋 Preview of extracted data:")
        click.echo(result_df.to_string())
    
    except Exception as e:
        click.echo(f"\n❌ Error: {str(e)}", err=True)
        raise click.Abort()


@cli.command()
@click.option('--pdfs', required=True, multiple=True, type=click.Path(exists=True), help='PDF files to process')
@click.option('--extract', required=True, help='What data to extract from each PDF')
@click.option('--output', required=True, help='Output Excel file path')
@click.option('--api-key', default=None, help='OpenAI API key')
@click.option('--model', default='gpt-4', help='AI model to use')
def batch(pdfs, extract, output, api_key, model):
    """Extract data from multiple PDF files"""
    
    click.echo(f"📁 Processing {len(pdfs)} PDF files")
    click.echo(f"🎯 Extraction: {extract}")
    click.echo(f"💾 Output: {output}")
    click.echo("-" * 50)
    
    api_key = api_key or os.getenv('OPENAI_API_KEY')
    if not api_key:
        click.echo("❌ Error: OpenAI API key not found")
        raise click.Abort()
    
    try:
        click.echo("🔄 Initializing extractor...")
        extractor = IntelligentExtractor(api_key=api_key, model=model)
        
        click.echo(f"📖 Processing {len(pdfs)} PDFs...")
        
        with click.progressbar(pdfs, label='Progress') as bar:
            for pdf in bar:
                # Process each PDF (progress bar updates automatically)
                pass
        
        # Actual batch extraction
        extractor.batch_extract_to_excel(
            pdf_paths=list(pdfs),
            instructions=extract,
            output_path=output
        )
        
        click.echo("\n" + "="*50)
        click.echo(f"✅ Batch extraction completed!")
        click.echo(f"📊 Results saved to: {output}")
        click.echo(f"📁 Total PDFs processed: {len(pdfs)}")
        click.echo("="*50)
    
    except Exception as e:
        click.echo(f"\n❌ Error: {str(e)}", err=True)
        raise click.Abort()


@cli.command()
def info():
    """Show API and configuration information"""
    
    api_key = os.getenv('OPENAI_API_KEY')
    
    click.echo("\n" + "="*50)
    click.echo("Intelligent PDF Extractor - Configuration")
    click.echo("="*50)
    
    if api_key:
        masked_key = api_key[:10] + "..." + api_key[-10:]
        click.echo(f"✅ OpenAI API Key: {masked_key}")
    else:
        click.echo("❌ OpenAI API Key: NOT SET")
    
    click.echo(f"📦 Version: 1.0.0")
    click.echo(f"🤖 Default Model: gpt-4")
    click.echo("\n" + "="*50)


if __name__ == '__main__':
    cli()
