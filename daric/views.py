from django.shortcuts import render
from django.core.exceptions import ObjectDoesNotExist
from daric import User

# Create your views here.
def firstFun(request):
    try:
        query_set =User.objects.all()

        for user in query_set:
            print(user)
    except ObjectDoesNotExist:
        pass


    return render("hello")