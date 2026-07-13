/**
 * static/js/demo.js — Demo Page Chat Widget Logic
 * =================================================
 * This file is an alternative to the inline <script> in demo.html.
 * You can switch to using this file by replacing the inline script block with:
 *   <script src="{{ url_for('static', filename='js/demo.js') }}"></script>
 *
 * It powers the browser-based bot simulation on /demo.
 *
 * Key behaviours:
 *  - Sends POST requests to /api/demo/chat with { message, phone }
 *  - Renders inbound (bot) and outbound (user) chat bubbles
 *  - Shows a typing indicator while awaiting the bot's reply
 *  - Quick-reply buttons for common inputs (hi, 1, 2, …)
 *  - Auto-sends "hi" on page load to get the greeting
 */

(function () {
  "use strict";

  // ── DOM refs ──────────────────────────────────────────────────────────────
  const messagesEl = document.getElementById("messages");
  const inputEl    = document.getElementById("msgInput");
  const sendBtn    = document.getElementById("sendBtn");
  const typingEl   = document.getElementById("typingIndicator");

  if (!messagesEl || !inputEl || !sendBtn) return; // not on the demo page

  // ── Config ────────────────────────────────────────────────────────────────
  const API_URL    = "/api/demo/chat";
  const DEMO_PHONE = "demo_" + Math.random().toString(36).slice(2, 10);

  // ── Helpers ───────────────────────────────────────────────────────────────

  /** Append a chat bubble to the message area. */
  function addBubble(text, direction) {
    const row    = document.createElement("div");
    row.className = `msg-row ${direction}`;

    const bubble = document.createElement("div");
    bubble.className = `bubble ${direction}`;
    bubble.textContent = text;

    const time    = document.createElement("div");
    time.className = "msg-time";
    time.textContent = new Date().toLocaleTimeString([], {
      hour: "2-digit", minute: "2-digit",
    });

    const wrap = document.createElement("div");
    wrap.appendChild(bubble);
    wrap.appendChild(time);
    row.appendChild(wrap);
    messagesEl.appendChild(row);
    messagesEl.scrollTop = messagesEl.scrollHeight;
  }

  /** Show or hide the "bot is typing" indicator. */
  function showTyping(visible) {
    if (!typingEl) return;
    typingEl.style.display = visible ? "block" : "none";
    if (visible) messagesEl.scrollTop = messagesEl.scrollHeight;
  }

  /** Random delay 400–700 ms to simulate a natural response time. */
  function naturalDelay() {
    return new Promise((r) => setTimeout(r, 400 + Math.random() * 300));
  }

  // ── Core send function ────────────────────────────────────────────────────

  async function sendMessage(overrideText) {
    const text = (overrideText || inputEl.value).trim();
    if (!text) return;

    inputEl.value       = "";
    sendBtn.disabled    = true;

    addBubble(text, "out");   // user bubble
    showTyping(true);

    try {
      const res  = await fetch(API_URL, {
        method:  "POST",
        headers: { "Content-Type": "application/json" },
        body:    JSON.stringify({ message: text, phone: DEMO_PHONE }),
      });

      if (!res.ok) throw new Error(`HTTP ${res.status}`);

      const data = await res.json();
      await naturalDelay();

      showTyping(false);
      addBubble(data.reply || "Hmm, something went wrong. Please try again.", "in");

    } catch (err) {
      console.error("[Demo]", err);
      showTyping(false);
      addBubble("⚠️ Connection error. Please try again.", "in");
    } finally {
      sendBtn.disabled = false;
      inputEl.focus();
    }
  }

  // ── Event listeners ───────────────────────────────────────────────────────

  sendBtn.addEventListener("click",   () => sendMessage());
  inputEl.addEventListener("keydown", (e) => { if (e.key === "Enter") sendMessage(); });

  document.querySelectorAll(".quick-btn").forEach((btn) => {
    btn.addEventListener("click", () => sendMessage(btn.textContent.trim()));
  });

  // ── Auto-start: send "hi" to trigger the greeting ─────────────────────────
  window.addEventListener("load", () => sendMessage("hi"));

})();