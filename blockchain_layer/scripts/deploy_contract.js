async function main() {
  const ProofOfReserves = await ethers.getContractFactory("ProofOfReserves");
  const contract = await ProofOfReserves.deploy();
  await contract.waitForDeployment();

  console.log("ProofOfReserves deployed to:", await contract.getAddress());
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
