Cómo funciona el sistema ⚙️
El sistema se basa en un flujo de trabajo claro y en un sistema de roles para controlar el acceso:

Creación de Expediente: Un usuario con rol de Gestor crea un nuevo expediente en el sistema, registrando datos clave como el tipo de pensión (Vejez, Invalidez, etc.) y su ID en el sistema de workflow externo (WF). Si es necesario, el gestor puede adjuntar un archivo (un documento clave) al expediente.

Generación de la Auditoría: De forma automática, el sistema identifica el tipo de pensión y genera una lista de chequeo específica para ese caso. Esta lista se llena con los requisitos y documentos que deben ser verificados, como el certificado de cotizaciones o informes médicos.

Proceso de Auditoría: El gestor asignado revisa el expediente y utiliza la lista de chequeo para marcar cada ítem como "validado" o "no validado". También puede añadir comentarios para explicar cualquier observación. El sistema podría mostrar visualmente el progreso de la auditoría.

Actualización de Estado: A medida que el gestor avanza, el estado del expediente se actualiza (por ejemplo, de "Pendiente" a "En Revisión"). Una vez que se completan todos los ítems, el sistema puede marcar el expediente como "Completo" o "Con Observaciones", dependiendo de los resultados.

Visualización y Roles: La visibilidad del sistema depende del rol del usuario que inicia sesión.

El Gestor solo ve y gestiona los expedientes que tiene asignados, y su dashboard le muestra su carga de trabajo.

El Administrador tiene una vista completa de todos los expedientes y puede acceder a reportes de calidad que muestran los errores más comunes, el rendimiento de los gestores y las métricas de eficiencia. Esto le permite tomar decisiones informadas para mejorar los procesos.



1. Gestor
Este modelo representaría a los usuarios del sistema. Puedes vincularlo directamente al modelo de usuario integrado de Django, lo que te permite aprovechar la autenticación y los permisos sin tener que crear un modelo desde cero.

Campos:

usuario: Una relación uno a uno (OneToOneField) con el modelo User de Django. Esto te da acceso al nombre de usuario, contraseña, email y otros campos del usuario estándar.

2. Expediente
Este modelo es para cada caso de pensión. Es el elemento central del cual se derivan las auditorías.

Campos:

id_wf: Un campo de texto (CharField) para el identificador del sistema de workflow.

titulo: Un campo de texto (CharField) para un nombre descriptivo.

tipo_pension: Un campo de texto (CharField) para el tipo de pensión (ej. "Vejez").

fecha_inicio_proceso: Un campo de fecha (DateField).

fecha_vencimiento: Un campo de fecha (DateField).

estado_general: Un campo de texto (CharField) con opciones predefinidas (ej. "Pendiente", "En revisión", "Completo").

gestor_asignado: Una clave foránea (ForeignKey) al modelo Gestor.

3. ListaChequeo
Este modelo representa una plantilla de auditoría, como la lista de requisitos para un tipo de pensión específico.

Campos:

nombre: Un campo de texto (CharField).

descripcion: Un campo de texto (TextField).

4. ItemChequeo
Este modelo representa cada punto individual dentro de una plantilla de auditoría.

Campos:

lista_chequeo: Una clave foránea (ForeignKey) al modelo ListaChequeo.

descripcion: Un campo de texto (TextField) para el texto del ítem.

es_critico: Un campo booleano (BooleanField) para marcar si el ítem es obligatorio.

5. AuditoriaExpediente
Este modelo es el registro de una auditoría realizada a un expediente.

Campos:

expediente: Una clave foránea (ForeignKey) al modelo Expediente.

lista_chequeo: Una clave foránea (ForeignKey) al modelo ListaChequeo.

fecha_auditoria: Un campo de fecha y hora (DateTimeField).

calificacion_auditoria: Un campo numérico (FloatField) para la puntuación.

observaciones: Un campo de texto (TextField).

6. EstadoItemAuditoria
Este modelo registra el resultado de la revisión de cada ítem en una auditoría específica.

Campos:

auditoria_expediente: Una clave foránea (ForeignKey) al modelo AuditoriaExpediente.

item_chequeo: Una clave foránea (ForeignKey) al modelo ItemChequeo.

estado_validacion: Un campo booleano (BooleanField).

comentarios: Un campo de texto (TextField).

Estos seis modelos cubren todas las funcionalidades clave para tu sistema de auditoría. Las relaciones entre ellos permiten un seguimiento completo y detallado de cada expediente, desde su asignación hasta la revisión final.







explicame como el usuario se crearia


El usuario se crearía de dos formas principales en tu sistema, dependiendo de quién lo haga: de forma manual por un administrador, o, si lo deseas, a través de un formulario web que tú crees.

1. Creación por un Administrador (Método Recomendado)
Este método es el más seguro y directo para un sistema de gestión interna.

Acceso al Panel de Administración: Un usuario con el rol de Administrador accede al panel de administración de Django (/admin).

Creación del Usuario: El administrador navega a la sección de "Usuarios" y hace clic en "Añadir usuario".

Llenado de Datos: Llena los campos obligatorios como nombre de usuario y contraseña.

Asignación de Rol: El administrador navega a la sección de "Grupos" en el mismo formulario y asigna el rol correspondiente, como "Gestor" o "Administrador". Esto le da al nuevo usuario los permisos necesarios para trabajar.

Creación del Modelo Gestor: Si tienes un modelo Gestor separado, el administrador podría necesitar crear una instancia de ese modelo y asociarla al usuario que acaba de crear.

2. Creación a Través de un Formulario Web
Esta opción requiere más trabajo de desarrollo, pero podría ser útil si quisieras permitir que un usuario se "registre" a sí mismo.

Formulario de Registro: Tendrías que crear una vista y una plantilla HTML con un formulario de registro.

Lógica en la Vista: Cuando el usuario envíe el formulario, la vista validará los datos y creará una nueva instancia del modelo User de Django.

Asignación de Rol por Defecto: En este caso, tendrías que asignar automáticamente al nuevo usuario a un rol por defecto, como "Gestor". Esto se hace con código Python después de que el usuario ha sido guardado en la base de datos.

Redirección: Finalmente, el usuario es redirigido a una página de confirmación o de inicio de sesión.

La primera opción es la más apropiada para tu proyecto de auditoría, ya que los usuarios son parte de una institución y sus roles son predefinidos. Esto te da un control total y elimina la necesidad de desarrollar una interfaz de registro.

<img width="1053" height="726" alt="image" src="https://github.com/user-attachments/assets/b90fa3d3-1f75-46f5-bc13-2cc945eb2cb9" />
