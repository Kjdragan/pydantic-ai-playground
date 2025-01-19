import asyncio
from agent import DatabaseConn, SupportDependencies, support_agent

async def test_support_agent():
    deps = SupportDependencies(user_id=102, db=DatabaseConn())

    # Query 1: Subscription plan
    # result = await support_agent.run("What is my subscription plan?", deps=deps)
    result = await support_agent.run("Why is my account locked?", deps=deps)
    print(result.data)
    

if __name__ == "__main__":
    asyncio.run(test_support_agent())