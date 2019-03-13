from django.db.migrations import serializer
from django.shortcuts import render

# Create your views here.

# from rest_framework.views import APIView
# from rest_framework.response import Response
# from django.shortcuts import get_object_or_404
#
# from .models import Poll, Choice
# from  .serializers import PollSerializer
#
# class PollList(APIView):
#     def get(self, request):
#         polls = Poll.objects.all()[:20]
#         data = PollSerializer(polls, many=True).data
#         return Response(data)
#
#
# class PollDetail(APIView):
#     def get(self, request, pk):
#         poll = get_object_or_404(Poll, pk=pk)
#         data = PollSerializer(poll).data
#         return Response(data)
from rest_framework.response import Response
from rest_framework.views import APIView

'''
The generic views of Django Rest Framework help us in code reusablity. 
They infer the response format and allowed methods from the serializer class and base class.

'''
from rest_framework import generics, status
from rest_framework.viewsets import ModelViewSet

from .models import Poll, Choice
from .serializers import (PollSerializer, ChoiceSerializer,
                          VoteSerializer, UserSerializer)
from django.contrib.auth import authenticate

'''
The /polls/ and /polls/<pk>/ urls require two view classes, 
with the same serializer and base queryset.
We can group them into a viewset, and connect them to the urls using a router.
'''


class PollViewSet(ModelViewSet):
    # authentication_classes = ()
    # permission_classes = ()
    queryset = Poll.objects.all()
    serializer_class = PollSerializer
    """
    Destroy a model instance.
    Authenticated users can delete only polls they have created.
    We will do that by overriding PollViewSet.destroy .
    """

    def destroy(self, request, *args, **kwargs):

        instance = self.get_object()
        if request.user.id==instance.id:
            self.perform_destroy(instance)
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(
            {"detail": "You can not delete this poll."},
            status=status.HTTP_403_FORBIDDEN
        )


    def perform_destroy(self, instance):
        instance.delete()



# class PollList(generics.ListCreateAPIView):
#     queryset = Poll.objects.all()
#     serializer_class = PollSerializer
#
#
# class PollDetail(generics.RetrieveUpdateDestroyAPIView):
#     queryset = Poll.objects.all()
#     serializer_class = PollSerializer


class ChoiceList(generics.ListCreateAPIView):
    '''
    From the urls, we pass on pk to ChoiceList. We override the get_queryset method,
    to filter on choices with this poll_id, and let DRF handle the rest.
    '''
    '''
    Authenticated users can create choices only for polls they have created.
    We will do that by overriding ChoiceList.post.
    '''

    def post(self, request, *args, **kwargs):
        poll= Poll.objects.get(id=kwargs['pk'])

        if request.user.id ==poll.created_by.id:
            return self.create(request, *args, **kwargs)
        message = {"detail": "You can not create choice for this poll."}
        return Response(message,status=status.HTTP_403_FORBIDDEN)



    # queryset = Choice.objects.all()
    def get_queryset(self):
        queryset = Choice.objects.filter(poll_id=self.kwargs["pk"])
        return queryset

    serializer_class = ChoiceSerializer



'''
queryset is not usable for creating object
'''
# class CreateVote(generics.CreateAPIView):
#     serializer_class = VoteSerializer
#


'''
We pass on poll id and choice id. We subclass this from APIView, 
rather than a generic view, 
because we competely customize the behaviour.
'''


class CreateVote(APIView):

    def post(self, request, pk, choice_pk):
        voted_by = request.data.get("voted_by")
        data = {'choice': choice_pk, 'poll': pk, 'voted_by': voted_by}
        serializer = VoteSerializer(data=data)
        if serializer.is_valid():
            vote = serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


'''
Use viewsets.ModelViewSet when you are going to allow all or most of CRUD operations on a model.
Use generics.* when you only want to allow some operations on a model
Use APIView when you want to completely customize the behaviour.
'''


class UserCreate(generics.CreateAPIView):
    authentication_classes = ()
    permission_classes = ()
    serializer_class = UserSerializer


class LoginView(APIView):
    permission_classes = ()


    def post(self, request, ):
        username = request.data.get("username")
        password = request.data.get("password")
        user = authenticate(username=username, password=password)
        if user:
            return Response({"token": user.auth_token.key,
                             "user":user.username,
                             })


        else:
            return Response({"error": "Wrong Credentials"}, status=status.HTTP_400_BAD_REQUEST)
