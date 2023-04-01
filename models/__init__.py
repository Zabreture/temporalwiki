from models.GPT2_Model import GPT2 as GPT2_Model

def load_model(type: str):
    if type=='GPT2':
        return GPT2_Model
    else:
        raise Exception('Select the correct model type. Currently supporting only T5 and GPT2.')