import streamlit as st
from streamlit.logger import get_logger

import os

import pinecone

from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import Pinecone
from langchain_community.llms.huggingface_hub import HuggingFaceHub
from langchain.chains.question_answering import load_qa_chain
from langchain.prompts import PromptTemplate

import azure.ai.translation.text
from azure.ai.translation.text import TextTranslationClient, TranslatorCredential
from azure.ai.translation.text.models import InputTextItem
from azure.core.exceptions import HttpResponseError

text_translator = TextTranslationClient(credential = TranslatorCredential("8a775052516145059fc3839081b55967", "southeastasia"));

# initialize connection to pinecone (get API key at app.pc.io)
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

llm = HuggingFaceHub(
            huggingfacehub_api_token="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",
            repo_id="mistralai/Mistral-7B-Instruct-v0.2",
            model_kwargs={"temperature":0.1,"max_length":2500}
        )

prompt_template = """
    Answer the question as detailed as possible from the provided context, make sure to provide all the details, if the answer is not in
    provided context just say, "answer is not available in the context", don't provide the wrong answer\n\n
    Context:\n {context}?\n
    Question: \n{question}\n

    Answer:
    """
prompt = PromptTemplate(template=prompt_template, input_variables=["context", "question"])
chain = load_qa_chain(llm, chain_type="stuff", prompt=prompt)

def translate_string(from_lang, to_lang, string):
    try:
        input_text_elements = [ InputTextItem(text = string) ]
        response = text_translator.translate(content = input_text_elements, to = [to_lang], from_parameter = from_lang)
        translation = response[0] if response else None

        if translation:
            for translated_text in translation.translations:
                return translated_text.text

    except HttpResponseError as exception:
        print(f"Error Code: {exception.error.code}")
        print(f"Message: {exception.error.message}")
        return string  # return original string if translation fails

def get_final_answer(text):
        parts = text.rsplit("Answer:", 1)
        if len(parts) > 1:
            return parts[-1].strip()  # Stripping to remove any leading/trailing whitespace
        else:
            return "No answer found."

def queryllm(text):
    user_question = text
    docs = vectorstore.similarity_search(user_question)
    sourcelist = extract_sources(docs)
    response = chain({"input_documents": docs, "question": user_question}, return_only_outputs=False)
    return response["output_text"], sourcelist

def extract_sources(docs):
    unique_sources = set()
    for doc in docs:
        source_name = doc.metadata.get('source')
        if source_name:
            # Remove the specified part from the source name
            source_name = source_name.replace('/content/pdfs/', '')
            unique_sources.add(source_name)
    return ', '.join(unique_sources)

st.set_page_config(
    page_title=("KVASU demo"),
    page_icon="🌱",
    )

st.title("💬 KVASU demo")
st.caption("🚀 powered by AgroGraph from NeuBiom Labs!")
system_message = "You are an Agrobot, here to help with information and context-specific recommendations for farming in Kerala for the following query. If you don't know something just say that you don't have the information."
lang = "English"
final_prompt = ""
sourcelist = ""
    
if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "assistant",
            "content": """
        Hi! I'm AgroBot, your personal agricultural assistant. I'm here to help you with information and context-specific recommendations for farming in Kerala. I can guide you through every step of the farming process. How can I help you today? """,
        }
    ]

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

with st.sidebar:
    lang = st.radio(
    "Select Language",
    ["English", "Malayalam(മലയാളം)"], index=0)

if prompt := st.chat_input("Ask me anything!"):
    status = 1
  
    with st.chat_message("user"):
        st.markdown(prompt)
        st.session_state.messages.append({"role": "user", "content": prompt})
        
    if lang == "English":
            final_prompt = prompt
    else:
            tr_prompt = translate_string('ml','en', prompt)   
            final_prompt = tr_prompt
            
    with st.chat_message("assistant"):
        msg_placeholder = st.empty()
        msg_placeholder.markdown("Thinking...")
        full_response = ""
        final_response = ""
        sourcelist = ""

        msg_placeholder.empty()
        full_response, sourcelist = queryllm(final_prompt)
            
            # Translate to Malayalam
        result_response = str(full_response)
        result = get_final_answer(result_response)
        if lang == "English":
            final_response = result
        else:
            tr_response = translate_string('en','ml', result )   
            final_response = tr_response
        
        msg_placeholder.markdown(final_response+ "Sources :" + sourcelist)
        st.session_state.messages.append({"role": "assistant", "content": final_response + "Sources :" + sourcelist})
