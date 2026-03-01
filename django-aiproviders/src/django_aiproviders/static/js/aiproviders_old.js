function AIProvidersExtractContext() {
let idCounter = 0;
const elements = [];

function newId() {
    return "el_" + (++idCounter);
}

function getLabel(el) {
    if (el.labels && el.labels[0]) return el.labels[0].innerText;
    if (el.getAttribute("aria-label")) return el.getAttribute("aria-label");
    return null;
}

document.querySelectorAll(`
    button,
    a[href],
    input,
    textarea,
    select
`).forEach(el => {
    if (!el.offsetParent) return;

    elements.push({
    id: newId(),
    role: el.tagName.toLowerCase(),
    text: el.innerText || el.value || null,
    label: getLabel(el),
    placeholder: el.placeholder || null,
    selector: el.id ? `#${el.id}` : null,
    disabled: el.disabled || false
    });
});

return {
    page: {
    title: document.title,
    url: location.href
    },
    elements
};
}

function addAIAssistIcons() {
const inputs = document.querySelectorAll("input[type='text'], textarea");

inputs.forEach(input => {
    // wrapper pour positionnement
    const wrapper = document.createElement("div");
    wrapper.style.position = "relative";
    input.parentNode.insertBefore(wrapper, input);
    wrapper.appendChild(input);

    // icône
    const icon = document.createElement("div");
    icon.innerText = "✨";
    icon.title = "Ask AI";
    icon.style.position = "absolute";
    icon.style.right = "8px";
    icon.style.top = "50%";
    icon.style.transform = "translateY(-50%)";
    icon.style.cursor = "pointer";
    icon.style.fontSize = "14px";
    icon.style.opacity = "0.7";

    wrapper.appendChild(icon);

    // clic sur l'icône
    icon.addEventListener("click", async () => {
    const question = prompt("Que doit remplir l'IA ?");
    if (!question) return;

    const payload = {
        question,
        inputContext: {
        id: input.id,
        name: input.name,
        placeholder: input.placeholder,
        label: input.labels?.[0]?.innerText || null
        },
        pageUrl: location.href
    };

    const response = await fetch("/api/agent-fill", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
    });

    const data = await response.json();

    input.value = data.text;
    input.dispatchEvent(new Event("input", { bubbles: true }));
    });
});
}

function initAssistantIcons() {
    addAIAssistIcons();
}

document.addEventListener("DOMContentLoaded", initAssistantIcons);

// Observer les changements (inputs ajoutés dynamiquement)
const observer = new MutationObserver(() => {
    initAssistantIcons();
});

observer.observe(document.body, {
    childList: true,
    subtree: true
});