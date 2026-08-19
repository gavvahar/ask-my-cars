import { getFilterOptions } from "./api.js";

function populateSelect(select, options) {
  select.innerHTML = "";
  options.forEach((optionValue) => {
    const option = document.createElement("option");
    option.value = optionValue;
    option.textContent = optionValue;
    option.selected = true;
    select.appendChild(option);
  });
}

export async function initFilters(onFilterChange) {
  const options = await getFilterOptions();

  const makesSelect = document.getElementById("filter-makes");
  const fuelTypesSelect = document.getElementById("filter-fuel-types");
  const yearMinInput = document.getElementById("filter-year-min");
  const yearMaxInput = document.getElementById("filter-year-max");

  populateSelect(makesSelect, options.makes);
  populateSelect(fuelTypesSelect, options.fuel_types);

  yearMinInput.min = options.year_min;
  yearMinInput.max = options.year_max;
  yearMinInput.value = options.year_min;

  yearMaxInput.min = options.year_min;
  yearMaxInput.max = options.year_max;
  yearMaxInput.value = options.year_max;

  makesSelect.addEventListener("change", onFilterChange);
  fuelTypesSelect.addEventListener("change", onFilterChange);

  yearMinInput.addEventListener("change", () => {
    if (Number(yearMinInput.value) > Number(yearMaxInput.value)) {
      yearMaxInput.value = yearMinInput.value;
    }
    onFilterChange();
  });

  yearMaxInput.addEventListener("change", () => {
    if (Number(yearMaxInput.value) < Number(yearMinInput.value)) {
      yearMinInput.value = yearMaxInput.value;
    }
    onFilterChange();
  });
}

export function getCurrentFilters() {
  const makesSelect = document.getElementById("filter-makes");
  const fuelTypesSelect = document.getElementById("filter-fuel-types");
  const yearMinInput = document.getElementById("filter-year-min");
  const yearMaxInput = document.getElementById("filter-year-max");

  return {
    makes: Array.from(makesSelect.selectedOptions).map(
      (option) => option.value,
    ),
    fuel_types: Array.from(fuelTypesSelect.selectedOptions).map(
      (option) => option.value,
    ),
    year_min: Number(yearMinInput.value),
    year_max: Number(yearMaxInput.value),
  };
}
