import keras
import numpy as np
import pickle
from keras.models import Sequential
from keras.layers import Dense, Dropout, Activation, Flatten
from keras.layers import Convolution2D, MaxPooling2D, BatchNormalization
from keras.utils import np_utils
from keras.datasets import cifar10
from matplotlib import pyplot as plt
from keras import backend as K
from keras.optimizers import SGD, Adam
from keras.models import load_model
from keras import regularizers
K.set_image_dim_ordering('th')

np.random.seed(123)
(X_train, y_train), (X_test, y_test) = cifar10.load_data()

##no need, cifar 10 classifier already has this (shape[0], 3, 32, 32)
#X_train = X_train.reshape(X_train.shape[0], 3, 32, 32)
#X_test = X_test.reshape(X_test.shape[0], 3, 32, 32)

#Convert data type and normalize valuesPython
#Make sure to check the preprocessing steps defined in the paper
# (From section 5: Batch Normalization (Ioffe & Szegedy (2015)), 
# from Zimmer's file, 
# "we should s subtracting the mean RGB value, computed on the training set, from each pixel.""
X_train = X_train.astype('float32')
X_test = X_test.astype('float32')
X_train /= 255
X_test /= 255

#setup the y instances using 1 hot encoding
Y_train = np_utils.to_categorical(y_train, 10)
Y_test = np_utils.to_categorical(y_test, 10)

#8 models to be generated (2*2*2)
for batch_size in [128, 8192]:
	for weight_decay in [0, 0.0005]:
		for optimizer in ['sgd', 'adam']:

			#define model architecture
			model = Sequential()

			#padding = "same" (=padding), padding = "valid" (= no padding)
			#layer 1,2
			model.add(Convolution2D(64, (3, 3), input_shape=(3,32,32), padding="same", activation='relu', kernel_regularizer=regularizers.l2(weight_decay), name='c1'))
			model.add(BatchNormalization())
			model.add(Convolution2D(64, (3, 3), padding="same", activation='relu', kernel_regularizer=regularizers.l2(weight_decay), name='c2'))
			model.add(BatchNormalization())
			model.add(MaxPooling2D(pool_size=(2,2), padding="same"))

			#layer 3,4
			model.add(BatchNormalization())
			model.add(Convolution2D(128, (3, 3), padding="same", activation='relu', kernel_regularizer=regularizers.l2(weight_decay), name='c3'))
			model.add(BatchNormalization())
			model.add(Convolution2D(128, (3, 3), padding="same", activation='relu', kernel_regularizer=regularizers.l2(weight_decay), name='c4'))
			model.add(BatchNormalization())
			model.add(MaxPooling2D(pool_size=(2,2), padding="same"))

			#layer 4,5
			model.add(BatchNormalization())
			model.add(Convolution2D(256, (3, 3), padding="same", activation='relu', kernel_regularizer=regularizers.l2(weight_decay), name='c5'))
			model.add(BatchNormalization())
			model.add(Convolution2D(256, (3, 3), padding="same", activation='relu', kernel_regularizer=regularizers.l2(weight_decay), name='c6'))
			model.add(BatchNormalization())
			model.add(MaxPooling2D(pool_size=(2,2), padding="same"))

			#layer 6
			model.add(BatchNormalization())
			model.add(Convolution2D(512, (3, 3), padding="same", activation='relu', kernel_regularizer=regularizers.l2(weight_decay), name='c7'))
			model.add(BatchNormalization())
			model.add(MaxPooling2D(pool_size=(2,2), padding="same"))

			#layer 7,8,9
			model.add(BatchNormalization())
			model.add(Flatten())
			model.add(Dense(4096, activation='relu', kernel_regularizer=regularizers.l2(weight_decay), name='f1'))
			model.add(Dense(4096, activation='relu', kernel_regularizer=regularizers.l2(weight_decay), name='f2'))
			model.add(Dense(1000, activation='relu', kernel_regularizer=regularizers.l2(weight_decay), name='f3'))
			model.add(Dense(10, activation='softmax', name='o'))

			#create required optimizer
			if optimizer == 'sgd':
				opt = SGD(lr=0.1, decay=0, nesterov=True)
			elif optimizer == 'adam':
				opt = Adam(lr=0.1, beta_1=0.9, beta_2=0.999, decay=0)

			#compile model
			model.compile(loss='categorical_crossentropy',
						  optimizer=opt,
			              metrics=['acc'])

			#fit the model
			for num_epochs, learning_rate in zip([150, 75, 50, 25], [0.1, 0.01, 0.001, 0.0001]):
				model.optimizer.lr.assign(learning_rate)
				history = model.fit(X_train, Y_train, batch_size=batch_size, epochs=num_epochs, verbose=1, shuffle=False)

			#save model file
			filename = 'model_batch_size_' + str(batch_size) + '_optimizer_' + str(optimizer) + '_weight_decay_' + str(weight_decay)
			model.save(filename + '.h5')
			
			#save the history object
			with open(filename + '.hist', 'wb') as f:
				pickle.dump(history, f)

			# Verify this afterwards
			# model.save('start_dummy.h5')

			# history = model.fit(X_train, Y_train, batch_size=batch_size, epochs=1, verbose=1, shuffle=False ) #callbacks=[tbCallBack]
			
			# model.save('end_dummy.h5')

			# print(history.hist)


			