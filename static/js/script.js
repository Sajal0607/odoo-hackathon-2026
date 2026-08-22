// Dayflow - small client-side helpers
document.addEventListener("DOMContentLoaded", () => {
    document.querySelectorAll(".flash").forEach((el) => {
        setTimeout(() => {
            el.style.transition = "opacity 0.4s";
            el.style.opacity = "0";
            setTimeout(() => el.remove(), 400);
        }, 4000);
    });
});

function validateSignupForm(form) {
    const password = form.password.value;
    if (password.length < 6) {
        alert("Password must be at least 6 characters long.");
        return false;
    }
    return true;
}

function confirmReject(evt) {
    if (!confirm("Are you sure you want to reject this leave request?")) {
        evt.preventDefault();
        return false;
    }
    return true;
}

function updateNetPreview(form) {
    const basic = parseFloat(form.basic_salary.value) || 0;
    const allowances = parseFloat(form.allowances.value) || 0;
    const deductions = parseFloat(form.deductions.value) || 0;
    const net = basic + allowances - deductions;
    const preview = form.querySelector(".net-preview");
    if (preview) preview.textContent = "₹" + net.toFixed(2);
}
