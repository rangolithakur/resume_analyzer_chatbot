import sys
import fitz
import docx
from openai import OpenAI

client = OpenAI(api_key="add-your-api-key")
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QTextEdit, QPushButton, QLabel, QFileDialog

#setting up open ai key 

class ChatBot(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Resume Evaluation Chatbot")
        self.layout = QVBoxLayout()
        print("111111")
        #ToDo allow user to attach the resume , analyse resume and match
        self.label = QLabel("Attach the resume:")
        self.layout.addWidget(self.label)
        
        self.attachButton = QPushButton("Attach Resume")
        self.attachButton.clicked.connect(self.attach_resume)
        self.layout.addWidget(self.attachButton)

        self.resumeBox = QTextEdit()
        self.layout.addWidget(self.resumeBox)

        self.labelDesignation = QLabel("Enter the designation:")
        self.layout.addWidget(self.labelDesignation)
        
        self.designationBox = QTextEdit()
        self.layout.addWidget(self.designationBox)

        self.labelSkills = QLabel('Enter the skills to verify')
        self.labelSkills.setToolTip("Comma separated or Space separated.")
        self.layout.addWidget(self.labelSkills)
        self.skillsBox = QTextEdit()
        self.layout.addWidget(self.skillsBox)

        self.submitButton = QPushButton("submit")
        self.submitButton.clicked.connect(self.evaluate_resume)
        self.layout.addWidget(self.submitButton)        

        self.responseBox = QTextEdit()
        self.responseBox.setReadOnly(True)
        self.layout.addWidget(self.responseBox)

        self.setLayout(self.layout)

    def evaluate_resume(self):
        resume = self.resumeBox.toPlainText().strip()
        designation = self.designationBox.toPlainText().strip()
        skills_input = self.skillsBox.toPlainText().strip()
        
        if resume == '' or designation == '':
            self.responseBox.setText("Please Enter Resume and Designation")
            return
        
        if skills_input:
            # Parse skills input
            skills = self.parse_skills(skills_input)
            user_input = f"Resume:\n{resume}\n\nDesignation:\n{designation}\n\nSkills:\n{', '.join(skills)}"
            messages = [
                {"role":"system", "content":"You are a helpful assstant."},
                {"role":"user", "content":f"Evaluate if the following resume is fit for the given designation and matches the required skills:\n\n{user_input}\n\nProvide your evaluation:"}
            ]

        else:
            user_input = f"Resume:\n{resume}\n\nDesignation:\n{designation}\n"
            messages = [
                {"role":"system", "content":"You are a helpful assstant."},
                {"role":"user", "content":f"Evaluate if the following resume is good fit for the given designation:\n\n{user_input}\n\n Provide your evaluation:"}]


        response = self.get_openai_response(messages)
        print(response)
        self.responseBox.setText(response)

    def get_openai_response(self,messages):
        try:
            #prompt = "Evaluate if the following resume is good fit for the given designation:\n\n{user_input}\n\n Provide your evaluation:"
            
            response = client.chat.completions.create(model="gpt-4",
            messages=messages,
            max_tokens=150)
            return response.choices[0].message.content.strip()
        except Exception as err:
            print(err)
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

    def parse_skills(self, skills_input):
        # Split by commas and spaces, and filter out empty strings
        skills = [skill.strip() for skill in skills_input.replace(',', ' ').split() if skill.strip()]
        return skills

if __name__ == "__main__":
    app = QApplication(sys.argv)
    chatbot = ChatBot()
    chatbot.show()
    sys.exit(app.exec_())