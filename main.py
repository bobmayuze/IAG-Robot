import numpy as np
import gradio as gr
import shutil
from langchain.document_loaders import UnstructuredHTMLLoader
import random
import time

HTML_FILE_PATH = './data/Arrowhead.html'

import os
from dotenv import load_dotenv
# Load environment variables from .env file
load_dotenv()
os.environ["OPENAI_API_KEY"] = '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'

from langchain.document_loaders import UnstructuredHTMLLoader
from langchain.llms import OpenAI
from langchain.indexes import VectorstoreIndexCreator
llm = OpenAI(temperature=0)

loader = UnstructuredHTMLLoader(HTML_FILE_PATH)
index = VectorstoreIndexCreator().from_loaders([loader])

def qeury_doc(built_index, query):
    res = built_index.query(query, llm=llm)
    return res

def save_html_to_docx(input_html):
    '''
    mab
    '''
    document = Document()
    new_parser = HtmlToDocx()
    html = '<h1>Title</h1>'
    new_parser.add_html_to_document(html, document)
    document.save('./data/foo-bar.docx')

def upload_file(files):
    saved_files = []
    for i, file in enumerate(files):
        source_file = file.name
        fname = source_file.split('/')[-1]
        print(fname)
        destination_file = './data/' + fname
        shutil.copy(source_file, destination_file)
        saved_files.append(destination_file)
    # return saved_files
    return 'foobar'

def upload_html(html_file):
    with open(html_file.name, "r") as file:
        html_content = file.read()
    return html_content

def respond(message, chat_history):
    bot_message = qeury_doc(index, message)
    chat_history.append((message, bot_message))
    return "", chat_history

with gr.Blocks() as demo:
    gr.Markdown(
        '''
        # 👩🏻‍⚖️ Investment Document Generator 
        Feeling overwhelmed by investment agreements? Try it out!
        '''
    )
    
    with gr.Row():
        html_input = gr.File(
            label= 'Generated Investment Agreement',
        )
        html_button = gr.Button("🦄Show it! ")

    with gr.Row():
        html_out = gr.HTML(value = '''
            '''
        )

    html_button.click(upload_html, html_input, html_out)

    with gr.Row():
        files_input = gr.File(
            label= 'Term Sheet & Cap Table',
            file_count="multiple"
        )
    
    file_button = gr.Button("🧙🏼 Generate ")

    # Generated outputs    
    with gr.Row():
        investment_agreement = gr.HTML(value = '''
            <h1 style="text-align: center;">
                Investment Agreement will be here
            </h1>
            '''
        )

    with gr.Row():
        user_query = gr.Textbox(
            label = 'Which part would you like to update'
        )
        wizard_button = gr.Button("Tell me! ")


    with gr.Row():
        chatbot = gr.Chatbot()

    wizard_button.click(respond, [user_query, chatbot], [user_query, chatbot])
    file_button.click(upload_file, inputs=files_input, outputs=investment_agreement)

demo.launch()
