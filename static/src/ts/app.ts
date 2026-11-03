/**
 * Capacity Connect - Core Frontend TypeScript Module
 * SIH26075 - Ministry of Earth Sciences (MoES) Portal
 */

// Mobile sidebar toggle
export function initSidebar(): void {
  const toggleBtn = document.getElementById('sidebar-toggle');
  const sidebar = document.getElementById('main-sidebar');
  const backdrop = document.getElementById('sidebar-backdrop');

  if (toggleBtn && sidebar) {
    toggleBtn.addEventListener('click', () => {
      sidebar.classList.toggle('-translate-x-full');
      if (backdrop) backdrop.classList.toggle('hidden');
    });
  }

  if (backdrop && sidebar) {
    backdrop.addEventListener('click', () => {
      sidebar.classList.add('-translate-x-full');
      backdrop.classList.add('hidden');
    });
  }
}

// User dropdown menu toggle
export function initUserMenu(): void {
  const menuBtn = document.getElementById('user-menu-button');
  const dropdown = document.getElementById('user-menu-dropdown');

  if (menuBtn && dropdown) {
    menuBtn.addEventListener('click', (e) => {
      e.stopPropagation();
      dropdown.classList.toggle('hidden');
    });

    document.addEventListener('click', (e) => {
      if (!dropdown.contains(e.target as Node) && !menuBtn.contains(e.target as Node)) {
        dropdown.classList.add('hidden');
      }
    });
  }
}

// Notification auto-dismiss toasts
export function initToasts(): void {
  const toasts = document.querySelectorAll('.toast-alert');
  toasts.forEach((toast) => {
    setTimeout(() => {
      toast.classList.add('opacity-0', 'transition-opacity', 'duration-500');
      setTimeout(() => toast.remove(), 500);
    }, 4500);
  });
}

// Assessment Countdown Timer
export function initAssessmentTimer(durationMinutes: number, formId: string, displayId: string): void {
  const display = document.getElementById(displayId);
  const form = document.getElementById(formId) as HTMLFormElement | null;
  if (!display || !form || durationMinutes <= 0) return;

  let totalSeconds = durationMinutes * 60;

  const timer = setInterval(() => {
    totalSeconds--;
    if (totalSeconds <= 0) {
      clearInterval(timer);
      display.textContent = "00:00 - Time's up!";
      alert("Assessment time has elapsed. Your responses are being submitted automatically.");
      form.submit();
      return;
    }

    const mins = Math.floor(totalSeconds / 60);
    const secs = totalSeconds % 60;
    display.textContent = `${String(mins).padStart(2, '0')}:${String(secs).padStart(2, '0')}`;

    if (totalSeconds <= 120) {
      display.classList.add('text-red-600', 'font-bold', 'animate-pulse');
    }
  }, 1000);
}

// Dynamic Client-side Search / Filter
export function initTableFilter(searchInputId: string, tableId: string): void {
  const input = document.getElementById(searchInputId) as HTMLInputElement | null;
  const table = document.getElementById(tableId);
  if (!input || !table) return;

  input.addEventListener('keyup', () => {
    const term = input.value.toLowerCase();
    const rows = table.querySelectorAll('tbody tr');
    rows.forEach((row) => {
      const text = row.textContent?.toLowerCase() || '';
      (row as HTMLElement).style.display = text.includes(term) ? '' : 'none';
    });
  });
}

// Initialize on DOMContentLoaded
document.addEventListener('DOMContentLoaded', () => {
  initSidebar();
  initUserMenu();
  initToasts();
});

// Expose utilities on window for inline dashboard scripting
(window as unknown as Record<string, unknown>).CapacityConnect = {
  initAssessmentTimer,
  initTableFilter,
};

