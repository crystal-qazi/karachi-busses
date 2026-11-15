(() => {
  "use strict";
  const token = document.querySelector('meta[name="csrf-token"]')?.content;
  if (!token) return;
  document.querySelectorAll('form[method="post" i], form:not([method])').forEach((form) => {
    if (!form.querySelector('input[name="csrf_token"]')) {
      const input = document.createElement("input");
      input.type = "hidden";
      input.name = "csrf_token";
      input.value = token;
      form.appendChild(input);
    }
  });
})();
