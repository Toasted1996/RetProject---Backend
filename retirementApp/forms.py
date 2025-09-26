#importaremos timezone para validar fechas
from datetime import timezone
from django import forms
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
            #Elimina puntos y guiones
            rut = rut.replace('.','').replace('-','')
            if len(rut) < 8 or len(rut) > 10:
                raise forms.ValidationError('El rut debe tener entre 8 y 10 caracteres')
            return rut
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
        
