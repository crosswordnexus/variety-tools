async function copyText(el, btn) {
  try {
    await navigator.clipboard.writeText(el.value);
    showCopiedMessage(btn);
  } catch (err) {
    console.error("Clipboard failed:", err);
  }
}

function showCopiedMessage(btn) {
  let msg = btn.nextElementSibling;
  if (!msg || !msg.classList.contains("copy-status")) {
    msg = document.createElement("span");
    msg.className = "copy-status";
    msg.style.margin = "0.5rem";
    msg.style.color = "green";
    btn.insertAdjacentElement("afterend", msg);
  }
  msg.textContent = "Copied!";
  msg.style.opacity = 1;
  setTimeout(() => {
    msg.style.transition = "opacity 0.5s";
    msg.style.opacity = 0;
  }, 1500);
}
