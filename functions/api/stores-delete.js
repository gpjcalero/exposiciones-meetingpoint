export async function onRequestDelete(context) {
    const { env, request } = context;
    const url = new URL(request.url);
    const id = url.searchParams.get("id");
    if (id) {
        await env.DB.prepare(`DELETE FROM stores WHERE id = ?`).bind(id).run();
        await env.DB.prepare(`DELETE FROM boxes WHERE store_id = ?`).bind(id).run();
        await env.DB.prepare(`DELETE FROM materials WHERE store_id = ?`).bind(id).run();
        await env.DB.prepare(`DELETE FROM photos WHERE store_id = ?`).bind(id).run();
        return Response.json({ ok: true });
    }
    return Response.json({ ok: false }, { status: 400 });
}
