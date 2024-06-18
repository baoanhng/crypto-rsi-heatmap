import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from pycoingecko import CoinGeckoAPI
from tqdm import tqdm
from tradingview_ta import get_multiple_analysis

cg = CoinGeckoAPI()


def get_RSI(coins: list) -> dict:
    exchange = "BINANCE"

    # Format symbols exchange:symbol
    symbols = [f"{exchange.upper()}:{symbol}" for symbol in coins]

    analysis = get_multiple_analysis(symbols=symbols, interval="1d", screener="crypto")

    # For each symbol get the RSI
    rsi_dict = {}
    for symbol in tqdm(symbols):
        if analysis[symbol] is None:
            # print(f"No analysis for {symbol}")
            continue
        clean_symbol = symbol.replace(f"{exchange.upper()}:", "")
        clean_symbol = clean_symbol.replace("USDT", "")
        rsi_dict[clean_symbol] = analysis[symbol].indicators["RSI"]

    return rsi_dict


def get_top_vol_coins(length: int = 50) -> list:
    # Maybe add some caching for this
    df = pd.DataFrame(cg.get_coins_markets("usd"))["symbol"].str.upper() + "USDT"

    # Also add symbols that give issues
    stableCoins = [
        "OKBUSDT",
        "DAIUSDT",
        "USDTUSDT",
        "USDCUSDT",
        "BUSDUSDT",
        "TUSDUSDT",
        "PAXUSDT",
        "EURUSDT",
        "GBPUSDT",
        "CETHUSDT",
        "WBTCUSDT",
    ]
    sorted_volume = df[~df.isin(stableCoins)]
    return sorted_volume[:length].tolist()


def plot_rsi_heatmap():
    print("Getting top volume cryptos...")
    top_vol = get_top_vol_coins(50)
    print("Getting RSI values...")
    data = get_RSI(top_vol)

    # Create lists of labels and RSI values
    labels = list(data.keys())
    rsi_values = list(data.values())

    # Calculate the average RSI value
    average_rsi = np.mean(rsi_values)

    # Create the scatter plot
    fig, ax = plt.subplots(figsize=(20, 10))
    fig.patch.set_facecolor("black")  # Set the background color of the figure to black
    ax.set_facecolor("black")  # Set the background color of the axes to black

    # Define the color for each RSI range
    color_map = [
        (100, 70, "red", "Overbought"),
        (70, 60, "darkred", "Strong"),
        (60, 40, "black", "Neutral"),
        (40, 30, "darkgreen", "Weak"),
        (30, 0, "green", "Oversold"),
    ]

    # Fill the areas with the specified colors and create custom legend
    legend_elements = []
    for start, end, color, label in color_map:
        ax.fill_between([0, len(labels) + 2], start, end, color=color, alpha=0.3)

        # Add the label to the custom legend
        if color == "black":
            color = "grey"
        legend_elements.append(plt.Line2D([0], [0], color=color, lw=4, label=label))

    # Plot each point with a white border for visibility
    for i, label in enumerate(labels):
        ax.scatter(i + 1, rsi_values[i], color="white", edgecolor="black")
        ax.annotate(
            label,
            (i + 1, rsi_values[i]),
            color="white",
            textcoords="offset points",
            xytext=(0, 10),
            ha="center",
        )

    # Draw the average RSI line and add the annotation
    ax.axhline(xmin=0, xmax=1, y=average_rsi, color="orange", linestyle="--")
    ax.text(
        len(labels) + 2,
        average_rsi,
        f"AVG RSI: {average_rsi:.2f}",
        color="orange",
        va="bottom",
        ha="center",
        fontsize=16,
    )

    # Set the color of the tick labels to white
    ax.tick_params(colors="white", which="both")

    # Set the y-axis limits based on RSI values
    ax.set_ylim(min(rsi_values) - 5, max(rsi_values) + 5)

    ax.set_xlim(0, len(labels) + 2)

    # Remove the x-axis ticks since we're annotating each point
    ax.set_xticks([])

    # Create the legend at the top
    ax.legend(
        handles=legend_elements,
        loc="upper center",
        bbox_to_anchor=(0.5, 1.05),
        ncol=5,
        fancybox=True,
        shadow=True,
        frameon=False,
        fontsize="large",
        labelcolor="white",
    )

    # Add y-axis label
    ax.set_ylabel("RSI", color="white", fontsize=12)
    ax.set_xlabel("Top 50 coins (volume)", color="white", fontsize=12)

    # Display the plot
    plt.tight_layout()

    plt.show()


if __name__ == "__main__":
    plot_rsi_heatmap()
