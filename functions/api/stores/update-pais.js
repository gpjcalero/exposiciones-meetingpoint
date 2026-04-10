export async function onRequestPost(context) {
  const { env, request } = context;
  const { id, pais } = await request.json();
  if (!id) return Response.json({ ok: false }, { status: 400 });

  await env.DB.prepare(`UPDATE stores SET pais = ? WHERE id = ?`)
    .bind(pais || '', id)
    .run();

  return Response.json({ ok: true });
}
