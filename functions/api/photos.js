export async function onRequestPost(context) {
  const { env, request } = context;
  const body = await request.json();

  await env.DB.prepare(`
    CREATE TABLE IF NOT EXISTS photos (
      id TEXT PRIMARY KEY,
      store_id TEXT NOT NULL,
      box_id TEXT NOT NULL,
      photo_data TEXT NOT NULL,
      created_at INTEGER
    )
  `).run();

  await env.DB.prepare(`
    INSERT INTO photos (id, store_id, box_id, photo_data, created_at)
    VALUES (?, ?, ?, ?, ?)
  `).bind(
    body.id,
    body.store_id,
    body.box_id,
    body.photo_data,
    Date.now()
  ).run();

  return Response.json({ ok: true });
}

export async function onRequestGet(context) {
  const { env, request } = context;
  const url = new URL(request.url);
  const storeId = url.searchParams.get("store_id");
  const boxId = url.searchParams.get("box_id");

  let query = `SELECT * FROM photos`;
  const filters = [];
  const binds = [];

  if (storeId) {
    filters.push(`store_id = ?`);
    binds.push(storeId);
  }
  if (boxId) {
    filters.push(`box_id = ?`);
    binds.push(boxId);
  }

  if (filters.length) {
    query += ` WHERE ` + filters.join(" AND ");
  }

  const stmt = env.DB.prepare(query).bind(...binds);
  const { results } = await stmt.all();

  return Response.json(results);
}

export async function onRequestDelete(context) {
  const { env, request } = context;
  const url = new URL(request.url);
  const id = url.searchParams.get('id');
  if (id) {
    await env.DB.prepare('DELETE FROM photos WHERE id = ?').bind(id).run();
    return Response.json({ ok: true });
  }
  return Response.json({ ok: false }, { status: 400 });
}
