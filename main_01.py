# import the necessary packages
#from picamera.array import PiRGBArray
#from picamera import PiCamera
import time
import cv2
from servomove import servopos
ser=servopos()

face_cascade= cv2.CascadeClassifier('haarcascade_frontalface_default.xml')

#nell'originale caricava la videata come larga 320 e alta 240 pixel
#da cui il 160 e il 120 del Px e Py
Px,Ix,Dx=-1/160,0,0
Py,Iy,Dy=-0.2/120,0,0
integral_x,integral_y=0,0
differential_x,differential_y=0,0
prev_x,prev_y=0,0

font = cv2.FONT_HERSHEY_SIMPLEX

height=480
height2=240

width=640
width2=320

cam = cv2.VideoCapture(0)
time.sleep(2)

while (True):
    ret, frame = cam.read()
    frame=cv2.flip(frame,1)
    gray=cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY)    
    #print(frame.shape)
    ser.setdcx(0)
    ser.setdcy(0)
    
    #detect face coordinates x,y,w,h
    faces=face_cascade.detectMultiScale(gray,1.3,5)
    c=0
    for(x,y,w,h) in faces:
        c+=1
        if(c>1): #esco all aprima faccia che trovo
            break
        #centre of face
        face_centre_x=x+w/2
        #print('face_centre_x= ' + str(face_centre_x))
        face_centre_y=y+h/2
        #print('face_centre_y= ' + str(face_centre_y))
        #pixels to move rispetto a centro del frame
        #error_x=160-face_centre_x
        error_x=width/2-face_centre_x
        #error_y=120-face_centre_y
        error_y=height/2-face_centre_y
        
        integral_x=integral_x+error_x
        integral_y=integral_y+error_y
        
        differential_x= prev_x- error_x
        differential_y= prev_y- error_y
        
        prev_x=error_x
        prev_y=error_y
        
        valx=Px*error_x +Dx*differential_x + Ix*integral_x
        valy=Py*error_y +Dy*differential_y + Iy*integral_y
        
        
        valx=round(valx,2)
        valy=round(valy,2)

        #print('pixelerrorx=',error_x,'valx=',valx)
        #print('pixelerrory=',error_y,'valy=',valy)
        if abs(error_x)<20:
            ser.setdcx(0)
        else:
            if abs(valx)>0.5:
                sign=valx/abs(valx)
                valx=0.5*sign
            ser.setposx(valx)

        if abs(error_y)<20:
            ser.setdcy(0)
        else:
            if abs(valy)>0.5:
                sign=valy/abs(valy)
                valy=0.5*sign
            ser.setposy(valy)
            
        if(c==1):
            frame=cv2.rectangle(frame,(x,y),(x+w,y+h),(255,0,0),6)
            testoX= 'pixelerrorx='+ str(error_x) +' valx=' + str(valx)
            testoY= 'pixelerrory='+ str(error_y) +' valy=' + str(valy)
            frame=cv2.putText(frame, testoX,(50,50), font, 0.5, (255, 255, 0), 1, cv2.LINE_AA)
            frame=cv2.putText(frame, testoY,(50,70), font, 0.5, (0, 255, 0), 1, cv2.LINE_AA)
            
            #centro faccia
            frame=cv2.line(frame, (x,y),(x+w,y+h), (0,0,255),1)
            frame=cv2.line(frame, (x,y+h),(x+w,y), (0,0,255),1)
            frame=cv2.circle(frame, (int(x+w/2),int(y+h/2)), 5, (0, 0, 255), -1)
            
            #centro schermo
            frame=cv2.line(frame, (width2,0),(width2,height), (0,255,255),1)
            frame=cv2.line(frame, (0,height2),(width,height2), (0,255,255),1)

            
    
    cv2.imshow('titolo finestra',frame) #display image
    
    key = cv2.waitKey(1) & 0xFF
    if key == ord("q"):
        break

cv2.destroyAllWindows()

