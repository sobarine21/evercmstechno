import streamlit as st
import google.generativeai as genai
import requests
import time

# Configure the API key securely from Streamlit's secrets
genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])

# Google Custom Search API Setup
def search_web(query):
    """
    Function to search for a query on the web using Google Custom Search.
    Returns a JSON response with search results.
    """
    cx = st.secrets["GOOGLE_CX"]  # Google Custom Search Engine ID
    api_key = st.secrets["GOOGLE_API_KEY"]  # API Key for Custom Search
    search_url = "https://www.googleapis.com/customsearch/v1"
    
    params = {
        "q": query,
        "cx": cx,
        "key": api_key,
        "num": 5  # Limit to top 5 search results
    }
    
    try:
        response = requests.get(search_url, params=params)
        response.raise_for_status()  # Raise HTTPError for bad responses
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Error while fetching search results: {e}")
        return {}

# AI Content Generation
def generate_ai_content(prompt, model_name='gemini-1.5-flash'):
    """
    Function to generate content using Google Generative AI.
    """
    try:
        # Load and configure the model
        model = genai.GenerativeModel(model_name)
        
        # Generate response from the model
        response = model.generate_content(prompt)
        
        if response.text:
            return response.text
        else:
            st.error("Failed to generate content.")
            return ""
    except Exception as e:
        st.error(f"Error during AI content generation: {e}")
        return ""

# Streamlit App UI
st.title("Ever AI - Content Generator & Web Search Tool")
st.write("This app generates AI content based on your prompt and checks if similar content is available online.")

# Prompt input field
prompt = st.text_area("Enter your prompt:", "Best alternatives to JavaScript?")

# Button to generate response and search for web results
if st.button("Generate Response & Search Web"):
    if prompt:
        with st.spinner('Generating response...'):
            # Step 1: Generate AI content
            ai_content = generate_ai_content(prompt)
            
            if ai_content:
                # Display generated content
                st.write("AI-Generated Response:")
                st.write(ai_content)
                
                # Step 2: Search the web for content similar to the AI-generated content
                st.write("Checking if similar content exists on the web...")
                search_results = search_web(prompt)
                
                if search_results.get("items"):
                    st.write("Found the following web results:")
                    for i, result in enumerate(search_results["items"]):
                        st.write(f"{i+1}. **{result['title']}** - {result['link']}")
                        st.write(f"   {result['snippet']}")
                else:
                    st.write("No similar web content found.")
                    
                # Step 3: Content Duplication Check
                st.write("Performing content duplication check...")
                duplicate_found = False
                for result in search_results.get("items", []):
                    if ai_content.lower() in result['snippet'].lower():
                        duplicate_found = True
                        st.warning(f"Potential duplicate content found: {result['title']} - {result['link']}")
                        break
                
                if not duplicate_found:
                    st.success("No significant content duplication found.")
    else:
        st.error("Please enter a valid prompt.")
        
# Advanced Error Handling and Progress Tracking
@st.cache_data
def cache_search_results(query):
    """Cache the search results to avoid redundant web requests."""
    st.write("Caching the search results for faster retrieval...")
    return search_web(query)

