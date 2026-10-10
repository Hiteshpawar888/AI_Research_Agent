
import {
    auth,
    getUserToken
} from "./firebase_auth.js";

const originalFetch = window.fetch.bind(window);

window.fetch = async (resource, options = {}) => {

    const requestUrl = new URL(
        resource instanceof Request
            ? resource.url
            : String(resource),
        window.location.href
    );

    const protectedEndpoint =
        requestUrl.origin === window.location.origin &&
        (
            requestUrl.pathname === "/upload" ||
            requestUrl.pathname === "/ask"
        );

    if (!protectedEndpoint) {
        return originalFetch(resource, options);
    }

    await auth.authStateReady();

    const token = await getUserToken();

    if (!token) {

        document.getElementById("openLoginBtn")?.click();

        const message =
            "Please log in before uploading or researching.";

        return new Response(
            JSON.stringify({
                success: false,
                message,
                answer: message
            }),
            {
                status: 401,
                headers: {
                    "Content-Type": "application/json"
                }
            }
        );
    }

    const headers = new Headers(
        resource instanceof Request
            ? resource.headers
            : undefined
    );

    new Headers(options?.headers).forEach(
        (value, name) => {
            headers.set(name, value);
        }
    );

    headers.set(
        "Authorization",
        `Bearer ${token}`
    );

    return originalFetch(
        resource,
        {
            ...options,
            headers
        }
    );
};
