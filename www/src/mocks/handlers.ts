import { http, HttpResponse } from "msw";

const encoder = new TextEncoder();

const delay = (ms: number) => new Promise((resolve) => setTimeout(resolve, ms));

export const handlers = [
  http.post("/predict_stream", async () => {
    const stream = new ReadableStream({
      async start(controller) {
        await delay(1000); // Initial delay
        controller.enqueue(
          encoder.encode(
            `Optimism is a Layer 2 scaling solution for Ethereum that uses optimistic rollup technology. Here are the key points about Optimism:




It is an "Optimistic Rollup", which means it bundles (or "rolls up") many Ethereum transactions into a single transaction on the Ethereum mainnet. This allows for much higher throughput and lower fees compared to transacting directly on Ethereum.




Optimism inherits the security of Ethereum's base layer while offering scalability improvements. It relies on Ethereum's consensus mechanism (proof-of-work or eventually proof-of-stake) rather than providing its own.




Optimism has a unique decentralized governance model with two chambers - the Token House and the Citizens' House. This allows for diverse stakeholder voices in decision-making around protocol upgrades and parameter changes.




It aims to stay as close to Ethereum as possible in terms of compatibility, simplicity, and design philosophy. This allows Optimism to benefit from improvements made to Ethereum over time.




The Optimism Collective is the decentralized autonomous organization (DAO) that governs the protocol. Token holders can participate in governance by voting on proposals.




In summary, Optimism is an Ethereum Layer 2 focused on scalability through optimistic rollups while maintaining decentralization and close compatibility with Ethereum.`
          )
        );

        await delay(1000); // Delay between chunks
        controller.enqueue(encoder.encode("New"));

        await delay(1000); // Delay between chunks
        controller.enqueue(encoder.encode("World"));
        controller.enqueue(encoder.encode("[END]"));

        controller.close();
      },
    });

    return new HttpResponse(stream, {
      headers: {
        "Content-Type": "text/plain",
      },
    });
  }),
];
