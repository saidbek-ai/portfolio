document.addEventListener("DOMContentLoaded", () => {
  const toggleBtn = document.getElementById("socialToggle");
  const socialLinks = document.querySelectorAll(".social-link");
  const toggleIcon = document.getElementById("toggleIcon");
  const toggleClose = document.getElementById("toggleClose");
  let isOpen = false;
  console.log(connectionError);

  // Define the positions for the circular menu (adjust radius as needed)
  // Distance from center (radius) is approximately 80px
  const linkPositions = [
    // 1. GitHub: Straight up (270 degrees)
    { top: "-80px", left: "0px" },
    // 2. LinkedIn: Up and Left (225 degrees)
    { top: "-60px", left: "-60px" },
    // 3. X/Twitter: Straight Left (180 degrees)
    { top: "0px", left: "-80px" },
  ];

  toggleBtn.addEventListener("click", () => {
    isOpen = !isOpen;
    toggleBtn.classList.toggle("animate-bounce");
    toggleIcon.classList.toggle("hidden");
    toggleClose.classList.toggle("hidden");

    socialLinks.forEach((link, index) => {
      const { top, left } = linkPositions[index];

      if (isOpen) {
        // OPENING: Set position and make visible
        link.style.top = top;
        link.style.left = left;
        link.classList.remove("scale-0", "opacity-0");
        link.classList.add("scale-100", "opacity-100");
        toggleIcon.classList.add("hidden");
        // toggleClose.classList.remove("hidden");
      } else {
        // CLOSING: Return to center and hide
        link.style.top = "0px";
        link.style.left = "0px";
        link.classList.remove("scale-100", "opacity-100");
        link.classList.add("scale-0", "opacity-0");
        toggleIcon.classList.remove("hidden");
        // toggleClose.classList.add("hidden");
      }
    });
  });
});
