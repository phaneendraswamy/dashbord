import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Set Streamlit page config
st.set_page_config(page_title="Your Sales Dashboard", layout="wide")

# Function to load CSV
def load_data(uploaded_file):
    if uploaded_file is not None:
        df = pd.read_csv(uploaded_file)
        return df
    return None

# Streamlit UI
st.title("📊 Your Sales Dashboard - Made Simple!")
st.write("Upload your sales data (CSV file) to see how your business is doing!")

uploaded_file = st.file_uploader("Drop Your CSV File Here", type=["csv"])

if uploaded_file:
    df = load_data(uploaded_file)
    st.write("### Sneak Peek at Your Data:")
    st.dataframe(df.head())

    # Check for required columns
    required_columns = {"Date", "Product", "Category", "Units Sold", "Price Per Unit", "Cost Per Unit", "Revenue", "Profit/Loss"}
    if not required_columns.issubset(df.columns):
        st.error(f"Oops! Your file is missing some key info: {required_columns}")
    else:
        # Convert Date column to datetime
        df["Date"] = pd.to_datetime(df["Date"])

        # --- Sidebar Filters ---
        st.sidebar.header("Filter Your Data")
        product_filter = st.sidebar.multiselect("Choose Products", options=df["Product"].unique(), default=df["Product"].unique())
        date_range = st.sidebar.date_input("Pick a Date Range", [df["Date"].min(), df["Date"].max()])
        filtered_df = df[
            (df["Product"].isin(product_filter)) &
            (df["Date"].between(pd.to_datetime(date_range[0]), pd.to_datetime(date_range[1])))
        ]

        # --- Key Metrics ---
        st.write("### Your Business at a Glance")
        col1, col2, col3 = st.columns(3)
        col1.metric("Total Sales", f"${filtered_df['Revenue'].sum():,.2f}")
        col2.metric("Total Profit/Loss", f"${filtered_df['Profit/Loss'].sum():,.2f}", 
                    delta="Profit" if filtered_df["Profit/Loss"].sum() > 0 else "Loss", 
                    delta_color="normal" if filtered_df["Profit/Loss"].sum() > 0 else "inverse")
        col3.metric("Units Sold", f"{filtered_df['Units Sold'].sum():,}")

        # --- Visualization 1: Interactive Sales Over Time ---
        st.write("### How Your Sales Look Over Time")
        st.write("Zoom in, hover for details—this shows your daily sales!")
        sales_trend = filtered_df.groupby("Date")["Revenue"].sum().reset_index()
        fig1 = px.line(sales_trend, x="Date", y="Revenue", title="Daily Sales Trend",
                       labels={"Revenue": "Total Sales ($)"}, line_shape="linear", color_discrete_sequence=["green"])
        fig1.update_layout(title_font_size=16, title_font_family="Arial", title_x=0.5)
        st.plotly_chart(fig1, use_container_width=True)

        # --- Visualization 2: Interactive Profit vs Loss ---
        st.write("### Are You Making Money or Losing It?")
        st.write("Green is profit, red is loss—click bars for details!")
        fig2 = go.Figure()
        fig2.add_trace(go.Bar(
            x=filtered_df["Date"], 
            y=filtered_df["Profit/Loss"],
            marker_color=filtered_df["Profit/Loss"].apply(lambda x: "green" if x > 0 else "red"),
            text=filtered_df["Profit/Loss"].apply(lambda x: f"${x:,.0f}"),
            textposition="auto"
        ))
        fig2.add_hline(y=0, line_dash="dash", line_color="black")
        fig2.update_layout(title="Profit or Loss Each Day", title_font_size=16, title_font_family="Arial", title_x=0.5,
                           xaxis_title="Date", yaxis_title="Profit/Loss ($)")
        st.plotly_chart(fig2, use_container_width=True)

        # --- Visualization 3: Interactive Top Products ---
        st.write("### Your Best-Selling Products")
        st.write("Hover to see exact sales—these are your top cash makers!")
        top_products = filtered_df.groupby("Product")["Revenue"].sum().reset_index().sort_values(by="Revenue", ascending=False).head(5)
        fig3 = px.bar(top_products, x="Revenue", y="Product", orientation="h", title="Top 5 Products by Sales",
                      labels={"Revenue": "Total Sales ($)"}, color="Revenue", color_continuous_scale="Blues")
        fig3.update_layout(title_font_size=16, title_font_family="Arial", title_x=0.5, showlegend=False)
        st.plotly_chart(fig3, use_container_width=True)

        # --- Visualization 4: Interactive Revenue Share by Category ---
        st.write("### Where Your Sales Come From")
        st.write("Click slices to explore—this pie shows your sales split!")
        category_revenue = filtered_df.groupby("Category")["Revenue"].sum().reset_index()
        fig4 = px.pie(category_revenue, values="Revenue", names="Category", title="Sales Share by Category",
                      color_discrete_sequence=["#66b3ff", "#ff9999"])
        fig4.update_traces(textinfo="percent+label", pull=[0.1, 0])  # Slightly explode one slice for emphasis
        fig4.update_layout(title_font_size=16, title_font_family="Arial", title_x=0.5)
        st.plotly_chart(fig4, use_container_width=True)

        # --- Visualization 5: Interactive Units Sold vs Profit ---
        st.write("### Does Selling More Mean More Profit?")
        st.write("Hover for product details—bigger bubbles mean more sales!")
        fig5 = px.scatter(filtered_df, x="Units Sold", y="Profit/Loss", size="Revenue", color="Product",
                          title="Units Sold vs Profit/Loss", hover_data=["Date", "Revenue"],
                          labels={"Profit/Loss": "Profit/Loss ($)"})
        fig5.update_layout(title_font_size=16, title_font_family="Arial", title_x=0.5)
        st.plotly_chart(fig5, use_container_width=True)

        # --- Chatbot-Style Summary ---
        st.write("### Your Sales Chatbot Says:")
        total_revenue = filtered_df["Revenue"].sum()
        total_profit = filtered_df["Profit/Loss"].sum()
        top_product = top_products.iloc[0]["Product"]
        top_product_revenue = top_products.iloc[0]["Revenue"]
        best_day = filtered_df.loc[filtered_df["Revenue"].idxmax()]["Date"].strftime("%Y-%m-%d")
        worst_day = filtered_df.loc[filtered_df["Profit/Loss"].idxmin()]["Date"].strftime("%Y-%m-%d")

        st.write("""
        Hey there! Here’s a quick rundown of your sales:
        - You’ve made **${:,.2f}** in total sales. Nice work!
        - Your total profit (or loss) is **${:,.2f}**. {} 
        - Your star product is **{}**, raking in **${:,.2f}**.
        - Your best sales day was **{}**—what happened there? Let’s do more of that!
        - Watch out for **{}**—it was your toughest day profit-wise.
        """.format(
            total_revenue,
            total_profit,
            "That’s a win!" if total_profit > 0 else "Let’s turn that around!",
            top_product,
            top_product_revenue,
            best_day,
            worst_day
        ))

        # --- Enhanced Chatbot Q&A ---
        user_question = st.text_input("Ask me about your sales!")
        if user_question:
            question = user_question.lower()
            if "best product" in question:
                st.write(f"Your best product is **{top_product}** with **${top_product_revenue:,.2f}** in sales!")
            elif "how much" in question and "on" in question:
                try:
                    date = pd.to_datetime(question.split("on")[-1].strip()).strftime("%Y-%m-%d")
                    revenue = filtered_df[filtered_df["Date"] == date]["Revenue"].sum()
                    st.write(f"On {date}, you made **${revenue:,.2f}**.")
                except:
                    st.write("Sorry, I couldn’t find that date. Try something like 'How much on 2024-01-01?'")
            else:
                st.write("I’m not sure how to answer that yet! Try asking about your best product or sales on a specific date.")

        # --- Tips Section ---
        st.write("### Quick Tips for You:")
        if filtered_df["Profit/Loss"].sum() < 0:
            st.write("- **Ouch, you’re losing money!** Check products with big losses (red bars) and see if costs are too high.")
        if filtered_df.groupby("Product")["Profit/Loss"].mean().min() < 0:
            losing_products = filtered_df.groupby("Product")["Profit/Loss"].mean()[lambda x: x < 0].index.tolist()
            st.write(f"- **Heads up!** These products are losing money on average: {', '.join(losing_products)}. Maybe tweak pricing?")
        if filtered_df["Units Sold"].corr(filtered_df["Profit/Loss"]) < 0.3:
            st.write("- **Selling more isn’t always better!** Focus on high-profit items (check the scatter plot).")
