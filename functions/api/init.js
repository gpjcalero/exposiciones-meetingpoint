export async function onRequestGet(context) {
  const { env } = context;

  const queries = [
    `CREATE TABLE IF NOT EXISTS stores (
      id TEXT PRIMARY KEY,
      pais TEXT,
      cod_sap TEXT,
      cliente TEXT,
      tienda TEXT,
      codigo_cliente TEXT,
      cliente_def TEXT,
      actividad TEXT
    )`,
    `CREATE TABLE IF NOT EXISTS boxes (
      id TEXT PRIMARY KEY,
      store_id TEXT NOT NULL,
      name TEXT NOT NULL
    )`,
    `CREATE TABLE IF NOT EXISTS materials (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      store_id TEXT NOT NULL,
      box_id TEXT NOT NULL,
      sap_code TEXT NOT NULL,
      location TEXT,
      date TEXT,
      status TEXT,
      notes TEXT
    )`,
    `CREATE TABLE IF NOT EXISTS logs (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      store_id TEXT,
      box_id TEXT,
      sap_code TEXT,
      location TEXT,
      ts INTEGER
    )`
  ];

  for (const q of queries) {
    await env.DB.prepare(q).run();
  }

  // Migration: add pais column if missing
  try {
    await env.DB.prepare(`ALTER TABLE stores ADD COLUMN pais TEXT DEFAULT ''`).run();
  } catch (e) { /* column already exists */ }

  return Response.json({ ok: true });
}
