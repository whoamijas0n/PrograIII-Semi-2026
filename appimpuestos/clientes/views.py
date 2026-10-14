from django.http.response import HttpResponse
from django.shortcuts import render

# Create your views here.

def hola_mundo(request):
        return HttpResponse("Hola mundo")   

def SaludoNombre(request, nombre, edad):
        return HttpResponse(f"Hola  {nombre}  Bienvenido a mi pagina, tu edad es {edad} anios")

def index(request):
    return render(request, 'index.html')