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

  let prompt;
  if (mode === 'name') {
    prompt = `This is a Porcelanosa showroom ambiente/box label. Near the top it shows the ambiente name such as "AMBIENTE 8 PORCELANOSA", "AMBIENTE 3", "BOX 1", "COULOIR", etc.
Extract ONLY the ambiente name or identifier shown on this label.
Return ONLY the name as plain text, nothing else. Example: "AMBIENTE 8 PORCELANOSA"
If you cannot read a clear name, return an empty string.`;
  } else {
    prompt = `This is a Porcelanosa product label (etiqueta de ambiente) listing products with their codes.
The label contains numeric product codes that are exactly 9 digits long, always starting with "100" followed by 6 more digits (e.g. 100562400, 100570014, 100416031, 100419471).
These codes appear at the START of each product line, before the product description.
There can be 5 to 30 codes in a single label, organized in sections like "Revestimiento" and "Pavimento".

Your task: read the label carefully and extract EVERY 9-digit numeric code that starts with 100.
Return ONLY a valid JSON array of strings with ALL the codes you find.
Example: ["100562400","100570014","100416031","100419471","100552499"]
If no codes found, return: []
Do not include any explanation, only the JSON array.`;
  }

  const response = await fetch('https://openrouter.ai/api/v1/chat/completions', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${OPENROUTER_API_KEY}`
    },
    body: JSON.stringify({
      model: 'google/gemini-flash-1.5',
      max_tokens: 1024,
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
    return Response.json({ sap_codes: [], error: 'AI analysis failed: ' + errText }, { status: 500 });
  }

  const data = await response.json();
  const text = (data.choices?.[0]?.message?.content || '').trim();

  if (mode === 'name') {
    return Response.json({ name: text });
  }

  let sap_codes = [];
  try {
    const match = text.match(/\[[\s\S]*\]/);
    if (match) {
      sap_codes = JSON.parse(match[0]);
    } else {
      // Fallback: extract all 9-digit codes starting with 100 from raw text
      const found = text.match(/\b100\d{6}\b/g);
      if (found) sap_codes = [...new Set(found)];
    }
  } catch (e) {
    // Fallback: extract codes directly from text
    const found = text.match(/\b100\d{6}\b/g);
    if (found) sap_codes = [...new Set(found)];
    console.error('Parse error, used fallback. Raw text:', text);
  }

  return Response.json({ sap_codes });
}
