import dotenv
from gentopia import chat
from gentopia.assembler.agent_assembler import AgentAssembler
from gentopia.tools import BaseTool
from gentopia.prompt import PromptTemplate


if __name__ == '__main__':

    dotenv.load_dotenv(".env")
    agent = AgentAssembler(file='configs/openai_memory_template.yaml').get_agent()

    #chat(agent)
    print(agent.run("what is 1+1"))
