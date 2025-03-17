import copy
import sys
import time
import numpy as np
from torch import nn
import torch
from torch.nn import Conv1d, MaxPool1d, Flatten, Linear, Sequential
from torch.utils.data import DataLoader
from torch.utils.data import dataset
from pycut.func import getTestAllMissing_index,getWindowMissing_index
import torch.nn.functional as F
import torch.optim as optim

#Definition of the network
class Autoencoder(nn.Module):
    def __init__(self,drop_perc,filter_size,stride,windows):
        super(Autoencoder, self).__init__()
        self.drop_perc = drop_perc
        self.filter_size = filter_size
        self.padding=int(self.filter_size/2)
        self.stride = stride
        # 编码器部分
        self.encode1 = Conv1d(3, 32, kernel_size=self.filter_size, stride=self.stride, padding=self.padding)  # 输入4通道，输出128通道，25x4卷积，步长为1，padding为filter_size的一半向下取整
        self.encode2 = Conv1d(32, 64, kernel_size=self.filter_size, stride=self.stride, padding=self.padding)
        self.encode3 = Conv1d(64, 64, kernel_size=self.filter_size, stride=self.stride, padding=self.padding)
        self.latent = Conv1d(64, 128, kernel_size=self.filter_size, stride=self.stride, padding=self.padding)
        self.decode1 = nn.ConvTranspose1d(128, 64, kernel_size=self.filter_size, stride=self.stride, padding=self.padding)
        self.decode2 = nn.ConvTranspose1d(64, 64, kernel_size=self.filter_size, stride=self.stride, padding=self.padding)
        self.decode3 = nn.ConvTranspose1d(64, 32, kernel_size=self.filter_size, stride=self.stride, padding=self.padding)
        self.output_layer = Conv1d(32, 3, kernel_size=self.filter_size, stride=self.stride, padding=self.padding)
        self.drop = nn.Dropout(self.drop_perc)
        self.mp = nn.MaxPool1d(kernel_size=2, stride=2, return_indices=True)
        self.up = nn.MaxUnpool1d(kernel_size=2, stride=2)

        self.bn1a = nn.LayerNorm([32, int(windows)])
        self.bn2a = nn.LayerNorm([64, int(windows / 2)])
        self.bn2c = nn.LayerNorm([64, int(windows / 4)])
        self.bn2d = nn.LayerNorm([64, int(windows / 8)])
        self.bn2f = nn.LayerNorm([64, int(windows / 2)])
        self.bn3 = nn.LayerNorm([128, int(windows / 8)])
        self.bn1c = nn.LayerNorm([32, int(windows)])
        self.relu = nn.ReLU(inplace=True)

    def forward(self, x):
        out = self.encode1(x)
        out = self.relu(out)
        out = self.bn1a(out)
        identity1 = out
        out, index1 = self.mp(out)
        out = self.drop(out)
        out = self.encode2(out)
        out = self.relu(out)
        out = self.bn2a(out)
        identity2 = out
        out, index2 = self.mp(out)
        out = self.drop(out)
        out = self.encode3(out)
        out = self.relu(out)
        out = self.bn2c(out)
        out, index3 = self.mp(out)
        out = self.drop(out)
        out = self.latent(out)
        out = self.bn3(out)
        out = self.decode1(out)
        out = self.relu(out)
        out = self.bn2d(out)
        out = self.up(out, index3)
        out = self.drop(out)
        out = self.decode2(out)
        out = self.relu(out)
        out = self.up(out, index2)
        out = self.bn2f(out)
        out += identity2
        out = self.drop(out)
        out = self.decode3(out)
        out = self.relu(out)
        out = self.up(out, index1)
        out = self.bn1c(out)
        out += identity1
        out = self.drop(out)
        out = self.output_layer(out)
        return out

#The class of dataset
class MyDataSet(dataset.Dataset):
    def __init__(self,data,label):
        super(MyDataSet, self).__init__()
        self.data = data
        self.label = label
        self.length = data.shape[0]
    def __getitem__(self, mask):
        return self.data[mask],self.label[mask]
    def __len__(self):
        return self.length

#The training function
def train_func(loop_num,epochs,epoch_num_all,epochNumTemp,window_size,num,TestAllMissing_index,trainyin_x,testyin_x,train_corrupt,batch_size,drop_perc,filter_size,stride,device,learning_rate,all_unit2,predictAll,end):
    for k in range(loop_num):
                global nowEpochNum
                nowEpochNum =epochNumTemp + k * epochs
                start = end
                if (start + window_size <= num):
                    trueStart = start
                    end = window_size + start
                    trueEnd = window_size + trueStart
                if (start + window_size > num):
                    trueStart = num - window_size
                    end = num
                    trueEnd = end
                testMissing_index_result = getWindowMissing_index(TestAllMissing_index,start,trueStart,end,window_size)
                testMissing_index = testMissing_index_result[0]
                del testMissing_index_result

                train_sec = trainyin_x[:, trueStart:trueEnd]
                train_sec = torch.tensor(train_sec).to(torch.int64)
                train_onehot = F.one_hot(train_sec, num_classes=3)
                train_corrupt_sec = train_corrupt[:, trueStart:trueEnd]
                train_corrupt_sec = torch.tensor(train_corrupt_sec).to(torch.int64)
                missing_pos = train_corrupt_sec == 0
                train_corrupt_sec[missing_pos] = 2
                train_corrupt_sec = train_corrupt_sec - 1
                train_corrupt_onehot = F.one_hot(train_corrupt_sec, num_classes=3)
                train_corrupt_onehot[missing_pos, :] = 0
                train_X = train_onehot
                train_X = torch.from_numpy(train_X.numpy().transpose(0, 2, 1))
                train_corrupt_X = train_corrupt_onehot
                train_corrupt_X = torch.from_numpy(train_corrupt_X.numpy().transpose(0, 2, 1))
                train_set = MyDataSet(data=train_corrupt_X, label=train_X)
                train_loader = torch.utils.data.DataLoader(dataset=train_set, batch_size=batch_size, shuffle=True)
                del train_set
                windows = train_sec.shape[1]
                model = Autoencoder(drop_perc, filter_size, stride, windows).to(device)
                criterion = nn.CrossEntropyLoss()
                optimizer = optim.Adam(model.parameters(), lr=learning_rate, betas=(0.9, 0.999), eps=1e-08, weight_decay=1e-5)
                lr_scheduler = optim.lr_scheduler.ReduceLROnPlateau(optimizer, mode='min', factor=0.9, patience=0)

                min_los = 1e10
                model.train()
                for epoch in range(epochs):
                    loss_sum=0
                    for data in train_loader:
                        corrupt, targets = data
                        corrupt = corrupt.float()
                        targets = targets.float()
                        targets = np.argmax(targets, axis=1)
                        corrupt = corrupt.to(device)
                        targets = targets.to(device)
                        output = model(corrupt)
                        loss = criterion(output, targets)
                        del output
                        optimizer.zero_grad()
                        loss.backward()
                        optimizer.step()
                        loss_sum=loss_sum+loss
                    nowEpochNum=nowEpochNum+1
                    print("schedule: {:.3f}%: ".format(nowEpochNum/epoch_num_all*100), "▓" * (nowEpochNum*100//epoch_num_all), end="")
                    print('\n')
                    proValue=round(nowEpochNum/epoch_num_all*100,1)
                    if epoch > 100 and optimizer.param_groups[0]["lr"] > 1e-4:
                        lr_scheduler.step(loss_sum)
                    if loss_sum < min_los and epoch > (epochs - 20):
                        min_los = loss_sum
                        torch.save(model.state_dict(), 'save.pth')
                del train_loader
                testyin_sec = testyin_x[:,trueStart : trueEnd]
                testyin_sec = torch.tensor(testyin_sec).to(torch.int64)
                missing_pos = testyin_sec == 0
                testyin_sec[missing_pos] = 2
                testyin_sec = testyin_sec - 1
                testyin_sec_onehot = F.one_hot(testyin_sec, num_classes=3)
                testyin_sec_onehot[missing_pos, :] = 0
                testyin_sec_onehot = torch.from_numpy(testyin_sec_onehot.numpy().transpose(0, 2, 1))
                testyin_X = testyin_sec_onehot
                testyin_X = testyin_X.float().to(device)

                model.load_state_dict(torch.load("save.pth"))
                model.eval()
                with torch.no_grad():
                    predict_onehot = model(testyin_X)
                del model
                predict_onehot_numpy = predict_onehot.detach().cpu().numpy()
                predict_onehot_numpy = predict_onehot_numpy.transpose(0, 2, 1)
                predict_missing_zong = []
                for i in range(all_unit2):
                    predict_missing_onehot = predict_onehot_numpy[i:i+1, testMissing_index[i], :]
                    predict_missing = np.argmax(predict_missing_onehot, axis=2)+1
                    predict_missing_zong.append(predict_missing[0])
                del train_sec, train_onehot,predict_onehot, predict_missing_onehot, predict_onehot_numpy
                del testMissing_index
                for m in range(len(predict_missing_zong)):
                    for n in range(len(predict_missing_zong[m])):
                        predictAll[m].append(predict_missing_zong[m][n])
    del train_corrupt_X,train_corrupt,train_X, testyin_X
    return predictAll
