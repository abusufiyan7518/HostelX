function toggleDropdown(id) {
    // Close all other open dropdowns first
    document.querySelectorAll('.dropdown-content').forEach(function(el) {
        if (el.id !== id) {
            el.classList.remove('show');
        }
    });

    // Toggle the clicked dropdown
    document.getElementById(id).classList.toggle('show');
}

// Close dropdown if user clicks outside
window.onclick = function(event) {
    if (!event.target.matches('.role-btn')) {
        document.querySelectorAll('.dropdown-content').forEach(function(el) {
            el.classList.remove('show');
        });
    }
}