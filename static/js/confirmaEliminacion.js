
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