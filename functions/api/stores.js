export async function onRequestGet(context) {
  const { env } = context;
  const { results } = await env.DB.prepare(
    `SELECT * FROM stores ORDER BY tienda`
  ).all();

  return Response.json(results);
}

export async function onRequestPost(context) {
  const { env, request } = context;
  const body = await request.json();

  await env.DB.prepare(`
    INSERT INTO stores (id, cod_sap, cliente, tienda, codigo_cliente, cliente_def, actividad)
    VALUES (?, ?, ?, ?, ?, ?, ?)
  `).bind(
    body.id,
    body.cod_sap || "",
    body.cliente || "",
    body.tienda || "",
    body.codigo_cliente || "",
    body.cliente_def || "",
    body.actividad || "Activo"
  ).run();

  return Response.json({ ok: true });
}

export async function onRequestDelete(context) {
  const { env, request } = context;
  const url = new URL(request.url);
  const id = url.searchParams.get("id");
  if (id) {
    await env.DB.prepare(`DELETE FROM stores WHERE id = ?`).bind(id).run();
    await env.DB.prepare(`DELETE FROM boxes WHERE store_id = ?`).bind(id).run();
    await env.DB.prepare(`DELETE FROM materials WHERE store_id = ?`).bind(id).run();
    return Response.json({ ok: true });
  }
  return Response.json({ ok: false }, { status: 400 });
}
