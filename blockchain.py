import datetime
import hashlib
import json
from flask import Flask,jsonify

class Blockchain:

	def  __init__(self):
		self.chain=[]
		self.create_block(1,'0')

	def create_block(self,proof,previous_hash):

		block={'index':len(self.chain)+1,'proof':proof,'timestamp':str(datetime.datetime.now()),'previous_hash':previous_hash}
		self.chain.append(block)
		return block

	def get_previous_block(self):
		return self.chain[-1]

	def pow(self,prev_proof):
		proof=1
		while True:
			h=hashlib.sha256(str(proof*proof - prev_proof*prev_proof).encode()).hexdigest()
			if h[:4]=='0000':
				return proof 
			proof=proof+1

	def hash(self,block):
		return  hashlib.sha256(json.dumps(block,sort_keys=True).encode()).hexdigest()

	def is_chain_valid(self,chain):

		previous_block=chain[0]
		i=1
		while i < len(chain):
			block=chain[i]
			if block['previous_hash']!=self.hash(previous_block):
				return False

			prev_proof=previous_block['proof']
			proof=block['proof']
			h=hashlib.sha256(str(proof*proof - prev_proof*prev_proof).encode()).hexdigest()
			if h[:4]!='0000':
				return False
			previous_block=block
			i=i+1
		return True


app=Flask(__name__)
blockchain=Blockchain()
@app.route('/mine_block',methods=['GET'])
def mine_block():
	prev_block=blockchain.get_previous_block()
	block=blockchain.create_block(blockchain.pow(prev_block['proof']),blockchain.hash(prev_block))
	response={'index':block['index'],'proof':block['proof'],'timestamp':block['timestamp'],'previous_hash':block['previous_hash'],'message':"congrats"}
	print(prev_block)
	return jsonify(response),200


@app.route('/get_chain',methods=['GET'])
def get_chain():
	response={'chain':blockchain.chain,"Length":len(blockchain.chain)}
	return jsonify(response),200

@app.route('/is_valid',methods=['GET'])
def is_valid():
	response={'message':blockchain.is_chain_valid(blockchain.chain)}
	return jsonify(response),200

app.run(host='0.0.0.0',port=5000)







