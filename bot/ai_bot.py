import os

from decouple import config

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_groq import ChatGroq

os.environ['GROQ_API_KEY']=config('GROQ_API_KEY')

class AIBot:

    def __init__(self):
        self.__chat = ChatGroq(
            model='llama-3.3-70b-versatile',
            )
      
    def invoke(self, question):
        prompt = PromptTemplate(
            input_variables=['texto'],
            template= (
                """
                Responda de forma gentil {texto}
                
                """               
                )
        
        )
        
        chain = prompt | self.__chat| StrOutputParser()
        
        try:
            response = chain.invoke({
                
                'texto': question
                
                })
            return response
        
        except Exception as e:
            print(f"Erro na invocação: {e}")
            return None

