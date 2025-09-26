from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Gestor
from retirementApp.forms import GestorForm
from django.db.models import Q

# Create your views here.

def inicio(request):
    return render(request, 'index.html')

                    #** CRUD GESTORES **#
#We're usign function based views for simplicity

#Vista para crear un gestor
def crearGestor(request):
    if request.method == 'POST':
        #Procesa formulario
        form = GestorForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Gestor creado exitosamente')
            return redirect('gestores') #redirige a la lista de gestores
        else:
            messages.error(request, 'Corrija los errores en el formulario')
    else:
        #Muestra formulario vacio
        form = GestorForm()
        
    #Datos para el template
    data = {
        'titulo':'Crear Gestor',
        'form': form
    }
    #renderizamos el template con los datos
    return render(request, 'gestores/createGestor.html', data)


#view para lista todos los gestores con filtro y busqueda
def listaGestores(request):
    gestores = Gestor.objects.all()
    # Filtrado por busqueda
    query = request.GET.get('query', '').strip()
    if query:
        gestores = gestores.filter(
            Q(nombre__icontains=query) | Q(apellido__icontains=query) | Q(rut__icontains=query)| Q(email__icontains=query)
        )

    #Datos para el template
    data = {
        'gestores': gestores,
        'title': 'Gestores'
    }
    return render(request, 'gestores/gestores.html', data)


