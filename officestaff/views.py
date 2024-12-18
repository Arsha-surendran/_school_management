from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import LoginSerializer
from rest_framework.permissions import IsAuthenticated
from core.models import Student
from core.serializers import StudentSerializer


class StaffLoginView(APIView):
    def post(self, request):
        serializer = LoginSerializer(data=request.data)

        if serializer.is_valid():
            email = serializer.validated_data['email']
            password = serializer.validated_data['password']

            # Authenticate user
            user = authenticate(request, username=email, password=password)

            if user is not None:
                # Check if the user's role is 'staff'
                if user.role != 'staff':
                    return Response(
                        {"detail": "Access restricted to Office Staff only."}, 
                        status=status.HTTP_403_FORBIDDEN
                    )

                # Generate JWT tokens
                refresh = RefreshToken.for_user(user)
                access_token = str(refresh.access_token)

                response_data = {
                    'access_token': access_token,
                    'refresh_token': str(refresh),
                    'user_id': user.id,
                    'name': user.name,
                    'email': user.email,
                    'role': user.role,
                }

                return Response(response_data, status=status.HTTP_200_OK)

            return Response({"detail": "Invalid email or password."}, status=status.HTTP_401_UNAUTHORIZED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# details of all students

class StudentListAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        students = Student.objects.all()  
        serializer = StudentSerializer(students, many=True)  # Serialize the data
        return Response(serializer.data, status=status.HTTP_200_OK)
