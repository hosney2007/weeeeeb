document.addEventListener("DOMContentLoaded", function () {

    document.querySelectorAll(".toast").forEach(function(toast){

        const close = toast.querySelector(".close-toast");

        close.addEventListener("click", function(){

            toast.style.opacity = "0";
            toast.style.transform = "translateX(120%)";

            setTimeout(function(){
                toast.remove();
            },300);

        });

        setTimeout(function(){

            toast.style.opacity = "0";
            toast.style.transform = "translateX(120%)";

            setTimeout(function(){
                toast.remove();
            },300);

        },3000);

    });

});






//scroll
const navbar = document.querySelector(".navbar");
if (document.body.scrollHeight <= window.innerHeight){
    navbar.classList.add("scrolled");
}
window.addEventListener("scroll", function () {
    const navbar = document.querySelector(".navbar");
    if (window.scrollY > 50){
        navbar.classList.add("scrolled");
    }else{
        navbar.classList.remove("scrolled")
    }

});
//coumter
const counters = document.querySelectorAll(".counter");
const counterObserver = new IntersectionObserver((entries) => {
    entries.forEach(entry =>{
        if (entry.isIntersecting){

            const counter = entry.target;
            const target = +counter.dataset.target;
            const symbol = counter.dataset.symbol || "";
            let current = 0;
            const increment = target /100;
            const updatecounter = () =>{
                if (current < target) {
                    current += increment;
                    counter.innerText = Math.ceil(current) + symbol;
                    requestAnimationFrame(updatecounter);

                } else {
                    counter.innerText = target + symbol;
                }
            };
            updatecounter();
            counterObserver.unobserve(counter);


        }
    });
});
counters.forEach( counter => counterObserver.observe(counter));







AOS.init({
    duration: 900,
    once: true,
    easing:"ease-in-out",
    offset: 100
})

//swiper
document.addEventListener("DOMContentLoaded", function () {

    new Swiper(".successSwiper", {
        slidesPerView: 3,
        spaceBetween: 30,
        loop: true,
        autoplay: {
            delay: 3500
        },
        pagination:{
            el: ".swiper-pagination",
            clickable: true,
        },
        breakpoints: {
            0: { slidesPerView: 1 },
            768: { slidesPerView: 2 },
            1200: { slidesPerView: 3 }
        }
    });

});


//view image

function openImage(src){
    document.getElementById("imageModal").style.display = "block";
    document.getElementById("modalImg").src = src;
}

function closeImage(){
    document.getElementById("imageModal").style.display = "none";
}


// ===============================
// Booking options


const exam = document.getElementById("exam");

const offline = document.querySelector('input[value="offline"]');
const online = document.querySelector('input[value="online"]');

const branchBox = document.getElementById("branch-box");
const branch = document.getElementById("branch");

const scheduleBox = document.getElementById("schedule-box");
const schedule = document.getElementById("schedule");


// ===============================
// Load available groups
// ===============================

async function loadSchedules() {
    const examValue = exam.value;

    const modeValue = document.querySelector(
        'input[name="mode"]:checked'
    )?.value;

    const branchValue = branch.value;


    // لو لسه مفيش Exam أو Mode
    if (!examValue || !modeValue) {

        scheduleBox.style.display = "none";

        schedule.innerHTML = `
            <option value="">Choose Group</option>
        `;

        return;
    }


    // ===============================
    // ONLINE
    // ===============================

    if (modeValue === "online") {

        branchBox.style.display = "none";

    }


    // ===============================
    // OFFLINE
    // ===============================

    if (modeValue === "offline") {

        branchBox.style.display = "flex";

        // لازم يختار الفرع
        if (!branchValue) {

            scheduleBox.style.display = "none";

            schedule.innerHTML = `
                <option value="">Choose Group</option>
            `;

            return;
        }

    }


    // ===============================
    // Get groups from Flask
    // ===============================

    let url =
        `/booking/schedules?course_id=${examValue}&mode=${modeValue}`;


    if (modeValue === "offline") {

        url += `&branch_id=${branchValue}`;

    }


    const response = await fetch(url);

    const schedules = await response.json();


    // نمسح القديم
    schedule.innerHTML = `
        <option value="">Choose Group</option>
    `;


    // نعرض الجروبات
    schedules.forEach(item => {

        const option = document.createElement("option");

        option.value = item.id;

        option.textContent = item.text
  
        schedule.appendChild(option);

    });


    scheduleBox.style.display = "flex";
}


// ===============================
// Events
// ===============================
// هذا الكود خاص بصفحة الحجز فقط، وعناصره (exam, offline...) مش موجودة
// في باقي صفحات الموقع. من غير الشرط ده كان بيحصل كراش في الكونسول
// في كل صفحة غير صفحة الحجز، وده كان بيمنع تعريف دالة copyText اللي
// بتستخدمها صفحة الدفع (payment.html) في زرار النسخ.
if (exam && offline && online && branchBox && branch && scheduleBox && schedule) {

    exam.addEventListener("change", loadSchedules);

    offline.addEventListener("change", loadSchedules);

    online.addEventListener("change", loadSchedules);

    branch.addEventListener("change", loadSchedules);

}



function copyText(id) {
    const text = document.getElementById(id).innerText;

    const input = document.createElement("textarea");
    input.value = text;

    document.body.appendChild(input);

    input.select();
    document.execCommand("copy");

    document.body.removeChild(input);

    alert("Copied Successfully");
}





