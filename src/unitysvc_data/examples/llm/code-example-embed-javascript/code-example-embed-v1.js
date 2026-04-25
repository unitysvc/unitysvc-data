const { UNITYSVC_API_KEY, SERVICE_BASE_URL, MODEL } = process.env;
for (const name of ["UNITYSVC_API_KEY", "SERVICE_BASE_URL", "MODEL"]) {
  if (!process.env[name]) {
    console.error(`${name} is not set`);
    process.exit(1);
  }
}

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
    const text = await response.text();
    console.error(`Error ${response.status}: ${text}`);
    process.exit(1);
  }

  const data = await response.json();
  for (const item of data.data || []) {
    const vec = item.embedding || [];
    console.log(`index=${item.index} dim=${vec.length} first3=${vec.slice(0, 3)}`);
  }
}

main().catch((err) => {
  console.error("API request failed:", err);
  process.exit(1);
});
