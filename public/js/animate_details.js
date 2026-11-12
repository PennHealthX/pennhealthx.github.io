function animateClick(e, isAnimating, detail, summary) {
  e.preventDefault();
  if (isAnimating)
    return;
  const summaryHeight = summary.offsetHeight;

  if (!detail.open) {
    isAnimating = true;
    detail.open = true;
    const fullHeight = detail.scrollHeight;
    detail.style.height = summaryHeight + "px";
    // Double RAF ensures the browser paints the `summaryHeight` before we
    // tell it to grow to `fullHeight`.
    requestAnimationFrame(() => {
      requestAnimationFrame(() => {
        detail.style.height = fullHeight + "px";
      });
    });
  } else {
    isAnimating = true;
    const startHeight = detail.offsetHeight;
    detail.style.height = startHeight + "px";

    requestAnimationFrame(() => {
      requestAnimationFrame(() => {
        detail.style.height = summaryHeight + "px";
      });
    });
  }
}

function animateDetail(detail) {
  const summary = detail.querySelector("summary");
  let isAnimating = false;

  summary.addEventListener(
    "click", (e) => animateClick(e, isAnimating, detail, summary)
  );

  detail.addEventListener("transitionend", (e) => {
    if (e.propertyName === "height") {
      isAnimating = false;
      if (detail.style.height === summary.offsetHeight + "px") {
        detail.open = false;
      }
      detail.style.height = "";
    }
  });
}

document.querySelectorAll("details").forEach((el) => animateDetail(el));
