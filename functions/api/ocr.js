export async function onRequestPost(context) {
  const { env, request } = context;
  const body = await request.json();
  const { image_base64, mime_type, mode } = body;

  if (!image_base64) {
    return Response.json({ error: 'No image provided' }, { status: 400 });
  }

  const OPENROUTER_API_KEY = env.OPENROUTER_API_KEY;
  if (!OPENROUTER_API_KEY) {
    return Response.json({ sap_codes: [], error: 'OPENROUTER_API_KEY not set in Cloudflare environment variables' }, { status: 500 });
  }

  const dataUrl = `data:${mime_type || 'image/jpeg'};base64,${image_base64}`;

  let prompt;
  if (mode === 'name') {
    prompt = `This is a Porcelanosa showroom ambiente/box label. Near the top it shows the ambiente name such as "AMBIENTE 8 PORCELANOSA", "AMBIENTE 3", "BOX 1", "COULOIR", etc.
Extract ONLY the ambiente name or identifier shown on this label.
Return ONLY the name as plain text, nothing else. Example: "AMBIENTE 8 PORCELANOSA"
If you cannot read a clear name, return an empty string.`;
  } else {
    prompt = `This is a Porcelanosa product label listing showroom products. It contains numeric product codes that are exactly 9 digits long, always starting with "100" followed by 6 more digits (e.g. 100562400, 100570014, 100416031).
These codes appear at the START of each product line, before the product description text.
The label has sections titled "Revestimiento" and "Pavimento" with many products listed.

Extract EVERY 9-digit numeric code starting with 100 from this label.
Return ONLY a valid JSON array of strings. Example: ["100562400","100570014","100416031","100419471"]
No explanation, only the JSON array. If none found, return: []`;
  }

  const response = await fetch('https://openrouter.ai/api/v1/chat/completions', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${OPENROUTER_API_KEY}`,
      'HTTP-Referer': 'https://exposiciones-meetingpoint.pages.dev',
      'X-Title': 'Porcelanosa Audit'
    },
    body: JSON.stringify({
      model: 'openai/gpt-4o-mini',
      max_tokens: 1024,
      messages: [{
        role: 'user',
        content: [
          {
            type: 'image_url',
            image_url: { url: dataUrl, detail: 'high' }
          },
          {
            type: 'text',
            text: prompt
          }
        ]
      }]
    })
  });

  const responseText = await response.text();

  if (!response.ok) {
    console.error('OpenRouter API error:', response.status, responseText);
    return Response.json({ sap_codes: [], error: `API error ${response.status}: ${responseText.slice(0, 200)}` }, { status: 500 });
  }

  let data;
  try { data = JSON.parse(responseText); } catch(e) {
    return Response.json({ sap_codes: [], error: 'Invalid JSON from API: ' + responseText.slice(0, 200) }, { status: 500 });
  }

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
      const found = text.match(/\b100\d{6}\b/g);
      if (found) sap_codes = [...new Set(found)];
    }
  } catch (e) {
    const found = text.match(/\b100\d{6}\b/g);
    if (found) sap_codes = [...new Set(found)];
    console.error('Parse error, fallback used. Raw:', text);
  }

  return Response.json({ sap_codes });
}
