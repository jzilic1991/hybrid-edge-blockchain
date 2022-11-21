pragma solidity ^0.8.0;

contract Reputation {

	struct Score {

		string name;
		int value;
		bool valid;

	}

	struct Incentive {

		uint id;
		int value;

	}

	struct Response {

		uint id;
		int value;

	}

	int constant public BASE = 1000;
	int constant public WEIGHT = 300;

	mapping (uint => Score) private reputationSystem;
	uint private nodeId = 0;
	uint private nodeCount = 0;

	event NodeRegistered (uint id, string name, int value, bool valid);
	event NodeUnregistered (uint id, string name);
	// event ReputationUpdate (uint id, int value, bool valid);
	event ReputationUpdate (Response[] rsp);
	event ResetReputation (Response[] rsp);


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

	function updateNodeReputation (Incentive[] memory _incentives) public {

		require (_incentives.length > 0, "Incentives are empty!");

		uint[] memory reportedIds = new uint[] (_incentives.length);
		uint index = 0;

		for (uint i = 0; i < _incentives.length; i++) {

			reputationSystem[_incentives[i].id].value = 
				reputationSystem[_incentives[i].id].value * (BASE - WEIGHT) + WEIGHT * _incentives[i].value;
			int residual = reputationSystem[_incentives[i].id].value % BASE;
			reputationSystem[_incentives[i].id].value -= residual;
			reputationSystem[_incentives[i].id].value /= BASE;

			bool found = false;

			for (uint j = 0; j < index; j++) {

				if (reportedIds[j] == _incentives[i].id) { 

					found = true;
					break;

				}

			}

			if (found) continue;

			reportedIds[index] = _incentives[i].id;
			index++;

		}

		Response[] memory response = new Response[] (index);

		for (uint i = 0; i < index; i++) {

			response[i] = Response (reportedIds[i], reputationSystem[reportedIds[i]].value);
			
		} 

		// emit ReputationUpdate (_id, reputationSystem[_id].value, reputationSystem[_id].valid);
		emit ReputationUpdate (response);

	}

	function getReputationScore (uint _id) public view returns (int, bool) {

		require (reputationSystem[_id].valid, "Node is not registered!");

		return (reputationSystem[_id].value, reputationSystem[_id].valid);

	}

	function resetReputations (uint[] memory _id) public {

		require (_id.length > 0, "Offloading site IDs are empty!");

		Response[] memory response = new Response[] (_id.length);

		for (uint i = 0; i < _id.length; i++) {

			reputationSystem[_id[i]].value = 0;
			response[i] = Response (_id[i], reputationSystem[_id[i]].value);

		}

		emit ResetReputation (response);

	} 

}