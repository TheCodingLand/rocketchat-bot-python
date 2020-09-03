from simpletransformers.question_answering import QuestionAnsweringModel
import json
import os



class QA(object):
    predictions=[]
    def __init__(self):
        self.model = QuestionAnsweringModel('bert','distilbert-base-uncased-distilled-squad',use_cuda=False, args={'reprocess_input_data': True, 'overwrite_output_dir': True})
    
    def predict(self, context, question):
        
        
        to_predict = [ {"context": context, 'qas': [{'question': question, 'id': '0'}]}]
        predictions = self.model.predict(to_predict)


        return predictions