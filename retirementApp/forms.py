#importaremos timezone para validar fechas
from datetime import datetime, timedelta, date, timezone
#Importamos forms de django
from django import forms
#Importamos modelos y fomularios de autenticacion para LOGIN y REGISTRO
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.models import User, Group
#Importamos modelos a usar 
from .models import Gestor, Expediente

#Formulario para el modelo gestor con validaciones para rut
#Formulario UNIFICADO - Crear Gestor + Usuario (Diseño basado en register)
class GestorForm(forms.ModelForm):
    # ✅ CAMPOS DE USUARIO (como en register)
    username = forms.EmailField(
        required=True,
        label='Email (Username)',
        widget=forms.EmailInput(attrs={'class':'form-control', 'placeholder':'email@dominio.com'})
    )
    password1 = forms.CharField(
        label='Contraseña',
        widget=forms.PasswordInput(attrs={'class':'form-control', 'placeholder':'Contraseña'})
    )
    password2 = forms.CharField(
        label='Confirmar Contraseña', 
        widget=forms.PasswordInput(attrs={'class':'form-control', 'placeholder':'Confirme la contraseña'})
    )
    
    class Meta:
        model = Gestor
        fields = ['rut', 'nombre', 'apellido', 'email']  # Campos específicos del gestor
        widgets = {
            'rut': forms.TextInput(attrs={'class':'form-control', 'placeholder':'12.345.678-9'}),
            'nombre': forms.TextInput(attrs={'class': 'form-control', 'placeholder':'Nombre'}),
            'apellido': forms.TextInput(attrs={'class': 'form-control', 'placeholder':'Apellido'}),
            'email': forms.EmailInput(attrs={'class':'form-control', 'placeholder':'Email de contacto'})
        }
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # ✅ Etiquetas claras
        self.fields['rut'].label = 'RUT'
        self.fields['nombre'].label = 'Nombre'
        self.fields['apellido'].label = 'Apellido'  
        self.fields['email'].label = 'Email de Contacto'
        
        # ✅ Help text como en register
        self.fields['username'].help_text = 'Este email se usará para hacer login'
        self.fields['email'].help_text = 'Email para comunicaciones del negocio'
        self.fields['password1'].help_text = 'Mínimo 8 caracteres'
        
    def clean_username(self):
        """Validar que el email no esté en uso"""
        username = self.cleaned_data.get('username')
        if username:
            if User.objects.filter(username=username).exists():
                raise forms.ValidationError('Ya existe un usuario con este email')
        return username
        
    def clean_password2(self):
        """Validar que las contraseñas coincidan (como en register)"""
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')
        
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError('Las contraseñas no coinciden')
        return password2
        
    def clean_rut(self):
        """Validación RUT (tu código existente)"""
        rut = self.cleaned_data.get('rut')
        if rut:
            rut_limpio = rut.replace('.', '').replace(' ', '').strip()
            
            if not rut_limpio:
                raise forms.ValidationError('El campo RUT es obligatorio')
                
            if '-' not in rut_limpio:
                if len(rut_limpio) >= 8:
                    rut_limpio = rut_limpio[:-1] + '-' + rut_limpio[-1]
                else:
                    raise forms.ValidationError('El RUT debe tener al menos 8 dígitos')
            
            if len(rut_limpio) < 9 or len(rut_limpio) > 12:
                raise forms.ValidationError('El RUT debe tener el formato 12345678-9')
            
            return rut_limpio
        
        raise forms.ValidationError('El campo RUT es obligatorio')

    def save_gestor(self, commit=True):
        """Método para guardar gestor + usuario (como save_user en register)"""
        # Crear el gestor
        gestor = super().save(commit=False)
        
        if commit:
            gestor.save()
            
            # Crear usuario asociado
            user = User.objects.create_user(
                username=self.cleaned_data['username'],
                email=self.cleaned_data['username'],
                password=self.cleaned_data['password1'],
                first_name=gestor.nombre,
                last_name=gestor.apellido
            )
            
            # Asignar al grupo Gestor
            grupo_gestor, created = Group.objects.get_or_create(name='Gestor')
            user.groups.add(grupo_gestor)
            user.save()
            
        return gestor




#Formulario Expediente
class ExpedienteForm(forms.ModelForm):
    # AGREGAR: Campo para extender plazo
    extender_plazo = forms.BooleanField(
        required=False,
        label='Extender plazo 30 días más',
        help_text='Marque para dar 30 días adicionales si el expediente está vencido',
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    
    class Meta:
        model = Expediente
        fields = [
            'titulo',
            'tipo_pension',
            'fecha_vencimiento',
            'documentos',
            'estado_expediente',
            'gestor'
        ]
        
        widgets = {
            'titulo': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': 'Ingrese título del expediente'
            }),
            'tipo_pension': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': 'Ej: Pensión de vejez, invalidez, etc.'
            }),
            'fecha_vencimiento': forms.DateInput(attrs={
                'class': 'form-control', 
                'type': 'date'
            }),
            'documentos': forms.ClearableFileInput(attrs={
                'class': 'form-control',
                'accept': '.pdf,.doc,.docx,.jpg,.png'
            }),
            'estado_expediente': forms.Select(attrs={
                'class': 'form-select'
            }),
            'gestor': forms.Select(attrs={
                'class': 'form-select'
            })
        }
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # LÓGICA MEJORADA PARA FECHAS
        if not self.instance.pk:
            # EXPEDIENTE NUEVO: fecha_inicio + 30 días
            fecha_default = date.today() + timedelta(days=30)
            self.fields['fecha_vencimiento'].initial = fecha_default
            # No mostrar opción de extender en expedientes nuevos
            self.fields['extender_plazo'].widget = forms.HiddenInput()
            
        else:
            # EXPEDIENTE EXISTENTE: verificar si está vencido
            fecha_actual = date.today()
            if self.instance.fecha_vencimiento <= fecha_actual:
                # Expediente vencido - mostrar opción de extender
                self.fields['extender_plazo'].widget.attrs.update({
                    'class': 'form-check-input',
                    'style': 'margin-top: 0.25rem;'
                })
                # Agregar mensaje informativo
                dias_vencido = (fecha_actual - self.instance.fecha_vencimiento).days
                self.fields['extender_plazo'].help_text = f'Expediente vencido hace {dias_vencido} días. Marque para extender 30 días más.'
            else:
                # Expediente vigente - ocultar opción de extender
                self.fields['extender_plazo'].widget = forms.HiddenInput()
        
        # Etiquetas en español
        self.fields['titulo'].label = 'Título del Expediente'
        self.fields['tipo_pension'].label = 'Tipo de Pensión'
        self.fields['fecha_vencimiento'].label = 'Fecha de Vencimiento'
        self.fields['documentos'].label = 'Documentos'
        self.fields['estado_expediente'].label = 'Estado del Expediente'
        self.fields['gestor'].label = 'Gestor Asignado'
        
        # Ordenar gestores
        self.fields['gestor'].queryset = Gestor.objects.all().order_by('nombre', 'apellido')
    
    # VALIDACIÓN ÚNICA Y MEJORADA
    def clean(self):
        cleaned_data = super().clean()
        fecha_vencimiento = cleaned_data.get('fecha_vencimiento')
        extender_plazo = cleaned_data.get('extender_plazo')
        
        # Si se marcó extender plazo
        if extender_plazo and self.instance.pk:
            # Calcular nueva fecha desde la fecha actual + 30 días
            nueva_fecha = date.today() + timedelta(days=30)
            cleaned_data['fecha_vencimiento'] = nueva_fecha
            
        # Validar que la fecha no sea pasada (solo para expedientes nuevos)
        elif fecha_vencimiento and not self.instance.pk:
            if fecha_vencimiento <= date.today():
                raise forms.ValidationError({
                    'fecha_vencimiento': 'La fecha de vencimiento debe ser futura'
                })
        
        return cleaned_data

    def save(self, commit=True):
        """Override save para manejar la extensión de plazo"""
        instance = super().save(commit=False)
        
        # Si se marcó extender plazo, actualizar la fecha
        if self.cleaned_data.get('extender_plazo') and self.instance.pk:
            instance.fecha_vencimiento = date.today() + timedelta(days=30)
            
        if commit:
            instance.save()
        return instance


#Formulario integrado para LOGIN customizado usando AuthenticationForm        
class CustomLoginForm(AuthenticationForm): #AuthenticationForm ya tiene una logica de validacion
    username = forms.CharField(widget=forms.TextInput(attrs={'class':'form-control', 'placeholder': 'Usuario','autofocus': True}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class':'form-control', 'placeholder':'Contraseña'}))



