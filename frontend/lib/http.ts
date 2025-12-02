import { API_URL } from './utils';

type FetchOptions = RequestInit & {
    params?: Record<string, string | number | boolean | undefined>;
};

export async function http<T>(path: string, options: FetchOptions = {}): Promise<T> {
    const { params, ...init } = options;

    // Construct URL
    // If path is already a full URL, use it. Otherwise append to API_URL.
    const baseUrl = path.startsWith('http') ? path : `${API_URL}${path.startsWith('/') ? '' : '/'}${path}`;
    const url = new URL(baseUrl);

    if (params) {
        Object.entries(params).forEach(([key, value]) => {
            if (value !== undefined && value !== null) {
                url.searchParams.append(key, String(value));
            }
        });
    }

    const headers = new Headers(init.headers);

    // Set Content-Type to application/json by default if body is not FormData
    if (!headers.has('Content-Type') && !(init.body instanceof FormData)) {
        headers.set('Content-Type', 'application/json');
    }

    // Handle Authorization token
    if (typeof window === 'undefined') {
        // Server-side: Get token from cookies
        try {
            const { cookies } = await import('next/headers');
            const cookieStore = await cookies();
            const token = cookieStore.get('token')?.value;
            if (token) {
                headers.set('Authorization', `Bearer ${token}`);
            }
        } catch {
            // Fallback or ignore if not in a request context
        }
    } else {
        // Client-side:
        // If the token is stored in a non-httpOnly cookie, we could read it here.
        // If it's httpOnly, we rely on `credentials: 'include'` to send the cookie.
        // However, if the backend strictly requires `Authorization: Bearer`, client-side fetch might fail
        // unless we have a proxy or middleware.
        // For now, we assume the backend might accept cookies OR we are using this mostly in Server Actions.
        // We'll set credentials to include to send cookies.
        // init.credentials = 'include'; // This is often needed for CORS with cookies
    }

    const config: RequestInit = {
        ...init,
        headers,
        // credentials: 'include', // Uncomment if cross-origin cookies are needed
    };

    try {
        const response = await fetch(url.toString(), config);

        if (!response.ok) {
            const errorData = await response.json().catch(() => ({}));
            throw new Error(errorData.detail || errorData.message || `Request failed with status ${response.status}`);
        }

        // Return null for 204 No Content
        if (response.status === 204) {
            return null as T;
        }

        return response.json();
    } catch (error) {
        console.error(`HTTP Request failed: ${path}`, error);
        throw error;
    }
}
