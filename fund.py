from flask import Flask, render_template, request,session
import yfinance as yf
import pandas as pd
import google.generativeai as genai
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import os
from prettytable import PrettyTable
api=os.getenv("makersuite")
genai.configure(api_key=api)
model=genai.GenerativeModel('gemini-1.5-flash')
fund=Flask(__name__)
fund.secret_key="ccmccxbnhh"

def plot_stock_price(stock_code):
    stock=yf.Ticker(stock_code)
    hist=stock.history(period="1y")
    if hist.empty:
        return None
    img_dir = "static"
    if not os.path.exists(img_dir):
        os.makedirs(img_dir)
    plt.figure(figsize=(10, 5))
    plt.plot(hist.index, hist['Close'], label=f"{stock_code} Closing Price", color='blue')
    plt.title(f"{stock_code} Stock Price (Last 1 Year)")
    plt.xlabel("Date")
    plt.ylabel("Closing Price (USD)")
    plt.legend()
    plt.grid(True)
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
    plt.xticks(rotation=45)
    img_path = os.path.join(img_dir, f"{stock_code}_stock.png")
    plt.savefig(img_path)
    plt.close()
    return f"/{img_path}" 

def get_basic_company_info(stock_code):
    stock=yf.Ticker(stock_code)
    table = PrettyTable()
    table.field_names = ["Attribute", "Value"]
    table.add_row(["Stock Code", stock_code])
    table.add_row(["Company Name", stock.info.get('longName', 'N/A')])
    table.add_row(["Sector",stock.info.get('sector', 'N/A')])
    table.add_row(["Industry", stock.info.get('industry', 'N/A')])
    table.add_row(["Employees",stock.info.get('fullTimeEmployees', 'N/A')])
    table.add_row(["Company Summary",stock.info.get('longBusinessSummary', 'N/A')[:200] + "..."])
    table.add_row(["Website",stock.info.get('website', 'N/A')])
    return table.get_html_string()

@fund.route("/", methods=["GET", "POST"])
def index():
    return render_template("index.html")

@fund.route("/main", methods=["GET", "POST"])
def main():
    if request.method == "POST":
        stock_code = request.form.get("q", "").upper()
        stock = yf.Ticker(stock_code)
        if stock.info and stock.info.get("symbol"):
            session["stock_code"] = stock_code
            return render_template("main.html")
        else:
            return render_template("main.html", error="The stock code you entered is invalid.")
    return render_template("main.html")
@fund.route("/info", methods=["GET", "POST"])
def info():
    return render_template("info.html")

@fund.route("/introduction", methods=["GET", "POST"])
def introduction():
    stock_code=session.get("stock_code")
    stock=yf.Ticker(stock_code)
    company_name=stock.info.get("longName","N/A")
    company_info = get_basic_company_info(stock_code)
    return (render_template("introduction.html",company_name=company_name,company_info=company_info))

@fund.route("/financial_info", methods=["GET", "POST"])
def financial_info():
    stock_code=session.get("stock_code")
    stock=yf.Ticker(stock_code)
    company_name=stock.info.get("longName","N/A")
    financial_info= pd.concat([
                    stock.balance_sheet.loc[["Total Assets","Total Debt","Stockholders Equity"]],
                    stock.financials.loc[["Total Revenue","EBIT","Net Income","Basic EPS"]],
                    stock.cash_flow.loc[["Free Cash Flow","Financing Cash Flow","Investing Cash Flow","Operating Cash Flow"]]])
    financial_info=financial_info.to_html(classes='table table-bordered table-striped')
    return (render_template("financial_info.html",company_name=company_name,financial_info=financial_info))

@fund.route("/stock_info", methods=["GET", "POST"])
def stock_info():
    stock_code=session.get("stock_code")
    stock=yf.Ticker(stock_code)
    company_name=stock.info.get("longName","N/A")
    stock_info= {
        "Sector": stock.info.get("sector","N/A"),
        "Market Price": stock.info.get("currentPrice","N/A"),
        "Day High": stock.info.get("dayHigh","N/A"),
        "Day Low": stock.info.get("dayLow","N/A"),
        "Last Close Price": stock.info.get("previousClose","N/A"),
        "Open Price": stock.info.get("open","N/A"),
        "ROA": stock.info.get("returnOnAssets","N/A"),
        "ROE": stock.info.get("returnOnEquity","N/A")}
    stock_df = pd.DataFrame.from_dict(stock_info, orient="index", columns=["Value"])
    stock_html=stock_df.to_html(classes='table table-bordered table-striped')
    img_path=plot_stock_price(stock_code)
    return (render_template("stock_info.html",company_name=company_name,stock_code=stock_code,stock_info=stock_html,img=img_path))

@fund.route("/homepage", methods=["GET", "POST"])
def homepage():
    return render_template("main.html")

@fund.route("/ms", methods=["GET", "POST"])
def ms():
    return render_template("ms.html")

@fund.route("/genAI", methods=["GET", "POST"])
def genAI():
    return render_template("genAI.html")

@fund.route("/genAI_result", methods=["GET", "POST"])
def genAI_result():
    q=request.form.get("q")
    r=model.generate_content(q).candidates[0].content.parts[0].text
    return (render_template("genAI_result.html",r=r))

@fund.route("/investment", methods=["GET", "POST"])
def investment():
    stock_code=session.get("stock_code")
    stock=yf.Ticker(stock_code)
    company_name=stock.info.get("longName","N/A")
    currentPrice=stock.info.get("currentPrice","N/A")
    return render_template("investment.html",currentPrice=currentPrice,company_name=company_name)

@fund.route("/investment_result", methods=["GET", "POST"])
def investment():
    stock_code=session.get("stock_code")
    stock=yf.Ticker(stock_code)
    company_name=stock.info.get("longName","N/A")
    currentPrice=stock.info.get("currentPrice","N/A")
    amount=request.form.get("q")
    quantity=amount/currentPrice
    return (render_template("investment.html",amount=amount,company_name=company_name,quantity=quantity))
if __name__ == "__main__":
    fund.run()

