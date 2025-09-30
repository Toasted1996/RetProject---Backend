
// Function para confirmar la eliminacion de un gestor mediante SweetAlert2
function confirmarEliminacion(gestorId, nombreGestor) {
    Swal.fire({
        title: '¿Está seguro?',
        text: `¿Desea eliminar al gestor ${nombreGestor}?`,
        icon: 'warning',
        showCancelButton: true,
        confirmButtonColor: '#dc3545',
        cancelButtonColor: '#6c757d',
        confirmButtonText: 'Sí, eliminar',
        cancelButtonText: 'Cancelar',
        buttonStyling: false,
        customClass:{
            confirmButton : 'btn btn-danger me-2',
            cancelButton : 'btn btn-secondary',
            action : 'gap-3'
        },
        reverseButtons: true
    }).then((result) => {
        if (result.isConfirmed) {
            // Crear formulario para envío POST
            const form = document.createElement('form');
            form.method = 'POST';
            form.action = `/gestores/eliminar/${gestorId}/`;
            
            // Agregar token CSRF
            const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
            const csrfInput = document.createElement('input');
            csrfInput.type = 'hidden';
            csrfInput.name = 'csrfmiddlewaretoken';
            csrfInput.value = csrfToken;
            form.appendChild(csrfInput);
            
            // Agregar al DOM y enviar
            document.body.appendChild(form);
            form.submit();
        }
    });
}

// Function para confirmar la eliminacion de un expediente mediante SweetAlert2
function confirmarEliminacionExpediente(expedienteId, tituloExpediente) {
    Swal.fire({
        title: '¿Está seguro?',
        html: `
            <div class="text-start">
                <p class="mb-3">Esta acción eliminará permanentemente:</p>
                <div class="alert alert-warning mb-3">
                    <strong><i class="fas fa-folder me-2"></i>${tituloExpediente}</strong><br>
                    <small class="text-muted">ID: #${expedienteId}</small>
                </div>
                <div class="alert alert-danger mb-0">
                    <i class="fas fa-exclamation-triangle me-2"></i>
                    <strong>¡ATENCIÓN!</strong> Esta acción eliminará:
                    <ul class="mb-0 mt-2">
                        <li>Toda la información del expediente</li>
                        <li>Los documentos adjuntos (si los hay)</li>
                        <li>El historial asociado</li>
                    </ul>
                    <hr class="my-2">
                    <small><strong>Esta acción NO se puede deshacer</strong></small>
                </div>
            </div>
        `,
        icon: 'warning',
        showCancelButton: true,
        confirmButtonColor: '#dc3545',
        cancelButtonColor: '#6c757d',
        confirmButtonText: '<i class="fas fa-trash me-2"></i>Sí, eliminar',
        cancelButtonText: '<i class="fas fa-times me-2"></i>Cancelar',
        buttonStyling: false,
        customClass:{
            confirmButton : 'btn btn-danger me-2',
            cancelButton : 'btn btn-secondary',
            action : 'gap-3',
            popup: 'swal-wide'
        },
        reverseButtons: true,
        width: '600px'
    }).then((result) => {
        if (result.isConfirmed) {
            // Mostrar loading
            Swal.fire({
                title: 'Eliminando expediente...',
                text: 'Por favor espere mientras se elimina el expediente',
                icon: 'info',
                allowOutsideClick: false,
                allowEscapeKey: false,
                showConfirmButton: false,
                didOpen: () => {
                    Swal.showLoading();
                }
            });
            
            // Crear formulario para envío POST
            const form = document.createElement('form');
            form.method = 'POST';
            form.action = `/expedientes/eliminar/${expedienteId}/`;
            
            // Agregar token CSRF
            const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
            const csrfInput = document.createElement('input');
            csrfInput.type = 'hidden';
            csrfInput.name = 'csrfmiddlewaretoken';
            csrfInput.value = csrfToken;
            form.appendChild(csrfInput);
            
            // Agregar al DOM y enviar
            document.body.appendChild(form);
            form.submit();
        }
    });
}