# Fannie Mae Knowledge Base & PDF to JSONL Converter

A comprehensive collection of tools and datasets for extracting, converting, and organizing Fannie Mae mortgage industry knowledge into machine-learning ready formats.

## 📋 Overview

This repository contains:
- **PDF to JSONL conversion tools** for extracting instruction-output pairs from documents
- **Web crawling utilities** for systematically extracting content from Fannie Mae websites
- **Complete Fannie Mae knowledge base** with 248+ instruction-output pairs
- **Multiple specialized datasets** covering different aspects of mortgage lending

## 🗂️ Repository Contents

### 📄 Core Scripts

| Script | Purpose | Usage |
|--------|---------|-------|
| `pdf_to_jsonl.py` | Convert PDFs to JSONL with Claude Haiku | `python pdf_to_jsonl.py document.pdf` |
| `pdf_to_jsonl_fast.py` | Fast PDF conversion using pattern matching | `python pdf_to_jsonl_fast.py doc.pdf --start 50 --end 100` |
| `crawl_selling_guide.py` | Extract content from Selling Guide website | `python crawl_selling_guide.py` |
| `fannie_mae_comprehensive_crawler.py` | Complete website content extraction | `python fannie_mae_comprehensive_crawler.py` |

### 📊 Knowledge Base Files

| File | Entries | Description |
|------|---------|-------------|
| `fannie_mae_complete_knowledge_base.jsonl` | **248** | 🎯 **Complete knowledge base** - All Fannie Mae content |
| `fannie_glossary.jsonl` | 71 | General mortgage/real estate terminology |
| `fannie_multifamily_attributes.jsonl` | 25 | Multifamily loan data attributes |
| `fannie_single_family_glossary.jsonl` | 45 | Single-family loan performance terms |
| `fannie_selling_guide_complete.jsonl` | 50 | Selling Guide policies and procedures |

### 🛠️ Utility Scripts

| Script | Purpose |
|--------|---------|
| `parse_fannie_attributes.py` | Extract structured data from Fannie Mae PDFs |
| `extract_fannie_single_family.py` | Process single-family loan performance data |
| `compile_fannie_mae_knowledge.py` | Merge and deduplicate all knowledge sources |

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip install PyPDF2 anthropic beautifulsoup4 requests
```

### 2. Convert PDF to JSONL
```bash
# Using pattern matching (no API key required)
python pdf_to_jsonl_fast.py document.pdf

# Using Claude Haiku (requires ANTHROPIC_API_KEY)
export ANTHROPIC_API_KEY="your-key-here"
python pdf_to_jsonl.py document.pdf
```

### 3. Use the Complete Knowledge Base
```python
import json

# Load the complete Fannie Mae knowledge base
with open('fannie_mae_complete_knowledge_base.jsonl', 'r') as f:
    knowledge_base = []
    for line in f:
        knowledge_base.append(json.loads(line))

# Example: Find definitions
definitions = [item for item in knowledge_base 
               if item['instruction'].startswith('What is')]
print(f"Found {len(definitions)} definitions")
```

## 📈 Knowledge Base Statistics

### Content Distribution
- **Definitions**: 180 entries (72.6%)
- **Requirements**: 18 entries (7.3%)
- **General Knowledge**: 45 entries (18.1%)
- **Products**: 5 entries (2.0%)

### Coverage Areas
- ✅ **Company Information** - History, mission, operations
- ✅ **Single-Family Business** - Products, technology, guidelines
- ✅ **Multifamily Business** - Financing, green lending, affordable housing
- ✅ **Consumer Resources** - Tools, calculators, education
- ✅ **Capital Markets** - MBS, CRT, structured transactions
- ✅ **Research & Insights** - Market analysis, housing trends
- ✅ **Regulatory & Compliance** - FHFA, housing goals, policies

## 🎯 Use Cases

### 🤖 AI Training
- **Fine-tune language models** on mortgage industry expertise
- **Create chatbots** with Fannie Mae knowledge
- **Build Q&A systems** for housing professionals

### 📚 Education & Training
- **Mortgage industry training** materials
- **Housing counselor** education resources
- **Real estate professional** reference guides

### 💼 Business Applications
- **Customer service** automation
- **Policy compliance** checking
- **Document processing** workflows

## 📖 Data Format

All JSONL files follow this consistent format:
```json
{
  "instruction": "What is a conventional loan?",
  "output": "A mortgage loan not insured or guaranteed by the federal government, typically requiring higher credit scores and down payments than government loans."
}
```

## 🔧 Advanced Usage

### Custom PDF Processing
```bash
# Process specific page ranges
python pdf_to_jsonl_fast.py large_document.pdf --start 100 --end 200

# Custom output location
python pdf_to_jsonl.py document.pdf -o custom_output.jsonl
```

### Web Content Extraction
```python
# Extract from specific Fannie Mae sections
from crawl_selling_guide import SellingGuideCrawler

crawler = SellingGuideCrawler()
content = crawler.extract_content_from_page("https://selling-guide.fanniemae.com/...")
```

## 📚 Key Knowledge Areas Covered

### Mortgage Products
- HomeReady (low down payment mortgages)
- RefiNow (refinancing options)
- HomeStyle (renovation financing)
- MH Advantage (manufactured housing)
- HomeStyle Energy (energy-efficient upgrades)

### Technology Solutions
- Desktop Underwriter (DU)
- Collateral Underwriter
- Day 1 Certainty
- Fannie Mae Connect
- Servicing Marketplace

### Business Operations
- Loan origination processes
- Underwriting guidelines
- Quality control requirements
- Servicing standards
- Risk management

## 🌟 Data Quality Features

- **Deduplication**: Automatic removal of duplicate entries
- **Validation**: Content length and quality checks
- **Formatting**: Consistent instruction-output structure
- **Categorization**: Organized by topic and complexity
- **Completeness**: Comprehensive coverage of Fannie Mae ecosystem

## 🤝 Contributing

1. **Add new data sources**: Create extraction scripts for additional documents
2. **Improve processing**: Enhance pattern matching and extraction algorithms
3. **Expand coverage**: Add new Fannie Mae website sections
4. **Quality improvements**: Better cleaning and validation processes

## 📋 Requirements

- Python 3.7+
- PyPDF2 (PDF processing)
- anthropic (Claude API - optional)
- beautifulsoup4 (web scraping)
- requests (HTTP requests)

## 🔐 API Keys

- **Anthropic API Key**: Required for `pdf_to_jsonl.py` (Claude Haiku)
- **No API keys needed**: For `pdf_to_jsonl_fast.py` and web crawling scripts

## 📊 Performance

- **Processing Speed**: ~10-50 pages/minute (depending on method)
- **Accuracy**: High-quality extraction with validation
- **Scale**: Handles documents up to 1000+ pages
- **Memory**: Efficient processing for large files

## 🎯 Output Quality

- **Instruction Clarity**: Questions are clear and specific
- **Output Completeness**: Answers include definitions, notes, and examples
- **Consistency**: Standardized format across all datasets
- **Relevance**: Industry-specific terminology and concepts

## 📞 Support

For questions or issues:
1. Check existing scripts and documentation
2. Review sample outputs in JSONL files
3. Examine extraction patterns in the code
4. Test with smaller documents first

---

**📄 Total Knowledge Base**: 248 instruction-output pairs covering the complete Fannie Mae ecosystem, ready for AI training, education, and business applications.

**🚀 Ready to use**: All datasets are immediately usable for language model training, chatbot development, or educational purposes.# fanniemae
