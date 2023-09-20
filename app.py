########################################################
                #streamlit app#
########################################################


import streamlit as st
import openai
import os
from dotenv import load_dotenv
load_dotenv()

openai.api_key = os.getenv("OPENAI_API_KEY")

def solarpdfllm(context:str, chat_history:str, human_input):
    final_response=openai.ChatCompletion.create(
        model="gpt-3.5-turbo-16k",
        messages=[
        {"role": "system", "content": """you are a helpful chatbot who needs to answer questions about 7-TSVG_Series_High-voltage_Static_Var_Generator_User_Manual_

It is a user manual for the TSVG Series High-Voltage Static Var Generator, which is a device that provides reactive power compensation on electrical grids.
The manual is intended for users and operators of the device. It provides instructions on transportation, installation, operation, maintenance, and troubleshooting.
The device falls in the domain of electrical engineering, specifically power system equipment. It is used to stabilize voltage, improve power quality, and increase stability on electrical grids.
Key features of the device include:
Provides continuously variable capacitive and inductive reactive power to control voltage and reactive power
Uses IGBT chain circuit converters
Rated voltages from 3kV to 35kV
Capacities from 1MVar to 42MVar
The manual covers:
Product specifications, naming, components
Transportation and installation precautions
Instructions for operation panel, touchscreen interface
Basic startup, shutdown and reset procedures
Routine maintenance tasks
Troubleshooting guide for faults
Replacement procedures for main parts
Overall, it provides comprehensive instructions and information for users to properly install, operate, and maintain the high-voltage static var generator device.
"""},
        {"role": "user", "content": f"""
    CONTEXT: {context}
    You are a helpful assistant, above is some context, 
    Please answer the question, and make sure you follow ALL of the rules below:
    1. Answer the questions only based on context provided, do not make things up, say i don't know if the information is not in the context
    2. Answer questions in a helpful manner that straight to the point, with clear structure & all relevant information that might help users answer the question
    3. Anwser should be formatted in Markdown with images in html format
    4. If there are relevant tables or markdown images they are very important reference data, please include them as part of the answer
    5. Convert markdown links to html like this:\nmarkdown:!(<alt-text>)[<image-path>]\nhtml:<img src="https://raw.githubusercontent.com/GeneralKugelBlitz/solarpdfchatbot/main/<image-path>" alt="<alt-text>" width="600"/>.\n\nExample: ![](Aspose.Words.a6dfd08d-0e42-4d9a-a393-729bb7fea2b2.001.png)\ninto this html:<img src="https://raw.githubusercontent.com/GeneralKugelBlitz/solarpdfchatbot/main/Aspose.Words.a6dfd08d-0e42-4d9a-a393-729bb7fea2b2.001.png" alt="" width="600"/>

    {chat_history}
    Human: {human_input}
    ANSWER (formatted in Markdown):
"""}
        ],
        temperature=0,
        stream=False
    )
    return final_response["choices"][0]["message"]["content"]


import dataclasses

@dataclasses.dataclass
class UserConversation:
    conversation: list[str] = dataclasses.field(default_factory=list)

    def add_to_conversation(self, message: str):
        self.conversation.append(message)
    # write list as string but with alternating lines as user and AI


    def write_as_string(self, num_lines=5):
        start_index = 0
        if len(self.conversation) > num_lines:
            start_index = len(self.conversation) - num_lines
        # join the lines together with a newline character between them
        return "\n".join(self.conversation[start_index:])
    
def get_retrievals(query):
    
    retrieved_docs = retriever.get_relevant_documents(query)
    docs=""
    for doc in retrieved_docs:
        docs=docs+doc.page_content+"\n\n"

    return docs



if not hasattr(st.session_state, 'coversation'):
    new_conversation = UserConversation()
    st.session_state.conversation = new_conversation
else:
    new_conversation = st.session_state.conversation

if not hasattr(st.session_state, 'retriever'):
    from retriever import retriever
    st.session_state.retriever = retriever
else:
    retriever = st.session_state.retriever

#retrieved_docs = retriever.get_relevant_documents("how to use instruction panel")

#chain({"input_documents": retrieved_docs, "human_input": "can you tell me how to use instruction panel, hopefullu with some images"}, return_only_outputs=True)


import re

def modify_markdown_links(input_string, username, repository):
    # Regular expression pattern to match Markdown image links
    pattern = r'!\[(.*?)\]\((.*?)\)'

    # Function to replace Markdown link with the desired format
    def replace_link(match):
        alt_text = match.group(1)
        image_path = match.group(2)
        raw_url = f'https://raw.githubusercontent.com/{username}/{repository}/main/{image_path}'
        return f'![{alt_text}]({raw_url})'

    # Use re.sub to find and replace all Markdown links in the input string
    modified_string = re.sub(pattern, replace_link, input_string)

    return modified_string


username="GeneralKugelBlitz"
repository="solarpdfchatbot"

st.title("TSVG Series High-voltage Static Var Generator User Manual Chatbot")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"], unsafe_allow_html=True)

# React to user input
if prompt := st.chat_input("Ask about TSVG var generator"):
    # Display user message in chat message container
    st.chat_message("user").markdown(prompt)
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    new_conversation.add_to_conversation(f"human:prompt")
    response=solarpdfllm(get_retrievals(prompt), new_conversation.write_as_string(), prompt)
    new_conversation.add_to_conversation(f"assistant:{response}")
    st.session_state.conversation = new_conversation

    modify_markdown_links(response, username, repository)

    # Display assistant response in chat message container
    with st.chat_message("assistant"):
        st.markdown(response, unsafe_allow_html=True)
    
    # Add assistant response to chat history
    st.session_state.messages.append({"role": "assistant", "content": response})