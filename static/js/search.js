import { askQuestion } from "./api.js";

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

function buildCarLookup(retrievedCars) {
  const lookup = new Map();
  retrievedCars.forEach((car) => {
    lookup.set(String(car.id), car);
  });
  return lookup;
}

function renderAnswer(answerText, retrievedCars) {
  const carLookup = buildCarLookup(retrievedCars);
  const answerEl = document.getElementById("answer-text");
  answerEl.innerHTML = "";

  const pattern = /\[Car ID:\s*(\d+)\]/g;
  let lastIndex = 0;
  let match;

  while ((match = pattern.exec(answerText)) !== null) {
    answerEl.appendChild(
      document.createTextNode(answerText.slice(lastIndex, match.index)),
    );

    const car = carLookup.get(match[1]);
    const badge = document.createElement("span");
    badge.className = "citation-badge";
    badge.textContent = car
      ? `${car.year} ${car.make} ${car.model}`
      : "cited car";
    answerEl.appendChild(badge);

    lastIndex = pattern.lastIndex;
  }
  answerEl.appendChild(document.createTextNode(answerText.slice(lastIndex)));
}

function createCarCard(car, citedIds) {
  const card = document.createElement("div");
  card.className = "car-card";
  if (citedIds.has(String(car.id))) {
    card.classList.add("cited");
  }

  const title = document.createElement("h3");
  title.textContent = `${car.year} ${car.make} ${car.model}`;
  card.appendChild(title);

  const details = document.createElement("p");
  details.textContent = `${car.vehicle_style} • ${car.engine_hp} HP • ${car.highway_mpg} hwy MPG • $${car.msrp.toLocaleString()}`;
  card.appendChild(details);

  return card;
}

function renderCars(retrievedCars, citedCarIds) {
  const citedIds = new Set(citedCarIds.map(String));
  const grid = document.getElementById("cars-grid");
  grid.innerHTML = "";
  retrievedCars.forEach((car) => {
    grid.appendChild(createCarCard(car, citedIds));
  });
}

function setLoading(isLoading) {
  document.getElementById("loading-state").style.display = isLoading
    ? "block"
    : "none";
  document.getElementById("ask-button").disabled = isLoading;
}

function hideResults() {
  document.getElementById("answer-section").style.display = "none";
  document.getElementById("cars-section").style.display = "none";
  document.getElementById("error-state").style.display = "none";
}

async function handleSubmit(event) {
  event.preventDefault();

  const question = document.getElementById("question-input").value.trim();
  if (!question) {
    return;
  }

  hideResults();
  setLoading(true);

  try {
    const result = await askQuestion(question);

    renderAnswer(result.answer, result.retrieved_cars);
    renderCars(result.retrieved_cars, result.cited_car_ids);

    document.getElementById("answer-section").style.display = "block";
    document.getElementById("cars-section").style.display = "block";
  } catch (error) {
    const errorEl = document.getElementById("error-state");
    errorEl.textContent = extractErrorDetail(error);
    errorEl.style.display = "block";
  } finally {
    setLoading(false);
  }
}

function init() {
  document.getElementById("ask-form").addEventListener("submit", handleSubmit);
}

init();
