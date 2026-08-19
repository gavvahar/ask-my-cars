const THEME_KEY = "theme";
const THEME_CHANGE_EVENT = "themechange";

function applyTheme(theme) {
  if (theme === "light" || theme === "dark") {
    document.documentElement.setAttribute("data-theme", theme);
  } else {
    document.documentElement.removeAttribute("data-theme");
  }
}

function setActiveButton(buttons, theme) {
  buttons.forEach((button) => {
    button.classList.toggle("active", button.dataset.theme === theme);
  });
}

function notifyThemeChange() {
  document.dispatchEvent(new CustomEvent(THEME_CHANGE_EVENT));
}

export function getEffectiveTheme() {
  const explicit = document.documentElement.dataset.theme;
  if (explicit === "light" || explicit === "dark") {
    return explicit;
  }
  return window.matchMedia("(prefers-color-scheme: dark)").matches
    ? "dark"
    : "light";
}

export function initTheme() {
  const stored = localStorage.getItem(THEME_KEY) || "system";
  applyTheme(stored);

  const buttons = Array.from(document.querySelectorAll("#theme-toggle button"));
  setActiveButton(buttons, stored);

  buttons.forEach((button) => {
    button.addEventListener("click", () => {
      const theme = button.dataset.theme;
      localStorage.setItem(THEME_KEY, theme);
      applyTheme(theme);
      setActiveButton(buttons, theme);
      notifyThemeChange();
    });
  });

  window
    .matchMedia("(prefers-color-scheme: dark)")
    .addEventListener("change", () => {
      const currentSetting = localStorage.getItem(THEME_KEY) || "system";
      if (currentSetting === "system") {
        notifyThemeChange();
      }
    });
}
