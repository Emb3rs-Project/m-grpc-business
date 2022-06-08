import os
from concurrent import futures

import dotenv
import grpc
import jsonpickle
import json

dotenv.load_dotenv()

from business.business_pb2_grpc import BusinessModuleServicer, add_BusinessModuleServicer_to_server

class BusinessModule(BusinessModuleServicer):
    
    def __init__(self) -> None:
        pass

    def bm(self, request, context):
        return super().bm(request, context)

    def internal_heat_recobery(self, request, context):
        return super().internal_heat_recobery(request, context)


def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    add_BusinessModuleServicer_to_server(BusinessModule(), server)

    server.add_insecure_port(
        f"{os.getenv('GRPC_HOST')}:{os.getenv('GRPC_PORT')}")

    print(
        f"CF module Listening at {os.getenv('GRPC_HOST')}:{os.getenv('GRPC_PORT')}")

    server.start()
    server.wait_for_termination()


serve()