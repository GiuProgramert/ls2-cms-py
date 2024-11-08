document.addEventListener("DOMContentLoaded", () => {
  const shareButton = document.getElementById("shareButton");

  shareButton.addEventListener("click", async () => {
    const url = new URL(window.location.origin + window.location.pathname);
    url.searchParams.append("shared", "true");
    const copyMessage = `Mira, te comparto esta publicación de CMS-PY: ${url}`;

    try {
      // Check if HTTPS or localhost
      const isSecureContext =
        window.isSecureContext || window.location.hostname === "localhost";

      if (isSecureContext) {
        await navigator.clipboard.writeText(copyMessage);
        window
          .Toastify({
            text: "Enlace copiado al portapapeles",
            position: "center",
            close: true,
            className: "toast",
            style: {
              background: "#0f9d58",
            },
          })
          .showToast();
      } else {
        throw new Error(
          "Clipboard API requires a secure context (HTTPS or localhost)."
        );
      }
    } catch (error) {
      // Fallback: Select text for manual copy
      const fallbackContainer = document.createElement("textarea");
      fallbackContainer.value = copyMessage;
      fallbackContainer.style.position = "absolute";
      fallbackContainer.style.left = "-9999px"; // Offscreen
      document.body.appendChild(fallbackContainer);
      fallbackContainer.select();
      document.execCommand("copy");
      document.body.removeChild(fallbackContainer);

      window
        .Toastify({
          text: "Enlace copiado manualmente al portapapeles",
          position: "center",
          close: true,
          className: "toast",
          style: {
            background: "#ffa500",
          },
        })
        .showToast();
    }
  });
});
