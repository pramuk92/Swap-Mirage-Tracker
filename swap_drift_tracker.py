import streamlit as st
import re
import pandas as pd
from itertools import permutations

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

st.title("💱 Carry Drift Tracker")
st.markdown("Paste central bank interest rate table below (e.g., from FXStreet):")

raw_input = st.text_area("📋 Paste Interest Rate Table", height=300)

if st.button("🔍 Analyse"):
    # Extract lines with central bank and rate
    lines = raw_input.splitlines()
    rate_data = []
    for line in lines:
        match = re.match(r"(.+?)\s+([\d.]+)\s*%", line)
        if match:
            bank, rate = match.groups()
            currency = bank_to_currency.get(bank.strip())
            if currency:
                rate_data.append((currency, float(rate)))

    if not rate_data:
        st.error("No valid interest rate data found.")
    else:
        df_rates = pd.DataFrame(rate_data, columns=["Currency", "Rate"])
        pairs = list(permutations(df_rates["Currency"], 2))

        results = []
        for base, quote in pairs:
            rate_base = df_rates[df_rates["Currency"] == base]["Rate"].values[0]
            rate_quote = df_rates[df_rates["Currency"] == quote]["Rate"].values[0]
            diff = rate_base - rate_quote
            direction = "Earn (positive carry)" if diff > 0 else "Pay (negative carry)"
            results.append({
                "Pair": f"{base}/{quote}",
                "Long {base}": direction,
                "Rate Differential (%)": round(diff, 3)
            })

        df_result = pd.DataFrame(results)
        df_result = df_result.sort_values(by="Rate Differential (%)", ascending=False).reset_index(drop=True)

        st.success("✅ Analysis Complete")
        st.dataframe(df_result, use_container_width=True)
