import signal
import time

import dotenv
import rich
from rich.box import Box

from gentopia.assembler.agent_assembler import AgentAssembler
from gentopia.output import enable_log
from gentopia import chat



if __name__ == '__main__':

    enable_log(log_level='debug')
    dotenv.load_dotenv(".env")

    assembler = AgentAssembler(file='configs/react.yaml')

    # # assembler.manager = LocalLLMManager()
    agent = assembler.get_agent()

    chat(agent)
    # print(agent.run("1+sqrt(33)=?"))
    # print(agent.run("1+sqrt(35)=?"))