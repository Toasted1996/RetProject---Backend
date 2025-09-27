#importaremos timezone para validar fechas
from datetime import timezone
#Importamos forms de django
from django import forms
#Importamos modelos y fomularios de autenticacion para LOGIN y REGISTRO
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User, Group
#Importamos modelos a usar 
from .models import Gestor, Expediente

#Formulario para el modelo gestor con validaciones para rut
class GestorForm(forms.ModelForm):
    class Meta:
        model = Gestor
        fields = ['rut','nombre', 'apellido', 'email']
        widgets = {
            'rut': forms.TextInput(attrs={'class':'form-control', 'placeholder':'Ingrese RUT'}),
            'nombre': forms.TextInput(attrs={'class': 'form-control', 'placeholder':'Ingrese nombre'}),
            'apellido': forms.TextInput(attrs={'class': 'form-control', 'placeholder':'Ingrese apellido'}),
            'email': forms.EmailInput(attrs={'class':'form-control', 'placeholder':'Ingrese email'})
        }
        
    #validacion adicional para el campo RUT
    def clean_rut(self):
        rut = self.cleaned_data.get('rut')
        if rut:
            # Limpiamos el RUT (elimina puntos y espacios, pero mantiene el guión)
            rut_limpio = rut.replace('.', '').replace(' ', '').strip()
            
            # Verificamos que tenga el formato correcto
            if not rut_limpio:
                raise forms.ValidationError('El campo RUT es obligatorio')
                
            # Si no tiene guión, lo agregamos en la posición correcta
            if '-' not in rut_limpio:
                if len(rut_limpio) >= 8:
                    # Agregamos el guión antes del último dígito
                    rut_limpio = rut_limpio[:-1] + '-' + rut_limpio[-1]
                else:
                    raise forms.ValidationError('El RUT debe tener al menos 8 dígitos')
            
            # Validamos la longitud final (con guión)
            if len(rut_limpio) < 9 or len(rut_limpio) > 12:
                raise forms.ValidationError('El RUT debe tener el formato 12345678-9')
            
            return rut_limpio
        
        raise forms.ValidationError('El campo RUT es obligatorio')
    

#Formulario Expediente
class ExpedienteForm(forms.ModelForm):
    class Meta:
        model = Expediente
        fields = '__all__'
        widgets = {
            'titulo': forms.TextInput(attrs={'class':'form-control', 'placeholder':'Ingrese titulo'}),
            'tipo_pension': forms.TextInput(attrs={'class':'form-control', 'placeholder':'Ingrese tipo de pension'}),
            'fecha_vencimiento': forms.DateInput(attrs={'class':'form-control', 'type':'date'}),
            'documentos': forms.ClearableFileInput(attrs={'class':'form-control'}),
            'estado_expediente': forms.Select(attrs={'class':'form-control'}),
            'gestor': forms.Select(attrs={'class':'form-control'})
        }
        
        #Validacion para que fecha de vencimiento sea > a fecha actual
    def clean_fecha_vencimiento(self):
        fecha_vencimiento = self.cleaned_data.get('fecha_vencimiento')
        if fecha_vencimiento and fecha_vencimiento <= timezone.now().date():
            raise forms.ValidationError('La fecha de vencimiento debe ser futura')
        return fecha_vencimiento


#Formulario integrado para LOGIN customizado usando AuthenticationForm        
class CustomLoginForm(AuthenticationForm): #AuthenticationForm ya tiene una logica de validacion
    username = forms.CharField(widget=forms.TextInput(attrs={'class':'form-control', 'placeholder': 'Usuario','autofocus': True}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class':'form-control', 'placeholder':'Contraseña'}))


#Formulario integrado para REGISTRO usando UserCreationForm
class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={'class':'form-control', 'placeholder':'nombre@dominio.com'}))
    nombre = forms.CharField(max_length = 30, required = True, widget= forms.TextInput(attrs={'class':'form-control', 'placeholder': 'Nombre'}))
    apellido = forms.CharField(max_length = 30, required = True, widget=forms.TextInput(attrs={'class':'form-control', 'placeholder':'Apellido'}))
    rol = forms.ModelChoiceField(
        queryset = Group.objects.all(),
        required = True,
        help_text = 'Seleccione un rol para el usuario'
    )
    
    class Meta:
        model = User
        fields = ('username', 'nombre', 'apellido', 'email', 'password1', 'password2', 'rol')
        widgets = {
            'username':forms.TextInput(attrs={'class':'form-control', 'placeholder':'Usuario'}),
        }
    #Metodo para guardar al usuario y asignarle grupo segun rol
    def save_user(self, commit=True):
        #Guarda el usuario
        user = super().save(commit=False)
        #limpiamos los datos pasados
        user.email =self.cleaned_data['email']
        user.nombre = self.cleaned_data['nombre']
        user.apellido = self.cleaned_data['apellido']
        #Si commit es True, guarda el usuario
        if commit:
            user.save()
            #Asigna un grupo segun el rol seleccionado 
            rol = self.cleaned_data['rol']
            user.groups.add(rol)
            user.save()
        return user
            