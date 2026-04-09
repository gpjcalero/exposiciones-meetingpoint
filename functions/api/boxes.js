export async function onRequestGet(context) {
  const { env, request } = context;
  const url = new URL(request.url);
  const storeId = url.searchParams.get("store_id");

  let query = `SELECT * FROM boxes`;
  let stmt;

  if (storeId) {
    query += ` WHERE store_id = ? ORDER BY name`;
    stmt = env.DB.prepare(query).bind(storeId);
  } else {
    query += ` ORDER BY name`;
    stmt = env.DB.prepare(query);
  }

  const { results } = await stmt.all();
  return Response.json(results);
}

export async function onRequestPost(context) {
  const { env, request } = context;
  const body = await request.json();

  await env.DB.prepare(`
    INSERT INTO boxes (id, store_id, name)
    VALUES (?, ?, ?)
  `).bind(
    body.id,
    body.store_id,
    body.name
  ).run();

  return Response.json({ ok: true });
}

export async function onRequestDelete(context) {
  const { env, request } = context;
  const url = new URL(request.url);
  const id = url.searchParams.get("id");
  if (id) {
    await env.DB.prepare(`DELETE FROM boxes WHERE id = ?`).bind(id).run();
    await env.DB.prepare(`DELETE FROM materials WHERE box_id = ?`).bind(id).run();
    return Response.json({ ok: true });
  }
  return Response.json({ ok: false }, { status: 400 });
}
