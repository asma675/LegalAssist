import OpenAI from "openai";

export const runtime = "nodejs"; // keep it on Node for stability on Vercel

const client = new OpenAI({
  apiKey: process.env.OPENAI_API_KEY,
});

export async function POST(req) {
  try {
    if (!process.env.OPENAI_API_KEY) {
      return Response.json(
        { error: "OPENAI_API_KEY is not set" },
        { status: 400 }
      );
    }

    const body = await req.json();
    const { prompt, system } = body || {};

    if (!prompt || typeof prompt !== "string") {
      return Response.json(
        { error: "Missing prompt (string)" },
        { status: 400 }
      );
    }

    const model = process.env.OPENAI_MODEL || "gpt-4o-mini";

    // Use Responses API 
    const r = await client.responses.create({
      model,
      input: [
        ...(system ? [{ role: "system", content: system }] : []),
        { role: "user", content: prompt },
      ],
    });

    const text = r.output_text || "";
    return Response.json({ text });
  } catch (err) {
    return Response.json(
      { error: err?.message || "Generate failed" },
      { status: 500 }
    );
  }
}
