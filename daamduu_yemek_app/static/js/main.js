// Navigation
let nav = document.querySelector(".navigation-wrap");
window.onscroll = function () {
  if(document.documentElement.scrollTop > 20){
    nav.classList.add("scroll-on");
  }else{
    nav.classList.remove("scroll-on");
  }
}

// Nav hide
let navBar = document.querySelectorAll(".nav-link");
let navCollapse = document.querySelector(".navbar-collapse.collapse");
navBar.forEach(function(a){
  a.addEventListener("click", function(){
    navCollapse.classList.remove("show");
  })
})

// Counter Design  
document.addEventListener("DOMContentLoaded", () => {
  function counter(id, start, end, duration) {
    let obj = document.getElementById(id);
    if (!obj) return; // Skip if element doesn't exist
    
    let current = start,
        range = end - start,
        increment = end > start ? 1 : -1,
        step = Math.abs(Math.floor(duration / range)),
        timer = setInterval(() => {
          current += increment;
          obj.textContent = current;
          if (current == end) {
            clearInterval(timer);
          }
        }, step);
  }
  
  // Only initialize counters if we're on the home page
  const counterElements = ["count1", "count2", "count3", "count4"];
  const hasCounters = counterElements.some(id => document.getElementById(id));
  
  if (hasCounters) {
    counter("count1", 0, 1287, 3000);
    counter("count2", 100, 5786, 2500);
    counter("count3", 0, 1440, 3000);
    counter("count4", 0, 7110, 3000);
  }
});