import streamlit as st
import re
import pandas as pd
from itertools import combinations

# Mapping central banks to currency codes (expanded with more common pairs)
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

# Define valid forex pairs (you can expand this list)
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
col1, col2 = st.columns(2)
with col1:
    min_differential = st.number_input("Minimum Rate Differential (%)", 
                                     min_value=0.0, max_value=10.0, value=0.1, step=0.1)
with col2:
    show_all_pairs = st.checkbox("Show all valid pairs", value=True)

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
            # Create rates dataframe and dictionary
            df_rates = pd.DataFrame(rate_data, columns=["Currency", "Rate"])
            rates_dict = dict(rate_data)
            
            st.success(f"✅ Found interest rates for {len(rate_data)} currencies")
            
            # Display current rates
            with st.expander("📊 Current Interest Rates"):
                st.dataframe(df_rates.sort_values("Rate", ascending=False), 
                           use_container_width=True, hide_index=True)
            
            # Generate valid pairs and calculate differentials
            results = []
            for pair in VALID_PAIRS:
                base, quote = pair.split('/')
                if base in rates_dict and quote in rates_dict:
                    rate_base = rates_dict[base]
                    rate_quote = rates_dict[quote]
                    diff = rate_base - rate_quote
                    
                    # Only include pairs meeting minimum differential
                    if abs(diff) >= min_differential:
                        if diff > 0:
                            direction = f"Long {base}/{quote}"
                            carry_type = "Earn"
                            recommendation = "✅ Favorable"
                        else:
                            direction = f"Short {base}/{quote} (Long {quote}/{base})"
                            carry_type = "Pay"
                            recommendation = "⚠️ Costly"
                        
                        results.append({
                            "Currency Pair": pair,
                            "Trade Direction": direction,
                            "Rate Differential (%)": round(diff, 3),
                            "Carry": carry_type,
                            "Recommendation": recommendation,
                            "Base Rate": rate_base,
                            "Quote Rate": rate_quote
                        })
            
            if not results:
                st.warning("No pairs found meeting the minimum rate differential criteria.")
            else:
                df_result = pd.DataFrame(results)
                
                # Separate favorable and costly trades
                df_favorable = df_result[df_result["Rate Differential (%)"] > 0].sort_values(
                    "Rate Differential (%)", ascending=False)
                df_costly = df_result[df_result["Rate Differential (%)"] < 0].sort_values(
                    "Rate Differential (%)", ascending=True)
                
                # Display favorable trades
                st.subheader("🎯 Favorable Carry Trades (Earn Interest)")
                if not df_favorable.empty:
                    st.dataframe(df_favorable[["Currency Pair", "Trade Direction", "Rate Differential (%)", "Base Rate", "Quote Rate"]], 
                               use_container_width=True, hide_index=True)
                else:
                    st.info("No favorable carry trades found.")
                
                # Display costly trades
                st.subheader("⚠️ Costly Carry Trades (Pay Interest)")
                if not df_costly.empty:
                    st.dataframe(df_costly[["Currency Pair", "Trade Direction", "Rate Differential (%)", "Base Rate", "Quote Rate"]], 
                               use_container_width=True, hide_index=True)
                else:
                    st.info("No costly carry trades found.")
                
                # Summary statistics
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Total Pairs Found", len(results))
                with col2:
                    st.metric("Favorable Trades", len(df_favorable))
                with col3:
                    st.metric("Costly Trades", len(df_costly))
                
                # Download option
                csv = df_result.to_csv(index=False)
                st.download_button(
                    label="📥 Download Results as CSV",
                    data=csv,
                    file_name="carry_trade_analysis.csv",
                    mime="text/csv"
                )

# Footer
st.markdown("---")
st.markdown("""
**💡 Tips:**
- Positive differential means you EARN interest when going long the base currency
- Negative differential means you PAY interest when going long the base currency  
- Always verify actual swap rates with your broker before trading
- Consider other factors like volatility and economic conditions
""")
