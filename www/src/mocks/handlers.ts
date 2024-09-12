import { http, HttpResponse } from "msw";

const encoder = new TextEncoder();

const delay = (ms: number) => new Promise((resolve) => setTimeout(resolve, ms));

const randomDelay = (min: number, max: number) =>
  delay(Math.floor(Math.random() * (max - min + 1) + min));

const streamText = async (
  text: string,
  controller: ReadableStreamDefaultController,
) => {
  const words = text.split(" ");
  for (const word of words) {
    await randomDelay(10, 50); // Simulate variable typing speed
    controller.enqueue(encoder.encode(`${word} `));
  }
};

export const handlers = [
  http.post("/predict_stream", async ({ request }) => {
    // @ts-expect-error
    const { shouldError } = await request.json();

    await delay(1_000);

    const stream = new ReadableStream({
      async start(controller) {
        if (shouldError) {
          await delay(50);
          controller.error(new Error("Simulated error in stream"));
          return;
        }

        const content = `Optimism is a Layer 2 scaling solution for Ethereum that uses optimistic rollup technology. Here are the key points about Optimism:

1. It is an "Optimistic Rollup", bundling many Ethereum transactions into a single transaction on the Ethereum mainnet.

2. Optimism inherits Ethereum's security while offering scalability improvements.

3. It has a unique decentralized governance model with two chambers - the Token House and the Citizens' House.

4. Optimism aims to stay as close to Ethereum as possible in terms of compatibility and design philosophy.

5. The Optimism Collective is the DAO that governs the protocol, allowing token holders to participate in governance.

In summary, Optimism is an Ethereum Layer 2 focused on scalability through optimistic rollups while maintaining decentralization and close compatibility with Ethereum.`;

        await streamText(content, controller);

        await randomDelay(10, 100);
        controller.enqueue(encoder.encode("[DONE]\n"));
        controller.close();
      },
    });

    return new HttpResponse(stream, {
      headers: {
        "Content-Type": "text/plain",
      },
    });
  }),

  http.post("/predict", async ({ request }) => {
    // @ts-expect-error
    const { shouldError, memory, question } = await request.json();

    await delay(1_000);

    if (shouldError) {
      return new HttpResponse(
        JSON.stringify({ message: "Simulated error in stream" }),
        {
          status: 500,
          statusText: "Internal Server Error",
          headers: {
            "Content-Type": "application/json",
          },
        },
      );
    }

    const response = {
      data: {
        answer:
          "The OP token distribution is structured to support various initiatives within the Optimism ecosystem. Key allocations include:\n\n- **19%** for airdrops\n- **20%** for retroactive public goods funding (retroPGF)\n- **25%** for ecosystem funding\n- **17%** for investors\n- **19%** for core contributors\n\nAdditionally, specific proposals, such as one from Beefy Finance, have requested OP tokens for liquidity incentives, with detailed allocations: **35%** for farm incentives, **50%** for boosting native farms, and **15%** for developer incentives. Changes to these allocations require approval from the Collective governance, ensuring community involvement in the decision-making process.",
        url_supporting: [
          "https://gov.optimism.io/t/clarification-on-op-token-supply/5589",
          "https://gov.optimism.io/t/ready-gf-phase-1-proposal-beefy/2967",
        ],
      },
      error: null,
    };

    return new HttpResponse(JSON.stringify(response), {
      headers: {
        "Content-Type": "application/json",
      },
    });
  }),
];
