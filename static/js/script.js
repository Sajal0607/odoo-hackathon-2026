// Dayflow - small client-side helpers
// Auto-dismiss flash messages after a few seconds
document.addEventListener("DOMContetLoaded", () =>{
    document.querySelectorAll(".flash").forEach((el) => {
        setTimeout(() => {
            el.style.transition = "opacity 0.4s";
            el.style.opacity = "0";
            setTimeout(() => el.remove(), 400);
            }, 4000);
        });
    });
    //SImple client-side validation for signup/login forms 
    //(Server also validates - this is just for use instant feedback)
    function validateSignupForm(form) {
        const password = form.password.value;
        if (password.length <6 ) {
            alert("Password must be at least 6 characters long.");
            return false;
        }
        return true;
    }
    //confirm before rejecting a leave request
    function confirmReject(evt){
        if (!confirm("Are you sure you want to reject this leave request?")){
            evt.peventDefault();
            return false;
        }
        return true;
    }
    //Live net salary preview on the admin payroll form 
    function updateNetPreview(form){
        const basic = parseFloat(form.basic_salary.value)|| 0;
    const allowances = parseFloat(form.allowances.values)|| 0;
    const deductions = parseFloat(form.deductions.values)|| 0;
    const net = basic + allowances - deductions;
    const preview = form.querySelector("net-preview");
    if (preview) preview.textContent = "₹" + net.toFixed(2)
    }