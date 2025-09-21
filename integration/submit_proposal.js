// submit_proposal.js
// Script to submit a governance proposal to the DAO contract using ethers.js

import { ethers } from "ethers";
import dotenv from "dotenv";
import fs from "fs";
dotenv.config();

// Load contract ABI and address (update as needed)
const DAO_ABI = JSON.parse(fs.readFileSync("../blockchain_layer/contracts/GovernanceDAO.json"));
const DAO_ADDRESS = process.env.DAO_CONTRACT_ADDRESS;

// Example proposal data (update as needed)
const proposalDescription = process.env.PROPOSAL_DESCRIPTION || "Test proposal";
const proposalData = process.env.PROPOSAL_DATA || "0x";

async function main() {
  const provider = new ethers.JsonRpcProvider(process.env.RPC_URL || "http://127.0.0.1:8545");
  const signer = new ethers.Wallet(process.env.PRIVATE_KEY, provider);
  const dao = new ethers.Contract(DAO_ADDRESS, DAO_ABI, signer);

  // Example: call submitProposal(description, data)
  const tx = await dao.submitProposal(proposalDescription, proposalData);
  console.log("Proposal submitted, tx hash:", tx.hash);
  await tx.wait();
  console.log("Proposal confirmed!");
}

main().catch((err) => {
  console.error(err);
  process.exit(1);
});
