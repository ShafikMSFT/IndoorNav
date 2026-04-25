import { useMsal } from "@azure/msal-react";
import { apiScope } from "../authConfig";

/**
 * Hook to get an access token for API calls.
 * Silently acquires a token, falls back to popup if needed.
 */
export function useApi() {
  const { instance, accounts } = useMsal();

  async function getToken(): Promise<string | null> {
    if (accounts.length === 0) return null;

    try {
      const response = await instance.acquireTokenSilent({
        scopes: [apiScope],
        account: accounts[0],
      });
      return response.accessToken;
    } catch {
      const response = await instance.acquireTokenPopup({
        scopes: [apiScope],
      });
      return response.accessToken;
    }
  }

  async function apiFetch(path: string, options: RequestInit = {}): Promise<Response> {
    const token = await getToken();
    const headers: Record<string, string> = {
      ...(options.headers as Record<string, string>),
    };
    if (token) {
      headers["Authorization"] = `Bearer ${token}`;
    }
    return fetch(path, { ...options, headers });
  }

  return { getToken, apiFetch, accounts, instance };
}
