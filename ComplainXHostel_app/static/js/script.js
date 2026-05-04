// Modal open
function openModal() {
    const modal = document.getElementById("modal");
    if (modal) {
        modal.style.display = "flex";
    }
}

// Modal close
function closeModal() {
    const modal = document.getElementById("modal");
    if (modal) {
        modal.style.display = "none";
    }
}

// Page load effect
document.addEventListener("DOMContentLoaded", function () {

    document.body.style.opacity = 0;
    document.body.style.transition = "0.4s ease-in-out";

    setTimeout(() => {
        document.body.style.opacity = 1;
    }, 50);

});