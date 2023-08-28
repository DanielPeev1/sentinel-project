from sklearn.utils import shuffle
import numpy as np
import tensorflow as tf
from keras.layers import Dense, Flatten, BatchNormalization, GroupNormalization, Conv2D, \
    Input, PReLU, AveragePooling2D
from sklearn.model_selection import train_test_split
from keras import Model, regularizers

#Loading in the dataset
dataset = np.load("dataset-lee-sigma-alt-plus.npy", allow_pickle=True)

#Arrays used to store the mean-squared error
#and root-mean-squared error values for the
#different folds of the k-fold cross validation used
MSE_test_values = []
RMSE_test_values = []

#k-fold validation loop with k = 5
for i in range(5):

    #Initial shuffling of the dataset
    dataset = shuffle(dataset)

    #The SAR image arrays used as input data for the network
    #The first two channels in this dataset are the VH and VV images
    #The third and fourth channels are the values for VH-VV and VH/VV
    sar = [entry["sarImage"][:, :, 0:4] for entry in dataset]

    #The dimensions of the SAR images
    height = [s.shape[0] for s in sar]
    width = [s.shape[1] for s in sar]

    #Resizing the SAR image arrays to all be of uniform dimensions
    maxWidth = max(width)
    maxHeight = max(height)
    sar = np.array(
        [np.pad(s, [(0, maxHeight - s.shape[0]), (0, maxWidth - s.shape[1]), (0, 0)]) for s in sar])

    #Loading in the NDVI values to be used as labels for the network
    ndvi = np.array([entry["y"] for entry in dataset])

    #The last NDVI values are stored as a fifth channel to the SAR image
    #Here they are loaded to the lastNDVI array
    lastNDVI = np.array([entry["sarImage"][:, :, 4:5] for entry in dataset])
    ids = np.array([entry["id"] for entry in dataset])

    #The shape of the SAR image
    sarShape = sar[0].shape

    ##The shape of the lastNDVI image
    lastNDVIShape = lastNDVI[0].shape
    ndviShape = ndvi[0].shape
    ndviReshaped = ndvi.reshape([ndvi.shape[0], ndvi.shape[1] * ndvi.shape[2]])

    #Dividing the dataset into a train and test set.
    #A test set size of 20% of the total data is used
    trainID, testID, trainX, testX, trainLastNDVI, testLastNDVI, trainY, testY = train_test_split(ids, sar, lastNDVI,
                                                                                                  ndviReshaped,
                                                                                                  test_size=0.2,
                                                                                                  random_state=41)
    #The architecture of the first Convolutional neural network
    inputSar = Input(shape=sarShape)
    img1 = GroupNormalization(groups = -1)(inputSar)
    img1 = Conv2D(filters=128, kernel_size=(5, 5), activation='relu', padding='same')(img1)
    img1 = AveragePooling2D(pool_size=(2, 2), strides=2)(img1)
    img1 = Conv2D(filters=64, kernel_size=(5, 5), activation='relu', padding='same')(img1)
    img1 = AveragePooling2D(pool_size=(2, 2), strides=2)(img1)
    img1 = Conv2D(filters=64, kernel_size=(5, 5), activation='relu', padding='same')(img1)
    img1 = Flatten()(img1)
    model1 = img1
    model1 = Dense(1028, activation="relu")(model1)
    model1 = Dense(ndviReshaped.shape[1])(model1)
    model1 = Model(inputs=inputSar, outputs=model1)

    #The architecture of the second Convolutional neural network
    inputLastNDVI = Input(shape=lastNDVIShape)
    img2 = inputLastNDVI
    img2 = Conv2D(filters=64, kernel_size=(3, 3), activation='relu', padding='same')(img2)
    img2 = AveragePooling2D(pool_size=(2, 2), strides=2)(img2)
    img2 = Flatten()(img2)
    model2 = img2
    model2 = Dense(256, activation="relu")(model2)
    model2 = Dense(ndviReshaped.shape[1])(model2)
    model2 = Model (inputs = inputLastNDVI, outputs = model2)

    #Combining the results of the two networks via a weighed sum
    #The weights can be adjusted
    combined = (1 * model1.output + 1 * model2.output)
    combined = Model (inputs = [model1.input, model2.input], outputs = combined)
    model = combined

    #A summary of the combined model
    print(model.summary())

    #Compililng the model
    model.compile(optimizer=tf.keras.optimizers.Adam(learning_rate=0.0001, weight_decay=0.01), loss="mean_squared_error",
                  metrics=[tf.keras.metrics.RootMeanSquaredError()])

    #Training and validating the model with a 10% validation split
    history = model.fit(
        x=[trainX, trainLastNDVI],
        y=trainY,
        epochs=40,
        verbose='auto',
        batch_size = 10,
        validation_split=0.1)

    #Evalueting the model on the test set and
    #recording the value for the MSE and RMSE for each fold
    score = model.evaluate([testX, testLastNDVI], testY)
    MSE_test_values.append(score[0])
    RMSE_test_values.append(score[1])

#Displaying the average value of the MSE and RMSE over all folds
print(np.average(MSE_test_values))
print(np.average(RMSE_test_values))