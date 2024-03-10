import pinecone 

from langchain.vectorstores import Pinecone
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.llms.huggingface_hub import HuggingFaceHub
from langchain.chains import RetrievalQA

import streamlit as st

@st.cache_resource

api_key = '497910a9-4c3c-4223-9442-1349d1e0bd66'
environment = 'gcp-starter'

# configure client
pc = pinecone.Pinecone(api_key=api_key)
spec = pinecone.PodSpec(environment=environment)
index_name = 'kvasudata'
index = pc.Index(index_name)
indexdetails = index.describe_index_stats()

embed = HuggingFaceEmbeddings(model_name='sentence-transformers/all-mpnet-base-v2')

text_field = "text"
vectorstore = Pinecone(
    index, embed, text_field
)

query = "what is the tiger population in wayanad for 2023"

result = vectorstore.similarity_search(
    query,  # our search query
    k=3  # return most relevant docs
)

llm = HuggingFaceHub(
            huggingfacehub_api_token="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",
            repo_id="mistralai/Mistral-7B-Instruct-v0.2",
            model_kwargs={"temperature":0.1,"max_length":512}
        )

def retrieval_answer(query):
    qa = RetrievalQA.from_chain_type(
    llm=llm, 
    chain_type='stuff',
    retriever=vectorstore.as_retriever(),
    )
    query = query
    result = qa.run(query)
    return result

def main():
    st.title("Question and Answering App powered by LLM and Pinecone")

    text_input = st.text_input("Ask your query...") 
    if st.button("Ask Query"):
        if len(text_input)>0:
            st.info("Your Query: " + text_input)
            answer = retrieval_answer(text_input)
            st.success(answer)

if __name__ == "__main__":
    main()

    






