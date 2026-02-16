# 📊 Stock Earnings Analyzer

A powerful Streamlit web application that helps identify stock opportunities by analyzing upcoming earnings, comparing current prices to analyst targets, and showing technical indicators with moving averages.

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![Streamlit](https://img.shields.io/badge/Streamlit-1.28+-red.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)

## ✨ Features

- 📅 **Earnings Date Filtering**: Search stocks by specific earnings dates (today, tomorrow, this week, next week, custom range)
- 💰 **Price vs Target Analysis**: Find stocks trading below analyst target prices
- 📊 **Moving Averages**: Visual 50-day and 200-day MA indicators with color coding
- 🎯 **Upside Potential**: Calculate potential gains if stock reaches target price
- 📈 **Technical Analysis**: Color-coded indicators showing bullish/bearish signals
- 📥 **Export to CSV**: Download results for further analysis
- 🔗 **Quick Links**: Direct links to Yahoo Finance for each stock

## 🎨 Screenshots

### Main Results Table
The app displays stocks with color-coded moving averages:
- 🟢 Green = Price above moving average (Bullish)
- 🔴 Red = Price below moving average (Bearish)

### Moving Average Summary
Detailed breakdown showing which stocks are in strong technical positions.

## 🚀 Live Demo

**[Try the app here](https://YOUR_APP_URL.streamlit.app)** _(Update this link after deployment)_

## 📋 Prerequisites

- Python 3.8 or higher
- Internet connection (for fetching real-time stock data)

## 💻 Installation

### Option 1: Run Locally

1. Clone this repository:
```bash
git clone https://github.com/YOUR_USERNAME/earnings-analyzer.git
cd earnings-analyzer
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the app:
```bash
streamlit run earnings_analyzer_v5.py
```

4. Open your browser to `http://localhost:8501`

### Option 2: Deploy to Streamlit Cloud

1. Fork this repository
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect your GitHub account
4. Select this repository and deploy!

## 🎯 How to Use

1. **Select Earnings Date Range**
   - Choose from preset options (Today, Tomorrow, This Week, Next Week)
   - Or select custom date range

2. **Set Minimum EPS**
   - Filter stocks by earnings per share threshold
   - Default: 0 (shows all stocks)

3. **Click "Analyze Stocks"**
   - App fetches earnings calendar
   - Analyzes each stock for price vs target
   - Calculates moving averages

4. **Review Results**
   - Main table shows all opportunities
   - Color indicators show MA status
   - Summary section provides statistics
   - Top 5 picks highlighted

5. **Export Results**
   - Download CSV for further analysis
   - Click symbols to view on Yahoo Finance

## 📊 Data Sources

- **Stock Data**: Yahoo Finance via `yfinance` library
- **Earnings Calendar**: Web scraping + yfinance API
- **Real-time Prices**: Updated during market hours

## 🛠️ Technical Details

### Technologies Used
- **Streamlit**: Web framework
- **Pandas**: Data manipulation
- **yfinance**: Stock data API
- **BeautifulSoup**: Web scraping
- **Requests**: HTTP requests

### Key Metrics Displayed
- Current Price
- Target Price (analyst mean)
- Upside Percentage
- 50-Day Moving Average
- 200-Day Moving Average
- EPS (Trailing & Forward)
- PE Ratio
- Market Capitalization
- Sector & Industry

### Moving Average Logic
```python
# Green indicator (🟢): Stock price > Moving Average
# Red indicator (🔴): Stock price < Moving Average

# Bullish Setup: Both MAs green
# Bearish Setup: Both MAs red
# Mixed: One green, one red
```

## ⚙️ Configuration

You can customize the app by modifying:

- **Stock Universe**: Edit the `stock_universe` list in `fetch_earnings_using_yfinance_comprehensive()`
- **Date Ranges**: Modify `get_date_range()` function
- **API Delays**: Adjust `time.sleep()` values for rate limiting

## 🐛 Troubleshooting

### App is slow
- Normal behavior: Fetching data for 100+ stocks takes 1-3 minutes
- Progress bars show status

### No stocks found
- Try wider date range (e.g., "This Week" instead of "Today")
- Lower minimum EPS to 0
- Enable debug mode to see detailed info

### Rate limit errors
- Built-in delays prevent this
- If issues persist, increase `time.sleep()` values

## 📝 Disclaimer

**IMPORTANT**: This tool is for educational and research purposes only. 

- ⚠️ Not financial advice
- ⚠️ Not a recommendation to buy or sell securities
- ⚠️ Past performance does not guarantee future results
- ⚠️ Always conduct your own due diligence
- ⚠️ Consult with a qualified financial advisor before making investment decisions

The data provided by this tool may be delayed or inaccurate. Use at your own risk.

## 🤝 Contributing

Contributions are welcome! Here's how:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

### Ideas for Contributions
- Add more technical indicators (RSI, MACD, etc.)
- Support for international markets
- Historical earnings performance
- Email alerts for new opportunities
- Portfolio tracking

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Yahoo Finance for providing stock data
- Streamlit team for the amazing framework
- yfinance library maintainers

## 📞 Contact

Have questions or suggestions? 

- Open an [Issue](https://github.com/YOUR_USERNAME/earnings-analyzer/issues)
- Start a [Discussion](https://github.com/YOUR_USERNAME/earnings-analyzer/discussions)

## 🌟 Star History

If you find this project useful, please consider giving it a star! ⭐

---

**Made with ❤️ and Python**

*Remember: Never invest money you can't afford to lose. Always do your own research.*
