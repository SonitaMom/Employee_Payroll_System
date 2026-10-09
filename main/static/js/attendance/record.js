document.getElementById("copyRecordLink").addEventListener("click", async function () {
    try {
        await navigator.clipboard.writeText(window.location.href);
    } catch (error) {
        alert("Unable to copy the link. Please copy it from your browser's address bar.");
    }
});
