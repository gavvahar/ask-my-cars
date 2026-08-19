import { postAiSummary } from "./api.js";
import { getCurrentFilters } from "./filters.js";

function extractErrorDetail(error) {
  const match = error.message.match(/:\s*(\{.*\})$/);
  if (!match) {
    return error.message;
  }
  try {
    const parsed = JSON.parse(match[1]);
    return parsed.detail ?? error.message;
  } catch {
    return error.message;
  }
}

export function initAiSummary() {
  const button = document.getElementById("generate-summary-btn");
  const resultEl = document.getElementById("ai-summary-result");

  button.addEventListener("click", async () => {
    button.disabled = true;
    const originalText = button.textContent;
    button.textContent = "Generating...";
    resultEl.textContent = "";

    try {
      const filters = getCurrentFilters();
      const { summary } = await postAiSummary(filters);
      resultEl.textContent = summary;
    } catch (error) {
      resultEl.textContent = extractErrorDetail(error);
    } finally {
      button.disabled = false;
      button.textContent = originalText;
    }
  });
}
