#Resume Analyzer Chatbot Assistant using Langchain API's , python, pyqt5 to query input resume to chatbot 

import sys
import fitz
import docx

import openai
from langchain_core.output_parsers import StrOutputParser
from langchain.prompts import PromptTemplate
from langchain_community.chat_models import ChatOpenAI
#from langchain import RunnableSequence

#client = openai.OpenAI(api_key="add-your-openai-api-key")
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QTextEdit, QPushButton, QLabel, QFileDialog
from PyQt5.QtCore import Qt
#setting up open ai key 

class ChatBot(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Resume Evaluation Chatbot")
        self.setFixedSize(400, 600)
        self.layout = QVBoxLayout()
        
        #ToDo allow user to attach the resume , analyse resume and match
        self.label = QLabel("Attach the resume:")
        self.layout.addWidget(self.label)
        
        self.attachButton = QPushButton("Attach Resume")
        self.attachButton.clicked.connect(self.attach_resume)
        self.layout.addWidget(self.attachButton)

        self.resumeBox = QTextEdit()
        self.layout.addWidget(self.resumeBox)

        self.labelDesignation = QLabel("Enter Queries to Validate Resume:")
        #self.layout.addWidget(self.labelDesignation)
        
        self.questionBox = QTextEdit()
        
        self.clear_button = QPushButton('X', self)
        self.clear_button.setFixedSize(20, 20)
        self.clear_button.setToolTip("Clear Queries")
        self.submitButton = QPushButton("submit")
        self.clear_button.setFlat(True)
        self.clear_button.clicked.connect(self.clear_text)
        
        button_layout = QHBoxLayout()

        button_layout.addWidget(self.labelDesignation)
        button_layout.addWidget(self.clear_button)
        button_layout.setSpacing(130)
        button_layout.setAlignment(Qt.AlignTop | Qt.AlignRight)
        self.layout.addLayout(button_layout)
        self.layout.addWidget(self.questionBox)
        #self.layout.addWidget(self.clear_button)
        
        self.submitButton.clicked.connect(self.evaluate_resume)
        self.layout.addWidget(self.submitButton)        

        self.labelResult = QLabel("Query Results:")
        self.responseBox = QTextEdit()
        self.setFixedSize(400, 700)
        self.responseBox.setReadOnly(True)
        self.layout.addWidget(self.labelResult)
        self.layout.addWidget(self.responseBox)

        self.setLayout(self.layout)

    def clear_text(self):
        self.questionBox.clear()
        
    def evaluate_resume(self):
        resume = self.resumeBox.toPlainText().strip()
        question = self.questionBox.toPlainText().strip()
        
        if resume == '' or question == '':
            self.responseBox.setText("Please Enter Resume and your query!")
            return
        
        prompt = """
        "You are a Resume Analyser chatbot,
        Your expertise is exclusively in providing detail about anything related to the input resume.
        This includes years of experience , how many skills candidate possess , designation, email and contact number,
        Given the input designation please identify the current market requirements and skills needed for this role. Then,
        compare these market requirements with the skills listed in the resume,
        Provide a detailed comparison highlighting the skills that match the market requirements and those that are missing as well as check If given designation is mentioned in resume."
        Certifications, If input skills are present or not present in input resume,
        breakdown answers into points for better readability"
        Question: {question}
        Answer: 
        """
        
        user_input = f"Resume:\n{resume} "+prompt
        resume_prompt_template = PromptTemplate(
            template=user_input,
            input_variables=["question"]
            
        )
        self.langchain_openai_response(resume_prompt_template, question)
        #response = self.get_openai_response(messages)
        #print(response)
        #self.responseBox.setText(response)

    def langchain_openai_response(self, prompt_template,question):
        llm = ChatOpenAI(model_name="gpt-3.5-turbo", openai_api_key="openapi-key")

        llm_chain = prompt_template | llm | StrOutputParser()
        result = llm_chain.invoke({'question':question})
        self.responseBox.setText(result)
             
    def get_openai_response(self,messages):
        try:
            response = client.chat.completions.create(model="gpt-4",
            messages=messages,
            max_tokens=150)
            return response.choices[0].message.content.strip()
        except Exception as err:
            return f"An error occured {str(err)}"
        
    def attach_resume(self):
        options = QFileDialog.Options()
        filename, _ = QFileDialog.getOpenFileName(self, "Open Resume File", "All Files (*);;Text Files (*.txt);;PDF Files (*.pdf);;Word Files (*.docx)", options=options)
        if filename:
            try:
                if filename.endswith(".pdf"):
                    resume_text = self.extract_text_from_pdf(filename)
                elif filename.endswith(".docx"):
                    resume_text = self.extract_text_from_docx(filename)
                else:
                    with open(filename, 'r') as fp:
                        resume_text = fp.read()
                self.resumeBox.setText(resume_text)
            except Exception as e:
                return f"An error occured while attaching resume {str(e)}"

    def extract_text_from_pdf(self, filename):
        try:
            document = fitz.open(filename)
            text = ""
            for page in document:
                text += page.get_text()
            return text
        except Exception as e:
            return f"Failed to read pdf resume{str(e)}"

    def extract_text_from_docx(self, filename):
        try:
            doc = docx.Document(filename)
            text = ""
            for para in doc.paragraphs:
                text += para.text + '\n'
            return text
        except Exception as e:
            return f"An error occured while reading docx resume{str(e)}"

if __name__ == "__main__":
    app = QApplication(sys.argv)
    chatbot = ChatBot()
    chatbot.show()
    sys.exit(app.exec_())
