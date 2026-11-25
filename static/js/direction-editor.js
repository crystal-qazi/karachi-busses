(() => {
  "use strict";

  const search = document.getElementById("ordered-stop-search");
  const select = document.getElementById("ordered-stop-select");
  const status = document.getElementById("ordered-stop-search-status");
  const addButton = document.getElementById("add-ordered-stop");

  if (!search || !select || !status || !addButton) return;

  const options = Array.from(select.options);

  const updateStopOptions = () => {
    const query = search.value.trim().toLocaleLowerCase();
    let visibleCount = 0;
    let firstVisible = null;

    options.forEach((option) => {
      const searchableText = (option.textContent + " " + option.value).toLocaleLowerCase();
      const matches = !query || searchableText.includes(query);
      option.hidden = !matches;

      if (matches) {
        visibleCount += 1;
        if (!firstVisible) firstVisible = option;
      }
    });

    if (select.selectedOptions.length && select.selectedOptions[0].hidden) {
      select.value = firstVisible ? firstVisible.value : "";
    }

    select.disabled = visibleCount === 0;
    addButton.disabled = visibleCount === 0;
    status.textContent = query
      ? visibleCount + " matching stop" + (visibleCount === 1 ? "" : "s")
      : options.length + " stops available";

    if (visibleCount === 0) {
      status.textContent = "No stops found. Try another name or ID.";
    }
  };

  search.addEventListener("input", updateStopOptions);
  updateStopOptions();
})();
