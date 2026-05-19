import asyncio
import click
from sqlalchemy import select

from src.common.password import get_password_hash
from src.database import create_engine, create_sessionmaker
from src.enums import UserRole
from src.models.user import User

# [실행]
# python -m src.cli create-admin

@click.group()
def cli():
    """쇼핑몰 관리용 CLI 도구"""
    pass

@cli.command()
@click.option("--email", prompt=True, help="관리자 이메일")
@click.option("--password", prompt=True, hide_input=True, confirmation_prompt=True, help="관리자 비밀번호")
@click.option("--name", prompt=True, help="관리자 이름")
def create_admin(email, password, name):
    """관리자 계정 생성"""
    asyncio.run(_create_admin_logic(email, password, name))


async def _create_admin_logic(username, password, name):
    engine = create_engine()
    session_factory = create_sessionmaker(engine)
    
    async with session_factory() as session:
        stmt = select(User).where(User.username == username)
        result = await session.execute(stmt)
        if result.scalar_one_or_none():
            click.echo(f"이미 존재하는 아이디입니다: {username}")
            return

        admin = User(
            username=username,
            name=name,
            hashed_password=get_password_hash(password),
            role=UserRole.admin
        )
        session.add(admin)
        await session.commit()
        click.echo(f"관리자 계정 생성 완료: {username}")
    
    await engine.dispose()


if __name__ == "__main__":
    cli()
