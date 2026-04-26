const { UNITYSVC_API_KEY, SERVICE_BASE_URL, MODEL } = process.env;

async function main() {
  const response = await fetch(`${SERVICE_BASE_URL}/chat/completions`, {
    method: "POST",
    headers: {
      Authorization: `Bearer ${UNITYSVC_API_KEY}`,
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      model: MODEL,
      messages: [
        { role: "system", content: "You are a helpful assistant." },
        { role: "user", content: "Say this is a test" },
      ],
    }),
  });
  if (!response.ok) {
    throw new Error(`HTTP ${response.status}: ${await response.text()}`);
  }
  const data = await response.json();
  console.log(data.choices[0].message.content);
}

main().catch((err) => {
  console.error(err.message);
  process.exit(1);
});
