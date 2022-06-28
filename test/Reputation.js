const Reputation = artifacts.require ('./Reputation.sol')

require ('chai').use (require ('chai-as-promised')).should()

contract ('Reputation', () => {

	let reputation, accounts

	before (async () => {
		
		reputation = await Reputation.deployed ()
		accounts = await web3.eth.getAccounts()
	
	})

	describe ('deployment', async () => {

		it ('deploys successfully', async () => {

			const address = await reputation.address

			assert.notEqual (address, 0x0)
			assert.notEqual (address, '')
			assert.notEqual (address, null)
			assert.notEqual (address, undefined)

		})

		it ('public constant values', async () => {

			const base = await reputation.BASE ()
			const weight = await reputation.WEIGHT ()

			assert.equal (base, 1000)
			assert.equal (weight, 300)

		})

	})

	describe ('node registration and unregistration', async () => {

		it ('registering and unregistring node', async () => {

			const nodeAstr = "Node A"
			const nodeBstr = "Node B"

			await reputation.registerNode ("", { from: accounts[0] }).should.be.rejected

			var result = await reputation.registerNode (nodeAstr, { from: accounts[0] })
			var event = result.logs[0].args

			assert.equal (event.id, 1, "This ID is not expected!")
			assert.equal (event.name, nodeAstr, "Node name is not correct!")
			assert.equal (event.value, 0, "Reputation score should be initialized!")
			assert.equal (event.valid, true, "Score validity should be valid!")

			result = await reputation.getNodeCount.call({ from: accounts[0] })
			assert.equal (result.words[0], 1, "Node count is not correct!")

			result = await reputation.registerNode (nodeBstr, { from: accounts[0] })
			event = result.logs[0].args

			assert.equal (event.id, 2, "This ID is not expected!")
			assert.equal (event.name, nodeBstr, "Node name is not correct!")
			assert.equal (event.value, 0, "Reputation score should be initialized!")
			assert.equal (event.valid, true, "Score validity should be valid!")

			result = await reputation.getNodeCount.call({from: accounts[0] })
			assert.equal (result.words[0], 2, "Node count is not correct!")

			var nodeA = await reputation.getNode.call (1, { from: accounts[0] })
			var nodeB = await reputation.getNode.call (2, { from: accounts[0] })

			assert.equal (nodeA['0'], nodeAstr, "Node name is not correct!")
			assert.equal (nodeA['1'].toNumber (), 0, "Reputation score should be initialized!")
			assert.equal (nodeA['2'], true, "Score validity should be valid!")

			assert.equal (nodeB['0'], nodeBstr, "Node name is not correct!")
			assert.equal (nodeB['1'].toNumber (), 0, "Reputation score should be initialized!")
			assert.equal (nodeB['2'], true, "Score validity should be valid!")

			result = await reputation.unregisterNode (1, { from: accounts[0] })
			event = result.logs[0].args

			assert.equal (event.id, 1, "This ID is not expected!")
			assert.equal (event.name, nodeAstr, "Node name is not correct!")
			await reputation.getNode.call (1, { from: accounts[0] }).should.be.rejected

			result = await reputation.getNodeCount.call({from: accounts[0] })
			assert.equal (result.words[0], 1, "Node count is not correct!")

			nodeB = await reputation.getNode.call (2, { from: accounts[0] })

			assert.equal (nodeB['0'], nodeBstr, "Node name is not correct!")
			assert.equal (nodeB['1'].toNumber (), 0, "Reputation score should be initialized!")
			assert.equal (nodeB['2'], true, "Score validity should be valid!")

			await reputation.unregisterNode (2, { from: accounts[0] })

			result = await reputation.getNodeCount.call({from: accounts[0] })
			assert.equal (result.words[0], 0, "Node count is not correct!")

		})		

	})

	describe ("reputation system", async () => {

		it ('update reputation score', async () => {

			const nodeAstr = "Node A"
			const BASE = await reputation.BASE.call ({ from: accounts[0] })
			const WEIGHT = await reputation.WEIGHT.call ({ from: accounts[0] })

			var reward = 0
			var value = 0
			var contractScore = 0
			var residual = 0
			var repScore = 0
			var incentive = 0
			var event

			var result = await reputation.registerNode (nodeAstr, { from: accounts[0] })
			event = result.logs[0].args
			var idA = event.id

			for (var i = 0; i < 50; i++) {

				reward = Math.random().toFixed (3) * (Math.round(Math.random()) ? 1 : -1)
				incentive = reward * BASE
				contractScore = (contractScore * (BASE - WEIGHT) + WEIGHT * incentive)
				residual = contractScore % BASE
				contractScore = contractScore - residual
				contractScore = contractScore / BASE

				result = await reputation.updateNodeReputation (idA, incentive, { from: accounts[0] })
				event = result.logs[0].args
				value = (event.value / BASE).toFixed (3)

				assert.equal ((contractScore / BASE).toFixed (3), value, "Reputation score is not correct!")
				
				repScore = await reputation.getReputationScore.call(idA, { from: accounts[0] })
				repScore = repScore['0'].negative ? -repScore['0'].words[0] : repScore['0'].words[0]
				repScore = (repScore / BASE).toFixed (3)
								
				assert.equal ((contractScore / BASE).toFixed (3), repScore, "Reputation score is not correct!")

			}

			await reputation.unregisterNode (idA, { from: accounts[0] })

		})

		it ('reputation updates for multiple nodes', async () => {

			const nodeAstr = "Node A"
			const nodeBstr = "Node B"
			const BASE = await reputation.BASE.call ({ from: accounts[0] })
			const WEIGHT = await reputation.WEIGHT.call ({ from: accounts[0] })

			var contractScoreA = 0
			var contractScoreB = 0

			var result = await reputation.registerNode (nodeAstr, { from: accounts[0] })
			var event = result.logs[0].args
			const idA = event.id
			
			result = await reputation.registerNode (nodeBstr, { from: accounts[0] })
			event = result.logs[0].args
			const idB = event.id

			var repScoreA = await reputation.getReputationScore.call(idA, { from: accounts[0] })
			var repScoreB = await reputation.getReputationScore.call(idB, { from: accounts[0] })

			assert.equal (repScoreA['0'].words[0], 0, "Initial reputation score is not correct!")
			assert.equal (repScoreB['0'].words[0], 0, "Initial reputation score is not correct!")

			for (var i = 0; i < 3; i++) {
				var rewardA = Math.random().toFixed (3) * (Math.round(Math.random()) ? 1 : -1)
				var rewardB = Math.random().toFixed (3) * (Math.round(Math.random()) ? 1 : -1)
				var incentiveA = rewardA * BASE
				var incentiveB = rewardB * BASE
				
				contractScoreA = (contractScoreA * (BASE - WEIGHT) + WEIGHT * incentiveA)
				var residual = contractScoreA % BASE
				contractScoreA = contractScoreA - residual
				contractScoreA = contractScoreA / BASE

				contractScoreB = (contractScoreB * (BASE - WEIGHT) + WEIGHT * incentiveB)
				residual = contractScoreB % BASE
				contractScoreB = contractScoreB - residual
				contractScoreB	 = contractScoreB / BASE

				var result = await reputation.updateNodeReputation (idA, incentiveA, { from: accounts[0] })
				event = result.logs[0].args
				var valueA = (event.value / BASE).toFixed (3)

				result = await reputation.updateNodeReputation (idB, incentiveB, { from: accounts[0] })
				event = result.logs[0].args
				var valueB = (event.value / BASE).toFixed (3)

				assert.equal ((contractScoreA / BASE).toFixed (3), valueA, "Reputation score is not correct!")
				assert.equal ((contractScoreB / BASE).toFixed (3), valueB, "Reputation score is not correct!")
				
				repScoreA = await reputation.getReputationScore.call(idA, { from: accounts[0] })
				repScoreA = repScoreA['0'].negative ? -repScoreA['0'].words[0] : repScoreA['0'].words[0]
				repScoreA = (repScoreA / BASE).toFixed (3)

				repScoreB = await reputation.getReputationScore.call(idB, { from: accounts[0] })
				repScoreB = repScoreB['0'].negative ? -repScoreB['0'].words[0] : repScoreB['0'].words[0]
				repScoreB = (repScoreB / BASE).toFixed (3)
									
				assert.equal ((contractScoreA / BASE).toFixed (3), repScoreA, "Reputation score is not correct!")
				assert.equal ((contractScoreB / BASE).toFixed (3), repScoreB, "Reputation score is not correct!")
			}

		})

	})

})