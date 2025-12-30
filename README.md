# SmartFormsGPT 📋

AI-Powered Insurance Claim Form Processing System

## Overview

SmartFormsGPT is an intelligent system for processing insurance claim forms using AI. It automates claim data extraction, validation, and decision-making to streamline the insurance claims process.

## Features

✅ **Automated Form Processing** - Extract data from PDFs, images, and scanned documents
✅ **Intelligent Validation** - Validate claim data against business rules
✅ **Decision Engine** - Automated claim approval/rejection based on configurable rules
✅ **Multiple Claim Types** - Support for Medical, Dental, Prescription, and other claim types
✅ **Batch Processing** - Process multiple claims simultaneously
✅ **Analytics Dashboard** - Real-time insights and reporting
✅ **Secure Authentication** - JWT-based authentication system

## Tech Stack

- **Frontend**: Streamlit
- **Backend**: Python 3.9+
- **AI/ML**: OpenAI GPT-4, LangChain
- **Database**: PostgreSQL / SQLite
- **Authentication**: JWT (python-jose)
- **Validation**: Pydantic

## Installation

### Prerequisites

- Python 3.9 or higher
- pip package manager
- PostgreSQL (optional, SQLite works for development)

### Setup

1. **Clone the repository**
```bash
git clone https://github.com/PyBADR/SmartFormsGPT.git
cd SmartFormsGPT
```

2. **Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Configure environment variables**
```bash
cp .env.example .env
# Edit .env and add your configuration
```

Required environment variables:
- `OPENAI_API_KEY`: Your OpenAI API key
- `DATABASE_URL`: Database connection string
- `SECRET_KEY`: Secret key for JWT authentication

5. **Initialize database**
```bash
python -c "from db import init_db; init_db()"
```

6. **Run the application**
```bash
streamlit run streamlit_app.py
```

The application will be available at `http://localhost:8501`

## Usage

### Submit a Claim

1. Navigate to "Submit Claim" page
2. Fill in patient and provider information
3. Enter claim details and amounts
4. Upload supporting documents (optional)
5. Click "Submit Claim"
6. View automated decision and confidence score

### View Claims

- Navigate to "View Claims" to see all submitted claims
- Expand each claim to view detailed information
- Filter and search claims by status, date, or amount

### Batch Processing

- Upload CSV or Excel file with multiple claims
- System processes all claims automatically
- Download results with decisions and confidence scores

### Analytics

- View real-time statistics and metrics
- Analyze claim trends and patterns
- Export reports for further analysis

## Project Structure

```
SmartFormsGPT/
├── streamlit_app.py      # Main Streamlit application
├── auth.py               # Authentication module
├── db.py                 # Database configuration
├── logger.py             # Logging configuration
├── requirements.txt      # Python dependencies
├── .env.example          # Environment variables template
├── schemas/
│   ├── base_claim.py     # Base claim schema
│   └── custom_claim.py   # Extended claim schemas
├── logic/
│   ├── decision_engine.py # Claim decision engine
│   └── rules.py          # Business rules
├── utils/
│   ├── helpers.py        # Utility functions
│   └── validators.py     # Data validators
├── prompts/
│   └── prompt.txt        # AI prompts
├── tests/
│   ├── test_validation.py
│   └── test_decision.py
└── docs/
    ├── NEXT_STEPS.md
    └── FINAL_SUMMARY.md
```

## Configuration

### Business Rules

Edit `logic/rules.py` to customize:
- Maximum claim amounts
- Auto-approval thresholds
- Service date validation ranges
- Documentation requirements

### AI Prompts

Customize AI behavior in `prompts/prompt.txt`:
- Extraction prompts
- Validation prompts
- Decision support prompts

## Testing

Run tests:
```bash
pytest tests/
```

Run with coverage:
```bash
pytest --cov=. tests/
```

## Development

### Adding New Claim Types

1. Create new schema in `schemas/custom_claim.py`
2. Extend from `BaseClaim`
3. Add type-specific fields and validators
4. Update decision engine rules if needed

### Customizing Decision Logic

1. Edit `logic/decision_engine.py`
2. Modify `evaluate_claim()` method
3. Add new rules in `logic/rules.py`
4. Update tests

## Security

- All passwords are hashed using bcrypt
- JWT tokens for authentication
- Environment variables for sensitive data
- Input validation and sanitization
- SQL injection prevention via SQLAlchemy ORM

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

MIT License - see LICENSE file for details

## Support

For issues and questions:
- GitHub Issues: [https://github.com/PyBADR/SmartFormsGPT/issues](https://github.com/PyBADR/SmartFormsGPT/issues)
- Email: support@smartformsgpt.com

## Roadmap

- [ ] OCR integration for scanned documents
- [ ] Multi-language support
- [ ] Mobile app
- [ ] Advanced analytics and ML insights
- [ ] Integration with major insurance platforms
- [ ] Real-time collaboration features

## Acknowledgments

- OpenAI for GPT-4 API
- Streamlit for the amazing framework
- The open-source community

---

Built with ❤️ by the SmartFormsGPT Team
