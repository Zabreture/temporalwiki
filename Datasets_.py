from torch.utils.data import Dataset, IterableDataset
import pandas as pd
import json
import random
import os

class CustomDataset(Dataset):
    def __init__(self, tokenizer, type_path, input_length, output_length, args, length=None):
        self.args = args
        self.tokenizer = tokenizer
        self.type_path = type_path
        self.dataset_version = self.args.dataset_version
        dataset_v = ['small', 'full']   
            
        if not self.dataset_version in dataset_v:
            raise Exception(f'Provided the correct dataset version among {dataset_v}')

        # dataset for continual training
        if self.type_path=='train':
            raise Exception('we do not use training set for CustomDataset class')
        elif type_path =='pretrain':
            total_line = 4378268
            skip = sorted(random.sample(range(1,total_line+1),total_line-length))
            self.dataset = pd.read_csv('data/Wikipedia_Full/wikipedia_08_gpt2/part1.csv', usecols=['text'], skiprows=skip)
        else:
            dataset_prefix = 'data/new_moee_validation/'
            openwebtext = pd.read_csv(f'{dataset_prefix}openwebtext.csv')
            kilt_wikipedia = pd.read_csv(f'{dataset_prefix}kilt_wikipedia.csv')
            lambada = pd.read_csv(f'{dataset_prefix}lambada.csv')
            lama = pd.read_csv(f'{dataset_prefix}trex_lama.csv')
            if self.args.dataset=='data/new_data/final_twiki_corpus_1024/08' or self.args.dataset=='data/new_data/final_twiki_corpus_1024/09':
                unchanged = pd.read_csv('data/new_data/tempate_mapped/0801-0901_unchanged_final_template2.csv')
                changed = pd.read_csv('data/new_data/tempate_mapped/0801-0901_changed_final_template2.csv')
            else:
                raise Exception(f'the following training data {self.args.dataset} does not have a designated validation dataset')
            self.dataset = pd.concat([openwebtext, kilt_wikipedia, lambada, lama, unchanged, changed])

        print(f'Length of dataset retrieving is.. {len(self.dataset)}')
        self.input_length = input_length
        self.output_length = output_length

    def __len__(self):
        return len(self.dataset)
  
    def input_to_target(self, input):
        input_s = input.split(' ')
        input = " ".join(input_s[:len(input_s)-1])
        target = " " + input_s[len(input_s)-1]
        return input, target

    def convert_to_features(self, example_batch, index):
        if index < 19200:
            input_, target_ = example_batch['text'], example_batch['text']       
        elif index < 24192:
            input_, target_ = self.input_to_target(example_batch['text'])
        elif index < 52928:
            input_ = example_batch['input']
            input_ = input_[:-1]
            target_ = " " + example_batch['output']
        else:
            input_ = example_batch['input']
            target_ = " " + example_batch['target']
        task = example_batch['task']
        source = self.tokenizer.batch_encode_plus([str(input_)], max_length=self.input_length, padding='max_length', truncation=True, return_tensors="pt")
        targets = self.tokenizer.batch_encode_plus([str(target_)], max_length=self.output_length, padding='max_length', truncation=True, return_tensors="pt")  
        return source, targets, task
        
    def __getitem__(self, index):
        source, targets, task = self.convert_to_features(self.dataset.iloc[index], index=index) 
        
        source_ids = source["input_ids"].squeeze()
        target_ids = targets["input_ids"].squeeze()

        src_mask    = source["attention_mask"].squeeze()
        target_mask = targets["attention_mask"].squeeze()

        return {"source_ids": source_ids, "source_mask": src_mask, "target_ids": target_ids, "target_mask": target_mask, "task": task}
    
class Pretrain_Chunks(Dataset):
    def __init__(self, dataset_name, tokenizer, input_length, output_length, args):
        self.args = args
        self.tokenizer = tokenizer
        self.input_length = input_length
        self.output_length = output_length
        self.dataset = pd.read_csv(dataset_name)
        print(f'Getting dataset {dataset_name} with length {len(self.dataset)}')
        
    def __len__(self):
        return len(self.dataset)

    def convert_to_features(self, example_batch, index=None):
        # continual pretraining
        if 'gpt2' in self.args.model_name_or_path:
            input_ = example_batch['text']
            target_ = example_batch['text']
        else:
            input_ = example_batch['input']
            target_ = example_batch['output']
        source = self.tokenizer.batch_encode_plus([str(input_)], max_length=self.input_length,
                                                    padding='max_length', truncation=True, return_tensors="pt")
        targets = self.tokenizer.batch_encode_plus([str(target_)], max_length=self.output_length,
                                                    padding='max_length', truncation=True, return_tensors="pt")                          
        return source, targets
    
    def __getitem__(self, index):
        source, targets = self.convert_to_features(self.dataset.iloc[index])
        
        source_ids = source["input_ids"].squeeze()
        target_ids = targets["input_ids"].squeeze()

        src_mask    = source["attention_mask"].squeeze()
        target_mask = targets["attention_mask"].squeeze()
        return {"source_ids": source_ids, "source_mask": src_mask, "target_ids": target_ids, "target_mask": target_mask}