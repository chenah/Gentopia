from gentopia.assembler.agent_assembler import AgentAssembler
from gentopia.output import enable_log
from gentopia import chat

if __name__ == '__main__':
    enable_log()
    assembler = AgentAssembler(file='configs/rewoo_template.yaml')
    agent = assembler.get_agent()
    chat(agent)
