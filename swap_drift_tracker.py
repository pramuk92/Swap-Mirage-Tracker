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

# Carry trade implications analysis
def analyze_carry_implications(rate_differential, pair):
    """
    Analyze trend implications based on carry trade dynamics
    """
    abs_diff = abs(rate_differential)
    
    if abs_diff > 2.0:  # Large differential
        if rate_differential > 0:
            return {
                "Trend Bias": "Strongly Bullish in Risk-On",
                "Risk Level": "High",
                "Market Behavior": "Trends persistently, shallow pullbacks",
                "Warning": "Violent reversal risk during risk-off events",
                "Trading Context": "Classic carry trade - monitor VIX and risk sentiment"
            }
        else:
            return {
                "Trend Bias": "Bearish in Risk-On / Bullish in Risk-Off", 
                "Risk Level": "High",
                "Market Behavior": "Often weak in stable markets, spikes in crises",
                "Warning": "Funding currency - can rally sharply during risk-off",
                "Trading Context": "Safe haven flows dominate during stress"
            }
    
    elif abs_diff > 0.5:  # Moderate differential
        if rate_differential > 0:
            return {
                "Trend Bias": "Mildly Bullish",
                "Risk Level": "Medium",
                "Market Behavior": "Moderate trending, sentiment-dependent",
                "Warning": "Moderate reversal risk",
                "Trading Context": "Watch overall risk appetite and central bank guidance"
            }
        else:
            return {
                "Trend Bias": "Mixed",
                "Risk Level": "Medium", 
                "Market Behavior": "Range-bound with directional spikes",
                "Warning": "Carry costs accumulate over time",
                "Trading Context": "Driven by technicals and other fundamentals"
            }
    
    else:  # Small differential
        return {
            "Trend Bias": "Neutral",
            "Risk Level": "Low",
            "Market Behavior": "Driven by other fundamentals",
            "Warning": "Low carry influence",
            "Trading Context": "Technical analysis and other macro factors dominate"
        }

# Risk sentiment classification for pairs
risk_sentiment_pairs = {
    "High Risk Appetite (Carry Trades)": ["AUD/JPY", "NZD/JPY", "EUR/AUD", "GBP/AUD", "AUD/NZD"],
    "Risk Off (Safe Havens)": ["USD/JPY", "USD/CHF", "JPY pairs"],
    "Moderate Risk": ["EUR/USD", "GBP/USD", "USD/CAD", "EUR/GBP"]
}

st.set_page_config(page_title="Carry Drift Tracker", page_icon="💱", layout="wide")

st.title("💱 Advanced Carry Drift Tracker")
st.markdown("""
This tool helps identify favorable currency pairs for carry trades based on interest rate differentials,
including analysis of trend implications and market behavior patterns.
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

show_analysis = st.checkbox("Show Detailed Trend Analysis", value=True)

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
                        # Get trend analysis
                        analysis = analyze_carry_implications(diff, pair)
                        
                        # Long position (buy base, sell quote)
                        results_long.append({
                            "Currency Pair": pair,
                            "Position": "Long",
                            "Rate Differential (%)": round(diff, 3),
                            "Carry": "Earn" if diff > 0 else "Pay",
                            "Base Rate": rate_base,
                            "Quote Rate": rate_quote,
                            "Description": f"Buy {base}, Sell {quote}",
                            "Trend Bias": analysis["Trend Bias"],
                            "Risk Level": analysis["Risk Level"],
                            "Market Behavior": analysis["Market Behavior"]
                        })
                        
                        # Short position (sell base, buy quote) - opposite differential
                        short_analysis = analyze_carry_implications(-diff, pair)
                        results_short.append({
                            "Currency Pair": pair,
                            "Position": "Short", 
                            "Rate Differential (%)": round(-diff, 3),  # Reverse the sign
                            "Carry": "Earn" if diff < 0 else "Pay",   # Opposite of long
                            "Base Rate": rate_base,
                            "Quote Rate": rate_quote,
                            "Description": f"Sell {base}, Buy {quote}",
                            "Trend Bias": short_analysis["Trend Bias"],
                            "Risk Level": short_analysis["Risk Level"],
                            "Market Behavior": short_analysis["Market Behavior"]
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
                        display_cols = ["Currency Pair", "Description", "Rate Differential (%)", "Base Rate", "Quote Rate"]
                        if show_analysis:
                            display_cols.extend(["Trend Bias", "Risk Level"])
                        
                        st.dataframe(long_earn[display_cols], 
                                   use_container_width=True, hide_index=True)
                    else:
                        st.info("No long positions earn interest")
                        
                with col2:
                    st.markdown("**By Going SHORT:**")
                    if not short_earn.empty:
                        display_cols = ["Currency Pair", "Description", "Rate Differential (%)", "Base Rate", "Quote Rate"]
                        if show_analysis:
                            display_cols.extend(["Trend Bias", "Risk Level"])
                            
                        st.dataframe(short_earn[display_cols], 
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
                        display_cols = ["Currency Pair", "Description", "Rate Differential (%)", "Base Rate", "Quote Rate"]
                        if show_analysis:
                            display_cols.extend(["Trend Bias", "Risk Level"])
                            
                        st.dataframe(long_pay[display_cols], 
                                   use_container_width=True, hide_index=True)
                    else:
                        st.info("No long positions pay interest")
                        
                with col2:
                    st.markdown("**By Going SHORT:**")  
                    if not short_pay.empty:
                        display_cols = ["Currency Pair", "Description", "Rate Differential (%)", "Base Rate", "Quote Rate"]
                        if show_analysis:
                            display_cols.extend(["Trend Bias", "Risk Level"])
                            
                        st.dataframe(short_pay[display_cols], 
                                   use_container_width=True, hide_index=True)
                    else:
                        st.info("No short positions pay interest")
                
                # Detailed Trend Analysis Section
                if show_analysis:
                    st.subheader("📈 Detailed Trend Analysis")
                    
                    # Show high-impact pairs first
                    high_impact = df_long[df_long["Rate Differential (%)"].abs() > 2.0]
                    if not high_impact.empty:
                        st.markdown("**🎯 High Impact Carry Pairs (|Differential| > 2%)**")
                        st.markdown("*These pairs show strong trend characteristics and require careful risk management*")
                        
                        for _, row in high_impact.iterrows():
                            with st.expander(f"📊 {row['Currency Pair']} - {row['Rate Differential (%)']}% Differential"):
                                col1, col2 = st.columns(2)
                                with col1:
                                    st.metric("Rate Differential", f"{row['Rate Differential (%)']}%")
                                    st.metric("Trend Bias", row['Trend Bias'])
                                    st.metric("Risk Level", row['Risk Level'])
                                with col2:
                                    st.write("**Market Behavior:**")
                                    st.info(row['Market Behavior'])
                                    st.write("**Trading Context:**")
                                    if row['Rate Differential (%)'] > 0:
                                        st.warning("Classic carry trade - monitor risk sentiment closely")
                                    else:
                                        st.warning("Funding currency - can spike during risk-off events")
                
                # Summary statistics
                st.subheader("📊 Summary")
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Total Opportunities", len(results_long) + len(results_short))
                with col2:
                    st.metric("Earn Opportunities", len(long_earn) + len(short_earn))
                with col3:
                    st.metric("High Impact Pairs", len(df_long[df_long["Rate Differential (%)"].abs() > 2.0]))
                with col4:
                    st.metric("Moderate Pairs", len(df_long[(df_long["Rate Differential (%)"].abs() > 0.5) & 
                                                          (df_long["Rate Differential (%)"].abs() <= 2.0)]))
                
                # Download option
                all_results = pd.concat([df_long, df_short], ignore_index=True)
                csv = all_results.to_csv(index=False)
                st.download_button(
                    label="📥 Download All Results as CSV",
                    data=csv,
                    file_name="carry_trade_analysis.csv",
                    mime="text/csv"
                )

# Enhanced Footer with Trading Education
st.markdown("---")
st.markdown("""
**🎓 Carry Trade Educational Guide**

**💡 Key Concepts:**
- **Carry Trade**: Borrow low-yield currency, invest in high-yield currency
- **Risk-On**: Carry trades perform well (high-yield currencies appreciate)  
- **Risk-Off**: Carry trades unwind violently (high-yield currencies crash)

**📊 Risk Sentiment Indicators to Monitor:**
- **VIX Index** (Fear Gauge) - above 20 = caution for carry trades
- **Equity Markets** - rising stocks = favorable for carry
- **Bond Yield Spreads** - widening = stronger carry momentum
- **Central Bank Guidance** - future rate expectations matter most

**⚡ Trading Implications:**
- **Large Differentials (>2%)**: Strong trends but high reversal risk
- **Moderate Differentials (0.5-2%)**: Good balance of carry and manageable risk
- **Small Differentials (<0.5%)**: Carry has minimal influence on price action

**🔍 Always Remember:**
- Verify actual swap rates with your broker
- Carry trades work until they don't - then they reverse fast
- Use proper position sizing and risk management
- Monitor overall market sentiment and economic conditions
""")
