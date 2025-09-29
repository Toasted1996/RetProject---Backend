// Función para confirmar eliminación de expedientes
function confirmarEliminacionExpediente(expedienteId, tituloExpediente) {
    Swal.fire({
        title: '¿Eliminar Expediente?',
        html: `<strong>${tituloExpediente}</strong><br><small class="text-muted">Esta acción no se puede deshacer</small>`,
        icon: 'warning',
        showCancelButton: true,
        confirmButtonColor: '#dc3545',
        cancelButtonColor: '#6c757d',
        confirmButtonText: '<i class="fas fa-trash-alt me-2"></i>Sí, Eliminar',
        cancelButtonText: '<i class="fas fa-ban me-2"></i>Cancelar',
        buttonsStyling: false,
        customClass: {
            confirmButton: 'btn btn-danger px-4 me-3',
            cancelButton: 'btn btn-outline-secondary px-4',
            actions: 'd-flex justify-content-center gap-3'
        }
    }).then((result) => {
        if (result.isConfirmed) {
            // Crear formulario para POST
            const form = document.createElement('form');
            form.method = 'POST';
            form.action = `/expedientes/eliminar/${expedienteId}/`;
            
            // Token CSRF
            const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
            const csrfInput = document.createElement('input');
            csrfInput.type = 'hidden';
            csrfInput.name = 'csrfmiddlewaretoken';
            csrfInput.value = csrfToken;
            form.appendChild(csrfInput);
            
            // Enviar
            document.body.appendChild(form);
            form.submit();
        }
    });
}

// Validación de formulario
document.addEventListener('DOMContentLoaded', function() {
    // Validación Bootstrap
    const forms = document.querySelectorAll('.needs-validation');
    
    Array.from(forms).forEach(form => {
        form.addEventListener('submit', event => {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            form.classList.add('was-validated');
        });
    });
    
    // Auto-focus en primer campo
    const firstInput = document.querySelector('input:not([type="hidden"]), select, textarea');
    if (firstInput) {
        firstInput.focus();
    }
});