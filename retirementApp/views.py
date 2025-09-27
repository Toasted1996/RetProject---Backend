#Importamos render, redirect y get_object_or_404 para manejo de vistas (renderizacion, redirigir y buscar objetos)
from django.shortcuts import render, redirect, get_object_or_404
#Importamos messages para mensajes flash
from django.contrib import messages
#Importamos los modelos a usar
from .models import Gestor
#Importamos los formularios a usar
from retirementApp.forms import GestorForm, CustomLoginForm, CustomUserCreationForm
#Importamos autenticacion, login y logout
from django.contrib.auth import authenticate, login, logout
#Importamos login_required para proteger vistas y user_passes_test para permisos(se asegura que sea admin)
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Q

# Create your views here.

#Verifica si el usuario es admin
def es_admin(user):
    #Verifica que el usuario pertenezca al grupo Administrador
    return user.groups.filter(name='Administrador').exists()
    

#Verifica si es gestor
def es_gestor(user):
    return user.groups.filter(name='Gestor').exists()



def inicio(request):
    return render(request, 'index.html')

                    #** CRUD GESTORES **#
#We're usign function based views for simplicity

#views para LOGIN y REGISTRO
def custom_login(request):
    #Si el usuario ya esta autenticado, redirige al inicio
    if request.user.is_authenticated:
        return redirect('inicio')
    #Si el metodo es POST, procesa el formulario para LOGIN
    if request.method == 'POST':
        form = CustomLoginForm(request, data = request.POST)
        #Verifica que el formulario sea valido
        if form.is_valid():
            #Trae los datos limpios del formulario
            username= form.cleaned_data.get('username')
            password= form.cleaned_data.get('password')
            #Autentica al usuario, comprobando credenciales
            user = authenticate(username=username, password=password)
            
            #Si el usuario es valido, lo loguea
            if user is not None:
                #Inicia sesion
                login(request, user)
                messages.success(request, 'Bienvenido/a de nuevo!') #Mensaje de exito
                #Redirigir segun su rol
                if user.groups.filter(name='Admin').exists():
                    return redirect('inicio')
                else:
                    return redirect('gestores')
            else: #Si no es valido, arrojara error
                messages.error(request, 'Usuario o contraseña incorrectos')
        else:
            messages.error(request, 'Corrija los datos ingresados')
    else:#Si no es POST, muestra el formulario vacio no autenticado
        form = CustomLoginForm()
    #Renderiza el formulario de login
    return render(request, 'auth/login.html', {'form': form, 'title':'Iniciar Sesión'})


#Views para LOGOUT
def custom_logout(request):
    #Si el request es de un usuario autenticado, obtiene su nombre, sino usa 'Usuario'
    name = request.user.first_name if request.user.is_authenticated and request.user.first_name else 'Usuario'
    logout(request)
    #Mensaje de exito
    messages.success(request, f'¡Nos vemos a la vuelta {name}!')
    return redirect('inicio')  #Redirige a inicio


# VISTA AUTENTICADA PARA ADMINs #
@login_required(login_url='login')
@user_passes_test(lambda u: u.groups.filter(name='Administrador').exists())
def register_user(request):
    #Esta es la vista para un Admin autenticado, podra crear nuevos usuarios
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save_user()#Guardamos el usuario con el metodo customizado
            messages.success(request, 'Usuario creado con exito')
            return redirect('login') #Redirige a login
        else:
            messages.error(request, 'Corrija los errores en el formulario')
    else:
        form = CustomUserCreationForm()
    return render(request, 'auth/register.html', {'form': form, 'title':'Registrar Usuario'})


#Vista para crear un gestor
@login_required(login_url='login') # Protege la vista, solo usuarios autenticados pueden acceder
@user_passes_test(es_admin) #Solo el administrador puede crear gestores
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

@login_required(login_url= 'login')
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

@login_required(login_url = 'login')
@user_passes_test(es_admin)
#view para editar un gestor
def editarGestor(request, id):
    #buscamos gestor por id
    gestor = get_object_or_404(Gestor, id=id)
    #validamos si es post
    if request.method == 'POST':
        #Procesa formulario con modelo existente
        form = GestorForm(request.POST, instance=gestor)
        #Si es valido, guarda
        if form.is_valid():
            form.save()
            messages.success(request, 'Gestor actualizado exitosamente')
            return redirect('gestores') #Redirije a la lista de gestores
        else: 
            messages.error(request, 'Corrija los errores en el formulario')
    else:
        form = GestorForm(instance=gestor) 
            
    data = {
        'titulo':'Editar Gestor',
        'form': form
    }
    return render(request, 'gestores/createGestor.html', data)


@login_required(login_url='login')
@user_passes_test(es_admin)
#vista para eliminar un gestor
def eliminarGestor(request, id):
    #Buscamos el gestor por id
    gestor = get_object_or_404(Gestor, id=id)
    #Si es post, eliminamos
    if request.method == 'POST':
        nombre = f'{gestor.nombre}{gestor.apellido}'
        gestor.delete()
        messages.success(request, f'Gestor {nombre} ha sidoa eliminado correctamente')
        return redirect ('gestores')    
    data = {
        'titulo':'Confirmar Eliminacion', 
        'gestor': gestor
    }
    