import torch
import torch.nn.functional as F
from transformers import BertTokenizer, BertModel
from transformers import RobertaTokenizer, RobertaConfig, RobertaModel, get_linear_schedule_with_warmup
import json
import numpy as np
import argparse

types = ['Shape mismatch', 'Numeric error', 'Type mismatch', 'API misuse', 'Non-General']
type2idx = {tp: idx for idx, tp in enumerate(types)}
idx2type = {idx: tp for tp, idx in type2idx.items()}


def load_data(path):
    dataset = []
    with open(path, 'r', encoding='utf-8') as fin:
        for line in fin:
            if line.strip() == '':
                continue
            js = json.loads(line.strip())
            dataset.append(js)
    return dataset


def get_batch(dataset, batch_size, shuffle=False):
    if shuffle:
        np.random.shuffle(dataset)
    nb_batch = (len(dataset) + batch_size - 1) // batch_size
    for i in range(nb_batch):
        batch_data = dataset[i * batch_size: (i + 1) * batch_size]
        yield batch_data


def batch_variable(batch_data, bert_tokenizer):
    batch_pairs = [(inst['Fix'], inst['Buggy']) for inst in batch_data]
    input_tensors = bert_tokenizer(batch_pairs, padding=True, truncation=True, max_length=512, return_tensors="pt")
    type_tensors = torch.tensor([type2idx[inst['Type']] for inst in batch_data], dtype=torch.long)
    return input_tensors, type_tensors


def batch_variable2(batch_data, bert_tokenizer):
    batch_fix = [inst['Fix'] for inst in batch_data]
    batch_bug = [inst['Buggy'] for inst in batch_data]
    input_tensors1 = bert_tokenizer(batch_fix, padding=True, truncation=True, max_length=512, return_tensors="pt")
    input_tensors2 = bert_tokenizer(batch_bug, padding=True, truncation=True, max_length=512, return_tensors="pt")
    type_tensors = torch.tensor([type2idx[inst['Type']] for inst in batch_data], dtype=torch.long)
    return input_tensors1, input_tensors2, type_tensors


def build_model_tokenizer(bert_path):
    # bert_config = RobertaConfig.from_pretrained(bert_path)
    bert_tokenizer = RobertaTokenizer.from_pretrained(bert_path)
    bert_model = RobertaModel.from_pretrained(bert_path)
    # bert_tokenizer = BertTokenizer.from_pretrained(bert_path)
    # bert_model = BertModel.from_pretrained(bert_path)
    return bert_model, bert_tokenizer


class DualCodeModel(torch.nn.Module):
    def __init__(self, bert_model, bert_dim, type_num, dropout=0.2):
        super(DualCodeModel, self).__init__()
        self.bert = bert_model
        self.dropout = dropout
        self.fc = torch.nn.Linear(bert_dim, type_num)

    def forward(self, inp1, inp2):
        bert_out1 = self.bert(**inp1, return_dict=False)[0]
        bert_out2 = self.bert(**inp2, return_dict=False)[0]
        bert_out1 = F.dropout(bert_out1, p=self.dropout, training=self.training)
        bert_out2 = F.dropout(bert_out2, p=self.dropout, training=self.training)
        cls_r1, cls_r2 = bert_out1[:, 0, :], bert_out2[:, 0, :]
        out = (cls_r1 - cls_r2) ** 2
        # out = torch.cat((cls_r1, cls_r2), dim=-1)
        # out = cls_r1 * cls_r2
        # out = torch.cat(((cls_r1 - cls_r2)**2, cls_r1 * cls_r2), dim=-1)
        # out = torch.cat(((cls_r1 - cls_r2)**2, cls_r1, cls_r2), dim=-1)
        # out = torch.cat((cls_r1 * cls_r2, cls_r1, cls_r2), dim=-1)
        return self.fc(out)


class CrossCodeModel(torch.nn.Module):
    def __init__(self, bert_model, bert_dim, type_num, dropout=0.2):
        super(CrossCodeModel, self).__init__()
        self.dropout = dropout
        self.bert = bert_model
        self.fc = torch.nn.Linear(bert_dim, type_num)

    def forward(self, inp):
        bert_out = self.bert(**inp, return_dict=False)[0]
        bert_out = F.dropout(bert_out, p=self.dropout, training=self.training)
        return self.fc(bert_out[:, 0, :])


def evaluate(test_data, model, tokenizer, args):
    model.eval()
    acc_num, total_num = 0, 0
    jsl_file = open('test.jsonl', 'w', encoding='utf-8')
    with torch.no_grad():
        for batch in get_batch(test_data, args.batch_size):
            # input_tensors, type_tensors = batch_variable(batch, tokenizer)
            # input_tensors = input_tensors.to(args.device)
            input_tensors1, input_tensors2, type_tensors = batch_variable2(batch, tokenizer)
            input_tensors1 = input_tensors1.to(args.device)
            input_tensors2 = input_tensors2.to(args.device)
            type_tensors = type_tensors.to(args.device)
            # bert_out = model(input_tensors)
            bert_out = model(input_tensors1, input_tensors2)
            pred = bert_out.detach().argmax(dim=-1)
            acc_num += (pred == type_tensors).sum().item()
            total_num += len(pred)

            for i, inst in enumerate(batch):
                inst.update({'PredType': idx2type[pred.data.tolist()[i]]})
                jstr = json.dumps(inst)
                jsl_file.write(jstr + '\n')

    acc = acc_num / total_num
    jsl_file.close()
    return acc


def train(args):
    train_set = load_data(args.train_file)
    dev_set = load_data(args.dev_file)
    test_set = load_data(args.test_file)
    print('train size: %d, dev size: %d, test size: %d' % (len(train_set), len(dev_set), len(test_set)))
    bert_model, bert_tokenizer = build_model_tokenizer(args.bert_path)
    # model = CrossCodeModel(bert_model, args.bert_dim, args.type_num, args.dropout).to(args.device)
    model = DualCodeModel(bert_model, args.bert_dim, args.type_num, args.dropout).to(args.device)
    print(model)
    print("Total Parameters: %d M" % (sum([p.nelement() for p in model.parameters()]) // 10 ** 6))

    no_decay = ["bias", "LayerNorm.weight"]
    optimizer_grouped_parameters = [{
        "params": [p for n, p in model.named_parameters() if not any(nd in n for nd in no_decay)],
        "weight_decay": 0.01},
        {"params": [p for n, p in model.named_parameters() if any(nd in n for nd in no_decay)],
         "weight_decay": 0.0},

        # {'params': [p for n, p in model.fc.named_parameters() if not any(nd in n for nd in no_decay)],
        # 'weight_decay': 1e-4, 'lr': 1e-4},
        # {'params': [p for n, p in model.fc.named_parameters() if any(nd in n for nd in no_decay)],
        # 'weight_decay': 0.0, 'lr': 1e-4}
        # {'params': [p for n, p in model.fc.named_parameters()],
        # 'weight_decay': 1e-4, 'lr': 2e-4}
    ]
    optimizer = torch.optim.AdamW(optimizer_grouped_parameters, lr=args.lr, eps=1e-8)

    t_total = len(train_set) // args.batch_size * args.epoch
    scheduler = get_linear_schedule_with_warmup(optimizer, num_warmup_steps=t_total // 10, num_training_steps=t_total)

    best_dev_acc, best_test_acc = 0, 0
    patient = 0
    for ep in range(args.epoch):
        train_loss = 0
        model.train()
        for batch in get_batch(train_set, args.batch_size, shuffle=True):
            # input_tensors, type_tensors = batch_variable(batch, bert_tokenizer)
            # input_tensors = input_tensors.to(args.device)
            input_tensors1, input_tensors2, type_tensors = batch_variable2(batch, bert_tokenizer)
            input_tensors1 = input_tensors1.to(args.device)
            input_tensors2 = input_tensors2.to(args.device)
            type_tensors = type_tensors.to(args.device)
            # bert_out = model(input_tensors)
            bert_out = model(input_tensors1, input_tensors2)
            loss = F.cross_entropy(bert_out, type_tensors)
            loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
            optimizer.step()
            scheduler.step()
            model.zero_grad()
            loss_val = loss.data.item()
            train_loss += loss_val

        dev_acc = evaluate(dev_set, model, bert_tokenizer, args)
        if dev_acc > best_dev_acc:
            patient = 0
            best_dev_acc = dev_acc
            test_acc = evaluate(test_set, model, bert_tokenizer, args)
            if test_acc > best_test_acc:
                best_test_acc = test_acc
                # save model
        else:
            patient += 1

        if patient >= args.patient:
            break

        print('Epoch [%d], patient: %d, training loss: %.4f, dev_acc: %s, test_acc: %s' %
              (ep + 1, patient, train_loss, dev_acc, test_acc))

    print('Final Dev Acc: %s, Test Acc: %s' % (best_dev_acc, best_test_acc))


def set_seeds(seed=1349):
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.cuda.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)
    torch.backends.cudnn.deterministic = True


def run():
    set_seeds(3347)
    parse = argparse.ArgumentParser('Coding...')
    parse.add_argument('--cuda', type=int, default=-1, help='cuda device, default cpu')
    parse.add_argument('-bs', '--batch_size', type=int, default=8, help='batch size')
    parse.add_argument('-ep', '--epoch', type=int, default=10, help='training epoch')
    parse.add_argument('--bert_dim', type=int, default=768, help='bert embedding size')
    parse.add_argument('--type_num', type=int, default=5, help='number of buggy type')
    parse.add_argument('--patient', type=int, default=3, help='early stopping')
    parse.add_argument('-lr', '--lr', type=float, default=2e-5, help='learning rate')
    parse.add_argument('--dropout', type=float, default=0.2, help='learning rate')
    parse.add_argument('-ml', '--max_len', type=int, default=512, help='max seq len')
    parse.add_argument('--train_file', type=str, default='code_data/train_data.jsonl', help='train data file')
    parse.add_argument('--dev_file', type=str, default='code_data/val_data.jsonl', help='dev data file')
    parse.add_argument('--test_file', type=str, default='code_data/test_data.jsonl', help='test data file')
    parse.add_argument('--bert_path', type=str, default='codeberta/', help='bert path')
    args = parse.parse_args()
    args.device = torch.device('cuda', args.cuda) if torch.cuda.is_available() and args.cuda >= 0 else torch.device(
        'cpu')
    print(args)
    train(args)


# nohup python train.py --cuda 6 --batch_size 8 -lr 2e-5 --bert_path codeberta &> dual_codeberta.log &
run()

