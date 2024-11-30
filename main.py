import streamlit as st
import streamlit.components.v1 as components
from streamlit_option_menu import option_menu
from langchain.agents import initialize_agent, load_tools
from langchain.llms import OpenAI
from langchain.memory import ConversationBufferMemory
from PIL import Image

# Initialize the LLM and load the tools
with open("api_key.txt", "r") as f:
    key = f.read().strip()
llm = OpenAI(api_key=key)
memory = ConversationBufferMemory(memory_key="chat_history")
tools = load_tools(["serpapi"], llm=llm, serpapi_api_key="__hidden__")
selected_country = "Italy"

# Function to reinitialize the agent when the country changes
def reinitialize_agent():
    global agent
    agent = initialize_agent(tools, llm, agent_type="conversational-react-description", memory=memory, verbose=True,
                             system_message=f"You are an expert in helping immigrants integrate into a new country. The user wants to move to {selected_country}. Provide detailed advice on paperwork, legal requirements, and practical steps to move to this country. Additionally, assist with translations and cultural integration questions to help newcomers feel at home.")

# Initialize the agent initially
reinitialize_agent()

# Set up the Streamlit page
def main():
    global selected_country
    st.set_page_config(page_title='InterGREAT.ai - Immigrant Integration Helper', layout='wide')

    # Add a taskbar on the top using streamlit-option-menu
    selected = option_menu(
        menu_title='Navigation',
        options=['Home', 'About', 'Services', 'Contact', 'FAQ', 'Help'],
        icons=['house', 'info-circle', 'gear', 'envelope', 'question-circle', 'life-ring'],
        menu_icon='cast',
        default_index=0,
        orientation='horizontal'
    )

    # Top right country selector
    countries = [
        "United States", "Canada", "United Kingdom", "Australia", "Germany", "France", "Italy", "Spain", "Netherlands",
        "Sweden",
        "Norway", "Denmark", "Finland", "Switzerland", "Japan", "South Korea", "India", "Brazil", "Mexico",
        "South Africa"
    ]
    government_websites = {
        "United States": "https://www.usa.gov/",
        "Canada": "https://www.canada.ca/",
        "United Kingdom": "https://www.gov.uk/",
        "Australia": "https://www.australia.gov.au/",
        "Germany": "https://www.bundesregierung.de/",
        "France": "https://www.service-public.fr/",
        "Italy": "https://www.governo.it/",
        "Spain": "https://www.lamoncloa.gob.es/",
        "Netherlands": "https://www.government.nl/",
        "Sweden": "https://www.government.se/",
        "Norway": "https://www.regjeringen.no/",
        "Denmark": "https://www.denmark.dk/",
        "Finland": "https://valtioneuvosto.fi/en",
        "Switzerland": "https://www.admin.ch/",
        "Japan": "https://www.japan.go.jp/",
        "South Korea": "http://www.korea.net/",
        "India": "https://www.india.gov.in/",
        "Brazil": "https://www.gov.br/",
        "Mexico": "https://www.gob.mx/",
        "South Africa": "https://www.gov.za/"
    }

    st.sidebar.title("I want to move to")
    selected_country = st.sidebar.selectbox("Select your destination country", countries,
                                            index=countries.index('Italy'), key='country_select',
                                            on_change=reinitialize_agent)

    # Display the selected country
    st.sidebar.write(f"🌍 Selected Country: {selected_country}")
    # Display the flag of the selected country
    flag_images = {
        "United States": "flags/us.png",
        "Canada": "flags/ca.png",
        "United Kingdom": "flags/gb.png",
        "Australia": "flags/au.png",
        "Germany": "flags/de.png",
        "France": "flags/fr.png",
        "Italy": "flags/it.png",
        "Spain": "flags/es.png",
        "Netherlands": "flags/nl.png",
        "Sweden": "flags/se.png",
        "Norway": "flags/no.png",
        "Denmark": "flags/dk.png",
        "Finland": "flags/fi.png",
        "Switzerland": "flags/ch.png",
        "Japan": "flags/jp.png",
        "South Korea": "flags/kr.png",
        "India": "flags/in.png",
        "Brazil": "flags/br.png",
        "Mexico": "flags/mx.png",
        "South Africa": "flags/za.png"
    }
    flag_image = flag_images.get(selected_country, None)
    if flag_image:
        st.sidebar.image(flag_image, use_container_width=True)

    # Add a chart that shows the value oscillation of the country's currency
    st.sidebar.write("📈 **Currency Value Oscillation**")
    import yfinance as yf

    # Fetch currency data for the selected country
    currency_tickers = {
        "United States": "EURUSD=X",
        "Canada": "EURCAD=X",
        "United Kingdom": "EURGBP=X",
        "Australia": "EURAUD=X",
        "Germany": "EURUSD=X",
        "France": "EURUSD=X",
        "Italy": "EURUSD=X",
        "Spain": "EURUSD=X",
        "Netherlands": "EURUSD=X",
        "Sweden": "EURSEK=X",
        "Norway": "EURNOK=X",
        "Denmark": "EURDKK=X",
        "Finland": "EURUSD=X",
        "Switzerland": "EURCHF=X",
        "Japan": "EURJPY=X",
        "South Korea": "EURKRW=X",
        "India": "EURINR=X",
        "Brazil": "EURBRL=X",
        "Mexico": "EURMXN=X",
        "South Africa": "EURZAR=X"
    }

    ticker = currency_tickers.get(selected_country, None)
    if ticker:
        data = yf.download(ticker, period="1mo", interval="1d")
        if not data.empty:
            min_value = data['Close'].min() * 0.95
            max_value = data['Close'].max() * 1.05
            st.sidebar.line_chart(data['Close'][(data['Close'] >= min_value) & (data['Close'] <= max_value)],
                                  height=200, use_container_width=True)
            # Display the actual value and currency name
            latest_value = float(data['Close'].iloc[-1])
            st.sidebar.write(f"Current Value: {latest_value:.2f} USD")
            currency_name = ticker.split('=')[0][:3]
            st.sidebar.write(f"Currency: {currency_name}")
        else:
            st.sidebar.write("⚠️ No currency data available for the selected country.")

    # Add government website search tool
    st.sidebar.write("### Government Website")
    gov_website = government_websites.get(selected_country, "")
    if gov_website:
        gov_query = st.sidebar.text_input("Search in the government website:", key='gov_query')
        if st.sidebar.button("Search in Gov Website", key='gov_search_button'):
            if gov_query:
                with st.spinner('💬 Asking InteGREAT...'):
                    custom_prompt = f"Use SERPAPI to search for information about: {gov_query} related to {selected_country}. Provide relevant information and links if available."
                    response = agent.run(custom_prompt)
                st.sidebar.markdown(
                    f"<div style='padding: 10px; background-color: #d0d0f5; border-radius: 5px; color: #000; font-weight: bold;'><strong>Response:</strong> {response}</div>",
                    unsafe_allow_html=True)

    # Center the title
    st.markdown("""
        <div style="text-align: center; position: relative;">
     <h1 style="color: #ff6347;"InteGREAT</h1>
</div>
    """, unsafe_allow_html=True)

    # Directly show the question prompt bar and chat history
    st.markdown('<div style="text-align: center;"><hr><h2 id="query-section">Ask InteGREAT</h2></div>',
                unsafe_allow_html=True)

    # Initialize session state for chat history
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []

    # Display chat history
    for entry in st.session_state.chat_history:
        st.markdown(f"""
            <div style="padding: 10px; background-color: #f0f0f0; border-radius: 10px; margin: 10px 0;">
                <strong>User:</strong> {entry['user']}<br>
                <strong>InteGREAT:</strong> {entry['response']}
            </div>
        """, unsafe_allow_html=True)

    # Input field for agent query
    query = st.text_input('Ask a question to InteGREAT:', key='query_input',
                          placeholder='Type your question here...')
    st.markdown(f"""
        <style>
            div.stTextInput > div > input {{
                padding-right: 40px;
            }}
        </style>
    """, unsafe_allow_html=True)

    # Button to ask the agent
    if st.button('Ask Agent', key='ask_button'):
        if query:
            with st.spinner('Waiting for InteGREATs response...'):
                response = agent.run(query)
                # Save query and response to chat history
                st.session_state.chat_history.append({"user": query, "response": response})
            # Display the updated chat history
            st.experimental_set_query_params()
        else:
            st.error("Please enter a query.")

if __name__ == "__main__":
    main()
