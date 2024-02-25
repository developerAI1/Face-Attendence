from django.http import HttpResponse
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.authentication import JWTAuthentication 
from rest_framework.views import APIView
from rest_framework.response import Response 
from django.contrib.auth import authenticate
from rest_framework.permissions import IsAuthenticated , AllowAny
from distutils import errors
from rest_framework.authentication import authenticate
from . renderer import *
from . serializers import *
from . models import *


import cv2 
import pickle 
import numpy as np
import os

facedetect=cv2.CascadeClassifier(os.getcwd() +"\model\haarcascade_frontalface_default.xml")

# Create your views here
def get_tokens_for_user(user):  
    refresh = RefreshToken.for_user(user)
    return {
        # 'refresh': str(refresh),
        'access': str(refresh.access_token),
    }
    
# Api for User Register
class UserRegistrationView(APIView):
    renderer_classes=[UserRenderer]
    def post(self,request,format=None):
        serializer=UserRegistrationSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            user=serializer.save()
            return Response({'message':'Registation successful',"status":"status.HTTP_200_OK",'user_id': user.id})
        return Response({errors:serializer.errors},status=status.HTTP_400_BAD_REQUEST)
    
# Api for user login
class UserLoginView(APIView):
    renderer_classes = [UserRenderer]
    def post(self, request, format=None):
        serializer = UserLoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.data.get('email')
        password = serializer.data.get('password')
        user = authenticate(email=email, password=password)
        if user is not None:
            token = get_tokens_for_user(user)
            is_admin = user.is_staff
            return Response({'token':token, "is_admin":is_admin,'msg':'Login Success'}, status=status.HTTP_200_OK)
        else:
            return Response({'errors':{'non_field_errors':['Email or Password is not Valid']}}, status=status.HTTP_404_NOT_FOUND)
# Api for user profile
class UserProfileView(APIView):
    renderer_classes = [UserRenderer]
    authentication_classes=[JWTAuthentication]
    def get(self, request, format=None):
        try:
            serializer = UserProfileSerializer(request.user)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'detail': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# Api for user logout
class LogoutUser(APIView):
    renderer_classes = [UserRenderer]
    permission_classes=[IsAuthenticated]
    def post(self, request, format=None):
        return Response({'message':'Logout Successfully'},status=status.HTTP_200_OK)

class Videocapture(APIView):
    faces_data = []
    i = 0

    def post(self, request):
        video = cv2.VideoCapture(0)
        Name = input(" Please Enter your Name : ")
        while True:
            ret, frame = video.read()
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = facedetect.detectMultiScale(gray, 1.3, 5)
            for (x, y, w, h) in faces:
                crop_img = frame[y:y+h, x:x+w, :]
                resized_img = cv2.resize(crop_img, (50, 50))
                if len(self.faces_data) <= 20 and self.i % 10 == 0:
                    self.faces_data.append(resized_img)
                self.i += 1
                cv2.putText(frame, str(len(self.faces_data)), (50, 50), cv2.FONT_HERSHEY_COMPLEX, 1, (50, 50, 255), 1)
                cv2.rectangle(frame, (x, y), (x+w, y+h), (50, 50, 255), 1)

            cv2.imshow("Frame", frame)
            k = cv2.waitKey(1)
            if k == ord('q') or len(self.faces_data) == 20:
                break

        video.release()
        cv2.destroyAllWindows()

        self.faces_data=np.asarray(self.faces_data)
        self.faces_data=self.faces_data.reshape(100 , -1)
        try:
            # Assuming self.faces_data and Name are defined properly in your code        
            if 'names.pkl' not in os.listdir(r'C:\Users\Mandeep\Desktop\AttendenceSystem\Face_Attendence\data'):
                names = [Name] * 20
                with open(r'C:\Users\Mandeep\Desktop\AttendenceSystem\Face_Attendence\data\names.pkl', 'wb') as f:
                    pickle.dump(names, f)
            else:
                with open(r'C:\Users\Mandeep\Desktop\AttendenceSystem\Face_Attendence\data\names.pkl', 'rb') as f:
                    names = pickle.load(f)
                names = names + [Name] * 20
                with open(r'C:\Users\Mandeep\Desktop\AttendenceSystem\Face_Attendence\data\names.pkl', 'wb') as f:
                    pickle.dump(names, f)

            if 'faces_data.pkl' not in os.listdir(r'C:\Users\Mandeep\Desktop\AttendenceSystem\Face_Attendence\data'):
                with open(r'C:\Users\Mandeep\Desktop\AttendenceSystem\Face_Attendence\data\faces_data.pkl', 'wb') as f:
                    pickle.dump(self.faces_data, f)
            else:
                with open(r'C:\Users\Mandeep\Desktop\AttendenceSystem\Face_Attendence\data\faces_data.pkl', 'rb') as f:
                    faces = pickle.load(f)
                faces = np.append(faces, self.faces_data, axis=0)
                with open(r'C:\Users\Mandeep\Desktop\AttendenceSystem\Face_Attendence\data\faces_data.pkl', 'wb') as f:
                    pickle.dump(faces, f)

            return Response({"message":"Everything Working fine"},status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'message': str(e)},status=status.HTTP_400_BAD_REQUEST)





                            
                