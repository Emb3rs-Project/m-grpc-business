import json
import os
from concurrent import futures
from pathlib import Path

import dotenv
import grpc
import jsonpickle

from base.wrappers import SimulationWrapper
from business.business_pb2 import BMInput, BMOutput
from business.business_pb2_grpc import BusinessModuleServicer, add_BusinessModuleServicer_to_server
from module.Businessmodulev1_clean import BM as run_feasability  # noqa

dotenv.load_dotenv()
PROJECT_PATH = str(Path.cwd().parent)


class BusinessModule(BusinessModuleServicer):
    def bm(self, request: BMInput, context) -> BMOutput:
        input_dict = {
            "platform": jsonpickle.decode(request.platform),
            "gis-module": jsonpickle.decode(request.gis_modules),
            "teo-module": jsonpickle.decode(request.teo_module),
            "market-module": jsonpickle.decode(request.market_module),
        }
        with SimulationWrapper(project_path=PROJECT_PATH):
            output = run_feasability(input_dict=input_dict, generate_template=False)
        return BMOutput(
            NPV_socio_economic=json.dumps(output["NPV_socio-economic"]),
            IRR_socio_economic=json.dumps(output["IRR_socio-economic"]),
            Sensitivity_NPV_socio_economic=json.dumps(output["Sensitivity_NPV_socio-economic"]),
            NPV_comm_actor=json.dumps(output["NPV_comm_actor"]),
            IRR_comm_actor=json.dumps(output["IRR_comm_actor"]),
            Sensitivity_NPV_comm_actor=json.dumps(output["Sensitivity_NPV_comm_actor"]),
            Discountrate_socio=json.dumps(output["Discountrate_socio"]),
            Discountrate_business=json.dumps(output["Discountrate_business"]),
            LCOH_s=json.dumps(output["LCOH_s"]),
            report=output["report"],
        )

    def internal_heat_recobery(self, request, context):
        return super().internal_heat_recobery(request, context)


def serve():
    server = grpc.server(
        futures.ThreadPoolExecutor(max_workers=100),
        options=[('grpc.max_send_message_length', -1), ('grpc.max_receive_message_length', -1)],
    )
    add_BusinessModuleServicer_to_server(BusinessModule(), server)

    server.add_insecure_port(f"{os.getenv('GRPC_HOST')}:{os.getenv('GRPC_PORT')}")
    print(f"Business module Listening at {os.getenv('GRPC_HOST')}:{os.getenv('GRPC_PORT')}")

    server.start()
    server.wait_for_termination()


if __name__ == '__main__':
    serve()
