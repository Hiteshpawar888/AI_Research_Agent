
/* ==========================================
   AI RESEARCH AGENT - FIREBASE AUTHENTICATION
========================================== */

import { initializeApp } from
  "https://www.gstatic.com/firebasejs/12.4.0/firebase-app.js";

import {
  getAuth,
  GoogleAuthProvider,
  signInWithPopup,
  createUserWithEmailAndPassword,
  signInWithEmailAndPassword,
  signOut,
  onAuthStateChanged
} from "https://www.gstatic.com/firebasejs/12.4.0/firebase-auth.js";


// ==========================================
// FIREBASE CONFIGURATION
// ==========================================

const firebaseConfig = {
  apiKey: "AIzaSyCUoT2GxsFD572apWPwcP0NB8jS5aOHCQ4",
  authDomain: "ai-research-agent-f00a9.firebaseapp.com",
  projectId: "ai-research-agent-f00a9",
  storageBucket: "ai-research-agent-f00a9.firebasestorage.app",
  messagingSenderId: "129217111860",
  appId: "1:129217111860:web:ebe1857c8fe8385c47e761",
  measurementId: "G-JC18T5SC5D"
};


// ==========================================
// INITIALIZE FIREBASE
// ==========================================

const app = initializeApp(firebaseConfig);

const auth = getAuth(app);

auth.useDeviceLanguage();


// ==========================================
// GOOGLE AUTHENTICATION
// ==========================================

const googleProvider = new GoogleAuthProvider();

googleProvider.setCustomParameters({
  prompt: "select_account"
});

async function loginWithGoogle() {
  const result = await signInWithPopup(
    auth,
    googleProvider
  );

  return result.user;
}


// ==========================================
// EMAIL SIGN UP
// ==========================================

async function registerWithEmail(email, password) {
  const result = await createUserWithEmailAndPassword(
    auth,
    email,
    password
  );

  return result.user;
}


// ==========================================
// EMAIL LOGIN
// ==========================================

async function loginWithEmail(email, password) {
  const result = await signInWithEmailAndPassword(
    auth,
    email,
    password
  );

  return result.user;
}


// ==========================================
// LOGOUT
// ==========================================

async function logoutUser() {
  await signOut(auth);
}


// ==========================================
// AUTHENTICATION STATE
// ==========================================

function observeAuthState(callback) {
  return onAuthStateChanged(auth, callback);
}


// ==========================================
// GET FIREBASE ID TOKEN
// For future FastAPI backend verification
// ==========================================

async function getUserToken() {
  const user = auth.currentUser;

  if (!user) {
    return null;
  }

  return await user.getIdToken();
}


// ==========================================
// EXPORT FUNCTIONS
// ==========================================

export {
  auth,
  googleProvider,
  loginWithGoogle,
  registerWithEmail,
  loginWithEmail,
  logoutUser,
  observeAuthState,
  getUserToken
};
