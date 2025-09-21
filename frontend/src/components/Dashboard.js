import React, { useEffect, useState } from "react";

function Dashboard() {
  const [snapshot, setSnapshot] = useState({});
  const [alert, setAlert] = useState("");
  const [proposals, setProposals] = useState([]);
  const [votes, setVotes] = useState({});

  useEffect(() => {
    fetch("http://localhost:5000/api/data/snapshot")
      .then((res) => res.json())
      .then((data) => setSnapshot(data));

    fetch("http://localhost:5000/api/risk/alert")
      .then((res) => res.json())
      .then((data) => setAlert(data.alert));

    fetch("http://localhost:5000/governance/proposals")
      .then((res) => res.json())
      .then((data) => setProposals(data.proposals || []));
  }, []);

  // Fetch votes for each proposal
  useEffect(() => {
    proposals.forEach((proposal, idx) => {
      fetch(`http://localhost:5000/governance/votes/${idx}`)
        .then((res) => res.json())
        .then((data) => setVotes((prev) => ({ ...prev, [idx]: data.votes })));
    });
  }, [proposals]);

  return (
    <div>
      <h2>Snapshot</h2>
      <p>Supply: {snapshot.supply}</p>
      <p>Reserves: {snapshot.reserves}</p>
      <h3>Status: {alert}</h3>
      <h2>Governance Proposals</h2>
      <ul>
        {proposals.map((proposal, idx) => (
          <li key={idx}>
            Proposal {idx}: {JSON.stringify(proposal)}<br />
            Votes: {JSON.stringify(votes[idx])}
          </li>
        ))}
      </ul>
    </div>
  );
}

export default Dashboard;
