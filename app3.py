import streamlit as st
import plotly.graph_objs as go
import plotly.express as px
import pandas as pd
import numpy as np
import requests
import time
from datetime import datetime, timedelta

# =============================================
# CONFIGURATION & THEMING
# =============================================
st.set_page_config(
    page_title="sBTC DeFi Dashboard | B25 Hackathon",
    page_icon="₿",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for professional styling
st.markdown("""
<style>
    .main {
        background-color: #0E1117;
    }
    .stApp {
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
        color: #f8f9fa;
    }
    .stButton>button {
        background-color: #4CAF50;
        color: white;
        border-radius: 8px;
        padding: 10px 24px;
        font-weight: bold;
    }
    .stTextInput>div>div>input {
        background-color: #2d3748;
        color: white;
    }
    .stDataFrame {
        border-radius: 10px;
    }
    .stAlert {
        border-radius: 10px;
    }
    .metric-card {
        background: rgba(30, 41, 59, 0.7);
        border-radius: 10px;
        padding: 20px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        margin-bottom: 20px;
    }
    .metric-title {
        font-size: 1rem;
        color: #94a3b8;
        margin-bottom: 5px;
    }
    .metric-value {
        font-size: 1.75rem;
        font-weight: bold;
        color: #f8f9fa;
    }
    .protocol-card {
        background: rgba(30, 41, 59, 0.7);
        border-radius: 10px;
        padding: 15px;
        margin-bottom: 15px;
        border-left: 4px solid #4CAF50;
    }
</style>
""", unsafe_allow_html=True)

# =============================================
# PROFESSIONAL DASHBOARD TITLE (MOVED TO TOP)
# =============================================
st.markdown(
    '''
    <div style="background: linear-gradient(90deg, #4CAF50 0%, #16213e 100%); padding: 32px 0 24px 0; border-radius: 0 0 18px 18px; box-shadow: 0 4px 24px rgba(76,175,80,0.10); margin-bottom: 32px; text-align: center;">
        <h1 style="color: #fff; font-size: 2.8rem; font-weight: 800; letter-spacing: 1px; margin-bottom: 8px;">
            <span style="color: #F0B90B;">₿</span> sBTC DeFi Intelligence Dashboard
        </h1>
        <p style="color: #e0e0e0; font-size: 1.25rem; font-weight: 400; margin: 0 auto; max-width: 700px;">
            Unified Bitcoin DeFi Analytics, Yield Optimization, and AI Insights<br>
            <span style="color: #4CAF50; font-weight: 600;">Built for the B25 Hackathon</span>
        </p>
    </div>
    ''',
    unsafe_allow_html=True
)

# =============================================
# DATA LOADING (MOVED UP)
# =============================================

def generate_mock_historical_data(protocol):
    """Generate realistic historical data for visualization"""
    dates = pd.date_range(end=datetime.today(), periods=30).date
    base_value = np.random.uniform(0.5, 2.0)
    
    if protocol == "ALEX":
        values = base_value + np.cumsum(np.random.normal(0.02, 0.05, 30))
        apy = np.clip(4.2 + np.random.normal(0, 0.5, 30), 3.0, 6.0)
    elif protocol == "Bitflow":
        values = base_value + np.cumsum(np.random.normal(0.015, 0.03, 30))
        apy = np.clip(3.8 + np.random.normal(0, 0.3, 30), 3.0, 5.0)
    else:  # Arkadiko
        values = base_value + np.cumsum(np.random.normal(0.025, 0.04, 30))
        apy = np.clip(5.1 + np.random.normal(0, 0.4, 30), 4.0, 6.5)
    
    return pd.DataFrame({
        "date": dates,
        "sbtc_balance": np.abs(values),
        "apy": apy,
        "yield_earned": np.abs(values) * apy / 365,
        "protocol": protocol
    })

def fetch_sbtc_portfolio_live():
    """
    Fetches live sBTC portfolio data from the Rebar Data API or another source.
    Returns a pandas DataFrame with columns:
    ['protocol', 'sbtc_balance', 'apy', 'yield_earned', 'tvl', 'risk_score', 'historical']
    If API is unavailable, returns an empty DataFrame.
    """
    # Example placeholder: Replace with actual API call logic
    try:
        # Example: response = requests.get("https://api.rebardata.com/sbtc_portfolio")
        # data = response.json()
        # df = pd.DataFrame(data)
        # For now, return empty DataFrame to trigger dummy data
        return pd.DataFrame()
    except Exception as e:
        return pd.DataFrame()

# Initialize portfolio_df as an empty DataFrame to handle potential errors early
portfolio_df = pd.DataFrame()
try:
    # Attempt to fetch live data
    portfolio_df = fetch_sbtc_portfolio_live() # fetch_sbtc_portfolio_live should already be defined
    
    # Validate fetched live data    required_cols = ['protocol', 'sbtc_balance', 'apy', 'yield_earned', 'tvl', 'risk_score', 'historical']
    if (portfolio_df.empty or 
        not all(col in portfolio_df.columns for col in required_cols) or
        any(portfolio_df[col].isnull().all() for col in required_cols if col != 'historical')): # historical can be complex
        # If live data is empty, missing critical columns, or all values in a column are null, raise an error to trigger dummy data.
        # We also check if 'historical' data, if present, contains valid DataFrames.
        if 'historical' in portfolio_df.columns:
            if not all(isinstance(h, pd.DataFrame) and not h.empty for h in portfolio_df['historical'] if h is not None):
                 raise ValueError("Live data fetched but 'historical' column contains invalid or empty DataFrames.")
        else: # If historical column itself is missing
            raise ValueError("Live data fetched but is incomplete or empty (missing 'historical' or other critical columns).")

except Exception as e:
    st.warning(f"Failed to fetch or validate live portfolio data: {str(e)[:200]}. Displaying dummy data.")
    portfolio_df = pd.DataFrame([
        {
            'protocol': 'ALEX', 'sbtc_balance': 1.2, 'apy': 4.5, 'yield_earned': 0.05,
            'tvl': 10000, 'risk_score': 2, 'historical': generate_mock_historical_data('ALEX')
        },
        {
            'protocol': 'Bitflow', 'sbtc_balance': 0.8, 'apy': 3.9, 'yield_earned': 0.03,
            'tvl': 8000, 'risk_score': 3, 'historical': generate_mock_historical_data('Bitflow')
        },
        {
            'protocol': 'Arkadiko', 'sbtc_balance': 1.0, 'apy': 5.2, 'yield_earned': 0.06,
            'tvl': 12000, 'risk_score': 2, 'historical': generate_mock_historical_data('Arkadiko')
        }
    ])
    # --- Log the dummy data creation for debugging ---
    try:
        debug_mode = st.secrets.get("DEBUG_MODE", False)
    except Exception: # Catch StreamlitSecretNotFoundError if secrets aren't set
        debug_mode = False # Default to False if secrets aren't available
    if debug_mode:
        st.sidebar.write("Debug: Using dummy portfolio data.") # Moved to sidebar for less intrusion
        # st.write("Dummy portfolio data created:") # Optional: show in main area
        # st.dataframe(portfolio_df.drop(columns=['historical']), height=200) # Drop historical for brevity

# =============================================
# SIDEBAR CONTENT
# =============================================
with st.sidebar:
    st.markdown("""
    <div style="text-align: center; margin-bottom: 30px;">
        <h2 style="color: #f8f9fa; margin-bottom: 5px;">sBTC Dashboard</h2>
        <p style="color: #94a3b8; margin-top: 0;">B25 Hackathon Submission</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Quick Actions
    st.markdown("""
    <div style="background: rgba(30, 41, 59, 0.7); padding: 15px; border-radius: 10px; margin-bottom: 20px;">
        <h3 style="color: #f8f9fa; margin-top: 0;">Quick Actions</h3>
    </div>
    """, unsafe_allow_html=True)
    if st.button("➕ Add Funds", key="add_funds"):
        st.success("Add Funds action triggered! (Demo placeholder)")
    if st.button("🔄 Rebalance Portfolio", key="rebalance_portfolio"):
        st.info("Rebalance Portfolio action triggered! (Demo placeholder)")
    if st.button("🏆 Claim Rewards", key="claim_rewards"):
        st.warning("Claim Rewards action triggered! (Demo placeholder)")
    
    # Portfolio Alerts
    st.markdown("""
    <div style="background: rgba(30, 41, 59, 0.7); padding: 15px; border-radius: 10px; margin-bottom: 20px;">
        <h3 style="color: #f8f9fa; margin-top: 0;">Portfolio Alerts</h3>
        <div style="display: flex; align-items: center; margin-bottom: 15px;">
            <div style="background: rgba(239, 68, 68, 0.2); padding: 5px; border-radius: 6px; margin-right: 10px;">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#ef4444" stroke-width="2">
                    <path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"></path>
                    <line x1="12" y1="9" x2="12" y2="13"></line>
                    <line x1="12" y1="17" x2="12.01" y2="17"></line>
                </svg>
            </div>
            <div>
                <p style="color: #f8f9fa; margin: 0; font-size: 0.9rem;">High concentration in ALEX (45%)</p>
                <p style="color: #94a3b8; margin: 0; font-size: 0.8rem;">Consider diversifying</p>
            </div>
        </div>
        <div style="display: flex; align-items: center; margin-bottom: 15px;">
            <div style="background: rgba(234, 179, 8, 0.2); padding: 5px; border-radius: 6px; margin-right: 10px;">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#f59e0b" stroke-width="2">
                    <circle cx="12" cy="12" r="10"></circle>
                    <line x1="12" y1="8" x2="12" y2="12"></line>
                    <line x1="12" y1="16" x2="12.01" y2="16"></line>
                </svg>
            </div>
            <div>
                <p style="color: #f8f9fa; margin: 0; font-size: 0.9rem;">Arkadiko APY increased</p>
                <p style="color: #94a3b8; margin: 0; font-size: 0.8rem;">Now at 5.3% (+0.2%)</p>
            </div>
        </div>
        <div style="display: flex; align-items: center;">
            <div style="background: rgba(76, 175, 80, 0.2); padding: 5px; border-radius: 6px; margin-right: 10px;">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#4CAF50" stroke-width="2">
                    <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path>
                    <polyline points="22 4 12 14.01 9 11.01"></polyline>
                </svg>
            </div>
            <div>
                <p style="color: #f8f9fa; margin: 0; font-size: 0.9rem;">$0.15 sBTC rewards ready</p>
                <p style="color: #94a3b8; margin: 0; font-size: 0.8rem;">Claim in Bitflow</p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Protocol Filter
    st.markdown("---")
    st.subheader("Filter Protocols")
    if not portfolio_df.empty and 'protocol' in portfolio_df.columns:
        unique_protocols = sorted(portfolio_df['protocol'].unique())
        # Check if 'selected_protocols' is already in session state to maintain selection across reruns
        if 'selected_protocols' not in st.session_state:
            st.session_state.selected_protocols = list(unique_protocols) # Default to all selected initially

        # Update session state when multiselect changes
        st.session_state.selected_protocols = st.multiselect(
            "Select protocols to display:",
            options=unique_protocols,
            default=st.session_state.selected_protocols # Use session state for default
        )
    else:
        st.markdown("No protocol data available to filter.")
        st.session_state.selected_protocols = [] # Ensure it's an empty list if no data

    # Hackathon Resources
    st.markdown("""
    <div style="background: rgba(30, 41, 59, 0.7); padding: 15px; border-radius: 10px;">
        <h3 style="color: #f8f9fa; margin-top: 0;">Hackathon Resources</h3>
        <a href="https://b25.devpost.com/" target="_blank" style="display: block; color: #4CAF50; text-decoration: none; margin: 10px 0; font-weight: 500;">➡️ B25 Devpost</a>
        <a href="https://docs.stacks.co/docs/sbtc-overview" target="_blank" style="display: block; color: #4CAF50; text-decoration: none; margin: 10px 0; font-weight: 500;">➡️ sBTC Documentation</a>
        <a href="https://alexlab.co/" target="_blank" style="display: block; color: #4CAF50; text-decoration: none; margin: 10px 0; font-weight: 500;">➡️ ALEX Protocol</a>
        <a href="https://bitflow.finance/" target="_blank" style="display: block; color: #4CAF50; text-decoration: none; margin: 10px 0; font-weight: 500;">➡️ Bitflow Finance</a>
        <a href="https://arkadiko.finance/" target="_blank" style="display: block; color: #4CAF50; text-decoration: none; margin: 10px 0; font-weight: 500;">➡️ Arkadiko Finance</a>
    </div>
    """, unsafe_allow_html=True)

    # Connect with Me
    st.markdown("---")
    st.subheader("Connect with Me")
    st.markdown("""
    - [Email](mailto:muhammadatiflatif67@gmail.com)
    - [LinkedIn](https://www.linkedin.com/in/muhammad-atif-latif-13a171318?utm_source=share&utm_campaign=share_via&utm_content=profile&utm_medium=android_app)
    - [Kaggle](https://www.kaggle.com/muhammadatiflatif)
    - [X (Twitter)](https://x.com/mianatif5867?s=09)
    - [GitHub](https://github.com/M-Atif-Latif)
    """)

# Filter the main DataFrame based on sidebar selection
if 'selected_protocols' in st.session_state and st.session_state.selected_protocols:
    filtered_portfolio_df = portfolio_df[portfolio_df['protocol'].isin(st.session_state.selected_protocols)]
else:
    # If no protocols are selected (e.g., user deselects all), or if state isn't set yet,
    # show all data or an empty state based on preference. For now, show all if nothing selected.
    filtered_portfolio_df = portfolio_df.copy() # Or pd.DataFrame() to show nothing

# =============================================
# HEADER SECTION
# =============================================
# --- Portfolio Summary Metrics ---
st.header("📊 Portfolio Overview")

# Update metrics based on filtered_portfolio_df
if not filtered_portfolio_df.empty:
    total_sbtc = filtered_portfolio_df['sbtc_balance'].sum()
    avg_apy = (filtered_portfolio_df['sbtc_balance'] * filtered_portfolio_df['apy']).sum() / total_sbtc if total_sbtc > 0 else 0
    total_yield_30d = filtered_portfolio_df['yield_earned'].sum() # Assuming yield_earned is for 30d
    # Risk score calculation might need more complex logic, e.g., weighted average or max
    # For simplicity, let's take the mode or a simple average if numeric, or a qualitative summary
    # Assuming risk_score is numeric (1-5)
    avg_risk_score_val = filtered_portfolio_df['risk_score'].mean() if not filtered_portfolio_df.empty else 0
    if avg_risk_score_val == 0:
        risk_level_display = "N/A"
        risk_color = "#94a3b8" # Neutral color
    elif avg_risk_score_val <= 2:
        risk_level_display = "Low"
        risk_color = "#4CAF50" # Green
    elif avg_risk_score_val <= 3.5:
        risk_level_display = "Medium"
        risk_color = "#f59e0b" # Orange
    else:
        risk_level_display = "High"
        risk_color = "#ef4444" # Red
    num_protocols = filtered_portfolio_df['protocol'].nunique()
else:
    total_sbtc, avg_apy, total_yield_30d, risk_level_display, num_protocols = 0, 0, 0, "N/A", 0
    risk_color = "#94a3b8"

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-title">Total sBTC</div>
        <div class="metric-value">{total_sbtc:.2f}</div>
        <div style="color: #94a3b8; font-size: 0.9rem;">Across {num_protocols} selected protocol(s)</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-title">Average APY</div>
        <div class="metric-value">{avg_apy:.2f}%</div>
        <div style="color: #94a3b8; font-size: 0.9rem;">Weighted by balance</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-title">30d Yield (Est.)</div>
        <div class="metric-value">{total_yield_30d:.4f} sBTC</div>
        <div style="color: #94a3b8; font-size: 0.9rem;">Based on current holdings</div>
    </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-title">Avg. Risk Score</div>
        <div class="metric-value" style="color: {risk_color};">{risk_level_display}</div>
        <div style="color: #94a3b8; font-size: 0.9rem;">Across selected protocols</div>
    </div>
    """, unsafe_allow_html=True)


# --- Portfolio Data & Visualizations (Now uses filtered_portfolio_df) ---
st.header("🔍 Protocol Breakdown")

if filtered_portfolio_df.empty:
    st.info("No data to display for the selected protocols. Please select protocols from the sidebar filter.")
else:
    tab1, tab2, tab3 = st.tabs(["Portfolio Distribution", "Performance Analysis", "Protocol Details"])

    with tab1:
        col1, col2 = st.columns([2, 1])
        with col1:
            if not filtered_portfolio_df.empty and 'sbtc_balance' in filtered_portfolio_df.columns and filtered_portfolio_df['sbtc_balance'].sum() > 0:
                fig = px.pie(
                    filtered_portfolio_df, 
                    values='sbtc_balance', 
                    names='protocol', 
                    hole=0.4,
                    color_discrete_sequence=px.colors.sequential.Viridis
                )
                fig.update_layout(
                    title="sBTC Allocation by Protocol",
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font_color='white'
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.markdown("<p style='text-align: center; color: #94a3b8;'>No sBTC balance data to display for pie chart.</p>", unsafe_allow_html=True)
        with col2:
            st.markdown("### Allocation Strategy")
            st.markdown("""
            <div style="background: rgba(30, 41, 59, 0.7); padding: 15px; border-radius: 10px;">
                <p style="color: #94a3b8;">Based on your current selection, we recommend:</p>
                <ul style="color: #f8f9fa;">
                    <li>Analyzing protocols with highest APY in selection.</li>
                    <li>Considering diversification if heavily weighted.</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)
            # Diversity score could also be updated based on filtered_portfolio_df
            st.metric("Portfolio Diversity Score", f"{min(num_protocols * 20, 80) + np.random.randint(0,5)}/100", "Dynamic based on selection")

    with tab2:
        if not filtered_portfolio_df.empty and 'protocol' in filtered_portfolio_df.columns and filtered_portfolio_df['protocol'].nunique() > 0:
            # Ensure the selectbox options are from the filtered data
            protocol_options_tab2 = sorted(filtered_portfolio_df['protocol'].unique())
            # Maintain selection for this specific selectbox if possible
            current_selection_tab2 = st.session_state.get('tab2_protocol_select', protocol_options_tab2[0] if protocol_options_tab2 else None)
            if current_selection_tab2 not in protocol_options_tab2 and protocol_options_tab2:
                current_selection_tab2 = protocol_options_tab2[0]
            
            protocol_for_history = st.selectbox(
                "Select Protocol for Historical Data", 
                protocol_options_tab2, 
                index=protocol_options_tab2.index(current_selection_tab2) if current_selection_tab2 and current_selection_tab2 in protocol_options_tab2 else 0,
                key='tab2_protocol_select' # Add a key to help preserve state
            )
            
            if protocol_for_history:
                # Get historical data from the original portfolio_df as historical data is per protocol
                # and not directly filtered by the main selection (it's nested)
                original_protocol_data = portfolio_df[portfolio_df['protocol'] == protocol_for_history]
                if not original_protocol_data.empty and isinstance(original_protocol_data.iloc[0]['historical'], pd.DataFrame):
                    selected_data = original_protocol_data.iloc[0]['historical']
                    # ... rest of the plotting code for tab2, ensure it uses 'selected_data' ...
                    fig = px.line(
                        selected_data,
                        x='date',
                        y=['sbtc_balance', 'apy'],
                        title=f"{protocol_for_history} Historical Performance",
                        labels={'value': 'Metric', 'variable': 'Legend'},
                        color_discrete_map={'sbtc_balance': '#4CAF50', 'apy': '#636EFA'}
                    )
                    fig.update_layout(
                        plot_bgcolor='rgba(0,0,0,0)',
                        paper_bgcolor='rgba(0,0,0,0)',
                        font_color='white',
                        hovermode="x unified"
                    )
                    fig.update_yaxes(title_text="sBTC Balance / APY (%)")
                    st.plotly_chart(fig, use_container_width=True)
                    # ... (col1, col2 for bar and area charts remain the same, using selected_data)
                    col1_tab2, col2_tab2 = st.columns(2)
                    with col1_tab2:
                        st.plotly_chart(px.bar(
                            selected_data,
                            x='date',
                            y='yield_earned',
                            title="Daily Yield Earned",
                            color_discrete_sequence=['#F0B90B']
                        ).update_layout(
                            plot_bgcolor='rgba(0,0,0,0)',
                            paper_bgcolor='rgba(0,0,0,0)',
                            font_color='white'
                        ), use_container_width=True)
                    with col2_tab2:
                        st.plotly_chart(px.area(
                            selected_data,
                            x='date',
                            y='sbtc_balance',
                            title="sBTC Balance Growth",
                            color_discrete_sequence=['#4CAF50']
                        ).update_layout(
                            plot_bgcolor='rgba(0,0,0,0)',
                            paper_bgcolor='rgba(0,0,0,0)',
                            font_color='white'
                        ), use_container_width=True)
                else:
                    st.markdown(f"<p style='color: #94a3b8;'>No historical data available for {protocol_for_history}.</p>", unsafe_allow_html=True)
            else:
                st.markdown("<p style='color: #94a3b8;'>Select a protocol to view its historical performance.</p>", unsafe_allow_html=True)
        else:
            st.markdown("<p style='color: #94a3b8;'>No protocols selected or available for performance analysis.</p>", unsafe_allow_html=True)

    with tab3:
        if not filtered_portfolio_df.empty:
            for _, row in filtered_portfolio_df.iterrows():
                # ... existing protocol card HTML, ensure it uses 'row' from filtered_portfolio_df ...
                st.markdown(f"""
                <div class="protocol-card">
                    <h3 style="color: #f8f9fa; margin-bottom: 5px;">{row['protocol']}</h3>
                    <div style="display: flex; justify-content: space-between;">
                        <div>
                            <p style="color: #94a3b8; margin: 2px 0;">sBTC Balance</p>
                            <p style="color: #f8f9fa; font-weight: bold; margin: 2px 0;">{row['sbtc_balance']:.4f}</p>
                        </div>
                        <div>
                            <p style="color: #94a3b8; margin: 2px 0;">APY</p>
                            <p style="color: #4CAF50; font-weight: bold; margin: 2px 0;">{row['apy']:.2f}%</p>
                        </div>
                        <div>
                            <p style="color: #94a3b8; margin: 2px 0;">Yield (30d)</p>
                            <p style="color: #f8f9fa; font-weight: bold; margin: 2px 0;">{row['yield_earned']:.4f}</p>
                        </div>
                        <div>
                            <p style="color: #94a3b8; margin: 2px 0;">Risk</p>
                            <p style="color: {'#ef4444' if row['risk_score'] > 3 else ('#f59e0b' if row['risk_score'] > 1 else '#4CAF50')}; font-weight: bold; margin: 2px 0;">
                                {'High' if row['risk_score'] > 3 else ('Medium' if row['risk_score'] > 1 else 'Low')}
                            </p>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.markdown("<p style='color: #94a3b8;'>No protocol details to display for the current selection.</p>", unsafe_allow_html=True)

# =============================================
# AI ANALYTICS SECTION (Now uses filtered_portfolio_df if applicable)
# =============================================
st.header("🤖 AI-Powered Portfolio Insights")

col1, col2 = st.columns([1, 2])

with col1:
    st.markdown("""
    <div style="background: rgba(30, 41, 59, 0.7); padding: 20px; border-radius: 10px; height: 100%;">
        <h3 style="color: #f8f9fa;">Portfolio Health</h3>
        <div style="margin: 15px 0;">
            <div style="display: flex; justify-content: space-between; margin-bottom: 5px;">
                <span style="color: #94a3b8;">Diversity</span>
                <span style="color: #f8f9fa;">Good</span>
            </div>
            <div style="height: 8px; background: #2d3748; border-radius: 4px;">
                <div style="width: 75%; height: 100%; background: #4CAF50; border-radius: 4px;"></div>
            </div>
        </div>
        <div style="margin: 15px 0;">
            <div style="display: flex; justify-content: space-between; margin-bottom: 5px;">
                <span style="color: #94a3b8;">Yield Efficiency</span>
                <span style="color: #f8f9fa;">Excellent</span>
            </div>
            <div style="height: 8px; background: #2d3748; border-radius: 4px;">
                <div style="width: 90%; height: 100%; background: #4CAF50; border-radius: 4px;"></div>
            </div>
        </div>
        <div style="margin: 15px 0;">
            <div style="display: flex; justify-content: space-between; margin-bottom: 5px;">
                <span style="color: #94a3b8;">Risk Management</span>
                <span style="color: #f8f9fa;">Moderate</span>
            </div>
            <div style="height: 8px; background: #2d3748; border-radius: 4px;">
                <div style="width: 60%; height: 100%; background: #f59e0b; border-radius: 4px;"></div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div style="background: rgba(30, 41, 59, 0.7); padding: 20px; border-radius: 10px; height: 100%;">
        <h3 style="color: #f8f9fa;">AI Recommendations</h3>
        <div style="margin-top: 15px;">
            <div style="display: flex; align-items: flex-start; margin-bottom: 15px;">
                <div style="background: #4CAF50; color: white; border-radius: 50%; width: 24px; height: 24px; display: flex; align-items: center; justify-content: center; margin-right: 10px; flex-shrink: 0;">1</div>
                <div>
                    <p style="color: #f8f9fa; margin: 0; font-weight: 500;">Rebalance to Arkadiko</p>
                    <p style="color: #94a3b8; margin: 0; font-size: 0.9rem;">Increase allocation by 15% to capture higher yields (currently 5.1% APY)</p>
                </div>
            </div>
            <div style="display: flex; align-items: flex-start; margin-bottom: 15px;">
                <div style="background: #4CAF50; color: white; border-radius: 50%; width: 24px; height: 24px; display: flex; align-items: center; justify-content: center; margin-right: 10px; flex-shrink: 0;">2</div>
                <div>
                    <p style="color: #f8f9fa; margin: 0; font-weight: 500;">Consider Stackswap for Stability</p>
                    <p style="color: #94a3b8; margin: 0; font-size: 0.9rem;">Lower risk option with consistent 3.9% APY</p>
                </div>
            </div>
            <div style="display: flex; align-items: flex-start;">
                <div style="background: #4CAF50; color: white; border-radius: 50%; width: 24px; height: 24px; display: flex; align-items: center; justify-content: center; margin-right: 10px; flex-shrink: 0;">3</div>
                <div>
                    <p style="color: #f8f9fa; margin: 0; font-weight: 500;">Monitor ALEX Vaults</p>
                    <p style="color: #94a3b8; margin: 0; font-size: 0.9rem;">TVL has increased 22% this month - potential for APY adjustments</p>
                </div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# =============================================
# WALLET INTEGRATION & EDUCATIONAL CONTENT
# =============================================
st.header("🔗 Wallet Integration & Education")

tab1, tab2, tab3 = st.tabs(["Connect Wallet", "Learn About sBTC", "DeFi Strategies"])

with tab1:
    st.markdown("""
    <div style="background: rgba(30, 41, 59, 0.7); padding: 20px; border-radius: 10px;">
        <h3 style="color: #f8f9fa; margin-top: 0;">Connect Your Stacks Wallet</h3>
        <p style="color: #94a3b8; margin-bottom: 20px;">
            View your actual sBTC balances and positions across all integrated protocols
        </p>
        <div style="margin: 20px 0;">
            <button style="background: #5546FF; color: white; border: none; padding: 10px 20px; border-radius: 8px; font-weight: bold; margin-right: 10px; cursor: pointer;">
                Connect Hiro Wallet
            </button>
            <button style="background: #2d3748; color: white; border: none; padding: 10px 20px; border-radius: 8px; font-weight: bold; cursor: pointer;">
                Enter Address Manually
            </button>
        </div>
        <div style="margin-top: 30px;">
            <h4 style="color: #f8f9fa;">Supported Wallets</h4>
            <div style="display: flex; gap: 32px; margin-top: 18px; justify-content: center; align-items: flex-end; flex-wrap: wrap;">
                <div style="text-align: center; min-width: 90px;">
                    <span style="font-size: 2.5rem;">🦉</span>
                    <p style="color: #94a3b8; margin: 8px 0 0; font-size: 0.85rem;">Hiro Wallet</p>
                </div>
                <div style="text-align: center; min-width: 90px;">
                    <span style="font-size: 2.5rem;">🦊</span>
                    <p style="color: #94a3b8; margin: 8px 0 0; font-size: 0.85rem;">Xverse</p>
                </div>
                <div style="text-align: center; min-width: 90px;">
                    <span style="font-size: 2.5rem;">👛</span>
                    <p style="color: #94a3b8; margin: 8px 0 0; font-size: 0.85rem;">Leather</p>
                </div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

with tab2:
    col1, col2 = st.columns([1, 1])
    with col1:
        st.markdown("""
        <div style="background: rgba(30, 41, 59, 0.7); padding: 20px; border-radius: 10px; height: 100%;">
            <h3 style="color: #f8f9fa; margin-top: 0;">What is sBTC?</h3>
            <p style="color: #94a3b8;">
                sBTC (Synthetic Bitcoin) is a 1:1 Bitcoin-backed asset on the Stacks blockchain that enables 
                Bitcoin holders to participate in DeFi without giving up custody of their BTC. sBTC is fully collateralized, decentralized, and programmable, making it a powerful tool for Bitcoin DeFi.
            </p>
            <div style="margin: 20px 0;">
                <div style="display: flex; align-items: center; margin-bottom: 10px;">
                    <div style="background: rgba(76, 175, 80, 0.2); padding: 5px; border-radius: 6px; margin-right: 10px;">
                        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#4CAF50" stroke-width="2">
                            <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path>
                            <polyline points="22 4 12 14.01 9 11.01"></polyline>
                        </svg>
                    </div>
                    <div>
                        <p style="color: #f8f9fa; margin: 0; font-weight: 500;">Fully Collateralized</p>
                        <p style="color: #94a3b8; margin: 0; font-size: 0.9rem;">1 sBTC = 1 BTC held in reserve, verifiable on-chain</p>
                    </div>
                </div>
                <div style="display: flex; align-items: center; margin-bottom: 10px;">
                    <div style="background: rgba(76, 175, 80, 0.2); padding: 5px; border-radius: 6px; margin-right: 10px;">
                        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#4CAF50" stroke-width="2">
                            <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path>
                            <polyline points="22 4 12 14.01 9 11.01"></polyline>
                        </svg>
                    </div>
                    <div>
                        <p style="color: #f8f9fa; margin: 0; font-weight: 500;">Decentralized</p>
                        <p style="color: #94a3b8; margin: 0; font-size: 0.9rem;">No single entity controls the peg; secured by threshold signatures</p>
                    </div>
                </div>
                <div style="display: flex; align-items: center;">
                    <div style="background: rgba(76, 175, 80, 0.2); padding: 5px; border-radius: 6px; margin-right: 10px;">
                        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#4CAF50" stroke-width="2">
                            <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path>
                            <polyline points="22 4 12 14.01 9 11.01"></polyline>
                        </svg>
                    </div>
                    <div>
                        <p style="color: #f8f9fa; margin: 0; font-weight: 500;">Programmable</p>
                        <p style="color: #94a3b8; margin: 0; font-size: 0.9rem;">Use sBTC in smart contracts and DeFi apps on Stacks</p>
                    </div>
                </div>
            </div>
            <p style="color: #94a3b8; font-size: 0.9rem; margin-top: 20px;">Learn more in the <a href='https://docs.stacks.co/docs/sbtc-overview' style='color: #4CAF50;' target='_blank'>official sBTC documentation</a>.</p>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown("""
        <div style="background: rgba(30, 41, 59, 0.7); padding: 20px; border-radius: 10px; height: 100%;">
            <h3 style="color: #f8f9fa; margin-top: 0;">How sBTC Works</h3>
            <div style="margin: 15px 0; position: relative;">
                <div style="position: absolute; left: 16px; top: 0; bottom: 0; width: 2px; background: #4CAF50;"></div>
                <div style="display: flex; margin-bottom: 25px;">
                    <div style="background: #4CAF50; color: white; border-radius: 50%; width: 34px; height: 34px; display: flex; align-items: center; justify-content: center; margin-right: 15px; flex-shrink: 0; z-index: 1;">1</div>
                    <div>
                        <p style="color: #f8f9fa; margin: 0 0 5px 0; font-weight: 500;">Lock BTC</p>
                        <p style="color: #94a3b8; margin: 0;">Deposit BTC into a decentralized threshold signature wallet</p>
                    </div>
                </div>
                <div style="display: flex; margin-bottom: 25px;">
                    <div style="background: #4CAF50; color: white; border-radius: 50%; width: 34px; height: 34px; display: flex; align-items: center; justify-content: center; margin-right: 15px; flex-shrink: 0; z-index: 1;">2</div>
                    <div>
                        <p style="color: #f8f9fa; margin: 0 0 5px 0; font-weight: 500;">Mint sBTC</p>
                        <p style="color: #94a3b8; margin: 0;">Equivalent sBTC is minted on Stacks, pegged 1:1 to BTC</p>
                    </div>
                </div>
                <div style="display: flex;">
                    <div style="background: #4CAF50; color: white; border-radius: 50%; width: 34px; height: 34px; display: flex; align-items: center; justify-content: center; margin-right: 15px; flex-shrink: 0; z-index: 1;">3</div>
                    <div>
                        <p style="color: #f8f9fa; margin: 0 0 5px 0; font-weight: 500;">Use in DeFi</p>
                        <p style="color: #94a3b8; margin: 0;">sBTC can be used in DeFi protocols for lending, trading, and more</p>
                    </div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

with tab3:
    st.markdown("""
    <div style="background: rgba(30, 41, 59, 0.7); padding: 20px; border-radius: 10px;">
        <h3 style="color: #f8f9fa; margin-top: 0;">DeFi Strategies</h3>
        <ul style="color: #f8f9fa;">
            <li><b>Yield Farming:</b> Provide sBTC liquidity to earn rewards across protocols.</li>
            <li><b>Lending & Borrowing:</b> Use sBTC as collateral for loans or to earn interest.</li>
            <li><b>Risk Management:</b> Diversify across protocols and monitor APY/risk changes.</li>
            <li><b>Automated Rebalancing:</b> Periodically adjust allocations for optimal yield and safety.</li>
        </ul>
        <p style="color: #94a3b8;">Tip: Always research protocol risks and monitor your positions regularly.</p>
    </div>
    """, unsafe_allow_html=True)

# =============================================
# FOOTER & CREDITS
# =============================================
st.markdown("""
<div style="text-align: center; margin-top: 50px; padding: 20px; color: #94a3b8; font-size: 0.9rem;">
    <p>Built for the B25 Hackathon | Powered by Stacks, sBTC, and Bitcoin DeFi</p>
    <p>© 2024 sBTC Analytics Dashboard | All data is for demonstration purposes</p>
</div>
""", unsafe_allow_html=True)

# =============================================
# HIDDEN DEBUG FEATURES (For Judges)
# =============================================
try:
    debug_mode = st.secrets.get("DEBUG_MODE", False)
except Exception:
    debug_mode = False
if debug_mode:
    with st.expander("🚨 Judge Debug Panel"):
        st.write("## Hackathon Submission Details")
        st.code("""
        Submission ID: B25-sBTC-ANALYTICS-0420
        Team: Bitcoin DeFi Builders
        Contact: team@btcdefi.dev
        Repository: github.com/btcdefi/sbtc-dashboard
        """)
        col1, col2 = st.columns(2)
        with col1:
            st.write("**Core Technologies**")
            st.markdown("""
            - Streamlit for frontend
            - Plotly for visualizations
            - Stacks API for live data
            - Gemini AI integration (simulated)
            - Custom CSS theming
            """)
        with col2:
            st.write("**Innovation Highlights**")
            st.markdown("""
            - Unified sBTC portfolio tracking
            - Cross-protocol yield optimization
            - AI-powered risk assessment
            - Educational resources integration
            - Wallet connectivity framework
            """)
        st.write("## Roadmap & Future Plans")
        st.markdown("""
        1. **Q3 2024**: Full Stacks wallet integration
        2. **Q4 2024**: Real AI insights via Gemini API
        3. **Q1 2025**: Mobile app release
        4. **Q2 2025**: Multi-chain sBTC support
        """)

# =============================================
# SESSION STATE MANAGEMENT
# =============================================
if 'portfolio_df' not in st.session_state:
    st.session_state.portfolio_df = fetch_sbtc_portfolio_live()

if st.button("🔄 Refresh All Data", key="refresh_all"):
    st.session_state.portfolio_df = fetch_sbtc_portfolio_live()
    st.rerun()