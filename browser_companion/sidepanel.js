const lifecycleEntries = [];

function lifecycleStatus(summary) {
  if (summary.status === "BLOCKED") {
    return "blocked";
  }
  if (summary.status === "RETURNED" || summary.status === "OBSERVED") {
    return "returned";
  }
  return "";
}

window.sidepanelRenderResult = function renderLifecycleResult(summary) {
  lifecycleEntries.push(canonicalize(summary));

  const result = document.getElementById("result");
  const entry = document.createElement("article");
  const heading = document.createElement("h3");
  const payload = document.createElement("pre");
  const statusClass = lifecycleStatus(summary);

  entry.className = `lifecycle-entry${statusClass ? ` ${statusClass}` : ""}`;
  heading.textContent = `Lifecycle entry ${lifecycleEntries.length}: ${summary.status || "RESULT"}`;
  payload.textContent = JSON.stringify(canonicalize(summary), null, 2);

  entry.append(heading, payload);
  result.append(entry);
  result.scrollTop = result.scrollHeight;
};
