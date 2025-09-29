#Importamos render, redirect y get_object_or_404 para manejo de vistas (renderizacion, redirigir y buscar objetos)
from django.shortcuts import render, redirect, get_object_or_404
#Importamos messages para mensajes flash
from django.contrib import messages
#Importamos los modelos a usar
from .models import Gestor, Expediente
#Importamos los formularios a usar
from retirementApp.forms import GestorForm, ExpedienteForm, CustomLoginForm
#Importamos autenticacion, login y logout
from django.contrib.auth import authenticate, login, logout
#Importamos el modelo User
from django.contrib.auth.models import User, Group
#Importamos login_required para proteger vistas y user_passes_test para permisos(se asegura que sea admin)
from django.contrib.auth.decorators import login_required, user_passes_test
#Importamos Q para manejar comparaciones complejas en las consultas
from django.db.models import Q
from datetime import date

# Create your views here.

#Verifica si el usuario es admin
def es_admin(user):
    #Verifica que el usuario pertenezca al grupo Administrador
    return user.is_authenticated and (user.is_superuser or user.groups.filter(name='Administrador').exists())
    

#Verifica si es gestor
def es_gestor(user):
    return user.is_authenticated and user.groups.filter(name='Gestor').exists()


def inicio(request):
    return render(request, 'index.html')


#Logica de Autenticacion para LOGIN
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
                if user.groups.filter(name='Administrador').exists():
                    return redirect('gestores')
                #Si es gestor, redirige a los expedientes existentes
                elif user.groups.filter(name='Gestor').exists():
                    return redirect('expedientes') #Redirige a expedientes para gestores
                else:
                    messages.error(request, 'No cuenta con una cuenta o rol asignado, contacte a su Manager')            
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


#** CRUD GESTORES **#
#We're usign function based views for simplicity

#views para LOGIN y REGISTRO
    #Si el request es de un usuario autenticado, obtiene su nombre, sino usa 'Usuario'
    name = request.user.first_name if request.user.is_authenticated and request.user.first_name else 'Usuario'
    logout(request)
    #Mensaje de exito
    messages.success(request, f'¡Nos vemos a la vuelta {name}!')
    return redirect('inicio')  #Redirige a inicio


#Vista protegida para registro de usuarios - SOLO ADMIN
@login_required(login_url='login')
@user_passes_test(es_admin)
def register_user(request):
    #Vista para que Admin cree nuevos usuarios
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '').strip()
        password2 = request.POST.get('password2', '').strip()
        rol = request.POST.get('rol', '').strip()
        
        errores = []
        if not all([username, email, password, password2, rol]):
            errores.append('Todos los campos son obligatorios.')
        
        elif password != password2:
            errores.append('Las contraseñas no coinciden.')

        elif User.objects.filter(username=username).exists():
            errores.append('El nombre de usuario ya existe.')

        elif User.objects.filter(email=email).exists():
            errores.append('El correo electrónico ya esta en uso.')
            
        elif len(password) < 6:
            errores.append('La contraseña debe tener al menos 6 caracteres.')
            
        if errores:
            for error in errores:
                messages.error(request, error)
        else:
            try:
                # Creacion del usuario
                nuevo_usuario = User.objects.create_user(
                    username = username,
                    email = email,
                    password = password,
                )    

                #Asignacion de rol
                if rol  == 'Administrador':
                    grupo = Group.objects.get(name='Administrador')
                else:
                    grupo = Group.objects.get(name='Gestor')
                nuevo_usuario.groups.add(grupo)
                nuevo_usuario.save()
                messages.success(request, f'Usuario {username} creado con exito' )
                return redirect('gestores')
            except Exception as error:
                messages.error(request, f'Error al crear usuario: {error}')
            
    data = {
        'title': 'Registrar Usuario'
    }
    return render(request, 'auth/register.html', data)


#Vista para crear un gestor
@login_required(login_url='login')
@user_passes_test(es_admin)
def crearGestor(request):
    """Vista unificada - Crear Gestor + Usuario"""
    if request.method == 'POST':
        form = GestorForm(request.POST)
        if form.is_valid():
            try:
                #Usar el método save_gestor (como save_user en register)
                gestor = form.save_gestor()
                messages.success(
                    request, 
                    f'Gestor {gestor.nombre} {gestor.apellido} creado exitosamente'
                )
                return redirect('gestores')
            except Exception as error:
                messages.error(request, f'Error al crear gestor: {error}')
        else:
            messages.error(request, 'Corrija los errores en el formulario')
    else:
        form = GestorForm()
    
    data = {
        'titulo': 'Crear Gestor',
        'form': form
    }
    return render(request, 'gestores/createGestor.html', data)

@login_required(login_url= 'login')
#view para lista todos los gestores con filtro y busqueda
def listaGestores(request):
    #Verificar rol
    if es_gestor(request.user):
        #El gestor solo podra ver info limitada - Su propio perfil con los expedientes asignados
        try:
            gestor_usuario = Gestor.objects.get(
                nombre = request.user.first_name,
                apellido = request.user.last_name
            )
            #Filtro para mostrar su propio perfil
            gestores = Gestor.objects.filter(id=gestor_usuario.id)
            create = False
            titulo = 'Mi perfil'
        except Gestor.DoesNotExist:
            messages.error(request, 'No se encontro el gestor asociado a su cuenta. Contacte a su Manager.')
    #Si es Admin podra ver todos los gestores
    elif es_admin(request.user):
        gestores = Gestor.objects.all()
        create = True
        titulo = 'Gestores'
    #Si no tiene rol asignada indicara error
    else:
        messages.error(request, 'No cuenta con permisos para acceder a esta sección.')
        return redirect('login')
    
    #Filtrado para admins
    query = request.GET.get('query', '').strip()
    if query and create:  # Solo si es admin
        gestores = gestores.filter(
            Q(nombre__icontains=query) | Q(apellido__icontains=query) | 
            Q(email__icontains=query) | Q(rut__icontains=query)
        )
    
    # ✅ ESTE ES EL RETURN QUE FALTABA - SIEMPRE SE DEBE EJECUTAR
    data = {
        'gestores': gestores,
        'query': query,
        'create': create,
        'title': titulo
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
        try:
            #Guardamos el nombre en una variable para el mensaje
            nombre = f'{gestor.nombre} {gestor.apellido}'
            
            # Buscar y eliminar usuario asociado
            username = f'{gestor.nombre.lower()}.{gestor.apellido.lower()}'
            #Buscar el usuario
            user = User.objects.filter(username=username).first()
            if user:
                user.delete()
                messages.success(request, f'Usuario {nombre} ha sido eliminado correctamente')
            else:
                messages.warning(request, f'Usuario {nombre} no encontrado')

            # Eliminar el gestor
            gestor.delete()
            messages.success(request, f'Gestor {nombre} ha sido eliminado correctamente')
            return redirect('gestores')
        
        except Exception as error:
            messages.error(request, f'Error al eliminar gestor: {error}')
            return redirect('gestores')
    
    # Si no es POST, redirigir a gestores
    return redirect('gestores')


#* CRUD EXPEDIENTES *#

@login_required(login_url='login')
def listaExpedientes(request):
    #Verifica roles
    if es_gestor(request.user):
        #Gestor vera solo expedientes asignados a el
        try:
            gestor_usuario = Gestor.objects.get(
                nombre=request.user.first_name, 
                apellido= request.user.last_name
            )
            expedientes = Expediente.objects.filter(gestor = gestor_usuario)
            create = False
            titulo = 'Mis expedientes asignados'
        except Gestor.DoesNotExist:
            expedientes = Expediente.objects.none()
            create = False
            titulo = 'Expedientes'
            messages.warning(request, 'No se encontro su perfil de gestor')
    #Si es admin podra crear expediente, ver expedientes, editarlos y eliminarlos
    elif es_admin(request.user):
        expedientes = Expediente.objects.all()
        create = True
        titulo = 'Gestion de Expedientes'
    #Si no cuenta con ningun rol arrojara mensaje y sera redirigido a login 
    else:
        messages.error(request, 'No cuenta con permisos para acceder a esta seccion')
        return redirect('login')

    #Filtro para busquedas
    query = request.GET.get('query', '').strip()
    if query:
            expedientes = expedientes.filter(
            Q(titulo__icontains=query) | Q(tipo_pension__icontains=query)
            |Q(gestor__nombre__icontains=query) | Q(gestor__apellido__icontains=query)
        )
    #Informacion de fecha actual para comparar vencimientos
    today = date.today()
    data = {
        'expedientes': expedientes,
        'query':query,
        'create':create,
        'title': titulo,
        'today': today
        }
    return render(request, 'expedientes/expedientes.html', data)    



@login_required(login_url='login')
@user_passes_test(es_admin)
def crearExpediente(request):
    """Vista para crear expediente - Solo administradores"""
    
    if request.method == 'POST':
        form = ExpedienteForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                expediente = form.save()
                messages.success(request, f'Expediente "{expediente.titulo}" creado exitosamente')
                return redirect('expedientes')
            except Exception as error:
                messages.error(request, f'Error al crear expediente: {error}')
        else:
            messages.error(request, 'Corrija los errores en el formulario')
    else:
        form = ExpedienteForm()
        
    data = {
        'titulo': 'Crear Expediente',
        'form': form
    }
    return render(request, 'expedientes/createExpediente.html', data)



@login_required(login_url='login')
def detalleExpediente(request, id):
    """Vista detalle de expediente - Admin y Gestor pueden ver"""
    expediente = get_object_or_404(Expediente, id=id)
    
    # Verificar permisos
    if es_gestor(request.user):
        # Gestor solo puede ver expedientes asignados a él
        try:
            gestor_obj = Gestor.objects.get(
                nombre=request.user.first_name,
                apellido=request.user.last_name
            )
            if expediente.gestor != gestor_obj:
                messages.error(request, 'No tiene permisos para ver este expediente')
                return redirect('expedientes')
        except Gestor.DoesNotExist:
            messages.error(request, 'No se encontró su perfil de gestor')
            return redirect('expedientes')
    elif not es_admin(request.user):
        messages.error(request, 'No tiene permisos para acceder a esta sección')
        return redirect('login')
    
    # Información adicional para el template
    hoy = date.today()
    dias_para_vencer = (expediente.fecha_vencimiento - hoy).days if expediente.fecha_vencimiento else None
    
    data = {
        'expediente': expediente,
        'title': f'Detalle - {expediente.titulo}',
        'puede_editar': es_admin(request.user),
        'puede_eliminar': es_admin(request.user),
        'today': hoy,
        'dias_para_vencer': dias_para_vencer,
        'vencido': expediente.fecha_vencimiento <= hoy if expediente.fecha_vencimiento else False
    }
    return render(request, 'expedientes/detalle.html', data)


@login_required(login_url='login')
@user_passes_test(es_admin)  # Solo Admin puede editar
def editarExpediente(request, id):
    #El expediente solo podra ser eliminado por el Admin
    expediente = get_object_or_404(Expediente, id=id)
    #Si es post, procesa el formulario
    if request.method == 'POST':
        #Recibe los datos, incluyendo archivos e instancia a expediente
        form = ExpedienteForm(request.POST, request.FILES, instance=expediente)
        if form.is_valid():
            try: #Cuando el formato es valido lo guarda y maneja la respuesta contraria con except
                expediente_actualizado = form.save()
                messages.success(request, f'Expediente "{expediente_actualizado.titulo}" actualizado exitosamente')
                return redirect('expedientes')
            except Exception as error:
                messages.error(request, f'Error al actualizar expediente: {error}')
        else:
            # Mostrar errores específicos del formulario
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field}: {error}')
    else:
        form = ExpedienteForm(instance=expediente)
    
    data = {
        'form': form,
        'expediente': expediente,
        'title': f'Editar - {expediente.titulo}',
        'action': 'editar',
        'gestores': Gestor.objects.all()  # Para el select del gestor
    }
    return render(request, 'expedientes/form.html', data)


@login_required(login_url='login')
@user_passes_test(es_admin)  # Solo Admin puede eliminar
def eliminarExpediente(request, id):
    """Eliminar expediente - Solo Administradores"""
    expediente = get_object_or_404(Expediente, id=id)
    
    if request.method == 'POST':
        try:
            titulo_expediente = expediente.titulo
            gestor_nombre = f"{expediente.gestor.nombre} {expediente.gestor.apellido}"
            
            # Eliminar archivo si existe
            if expediente.documentos:
                try:
                    expediente.documentos.delete()
                except:
                    pass  # Si no se puede eliminar el archivo, continuar
            
            expediente.delete()
            messages.success(request, f'Expediente "{titulo_expediente}" de {gestor_nombre} eliminado exitosamente')
        except Exception as error:
            messages.error(request, f'Error al eliminar expediente: {error}')
        
        return redirect('expedientes')
    
    # Si es GET, mostrar página de confirmación
    data = {
        'expediente': expediente,
        'title': f'Eliminar - {expediente.titulo}'
    }
    return render(request, 'expedientes/confirmar_eliminar.html', data)