import cv2
import numpy as np
import os 
import mysql.connector
from mysql.connector import Error
from mysql.connector import errorcode

recognizer = cv2.face.LBPHFaceRecognizer_create()
recognizer.read('D:/VIT/EPICS Project/OpenCV-Face-Recognition-master/FacialRecognition/trainer/trainer.yml')
cascadePath = "D:/VIT/EPICS Project/OpenCV-Face-Recognition-master/FacialRecognition/haarcascade_frontalface_default.xml"
faceCascade = cv2.CascadeClassifier(cascadePath);

font = cv2.FONT_HERSHEY_SIMPLEX

#iniciate id counter
id=0
mydb = mysql.connector.connect(
  host="localhost",
  user="root",
  password="9810900370",
  database="ajbank"
)

mycursor = mydb.cursor()
# names related to ids: example ==> Ansh: id=1,  etc
names = ["None","Ashu","Swati","Anshuman","Jenish","Ayush","Rachit","Shrey","Siddharth",]

# Initialize and start realtime video capture
cam = cv2.VideoCapture(0)
cam.set(3, 640) # set video widht
cam.set(4, 480) # set video height

# Define min window size to be recognized as a face
minW = 0.1*cam.get(3)
minH = 0.1*cam.get(4)

while True:

    ret, img =cam.read()
    img = cv2.flip(img, 1) # Flip vertically

    gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)

    faces = faceCascade.detectMultiScale( 
        gray,
        scaleFactor = 1.2,
        minNeighbors = 5,
        minSize = (int(minW), int(minH)),
       )

    for(x,y,w,h) in faces:

        cv2.rectangle(img, (x,y), (x+w,y+h), (0,255,0), 2)

        id, confidence = recognizer.predict(gray[y:y+h,x:x+w])

        # Check if confidence is less them 100 ==> "0" is perfect match 
        if (confidence < 100):
            print(id)
            PersonID = id
            id = names[id]
            print(id)
            confidence = "  {0}%".format(round(100 - confidence))
            t=1
            #put_text(test_img,predict_name,x,y)
            try:
                connection = mysql.connector.connect(host='localhost',
                                                     database='ajbank',
                                                     user='root',
                                                     password='9810900370')
                mySql_insert_query = ("""INSERT INTO face (PersonID,Username) 
                                       VALUES 
                                       (%s, %s) """)
                                       
                
                record = (PersonID, id)
                cursor = connection.cursor()
                cursor.execute(mySql_insert_query, record)
                connection.commit()
                cam.release()
                print(cursor.rowcount, "Record inserted successfully into Guest table")
                cursor.close()
                break

            except mysql.connector.Error as error:
                print("Failed to insert record into Laptop table {}".format(error))

            finally:
                if (connection.is_connected()):
                    connection.close()
                    print("MySQL connection is closed")
                    break
                
        else:
            id = "unknown"
            confidence = "  {0}%".format(round(100 - confidence))
        
        cv2.putText(img, str(id), (x+5,y-5), font, 1, (255,255,255), 2)
        cv2.putText(img, str(confidence), (x+5,y+h-5), font, 1, (255,255,0), 1)  
    
    cv2.imshow('camera',img) 

    k = cv2.waitKey(10) & 0xff # Press 'ESC' for exiting video
    if k == 27:
        break

# Do a bit of cleanup
print("\n [INFO] Exiting Program and cleanup stuff")

#sql = "INSERT INTO Persons (PersonID, Username) VALUES (%s, %s)"
#val = ("1", id)

cv2.destroyAllWindows()
print(id)

