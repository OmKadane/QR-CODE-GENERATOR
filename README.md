# Rainbow QR Code Generator

A beautiful web application that generates rainbow-colored QR codes with optional logo customization.

## Features

- Generate QR codes with rainbow gradient effect
- Optional logo customization
- Modern and responsive UI
- Download generated QR codes
- High error correction for better scannability

## Installation

1. Clone this repository:
```bash
git clone <https://github.com/OmKadane/QR-CODE-GENERATOR.git>
cd QR-Code-Generator
```

2. Create a virtual environment (recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install the required dependencies:
```bash
pip install -r requirements.txt
```

## Usage

1. Start the Flask application:
```bash
python app.py
```

2. Open your web browser and navigate to:
```
http://localhost:5000
```

3. Enter a URL and optionally a logo URL to generate your QR code.

## Requirements

- Python 3.7+
- Flask
- qrcode
- Pillow
- requests
- beautifulsoup4
- numpy

## License

MIT License 
