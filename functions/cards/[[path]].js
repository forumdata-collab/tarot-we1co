// Serve tarot card images from R2 bucket (deck/<file>.jpg)
// Route: /cards/<filename>
export async function onRequestGet({ env, request, params }) {
  const origin = request.headers.get("Origin") || "";
  const cors = {
    "Access-Control-Allow-Origin": origin || "*",
    "Access-Control-Allow-Methods": "GET, HEAD, OPTIONS",
    "Access-Control-Max-Age": "86400",
  };
  if (request.method === "OPTIONS") {
    return new Response(null, { status: 204, headers: cors });
  }
  const key = (params.path || []).join("/");
  if (!key || key.includes("..") || key.includes("/")) {
    return new Response("bad request", { status: 400, headers: cors });
  }
  const obj = await env.TAROT_CARDS.get("deck/" + key);
  if (!obj) {
    return new Response("not found", { status: 404, headers: cors });
  }
  const headers = new Headers(cors);
  obj.writeHttpMetadata(headers);
  headers.set("etag", obj.httpEtag);
  headers.set("Cache-Control", "public, max-age=86400, immutable");
  return new Response(obj.body, { headers });
}
