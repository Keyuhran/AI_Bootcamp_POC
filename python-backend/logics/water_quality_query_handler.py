# This script contains a list of functions shown the cells below:
# 1. identify_water_quality parameter
# 2. match with PUB water quality standards and regulatory guidelines
# 3. Extract information from previous email archives
# 4. generate_response_based_on_water_quality_standards

import logging
logging.basicConfig(level=logging.INFO, filename="log.log", filemode = 'w')

from helper_functions import llm
from helper_functions.llm import get_completion_by_messages
import os
from langchain_openai import ChatOpenAI
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_community.document_loaders import OutlookMessageLoader
from langchain_community.vectorstores.utils import filter_complex_metadata
from langchain_experimental.text_splitter import SemanticChunker
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from helper_functions.llm import count_tokens
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
import chromadb

# Import the data file in csv format
import pandas as pd
import json
# Convert .csv table into pandas Dataframe
water_quality_df = pd.read_csv('data/utf8_Consolidated WQ Parameters.csv')
parameter_list = water_quality_df['Parameter List'].tolist()

# Cache for loaded vector DBs
vector_cache = {}

# Supporting functions
# Creation of vectordb for email responses
def create_email_vectordb(embeddings_model,vectordb_name):
    vectorstore_path = "data/vectordb_" + vectordb_name
    directory = os.listdir('data/Queries Received and Email Responses')
    list_of_emails = []
    for filename in directory:
        filename = os.path.join('data', 'Queries Received and Email Responses', filename)
        loader = OutlookMessageLoader(filename)
        text_from_file = loader.load()
        list_of_emails.append(text_from_file[0])
    text_splitter = SemanticChunker(embeddings_model)
    splitted_documents = text_splitter.split_documents(list_of_emails)
    vectordb = Chroma.from_documents(
        filter_complex_metadata(splitted_documents),
        embedding=embeddings_model, 
        collection_name= vectordb_name, 
        persist_directory= vectorstore_path
    )
    return vectordb

def create_wq_reference_vectordb(embeddings_model):
    from langchain_community.vectorstores import Chroma
    from langchain.docstore.document import Document

    loader_eph = PyPDFLoader('data/code-of-practice-on-drinking-water-sampling-and-safety-plans-sfa-apr-2019.pdf')
    doc_eph = loader_eph.load()
    loader_who = PyPDFLoader('data/WHO GDWQ 4th ed 1st 2nd addenda 2022-eng.pdf')
    doc_who = loader_who.load()
    loader_sfa = PyPDFLoader('data/Environmental Public Health (Water suitable for drinking)(No. 2) Regulations SFA Apr 2019.pdf')
    doc_sfa = loader_sfa.load()

    splitter = RecursiveCharacterTextSplitter(
        separators=["\n\n", "\n", " ", ""],
        chunk_size=1024,
        chunk_overlap=50,
        length_function=count_tokens
    )
    split_docs = splitter.split_documents(doc_eph + doc_who + doc_sfa)
    

    # ⚠️ Filter out empty or whitespace-only chunks
    split_docs = [doc for doc in split_docs if doc.page_content.strip()]

    persist_dir = "data/vectordb_wq_reference"
    collection_name = "wq_reference"

    vectordb = Chroma(
    embedding_function=embeddings_model,
    collection_name=collection_name,
    persist_directory=persist_dir
)

    batch_size = 100
    for i in range(0, len(split_docs), batch_size):
        batch = split_docs[i:i + batch_size]
        if all(doc.page_content.strip() for doc in batch):  # Redundant safety check
            vectordb.add_documents(batch)

    return vectordb

def vectordb_acquire(vectordb_name: str, force_rebuild: bool = False):
    global vector_cache

    if not force_rebuild and vectordb_name in vector_cache:
        return vector_cache[vectordb_name]

    embeddings_model = OpenAIEmbeddings(model='text-embedding-3-small', show_progress_bar=True)
    vectorstore_path = f"data/vectordb_{vectordb_name}"

    if 'email' in vectordb_name:
        current_dir = os.path.dirname(os.path.abspath(__file__))
        root_dir = os.path.dirname(current_dir)
        persist_directory = os.path.join(root_dir, vectorstore_path)

        if force_rebuild and os.path.exists(persist_directory):
            import shutil
            shutil.rmtree(persist_directory)

        if os.path.exists(persist_directory):
            vectordb = Chroma(
                persist_directory=persist_directory,
                collection_name=vectordb_name,
                embedding_function=embeddings_model
            )
        else:
            vectordb = create_email_vectordb(embeddings_model, vectordb_name)

    elif 'wq_reference' in vectordb_name:
        persist_directory = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            '..', 'python-backend', 'data', 'vectordb_wq_reference'
        )
        persist_directory = os.path.abspath(persist_directory)

        if force_rebuild and os.path.exists(persist_directory):
            import shutil
            shutil.rmtree(persist_directory)

        if os.path.exists(persist_directory):
            vectordb = Chroma(
                persist_directory=persist_directory,
                collection_name='wq_reference',
                embedding_function=embeddings_model
            )
        else:
            vectordb = create_wq_reference_vectordb(embeddings_model)
    else:
        raise ValueError(f"Unrecognized vectordb_name: {vectordb_name}")

    vector_cache[vectordb_name] = vectordb
    return vectordb


# 1. identify_water_quality parameter (keep)
def identify_water_quality_parameter(user_message):
    delimiter = "####"
    system_message = f"""
    You will be provided with water quality queries. \
    The water quality query will be enclosed in the pair of {delimiter}.
    Decide if the query contains any specific parameters from the 'Parameter List' column in the below Dataframe.  
    {parameter_list}    
    If there are any relevant parameters found, output the names into a list. 
    If are no relevant parameters are found, output an empty list.
    Would you like to make another enquiry?".
    """
    messages =  [
        {'role':'system','content': system_message},
        {'role':'user','content': f"{delimiter}{user_message}{delimiter}"},
    ]
    output_step_1 = get_completion_by_messages(messages)
    output_step_1 = eval(output_step_1)
    return output_step_1 

# 2. match with PUB water quality standards and regulatory guidelines (keep)
def get_water_quality_guidelines(list_of_water_quality_parameters: list):
    wq_parameter_guidelines = water_quality_df[water_quality_df['Parameter List'].isin(list_of_water_quality_parameters)]
    wq_parameter_guidelines = wq_parameter_guidelines.to_markdown()
    return wq_parameter_guidelines

#3. Extract further information with reference from WHO, SFA and EPH reference material based in parameters from previous step
def substantiate_water_quality_parameter(wq_parameters):
    vectordb = vectordb_acquire("wq_reference")
    llm = ChatOpenAI(model='gpt-4o-mini', temperature=0, seed=42)
    template = """You are an AI assistant under the company PUB helping users understand water quality guidelines. 
    You are given reference material from WHO, SFA, and EPH regulatory documents. Use this context actively and construct detailed, factual answers.

    When answering:
    - Be confident in citing and summarizing provided content.
    - Prioritize clarity and structure over brevity.
    - Use bullet points, numbered steps, or short sections to break down complex explanations.
    - Do not answer with generic or vague statements. 
    - Do not refer the user externally unless necessary.
    - Prefer complete, informative responses over cautious summaries.
    - Cite sections or keywords when relevant.
    - Never tell the customer seek assistance from other authorities. PUB is the responsible party.

    Context: {context}

    Question: {question}

    Answer:"""
    QA_CHAIN_PROMPT = PromptTemplate.from_template(template)
    retrieved_docs = vectordb.as_retriever(search_type="mmr", k=20, fetch_k=50).get_relevant_documents(f'Obtain guideline values for {wq_parameters}')
    if not retrieved_docs:
        return [], "No relevant reference materials found for the given parameters."
    qa_chain = RetrievalQA.from_chain_type(
        llm=llm,
        retriever=vectordb.as_retriever(search_type="similarity", k=10),
        return_source_documents=False,
        chain_type_kwargs={"prompt": QA_CHAIN_PROMPT}
    )
    answer = qa_chain.invoke(f'Obtain the guideline values and relevant information for the parameters listed in {wq_parameters}')
    return retrieved_docs, answer

#4. Get relevant email records
def get_email_records(user_message,vectordb_name):
    vectordb = vectordb_acquire(vectordb_name)
    output_step_4 = vectordb.similarity_search_with_relevance_scores(user_message, k=4)
    return output_step_4

# 5. generate_response_based_on_water_quality_standards
def generate_response_based_on_water_quality_standards(user_message, water_quality_parameters, qa_summary, email_archives, reference_archives):
    delimiter = "####"

    system_message = f'''
    You are an AI assistant from the Public Utilities Board (PUB) of Singapore.

    Your task is to draft an official reply to customer queries about drinking water quality based on the facts provided.

    When answering:

    - **Step 1: Identify Water Quality Parameters**
      - Use the provided water quality parameter table below:
      {water_quality_parameters}
      - If relevant parameters (e.g., fluoride, lead, nitrate) are detected, quote their  standard average and range.
      - Cite guidelines from other sources as reassurance
      - Construct a summary table (Parameter | PUB Standard Average | PUB Standard Range | WHO Limit) if needed.

    - **Step 2: Reference Authoritative Sources**
      - Use the following QA summary based on reference documents:
      {qa_summary}
      - Only quote facts from these references. Do not invent or assume anything.

    - **Step 3: Compose Customer-Focused Reply**
      - Use the style and examples from the provided past PUB emails:
      {[doc[0].page_content for doc in email_archives if doc]}
      - The tone must be formal, helpful, confident, reassuring and concise.
      - If false or misleading claims (e.g., water dispenser companies) are mentioned, state that PUB monitors and coordinates with CCCS.
      - Always state that PUB conducts daily water sampling and Singapore tap water is safe for direct consumption.

    **Formatting Requirements**:
    - Organize your reply into two sections clearly:
      {delimiter} <Water Quality Table & Reasoning> {delimiter}
      {delimiter} <Response to Customer> {delimiter}
    - Always include citations (in accordance with EPH 2019) or (as per WHO Guidelines) to state that PUB complies with these guidelines.
    - Keep the customer response under 2-3 paragraphs maximum. Each paragraph should have a minimum of 4-5 sentences.
    - Be technical but understandable. Avoid vague language.

    IMPORTANT:
    - Always quote exact numbers for parameters if found.
    - Never omit regulatory references.
    - Never use generic phrases like "PUB complies with regulations" without citing specifics.
    '''

    messages = [
        {'role': 'system', 'content': system_message},
        {'role': 'user', 'content': f"{delimiter}{user_message}{delimiter}"},
    ]

    return get_completion_by_messages(messages)

def process_user_message_wq(user_input):
    process_step_1 = identify_water_quality_parameter(user_input)
    process_step_2 = get_water_quality_guidelines(process_step_1)
    ref_chunks, process_step_3 = substantiate_water_quality_parameter(process_step_1)
    process_step_4a = get_email_records(user_input,'email_semantic_98') 
    process_step_4b = get_email_records(user_input,'wq_reference') 
    reply = generate_response_based_on_water_quality_standards(user_input, process_step_2, process_step_3, process_step_4a, ref_chunks)
    return reply
