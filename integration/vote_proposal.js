// vote_proposal.js
// Script to vote on a governance proposal using ethers.js

import { ethers } from "ethers";
import dotenv from "dotenv";
import fs from "fs";
dotenv.config();

// Load contract ABI and address (update as needed)
const DAO_ABI = JSON.parse(fs.readFileSync("../blockchain_layer/contracts/GovernanceDAO.json"));
const DAO_ADDRESS = process.env.DAO_CONTRACT_ADDRESS;

// Voting parameters
const proposalId = process.env.PROPOSAL_ID; // Should be set to the proposal you want to vote on
const support = process.env.VOTE_SUPPORT === "true"; // true for yes, false for no

async function main() {
  if (!proposalId) {
    throw new Error("PROPOSAL_ID environment variable not set.");
  }
  const provider = new ethers.JsonRpcProvider(process.env.RPC_URL || "http://127.0.0.1:8545");
  const signer = new ethers.Wallet(process.env.PRIVATE_KEY, provider);
  const dao = new ethers.Contract(DAO_ADDRESS, DAO_ABI, signer);

  // Example: call vote(proposalId, support)
  const tx = await dao.vote(proposalId, support);
  console.log("Vote submitted, tx hash:", tx.hash);
  await tx.wait();
  console.log("Vote confirmed!");
}

main().catch((err) => {
  console.error(err);
  process.exit(1);
});
