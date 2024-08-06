import requests
import mysql.connector
import pandas as pd
import json
import yfinance as yf
from datetime import datetime

sp500_tickers = [
    "A", "AAL", "AAP", "AAPL", "ABBV", "ABT", "ACN", "ADBE", "ADI", "ADM", "ADP", "ADSK", "AEE", "AEP", "AES", "AFL", 
    "AIG", "AIZ", "AJG", "AKAM", "ALB", "ALGN", "ALK", "ALL", "ALLE", "AMAT", "AMCR", "AMD", "AME", "AMGN", "AMP", 
    "AMT", "AMZN", "ANET", "ANSS", "AON", "AOS", "APA", "APD", "APH", "APTV", "ARE", "ATO", "AVB", "AVGO", "AVY", 
    "AWK", "AXP", "AZO", "BA", "BAC", "BAX", "BBWI", "BBY", "BDX", "BEN", "BIIB", "BIO", "BK", "BKNG", "BKR", "BLK", 
    "BMY", "BR", "BRO", "BSX", "BWA", "BX", "C", "CAG", "CAH", "CARR", "CAT", "CB", "CBOE", "CBRE", "CCI", "CCL",
    "CDNS", "CDW", "CE", "CEG", "CF", "CFG", "CHD", "CHRW", "CHTR", "CI", "CINF", "CL", "CLX", "CMA", 
    "CMCSA", "CME", "CMG", "CMI", "CMS", "CNC", "CNP", "COF", "COO", "COP", "COST", "CPB", "CPRT", "CPT", "CRL", 
    "CRM", "CSCO", "CSX", "CTAS", "CTLT", "CTRA", "CTSH", "CTVA", "CVS", "CVX", "D", "DAL", "DD", "DE", "DELL", 
    "DFS", "DG", "DGX", "DHI", "DHR", "DIS", "DLR", "DLTR", "DOV", "DOW", "DPZ", "DRI", "DTE", "DUK", "DVA", "DVN", 
    "DXC", "DXCM", "EA", "EBAY", "ECL", "ED", "EFX", "EIX", "EL", "EMN", "EMR", "ENPH", "EOG", "EPAM", "EQIX", 
    "EQR", "ES", "ESS", "ETN", "ETR", "EVRG", "EW", "EXC", "EXPD", "EXPE", "EXR", "F", "FANG", "FAST", "FCX", "FDS", 
    "FDX", "FE", "FFIV", "FIS", "FITB", "FLR", "FLS", "FMC", "FOX", "FOXA", "FRT", "FTI", "FTNT", "FTV", "GD", "GE", 
    "GILD", "GIS", "GL", "GLW", "GM", "GNRC", "GOOG", "GOOGL", "GPC", "GPN", "GPS", "GRMN", "GS", "GWW", "HAL", 
    "HAS", "HBAN", "HBI", "HCA", "HCI", "HIG", "HII", "HLT", "HOLX", "HON", "HPE", "HPQ", "HRL", "HSIC", "HST", 
    "HSY", "HUM", "HWM", "IBM", "ICE", "IDXX", "IEX", "IFF", "ILMN", "INCY", "INTC", "INTU", "IP", "IPG", "IPGP", 
    "IQV", "IR", "IRM", "ISRG", "IT", "ITW", "IVZ", "J", "JBHT", "JCI", "JKHY", "JNJ", "JNPR", "JPM", "K", "KEY", 
    "KEYS", "KHC", "KIM", "KLAC", "KMB", "KMI", "KMX", "KO", "KR", "KSS", "L", "LDOS", "LEG", "LEN", "LH", "LHX", 
    "LIN", "LKQ", "LLY", "LMT", "LNC", "LNT", "LOW", "LRCX", "LUMN", "LUV", "LYB", "MA", "MAA", "MAR", "MAS", 
    "MCD", "MCHP", "MCK", "MCO", "MDT", "MET", "META", "MGM", "MHK", "MKC", "MKTX", "MLM", "MMC", "MMM", "MNST", 
    "MO", "MOS", "MPC", "MPWR", "MRK", "MRO", "MS", "MSCI", "MSFT", "MSI", "MTB", "MTD", "MU", "NCLH", "NDAQ", 
    "NDSN", "NEE", "NEM", "NFLX", "NI", "NKE", "NOC", "NOV", "NRG", "NSC", "NTAP", "NTRS", "NUE", "NVDA", "NVR", 
    "NWL", "NWS", "NWSA", "O", "ODFL", "OKE", "OMC", "ORCL", "ORLY", "OTIS", "OXY", "PAYC", "PAYX", "PCAR", "PEG", 
    "PEP", "PFE", "PFG", "PG", "PGR", "PH", "PHM", "PKG", "PLD", "PLTR", "PM", "PNC", "PNR", "PNW", "POOL", "PPG", 
    "PPL", "PRGO", "PRU", "PSA", "PSX", "PTC", "PVH", "PWR", "PYPL", "QCOM", "QRVO", "RCL", "REG", "REGN", "RF", 
    "RHI", "RJF", "RL", "RMD", "ROK", "ROL", "ROP", "ROST", "RSG", "RTX", "SBAC", "SBUX", "SCHW", "SEE", "SHW", 
    "SJM", "SLB", "SNA", "SNPS", "SO", "SPG", "SPGI", "SRE", "STE", "STT", "STX", "STZ", "SWK", "SWKS", "SYF", 
    "SYK", "SYY", "T", "TAP", "TDG", "TDY", "TECH", "TEL", "TER", "TFC", "TFX", "TGNA", "TGT", "TJX", "TMO", "TMUS", 
    "TPR", "TRMB", "TROW", "TRV", "TSCO", "TSLA", "TSN", "TT", "TTWO", "TXN", "TXT", "TYL", "UA", "UAL", "UDR", 
    "UHS", "ULTA", "UNH", "UNM", "UNP", "UPS", "URI", "USB", "V", "VFC", "VLO", "VMC", "VNO", "VRSK", "VRSN", 
    "VRTX", "VTR", "VTRS", "VZ", "WAB", "WAT", "WBA", "WDC", "WEC", "WELL", "WFC", "WHR", "WM", "WMB", "WMT", 
    "WRB", "WST", "WY", "WYNN", "XEL", "XOM", "XRAY", "XYL", "YUM", "ZBH", "ZBRA", "ZION", "ZTS"
]



mydb = mysql.connector.connect(
    host="localhost",
    user="root",
    password="c0nygre",
    database="portfolio_manager"
)

mycursor = mydb.cursor()

def fetch_stock_data(ticker):
    stock = yf.Ticker(ticker)
    data = stock.history(period='1d')
    
    if not data.empty:
        latest_data = data.iloc[-1]
        ticker_symbol = ticker
        company_name = stock.info['shortName']
        current_price = stock.info.get('currentPrice')
        price_timestamp = datetime.now()
        opening_price = latest_data['Open']
        closing_price = latest_data['Close']
        
        return {
            'ticker_symbol': ticker,
            'company_name': company_name,
            'current_price': current_price,
            'price_timestamp': price_timestamp,
            'opening_price': opening_price,
            'closing_price': closing_price
        }
    
    else:
        return None

for ticker in sp500_tickers:
    latest_data = fetch_stock_data(ticker)
    
    if latest_data:
        sql = """
        INSERT INTO stocks (ticker_symbol, company_name, current_price, price_timestamp, opening_price, closing_price)
        VALUES (%s, %s, %s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE
            company_name=VALUES(company_name),
            current_price=VALUES(current_price),
            price_timestamp=VALUES(price_timestamp),
            opening_price=VALUES(opening_price),
            closing_price=VALUES(closing_price)
        """
        val = (
            latest_data['ticker_symbol'], latest_data['company_name'], latest_data['current_price'], 
            latest_data['price_timestamp'], latest_data['opening_price'], latest_data['closing_price']
        )
        mycursor.execute(sql, val)

mydb.commit()
print(mycursor.rowcount, "records inserted or updated.")

mycursor.close()
mydb.close()

