document.querySelector("#password").addEventListener("keyup", (event) => {
  if (event.key === "Enter") {
    document.querySelector("button").click();
  }
});

function showMessage(message) {
  document.querySelector("#message").textContent = message;
  document.querySelector("#message").classList.remove("hidden");
  setTimeout(() => {
    document.querySelector("#message").classList.add("hidden");
  }, 5000);
}

document.querySelector("button").addEventListener("click", (event) => {
  event.preventDefault();

  const username = document.querySelector("#username").value;
  const password = document.querySelector("#password").value;

  if (username === "" || password === "") {
    showMessage("Please fill in all fields");
  } else {
    fetch("/authenticate", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ username, password }),
    })
      .then((response) => {
        if (response.ok) {
          window.location.reload();
        } else {
          document.querySelector("#username").value = "";
          document.querySelector("#password").value = "";
          showMessage("Invalid username or password");
        }
      })
      .catch((error) => {
        console.error(error);
      });
  }
});
