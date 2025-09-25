from django.db import models
#Importamos validadores para campos de rut y calificaciones
from django.core.validators import MinValueValidator, MaxValueValidator, RegexValidator

# Create your models here.

#Modelo para los gestores de pension
class Gestor(models.Model):
    #Validamos el formato del RUT chileno con una expresion regular
    rut = models.CharField(max_length=12, unique=True, validators=[RegexValidator(regex=r'^\d{1,2}\d{3}\d{3}-[\dkK]$', message='El RUT debe tener el formato 12345678-9')])
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)
    email = models.EmailField()
    
    def __str__(self):
        return f'{self.nombre} {self.apellido}'
    
    class Meta:
        db_table = 'gestores'

#Constante estado - expedientes
EXPEDIENTE_CHOICES = [
    ('activo', 'Activo'),
    ('inactivo', 'Inactivo'),
]



#Modelo para los expedientes de pension
class Expediente(models.Model):
    titulo = models.CharField(max_length=200)
    tipo_pension = models.CharField(max_length=100)
    #fecha inicio auto_now_add para que se asigne la fecha cuando se crea el objeto
    fecha_inicio = models.DateField(auto_now_add =True)
    fecha_vencimiento = models.DateField()
    documentos = models.FileField(upload_to='documentos/')
    estado_expediente = models.CharField(max_length=50, choices = EXPEDIENTE_CHOICES) #Pueden ser opciones predefinidas
    
    gestor = models.ForeignKey(Gestor, on_delete=models.CASCADE)
    
    def __str__(self):
        return f'Expediente {self.id} {self.titulo}'
    
    class Meta:
        db_table = 'expedientes'

#Modelo para las listas de chequeo
class ListaChequeo(models.Model):
    nombre = models.CharField(max_length=200)
    descripcion = models.TextField(max_length=500)
    
    def __str__(self):
        return self.nombre
    
    class Meta:
        db_table = 'lista_chequeo'

#Modelo para los items de la lista de chequeo        
class ItemChequeo(models.Model):
    lista_chequeo = models.ForeignKey(ListaChequeo, on_delete=models.CASCADE)
    descripcion = models.CharField(max_length=300)
    is_critical = models.BooleanField(default=False)
    
    def __str__(self):
        return self.descripcion
    
    class Meta:
        db_table = 'item_chequeo'


#Modelo para registrar las auditorias de los expedientes
class AuditoriaExpediente(models.Model):
    expediente = models.ForeignKey(Expediente,on_delete=models.CASCADE)
    lista_chequeo = models.ForeignKey(ListaChequeo, on_delete=models.CASCADE)
    fecha_auditoria = models.DateField(auto_now_add=True)
    calificacion = models.IntegerField(default=0,validators=[MinValueValidator(0), MaxValueValidator(10)], help_text ='Calificacion de 0 a 10')
    observaciones = models.TextField(max_length=500, blank=True, null=True)
    
    def __str__(self):
        return f'Auditoria {self.id} - Expediente {self.expediente.id} - {self.fecha_auditoria} - {self.calificacion}'
    
    class Meta:
        db_table = 'auditoria_expediente'

#Constante estado - items auditoria
ITEMS_AUDITORIA_CHOICES = [
    ('cumple', 'Cumple'),
    ('no_cumple', 'No Cumple'),
]


#Metodo para registrar los items de auditoria
class ItemAuditoria(models.Model):
    auditoria_expediente = models.ForeignKey(AuditoriaExpediente, on_delete=models.CASCADE)
    item_chequeo = models.ForeignKey(ItemChequeo, on_delete=models.CASCADE)
    estado_auditoria = models.CharField(max_length=50, choices = ITEMS_AUDITORIA_CHOICES)
    observaciones = models.TextField(max_length=500, blank=True, null=True)
    
    def __str__(self):
        return f'Item Auditoria {self.id} - Auditoria {self.auditoria_expediente.id} - Item {self.item_chequeo.id} - {self.estado_auditoria}'

    class Meta:
        db_table = 'item_auditoria'