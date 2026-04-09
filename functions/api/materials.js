export async function onRequestGet(context) {
  const { env, request } = context;
  const url = new URL(request.url);

  const storeId = url.searchParams.get("store_id");
  const boxId = url.searchParams.get("box_id");

  let query = `SELECT * FROM materials`;
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

  query += ` ORDER BY id DESC`;

  const stmt = env.DB.prepare(query).bind(...binds);
  const { results } = await stmt.all();

  return Response.json(results);
}

export async function onRequestPost(context) {
  const { env, request } = context;
  const body = await request.json();

  await env.DB.prepare(`
    INSERT INTO materials (store_id, box_id, sap_code, location, date, status, notes)
    VALUES (?, ?, ?, ?, ?, ?, ?)
  `).bind(
    body.store_id,
    body.box_id,
    body.sap_code,
    body.location || "",
    body.date || "",
    body.status || "ACTIVO",
    body.notes || ""
  ).run();

  await env.DB.prepare(`
    INSERT INTO logs (store_id, box_id, sap_code, location, ts)
    VALUES (?, ?, ?, ?, ?)
  `).bind(
    body.store_id,
    body.box_id,
    body.sap_code,
    body.location || "",
    Date.now()
  ).run();

  return Response.json({ ok: true });
}

export async function onRequestDelete(context) {
  const { env, request } = context;
  const url = new URL(request.url);
  const sap = url.searchParams.get("sap");
  const boxId = url.searchParams.get("box_id");
  if (sap && boxId) {
    await env.DB.prepare(`DELETE FROM materials WHERE sap_code = ? AND box_id = ?`).bind(sap, boxId).run();
    return Response.json({ ok: true });
  }
  return Response.json({ ok: false }, { status: 400 });
}
