document.addEventListener("DOMContentLoaded", () => {
    const serverBtns = document.querySelectorAll(".server-btn");
    const tabs = document.querySelectorAll(".tab");
    const emoteGrid = document.getElementById("emoteGrid");
    const customEmote = document.getElementById("customEmote");
    const sendBtn = document.getElementById("sendBtn");
    const resultBox = document.getElementById("result");
    const statusEl = document.getElementById("status");

    let selectedServer = "INDIA";
    let selectedEmoteId = null;

    // Sample emotes (replace with real image URLs and IDs as needed)
    const emotes = {
        funny: [
            { id: "909000063", name: "AK47 Dance", img: "https://via.placeholder.com/70/1e1e32/00ff88?text=AK47" },
            { id: "909000001", name: "Laugh", img: "https://via.placeholder.com/70/1e1e32/ffaa00?text=LOL" },
            { id: "909000002", name: "Crazy", img: "https://via.placeholder.com/70/1e1e32/ff3366?text=CRAZY" }
        ],
        greeting: [
            { id: "909000010", name: "Wave", img: "https://via.placeholder.com/70/1e1e32/00aaff?text=WAVE" },
            { id: "909000011", name: "Salute", img: "https://via.placeholder.com/70/1e1e32/00ff88?text=SALUTE" },
            { id: "909000012", name: "Hello", img: "https://via.placeholder.com/70/1e1e32/ffaa00?text=HI" }
        ],
        dance: [
            { id: "909000020", name: "Dance 1", img: "https://via.placeholder.com/70/1e1e32/ff3366?text=DANCE" },
            { id: "909000021", name: "Break", img: "https://via.placeholder.com/70/1e1e32/00ff88?text=BREAK" },
            { id: "909000022", name: "Hip Hop", img: "https://via.placeholder.com/70/1e1e32/00aaff?text=HIP" }
        ]
    };

    function renderEmotes(category) {
        emoteGrid.innerHTML = "";
        if (category === "custom") {
            emoteGrid.classList.add("hidden");
            customEmote.classList.remove("hidden");
            selectedEmoteId = null;
            return;
        }
        emoteGrid.classList.remove("hidden");
        customEmote.classList.add("hidden");

        (emotes[category] || []).forEach(emote => {
            const div = document.createElement("div");
            div.className = "emote-item";
            div.innerHTML = `
                <img src="${emote.img}" alt="${emote.name}">
                <span>${emote.name}</span>
                <small>ID: ${emote.id}</small>
            `;
            div.onclick = () => {
                document.querySelectorAll(".emote-item").forEach(el => el.classList.remove("selected"));
                div.classList.add("selected");
                selectedEmoteId = emote.id;
            };
            emoteGrid.appendChild(div);
        });
    }

    serverBtns.forEach(btn => {
        btn.addEventListener("click", () => {
            serverBtns.forEach(b => b.classList.remove("active"));
            btn.classList.add("active");
            selectedServer = btn.dataset.server;
        });
    });

    tabs.forEach(tab => {
        tab.addEventListener("click", () => {
            tabs.forEach(t => t.classList.remove("active"));
            tab.classList.add("active");
            renderEmotes(tab.dataset.cat);
        });
    });

    // Initial load
    renderEmotes("funny");

    sendBtn.addEventListener("click", async () => {
        const teamCode = document.getElementById("teamCode").value.trim();
        const customId = document.getElementById("customEmoteId").value.trim();
        const emoteId = selectedEmoteId || customId;

        const uids = Array.from(document.querySelectorAll(".uid-input"))
            .map(input => input.value.trim())
            .filter(uid => uid);

        if (!teamCode) {
            showResult("Please enter a Team Code first.", true);
            return;
        }
        if (!emoteId) {
            showResult("Please select or enter an Emote ID.", true);
            return;
        }

        statusEl.textContent = "Sending...";
        sendBtn.disabled = true;

        try {
            const response = await fetch("/api/send", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    team_code: teamCode,
                    emote_id: emoteId,
                    server_name: selectedServer,
                    uids: uids
                })
            });

            const data = await response.json();
            if (data.success) {
                showResult("✅ Emote sent successfully! " + (data.message || ""), false);
            } else {
                showResult("❌ " + (data.error || "Failed to send emote"), true);
            }
        } catch (err) {
            showResult("❌ Network error: " + err.message, true);
        } finally {
            statusEl.textContent = "Ready";
            sendBtn.disabled = false;
        }
    });

    function showResult(msg, isError) {
        resultBox.textContent = msg;
        resultBox.classList.remove("hidden", "error");
        if (isError) resultBox.classList.add("error");
        resultBox.classList.remove("hidden");
    }
});
