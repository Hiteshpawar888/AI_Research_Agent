
/* ==========================================
   AI RESEARCH AGENT
   FIREBASE AUTHENTICATION UI
========================================== */

import {
    auth,
    loginWithGoogle,
    registerWithEmail,
    loginWithEmail,
    logoutUser,
    observeAuthState
} from "./firebase_auth.js";

import {
    sendPasswordResetEmail
} from "https://www.gstatic.com/firebasejs/12.4.0/firebase-auth.js";


// ==========================================
// ELEMENT REFERENCES
// ==========================================

const byId = (id) => document.getElementById(id);

const modal = byId("authModal");
const dialog = modal.querySelector(".auth-dialog");

const form = byId("authForm");

const emailInput = byId("authEmail");
const passwordInput = byId("authPassword");
const confirmInput = byId("authConfirmPassword");

const messageBox = byId("authMessage");

const googleButton = byId("authGoogleBtn");
const submitButton = byId("authSubmitBtn");
const forgotButton = byId("authForgotPasswordBtn");

const confirmWrap = byId("authConfirmWrap");
const switchButton = byId("authSwitchBtn");

const userDropdown = byId("authUserDropdown");
const userMenuButton = byId("authUserMenuBtn");

let currentMode = "login";
let busy = false;
let previousFocus = null;


// ==========================================
// DISPLAY SUCCESS / ERROR MESSAGES
// ==========================================

function showMessage(message, isSuccess = false) {

    messageBox.textContent = message;

    messageBox.classList.toggle(
        "auth-success",
        isSuccess
    );

    messageBox.hidden = !message;
}


// ==========================================
// FIREBASE ERROR MESSAGES
// ==========================================

function readableError(error) {

    const code = error?.code || "";

    const messages = {

        "auth/invalid-email":
            "Please enter a valid email address.",

        "auth/missing-email":
            "Please enter your email address.",

        "auth/email-already-in-use":
            "This email is already registered. Please log in instead.",

        "auth/weak-password":
            "Please choose a stronger password (at least 6 characters).",

        "auth/invalid-credential":
            "Incorrect email or password.",

        "auth/wrong-password":
            "Incorrect email or password.",

        "auth/user-not-found":
            "No account found. Try signing up.",

        "auth/popup-closed-by-user":
            "The Google sign-in window was closed. Please try again.",

        "auth/cancelled-popup-request":
            "Another sign-in window is already open. Please try again.",

        "auth/popup-blocked":
            "Please allow popups for this website to use Google sign-in.",

        "auth/unauthorized-domain":
            "This website domain must be added to Firebase Authentication Authorized domains.",

        "auth/operation-not-allowed":
            "This sign-in method is not enabled in Firebase Authentication.",

        "auth/network-request-failed":
            "Network connection failed. Please try again.",

        "auth/too-many-requests":
            "Too many attempts. Please wait a while and try again."

    };

    return messages[code] ||
        "Could not complete authentication. Please try again.";
}


// ==========================================
// LOADING / BUSY STATE
// ==========================================

function setBusy(nextBusy) {

    busy = nextBusy;

    submitButton.disabled = nextBusy;
    googleButton.disabled = nextBusy;
    forgotButton.disabled = nextBusy;
    switchButton.disabled = nextBusy;

    submitButton.textContent = nextBusy
        ? "Please wait..."
        : currentMode === "signup"
            ? "Create account"
            : "Log in";
}


// ==========================================
// SWITCH LOGIN / SIGN UP
// ==========================================

function setMode(nextMode) {

    currentMode = nextMode;

    form.reset();
    showMessage("");

    const signup = nextMode === "signup";

    byId("authTitle").textContent = signup
        ? "Create your account"
        : "Welcome back";

    byId("authSubtitle").textContent = signup
        ? "Sign up to access your AI Research Agent account."
        : "Log in to your research account.";

    confirmWrap.hidden = !signup;

    confirmInput.required = signup;
    confirmInput.disabled = !signup;

    passwordInput.autocomplete = signup
        ? "new-password"
        : "current-password";

    forgotButton.hidden = signup;

    byId("authSwitchPrompt").textContent = signup
        ? "Already have an account?"
        : "New to AI Research Agent?";

    switchButton.textContent = signup
        ? "Log in"
        : "Create an account";

    submitButton.textContent = signup
        ? "Create account"
        : "Log in";
}


// ==========================================
// OPEN AUTH MODAL
// ==========================================

function openModal(mode = "login") {

    previousFocus = document.activeElement;

    setMode(mode);

    modal.hidden = false;

    document.body.classList.add(
        "auth-modal-open"
    );

    window.requestAnimationFrame(() => {
        emailInput.focus();
    });
}


// ==========================================
// CLOSE AUTH MODAL
// ==========================================

function closeModal() {

    if (busy) return;

    modal.hidden = true;

    document.body.classList.remove(
        "auth-modal-open"
    );

    previousFocus?.focus?.();
}


// ==========================================
// CLOSE USER DROPDOWN
// ==========================================

function closeUserDropdown() {

    userDropdown.hidden = true;

    userMenuButton.setAttribute(
        "aria-expanded",
        "false"
    );
}


// ==========================================
// LOGIN / SIGN UP BUTTON EVENTS
// ==========================================

byId("openLoginBtn").addEventListener(
    "click",
    () => openModal("login")
);

byId("openSignupBtn").addEventListener(
    "click",
    () => openModal("signup")
);

byId("authCloseBtn").addEventListener(
    "click",
    closeModal
);


// CLOSE WHEN CLICKING OUTSIDE THE MODAL

modal.addEventListener("click", (event) => {

    if (event.target === modal) {
        closeModal();
    }

});


// SWITCH BETWEEN LOGIN AND SIGN UP

switchButton.addEventListener("click", () => {

    if (busy) return;

    setMode(
        currentMode === "login"
            ? "signup"
            : "login"
    );

});


// ==========================================
// ESCAPE KEY HANDLING
// ==========================================

document.addEventListener("keydown", (event) => {

    if (event.key !== "Escape") return;

    if (!modal.hidden) {
        closeModal();
    } else {
        closeUserDropdown();
    }

});


// ==========================================
// MODAL KEYBOARD FOCUS
// ==========================================

dialog.addEventListener("keydown", (event) => {

    if (event.key !== "Tab") return;

    const focusable = [
        ...dialog.querySelectorAll(
            "button:not([disabled]):not([hidden]), input:not([disabled]):not([hidden])"
        )
    ].filter((element) => !element.closest("[hidden]"));

    if (!focusable.length) return;

    const first = focusable[0];
    const last = focusable[focusable.length - 1];

    if (
        event.shiftKey &&
        document.activeElement === first
    ) {
        event.preventDefault();
        last.focus();
    } else if (
        !event.shiftKey &&
        document.activeElement === last
    ) {
        event.preventDefault();
        first.focus();
    }

});


// ==========================================
// GOOGLE LOGIN
// ==========================================

googleButton.addEventListener(
    "click",
    async () => {

        if (busy) return;

        setBusy(true);
        showMessage("");

        try {

            await loginWithGoogle();

            setBusy(false);

            closeModal();

        } catch (error) {

            showMessage(
                readableError(error)
            );

        } finally {

            setBusy(false);

        }

    }
);


// ==========================================
// EMAIL LOGIN / SIGN UP
// ==========================================

form.addEventListener(
    "submit",
    async (event) => {

        event.preventDefault();

        if (busy) return;

        const email = emailInput.value.trim();
        const password = passwordInput.value;

        if (
            !email ||
            !emailInput.validity.valid
        ) {

            showMessage(
                "Please enter a valid email address."
            );

            return;
        }

        if (password.length < 6) {

            showMessage(
                "Your password must be at least 6 characters."
            );

            return;
        }

        if (
            currentMode === "signup" &&
            password !== confirmInput.value
        ) {

            showMessage(
                "Passwords do not match."
            );

            return;
        }

        setBusy(true);
        showMessage("");

        try {

            if (currentMode === "signup") {

                await registerWithEmail(
                    email,
                    password
                );

            } else {

                await loginWithEmail(
                    email,
                    password
                );

            }

            setBusy(false);
            closeModal();

        } catch (error) {

            showMessage(
                readableError(error)
            );

        } finally {

            setBusy(false);

        }

    }
);


// ==========================================
// FORGOT PASSWORD
// ==========================================

forgotButton.addEventListener(
    "click",
    async () => {

        if (busy) return;

        const email = emailInput.value.trim();

        if (
            !email ||
            !emailInput.validity.valid
        ) {

            showMessage(
                "Enter your email address above, then select Forgot password."
            );

            emailInput.focus();

            return;
        }

        setBusy(true);
        showMessage("");

        try {

            await sendPasswordResetEmail(
                auth,
                email
            );

            showMessage(
                "If an account exists for this email, a password reset email will be sent.",
                true
            );

        } catch (error) {

            showMessage(
                readableError(error)
            );

        } finally {

            setBusy(false);

        }

    }
);


// ==========================================
// USER MENU
// ==========================================

userMenuButton.addEventListener("click", () => {

    const isOpen = !userDropdown.hidden;

    userDropdown.hidden = isOpen;

    userMenuButton.setAttribute(
        "aria-expanded",
        String(!isOpen)
    );

});


// CLOSE USER MENU WHEN CLICKING OUTSIDE

document.addEventListener("click", (event) => {

    if (
        !byId("authUserMenu").contains(
            event.target
        )
    ) {
        closeUserDropdown();
    }

});


// ==========================================
// LOGOUT
// ==========================================

byId("authLogoutBtn").addEventListener(
    "click",
    async () => {

        try {

            byId("authLogoutBtn").disabled = true;

            await logoutUser();

            closeUserDropdown();

        } catch (error) {

            alert(
                readableError(error)
            );

        } finally {

            byId("authLogoutBtn").disabled = false;

        }

    }
);


// ==========================================
// FIREBASE LOGIN STATE
// ==========================================

observeAuthState((user) => {

    byId("authGuestActions").hidden = Boolean(user);

    byId("authUserMenu").hidden = !user;

    if (!user) {

        closeUserDropdown();

        return;
    }

    const fullName =
        user.displayName ||
        user.email?.split("@")[0] ||
        "My account";

    byId("authUserLabel").textContent =
        fullName;

    byId("authUserEmail").textContent =
        user.email || "Google Account";

    byId("authUserAvatar").textContent =
        fullName.trim().charAt(0).toUpperCase() || "U";

});
