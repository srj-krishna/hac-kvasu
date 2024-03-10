import streamlit as st

import pinecone

# initialize connection to pinecone (get API key at app.pc.io)
api_key = '497910a9-4c3c-4223-9442-1349d1e0bd66'
environment = 'gcp-starter'

# configure client
pc = pinecone.Pinecone(api_key=api_key)
spec = pinecone.PodSpec(environment=environment)
index_name = 'kvasudata'

index = pc.Index(index_name)
indexdetails = index.describe_index_stats()

st.set_page_config(
    page_title=("KVASU demo"),
    page_icon="🌱",
    )

st.title("💬 AgroBot")
st.caption("🚀 powered by AgroGraph from NeuBiom Labs!")

if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "assistant",
            "content": """
        Hi! I'm AgroBot""",
        }
    ]
    
system_message = "You are an Agrobot, here to help with information and context-specific recommendations for farming in Kerala for the following query. If you don't know something just say that you don't have the information."
lang = "English"
final_prompt = ""
