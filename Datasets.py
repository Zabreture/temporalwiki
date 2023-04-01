from torch.utils.data import Dataset
import pandas as pd
import random


class CustomDataset(Dataset):
    def __init__(self, tokenizer, type_path, input_length, output_length, args, length=None, lama_type=None):
        self.args = args
        self.tokenizer = tokenizer
        self.type_path = type_path
        self.dataset_version = self.args.dataset_version

        self.lama_type = lama_type  # for validation, it decided 'unchanged' or 'changed'
        dataset_v = ['small', 'full']

        if self.dataset_version not in dataset_v:
            raise Exception(f'Provided the correct dataset version among {dataset_v}')

        # dataset for continual training
        if self.type_path == 'train':
            if self.args.mode == 'finetune':
                if 'unchanged' in self.args.dataset:
                    self.dataset = pd.read_csv('data/evaluation/lighttuning/lighttuning_unchanged_500.csv')
                else:
                    self.dataset = pd.read_csv('data/evaluation/lighttuning/lighttuning_changed_500.csv')
                # self.dataset = pd.read_csv('data/TWiki_Probes/lighttuning/'+self.args.dataset+'.csv')
            elif self.args.dataset == 'wikipedia_0809':
                self.dataset = pd.read_csv('data/TWiki_Diffsets/wikipedia_0809_subset.csv')
            elif self.args.dataset == 'wikipedia_0809_gpt2':
                self.dataset = pd.read_csv('data/TWiki_Diffsets/wikipedia_0809_gpt2.csv')
            elif self.args.dataset == 'wikipedia_0910':
                self.dataset = pd.read_csv('data/TWiki_Diffsets/wikipedia_0910_subset.csv')
            elif self.args.dataset == 'wikipedia_0910_gpt2':
                self.dataset = pd.read_csv('data/TWiki_Diffsets/wikipedia_0910_gpt2.csv')
            elif self.args.dataset == 'wikipedia_1011':
                self.dataset = pd.read_csv('data/TWiki_Diffsets/wikipedia_1011_subset.csv')
            elif self.args.dataset == 'wikipedia_1011_gpt2':
                self.dataset = pd.read_csv('data/TWiki_Diffsets/wikipedia_1011_gpt2.csv')
            elif self.args.dataset == 'wikipedia_1112_gpt2':
                self.dataset = pd.read_csv('data/TWiki_Diffsets/wikipedia_1112_gpt2.csv')
            else:
                raise Exception('The given dataset does not exist in data directory.')
        elif type_path == 'pretrain':
            total_line = 4378268
            skip = sorted(random.sample(range(1, total_line + 1), total_line - length))
            self.dataset = pd.read_csv('data/Wikipedia_Full/wikipedia_08_gpt2/part1.csv', usecols=['text'],
                                       skiprows=skip)
        else:
            # evaluation dataset
            if self.args.check_validation_only:
                if self.args.mode == 'evaluate_ppl_corpus':
                    self.dataset = pd.read_csv('data/perplexity/' + self.args.dataset + '.csv')
                else:
                    if self.args.dataset == 'IL':
                        self.dataset = pd.read_csv('data/IL.csv')
                    else:
                        self.dataset = pd.read_csv('data/twiki_probes/' + self.args.dataset + '.csv')
            # validation dataset
            elif self.args.mode == 'finetune':
                self.dataset = pd.read_csv('data/evaluation/final/' + self.args.dataset + '.csv')
            elif self.args.dataset == 'IL':
                self.dataset = pd.read_csv('data/TWiki_Probes/IL.csv')
            elif self.args.dataset == 'data/wikipedia_09' or self.args.dataset == 'wikipedia_0809' or \
                    self.args.dataset == 'data/wikipedia_09_gpt2' or self.args.dataset == 'wikipedia_0809_gpt2':
                if self.lama_type == 'unchanged':
                    self.dataset = pd.read_csv('data/twiki_probes/0801-0901_unchanged.csv')
                elif self.lama_type == 'changed':
                    self.dataset = pd.read_csv('data/twiki_probes/0801-0901_changed.csv')
                else:
                    self.dataset = pd.read_csv('data/TWiki_Probes/IL.csv')
            elif self.args.dataset == 'data/wikipedia_10_gpt2' or self.args.dataset == 'data/wikipedia_10' or \
                    self.args.dataset == 'wikipedia_0910' or self.args.dataset == 'wikipedia_0910_gpt2':
                if self.lama_type == 'unchanged':
                    self.dataset = pd.read_csv('data/twiki_probes/0901-1001_unchanged.csv')
                elif self.lama_type == 'changed':
                    self.dataset = pd.read_csv('data/twiki_probes/0901-1001_changed.csv')
                else:
                    self.dataset = pd.read_csv('data/TWiki_Probes/IL.csv')
            elif self.args.dataset == 'data/wikipedia_11_gpt2' or self.args.dataset == 'data/wikipedia_11' or \
                    self.args.dataset == 'wikipedia_1011' or self.args.dataset == 'wikipedia_1011_gpt2':
                if self.lama_type == 'unchanged':
                    self.dataset = pd.read_csv('data/twiki_probes/1001-1101_unchanged.csv')
                elif self.lama_type == 'changed':
                    self.dataset = pd.read_csv('data/twiki_probes/1001-1101_changed.csv')
                else:
                    self.dataset = pd.read_csv('data/TWiki_Probes/IL.csv')
            elif self.args.dataset == 'data/wikipedia_12_gpt2' or self.args.dataset == 'data/wikipedia_12' or \
                    self.args.dataset == 'wikipedia_1112' or self.args.dataset == 'wikipedia_1112_gpt2':
                if self.lama_type == 'unchanged':
                    self.dataset = pd.read_csv('data/twiki_probes/1101-1201_unchanged.csv')
                elif self.lama_type == 'changed':
                    self.dataset = pd.read_csv('data/twiki_probes/1101-1201_changed.csv')
                else:
                    self.dataset = pd.read_csv('data/TWiki_Probes/IL.csv')
            else:
                self.dataset = pd.read_csv('data/TWiki_Probes/IL.csv')

        print(f'Length of dataset retrieving is.. {len(self.dataset)}')
        self.input_length = input_length
        self.output_length = output_length

    def __len__(self):
        return len(self.dataset)

    def convert_to_features(self, example_batch):
        # continual pretraining
        input_nonprompt = None
        label_ = None
        if self.type_path == 'validation':
            if self.args.mode == 'evaluate_ppl_corpus':
                input_ = example_batch['text']
                target_ = example_batch['text']
            else:
                s = example_batch['subject']
                r = example_batch['relation']
                o = example_batch['object']
                if self.args.mode == 'evaluate_ppl':
                    input_ = s + ' ' + r + ' ' + o
                    input_nonprompt = ' ' + o
                    target_ = s + ' ' + r + ' ' + o
                elif self.args.mode == 'evaluate':
                    input_ = s + ' ' + r
                    target_ = o
                elif self.args.mode == 'finetune':
                    label_ = s + ' ' + r + ' ' + o
                    input_ = s + ' ' + r
                    target_ = o
                else:
                    target_ = s + ' ' + r + ' ' + o
                    input_ = s + ' ' + r + ' ' + o
                    input_nonprompt = ' ' + o
        else:
            if self.args.mode == 'finetune':
                s = example_batch['subject']
                r = example_batch['relation']
                o = example_batch['object']
                input_ = s + ' ' + r + ' ' + o
                target_ = s + ' ' + r + ' ' + o
                label_ = s + ' ' + r + ' ' + o
            else:
                input_ = example_batch['text']
                target_ = example_batch['text']
        source = self.tokenizer.batch_encode_plus([str(input_)], max_length=self.input_length,
                                                  padding='max_length', truncation=True, return_tensors="pt")
        targets = self.tokenizer.batch_encode_plus([str(target_)], max_length=self.output_length,
                                                   padding='max_length', truncation=True, return_tensors="pt")
        if input_nonprompt is not None:
            input_nonprompt = self.tokenizer.batch_encode_plus([str(input_nonprompt)], max_length=self.input_length,
                                                               padding='max_length', truncation=True,
                                                               return_tensors="pt")
        if label_ is not None:
            label_ = self.tokenizer.batch_encode_plus([str(label_)], max_length=self.input_length,
                                                      padding='max_length', truncation=True, return_tensors="pt")

        return source, targets, input_nonprompt, label_

    def __getitem__(self, index):
        source, targets, input_nonprompt, label = self.convert_to_features(self.dataset.iloc[index])

        source_ids = source["input_ids"].squeeze()
        target_ids = targets["input_ids"].squeeze()

        src_mask = source["attention_mask"].squeeze()
        target_mask = targets["attention_mask"].squeeze()

        if input_nonprompt is not None:
            source_nonprompt_ids = input_nonprompt["input_ids"].squeeze()
            source_nonprompt_mask = input_nonprompt["attention_mask"].squeeze()
        else:
            source_nonprompt_mask = -1
            source_nonprompt_ids = -1

        if label is not None:
            label_ids = label["input_ids"].squeeze()
            label_mask = label["attention_mask"].squeeze()
        else:
            label_ids = -1
            label_mask = -1

        return {"source_ids": source_ids, "source_mask": src_mask, "target_ids": target_ids, "target_mask": target_mask,
                "source_nonprompt_ids": source_nonprompt_ids, "source_nonprompt_mask": source_nonprompt_mask,
                "label_ids": label_ids, "label_mask": label_mask}


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

    def convert_to_features(self, example_batch):
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

        src_mask = source["attention_mask"].squeeze()
        target_mask = targets["attention_mask"].squeeze()
        return {"source_ids": source_ids, "source_mask": src_mask, "target_ids": target_ids, "target_mask": target_mask}
