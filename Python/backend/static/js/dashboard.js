import { getDashboard } from "./api.js";
import { initFilters, getCurrentFilters } from "./filters.js";
import { renderCharts } from "./charts.js";
import { renderKpis } from "./kpis.js";
import { renderLeaderboard } from "./leaderboard.js";
import { initAiSummary } from "./ai-summary.js";
import { initTheme } from "./theme.js";

async function refresh() {
  const filters = getCurrentFilters();
  const emptyMessage = document.getElementById("empty-state-message");
  const content = document.getElementById("dashboard-content");

  try {
    const data = await getDashboard(filters);
    renderKpis(data.kpis);

    if (data.kpis.count === 0) {
      emptyMessage.style.display = "block";
      content.style.display = "none";
    } else {
      emptyMessage.style.display = "none";
      content.style.display = "block";
      renderCharts(data.charts);
      renderLeaderboard(data.leaderboard);
    }
  } catch (error) {
    console.error("Failed to load dashboard data:", error);
  }
}

async function init() {
  initTheme();
  await initFilters(refresh);
  await refresh();
  initAiSummary();
}

init();
