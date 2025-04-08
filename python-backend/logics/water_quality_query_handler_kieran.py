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

# Supporting functions
# Creation of vectordb for email responses
def create_email_vectordb(embeddings_model,vectordb_name):
    vectorstore_path = "data/vectordb_" + vectordb_name
    # Use .listdir() method to list all the files and directories of a specified location
    # Define directory for emails
    directory = os.listdir('data/Queries Received and Email Responses')
    # Empty list which will be used to append new values
    list_of_emails = []

    for filename in directory:
        filename = "data" + '/' + 'Queries Received and Email Responses' + '/' + filename
        loader = OutlookMessageLoader(filename)
        text_from_file = loader.load()
        # append the text from the single file to the existing list
        list_of_emails.append(text_from_file[0])
        # print(f"Successfully read from {filename}")
    # Create the text splitter
    text_splitter = SemanticChunker(embeddings_model)
    # Split the documents into smaller chunks
    splitted_documents = text_splitter.split_documents(list_of_emails)
    # Create Vector Database
    vectordb = Chroma.from_documents(
        filter_complex_metadata(splitted_documents),
        embedding=embeddings_model, 
        collection_name= vectordb_name, 
        persist_directory= vectorstore_path # define location directory to save the vectordb
    )
    return vectordb # return vectordb to be used

def create_wq_reference_vectordb(embeddings_model):
    # Load in documents 
    loader_eph = PyPDFLoader('data\code-of-practice-on-drinking-water-sampling-and-safety-plans-sfa-apr-2019.pdf')
    doc_eph = loader_eph.load()
    loader_who = PyPDFLoader('data\WHO GDWQ 4th ed 1st 2nd addenda 2022-eng.pdf')
    doc_who = loader_who.load()
    loader_sfa = PyPDFLoader('data\Environmental Public Health (Water suitable for drinking)(No. 2) Regulations SFA Apr 2019.pdf')
    doc_sfa = loader_sfa.load()
 
    # Creating character splitter for document splitting and chunking
    splitter1 = RecursiveCharacterTextSplitter(
        separators=["\n\n", "\n", " ", ""],
        chunk_size=500,
        chunk_overlap=50,
        length_function=count_tokens
    )

    split_eph = splitter1.split_documents(doc_eph)
    split_who = splitter1.split_documents(doc_who)
    split_sfa = splitter1.split_documents(doc_sfa)
    split_doc_merge = split_eph + split_who + split_sfa

    # Creating basic vector database
    vectordb = Chroma.from_documents(
        collection_name="wq_reference",
        documents=split_doc_merge,
        embedding=embeddings_model,
        persist_directory="data/vectordb_wq_reference",  # Where to save data locally, remove if not neccesary
    )

    # # Alternate Code

    # doc_load = doc_eph + doc_who + doc_sfa
    # all_chunks = []
    # for doc in doc_load:
    #     chunks = splitter1.split_text(doc.page_content)
    #     for chunk in chunks:
    #         chunked_doc = {"text": chunk,"metadata":doc.metadata}
    #         all_chunks.append(chunked_doc)

    # vectordb = Chroma.from_texts(
    #     texts=[doc["text"] for doc in all_chunks],
    #     embedding=embeddings_model,
    #     metadatas=[doc["metadata"] for doc in all_chunks],
    #     collection_name="wq_reference",
    #     persist_directory="data/vectordb_wq_reference"
    # )
    return vectordb

# Checking for presence of vectordb, spun off as a separate function as it is used on Step 3 and 4.
def vectordb_acquire(vectordb_name: str):
    # Create embeddings model
    embeddings_model = OpenAIEmbeddings(model = 'text-embedding-3-small',show_progress_bar=True)
    vectorstore_path = "data\\vectordb_" + vectordb_name
    # Create code to differentiate between the two vectordbs (vectordb_email_semantic and vectordb_reference) in this workflow
    match vectordb_name.lower():
        case name if 'email' in name:
        # check for presence of email_semantic vectordb
            if os.path.exists(vectorstore_path):
                # If directory exists, load using Chroma.
                print('VectorDB found, now loading existing vector database...')
                # Obtain current script's directory
                current_dir = os.path.dirname(os.path.abspath(__file__))
                # Go up one level to main directory
                root_dir = os.path.dirname(current_dir)
                # construct path to the vectordb folder
                persist_directory = os.path.join(root_dir,vectorstore_path)
                vectordb = Chroma(
                    persist_directory=persist_directory,
                    collection_name=vectordb_name,
                    embedding_function=embeddings_model
                )
                print(f'{vectordb_name} loaded successfully!')
            else:
                print('email_semantic vector database directory not found, proceeding to create vector database.')
                vectordb = create_email_vectordb(embeddings_model,vectordb_name)

            return vectordb # return vectordb to be used
        
        case "vectordb_wq_reference":
        # check for the presence of vectordb_wq_reference
            if os.path.exists('data\\vectordb_wq_reference'):
                # If directory exists, load using Chroma.
                print('VectorDB found, now loading existing vector database...')
                # Obtain current script's directory
                current_dir = os.path.dirname(os.path.abspath(__file__))
                # Go up one level to main directory
                root_dir = os.path.dirname(current_dir)
                # construct path to the vectordb folder
                persist_directory = os.path.join(root_dir,'data\\vectordb_wq_reference')
                vectordb = Chroma(
                    persist_directory=persist_directory,
                    collection_name='wq_reference',
                    embedding_function=embeddings_model
                )
                print('wq_reference vectordb loaded successfully!')
            else:
                print('wq_reference vector database directory not found, proceeding to create vector database.')
                vectordb = create_wq_reference_vectordb(embeddings_model)
                
            return vectordb # return vectordb to be used
        
# 1. identify_water_quality parameter (keep)
def identify_water_quality_parameter(user_message):
    delimiter = "####"

    system_message = f"""
    You will be provided with water quality queries. \
    The water quality query will be enclosed in
    the pair of {delimiter}.
    Decide if the query contains any specific parameters from the 'Parameter List' column in the below Dataframe.  
    {parameter_list}    
    If there are any relevant parameters found, output the names into a list. 
    If are no relevant parameters are found, output an empty list.
    Would you like to make another enquiry?".
    """

    messages =  [
        {'role':'system',
         'content': system_message},
        {'role':'user',
         'content': f"{delimiter}{user_message}{delimiter}"},
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
def substantiate_water_quality_parameter(wq_parameters): # consider using the parameters or user input.
    # Check for presence of vectordb
    vectordb = vectordb_acquire("vectordb_wq_reference")
    # llm to be used in RAG pipeplines in this notebook
    llm = ChatOpenAI(model='gpt-4o-mini', temperature=0, seed=42)
    template = """You are an AI tasked with finding relevant reference materials related to water quality parameters mentioned in the question. 
    Use the provided context to formulate a concise answer. If you don't know the answer, say, "I don't know"—don't guess. 
    Answer in 5 sentences or fewer, and cite specific sections or references where possible.

    Context: {context}

    Question: {question}

    Your Answer: 
    """
    QA_CHAIN_PROMPT = PromptTemplate.from_template(template)
    print('QA_chain prompt formed')
    
    # Debugging: Check if retrieval returns results
    retrieved_docs = vectordb.as_retriever(k=10).get_relevant_documents(f'Obtain guideline values for {wq_parameters}')
    if not retrieved_docs:
        return "No relevant reference materials found for the given parameters."

    # Run the RetrievalQA chain
    try:
        qa_chain = RetrievalQA.from_chain_type(
            llm=llm,
            retriever=vectordb.as_retriever(k=10),
            return_source_documents=False,  # Set to True for debugging if needed
            chain_type_kwargs={"prompt": QA_CHAIN_PROMPT}
        )
        answer = qa_chain.invoke(f'Obtain the guideline values and relevant information for the parameters listed in {wq_parameters}')
    except Exception as e:
        return f"Error during QA chain execution: {str(e)}"
    
    return answer

#4. Get relevant email records
def get_email_records(user_message,vectordb_name):
    # Check for presence of vectordb
    vectordb = vectordb_acquire(vectordb_name)

    output_step_4 = vectordb.similarity_search_with_relevance_scores(user_message, k=4)
    return output_step_4

# 5. generate_response_based_on_water_quality_standards
def generate_response_based_on_water_quality_standards(user_message, water_quality_parameters, wq_parameters_reference, email_archives):
    delimiter = "####"

    # ORIGINAL PROMPT
    # system_message = f"""
    # Follow these steps to answer the customer queries.
    # The customer query will be delimited with a pair {delimiter}.

    # Step 1:{delimiter} If the user is is asking about water quality, \
    # understand the relevant parameter(s) from the 'Parameter List' column in table below:
    # {water_quality_parameters}

    # Step 2:{delimiter} Present the water quality parameters (listed in Step 1) and PUB Drinking Water Standard\
    # in table format. The water quality parameters must be on the first column, with 'PUB Drinking Water Standard Average' \
    # and 'PUB Drinking Water Standard Range' on subsequent columns. \
    # Do not make comparisons between 'PUB Drinking Water Standard Range' and 'PUB Drinking Water Standard Average'.
    # State the WHO Guidelines and EPH Regulations for the parameters found in {wq_parameters_reference}, 
    # assure water is safe for drinking. You must only rely on figures from the table. 
    
    # Step 3:{delimiter}: Provide a draft email body using the writing style using content from {email_archives}.  
    # Answer the customer in a friendly tone. \
    # Do not make comparisons between 'PUB Drinking Water Standard Range' and 'PUB Drinking Water Standard Average'. \
    # Make sure the statements are factually accurate. \
    # Avoid repeating points from Step 2.
    # Use Neural Linguistic Programming to construct your response.

    # Use the following format:
    # {delimiter} <Water quality table & Reasoning>
    # {delimiter} <response to customer>

    # Make sure to include {delimiter} to separate every step.
    # """
    system_message = f'''
    Follow these steps to answer customer queries about water quality. The customer query will be delimited with a pair {delimiter}.

    ### Step 1: Identify Relevant Parameters  
    Identify if the query mentions any specific water quality parameters from the 'Parameter List' column in the table below:  
    {water_quality_parameters}  

    - If relevant parameters are found, list them in bullet form.
    - If no parameters are found, state "No specific parameters mentioned."

    ### Step 2: Present Water Quality Standards  
    For the parameters identified in Step 1:  
    - Create a table summarizing the following:
    - Water Quality Parameter (1st column)  
    - PUB Drinking Water Standard Average (2nd column)  
    - PUB Drinking Water Standard Range (3rd column)  
    - Use WHO Guidelines and EPH Regulations to substantiate the response for each parameter.
    - Conclude whether the water meets safety guidelines for drinking based on the data.
    
    ### Step 3: Draft a Customer-Focused Email  
    Write a draft email response using information from {email_archives}.  
    - The tone should be friendly, professional, and reassuring.  
    - Avoid repeating technical data from Step 2 verbatim. Instead:
    - Summarize conclusions in layman’s terms.
    - Provide additional helpful context, if necessary.
    - Use examples or templates from {email_archives} to align the style with past correspondence.  

    ### Formatting:  
    - Begin each step with {delimiter}.  
    - End each step with {delimiter}.  
    - Include "Water quality table & Reasoning" and "Response to customer" sections.  
    - Ensure statements are factually accurate and aligned with the provided data.

    Deliver your response in this format:
    {delimiter} <Water quality table & Reasoning>  
    {delimiter} <response to customer>
    '''
    messages =  [
        {'role':'system',
         'content': system_message},
        {'role':'user',
         'content': f"{delimiter}{user_message}{delimiter}"},
    ]

    response_to_customer = get_completion_by_messages(messages)
    # response_to_customer = response_to_customer.split(delimiter)[-1]
    return response_to_customer

# response = generate_response_based_on_water_quality_standards(user_input,result_step_2,result_step_3,result_step_4)
# print(response)

def process_user_message_wq(user_input):
    # Process 1. identify_water_quality parameter
    process_step_1 = identify_water_quality_parameter(user_input)

    # Process 2: Match with PUB water quality standards and regulatory guidelines
    process_step_2 = get_water_quality_guidelines(process_step_1)

    # Process 3: Match with PUB water quality standards and regulatory guidelines
    process_step_3 = substantiate_water_quality_parameter(process_step_1)
    print('qa_chain invoked successfully initiaized')

    # Process 4: Match with PUB water quality standards and regulatory guidelines
    process_step_4 = get_email_records(user_input,'email_semantic_98') 

    # Process 5: Generate Response based on Course Details
    reply = generate_response_based_on_water_quality_standards(user_input,process_step_2,process_step_3,process_step_4)

    return reply
