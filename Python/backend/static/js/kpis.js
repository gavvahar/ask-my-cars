export function renderKpis(kpisData) {
  document.querySelector("#kpi-count .kpi-value").textContent = kpisData.count;
  document.querySelector("#kpi-avg-mpg .kpi-value").textContent =
    kpisData.avg_mpg ?? "—";
  document.querySelector("#kpi-avg-hp .kpi-value").textContent =
    kpisData.avg_hp ?? "—";
}
