const { OpenAI } = require("openai");

const client = new OpenAI({
  baseURL: process.env.SERVICE_BASE_URL,
  apiKey: process.env.UNITYSVC_API_KEY,
});

async function main() {
  const stream = await client.chat.completions.create({
    model: process.env.MODEL,
    messages: [
      { role: "system", content: "You are a helpful assistant." },
      { role: "user", content: "Say this is a test" },
    ],
    stream: true,
  });
  for await (const chunk of stream) {
    const delta = chunk.choices[0]?.delta?.content;
    if (delta) {
      process.stdout.write(delta);
    }
  }
  process.stdout.write("\n");
}

main().catch((err) => {
  console.error(err.message);
  process.exit(1);
});
