import { create } from "zustand";

export type ThemeMode = "system" | "light" | "dark";

interface UiState {
  sidebarOpen: boolean;
  paletteOpen: boolean;
  theme: ThemeMode;
  setSidebarOpen: (open: boolean) => void;
  toggleSidebar: () => void;
  setPaletteOpen: (open: boolean) => void;
  setTheme: (theme: ThemeMode) => void;
}

const SIDEBAR_KEY = "app:sidebar";
const THEME_KEY = "app:theme";
let removeSystemThemeListener: (() => void) | undefined;

function resolvedTheme(theme: ThemeMode): "light" | "dark" {
  if (theme === "light" || theme === "dark") return theme;
  return typeof matchMedia === "function" &&
    matchMedia("(prefers-color-scheme: dark)").matches
    ? "dark"
    : "light";
}

function applyTheme(theme: ThemeMode): void {
  if (typeof document === "undefined") return;
  const resolved = resolvedTheme(theme);
  document.documentElement.dataset.theme = resolved;
  document.documentElement.style.colorScheme = resolved;
}

function persist(key: string, value: string): void {
  try {
    localStorage.setItem(key, value);
  } catch {
    // Storage can be unavailable during SSR or in locked-down browsers.
  }
}

export const useUi = create<UiState>((set, get) => ({
  sidebarOpen: true,
  paletteOpen: false,
  theme: "system",
  setSidebarOpen: (sidebarOpen) => {
    set({ sidebarOpen });
    persist(SIDEBAR_KEY, sidebarOpen ? "1" : "0");
  },
  toggleSidebar: () => get().setSidebarOpen(!get().sidebarOpen),
  setPaletteOpen: (paletteOpen) => set({ paletteOpen }),
  setTheme: (theme) => {
    set({ theme });
    persist(THEME_KEY, theme);
    applyTheme(theme);
  },
}));

export function hydrateUiPrefs(): void {
  try {
    const sidebar = localStorage.getItem(SIDEBAR_KEY);
    const storedTheme = localStorage.getItem(THEME_KEY);
    const theme: ThemeMode =
      storedTheme === "light" ||
      storedTheme === "dark" ||
      storedTheme === "system"
        ? storedTheme
        : "system";
    useUi.setState({
      ...(sidebar == null ? {} : { sidebarOpen: sidebar === "1" }),
      theme,
    });
    applyTheme(theme);

    removeSystemThemeListener?.();
    if (typeof matchMedia === "function") {
      const media = matchMedia("(prefers-color-scheme: dark)");
      const handleChange = () => {
        if (useUi.getState().theme === "system") applyTheme("system");
      };
      media.addEventListener("change", handleChange);
      removeSystemThemeListener = () =>
        media.removeEventListener("change", handleChange);
    }
  } catch {
    applyTheme("system");
  }
}
