import streamlit as st
import re
import pandas as pd

# Mapping central banks to currency codes
bank_to_currency = {
    "Federal Reserve": "USD",
    "European Central Bank": "EUR", 
    "Bank of England": "GBP",
    "Reserve Bank of Australia": "AUD",
    "Reserve Bank of New Zealand": "NZD",
    "Bank of Japan": "JPY",
    "Bank of Canada": "CAD",
    "Swiss National Bank": "CHF"
}

# Define valid forex pairs
VALID_PAIRS = [
    'EUR/USD', 'GBP/USD', 'USD/JPY', 'USD/CHF', 'AUD/USD', 'USD/CAD', 'NZD/USD',
    'EUR/GBP', 'EUR/JPY', 'EUR/CHF', 'EUR/AUD', 'EUR/CAD', 'EUR/NZD',
    'GBP/JPY', 'GBP/CHF', 'GBP/AUD', 'GBP/CAD', 'GBP/NZD',
    'AUD/JPY', 'CAD/JPY', 'CHF/JPY', 'NZD/JPY',
    'AUD/CAD', 'AUD/CHF', 'AUD/NZD',
    'CAD/CHF', 'NZD/CAD', 'NZD/CHF'
]

st.set_page_config(page_title="Carry Drift Tracker", page_icon="💱", layout="wide")

st.title("💱 Carry Drift Tracker")
st.markdown("""
This tool helps identify favorable currency pairs for carry trades based on interest rate differentials.
Paste central bank interest rate table below (e.g., from FXStreet):
""")

# Sample data for user reference
with st.expander("📋 Sample Input Format (Click to expand)"):
    st.code("""Federal Reserve 5.50%
European Central Bank 4.50%
Bank of England 5.25%
Reserve Bank of Australia 4.35%
Reserve Bank of New Zealand 5.50%
Bank of Japan 0.10%
Bank of Canada 5.00%
Swiss National Bank 1.75%""")

raw_input = st.text_area("Paste Interest Rate Table Here", height=200, placeholder="Paste the interest rate table here...")

# Additional options
st.subheader("⚙️ Options")
min_differential = st.number_input("Minimum Rate Differential (%)", 
                                 min_value=0.0, max_value=10.0, value=0.1, step=0.1)

if st.button("🔍 Analyse", type="primary"):
    if not raw_input.strip():
        st.error("Please paste the interest rate table.")
    else:
        # Extract lines with central bank and rate
        lines = raw_input.splitlines()
        rate_data = []
        
        for line in lines:
            # More flexible regex pattern to handle different formats
            match = re.match(r"(.+?)\s+([\d.]+)\s*%?", line)
            if match:
                bank, rate = match.groups()
                currency = bank_to_currency.get(bank.strip())
                if currency:
                    rate_data.append((currency, float(rate)))
        
        if not rate_data:
            st.error("No valid interest rate data found. Please check the format.")
            st.info("Make sure the data includes central bank names and interest rates in percentage format.")
        else:
            # Create rates dictionary
            rates_dict = dict(rate_data)
            
            st.success(f"✅ Found interest rates for {len(rate_data)} currencies")
            
            # Display current rates
            with st.expander("📊 Current Interest Rates"):
                df_rates = pd.DataFrame(list(rates_dict.items()), columns=["Currency", "Rate"])
                st.dataframe(df_rates.sort_values("Rate", ascending=False), 
                           use_container_width=True, hide_index=True)
            
            # Generate results with long and short positions
            results_long = []  # For going LONG the base currency
            results_short = [] # For going SHORT the base currency
            
            for pair in VALID_PAIRS:
                base, quote = pair.split('/')
                if base in rates_dict and quote in rates_dict:
                    rate_base = rates_dict[base]
                    rate_quote = rates_dict[quote]
                    diff = rate_base - rate_quote
                    
                    if abs(diff) >= min_differential:
                        # Long position (buy base, sell quote)
                        results_long.append({
                            "Currency Pair": pair,
                            "Position": "Long",
                            "Rate Differential (%)": round(diff, 3),
                            "Carry": "Earn" if diff > 0 else "Pay",
                            "Base Rate": rate_base,
                            "Quote Rate": rate_quote,
                            "Description": f"Buy {base}, Sell {quote}"
                        })
                        
                        # Short position (sell base, buy quote) - opposite differential
                        results_short.append({
                            "Currency Pair": pair,
                            "Position": "Short", 
                            "Rate Differential (%)": round(-diff, 3),  # Reverse the sign
                            "Carry": "Earn" if diff < 0 else "Pay",   # Opposite of long
                            "Base Rate": rate_base,
                            "Quote Rate": rate_quote,
                            "Description": f"Sell {base}, Buy {quote}"
                        })
            
            if not results_long:
                st.warning("No pairs found meeting the minimum rate differential criteria.")
            else:
                df_long = pd.DataFrame(results_long)
                df_short = pd.DataFrame(results_short)
                
                # Show earning opportunities for both long and short
                st.subheader("💰 Earn Interest Opportunities")
                
                # Long positions that earn
                long_earn = df_long[df_long["Carry"] == "Earn"].sort_values("Rate Differential (%)", ascending=False)
                # Short positions that earn  
                short_earn = df_short[df_short["Carry"] == "Earn"].sort_values("Rate Differential (%)", ascending=False)
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("**By Going LONG:**")
                    if not long_earn.empty:
                        st.dataframe(long_earn[["Currency Pair", "Description", "Rate Differential (%)", "Base Rate", "Quote Rate"]], 
                                   use_container_width=True, hide_index=True)
                    else:
                        st.info("No long positions earn interest")
                        
                with col2:
                    st.markdown("**By Going SHORT:**")
                    if not short_earn.empty:
                        st.dataframe(short_earn[["Currency Pair", "Description", "Rate Differential (%)", "Base Rate", "Quote Rate"]], 
                                   use_container_width=True, hide_index=True)
                    else:
                        st.info("No short positions earn interest")
                
                # Show costly positions
                st.subheader("💸 Pay Interest Positions")
                
                # Long positions that cost
                long_pay = df_long[df_long["Carry"] == "Pay"].sort_values("Rate Differential (%)", ascending=True)
                # Short positions that cost
                short_pay = df_short[df_short["Carry"] == "Pay"].sort_values("Rate Differential (%)", ascending=True)
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("**By Going LONG:**")
                    if not long_pay.empty:
                        st.dataframe(long_pay[["Currency Pair", "Description", "Rate Differential (%)", "Base Rate", "Quote Rate"]], 
                                   use_container_width=True, hide_index=True)
                    else:
                        st.info("No long positions pay interest")
                        
                with col2:
                    st.markdown("**By Going SHORT:**")  
                    if not short_pay.empty:
                        st.dataframe(short_pay[["Currency Pair", "Description", "Rate Differential (%)", "Base Rate", "Quote Rate"]], 
                                   use_container_width=True, hide_index=True)
                    else:
                        st.info("No short positions pay interest")
                
                # Summary statistics
                st.subheader("📈 Summary")
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Total Opportunities", len(results_long) + len(results_short))
                with col2:
                    st.metric("Earn Opportunities", len(long_earn) + len(short_earn))
                with col3:
                    st.metric("Long Earn", len(long_earn))
                with col4:
                    st.metric("Short Earn", len(short_earn))
                
                # Download option
                all_results = pd.concat([df_long, df_short], ignore_index=True)
                csv = all_results.to_csv(index=False)
                st.download_button(
                    label="📥 Download All Results as CSV",
                    data=csv,
                    file_name="carry_trade_analysis.csv",
                    mime="text/csv"
                )

# Suggested enhancement for your analysis
carry_implications = {
    "High Positive Differential (>2%)": {
        "Trend Bias": "Bullish in risk-on environments",
        "Risk": "Sharp reversals during risk-off",
        "Typical Behavior": "Trends well, shallow pullbacks"
    },
    "Moderate Positive (0.5-2%)": {
        "Trend Bias": "Mildly bullish",
        "Risk": "Moderate reversal risk", 
        "Typical Behavior": "Mixed direction, sentiment-dependent"
    },
    "Near Zero": {
        "Trend Bias": "Neutral",
        "Risk": "Low carry-related risk",
        "Typical Behavior": "Driven by other fundamentals"
    },
    "Negative Differential": {
        "Trend Bias": "Bearish in risk-on, bullish in risk-off",
        "Risk": "Carry costs accumulate",
        "Typical Behavior": "Often range-bound with spikes"
    }
}
# Footer
st.markdown("---")
st.markdown("""
**💡 Trading Tips:**
- **Earn Interest**: Go LONG when base rate > quote rate, or SHORT when base rate < quote rate
- **Pay Interest**: Go LONG when base rate < quote rate, or SHORT when base rate > quote rate  
- Always verify actual swap rates with your broker before trading
- Consider other factors like volatility and economic conditions
- Higher interest rate differentials typically mean higher potential carry returns
""")
