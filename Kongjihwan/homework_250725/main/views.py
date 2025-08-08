from django.shortcuts import render

# Create your views here.
def index(request):
  return render(request, 'app/main.html')

def chatbot(request):
  return render(request, 'app/chatbot.html')