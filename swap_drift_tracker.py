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

# Strategic watchlist creation
def create_strategic_watchlist(rates_dict):
    """
    Create categorized watchlist for systematic trading
    """
    watchlist = {
        "Primary Carry Trades": [],
        "Secondary Carry Trades": [], 
        "Risk-Off Hedges": [],
        "Neutral Pairs": []
    }
    
    for pair in VALID_PAIRS:
        base, quote = pair.split('/')
        if base in rates_dict and quote in rates_dict:
            diff = rates_dict[base] - rates_dict[quote]
            
            if diff > 2.0:  # Strong positive carry
                watchlist["Primary Carry Trades"].append({
                    "pair": pair,
                    "diff": diff,
                    "direction": "LONG",
                    "rationale": "High yield, strong trend potential",
                    "entry_strategy": "Buy pullbacks to daily support during risk-on"
                })
            elif diff > 0.5:  # Moderate carry
                watchlist["Secondary Carry Trades"].append({
                    "pair": pair, 
                    "diff": diff,
                    "direction": "LONG",
                    "rationale": "Moderate yield, good risk-reward",
                    "entry_strategy": "Buy technical breakouts with risk-on confirmation"
                })
            elif diff < -1.0:  # Negative carry (risk-off)
                watchlist["Risk-Off Hedges"].append({
                    "pair": pair,
                    "diff": diff, 
                    "direction": "SHORT" if diff > 0 else "LONG",
                    "rationale": "Safe haven, buy during stress",
                    "entry_strategy": "Buy during VIX spikes and risk-off events"
                })
            else:  # Neutral
                watchlist["Neutral Pairs"].append({
                    "pair": pair,
                    "diff": diff,
                    "direction": "NEUTRAL", 
                    "rationale": "Carry neutral, trade technically",
                    "entry_strategy": "Pure technical analysis, range trading"
                })
    
    # Sort each category by absolute differential
    for category in watchlist:
        watchlist[category].sort(key=lambda x: abs(x['diff']), reverse=True)
    
    return watchlist

# Entry rules for different pair types
def get_entry_rules(pair_type, pair_info):
    """
    Get specific entry rules for each pair type
    """
    rules = {
        "Primary Carry Trades": {
            "Timeframe": "Daily + 4HR confluence",
            "Entry Signal": "Pullback to 50-day EMA with bullish reversal",
            "Confirmation": "RSI (40-50) bounce, risk-on environment (VIX < 20)",
            "Stop Loss": "Below recent swing low (1-2% risk)",
            "Target": "Previous highs + 2:1 risk-reward",
            "Position Size": "1-2% account risk",
            "Management": "Trail stop to breakeven at +1%, partial profits at 1.5R"
        },
        "Secondary Carry Trades": {
            "Timeframe": "4HR + Daily alignment",
            "Entry Signal": "Break above consolidation with volume",
            "Confirmation": "MACD crossover, risk-on confirmation",
            "Stop Loss": "Below support level",
            "Target": "1.5:1 to 2:1 risk-reward", 
            "Position Size": "1% account risk",
            "Management": "Take partial profits at 1R, trail remainder"
        },
        "Risk-Off Hedges": {
            "Timeframe": "Daily + Weekly for timing",
            "Entry Signal": "VIX spike above 25, safe haven flows",
            "Confirmation": "Price breaking key resistance with momentum",
            "Stop Loss": "Wider stops (2-3%) due to volatility",
            "Target": "Quick 2-5% moves during panic",
            "Position Size": "0.5-1% account risk",
            "Management": "Quick profits, don't get greedy"
        },
        "Neutral Pairs": {
            "Timeframe": "4HR for entries",
            "Entry Signal": "Range breakout or bounce",
            "Confirmation": "Stochastic oversold/overbought reversals", 
            "Stop Loss": "Beyond range boundaries",
            "Target": "Opposite side of range",
            "Position Size": "1% account risk",
            "Management": "Range trading mentality"
        }
    }
    
    return rules.get(pair_type, {})

st.set_page_config(page_title="Advanced Carry Drift Tracker", page_icon="💱", layout="wide")

st.title("💱 Advanced Carry Drift Tracker")
st.markdown("""
This tool helps identify favorable currency pairs for carry trades based on interest rate differentials,
including systematic trading strategies and risk management frameworks.
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
show_strategy = st.checkbox("Show Systematic Trading Strategy", value=True)

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
                
                # Systematic Trading Strategy Section
                if show_strategy:
                    st.subheader("🎯 Systematic Trading Strategy")
                    
                    # Create strategic watchlist
                    watchlist = create_strategic_watchlist(rates_dict)
                    
                    # Display market regime guidance
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown("**📈 Risk-On Strategy (VIX < 20)**")
                        st.markdown("""
                        **Primary Actions:**
                        - Focus on LONG Primary Carry Trades
                        - Enter on pullbacks to daily support
                        - Use 4HR/Daily confluence for timing
                        
                        **Entry Example (USD/JPY):**
                        1. Wait for pullback to 50-day EMA
                        2. Bullish reversal candle pattern
                        3. RSI bounce from 40-50 zone
                        4. Enter with 1-2% stop loss
                        """)
                    
                    with col2: 
                        st.markdown("**📉 Risk-Off Strategy (VIX > 25)**")
                        st.markdown("""
                        **Defensive Actions:**
                        - Reduce carry trade exposure
                        - Consider Risk-Off Hedges
                        - Move to safe havens
                        
                        **Risk Management:**
                        - Tighten stops on carry trades
                        - Monitor correlation breakdowns  
                        - Prepare for violent reversals
                        """)
                    
                    # Display strategic watchlist with trading rules
                    st.markdown("**📋 Strategic Trading Watchlist**")
                    
                    for category, pairs in watchlist.items():
                        if pairs:  # Only show non-empty categories
                            with st.expander(f"**{category}** ({len(pairs)} pairs)", expanded=category=="Primary Carry Trades"):
                                for pair_info in pairs:
                                    st.markdown(f"**{pair_info['pair']}** - {pair_info['diff']:.2f}% differential")
                                    
                                    col1, col2 = st.columns([1, 2])
                                    with col1:
                                        st.write(f"**Direction:** {pair_info['direction']}")
                                        st.write(f"**Rationale:** {pair_info['rationale']}")
                                    with col2:
                                        st.write(f"**Entry Strategy:** {pair_info['entry_strategy']}")
                                    
                                    # Show detailed trading rules
                                    rules = get_entry_rules(category, pair_info)
                                    if rules:
                                        with st.expander("Detailed Trading Rules"):
                                            for rule_name, rule_value in rules.items():
                                                st.write(f"**{rule_name}:** {rule_value}")
                                    
                                    st.markdown("---")
                
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
**🎓 Advanced Carry Trade Educational Guide**

**💡 Systematic Trading Framework:**
- **Market Regime First**: Always assess risk-on/risk-off environment
- **Watchlist Categorization**: Trade Primary carries in risk-on, hedges in risk-off  
- **Multi-Timeframe**: Daily bias + 4HR entries for optimal timing
- **Risk Management**: 1-2% risk per trade, proper position sizing

**📊 Key Risk Sentiment Indicators:**
- **VIX Index**: <20 = risk-on, >25 = risk-off
- **SP500 Trend**: Above 200MA = favorable for carry
- **AUD/JPY Correlation**: Rising = risk-on, falling = risk-off
- **Treasury Yields**: Steepening = risk-on, flattening = caution

**⚡ Trading Psychology:**
- **Patience**: Carry trades develop over weeks/months
- **Discipline**: Stick to entry rules, don't chase moves
- **Flexibility**: Adapt to changing market regimes
- **Risk Awareness**: Know when carry trades are dangerous

**🔍 Always Verify:**
- Actual swap rates with your broker
- Current market sentiment and correlations
- Central bank policy expectations
- Technical alignment with fundamental bias
""")
