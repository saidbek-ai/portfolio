// =============================================================
// 1. DEBOUNCE FUNCTION
//==============================================================
const debounce = (func, delay) => {
    let timeoutId;
    return function(...args) {
        clearTimeout(timeoutId); // Cancel previous scheduled call
        timeoutId = setTimeout(() => {
            func.apply(this, args); // Schedule the current call
        }, delay);
    };
};

// =============================================================
// 2. GLOBAL TOAST FUNCTION
// =============================================================
window.toast = null;
let currentTheme = localStorage.getItem("theme") || "light";

function initializeNotyf(isDarkMode) {
  // Light Mode: Tailwind slate-700
  // Dark Mode: Tailwind slate-500
  const neutralBgColor = isDarkMode ? '#64748B' : '#334155';
  
  window.toast = new Notyf({
    duration: 2500, 
    position: {x: "right", y: "bottom"},
    dismissible:true,
    types: [
      {
        type: "success",
        background: neutralBgColor,
        icon: { className: 'notyf__icon--success', tagName: 'i' }
      },
      {
        type: "error",
        background: neutralBgColor,
        icon: { className: 'notyf__icon--error', tagName: 'i' }
      },
      {
        type: "info",
        background: neutralBgColor,
      },
    ]
  })
}

// ============================================================
// 3. DOMContentLoaded LISTENER for theme setter(dark/light)
// =============================================================
document.addEventListener("DOMContentLoaded", () => {
    // --- Theme Logic (This is correctly inside DOMContentLoaded) ---
    const savedTheme = localStorage.getItem("theme");
    const prefersDark = window.matchMedia(
        "(prefers-color-scheme: dark)"
    ).matches;
    const theme = savedTheme || (prefersDark ? "dark" : "light");

    if (theme === "dark") {
        document.documentElement.classList.add("dark");
    } else {
        document.documentElement.classList.remove("dark");
    }

    initializeNotyf(savedTheme === "dark")

});