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

st.set_page_config(
    page_title=("KVASU demo"),
    page_icon="🌱",
    )
