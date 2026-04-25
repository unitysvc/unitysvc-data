const { UNITYSVC_API_KEY, SERVICE_BASE_URL, MODEL } = process.env;

async function main() {
  const response = await fetch(SERVICE_BASE_URL, {
    method: "POST",
    headers: {
      Authorization: `Bearer ${UNITYSVC_API_KEY}`,
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      model: MODEL,
      input: ["Embed this sentence.", "As well as this one."],
    }),
  });
  if (!response.ok) {
    throw new Error(`HTTP ${response.status}: ${await response.text()}`);
  }
  const { data } = await response.json();
  console.log(`got ${data.length} embeddings of dimension ${data[0].embedding.length}`);
}

main().catch((err) => {
  console.error(err.message);
  process.exit(1);
});
