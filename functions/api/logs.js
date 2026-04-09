export async function onRequestGet(context) {
    const { env } = context;
    const { results } = await env.DB.prepare(`SELECT * FROM logs ORDER BY id DESC LIMIT 100`).all();
    return Response.json(results);
}
