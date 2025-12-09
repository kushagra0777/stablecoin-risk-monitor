// SPDX-License-Identifier: MIT
pragma solidity ^0.8.9;

import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/security/ReentrancyGuard.sol";
import "@openzeppelin/contracts/utils/Counters.sol";

contract GovernanceDAO is Ownable, ReentrancyGuard {
    using Counters for Counters.Counter;
    
    Counters.Counter private _proposalIds;
    
    // Minimum tokens required to create a proposal
    uint256 public constant PROPOSAL_THRESHOLD = 1000 * 10**18; // 1000 tokens
    
    // Voting duration in seconds (7 days)
    uint256 public constant VOTING_DURATION = 7 days;
    
    // Minimum quorum percentage (20%)
    uint256 public constant QUORUM_PERCENTAGE = 20;
    
    enum ProposalState {
        Pending,
        Active,
        Defeated,
        Succeeded,
        Executed
    }
    
    enum VoteType {
        Against,
        For,
        Abstain
    }
    
    struct Proposal {
        uint256 id;
        address proposer;
        string title;
        string description;
        uint256 startTime;
        uint256 endTime;
        uint256 forVotes;
        uint256 againstVotes;
        uint256 abstainVotes;
        bool executed;
        ProposalState state;
        // Action parameters for execution
        address target;
        bytes data;
        uint256 value;
    }
    
    struct Vote {
        bool hasVoted;
        VoteType vote;
        uint256 weight;
    }
    
    // Proposal ID => Proposal
    mapping(uint256 => Proposal) public proposals;
    
    // Proposal ID => voter => Vote
    mapping(uint256 => mapping(address => Vote)) public votes;
    
    // User balances (in a real implementation, this would integrate with your stablecoin contract)
    mapping(address => uint256) public balances;
    uint256 public totalSupply;
    
    // Array to store all proposal IDs
    uint256[] public proposalIds;
    
    event ProposalCreated(
        uint256 indexed proposalId,
        address indexed proposer,
        string title,
        string description,
        uint256 startTime,
        uint256 endTime
    );
    
    event VoteCast(
        address indexed voter,
        uint256 indexed proposalId,
        VoteType vote,
        uint256 weight
    );
    
    event ProposalExecuted(uint256 indexed proposalId);
    
    event ProposalStateChanged(uint256 indexed proposalId, ProposalState newState);
    
    constructor() {}
    
    // Function to set user balance (for testing purposes)
    function setBalance(address user, uint256 amount) external onlyOwner {
        totalSupply = totalSupply - balances[user] + amount;
        balances[user] = amount;
    }
    
    function createProposal(
        string memory title,
        string memory description,
        address target,
        bytes memory data,
        uint256 value
    ) external returns (uint256) {
        require(balances[msg.sender] >= PROPOSAL_THRESHOLD, "Insufficient tokens to create proposal");
        require(bytes(title).length > 0, "Title cannot be empty");
        require(bytes(description).length > 0, "Description cannot be empty");
        
        _proposalIds.increment();
        uint256 proposalId = _proposalIds.current();
        
        uint256 startTime = block.timestamp;
        uint256 endTime = startTime + VOTING_DURATION;
        
        proposals[proposalId] = Proposal({
            id: proposalId,
            proposer: msg.sender,
            title: title,
            description: description,
            startTime: startTime,
            endTime: endTime,
            forVotes: 0,
            againstVotes: 0,
            abstainVotes: 0,
            executed: false,
            state: ProposalState.Active,
            target: target,
            data: data,
            value: value
        });
        
        proposalIds.push(proposalId);
        
        emit ProposalCreated(proposalId, msg.sender, title, description, startTime, endTime);
        
        return proposalId;
    }
    
    function vote(uint256 proposalId, VoteType voteType) external nonReentrant {
        require(balances[msg.sender] > 0, "No voting power");
        require(proposalId <= _proposalIds.current() && proposalId > 0, "Invalid proposal ID");
        
        Proposal storage proposal = proposals[proposalId];
        require(proposal.state == ProposalState.Active, "Proposal not active");
        require(block.timestamp >= proposal.startTime, "Voting not started");
        require(block.timestamp <= proposal.endTime, "Voting ended");
        require(!votes[proposalId][msg.sender].hasVoted, "Already voted");
        
        uint256 weight = balances[msg.sender];
        
        votes[proposalId][msg.sender] = Vote({
            hasVoted: true,
            vote: voteType,
            weight: weight
        });
        
        if (voteType == VoteType.For) {
            proposal.forVotes += weight;
        } else if (voteType == VoteType.Against) {
            proposal.againstVotes += weight;
        } else {
            proposal.abstainVotes += weight;
        }
        
        emit VoteCast(msg.sender, proposalId, voteType, weight);
    }
    
    function executeProposal(uint256 proposalId) external nonReentrant {
        require(proposalId <= _proposalIds.current() && proposalId > 0, "Invalid proposal ID");
        
        Proposal storage proposal = proposals[proposalId];
        require(proposal.state == ProposalState.Active, "Proposal not active");
        require(block.timestamp > proposal.endTime, "Voting still active");
        require(!proposal.executed, "Already executed");
        
        // Update proposal state based on results
        _updateProposalState(proposalId);
        
        if (proposal.state == ProposalState.Succeeded) {
            proposal.executed = true;
            
            // Execute the proposal action
            if (proposal.target != address(0)) {
                (bool success, ) = proposal.target.call{value: proposal.value}(proposal.data);
                require(success, "Proposal execution failed");
            }
            
            emit ProposalExecuted(proposalId);
        }
    }
    
    function _updateProposalState(uint256 proposalId) internal {
        Proposal storage proposal = proposals[proposalId];
        
        uint256 totalVotes = proposal.forVotes + proposal.againstVotes + proposal.abstainVotes;
        uint256 quorum = (totalSupply * QUORUM_PERCENTAGE) / 100;
        
        if (totalVotes < quorum) {
            proposal.state = ProposalState.Defeated;
        } else if (proposal.forVotes > proposal.againstVotes) {
            proposal.state = ProposalState.Succeeded;
        } else {
            proposal.state = ProposalState.Defeated;
        }
        
        emit ProposalStateChanged(proposalId, proposal.state);
    }
    
    // View functions
    function getProposal(uint256 proposalId) external view returns (Proposal memory) {
        require(proposalId <= _proposalIds.current() && proposalId > 0, "Invalid proposal ID");
        return proposals[proposalId];
    }
    
    function getProposalState(uint256 proposalId) external view returns (ProposalState) {
        require(proposalId <= _proposalIds.current() && proposalId > 0, "Invalid proposal ID");
        
        Proposal memory proposal = proposals[proposalId];
        
        if (proposal.executed) {
            return ProposalState.Executed;
        }
        
        if (block.timestamp <= proposal.endTime) {
            return ProposalState.Active;
        }
        
        uint256 totalVotes = proposal.forVotes + proposal.againstVotes + proposal.abstainVotes;
        uint256 quorum = (totalSupply * QUORUM_PERCENTAGE) / 100;
        
        if (totalVotes < quorum) {
            return ProposalState.Defeated;
        } else if (proposal.forVotes > proposal.againstVotes) {
            return ProposalState.Succeeded;
        } else {
            return ProposalState.Defeated;
        }
    }
    
    function getAllProposals() external view returns (uint256[] memory) {
        return proposalIds;
    }
    
    function getProposalCount() external view returns (uint256) {
        return _proposalIds.current();
    }
    
    function getVote(uint256 proposalId, address voter) external view returns (Vote memory) {
        return votes[proposalId][voter];
    }
    
    function hasVoted(uint256 proposalId, address voter) external view returns (bool) {
        return votes[proposalId][voter].hasVoted;
    }
    
    // Emergency functions
    function emergencyPause(uint256 proposalId) external onlyOwner {
        Proposal storage proposal = proposals[proposalId];
        proposal.state = ProposalState.Defeated;
        emit ProposalStateChanged(proposalId, ProposalState.Defeated);
    }
}
