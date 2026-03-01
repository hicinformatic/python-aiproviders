var ai_icon = "/static/img/ai-icon.svg";
var data_ignore = "data-aiproviders-ignore";

function closeWidget() {
    const overlay = document.getElementById("aiproviders-widget-overlay");
    if (overlay) {
        overlay.remove();
        document.removeEventListener("keydown", handleWidgetEsc);
    }
}

function handleWidgetEsc(e) {
    if (e.key === "Escape") closeWidget();
}

function getInputContext(inputEl) {
    if (!inputEl || !(inputEl instanceof HTMLElement)) return {};
    const labelEl = inputEl.id ? document.querySelector('label[for="' + inputEl.id + '"]') : null;
    return {
        name: inputEl.getAttribute("name") || undefined,
        id: inputEl.id || undefined,
        placeholder: inputEl.getAttribute("placeholder") || undefined,
        type: (inputEl.getAttribute("type") || inputEl.tagName.toLowerCase()) || undefined,
        value: inputEl.value || undefined,
        label: (labelEl && labelEl.textContent) ? labelEl.textContent.trim() : undefined,
    };
}

function showWidget(iconEl, inputEl) {
    const url = window.AIPROVIDERS_WIDGET_URL;
    if (!url) return;
    const existing = document.getElementById("aiproviders-widget-overlay");
    if (existing) {
        closeWidget();
        return;
    }
    fetch(url)
        .then(r => r.text())
        .then(html => {
            const overlay = document.createElement("div");
            overlay.id = "aiproviders-widget-overlay";
            overlay.className = "aiproviders-widget-overlay";
            overlay.innerHTML = '<div class="aiproviders-widget-container aiproviders-widget-container--focus">' + html + "</div>";
            overlay.addEventListener("click", function (e) {
                if (e.target === overlay) closeWidget();
            });
            document.addEventListener("keydown", handleWidgetEsc);
            document.body.appendChild(overlay);
            const textarea = overlay.querySelector("#aiproviders-widget-textarea");
            if (textarea) textarea.focus();
            const form = overlay.querySelector(".aiproviders-widget-form");
            let conversation = [];
            let firstMsg = true;
            const inputContext = inputEl ? getInputContext(inputEl) : {};
            if (form) {
                form.addEventListener("submit", function (e) {
                    e.preventDefault();
                    const q = (form.querySelector('[name="q"]') || textarea).value.trim();
                    if (!q) return;
                    const promptUrl = window.AIPROVIDERS_PROMPT_URL || (window.AIPROVIDERS_WIDGET_URL || "").replace(/widget\/?$/, "prompt/");
                    if (!promptUrl) return;
                    const responseEl = overlay.querySelector(".aiproviders-widget-response");
                    responseEl.textContent = "...";
                    const body = JSON.stringify({ q: q, conversation: conversation, first: firstMsg, context: inputContext });
                    const csrfEl = document.querySelector("[name=csrfmiddlewaretoken]");
                    const csrf = (csrfEl && csrfEl.value) || (document.cookie.match(/csrftoken=([^;]+)/) || [])[1] || "";
                    const headers = { "Content-Type": "application/json", "X-CSRFToken": csrf };
                    fetch(promptUrl, { method: "POST", body: body, headers: headers })
                        .then(r => r.json())
                        .then(data => {
                            const r = (data.results || [])[0];
                            if (!r) {
                                responseEl.textContent = "No response";
                                return;
                            }
                            conversation.push({ role: "user", content: q });
                            conversation.push({ role: "assistant", content: (r.content || "").toString() });
                            firstMsg = false;
                            let html = "<div class=\"aiproviders-widget-result\">";
                            if (r.error) {
                                html += "<div class=\"aiproviders-widget-error\">" + r.error + "</div>";
                            } else if (r.content) {
                                html += "<div class=\"aiproviders-widget-content\">" + r.content.replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/\n/g, "<br>") + "</div>";
                                if (r.usage) {
                                    html += "<div class=\"aiproviders-widget-usage\">" + (r.usage.input_tokens || 0) + " in / " + (r.usage.output_tokens || 0) + " out</div>";
                                }
                            }
                            html += "</div>";
                            responseEl.innerHTML = html;
                            if (textarea) textarea.value = "";
                            if (inputEl && r.content && !r.error) {
                                let target = inputEl;
                                if (!document.body.contains(inputEl)) {
                                    if (inputEl.id) target = document.getElementById(inputEl.id);
                                    else if (inputEl.name && inputEl.form) target = inputEl.form.querySelector('[name="' + inputEl.name + '"]') || inputEl;
                                    if (!target || !document.body.contains(target)) return;
                                }
                                const text = (r.content || "").toString();
                                const isFirstResponse = conversation.length === 2;
                                if (isFirstResponse) {
                                    const start = target.selectionStart != null ? target.selectionStart : target.value.length;
                                    const end = target.selectionEnd != null ? target.selectionEnd : start;
                                    target.value = target.value.slice(0, start) + text + target.value.slice(end);
                                    const newPos = start + text.length;
                                    target.setSelectionRange(newPos, newPos);
                                } else {
                                    target.value = text;
                                    target.setSelectionRange(text.length, text.length);
                                }
                                target.dispatchEvent(new Event("input", { bubbles: true }));
                            }
                        })
                        .catch(() => {
                            responseEl.textContent = "Erreur";
                        });
                });
            }
        });
}

function listenAllInputHover() {
    const inputs = document.querySelectorAll(`input:not([${data_ignore}]), textarea:not([${data_ignore}])`);

    inputs.forEach(input => {
    
        input.addEventListener("mouseenter", () => {
            const img = document.createElement("img");
            img.src = ai_icon;
            img.style.width = "25px";
            img.style.height = "25px";
            img.style.opacity = "1";
            img.style.position = "sticky";
            img.style.marginLeft = "-30px";
            img.style.marginTop = "5px";
            img.style.cursor = "pointer";
            img.id = "ai-icon" + input.id;
            img.className = "aiproviders-icon";
            input.insertAdjacentElement("afterend", img);
            img.addEventListener("click", (e) => {
                e.preventDefault();
                showWidget(img, input);
            });
        });

        input.addEventListener("mouseleave", () => {
            const img = document.getElementById("ai-icon" + input.id);
            if (!img) return;
            const timeoutId = setTimeout(() => img.remove(), 200);
            const cancelRemove = () => clearTimeout(timeoutId);
            img.addEventListener("mouseenter", cancelRemove, { once: true });
            img.addEventListener("mouseleave", () => img.remove(), { once: true });
        });
    });
}

document.addEventListener("DOMContentLoaded", function () {
    listenAllInputHover();
});