import requests
from uuid import uuid4
from urllib.parse import urlparse
import datetime
import hashlib
import json
from flask import Flask,jsonify,request

class Blockchain:

	def  __init__(self):
		self.chain=[]
		self.transactions=[]  #mempool
		self.create_block(1,'0')
		self.nodes=set()

	def create_block(self,proof,previous_hash):

		block={'index':len(self.chain)+1,'proof':proof,'timestamp':str(datetime.datetime.now()),'previous_hash':previous_hash,'transactions':self.transactions}
		self.transactions=[]
		self.chain.append(block)
		return block

	def add_transaction(self,sender,reciever,amount):
		self.transactions.append({'sender':sender,'reciever':reciever, 'amount':amount})
		return (self.get_previous_block())['index']+1

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

	def add_node(self,address):
		parsed_url=urlparse(address)
		self.nodes.add(parsed_url.netloc)

	def update_chain(self):
		longest_chain=None
		max_length=len(self.chain)
		for node in self.nodes:
			response=requests.get(f'http://node/get_chain')
			if response.status_code==200:
				length=response.json()['Length']
				chain=response.json()['chain']
				if length>max_length and self.is_chain_valid(chain):
					longest_chain=chain
					max_length=length
		if longest_chain:
			self.chain=longest_chain
			return True
		return False


app=Flask(__name__)
node_adress=str(uuid4()).replace('-','')
blockchain=Blockchain()
@app.route('/mine_block',methods=['GET'])
def mine_block():
	prev_block=blockchain.get_previous_block()
	blockchain.add_transaction(node_adress,"Shreyas",5)
	block=blockchain.create_block(blockchain.pow(prev_block['proof']),blockchain.hash(prev_block))
	response={'transactions':block['transactions'],'index':block['index'],'proof':block['proof'],'timestamp':block['timestamp'],'previous_hash':block['previous_hash'],'message':"congrats"}
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


@app.route('/add_transaction',methods=['POST'])
def add_transaction():
	json=request.get_json()
	index=blockchain.add_transaction(json['sender'],json['reciever'],json['amount'])
	response={'message':f'transaction added to {index}th block'}
	return jsonify(response),201


@app.route('/connect_node',methods=['POST'])
def connect_node():
	json=request.get_json()
	nodes=json.get('nodes')
	for node in nodes:
		blockchain.add_node(node)
	response={'message':'Nodes connected','Nodes':list(blockchain.nodes)}
	return jsonify(response),201

@app.route('/replace_chain',methods=['GET'])
def replace_chain():
	response={'message':blockchain.update_chain()}
	return jsonify(response),200

app.run(host='0.0.0.0',port=5003)







