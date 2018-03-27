all: rpc_pb2.py rpc_pb2_grpc.py

clean:
	-rm rpc_pb2.py
	-rm rpc_pb2_grpc.py

rpc_pb2_grpc.py: rpc_pb2.py

rpc_pb2.py: rpc.proto
	python3 -m grpc_tools.protoc --proto_path=. --python_out=. --grpc_python_out=. rpc.proto

