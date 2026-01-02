import OpenAI from "openai";

export const runtime = "nodejs";

const client = new OpenAI({
  apiKey: process.env.OPENAI_API_KEY,
});

export async function POST(req) {
  try {
    const body = await req.json();
    const { text } = body || {};

    if (!process.env.OPENAI_API_KEY) {
      return Response.json({ error: "Missing OPENAI_API_KEY" }, { status: 400 });
    }
    if (!text) {
      return Response.json({ error: "Missing text" }, { status: 400 });
    }

    const model = process.env.OPENAI_MODEL || "gpt-4o-mini";

    const system =
      "You are a legal assistant. Analyze the text and return JSON with keys: summary, risks (array), clauses (array of {name, excerpt}), and recommendations (array). Keep it concise.";

    const r = await client.responses.create({
      model,
      input: [
        { role: "system", content: system },
        { role: "user", content: text },
      ],
    });

    const out = r.output_text || "";

    // Try JSON parse; if model returns plain text, wrap it.
    let parsed;
    try {
      parsed = JSON.parse(out);
    } catch {
      parsed = { summary: out, risks: [], clauses: [], recommendations: [] };
    }

    return Response.json(parsed);
  } catch (err) {
    return Response.json(
      { error: err?.message || "AI analyze failed" },
      { status: 500 }
    );
  }
}
