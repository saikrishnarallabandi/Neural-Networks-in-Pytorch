import torch 
import os, sys 
import numpy 
from torch.utils.data import Dataset 
from torch.utils.data import DataLoader 
import torch.nn as nn 
import torch.nn.functional as F 
from torch.autograd import Variable 
from torch import autograd 
from pytorch_models import Train_vae
from pytorch_models import enc as Encoder
from pytorch_models import dec as Decoder
import numpy as np

class vcc2018_data(Dataset):


         def __init__(self, inp, out):

             self.x = inp
             self.y = out

         def __getitem__(self,index ):

             return self.x[index], self.y[index]

         def __len__(self,):

              return len(self.x)


learning_rate = 0.001
src_dim = 60
latent_dim = src_dim
hidden_dim = 512

pred_dir = '/home3/srallaba/projects/siri_expts/8september/scripts/predicted_pytorch_dnn' ### path to folder prediction folder

X_train = []
Y_train = []
X_valid = []
Y_valid = []
valid_files = []

g = open('files.test','w')
print("loading data.....")

source_folder ='/home3/srallaba/projects/siri_expts/8september/Data/vcc2018_training/SF1_TF1/input_full/'  ### input folder
os.chdir(source_folder)
files = sorted(os.listdir('.'))

for file in files:
        x_train = numpy.loadtxt(file)
        X_train.append(x_train)

target_folder ='/home3/srallaba/projects/siri_expts/8september/Data/vcc2018_training/SF1_TF1/output_full/'  ### output folder
os.chdir(target_folder)
files = sorted(os.listdir('.'))

for file in files:
#        print("file is:", file)
        y_train = numpy.loadtxt(file)
        Y_train.append(y_train)

valid_input_folder ='/home3/srallaba/projects/siri_expts/8september/Data/vcc2018_training/SF1_TF1/valid_input/'  ### valid input folder
os.chdir(valid_input_folder)
files = sorted(os.listdir('.'))

for file in files:
        x_valid = numpy.loadtxt(file)
        X_valid.append(x_valid)

valid_output_folder ='/home3/srallaba/projects/siri_expts/8september/Data/vcc2018_training/SF1_TF1/valid_output/'  ### valid output folder
os.chdir(valid_output_folder)
files = sorted(os.listdir('.'))

for file in files:
        y_valid = numpy.loadtxt(file)
        Y_valid.append(y_valid)


train_data = vcc2018_data(X_train, Y_train)
train_loader = DataLoader(dataset = train_data, batch_size=1, shuffle=True)


valid_data = vcc2018_data(X_valid, Y_valid)
valid_loader = DataLoader(dataset = valid_data, batch_size=1, shuffle=False)

encoder = Encoder(src_dim, hidden_dim, hidden_dim)
decoder = Decoder(latent_dim, hidden_dim, src_dim)
Model= Train_vae(encoder, decoder).float()

loss_func = nn.MSELoss()
optimizer = torch.optim.SGD(Model.parameters(), lr=learning_rate, momentum= 0.9)
scheduler = torch.optim.lr_scheduler.ReduceLROnPlateau(optimizer, 'min')

def Train(epoch):
  Model.train()
  total_loss = 0
  print("epoch", epoch)

  for src, tgt in train_loader:
    decoder_output, latent_loss = Model(autograd.Variable(src, requires_grad=True).float())
#    print("predictions", decoder_output)

    loss = loss_func(decoder_output.float(), src.float()) + latent_loss
    total_loss += loss.item()
    optimizer.zero_grad()
    loss.backward()       
    optimizer.step()
  print("Training loss after ", epoch, "epochs is: ", (total_loss * 1.0)/ (epoch+1))


  val_loss = validation(epoch)
  scheduler.step(val_loss)

# Evaluate

def validation(epoch):
  Model.eval()
  total_loss = 0

  for src, tgt in valid_loader:
    decoder_output, latent_loss = Model(autograd.Variable(src).float())
 #   print("predictions", pred)
    loss = loss_func(decoder_output.float(), src.float()) + latent_loss
    total_loss += loss.item()

    optimizer.zero_grad()
    loss.backward()
    optimizer.step()
  print("Validation loss after ", epoch, "epochs is: ", total_loss * 1.0/ (epoch+1))
  return total_loss

# Train
for epoch in range(30):
   Train(epoch)
   print('\n')


