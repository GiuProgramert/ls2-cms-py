document.addEventListener("DOMContentLoaded", () => {
  const shareButton = document.getElementById("shareButton");

  shareButton.addEventListener("click", async () => {
    const url = new URL(window.location.origin + window.location.pathname);

    url.searchParams.append("shared", "true");

    const copyMessage = `Mira, te comparto esta publicación de CMS-PY: ${url}`;

    try {
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
    } catch (error) {
      window
        .Toastify({
          test: "Error al intentar copiar el enlace",
          position: "center",
          close: true,
          className: "toast",
          style: {
            background: "#b90f29",
          },
        })
        .showToast();
    }
  });
});
