function showMessage(message) {
  document.querySelector("#message").textContent = message;
  document.querySelector("#message").classList.remove("hidden");
  setTimeout(() => {
    document.querySelector("#message").classList.add("hidden");
  }, 5000);
}

document.querySelector("#sign-out").addEventListener("click", (event) => {
  fetch("/deauthenticate", {
    method: "POST",
  }).then(() => {
    window.location.reload();
  });
});

document
  .querySelector("#create-container")
  .addEventListener("submit", (event) => {
    event.preventDefault();

    const url = encodeURIComponent(document.querySelector("#url").value);

    let expires;
    if (document.querySelector("#expiration-enable")?.checked === false) {
      expires = 0;
    } else {
      expires = Math.floor(
        (new Date(document.querySelector("#expiration").value).valueOf() -
          new Date().valueOf()) /
          1000,
      );
    }

    fetch(`/new/${url}?expires=${expires}`, {
      method: "POST",
    })
      .then((response) => {
        if (response.ok) {
          window.location.reload();
        } else {
          response.json().then((data) => {
            showMessage(data.error.toUpperCase());
          });
        }
      })
      .catch((error) => {
        console.error(error);
      });
  });

for (const element of document.querySelectorAll(".timestamp")) {
  const date = new Date(0);
  date.setUTCSeconds(Number.parseInt(element.innerHTML));
  element.innerHTML = `${date.toLocaleTimeString()} ${date.toLocaleDateString(
    "en-US",
    {
      month: "long",
      day: "numeric",
      year: "numeric",
    },
  )}`;
}

try {
  document
    .querySelector("input[name='expiration-enable']")
    .addEventListener("input", (event) => {
      if (event.target.checked) {
        document.querySelector("input#expiration").classList.remove("hidden");
      } else {
        document.querySelector("input#expiration").classList.add("hidden");
      }
    });
} catch {}

for (const element of document.querySelectorAll(
  "input[type='datetime-local'",
)) {
  const tzoffset = new Date().getTimezoneOffset() * 60;
  let date = new Date(0);
  // min
  date.setUTCSeconds(Number.parseInt(element.getAttribute("min")) - tzoffset);
  element.setAttribute("min", date.toISOString().replace(/\.[0-9]{3}Z/, ""));

  // value
  date = new Date(0);
  date.setUTCSeconds(Number.parseInt(element.getAttribute("value")) - tzoffset);
  element.setAttribute("value", date.toISOString().replace(/\.[0-9]{3}Z/, ""));

  // max
  date = new Date(0);
  date.setUTCSeconds(Number.parseInt(element.getAttribute("max")) - tzoffset);
  element.setAttribute("max", date.toISOString().replace(/\.[0-9]{3}Z/, ""));
}

for (const element of document.querySelectorAll("span.delete")) {
  element.addEventListener("click", () => {
    if (!window.confirm("Are you sure you want to delete this link?")) {
      return;
    }

    const id = element.getAttribute("data-id");
    fetch(`/${id}`, {
      method: "DELETE",
    }).then(() => {
      window.location.reload();
    });
  });
}
