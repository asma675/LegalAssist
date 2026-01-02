import OpenAI from "openai";

export const runtime = "nodejs";

const client = new OpenAI({
  apiKey: process.env.OPENAI_API_KEY,
});

// Small helper to extract JSON even if model wraps it in text
function extractJson(text) {
  if (!text) return null;

  // Try direct parse first
  try {
    return JSON.parse(text);
  } catch {}

  // Try to find first JSON object in the text
  const start = text.indexOf("{");
  const end = text.lastIndexOf("}");
  if (start >= 0 && end > start) {
    const maybe = text.slice(start, end + 1);
    try {
      return JSON.parse(maybe);
    } catch {}
  }

  return null;
}

export async function POST(req) {
  try {
    if (!process.env.OPENAI_API_KEY) {
      return Response.json(
        { error: "OPENAI_API_KEY is not set" },
        { status: 400 }
      );
    }

    const body = await req.json();
    const { text } = body || {};

    if (!text || typeof text !== "string") {
      return Response.json({ error: "Missing text (string)" }, { status: 400 });
    }

    const model = process.env.OPENAI_MODEL || "gpt-4o-mini";

    const system = `
You are a careful legal assistant. Analyze the provided document text.
Return ONLY valid JSON in this exact schema:

{
  "summary": "string",
  "risks": ["string", "..."],
  "clauses": [{"name": "string", "excerpt": "string"}],
  "recommendations": ["string", "..."]
}

Rules:
- Be concise and practical.
- If the text is missing details, note that in risks/recommendations.
- Do not add extra keys.
`.trim();

    const r = await client.responses.create({
      model,
      input: [
        { role: "system", content: system },
        { role: "user", content: text },
      ],
    });

    const out = r.output_text || "";
    const parsed = extractJson(out);

    // Fallback if model returns plain text for any reason
    if (!parsed) {
      return Response.json({
        summary: out || "No summary returned.",
        risks: [],
        clauses: [],
        recommendations: [],
      });
    }

    // Ensure shape is always present (extra-safe)
    return Response.json({
      summary: parsed.summary || "",
      risks: Array.isArray(parsed.risks) ? parsed.risks : [],
      clauses: Array.isArray(parsed.clauses) ? parsed.clauses : [],
      recommendations: Array.isArray(parsed.recommendations)
        ? parsed.recommendations
        : [],
    });
  } catch (err) {
    return Response.json(
      { error: err?.message || "Analyze failed" },
      { status: 500 }
    );
  }
}
