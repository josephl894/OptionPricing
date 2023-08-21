import yfinance as yf
from datetime import datetime, date
import numpy as np
import pandas as pd
import fetchYield
import volatilityIndexes
import monteCarloAmerican
import tkinter as tk
from tkinter import messagebox

class App:
    def __init__(self, root):
        self.ticker = None
        self.expiration = None
        self.option_type = None
        self.strike = None
        self.price = None
        self.T = None
        self.r = None
        self.sigma = None
        self.root = root
        self.root.title("Monte Carlo Simulation")
    
        # Create labels and entry widgets
        self.input_labels = ["Ticker:", "Expiration date (yyyy-mm-dd):", "call/put:", "Strike price:"]
        self.entries = []

        for label in self.input_labels:
            lbl = tk.Label(self.root, text=label)
            lbl.pack(anchor="w", padx=10, pady=5)
            entry = tk.Entry(self.root, width=40)
            entry.pack(padx=10, pady=5)
            self.entries.append(entry)

        submit_btn = tk.Button(self.root, text="Submit", command=self.on_submit)
        submit_btn.pack(pady=20)

    def on_submit(self):
        self.ticker = self.entries[0].get()
        self.expiration = self.entries[1].get()
        self.option_type = self.entries[2].get()
        self.strike = int(self.entries[3].get())

        transformed_values = self.transform()
        output_values = ["{:.2f}".format(x) for x in transformed_values]
        self.display_values([self.ticker, self.expiration , self.option_type, self.strike], output_values)
    
    def display_values(self, input_values, output_values):
        new_win = tk.Toplevel(self.root)
        new_win.title("Values")

        # Separator label for visual separation
        separator = tk.Label(new_win, text="INPUTS", font=("Arial", 12, "bold"), pady=10)
        separator.pack(fill="x")

        # Display the input values
        for input_label, value in zip(self.input_labels, input_values):
            display_label = tk.Label(new_win, text=f"{input_label} {value}", padx=10, pady=5)
            display_label.pack()

        # Create frames for outputs      
        output_frame = tk.Frame(new_win, padx=10, pady=10, bg="gray")
        output_frame.pack(fill="both", padx=10, pady=5)

        # Separator label for visual separation
        separator = tk.Label(new_win, text="OUTPUTS", font=("Arial", 12, "bold"), pady=10)
        separator.pack(fill="x")

        # Display the transformed (output) values with dummy "Output" labels
        output_labels = ["Real-time Price:", "HV/IV Ratio:", "Computed Price (Monte Carlos):", "%Difference:"]
        for output_label, value in zip(output_labels, output_values):
            display_label = tk.Label(new_win, text=f"{output_label} {value}", padx=10, pady=5)
            display_label.pack()

        # Close button for the new window
        close_btn = tk.Button(new_win, text="Close", command=new_win.destroy)
        close_btn.pack(pady=20)

    def get_realtime_option_premium(self, ticker, expiration, strike, option_type):
        #check for existing contract for given parameters
        try:
            opt = yf.Ticker(ticker).option_chain(expiration)
        except Exception as e:
            messagebox.showerror("Error", str(e))

        if option_type == 'call':
            options = opt.calls
        elif option_type == 'put':
            options = opt.puts
        else:
            raise ValueError("Invalid option type. Must be 'call' or 'put'.")
        
        # Filter by strike price
        try:
            strike in options[options['strike']]
            option_data = options[options['strike'] == strike]
        except Exception as e:
            messagebox.showerror("Error", str(e))
        
        if not option_data.empty:
            return option_data.iloc[0]['lastPrice']
        else:
            return None

    def fetch_implied_volatility(self, ticker, expiration, strike, option_type):
        # Get the option chain for the ticker and expiration date
        option_chain = yf.Ticker(ticker).option_chain(expiration)
        
        if option_type == "call":
            options = option_chain.calls
        elif option_type == "put":
            options = option_chain.puts
        else:
            raise ValueError("Invalid option type. Choose 'call' or 'put'.")

        # Find the option with the given strike price
        option_row = options[options['strike'] == strike]

        if not option_row.empty:
            return option_row
        else:
            return None

    def transform(self):
        try:
            stock = yf.Ticker(self.ticker)
        except Exception as e: #check ticker mispelling
            messagebox.showerror("Error", str(e))

        self.price = stock.history(period="1d")['Close'].iloc[0] #current stock price
        self.T = (datetime.strptime(self.expiration, "%Y-%m-%d") - datetime.utcnow()).days / 365 #time to expiration
        premium = self.get_realtime_option_premium(self.ticker, self.expiration, self.strike, self.option_type) #real-time option premium
        self.r = fetchYield.fetch_gov_yield(datetime.strptime(self.expiration,'%Y-%m-%d')) #fetch risk-free yield rate

        # MonteCarlo simulation
        option_row = self.fetch_implied_volatility(self.ticker, self.expiration, self.strike, self.option_type)
        self.sigma = option_row['impliedVolatility'].iloc[0] / 100
        MC_price = monteCarloAmerican.MC_american(self.price, self.strike, self.T, self.r, self.sigma)
        if self.option_type == "call":
            computed_MC_price = MC_price[0]
        elif self.option_type == "put":
            computed_MC_price = MC_price[1]
            
        # IV-HV ratio
        duration = 30 #using one month as a basis time range for computing HV and IV indexes
        hv_index = volatilityIndexes.calculate_historical_volatility_index(self.ticker, duration)

        # Print
        return [premium, self.sigma/hv_index, computed_MC_price, 100* ((computed_MC_price - premium)/premium)]

def main():
    root = tk.Tk()
    App(root)
    root.mainloop() 

if __name__ == "__main__":
    main()