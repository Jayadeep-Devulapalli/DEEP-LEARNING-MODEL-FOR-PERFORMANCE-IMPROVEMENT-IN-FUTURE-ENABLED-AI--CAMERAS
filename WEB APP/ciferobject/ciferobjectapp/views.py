# Create your views here.
from django.shortcuts import render
from django.template import RequestContext
from django.contrib import messages
import pymysql
from django.http import HttpResponse
from django.core.files.storage import FileSystemStorage
import os
import cv2
from PIL import Image, ImageDraw, ImageFont

import tensorflow as tf
from tensorflow.keras.datasets import cifar10
from tensorflow.keras.models import Sequential, load_model
from tensorflow.keras.layers import Conv2D, MaxPooling2D, Flatten, Dense, Dropout
from tensorflow.keras.utils import to_categorical
import numpy as np
from PIL import Image
import matplotlib.pyplot as plt
class_names = ['airplane', 'automobile', 'bird', 'cat', 'deer', 'dog', 'frog', 'horse', 'ship', 'truck']

def Upload(request):
    if request.method == 'GET':
       return render(request, 'Upload.html', {})

def index(request):
    if request.method == 'GET':
       return render(request, 'index.html', {})

def Login(request):
    if request.method == 'GET':
       return render(request, 'Login.html', {})

def Register(request):
    if request.method == 'GET':
       return render(request, 'Register.html', {})


def Signup(request):
    if request.method == 'POST':
      #user_ip = getClientIP(request)
      #reader = geoip2.database.Reader('C:/Python/PlantDisease/GeoLite2-City.mmdb')
      #response = reader.city('103.48.68.11')
      #print(user_ip)
      #print(response.location.latitude)
      #print(response.location.longitude)
      username = request.POST.get('username', False)
      password = request.POST.get('password', False)
      contact = request.POST.get('contact', False)
      email = request.POST.get('email', False)
      address = request.POST.get('address', False)
      
      db_connection = pymysql.connect(host='127.0.0.1',port = 3306,user = 'root', password = 'root', database = 'ObjectDB',charset='utf8')
      db_cursor = db_connection.cursor()
      student_sql_query = "INSERT INTO register(username,password,contact,email,address) VALUES('"+username+"','"+password+"','"+contact+"','"+email+"','"+address+"')"
      db_cursor.execute(student_sql_query)
      db_connection.commit()
      print(db_cursor.rowcount, "Record Inserted")
      if db_cursor.rowcount == 1:
       context= {'data':'Signup Process Completed'}
       return render(request, 'Register.html', context)
      else:
       context= {'data':'Error in signup process'}
       return render(request, 'Register.html', context)    
        
def UserLogin(request):
    if request.method == 'POST':
        username = request.POST.get('username', False)
        password = request.POST.get('password', False)
        utype = 'none'
        con = pymysql.connect(host='127.0.0.1',port = 3306,user = 'root', password = 'root', database = 'ObjectDB',charset='utf8')
        with con:
            cur = con.cursor()
            cur.execute("select * FROM register")
            rows = cur.fetchall()
            for row in rows:
                if row[0] == username and row[1] == password:
                    utype = 'success'
                    break
        if utype == 'success':
            file = open('session.txt','w')
            file.write(username)
            file.close()
            context= {'data':'welcome '+username}
            return render(request, 'UserScreen.html', context)
        if utype == 'none':
            context= {'data':'Invalid login details'}
            return render(request, 'Login.html', context)


# Build a simple CNN model architecture
def create_model():
    model = Sequential()
    model.add(Conv2D(32, (3, 3), activation='relu', input_shape=(32, 32, 3)))
    model.add(Conv2D(32, (3, 3), activation='relu'))
    model.add(MaxPooling2D((2, 2)))
    model.add(Dropout(0.25))
    
    model.add(Conv2D(64, (3, 3), activation='relu'))
    model.add(Conv2D(64, (3, 3), activation='relu'))
    model.add(MaxPooling2D((2, 2)))
    model.add(Dropout(0.25))
    
    model.add(Flatten())
    model.add(Dense(512, activation='relu'))
    model.add(Dropout(0.5))
    model.add(Dense(10, activation='softmax'))
    
    model.compile(loss='categorical_crossentropy', optimizer='adam', metrics=['accuracy'])
    return model

# Train a model on CIFAR-10 if no pre-trained model exists
def train_model():
    (x_train, y_train), (x_test, y_test) = cifar10.load_data()
    x_train = x_train.astype('float32') / 255.0
    x_test = x_test.astype('float32') / 255.0
    y_train = to_categorical(y_train, 10)
    y_test = to_categorical(y_test, 10)
    
    model = create_model()
    model.fit(x_train, y_train, batch_size=64, epochs=10, validation_data=(x_test, y_test))
    model.save('model/cifar10_model.h5')
    return model


def UploadImage(request):
    if request.method == 'POST':
        myfile = request.FILES['t1']
        fname = request.FILES['t1'].name
        fs = FileSystemStorage()
        
        if os.path.exists('ciferobjectapp/static/object/test.png'):
            os.remove('ciferobjectapp/static/object/test.png')
        filename = fs.save('ciferobjectapp/static/object/test.png', myfile)
        
      #  model = load_model('model/cifar10_model.h5')

        # Load a pre-trained model if available; otherwise, train a new one.
        try:
            model = load_model('model/cifar10_model.h5')
            print("Loaded pre-trained model.")
        except Exception as e:
            print("Pre-trained model not found. Training a new model...")
            model = train_model()



        '''
        img = cv2.imread('ciferobjectapp/static/object/test.png')
        img = cv2.resize(img, (64,64))
        im2arr = np.array(img)
        im2arr = im2arr.reshape(1,64,64,3)
        X = np.asarray(im2arr)
        X = X.astype('float32')
        X = X/255
        preds = model.predict(X)
        print(str(preds)+" "+str(np.argmax(preds)))
        predict = np.argmax(preds)
        print(plants[predict])
        img = im2arr.reshape(64,64,3)
'''
        # Open the image and convert to RGB
        img = Image.open(filename).convert('RGB')
        #img = cv2.imread('ciferobjectapp/static/object/test.png')
        # Resize image to match CIFAR-10 input size (32x32)
        img_resized = img.resize((32, 32))
        img_array = np.array(img_resized).astype('float32') / 255.0
        img_array = np.expand_dims(img_array, axis=0)  # Add batch dimension
        
        # Predict the class of the image
        prediction = model.predict(img_array)
        predicted_class = class_names[np.argmax(prediction)]
        print(predicted_class)
        
        
        # Load the original image for display
        original_img = Image.open(filename).convert('RGB').resize((840, 620))

        # Create a drawing context
        draw = ImageDraw.Draw(original_img)

        # Load a font (default PIL font used here; you can specify a TTF file)
        try:
            font = ImageFont.truetype("arial.ttf", 25)  # Use Arial font
        except IOError:
            font = ImageFont.load_default()  # Fallback if Arial is not available

        # Define text and position
        text = f"Object Identified as {predicted_class}"
        text_position = (10, 25)
        text_color = (255, 0, 0)  # Yellow color

        # Draw text on image
        draw.text(text_position, text, fill=text_color, font=font)

        # Show the image with text
        original_img.show()
        #img = cv2.resize(img,(850,650))
        #cv2.putText(img, 'Object Identified as '+class_names[predicted_class], (10, 25),  cv2.FONT_HERSHEY_SIMPLEX,0.7, (0, 255, 255), 2)

        #cv2.imshow('Object Identified as '+class_names[predicted_class],img)
        #cv2.waitKey(0)
        context= {'data':predicted_class}
        return render(request, 'Upload.html', context)
    return render(request, 'Upload.html')



        
            
