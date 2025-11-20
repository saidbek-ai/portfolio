document.addEventListener("DOMContentLoaded", () => {
  const html = document.documentElement;

  // Mobile menu toggler
  const menuToggleBtn = document.getElementById("menuBtn");
  const mobileMenu = document.getElementById("mobileMenu");

  // Theme toggler
  const themeToggleBtn = document.getElementById("theme-toggle-btn");
  const sunIcon = document.getElementById("sun-icon");
  const moonIcon = document.getElementById("moon-icon");

  // User Profile dropdown
  const userMenuBtn = document.getElementById("userMenuBtn");
  const userMenu = document.getElementById("userMenu");

  // Theme setter in initial loading
  if (
    localStorage.getItem("theme") === "dark" ||
    (!localStorage.getItem("theme") &&
      window.matchMedia("(prefers-color-scheme: dark)").matches)
  ) {
    document.documentElement.classList.add("dark");
  } else {
    document.documentElement.classList.remove("dark");
  }

  // Function to handle the theme toggle.
  function toggleTheme() {
    const isDarkMode = html.classList.toggle("dark");
    localStorage.setItem("theme", isDarkMode ? "dark" : "light");

    // Toggle icon visibilitya
    if (isDarkMode) {
      sunIcon.classList.remove("hidden");
      moonIcon.classList.add("hidden");
    } else {
      sunIcon.classList.add("hidden");
      moonIcon.classList.remove("hidden");
    }

    themeToggleBtn.setAttribute(
      "aria-label",
      isDarkMode ? "Switch to light mode" : "Switch to dark mode"
    );

    // Re-initialize Notyf with the theme-specific colors to change colors
    initializeNotyf(isDarkMode);
    // Show a confirmation toast
    window.toast.open({
      type: 'info',
      message: `Switched to ${isDarkMode ? "Dark": "Light"} Mode.`, 
      duration: 1200,
      dismissible: false
    });
  }

  // Initialize theme on page load
  const savedTheme = localStorage.getItem("theme");
  if (
    savedTheme === "dark" ||
    (!savedTheme && window.matchMedia("(prefers-color-scheme: dark)").matches)
  ) {
    html.classList.add("dark");
    sunIcon.classList.remove("hidden");
    moonIcon.classList.add("hidden");
  } else {
    html.classList.remove("dark");
    sunIcon.classList.add("hidden");
    moonIcon.classList.remove("hidden");
  }

  // Toggle theme listener
  themeToggleBtn.addEventListener("click", toggleTheme);
  menuToggleBtn.addEventListener("click", () => {
    mobileMenu.classList.toggle("hidden");
  });

  // User btn dropdown listener
  userMenuBtn.addEventListener("click", () => {
    userMenu.classList.toggle("hidden");
  });


  const unreadMsg = document.getElementById("unread_msg_count");
  const chatNavLink = document.getElementById("chat_nav_link");
  const chatLinkErr = document.getElementById("chat_link_err");

  // === WebSocket Connection ===
  const protocol = window.location.protocol === "https:" ? "wss" : "ws";
  const socketUrl = `${protocol}://${window.location.host}/ws/user/`;

  // CRITICAL: Make these persistent across the entire script execution
  let unreadMsgCount = 0;
  let connectionError = null;
  let userSocket = null;
  let pingInterval = null;
  let isConnecting = false; // Flag to prevent multiple connection attempts
  let retryCount = 0; // For exponential backoff
  const MAX_RETRY_TIMEOUT = 30000; // Max 30 seconds wait

  function updateUnreadCountUI() {
    if (unreadMsg) {
      if (unreadMsgCount > 0) {
        unreadMsg.textContent = unreadMsgCount;
        unreadMsg.classList.remove("hidden");
      } else {
        unreadMsg.classList.add("hidden");
      }
    }
  }

  function showErrorOnConnect(isError) {
    if (isError) {
      chatLinkErr.classList.remove("hidden");
      chatNavLink.classList.add("hidden");
    } else {
      chatLinkErr.classList.add("hidden");
      chatNavLink.classList.remove("hidden");
    }
  }

  chatLinkErr.addEventListener("click", () =>
    window.toast.open({
      type: 'error',
      message: connectionError, 
      duration: 3000,
    })
  );

  /**
   * Attempts to establish a WebSocket connection.
   * Implements a singleton pattern and exponential backoff for efficiency.
   */
  function connectWebSocket() {
    if (
      (userSocket &&
        (userSocket.readyState === WebSocket.OPEN ||
          userSocket.readyState === WebSocket.CONNECTING)) ||
      isConnecting
    ) {
      console.log("WebSocket is already connected or attempting to connect.");
      return;
    }

    isConnecting = true;
    console.log("Starting WebSocket connection...");

    // Clear any previous ping interval to avoid zombie pings
    if (pingInterval) {
      clearInterval(pingInterval);
      pingInterval = null;
    }

    userSocket = new WebSocket(socketUrl);

    userSocket.onopen = () => {
      console.log("User socket connected!");
      isConnecting = false;
      retryCount = 0;

      connectionError = null;
      showErrorOnConnect(false); // [false] to reset ui error state

      // Start ping interval
      pingInterval = setInterval(() => {
        if (userSocket && userSocket.readyState === WebSocket.OPEN) {
          userSocket.send(JSON.stringify({ type: "ping" }));
        } else {
          clearInterval(pingInterval);
        }
      }, 20000); // send ping in every 20 sec
    };

    userSocket.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        const type = data?.type;

        if (type === "error" && data?.message === "limit_exceeded") {
          connectionError =
            "Connection limit exceeded. Please close unnecessary tabs.";

          window.toast.open({
            type: 'error',
            message: connectionError, 
            duration: 3000,
          });
          showErrorOnConnect(true); // [true] to show connection err
        }

        if (type === "initial" && typeof data?.msg_count === "number") {
          unreadMsgCount = data.msg_count;
        } else if (type === "new_msg") {
          unreadMsgCount++;

          // Notify on page
          window.toast.open({
            type: 'info',
            message: "You have new message", 
            duration: 1000,
            dismissible: false,
          });
        }

        updateUnreadCountUI();
      } catch (err) {
        console.error("Failed to parse or handle message", err, event.data);
      }
    };

    userSocket.onclose = (event) => {
      console.warn(
        `User socket disconnected. Code: ${event.code}. Reason: ${event.reason}`
      );
      isConnecting = false;

      if (pingInterval) {
        clearInterval(pingInterval);
        pingInterval = null;
      }

      // DO NOT attempt to reconnect on explicit server rejection (like your 4000 code)
      // or normal closure (1000). The server should control non-recoverable errors.
      if (event.code === 4000) {
        connectionError =
          "Connection permanently closed due to limit. Please remove unnecessary tabs and try again in 2 min.";
          
        window.toast.open({
            type: 'error',
            message: connectionError, 
            duration: 3000,
        });
        showErrorOnConnect(true); // [true] to show connection err
        return;
      }

      // Reconnection Logic (Exponential Backoff for Efficiency)
      const timeout = Math.min(
        MAX_RETRY_TIMEOUT,
        1000 * Math.pow(2, retryCount)
      );
      console.log(
        `Attempting reconnection in ${timeout / 1000} seconds... (Retry: ${
          retryCount + 1
        })`
      );

      setTimeout(() => {
        retryCount++;
        connectWebSocket();
      }, timeout);
    };

    userSocket.onerror = (error) => {
      console.error("Websocket Error", error);
    };
  }

  connectWebSocket();
});
