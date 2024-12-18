from django.shortcuts import render
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import LoginSerializer
from core.models import LibraryHistory
from core.serializers import LibraryHistorySerializer
from rest_framework.permissions import IsAuthenticated

# login for librarian
class LibrarianLoginView(APIView):
    def post(self, request):
        serializer = LoginSerializer(data=request.data)

        if serializer.is_valid():
            email = serializer.validated_data['email']
            password = serializer.validated_data['password']

            # Authenticate user
            user = authenticate(request, username=email, password=password)

            if user is not None:
                # Check if the user's role is 'librarian'
                if user.role != 'librarian':
                    return Response(
                        {"detail": "Access restricted to librarian only."}, 
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

# list of library history

class LibraryHistoryListAPIView(APIView):
    permission_classes=[IsAuthenticated]
    
    def get(self, request):
        
        library_history = LibraryHistory.objects.all()  

        serializer = LibraryHistorySerializer(library_history, many=True)  # Serialize the list of records
        return Response(serializer.data, status=status.HTTP_200_OK)