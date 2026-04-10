export async function onRequestPost(context) {
  const { env, request } = context;
  const body = await request.json();
  const { image_base64, mime_type, mode } = body;

  if (!image_base64) {
    return Response.json({ error: 'No image provided' }, { status: 400 });
  }

  const OPENROUTER_API_KEY = env.OPENROUTER_API_KEY;
  if (!OPENROUTER_API_KEY) {
    return Response.json({ sap_codes: [], error: 'API key not configured' }, { status: 500 });
  }

  const dataUrl = `data:${mime_type || 'image/jpeg'};base64,${image_base64}`;

  const prompt = mode === 'name'
    ? 'Look at this image of a showroom ambiente/box label. Extract the name or identifier of the ambiente (e.g. "BOX 1", "COULOIR", "HALL", "SALLE DE BAIN", etc.). Return ONLY the name as a plain string, nothing else. If you cannot determine a name, return an empty string.'
    : 'Look at this image of product labels or showroom display tags. Extract ALL SAP codes visible in the image. SAP codes are numeric codes, typically 6-10 digits long (e.g. 100336896, 1222347). Return ONLY a valid JSON array of the SAP code strings found, with no explanation. Example output: ["100336896","100412347"]. If no SAP codes are visible, return: []';

  const response = await fetch('https://openrouter.ai/api/v1/chat/completions', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${OPENROUTER_API_KEY}`
    },
    body: JSON.stringify({
      model: 'google/gemini-flash-1.5',
      max_tokens: 512,
      messages: [{
        role: 'user',
        content: [
          {
            type: 'image_url',
            image_url: { url: dataUrl }
          },
          {
            type: 'text',
            text: prompt
          }
        ]
      }]
    })
  });

  if (!response.ok) {
    const errText = await response.text();
    console.error('OpenRouter API error:', errText);
    return Response.json({ sap_codes: [], error: 'AI analysis failed' }, { status: 500 });
  }

  const data = await response.json();
  const text = (data.choices?.[0]?.message?.content || '').trim();

  // Name mode: return the detected name
  if (mode === 'name') {
    return Response.json({ name: text });
  }

  // SAP mode: parse JSON array from response
  let sap_codes = [];
  try {
    const match = text.match(/\[[\s\S]*\]/);
    if (match) sap_codes = JSON.parse(match[0]);
  } catch (e) {
    console.error('Parse error:', e, 'Raw text:', text);
  }

  return Response.json({ sap_codes });
}
