import { getEffectiveTheme } from "./theme.js";

const CHART_IDS = [
  "chart-hp-mpg",
  "chart-mpg-by-style",
  "chart-hp-msrp",
  "chart-hp-trend",
  "chart-mpg-trend",
];

const THEME_COLORS = {
  light: {
    paper_bgcolor: "#ffffff",
    plot_bgcolor: "#ffffff",
    fontColor: "#1a1a1a",
  },
  dark: {
    paper_bgcolor: "#1a1d27",
    plot_bgcolor: "#1a1d27",
    fontColor: "#e6e6e6",
  },
};

export function applyChartTheme() {
  const theme = getEffectiveTheme();
  const colors = THEME_COLORS[theme];

  CHART_IDS.forEach((id) => {
    const element = document.getElementById(id);
    if (!element || !element.data) {
      return;
    }
    Plotly.relayout(id, {
      paper_bgcolor: colors.paper_bgcolor,
      plot_bgcolor: colors.plot_bgcolor,
      "font.color": colors.fontColor,
    });
  });
}

export function renderCharts(chartsData) {
  Plotly.react(
    "chart-hp-mpg",
    chartsData.hp_mpg.data,
    chartsData.hp_mpg.layout,
  );
  Plotly.react(
    "chart-mpg-by-style",
    chartsData.mpg_by_style.data,
    chartsData.mpg_by_style.layout,
  );
  Plotly.react(
    "chart-hp-msrp",
    chartsData.hp_msrp.data,
    chartsData.hp_msrp.layout,
  );
  Plotly.react(
    "chart-hp-trend",
    chartsData.year_trends.hp_trend.data,
    chartsData.year_trends.hp_trend.layout,
  );
  Plotly.react(
    "chart-mpg-trend",
    chartsData.year_trends.mpg_trend.data,
    chartsData.year_trends.mpg_trend.layout,
  );
  applyChartTheme();
}

document.addEventListener("themechange", applyChartTheme);
