import yfinance as yf
import matplotlib.pyplot as plt
import seaborn as sns
import os
from django.shortcuts import render
from django.conf import settings
from django.http import HttpResponse

def stocks_home(request):
    return render(request, "stocks/index.html")

def form_page(request):
    return render(request, "stocks/stock_form.html")

def process_form(request):
    if request.method == "POST":
        stock_name = request.POST.get("stock_name")
        from_date = request.POST.get("from_date")
        to_date = request.POST.get("to_date")

        # Fetch stock data
        stock = yf.Ticker(stock_name)
        df = stock.history(start=from_date, end=to_date)

        if df.empty:
            return render(request, "stocks/stock_results.html", {"error": "No data found for the given inputs."})

        # Keep a copy of the full dataset for download
        df_full = df.copy()

        # Limit the displayed results to only 5 rows
        df_display = df.head(5)

        # Select relevant columns
        df_display = df_display[['Open', 'Close', 'High', 'Low', 'Volume']]
        df_full = df_full[['Open', 'Close', 'High', 'Low', 'Volume']]

        # Compute correlation matrix
        correlation_matrix = df_display.corr()

        # Compute key metrics for stock analysis
        start_price = df_display.iloc[0]['Close']
        end_price = df_display.iloc[-1]['Close']
        price_change = end_price - start_price
        price_change_percent = (price_change / start_price) * 100
        avg_volume = df_display['Volume'].mean()
        max_price = df_display['High'].max()
        min_price = df_display['Low'].min()

        # Determine trend direction
        if price_change > 0:
            trend = "The stock has been performing well, showing an upward trend."
        else:
            trend = "The stock has been declining, indicating a downward trend."

        # Determine volatility (price fluctuation)
        volatility = df_display['Close'].pct_change().std() * 100 

        if volatility > 2:
            volatility_text = "The stock is highly volatile, meaning prices fluctuate significantly."
        else:
            volatility_text = "The stock is relatively stable with minimal fluctuations."

        # Generate analysis paragraph
        stock_analysis = f"""
        The stock {stock_name} started at {start_price:.2f} and closed at {end_price:.2f}, 
        showing a {price_change_percent:.2f}% {"increase 📈" if price_change > 0 else "decrease 📉"} over the selected period. 
        The highest price recorded was {max_price:.2f}, while the lowest was {min_price:.2f}.
        The average trading volume was {avg_volume:,.0f} shares per day. 
        {trend} {volatility_text}
        """

        # Save session data for CSV downloads
        request.session["csv_data"] = df_display.to_csv()  
        request.session["full_csv_data"] = df_full.to_csv()  
        request.session["correlation_csv"] = correlation_matrix.to_csv()

        # Generate heatmap
        plt.figure(figsize=(8, 6))
        sns.heatmap(correlation_matrix, annot=True, cmap="coolwarm", fmt=".2f", linewidths=0.5)
        img_path = os.path.join(settings.MEDIA_ROOT, "correlation_heatmap.png")
        plt.savefig(img_path)
        plt.close()

        # Convert tables to HTML
        stock_data = list(zip(df_display.index, df_display.values.tolist()))
        correlation_html = correlation_matrix.to_html()

        return render(request, "stocks/stock_results.html", {
            "stock_name": stock_name,
            "stock_columns": df_display.columns.tolist(),
            "stock_data": stock_data,
            "correlation": correlation_matrix.to_html(),
            "correlation_image": settings.MEDIA_URL + "correlation_heatmap.png",
            "stock_analysis": stock_analysis
        })

    return render(request, "stocks/stock_form.html")

def download_csv(request):
    full_csv_data = request.session.get("full_csv_data", "")

    if not full_csv_data:
        return HttpResponse("No full stock data available for download.", content_type="text/plain")

    response = HttpResponse(full_csv_data, content_type="text/csv")
    response["Content-Disposition"] = 'attachment; filename="full_stock_data.csv"'
    return response

def download_correlation(request):
    correlation_csv = request.session.get("correlation_csv", "")

    if not correlation_csv:
        return HttpResponse("No correlation data available", content_type="text/plain")

    response = HttpResponse(correlation_csv, content_type="text/csv")
    response["Content-Disposition"] = 'attachment; filename="correlation_data.csv"'
    return response
