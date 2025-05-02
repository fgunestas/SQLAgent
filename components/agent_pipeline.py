from langgraph.graph import END, START, StateGraph
from components.agent import State,query_generator,query_executor,response_generator
from langchain_core.messages import HumanMessage



def agent_pipeline(query: str,test=0):
    graph_builder = StateGraph(State)

    graph_builder.add_node("query_generator", query_generator)
    graph_builder.add_node("query_executor", query_executor)
    graph_builder.add_node("response_generator", response_generator)



    graph_builder.add_edge(START, "query_generator")
    graph_builder.add_edge("query_generator", "query_executor")
    graph_builder.add_edge("query_executor", "response_generator")
    graph_builder.add_edge("query_executor", END)

    graph = graph_builder.compile()
    query = {"messages": [HumanMessage(query)]}

    from pprint import pprint
    for output in graph.stream(query):
        for key, value in output.items():
            if test==1:
                pprint(f"Output from node '{key}':")
                pprint(value["messages"][-1])
            final_state = value
        if test == 1:
            pprint("------")

    messages = final_state["messages"]
    final_message = messages[-1]
    return final_message