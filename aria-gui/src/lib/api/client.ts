export async function sendChatMessage(
  prompt: string,
  model = 'gemini-2.5-flash',
  temperature = 0.1,
  maxTokens = 600
): Promise<string> {
  const apiKey = import.meta.env.VITE_GOOGLE_API_KEY
  if (!apiKey) throw new Error('VITE_GOOGLE_API_KEY not set')

  const res = await fetch(
    `https://generativelanguage.googleapis.com/v1beta/models/${model}:generateContent?key=${apiKey}`,
    {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        contents: [{ parts: [{ text: prompt }] }],
        generationConfig: { temperature, maxOutputTokens: maxTokens },
      }),
    }
  )
  if (!res.ok) throw new Error(`API error ${res.status}: ${await res.text()}`)
  const data = await res.json()
  return data.candidates?.[0]?.content?.parts?.[0]?.text || ''
}
