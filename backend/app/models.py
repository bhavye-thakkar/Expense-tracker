from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from .database import Base
from datetime import datetime


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    full_name = Column(String)
    expenses = relationship("Expense", back_populates="owner")
    group_memberships = relationship("GroupMember", back_populates="user")


# Common base class for expense attributes
class ExpenseBase(Base):
    __abstract__ = True

    id = Column(Integer, primary_key=True, index=True)
    date = Column(DateTime, nullable=False)
    category = Column(String, index=True)
    amount = Column(Float)
    description = Column(String)


class Expense(ExpenseBase):
    __tablename__ = "expenses"

    payment_method = Column(String)
    user_id = Column(Integer, ForeignKey("users.id"))
    owner = relationship("User", back_populates="expenses")


class Group(Base):
    __tablename__ = "groups"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)  # Removed unique constraint
    created_by = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)

    members = relationship("GroupMember", back_populates="group")
    expenses = relationship("GroupExpense", back_populates="group")
    creator = relationship("User")


class GroupMember(Base):
    __tablename__ = "group_members"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    group_id = Column(Integer, ForeignKey("groups.id"))
    joined_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="group_memberships")
    group = relationship("Group", back_populates="members")


class GroupExpense(ExpenseBase):
    __tablename__ = "group_expenses"

    group_id = Column(Integer, ForeignKey("groups.id"))
    paid_by = Column(Integer, ForeignKey("users.id"))

    splits = relationship("ExpenseSplit", back_populates="expense")
    group = relationship("Group", back_populates="expenses")
    payer = relationship("User")


class ExpenseSplit(Base):
    __tablename__ = "expense_splits"

    id = Column(Integer, primary_key=True, index=True)
    expense_id = Column(Integer, ForeignKey("group_expenses.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    amount = Column(Float)
    paid = Column(Boolean, default=False)

    expense = relationship("GroupExpense", back_populates="splits")
    user = relationship("User")
