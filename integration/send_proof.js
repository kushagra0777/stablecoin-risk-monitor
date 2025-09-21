// send_proof.js
// Script to send a Merkle proof to a deployed contract using ethers.js

import { ethers } from "ethers";
import dotenv from "dotenv";
import fs from "fs";
dotenv.config();

// Load contract ABI and address (use only the ABI property from the artifact)
const artifact = JSON.parse(fs.readFileSync("../blockchain_layer/contracts/ProofOfReserves.json"));
const CONTRACT_ABI = artifact.abi;
const CONTRACT_ADDRESS = process.env.CONTRACT_ADDRESS;

// Load Merkle proof and root (replace with actual data or import from Python output)
const merkleRoot = process.env.MERKLE_ROOT;
const proof = JSON.parse(process.env.MERKLE_PROOF || "[]");
const leaf = process.env.MERKLE_LEAF;

async function main() {
  const provider = new ethers.JsonRpcProvider(process.env.RPC_URL || "http://127.0.0.1:8545");
  const signer = new ethers.Wallet(process.env.PRIVATE_KEY, provider);
  const contract = new ethers.Contract(CONTRACT_ADDRESS, CONTRACT_ABI, signer);

  // Call updateRoot with the Merkle root
  const tx1 = await contract.updateRoot(merkleRoot);
  console.log("updateRoot transaction hash:", tx1.hash);
  await tx1.wait();
  console.log("Merkle root updated!");

  // Call verifyProof with total reserves (from .env or hardcoded for now)
  const totalReserves = process.env.TOTAL_RESERVES;
  if (!totalReserves) {
    console.warn("TOTAL_RESERVES not set in .env. Skipping verifyProof call.");
    return;
  }
  const tx2 = await contract.verifyProof(totalReserves);
  console.log("verifyProof transaction hash:", tx2.hash);
  await tx2.wait();
  console.log("Proof verified!");
}

main().catch((err) => {
  console.error(err);
  process.exit(1);
});
