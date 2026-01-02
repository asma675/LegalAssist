import OpenAI from "openai";

export const runtime = "nodejs"; // important for Vercel stability

const client = new OpenAI({
  apiKey: process.env.OPENAI_API_KEY,
});

export async function POST(req) {
  try {
    const body = await req.json();
    const { prompt, system } = body || {};

    if (!process.env.OPENAI_API_KEY) {
      return Response.json({ error: "Missing OPENAI_API_KEY" }, { status: 400 });
    }
    if (!prompt) {
      return Response.json({ error: "Missing prompt" }, { status: 400 });
    }

    const model = process.env.OPENAI_MODEL || "gpt-4o-mini";

    // Responses API (recommended modern endpoint)
    const r = await client.responses.create({
      model,
      input: [
        ...(system ? [{ role: "system", content: system }] : []),
        { role: "user", content: prompt },
      ],
    });

    // Safely extract text
    const text = r.output_text || "";
    return Response.json({ text });
  } catch (err) {
    return Response.json(
      { error: err?.message || "AI generate failed" },
      { status: 500 }
    );
  }
}
