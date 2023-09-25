from django.shortcuts import render

# Create your views here.

def upload_folder(request):
    return render(request, 'chat/chat.html')
