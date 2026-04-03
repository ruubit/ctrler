const params = new URLSearchParams(location.hash.slice(1));
const SESSION_TOKEN = params.get("token");

if (!SESSION_TOKEN) {
    alert("Missing session token. Please reconnect using the QR code.");
    throw new Error("Session token missing");
}

let LIGHT;
let BASE_BACKGROUND_LIGHT;

document.addEventListener("DOMContentLoaded", initialize);


/**
 * Initialize some constants and register the button callbacks.
 * 
 */
function initialize() {
    const buttons = document.querySelectorAll("button");
    registerButtonCallbacks(buttons);
    LIGHT = document.getElementById("light");
    BASE_BACKGROUND_LIGHT = LIGHT.style.background;
}

/**
 * Registers the event listeners for the play, pause, rewind and forward buttons.
 * 
 * @param {NodeListOf<HTMLButtonElement>} buttons - The buttons.
 */
function registerButtonCallbacks(buttons) {
    for (let button of buttons) {
        button.addEventListener("click", handleButtonClick)
    }
}

/**
 * Handle a button click.
 * 
 * @param {MouseEvent} e - The click event of the button.
 */
function handleButtonClick(e) {
    animateRemoteLight();
    postAction(e.currentTarget.id);
}

/**
 * Animate the change of color of the light of the remote controller in a simple
 * way.
 * 
 */
function animateRemoteLight(){
    LIGHT.style.background = `linear-gradient(
    rgb(255, 0, 0), 
    rgb(109, 21, 21), 
    rgb(187, 36, 36), 
    rgb(255, 255, 255))`;
    LIGHT.style.boxShadow = '0px 0px 20px 5px rgb(254, 97, 97)';
    setTimeout(() => {
        LIGHT.style.background = BASE_BACKGROUND_LIGHT;
        LIGHT.style.boxShadow = '';
    }, 200);
}

/**
 * Posts an action of a user (i.e. a click on play, pause, rewind or forward) to
 * the API.
 * 
 * @param {string} action - The actual action, one of play, pause, rewind or forward.
 */
async function postAction(action) {
    try {
        const response = await fetch("/api/action", {
            method: "POST",
            body: JSON.stringify({ "action": action}),
            headers: {
                "Content-type": "application/json",
                "Authorization": `Bearer ${SESSION_TOKEN}`
            }
        });
        if (!response.ok) {
            console.log(`Post request failed. Status code: ${response.status}.`)
            alert("The request failed, make sure you paired your phone via the QR code.")
        }
    } catch (e) {
        console.log(e);
        alert("An error occurred... Is the server still running?");
    }
}


