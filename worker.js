// Cloudflare Worker for passwords.tysonmediagroup.org
// Proxies API calls to my.tysonmediagroup.org edge storage & serves static staff password manager

export default {
  async fetch(request, env) {
    const url = new URL(request.url);

    // Proxy API requests to my.tysonmediagroup.org edge API
    if (url.pathname.startsWith("/api/")) {
      const targetUrl = new URL(url.pathname + url.search, "https://my.tysonmediagroup.org");
      const subReq = new Request(targetUrl.toString(), request);
      return fetch(subReq);
    }

    if (env && env.ASSETS) {
      return env.ASSETS.fetch(request);
    }
    return new Response("Not Found", { status: 404 });
  }
};
