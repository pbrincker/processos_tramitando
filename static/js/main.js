document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'))
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl)
    });

    // Format currency inputs
    const valorEstimadoInput = document.querySelector('input[name="valor_estimado"]');
    if (valorEstimadoInput) {
        valorEstimadoInput.addEventListener('input', function(e) {
            let value = e.target.value.replace(/\D/g, '');
            value = (value/100).toFixed(2);
            e.target.value = value;
        });
    }

    // Add date picker polyfill for browsers that don't support input[type="date"]
    const dateInputs = document.querySelectorAll('input[type="date"]');
    dateInputs.forEach(input => {
        if (input.type !== 'date') {
            input.setAttribute('placeholder', 'DD/MM/YYYY');
        }
    });
});
