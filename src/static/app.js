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

// Draw the reply into its bubble: ``` fenced parts become code blocks, the rest stays text.
// Only textContent is used, so code in a reply can never inject HTML.
function render(el, text) {
  el.replaceChildren();
  text.split("```").forEach((part, i) => {
    if (i % 2 === 0) {
      if (part.trim()) el.append(document.createTextNode(part.trim() + "\n"));
      return;
    }
    // Drop the language tag on the fence line, e.g. "python"
    const code = part.replace(/^[^\n]*\n/, "").replace(/\n$/, "");
    el.append(codeBlock(code));
  });
}

function codeBlock(code) {
  const block = document.createElement("div");
  block.className = "code-block";
  const pre = document.createElement("pre");
  const codeEl = document.createElement("code");
  codeEl.textContent = code;
  pre.append(codeEl);
  const copy = document.createElement("button");
  copy.type = "button";
  copy.className = "copy";
  copy.textContent = "Copy";
  copy.addEventListener("click", async () => {
    try {
      await navigator.clipboard.writeText(code);
      copy.textContent = "Copied";
    } catch {
      copy.textContent = "Copy failed";
    }
    setTimeout(() => { copy.textContent = "Copy"; }, 1500);
  });
  block.append(pre, copy);
  return block;
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
