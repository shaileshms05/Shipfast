"""
Example: Using LangChain with ShipFast v3.0
Demonstrates how to use LangChain chains, tools, and agents
"""

from services.ai.langchain_cerebras import create_langchain_chat, create_langchain_llm
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser


def example_basic_chat():
    """Basic chat completion"""
    print("=" * 60)
    print("Example 1: Basic Chat Completion")
    print("=" * 60)
    
    # Create LangChain-compatible Cerebras chat model
    llm = create_langchain_chat()
    
    # Simple invocation
    messages = [HumanMessage(content="What is Python?")]
    response = llm.invoke(messages)
    
    print(f"Response: {response.content}")
    print()


def example_with_system_prompt():
    """Chat with system prompt"""
    print("=" * 60)
    print("Example 2: Chat with System Prompt")
    print("=" * 60)
    
    llm = create_langchain_chat()
    
    messages = [
        SystemMessage(content="You are a helpful coding assistant."),
        HumanMessage(content="Explain list comprehension in Python")
    ]
    
    response = llm.invoke(messages)
    print(f"Response: {response.content}")
    print()


def example_langchain_chain():
    """Using LangChain chains"""
    print("=" * 60)
    print("Example 3: LangChain Chain with Prompts")
    print("=" * 60)
    
    llm = create_langchain_chat()
    
    # Create a prompt template
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a code review expert. Review the following code and provide feedback."),
        ("human", "{code}")
    ])
    
    # Create a chain
    chain = prompt | llm | StrOutputParser()
    
    # Use the chain
    code = """
def add(a, b):
    return a + b
"""
    
    response = chain.invoke({"code": code})
    print(f"Code Review: {response}")
    print()


def example_multiple_chains():
    """Chaining multiple operations"""
    print("=" * 60)
    print("Example 4: Multiple Chained Operations")
    print("=" * 60)
    
    llm = create_langchain_chat()
    
    # Step 1: Generate code
    generate_prompt = ChatPromptTemplate.from_template(
        "Write a Python function that {task}"
    )
    generate_chain = generate_prompt | llm | StrOutputParser()
    
    # Step 2: Review code
    review_prompt = ChatPromptTemplate.from_template(
        "Review this code and suggest improvements:\n\n{code}"
    )
    review_chain = review_prompt | llm | StrOutputParser()
    
    # Execute chain
    task = "calculates the factorial of a number"
    code = generate_chain.invoke({"task": task})
    print(f"Generated Code:\n{code}\n")
    
    review = review_chain.invoke({"code": code})
    print(f"Code Review:\n{review}")
    print()


def example_with_temperature():
    """Controlling temperature"""
    print("=" * 60)
    print("Example 5: Temperature Control")
    print("=" * 60)
    
    # Creative (high temperature)
    creative_llm = create_langchain_chat(temperature=0.9)
    
    # Deterministic (low temperature)
    deterministic_llm = create_langchain_chat(temperature=0.1)
    
    prompt = "Come up with a creative name for a code editor"
    
    print("Creative response:")
    response1 = creative_llm.invoke([HumanMessage(content=prompt)])
    print(response1.content)
    print()
    
    print("Deterministic response:")
    response2 = deterministic_llm.invoke([HumanMessage(content=prompt)])
    print(response2.content)
    print()


def example_batch_processing():
    """Batch processing multiple inputs"""
    print("=" * 60)
    print("Example 6: Batch Processing")
    print("=" * 60)
    
    llm = create_langchain_chat()
    
    # Batch multiple questions
    questions = [
        "What is REST API?",
        "What is GraphQL?",
        "What is gRPC?"
    ]
    
    messages_list = [[HumanMessage(content=q)] for q in questions]
    
    # Process in batch
    responses = llm.batch(messages_list)
    
    for q, r in zip(questions, responses):
        print(f"Q: {q}")
        print(f"A: {r.content[:100]}...")
        print()


def example_streaming():
    """Streaming responses"""
    print("=" * 60)
    print("Example 7: Streaming Response")
    print("=" * 60)
    
    llm = create_langchain_chat()
    
    prompt = "Write a short story about a robot learning to code"
    
    print("Streaming response:")
    for chunk in llm.stream([HumanMessage(content=prompt)]):
        print(chunk.content, end="", flush=True)
    print("\n")


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("LangChain + ShipFast v3.0 Examples")
    print("=" * 60 + "\n")
    
    try:
        example_basic_chat()
        example_with_system_prompt()
        example_langchain_chain()
        example_multiple_chains()
        example_with_temperature()
        example_batch_processing()
        # example_streaming()  # Uncomment to test streaming
        
        print("=" * 60)
        print("All examples completed successfully!")
        print("=" * 60)
        
    except Exception as e:
        print(f"Error: {e}")
        print("\nMake sure:")
        print("1. You're in the shipfast_v3 directory")
        print("2. Virtual environment is activated")
        print("3. CEREBRAS_API_KEY is set in .env")
        print("4. All dependencies are installed: pip install -r requirements.txt")
