function createCell(text) {
  const td = document.createElement("td");
  td.textContent = text;
  return td;
}

export function renderLeaderboard(leaderboardData) {
  const tbody = document.getElementById("leaderboard-body");
  tbody.innerHTML = "";
  leaderboardData.forEach((row) => {
    const tr = document.createElement("tr");
    tr.appendChild(createCell(row.make));
    tr.appendChild(createCell(row.model));
    tr.appendChild(createCell(row.year));
    tr.appendChild(createCell(row.engine_hp));
    tr.appendChild(createCell(row.highway_mpg));
    tr.appendChild(createCell(row.efficiency_score));
    tbody.appendChild(tr);
  });
}
