# Role of this script is to check for the presence of a json file 

import json
import requests
import time
from bs4 import BeautifulSoup
import os
from langchain.chains import RetrievalQA
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_community.vectorstores import Chroma
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate, PromptTemplate


def create_pub_faq_json():
# leave the script on rails or make it a generic scrapping script that requires list of urls and save path for the json output.

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.121 Safari/537.36"
    }
    url = [
        "https://www.pub.gov.sg/Public/WaterLoop/Water-Quality",
        "https://www.pub.gov.sg/Public/KeyInitiatives/Smart-Water-Meter"
        ]
    scraped_data = []

    for url in url:
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Remove scripts and styles
            for script in soup(["script", "style"]):
                script.decompose()
            
            # Extract text in meaningful sections
            sections = []
            for header in soup.find_all(['h1', 'h2', 'h3', 'p']):
                sections.append(header.get_text(strip=True))
            
            page_data = {
                "url": url,
                "sections": sections
            }
            
            scraped_data.append(page_data)            
            time.sleep(1) # Respectful scraping delay
        else:
            print(f"Failed to retrieve {url} with status code: {response.status_code}")

    # Save data
    # Determine save directory for the json file.
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    test_dir = os.path.join(root_dir,'data\\pub_site_faq.json')
    with open(test_dir, "w") as f: # using w will rewrite the json file if it already exists
        json.dump(scraped_data, f)
    # not return specified as vectordb creation will pull the json file directly from the directory.

def create_pub_faq_vectordb():
    with open("data\\pub_site_faq.json", "r") as f:
        pub_faq = json.load(f)

    embeddings_model = OpenAIEmbeddings(model = 'text-embedding-3-small',show_progress_bar=True)
    text_splitter = RecursiveCharacterTextSplitter(chunk_size = 300, chunk_overlap = 50)
    vectordb = Chroma(
        collection_name= "PUB_FAQ_collection",
        embedding_function=embeddings_model,
        persist_directory='data/PUB_FAQ_collection'
            )

    for entry in pub_faq:
        url = entry["url"]
        sections = entry["sections"]

        # combine the lists of strings into a single string that is then split
        full_texts = " ".join(sections)       
        split_texts = text_splitter.split_text(full_texts)

        # embed each chunk and generate embedding, next store it in the ChromaDB.
        for idx, chunk in enumerate(split_texts):
            document_id = f"{url}#chunk-{idx + 1}"
            vectordb.add_texts(
                texts=[chunk],
                metadatas=[{"url":url}],
                ids = [document_id]
            )            
    print(f'Vector data base created with number of chunks = {vectordb._collection.count()}')
    return vectordb

def final_production_claim_response(public_query):

    # Create embeddings model
    embeddings_model = OpenAIEmbeddings(model = 'text-embedding-3-small',show_progress_bar=True)    
    # check for presence of vectordb
    if os.path.exists('data\\PUB_FAQ_collection'):
        print('PUB FAQ vectordb file found. Proceeding to load...')
        # Obtain current script's directory
        current_dir = os.path.dirname(os.path.abspath(__file__))
        # Go up one level to main directory
        root_dir = os.path.dirname(current_dir)
        # construct path to the vectordb folder
        persist_directory = os.path.join(root_dir,'data\\PUB_FAQ_collection')
        vector_store = Chroma(
            persist_directory=persist_directory,
            collection_name='PUB_FAQ_collection',
            embedding_function=embeddings_model
        )
    else:
        print('PUB FAQ vectordb not found. Proceeding to create vector database')
        print('Checking for presence of PUB FAQ JSON to create vector database')

        # check for the presence of the json file.
        if os.path.isfile('data\\pub_site_faq.json'):
            print('PUB FAQ JSON file exists. Proceeding to load...')
        else: 
            print('PUB FAQ JSON file not found. Proceeding with creation through website scrapping')
            create_pub_faq_json()    
        vector_store = create_pub_faq_vectordb() 

    # Proceeding to create RetrievalQA
    llm = ChatOpenAI(model='gpt-4o-mini', temperature=0, seed=42)

    # Build prompt
    # delimiter = "###"
    # system_prompt = SystemMessagePromptTemplate.from_template("""You are a customer service representative. 
    # Use the given context to answer public query delimited with a pair of '###' delimiters.
    # If you don't know the answer, please indicate as such. Keep the answer as concise as possible.
    # {context}
    # Question: ###{question}###
    # Helpful Answer:
    # """)
    # human_message = HumanMessagePromptTemplate.from_template("{question}")
    # prompt = ChatPromptTemplate.from_messages([system_prompt, human_message])
    
    # qa_chain = RetrievalQA.from_chain_type(
    #     llm=llm,
    #     retriever = vector_store.as_retriever(),
    #     chain_type_kwargs ={"prompt": prompt}
    # )
    # print('code stopped at line 145')
    # response = qa_chain.invoke(public_query)
    # print('code stopped at line 146')
    # product_claim_query_response = response["result"]

    template = """Use the following pieces of context to answer the question at the end. If you don't know the answer, 
    just say that you don't know, don't try to make up an answer. Cite the relevant sections where possible. Keep the 
    answer as concise as possible.
    {context}
    Question: {question}
    Helpful Answer:"""
    QA_CHAIN_PROMPT = PromptTemplate.from_template(template)

    # Run chain
    qa_chain2 = RetrievalQA.from_chain_type(
        ChatOpenAI(model='gpt-4o-mini'),
        retriever=vector_store.as_retriever(k=10),
        return_source_documents=True, # Make inspection of document possible in debug
        chain_type_kwargs={"prompt": QA_CHAIN_PROMPT}
    )
    response = qa_chain2.invoke(public_query)
    product_claim_query_response = response["result"]

    return product_claim_query_response
