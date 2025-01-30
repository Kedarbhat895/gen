from dotenv import load_dotenv
import autogen
import yfinance as yf
import streamlit as st


# Load environment variables
load_dotenv("key.env")

llm_config = {
    "model": "gpt-3.5-turbo", 
}
writing_tasks = [
        """Develop an engaging financial report using all information provided, include the normalized_prices.png figure,
        and other figures if provided.
        Mainly rely on the information provided. 
        Create a Table comparing all the fundamental ratios and data, make sure to enter the current price in the table.
        Provide comments and description of all the fundamental ratios and data.
        Compare the stocks, consider their correlation and risks, provide a comparative analysis of the stocks.
        Retrieve the **2 most recent news headlines** for each stock in {stocks}.

        For each stock:
        1. List the **headline and source**. If you have multiple sources mention any one of them.
        2. Summarize the key **themes and trends** from these headlines (e.g., earnings, new contracts, regulations, lawsuits, etc.).
        3. Analyze how the news may **impact the stock price** (e.g., positive, negative, neutral).
        4. Extract any **mentions of government policies, regulations, or macroeconomic factors** affecting the stock if mentioned.

            Format the response as follows:

            ### Stock News Summary

            #### [Stock Name]
            - **Key Headlines & Sources**: 
            1. *[Headline 1]* (Source: [Source Name])
            2. *[Headline 2]* (Source: [Source Name])

            - **Themes & Trends**:
            - **[Key Theme 1]**: Explanation
            - **[Key Theme 2]**: Explanation
            - **Sentiment Analysis**: Positive/Negative/Neutral
            - **Potential Effect on Stock Price**: Brief reasoning

            - **Macroeconomic & Regulatory Impact**:
            - Any relevant policy changes, economic trends, or sector-wide shifts.

            Make sure to extract information from **credible financial sources** and provide well-structured insights.

        Provide a summary of the recent news about each stock. 
        Provide connections between the news headlines provided and the fundamental ratios.
        Provide an analysis of possible future scenarios. 
        """]

exporting_task = ["""Save the report and only the report to a .md file using a python script."""]

financial_assistant = autogen.AssistantAgent(
    name="Financial_assistant",
    llm_config=llm_config,
)
research_assistant = autogen.AssistantAgent(
    name="Researcher",
    llm_config=llm_config,
)

writer = autogen.AssistantAgent(
    name="writer",
    llm_config=llm_config,
    system_message="""
        You are a professional writer, known for
        your insightful and engaging finance reports.
        You transform complex concepts into compelling narratives. 
        Include all metrics provided to you as context in your analysis.
        Only answer with the financial report written in markdown directly, do not include a markdown language block indicator.
        Only return your final work without additional comments.
        """,
)

export_assistant = autogen.AssistantAgent(
    name="Exporter",
    llm_config=llm_config,
)
# ===

critic = autogen.AssistantAgent(
    name="Critic",
    is_termination_msg=lambda x: x.get("content", "").find("TERMINATE") >= 0,
    llm_config=llm_config,
    system_message="You are a critic. You review the work of "
                "the writer and provide constructive "
                "feedback to help improve the quality of the content",
)

legal_reviewer = autogen.AssistantAgent(
    name="Legal_Reviewer",
    llm_config=llm_config,
    system_message="You are a legal reviewer, known for "
        "your ability to ensure that content is legally compliant "
        "and free from any potential legal issues. "
        "Make sure your suggestion is concise (within 3 bullet points), "
        "concrete and to the point. "
        "Begin the review by stating your role.",
)

consistency_reviewer = autogen.AssistantAgent(
    name="Consistency_reviewer",
    llm_config=llm_config,
    system_message="You are a consistency reviewer, known for "
        "your ability to ensure that the written content is consistent throughout the report. "
        "Refer numbers and data in the report to determine which version should be chosen " 
        "in case of contradictions. "
        "Make sure your suggestion is concise (within 3 bullet points), "
        "concrete and to the point. "
        "Begin the review by stating your role. ",
)

textalignment_reviewer = autogen.AssistantAgent(
    name="Text_alignment_reviewer",
    llm_config=llm_config,
    system_message="You are a text data alignment reviewer, known for "
        "your ability to ensure that the meaning of the written content is aligned "
        "with the numbers written in the text. " 
        "You must ensure that the text clearely describes the numbers provided in the text "
        "without contradictions. "
        "Make sure your suggestion is concise (within 3 bullet points), "
        "concrete and to the point. "
        "Begin the review by stating your role. ",
)

completion_reviewer = autogen.AssistantAgent(
    name="Completion_Reviewer",
    llm_config=llm_config,
    system_message="You are a content completion reviewer, known for "
        "your ability to check that financial reports contain all the required elements. "
        "You always verify that the report contains: a news report about each asset, " 
        "If you see any bullet points empty, force the writer to remove or refactor it"
        "a description of the different ratios and prices, "
        "a description of possible future scenarios, a table comparing fundamental ratios and "
        " at least a single figure. "
        "Make sure your suggestion is concise (within 3 bullet points), "
        "concrete and to the point. "
        "Make sure the atleast one image is added in the report, this is must"
        "Begin the review by stating your role. ",
)

meta_reviewer = autogen.AssistantAgent(
    name="Meta_Reviewer",
    llm_config=llm_config,
    system_message="You are a meta reviewer, you aggregate and review "
    "the work of other reviewers and give a final suggestion on the content.",
)

def reflection_message(recipient, messages, sender, config):
    return f'''Review the following content. 
            \n\n {recipient.chat_messages_for_summary(sender)[-1]['content']}'''

review_chats = [
    {
    "recipient": legal_reviewer, "message": reflection_message, 
     "summary_method": "reflection_with_llm",
     "summary_args": {"summary_prompt" : 
        "Return review into a JSON object only:"
        "{'Reviewer': '', 'Review': ''}.",},
     "max_turns": 1},
    {"recipient": textalignment_reviewer, "message": reflection_message, 
     "summary_method": "reflection_with_llm",
     "summary_args": {"summary_prompt" : 
        "Return review into a JSON object only:"
        "{'reviewer': '', 'review': ''}",},
     "max_turns": 1},
    {"recipient": consistency_reviewer, "message": reflection_message, 
     "summary_method": "reflection_with_llm",
     "summary_args": {"summary_prompt" : 
        "Return review into a JSON object only:"
        "{'reviewer': '', 'review': ''}",},
     "max_turns": 1},
    {"recipient": completion_reviewer, "message": reflection_message, 
     "summary_method": "reflection_with_llm",
     "summary_args": {"summary_prompt" : 
        "Return review into a JSON object only:"
        "{'reviewer': '', 'review': ''}",},
     "max_turns": 1},
     {"recipient": meta_reviewer, 
      "message": "Aggregrate feedback from all reviewers and give final suggestions on the writing.", 
     "max_turns": 1},
]

critic.register_nested_chats(
    review_chats,
    trigger=writer,
)

# ===

user_proxy_auto = autogen.UserProxyAgent(
    name="User_Proxy_Auto",
    human_input_mode="NEVER",
    is_termination_msg=lambda x: x.get("content", "") and x.get("content", "").rstrip().endswith("TERMINATE"),
    code_execution_config={
        "last_n_messages": 3,
        "work_dir": "coding",
        "use_docker": False,
    },  
)

assets = st.text_input("Assets you want to analyze (provide the tickers)?")
hit_button = st.button('Start analysis')

stocks = assets.split(",")

if hit_button is True:

    from datetime import datetime
    date_str = datetime.now().strftime("%Y-%m-%d")

    stock_data = {}

    for symbol in stocks:
        try:
            stock = yf.Ticker(symbol)
            info = stock.info  # Fetch stock information
            

            historical_data = stock.history(period="1mo") 
        
            close_prices = historical_data['Close'].tolist()
            
            first_price = close_prices[0]
            normalized_prices = [(price / first_price) * 100 for price in close_prices]

            stock_data[symbol] = {
                
                "name": info.get("longName", "Unknown"),
                "current_price": info.get("currentPrice", "N/A"),
                "currency": info.get("financialCurrency", "N/A"),
                "PE_ratio": info.get("trailingPE", "N/A"),
                "forward_PE": info.get("forwardPE", "N/A"),
                "dividends": info.get("dividendYield", "N/A"),
                "price_to_book": info.get("priceToBook", "N/A"),
                "debt_to_equity": info.get("debtToEquity", "N/A"),
                "return_on_equity": info.get("returnOnEquity", "N/A"),
                "market_cap": info.get("marketCap", "N/A"),
                "sector": info.get("sector", "N/A"),
                "industry": info.get("industry", "N/A"),
                "normalized_prices": normalized_prices
            }
        except Exception as e:
            stock_data[symbol] = {"error": f"Failed to retrieve data: {str(e)}"}

    financial_tasks = [
    f"""Today is the {date_str}. 
    Provided the {stock_data} analyze the performance over the past 3 months in terms of percentage change.
    Prepare a figure of the normalized price of these stocks and save it to a file named normalized_prices.png. Include information about, if applicable: 
    * Current Price
    * P/E ratio
    * Forward P/E
    * Dividends
    * Price to book
    * Debt/Eq
    * ROE
    * Analyze the correlation between the stocks
    All the above mentioned fields is must in the final output created.
    Do not use a solution that requires an API key.
    Make sure the currency of the stock is right.
    Verify that `normalized_prices.png` is created and properly formatted before proceeding this is a must.
    If some of the data does not makes sense, such as a price of 0, change the query and re-try.""",

    """Investigate possible reasons of the stock performance leveraging market news headlines from Bing News or Google Search. Retrieve news headlines using python and return them. Use the full name stocks to retrieve headlines. Retrieve at least 10 headlines per stock. Do not use a solution that requires an API key. Do not perform a sentiment analysis"""]


    # financial_tasks = [
#     f"""Today is the {date_str}. 
#     What are the current stock prices of {assets}, and how is the performance over the past 6 months in terms of percentage change? 
#     Start by retrieving the full name and currency of each stock and use it for all future requests.
#     Prepare a figure of the normalized price of these stocks and save it to a file named normalized_prices.png. Include information about, if applicable: 
#     * Stock Price in the right currency
#     * P/E ratio
#     * Forward P/E
#     * Dividends
#     * Price to book
#     * Debt/Eq
#     * ROE
#     * Analyze the correlation between the stocks
#     Do not use a solution that requires an API key and calculate the above mentioned values.
#     If some of the data does not makes sense, such as a price of 0, change the query and re-try.""",

#     """Investigate possible reasons of the stock performance leveraging market news headlines from Bing News or Google Search. Retrieve news headlines using python and return them. Use the full name stocks to retrieve headlines. Retrieve at least 10 headlines per stock. Do not use a solution that requires an API key. Do not perform a sentiment analysis.""",
# ]

    with st.spinner("Agents working on the analysis...."):
        chat_results = autogen.initiate_chats(
            [
                {
                    "sender": user_proxy_auto,
                    "recipient": financial_assistant,
                    "message": financial_tasks[0],
                    "silent": False,
                    "summary_method": "reflection_with_llm",
                    "summary_args": {
                        "summary_prompt" : "Return the stock prices of the stocks, their performance and all other metrics"
                        "into a JSON object only. Provide the name of all figure files created. Provide the full name of each stock.",
                                    },
                    "clear_history": False,
                    "carryover": "Wait for confirmation of code execution before terminating the conversation. Verify that the data is not completely composed of NaN values. Reply TERMINATE in the end when everything is done."
                },
                {
                    "sender": user_proxy_auto,
                    "recipient": research_assistant,
                    "message": financial_tasks[1],
                    "silent": False,
                    "summary_method": "reflection_with_llm",
                    "summary_args": {
                        "summary_prompt" : "Provide the news headlines as a paragraph for each stock, be precise but do not consider news events that are vague, return the result as a JSON object only.",
                                    },
                    "clear_history": False,
                    "carryover": "Wait for confirmation of code execution before terminating the conversation. Reply TERMINATE in the end when everything is done."
                },
                {
                    "sender": critic,
                    "recipient": writer,
                    "message": writing_tasks[0],
                    "carryover": "I want to include a figure and a table of the provided data in the financial report.",
                    "max_turns": 2,
                    "summary_method": "last_msg",
                }
            ]
        )


    st.image("./coding/normalized_prices.png")
    st.markdown(chat_results[-1].chat_history[-1]["content"])