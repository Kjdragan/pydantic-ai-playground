from dataclasses import dataclass
from database import SessionLocal
from models import User
from contextlib import contextmanager
from pydantic import BaseModel, Field
from pydantic_ai import Agent, RunContext

@contextmanager
def get_session():
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()
        
class DatabaseConn:
    @classmethod
    async def user_name(cls, *, id: int) -> str | None:
        with get_session() as session:
            user = session.query(User).filter_by(id=id).first()
            return user.name if user else None

    @classmethod
    async def account_status(cls, *, id: int) -> str:
        with get_session() as session:
            user = session.query(User).filter_by(id=id).first()
            return user.account_status if user else "Locked"

    @classmethod
    async def subscription_plan(cls, *, id: int) -> str:
        with get_session() as session:
            user = session.query(User).filter_by(id=id).first()
            return user.subscription_plan if user else "Free Plan"
        

@dataclass
class SupportDependencies:
    user_id: int
    db: DatabaseConn
    

class SupportResult(BaseModel):
    support_advice: str = Field(description="Advice returned to the user")
    escalate_to_admin: bool = Field(description="Whether to escalate the query to an admin")
    risk_level: int = Field(description="Risk level of the query", ge=0, le=10)
    

support_agent = Agent(
    "openai:gpt-4o",
    deps_type=SupportDependencies,
    result_type=SupportResult,
    system_prompt=(
        "You are a SaaS support agent. Help users with their accounts, "
        "check subscription plans, and determine if their query should be escalated to an admin."
    ),
)


@support_agent.system_prompt
async def add_ser_name(ctx: RunContext[SupportDependencies]) -> str:
    user_name = await ctx.deps.db.user_name(id=ctx.deps.user_id)
    return f"The user's name is {user_name!r}"


@support_agent.tool
async def account_status(ctx: RunContext[SupportDependencies]) -> str:
    """Returns the user's account status."""
    status = await ctx.deps.db.account_status(id=ctx.deps.user_id)
    return f"Your account is currently: {status}"


@support_agent.tool
async def subscription_plan(ctx: RunContext[SupportDependencies]) -> str:
    """Returns the user's subscription plan."""
    plan = await ctx.deps.db.subscription_plan(id=ctx.deps.user_id)
    return f"Your current subscription plan is: {plan}"
















