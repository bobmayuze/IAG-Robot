import pandas

from langchain.llms import OpenAI
from langchain.document_loaders.csv_loader import CSVLoader
from langchain.document_loaders import Docx2txtLoader
from langchain import PromptTemplate, LLMChain

QUESTIONS = [
  "What is the name of the company?",
  "Where is the company incorporated?",
  "How many Common Board Members are expected?",
  "How many Mutual Consent Board Members are expected?",
  "How many Series Seed Board Members are expected?",
  "What is the Major Purchaser Dollar Threshold?",
  "What is the Total Series Seed Investment Amount?",
  "What is the Available Option Pool after closing?",
  "How much is the company reimbursing investors?",
  "What is the Series Seed price per share?",
  "What are the total number of common shares issued and outstanding before this financing? The answer should be a single number.",
  "What is the total number of shares reserved for the option pool after the financing closes? The answer should be a single number.",
  "What is the total number of issued and outstanding options currently? The answer should be a single number.",
  "What is the total number of options available to grant? This is the difference between the total number of shares reserved for the option pool after the financing closes and the total number of issued and outstanding options currently. The answer should be a single number and not a difference.",
  "Return tuples of the investors investing in the round, how much are they investing, and how many shares of Series Seed they receive from the investment for each investor. Each tuple should be enclosed in parenthesis.",
  "What is the total number of shares that will be authorized after closing? The answer should be a single number.",
  "What is the total number of common shares that will be authorized after closing? The answer should be a single number.",
  "What is the total number of preferred shares that will be authorized after closing? The answer should be a single number.",
]


def get_answer_from_termsheet(termsheet_str, termsheet_question):
  question_prompt_template = """Use the following portion of a company term sheet document to see if any of the text is relevant to answer the question. The answer should be succinct and contain no extra information other than answering the question. If the context does not provide enough information to answer the question, return "COMPLETE_THIS".
{context}
Question: {question}
Answer:"""

  prompt = PromptTemplate(template=question_prompt_template,
                          input_variables=["context", "question"])

  llm = OpenAI()
  llm_chain = LLMChain(prompt=prompt, llm=llm)

  return llm_chain.run(context=termsheet_str, question=termsheet_question)


def get_answer_from_captable(captable_str, captable_question):
  question_prompt_template = """Use the following portion of a company cap table spreadsheet to see if any of the text is relevant to answer the question. The answer should be succinct and contain no extra information other than answering the question. If the context does not provide enough information to answer the question, return "COMPLETE_THIS".
{context}
Question: {question}
Answer:"""
  prompt = PromptTemplate(template=question_prompt_template,
                          input_variables=["context", "question"])

  llm = OpenAI()
  llm_chain = LLMChain(prompt=prompt, llm=llm)

  return llm_chain.run(context=captable_str, question=captable_question)


def answer_questions(document_file_path,
                     xls_file_path,
                     questions=QUESTIONS,
                     cap_table_questions_number=9):

  docx_loader = Docx2txtLoader(document_file_path)

  docx_documents = docx_loader.load()

  docx_context = docx_documents[0].page_content

  xls_df = pandas.read_excel(xls_file_path)
  xls_df.to_csv('captable.csv', encoding='utf-8')

  xls_loader = CSVLoader(file_path='./captable.csv')

  xls_documents = xls_loader.load()

  xls_context = ' '.join([doc.page_content for doc in xls_documents])

  question_to_docsearch = {
    q: ("TERMSHEET" if i < cap_table_questions_number else "CAPTABLE")
    for i, q in enumerate(questions)
  }

  questions_to_answers = {}

  for question in questions:

    if question_to_docsearch[question] == 'TERMSHEET':
      questions_to_answers[question] = get_answer_from_termsheet(
        docx_context, question)

    else:
      questions_to_answers[question] = get_answer_from_captable(
        xls_context, question)

  res = {}
  for t in field_to_question:
    res[t] = {}
    for q in field_to_question[t]:
      if field_to_question[t][q] in questions_to_answers:
        res[t][q] = questions_to_answers[field_to_question[t][q]]
      else:
        res[t][q] = field_to_question[t][q]

  return res

field_to_question = {
  "OVERVIEW_DEFINITIONS": {
    "Agreement_Date": "__NONE__",
    "Company": "What is the name of the company?",
    "Governing_Law": "Delaware",
    "Dispute_Resolution_Jurisdiction": "Santa Clara, CA",
    "State_of_Incorporation": "Where is the company incorporated?",
    "Stock_Plan": "__NONE__"
  },
  "BOARD_COMPOSITION_DEFINITIONS": {
    "Common_Board_Member_Count": "How many Common Board Members are expected?",
    "Mutual_Consent_Board_Member_Count":
    "How many Mutual Consent Board Members are expected?",
    "Series_Seed_Board_Member_Count":
    "How many Series Seed Board Members are expected?",
    "Common_Control_Holders": "__NONE__"
  },
  "TERM_SHEET_DEFINITIONS": {
    "Major_Purchaser_Dollar_Threshold":
    'What is the Major Purchaser Dollar Threshold?',
    "Purchase_Price":
    "What is the Series Seed price per share?",
    "Total_Series_Seed_Investment_Amount":
    "What is the Total Series Seed Investment Amount?",
    "Unallocated_Post_Money_Option_Pool_Percent":
    "What is the Available Option Pool after closing?",
    "Purchaser_Counsel_Reimbursement_Amount":
    "How much is the company reimbursing investors?"
  },
  "RESULTING_CAP_TABLE_DEFINITIONS": {
    "Common_Shares_Issued_and_Outstanding_Pre_Money":
    "What are the total number of common shares issued and outstanding before this financing? The answer should be a single number.",
    "Total_Post_Money_Shares_Reserved_for_Option_Pool":
    "What is the total number of shares reserved for the option pool after the financing closes",
    "Number_of_Issued_And_Outstanding_Options":
    "What is the total number of issued and outstanding options currently? The answer should be a single number.",
    "Unallocated_Post_Money_Option_Pool_Shares":
    "What is the total number of options available to grant? This is the difference between the total number of shares reserved for the option pool after the financing closes and the total number of issued and outstanding options currently. The answer should be a single number and not a difference.",
    "Purchasers":
    'Return tuples of the investors investing in the round, how much are they investing, and how many shares of Series Seed they receive from the investment for each investor. Each tuple should be enclosed in parenthesis.',
  }
}
