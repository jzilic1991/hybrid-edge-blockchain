pragma solidity ^0.8.0;

contract Reputation {

	struct Score {

		string name;
		int value;
		bool valid;

	}

	int constant public BASE = 1000;
	int constant public WEIGHT = 300;

	mapping (uint => Score) private reputationSystem;
	uint private nodeId = 0;
	uint private nodeCount = 0;

	event NodeRegistered (uint id, string name, int value, bool valid);
	event NodeUnregistered (uint id, string name);
	event ReputationUpdate (uint id, int value, bool valid);

	function registerNode (string memory _name) public {

		require (bytes (_name).length > 0, "Node parameter is empty or null!");
		
		nodeId++;
		nodeCount++;
		reputationSystem[nodeId].name = _name;
		reputationSystem[nodeId].value = 0;
		reputationSystem[nodeId].valid = true;

		emit NodeRegistered (nodeId, reputationSystem[nodeId].name, reputationSystem[nodeId].value,
			reputationSystem[nodeId].valid);

	}

	function unregisterNode (uint _id) public {

		require (reputationSystem[_id].valid, "Node is not registered!");

		Score memory tmp = reputationSystem[_id];
		delete reputationSystem[_id];
		nodeCount--;

		emit NodeUnregistered(_id, tmp.name);

	}

	function getNodeCount () public view returns (uint) {

		return nodeCount;

	}

	function getNode (uint _id) public view returns (string memory, int, bool) {

		require (reputationSystem[_id].valid, "Node is not registered!");

		return (reputationSystem[_id].name, reputationSystem[_id].value,
			reputationSystem[_id].valid);

	}

	function updateNodeReputation (uint _id, int _incentive) public {

		require (reputationSystem[_id].valid, "Node is not registered!");

		reputationSystem[_id].value = reputationSystem[_id].value * (BASE - WEIGHT) + WEIGHT * _incentive;
		int residual = reputationSystem[_id].value % BASE;
		reputationSystem[_id].value -= residual;
		reputationSystem[_id].value /= BASE;


		emit ReputationUpdate (_id, reputationSystem[_id].value, reputationSystem[_id].valid);

	}

	function getReputationScore (uint _id) public view returns (int, bool) {

		require (reputationSystem[_id].valid, "Node is not registered!");

		return (reputationSystem[_id].value, reputationSystem[_id].valid);

	}

	// function getAllReputations () public view returns (string[] memory, int[] memory) {

	// 	string[] memory nodes;
	// 	int[] memory scores;

	// 	for (uint i = 0; i < keys.length; i++) {

	// 		nodes = new string[] (i + 1);
	// 		nodes[i] = keys[i];

	// 		scores = new int[] (i + 1);
	// 		scores[i] = reputationSystem[keys[i]].value;

	// 	}

	// 	return (nodes, scores);

	// } 

}