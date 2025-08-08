from django.shortcuts import render

# Create your views here.
def main(request):
  return render(request, 'app/main.html')

def chatbot(request):
  return render(request, 'app/index.html')