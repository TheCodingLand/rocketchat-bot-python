from simpletransformers.question_answering import QuestionAnsweringModel
QuestionAnsweringModel('distilbert', 'distilbert-base-uncased-distilled-squad',use_cuda=False, args={'reprocess_input_data': True, 'overwrite_output_dir': True})
