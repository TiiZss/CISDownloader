# CIS Benchmark Downloader

![Python](https://img.shields.io/badge/python-3.8+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Maintained](https://img.shields.io/badge/maintained-yes-brightgreen.svg)
[![Buy Me A Coffee](https://img.shields.io/badge/Buy%20Me%20A%20Coffee-Support%20Me-orange.svg)](https://www.buymeacoffee.com/TiiZss)

Automated tool to download the **latest version** of all CIS Benchmarks directly from the CIS Security website. It handles authentication (via session), organizes files by category, and implements anti-scraping measures.

## 🌟 Features

- **Automated Downloads**: Scrapes and downloads all available benchmarks.
- **Latest Version Only**: Automatically detects and keeps only the most recent version of each benchmark (tie-breaking with `pk_vid`).
- **Smart Categorization**: Organizes PDFs into folders (e.g., `CIS_Benchmarks/Amazon Web Services/`).
- **Native Browser Download**: Uses Selenium's native download capability to avoid session/cookie issues.
- **Anti-Scraping**: Implements random wait times and User-Agent rotation.
- **Auto-Renaming**: Renames downloaded files to clean, readable names.

## 🚀 Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/TiiZss/CIS-Benchmark-Scraper.git
   cd CIS-Benchmark-Scraper
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

   **Requirements:**
   - Python 3.8+
   - Google Chrome installed

## 🛠️ Usage

Simply run the script:

```bash
python cisdownloader.py
```

The script will launch a Chrome window (managed by Selenium), navigate to the CIS portal, and start downloading files to the `CIS_Benchmarks` directory.

> **Note**: The script attempts to automatically accept cookies. If you see the browser stuck on the cookie banner, manual intervention might be required (though unlikely).

## ☕ Support

If this tool saved you time, consider buying me a coffee!

<a href="https://www.buymeacoffee.com/TiiZss" target="_blank"><img src="https://cdn.buymeacoffee.com/buttons/v2/default-yellow.png" alt="Buy Me A Coffee" style="height: 60px !important;width: 217px !important;" ></a>

## ⭐ Star History

If you find this project useful, please **give it a star**! It helps others find the project and motivates me to keep improving it.

[![Star History Chart](https://api.star-history.com/svg?repos=TiiZss/CIS-Benchmark-Scraper&type=Date)](https://star-history.com/#TiiZss/CIS-Benchmark-Scraper&Date)

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.
