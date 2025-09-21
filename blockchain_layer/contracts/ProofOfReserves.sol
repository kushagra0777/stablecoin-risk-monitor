// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract ProofOfReserves {
    bytes32 public merkleRoot;
    uint256 public circulatingSupply;

    event ProofVerified(bool valid);
    event Alert(string message);

    function setSupply(uint256 _supply) public {
        circulatingSupply = _supply;
    }

    function updateRoot(bytes32 _root) public {
        merkleRoot = _root;
    }

    function verifyProof(uint256 totalReserves) public {
        if (totalReserves >= circulatingSupply) {
            emit ProofVerified(true);
        } else {
            emit ProofVerified(false);
            emit Alert("Reserves < Supply detected!");
        }
    }
}
