const messagesEl = document.getElementById("messages");
const form = document.getElementById("composer");
const input = document.getElementById("input");
const sendButton = document.getElementById("send");
const resetButton = document.getElementById("reset");

// Each page load is a new conversation, since the page doesn't redraw earlier messages
let sessionId = crypto.randomUUID();

function addMessage(role, text) {
  const el = document.createElement("div");
  el.className = `message ${role}`;
  el.textContent = text;
  messagesEl.append(el);
  el.scrollIntoView({ block: "end" });
  return el;
}

// Draw the reply text into its bubble
function render(el, text) {
  el.textContent = text;
}

function setBusy(busy) {
  sendButton.disabled = busy;
  resetButton.disabled = busy;
}

async function send(text) {
  addMessage("user", text);
  const reply = addMessage("assistant pending", "Reasoning…");
  setBusy(true);
  try {
    const response = await fetch("/api/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ session_id: sessionId, message: text }),
    });
    if (!response.ok) throw new Error(`Server returned ${response.status}`);

    const reader = response.body.getReader();
    const decoder = new TextDecoder();
    let full = "";
    for (;;) {
      const { done, value } = await reader.read();
      if (done) break;
      full += decoder.decode(value, { stream: true });
      reply.classList.remove("pending");
      render(reply, full);
      reply.scrollIntoView({ block: "end" });
    }
    if (full.startsWith("Error invoking agent:")) reply.classList.add("error");
  } catch (error) {
    reply.className = "message assistant error";
    reply.textContent = `Could not reach the server: ${error.message}`;
  } finally {
    setBusy(false);
    input.focus();
  }
}

form.addEventListener("submit", (event) => {
  event.preventDefault();
  const text = input.value;
  if (!text.trim() || sendButton.disabled) return;
  input.value = "";
  send(text);
});

// Enter sends, Shift+Enter keeps a new line
input.addEventListener("keydown", (event) => {
  if (event.key === "Enter" && !event.shiftKey && !event.isComposing) {
    event.preventDefault();
    form.requestSubmit();
  }
});

resetButton.addEventListener("click", async () => {
  try {
    await fetch("/api/reset", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ session_id: sessionId }),
    });
  } catch {}
  sessionId = crypto.randomUUID();
  messagesEl.querySelectorAll(".message").forEach((el) => el.remove());
  input.focus();
});
