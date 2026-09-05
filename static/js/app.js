/**
 * Assisted-Living Facility Operational Communication System - Client-side Controller
 */

document.addEventListener('DOMContentLoaded', () => {
    // 1. Interactive Medical Boundary Warning on Question Input
    const questionInput = document.getElementById('questionTextInput');
    const medicalWarningBox = document.getElementById('medicalWarningBox');

    const MEDICAL_TERMS = [
        'medication', 'medicine', 'tylenol', 'paracetamol', 'fever', 'dose', 'dosage',
        'infection', 'diagnos', 'treatment', 'pill', 'antibiotic', 'blood pressure',
        'condition', 'cure', 'doctor say', 'sick', 'illness'
    ];

    if (questionInput && medicalWarningBox) {
        questionInput.addEventListener('input', (e) => {
            const val = e.target.value.toLowerCase();
            const detected = MEDICAL_TERMS.filter(term => val.includes(term));
            if (detected.length > 0) {
                medicalWarningBox.style.display = 'block';
                medicalWarningBox.innerHTML = `
                    <strong>⚠️ Non-Medical Boundary Alert:</strong>
                    Your inquiry contains clinical or medical terms (<em>${detected.join(', ')}</em>). 
                    This system provides <strong>operational support only</strong>. 
                    If submitted, this inquiry will be redirected to nursing staff rather than processed as an operational question.
                `;
            } else {
                medicalWarningBox.style.display = 'none';
            }
        });
    }

    // 2. User Quick-Switch Handler
    const userSwitcher = document.getElementById('userSwitcher');
    if (userSwitcher) {
        userSwitcher.addEventListener('change', (e) => {
            const username = e.target.value;
            if (username) {
                window.location.href = `/switch_user/${username}`;
            }
        });
    }

    // 3. Modal Helpers
    window.openModal = function(modalId) {
        const modal = document.getElementById(modalId);
        if (modal) modal.classList.add('active');
    };

    window.closeModal = function(modalId) {
        const modal = document.getElementById(modalId);
        if (modal) modal.classList.remove('active');
    };

    // Close modal on overlay click
    document.querySelectorAll('.modal-overlay').forEach(overlay => {
        overlay.addEventListener('click', (e) => {
            if (e.target === overlay) {
                overlay.classList.remove('active');
            }
        });
    });
});
