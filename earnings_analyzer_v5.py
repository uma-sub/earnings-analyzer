import streamlit as st
import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta, date
import time
import requests
from bs4 import BeautifulSoup

st.set_page_config(page_title="Earnings & Target Price Analyzer", layout="wide")

st.title("📊 Yahoo Finance Earnings & Target Price Analyzer")
st.markdown("Find stocks with high EPS and current price below target price")

# Sidebar controls
st.sidebar.header("Filters")
min_eps = st.sidebar.number_input("Minimum EPS", value=0.0, step=0.1, 
                                   help="Minimum earnings per share (use 0 to see all)")

# Date filter options
st.sidebar.subheader("Earnings Date Filter")
date_filter_type = st.sidebar.selectbox(
    "Filter by Earnings Date",
    ["Today", "Tomorrow", "This Week", "Next Week", "This Month", "Custom Date Range"]
)

# Custom date range inputs
start_date = None
end_date = None
if date_filter_type == "Custom Date Range":
    col1, col2 = st.sidebar.columns(2)
    with col1:
        start_date = st.date_input("Start Date", value=datetime.now().date())
    with col2:
        end_date = st.date_input("End Date", value=datetime.now().date() + timedelta(days=7))

show_debug = st.sidebar.checkbox("Show Debug Info", value=False)

def get_date_range(filter_type, start=None, end=None):
    """Get start and end dates based on filter type"""
    today = datetime.now().date()
    
    if filter_type == "Today":
        return today, today
    elif filter_type == "Tomorrow":
        tomorrow = today + timedelta(days=1)
        return tomorrow, tomorrow
    elif filter_type == "This Week":
        # Current week (Monday to Sunday)
        start_of_week = today - timedelta(days=today.weekday())
        end_of_week = start_of_week + timedelta(days=6)
        return start_of_week, end_of_week
    elif filter_type == "Next Week":
        # Next week (Monday to Sunday)
        start_of_next_week = today + timedelta(days=(7 - today.weekday()))
        end_of_next_week = start_of_next_week + timedelta(days=6)
        return start_of_next_week, end_of_next_week
    elif filter_type == "This Month":
        start_of_month = today.replace(day=1)
        # Get last day of month
        if today.month == 12:
            end_of_month = today.replace(day=31)
        else:
            end_of_month = (today.replace(month=today.month + 1, day=1) - timedelta(days=1))
        return start_of_month, end_of_month
    elif filter_type == "Custom Date Range":
        return start, end
    
    return today, today + timedelta(days=7)

def fetch_earnings_from_yahoo_multiple_days(start_date, end_date):
    """Fetch earnings for each day in the range from Yahoo Finance"""
    st.info("🔍 Fetching earnings calendar from Yahoo Finance for each day...")
    
    all_earnings = []
    current_date = start_date
    days_checked = 0
    max_days = (end_date - start_date).days + 1
    
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    while current_date <= end_date and days_checked < 30:  # Max 30 days to avoid too many requests
        status_text.text(f"Checking {current_date.strftime('%Y-%m-%d')}...")
        
        try:
            # Yahoo Finance earnings calendar URL for specific date
            url = f"https://finance.yahoo.com/calendar/earnings?day={current_date.strftime('%Y-%m-%d')}"
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
            }
            
            response = requests.get(url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Look for the earnings table
                tables = soup.find_all('table')
                for table in tables:
                    rows = table.find_all('tr')
                    for row in rows[1:]:  # Skip header
                        cols = row.find_all('td')
                        if len(cols) >= 2:
                            try:
                                # Extract symbol
                                symbol_elem = cols[0].find('a')
                                if symbol_elem:
                                    symbol = symbol_elem.get_text(strip=True)
                                    company = cols[1].get_text(strip=True) if len(cols) > 1 else ""
                                    
                                    # Try to get EPS estimate (usually in column 2 or 3)
                                    eps_estimate = None
                                    for col_idx in [2, 3, 4]:
                                        if len(cols) > col_idx:
                                            try:
                                                eps_text = cols[col_idx].get_text(strip=True)
                                                if eps_text and eps_text != '-' and eps_text != 'N/A':
                                                    # Try to parse as float
                                                    eps_estimate = float(eps_text.replace('$', '').replace(',', ''))
                                                    break
                                            except:
                                                continue
                                    
                                    # Check if we already have this symbol for this date
                                    if not any(e['Symbol'] == symbol and e['Earnings Date'] == current_date for e in all_earnings):
                                        all_earnings.append({
                                            'Symbol': symbol,
                                            'Company': company,
                                            'EPS Estimate': eps_estimate,
                                            'Earnings Date': current_date
                                        })
                                        
                                        if show_debug:
                                            st.write(f"Found: {symbol} on {current_date}")
                            except Exception as e:
                                if show_debug:
                                    st.write(f"Error parsing row: {e}")
                                continue
                
                if show_debug:
                    st.write(f"Found {len([e for e in all_earnings if e['Earnings Date'] == current_date])} stocks for {current_date}")
            
        except Exception as e:
            if show_debug:
                st.write(f"Error fetching {current_date}: {str(e)}")
        
        days_checked += 1
        progress_bar.progress(days_checked / max_days)
        current_date += timedelta(days=1)
        time.sleep(1)  # Rate limiting - important!
    
    progress_bar.empty()
    status_text.empty()
    
    return all_earnings

def fetch_earnings_using_yfinance_comprehensive(start_date, end_date):
    """Check a comprehensive list of stocks for earnings dates using yfinance"""
    st.info("🔍 Checking stocks for earnings dates using yfinance (this may take a few minutes)...")
    
    # Comprehensive list of stocks to check
    stock_universe = [
        # Large Cap Tech
        'AAPL', 'MSFT', 'GOOGL', 'GOOG', 'AMZN', 'NVDA', 'META', 'TSLA', 'AVGO', 'ORCL',
        'ADBE', 'CRM', 'CSCO', 'ACN', 'AMD', 'INTC', 'QCOM', 'TXN', 'INTU', 'IBM',
        'SNOW', 'NOW', 'PANW', 'PLTR', 'CRWD', 'SHOP', 'SQ', 'UBER', 'ABNB', 'RBLX',
        'DDOG', 'NET', 'ZS', 'OKTA', 'MDB', 'TEAM', 'WDAY', 'ZM', 'DOCU', 'TWLO',
        
        # Finance
        'JPM', 'BAC', 'WFC', 'C', 'GS', 'MS', 'BLK', 'SCHW', 'V', 'MA',
        'PYPL', 'AXP', 'SPGI', 'BRK-B', 'USB', 'PNC', 'TFC', 'COF', 'BK', 'STT',
        'CB', 'PGR', 'TRV', 'ALL', 'AIG', 'MET', 'PRU', 'AFL', 'HIG', 'CINF',
        
        # Healthcare
        'UNH', 'JNJ', 'LLY', 'ABBV', 'MRK', 'TMO', 'ABT', 'DHR', 'PFE', 'AMGN',
        'CVS', 'CI', 'HUM', 'ISRG', 'VRTX', 'REGN', 'GILD', 'BIIB', 'MDT', 'BSX',
        'SYK', 'EW', 'IDXX', 'ZBH', 'BAX', 'HOLX', 'RMD', 'ALGN', 'DXCM', 'PODD',
        
        # Consumer Discretionary
        'AMZN', 'TSLA', 'HD', 'MCD', 'NKE', 'SBUX', 'TGT', 'LOW', 'TJX', 'BKNG',
        'CMG', 'YUM', 'DRI', 'ULTA', 'ROST', 'DG', 'DLTR', 'BBY', 'ORLY', 'AZO',
        'MAR', 'HLT', 'MGM', 'WYNN', 'LVS', 'POOL', 'WHR', 'LEN', 'DHI', 'PHM',
        
        # Consumer Staples
        'WMT', 'COST', 'PG', 'KO', 'PEP', 'PM', 'MO', 'CL', 'KMB', 'GIS',
        'K', 'HSY', 'MDLZ', 'KHC', 'MKC', 'SJM', 'CAG', 'CPB', 'HRL', 'TSN',
        'EL', 'CL', 'CHD', 'CLX', 'TAP', 'STZ', 'BF-B', 'SAM', 'MNST', 'KDP',
        
        # Energy
        'XOM', 'CVX', 'COP', 'SLB', 'EOG', 'PSX', 'VLO', 'MPC', 'OXY', 'HAL',
        'MRO', 'DVN', 'FANG', 'APA', 'HES', 'KMI', 'WMB', 'OKE', 'LNG', 'TRGP',
        
        # Industrial
        'BA', 'CAT', 'GE', 'HON', 'UPS', 'RTX', 'DE', 'LMT', 'MMM', 'ETN',
        'EMR', 'ITW', 'PH', 'CARR', 'OTIS', 'PCAR', 'CMI', 'NSC', 'UNP', 'CSX',
        'FDX', 'DAL', 'UAL', 'LUV', 'AAL', 'JBLU', 'WM', 'RSG', 'IR', 'FAST',
        
        # Communications
        'DIS', 'CMCSA', 'NFLX', 'T', 'VZ', 'TMUS', 'CHTR', 'EA', 'TTWO', 'WBD',
        'PARA', 'FOXA', 'FOX', 'OMC', 'IPG', 'MTCH', 'PINS', 'SNAP', 'SPOT', 'LYV',
        
        # Real Estate & Utilities
        'NEE', 'DUK', 'SO', 'D', 'AEP', 'EXC', 'SRE', 'PLD', 'AMT', 'CCI',
        'EQIX', 'PSA', 'WELL', 'AVB', 'EQR', 'VICI', 'O', 'DLR', 'SPG', 'VTR',
        
        # Materials
        'LIN', 'APD', 'SHW', 'ECL', 'NEM', 'FCX', 'DD', 'DOW', 'PPG', 'NUE',
        'VMC', 'MLM', 'ALB', 'CF', 'MOS', 'IFF', 'FMC', 'CE', 'EMN', 'LYB',
        
        # Mid/Small Cap
        'ENPH', 'SEDG', 'FSLR', 'RUN', 'SPWR', 'DQ', 'NOVA', 'JKS', 'CSIQ', 'MAXN',
    ]
    
    stocks_with_earnings = []
    progress_bar = st.progress(0)
    status_text = st.empty()
    checked = 0
    found = 0
    
    for idx, symbol in enumerate(stock_universe):
        status_text.text(f"Checking {symbol}... ({idx + 1}/{len(stock_universe)}) - Found: {found}")
        
        try:
            ticker = yf.Ticker(symbol)
            
            # Try to get earnings date from calendar
            earnings_date = None
            try:
                calendar = ticker.calendar
                if calendar is not None:
                    if isinstance(calendar, pd.DataFrame):
                        # Check if 'Earnings Date' is in the DataFrame
                        if 'Earnings Date' in calendar.columns:
                            earnings_dates = calendar['Earnings Date']
                            if len(earnings_dates) > 0:
                                earnings_date = pd.to_datetime(earnings_dates.iloc[0]).date()
                        elif 'Earnings Date' in calendar.index:
                            earnings_dates = calendar.loc['Earnings Date']
                            if isinstance(earnings_dates, pd.Series) and len(earnings_dates) > 0:
                                earnings_date = pd.to_datetime(earnings_dates.iloc[0]).date()
                    elif isinstance(calendar, dict) and 'Earnings Date' in calendar:
                        earnings_dates = calendar['Earnings Date']
                        if isinstance(earnings_dates, (list, pd.Series)) and len(earnings_dates) > 0:
                            earnings_date = pd.to_datetime(earnings_dates[0]).date()
            except Exception as e:
                if show_debug:
                    st.write(f"Calendar error for {symbol}: {e}")
            
            # Alternative method: try earnings_dates property
            if not earnings_date:
                try:
                    if hasattr(ticker, 'earnings_dates'):
                        earnings_df = ticker.earnings_dates
                        if earnings_df is not None and len(earnings_df) > 0:
                            # Get the next upcoming earnings date
                            future_dates = earnings_df[earnings_df.index >= pd.Timestamp.now()]
                            if len(future_dates) > 0:
                                earnings_date = future_dates.index[0].date()
                except Exception as e:
                    if show_debug:
                        st.write(f"Earnings dates error for {symbol}: {e}")
            
            # Check if earnings date is in range
            if earnings_date and start_date <= earnings_date <= end_date:
                info = ticker.info
                eps_trailing = info.get('trailingEps')
                eps_forward = info.get('forwardEps')
                
                stocks_with_earnings.append({
                    'Symbol': symbol,
                    'Company': info.get('longName', symbol),
                    'EPS Estimate': eps_trailing or eps_forward,
                    'Earnings Date': earnings_date
                })
                found += 1
                
                if show_debug:
                    st.write(f"✅ {symbol} has earnings on {earnings_date}")
        
        except Exception as e:
            if show_debug:
                st.write(f"Error checking {symbol}: {e}")
        
        checked += 1
        progress_bar.progress(checked / len(stock_universe))
        time.sleep(0.25)  # Rate limiting
    
    progress_bar.empty()
    status_text.empty()
    
    st.success(f"Checked {checked} stocks, found {found} with earnings in date range")
    return stocks_with_earnings

def get_stock_details(symbol):
    """Get current price, target price, moving averages, and other details for a stock"""
    try:
        ticker = yf.Ticker(symbol)
        info = ticker.info
        
        # Try multiple fields for current price
        current_price = (info.get('currentPrice') or 
                        info.get('regularMarketPrice') or 
                        info.get('regularMarketPreviousClose') or
                        info.get('previousClose'))
        
        target_price = info.get('targetMeanPrice')
        
        # Get EPS - try multiple fields
        eps_trailing = info.get('trailingEps')
        eps_forward = info.get('forwardEps')
        eps = eps_trailing or eps_forward or 0
        
        # Calculate moving averages from historical data
        ma_50 = None
        ma_200 = None
        above_ma_50 = None
        above_ma_200 = None
        
        try:
            # Fetch historical data (need at least 200 days for 200-day MA)
            hist = ticker.history(period="1y", interval="1d")
            
            if hist is not None and len(hist) > 0:
                # Calculate 50-day moving average
                if len(hist) >= 50:
                    ma_50 = hist['Close'].tail(50).mean()
                    if current_price and ma_50:
                        above_ma_50 = current_price > ma_50
                
                # Calculate 200-day moving average
                if len(hist) >= 200:
                    ma_200 = hist['Close'].tail(200).mean()
                    if current_price and ma_200:
                        above_ma_200 = current_price > ma_200
                
                if show_debug:
                    st.write(f"{symbol}: Price=${current_price}, MA50=${ma_50:.2f if ma_50 else 'N/A'}, MA200=${ma_200:.2f if ma_200 else 'N/A'}")
        except Exception as e:
            if show_debug:
                st.write(f"Error calculating MAs for {symbol}: {e}")
        
        # Calculate upside
        upside = None
        if target_price and current_price and current_price > 0:
            upside = ((target_price - current_price) / current_price * 100)
        
        return {
            'Current Price': current_price,
            'Target Price': target_price,
            'Upside %': upside,
            'EPS (Trailing)': eps_trailing,
            'EPS (Forward)': eps_forward,
            'EPS': eps,
            'PE Ratio': info.get('trailingPE'),
            'Market Cap': info.get('marketCap'),
            'Sector': info.get('sector', 'N/A'),
            'Industry': info.get('industry', 'N/A'),
            'MA 50': ma_50,
            'MA 200': ma_200,
            'Above MA 50': above_ma_50,
            'Above MA 200': above_ma_200,
        }
    except Exception as e:
        if show_debug:
            st.write(f"Error fetching details for {symbol}: {str(e)}")
        return None

# Main app logic
if st.sidebar.button("🔍 Analyze Stocks", type="primary"):
    # Get date range
    filter_start, filter_end = get_date_range(date_filter_type, start_date, end_date)
    
    st.info(f"🗓️ Looking for stocks with earnings between **{filter_start}** and **{filter_end}**")
    
    # STEP 1: Get stocks with earnings in the date range
    st.subheader("Step 1: Fetching Earnings Calendar")
    
    # Try Yahoo Finance scraping first
    earnings_stocks = fetch_earnings_from_yahoo_multiple_days(filter_start, filter_end)
    
    # If Yahoo scraping didn't get enough results, use yfinance method
    if not earnings_stocks or len(earnings_stocks) < 5:
        st.warning("Yahoo Finance scraping returned limited results. Using comprehensive yfinance check...")
        earnings_stocks = fetch_earnings_using_yfinance_comprehensive(filter_start, filter_end)
    
    if not earnings_stocks:
        st.error("❌ Could not find any stocks with earnings in the selected date range.")
        st.info("""
        **Possible reasons:**
        1. No major companies have earnings on these specific dates
        2. The date range might be too narrow
        3. Yahoo Finance calendar data may not be accessible
        
        **Try:**
        - Select a wider date range (e.g., "This Week" or "Next Week")
        - Try a different week
        - Check Yahoo Finance website manually to verify earnings dates
        """)
    else:
        st.success(f"📊 Found **{len(earnings_stocks)}** stocks with earnings in selected date range")
        
        # Show the stocks with earnings grouped by date
        earnings_df = pd.DataFrame(earnings_stocks)
        earnings_by_date = earnings_df.groupby('Earnings Date').size().reset_index(name='Count')
        
        st.subheader("Earnings Distribution by Date")
        st.dataframe(earnings_by_date, use_container_width=True, hide_index=True)
        
        # Show the stocks with earnings
        with st.expander(f"📋 View all {len(earnings_stocks)} stocks with earnings"):
            display_earnings = earnings_df.copy()
            display_earnings['Earnings Date'] = display_earnings['Earnings Date'].apply(
                lambda x: x.strftime('%Y-%m-%d') if isinstance(x, date) else x
            )
            st.dataframe(display_earnings, use_container_width=True, hide_index=True)
        
        # STEP 2: Now analyze only these stocks for price vs target
        st.subheader("Step 2: Analyzing Prices and Targets")
        st.info(f"💰 Analyzing prices and targets for {len(earnings_stocks)} stocks...")
        
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        opportunities = []
        failed_checks = []
        
        for idx, stock in enumerate(earnings_stocks):
            symbol = stock['Symbol']
            status_text.text(f"Analyzing {symbol}... ({idx + 1}/{len(earnings_stocks)})")
            
            details = get_stock_details(symbol)
            
            if details:
                # Combine earnings info with price details
                full_data = {**stock, **details}
                
                current_price = details.get('Current Price')
                target_price = details.get('Target Price')
                eps = details.get('EPS', 0)
                
                # Debug info
                if show_debug:
                    st.write(f"{symbol}: CP=${current_price}, TP=${target_price}, EPS={eps}")
                
                # Check if it meets criteria
                if (current_price and target_price and eps is not None and
                    current_price < target_price and eps >= min_eps):
                    opportunities.append(full_data)
                else:
                    failed_checks.append({
                        'Symbol': symbol,
                        'Current Price': current_price,
                        'Target Price': target_price,
                        'EPS': eps,
                        'Reason': 'Price >= Target' if (current_price and target_price and current_price >= target_price) 
                                 else f'EPS too low ({eps})' if eps < min_eps 
                                 else 'Missing data'
                    })
            else:
                failed_checks.append({'Symbol': symbol, 'Reason': 'Could not fetch data'})
            
            progress_bar.progress((idx + 1) / len(earnings_stocks))
            time.sleep(0.3)  # Rate limiting
        
        progress_bar.empty()
        status_text.empty()
        
        # Show summary
        st.subheader("📊 Analysis Summary")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Stocks with Earnings", len(earnings_stocks))
        with col2:
            st.metric("✅ Opportunities Found", len(opportunities))
        with col3:
            st.metric("❌ Didn't Meet Criteria", len(failed_checks))
        
        # Show failed checks in debug mode
        if show_debug and failed_checks:
            with st.expander(f"🔍 Debug: {len(failed_checks)} stocks that didn't meet criteria"):
                st.dataframe(pd.DataFrame(failed_checks), use_container_width=True, hide_index=True)
        
        # Display opportunities
        if opportunities:
            st.subheader(f"✅ {len(opportunities)} Stocks Trading Below Target Price")
            st.caption(f"With earnings between {filter_start} and {filter_end}")
            
            # Create results dataframe
            results_df = pd.DataFrame(opportunities)
            
            # Format for display with indicators in the MA columns
            def format_ma_with_indicator(price, ma_value):
                """Add visual indicator to MA value"""
                if price and ma_value:
                    if price > ma_value:
                        return f"🟢 ${ma_value:.2f}"
                    else:
                        return f"🔴 ${ma_value:.2f}"
                return "N/A"
            
            display_data = []
            for idx, row in results_df.iterrows():
                current_price = row['Current Price']
                ma_50 = row.get('MA 50')
                ma_200 = row.get('MA 200')
                symbol = row['Symbol']
                
                display_data.append({
                    'Symbol': f"https://finance.yahoo.com/quote/{symbol}",
                    'Company': row['Company'],
                    'Earnings Date': row['Earnings Date'].strftime('%Y-%m-%d') if isinstance(row['Earnings Date'], date) else row['Earnings Date'],
                    'Sector': row['Sector'],
                    'Current Price': f"${current_price:.2f}" if current_price else "N/A",
                    'Target Price': f"${row['Target Price']:.2f}" if row['Target Price'] else "N/A",
                    'Upside %': f"{row['Upside %']:.2f}%" if row['Upside %'] is not None else "N/A",
                    '50-Day MA': format_ma_with_indicator(current_price, ma_50),
                    '200-Day MA': format_ma_with_indicator(current_price, ma_200),
                    'EPS (Trailing)': f"{row['EPS (Trailing)']:.2f}" if row['EPS (Trailing)'] else "N/A",
                    'EPS (Forward)': f"{row['EPS (Forward)']:.2f}" if row['EPS (Forward)'] else "N/A",
                    'PE Ratio': f"{row['PE Ratio']:.2f}" if row['PE Ratio'] else "N/A",
                    'Market Cap': f"${row['Market Cap']:,.0f}" if row['Market Cap'] else "N/A",
                })
            
            display_df = pd.DataFrame(display_data)
            
            # Sort by upside percentage
            upside_values = results_df['Upside %'].fillna(0)
            display_df['_sort'] = upside_values.values
            display_df = display_df.sort_values('_sort', ascending=False).drop('_sort', axis=1)
            
            # Display with column config for clickable links
            st.dataframe(
                display_df,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "Symbol": st.column_config.LinkColumn(
                        "Symbol",
                        help="Click to view on Yahoo Finance",
                        display_text=r"https://finance\.yahoo\.com/quote/(.*)"
                    )
                }
            )
            
            # Add legend right after the table
            st.markdown("""
            **Legend:**
            - 🟢 = Stock price is ABOVE the moving average (Bullish signal)
            - 🔴 = Stock price is BELOW the moving average (Bearish signal)
            - 💡 Click any ticker symbol to view on Yahoo Finance
            """)
            
            # Add visual indicators using markdown for stocks above MAs
            st.markdown("---")
            st.subheader("📊 Moving Average Summary")
            
            # Create indicator dataframe
            ma_indicators = []
            for idx, row in results_df.iterrows():
                symbol = row['Symbol']
                current_price = row['Current Price']
                ma_50 = row.get('MA 50')
                ma_200 = row.get('MA 200')
                
                if current_price and ma_50 and ma_200:
                    above_50 = current_price > ma_50
                    above_200 = current_price > ma_200
                    
                    # Determine status
                    if above_50 and above_200:
                        status = "🟢 Above Both MAs (Bullish)"
                    elif above_200:
                        status = "🟡 Above 200-Day MA"
                    elif above_50:
                        status = "🟠 Above 50-Day MA Only"
                    else:
                        status = "🔴 Below Both MAs"
                    
                    ma_indicators.append({
                        'Symbol': symbol,
                        'Status': status,
                        'Price vs 50-MA': f"+{((current_price/ma_50 - 1) * 100):.1f}%" if above_50 else f"{((current_price/ma_50 - 1) * 100):.1f}%",
                        'Price vs 200-MA': f"+{((current_price/ma_200 - 1) * 100):.1f}%" if above_200 else f"{((current_price/ma_200 - 1) * 100):.1f}%",
                    })
            
            if ma_indicators:
                ma_df = pd.DataFrame(ma_indicators)
                
                # Add hyperlinks to symbols in MA summary table
                ma_df['Symbol'] = ma_df['Symbol'].apply(lambda x: f"https://finance.yahoo.com/quote/{x}")
                
                st.dataframe(
                    ma_df, 
                    use_container_width=True, 
                    hide_index=True,
                    column_config={
                        "Symbol": st.column_config.LinkColumn(
                            "Symbol",
                            help="Click to view on Yahoo Finance",
                            display_text=r"https://finance\.yahoo\.com/quote/(.*)"
                        )
                    }
                )
                
                # Summary stats
                total_with_ma = len(ma_indicators)
                above_both = sum(1 for ind in ma_indicators if "Above Both" in ind['Status'])
                above_200_only = sum(1 for ind in ma_indicators if "Above 200-Day" in ind['Status'])
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("🟢 Above Both MAs", f"{above_both} / {total_with_ma}")
                with col2:
                    st.metric("🟡 Above 200-Day MA", f"{above_200_only} / {total_with_ma}")
                with col3:
                    pct_above_200 = ((above_both + above_200_only) / total_with_ma * 100) if total_with_ma > 0 else 0
                    st.metric("% Above 200-Day MA", f"{pct_above_200:.1f}%")
            
            st.markdown("---")
            
            # Also add a note about clicking symbols
            st.caption("💡 Click on any ticker symbol to view it on Yahoo Finance")
            
            # Summary metrics
            col1, col2, col3 = st.columns(3)
            with col1:
                avg_upside = upside_values[upside_values > 0].mean()
                st.metric("Average Upside", f"{avg_upside:.2f}%")
            with col2:
                max_upside = upside_values.max()
                st.metric("Max Upside", f"{max_upside:.2f}%")
            with col3:
                avg_eps = results_df['EPS'].mean()
                st.metric("Average EPS", f"${avg_eps:.2f}")
            
            # Download button
            csv = display_df.to_csv(index=False)
            st.download_button(
                label="📥 Download Results as CSV",
                data=csv,
                file_name=f"earnings_analysis_{filter_start}_{datetime.now().strftime('%H%M%S')}.csv",
                mime="text/csv"
            )
            
            # Show top picks
            st.subheader("🎯 Top 5 Picks by Upside Potential")
            top_5_results = results_df.head(5)
            for idx, row in top_5_results.iterrows():
                symbol = row['Symbol']
                company = row['Company']
                upside = row['Upside %']
                current_price = row['Current Price']
                ma_50 = row.get('MA 50')
                ma_200 = row.get('MA 200')
                
                # Determine MA status
                ma_status = ""
                if current_price and ma_50 and ma_200:
                    above_50 = current_price > ma_50
                    above_200 = current_price > ma_200
                    if above_50 and above_200:
                        ma_status = "🟢 Above Both MAs"
                    elif above_200:
                        ma_status = "🟡 Above 200-Day MA"
                    elif above_50:
                        ma_status = "🟠 Above 50-Day MA Only"
                    else:
                        ma_status = "🔴 Below Both MAs"
                
                # Find corresponding row in display_df
                display_row = display_df[display_df['Symbol'].str.contains(symbol)].iloc[0]
                
                with st.expander(f"**{symbol}** - {company} ({display_row['Upside %']} upside) {ma_status}"):
                    col1, col2 = st.columns(2)
                    with col1:
                        st.write(f"**Earnings Date:** {display_row['Earnings Date']}")
                        st.write(f"**Current Price:** {display_row['Current Price']}")
                        st.write(f"**Target Price:** {display_row['Target Price']}")
                        st.write(f"**Upside:** {display_row['Upside %']}")
                        st.write(f"**50-Day MA:** {display_row['50-Day MA']}")
                        st.write(f"**200-Day MA:** {display_row['200-Day MA']}")
                    with col2:
                        st.write(f"**Sector:** {display_row['Sector']}")
                        st.write(f"**EPS (Trailing):** {display_row['EPS (Trailing)']}")
                        st.write(f"**EPS (Forward):** {display_row['EPS (Forward)']}")
                        st.write(f"**PE Ratio:** {display_row['PE Ratio']}")
                        if ma_status:
                            st.write(f"**MA Status:** {ma_status}")
        else:
            st.warning("⚠️ No stocks found matching the criteria (Current Price < Target Price AND EPS >= Minimum).")
            st.info(f"""
            **All {len(earnings_stocks)} stocks with earnings in your date range were checked, but none met the criteria:**
            1. Current Price must be less than Target Price
            2. EPS must be >= your minimum EPS setting (currently: {min_eps})
            
            **Try:**
            - Lower the minimum EPS to 0
            - Select a different date range
            - Enable "Show Debug Info" to see why stocks didn't qualify
            """)

# Instructions
with st.expander("ℹ️ How to use"):
    st.markdown("""
    ### Instructions
    
    1. **Choose Date Filter**: Select when you want to find earnings
       - **Today**: Only stocks with earnings today
       - **Tomorrow**: Only stocks with earnings tomorrow
       - **This Week**: Stocks with earnings this week (Monday-Sunday)
       - **Next Week**: Stocks with earnings next week
       - **This Month**: Stocks with earnings this month
       - **Custom Date Range**: Pick your own start and end dates
    2. **Set Minimum EPS**: Enter the minimum earnings per share (default: 0 to see all)
    3. **Click Analyze**: The app will:
       - First try to fetch Yahoo Finance earnings calendar for each day
       - Fall back to checking 300+ stocks via yfinance if needed
       - Show you opportunities where Current Price < Target Price
    
    ### Optimized Process
    
    ✅ **Step 1**: Fetch earnings calendar for selected dates  
    ✅ **Step 2**: Analyze only those stocks (not all stocks)  
    ✅ **Step 3**: Show opportunities with upside potential
    
    ### Tips
    
    - Set minimum EPS to 0 to see all opportunities
    - Results will vary by date - different companies report on different days
    - Enable debug mode to see detailed information
    - Wider date ranges (week/month) will find more stocks
    
    ### Disclaimer
    
    This tool provides publicly available financial data for research purposes only. 
    Not financial advice. Always do your own research.
    """)

st.sidebar.markdown("---")
st.sidebar.caption("Data source: Yahoo Finance via yfinance")
st.sidebar.caption("⚠️ Not financial advice")
