from sqlalchemy.orm import Session
from sqlalchemy import desc, func, and_
from datetime import datetime, timedelta
from typing import List, Optional, Dict
from .models import User, Transaction, Inventory, TransactionType
from .db import SessionLocal


class DatabaseService:
    """Database service layer for all database operations"""

    def __init__(self):
        self.db: Optional[Session] = None

    def __enter__(self):
        self.db = SessionLocal()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.db:
            self.db.close()

    # User operations
    def get_user_by_telegram_id(self, telegram_id: int) -> Optional[Dict]:
        """Get user by telegram_id"""
        user = self.db.query(User).filter(User.telegram_id == telegram_id).first()
        if user:
            return self._user_to_dict(user)
        return None

    def get_user(self, user_id: int) -> Optional[Dict]:
        """Get user by id"""
        user = self.db.query(User).filter(User.id == user_id).first()
        if user:
            return self._user_to_dict(user)
        return None

    def get_all_users(self) -> List[Dict]:
        """Get all active users"""
        users = self.db.query(User).filter(User.is_active == True).all()
        return [self._user_to_dict(user) for user in users]

    def create_user(self, name: str, telegram_id: int, phone_number: str = None) -> Dict:
        """Create new user"""
        user = User(
            name=name,
            telegram_id=telegram_id,
            phone_number=phone_number
        )
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return self._user_to_dict(user)

    def update_user_towel_count(self, user_id: int, transaction_type: str, quantity: int) -> Optional[Dict]:
        """Update user towel count based on transaction"""
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            return None

        # Create transaction
        transaction = Transaction(
            user_id=user_id,
            transaction_type=TransactionType.GIVEN if transaction_type == 'given' else TransactionType.TAKEN,
            quantity=quantity,
            notes="Telegram bot orqali"
        )
        self.db.add(transaction)

        # Update user towel count
        if transaction_type == 'given':
            user.towel_count += quantity
        else:  # taken
            user.towel_count -= quantity
            if user.towel_count < 0:
                user.towel_count = 0

        user.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(user)

        return {
            'transaction': self._transaction_to_dict(transaction),
            'user': self._user_to_dict(user)
        }

    def get_user_transactions(self, user_id: int, limit: int = 50) -> List[Dict]:
        """Get transactions for a user"""
        transactions = self.db.query(Transaction).filter(
            Transaction.user_id == user_id
        ).order_by(desc(Transaction.created_at)).limit(limit).all()
        return [self._transaction_to_dict(t) for t in transactions]

    # Inventory operations
    def get_inventory(self) -> Optional[Dict]:
        """Get inventory status"""
        inventory = self.db.query(Inventory).first()
        if not inventory:
            # Create default inventory if not exists
            inventory = Inventory(total_towels=0, remaining_towels=0)
            self.db.add(inventory)
            self.db.commit()
            self.db.refresh(inventory)
        return self._inventory_to_dict(inventory)

    def update_inventory(self, total_towels: int = None, remaining_towels: int = None):
        """Update inventory"""
        inventory = self.db.query(Inventory).first()
        if not inventory:
            inventory = Inventory()
            self.db.add(inventory)

        if total_towels is not None:
            inventory.total_towels = total_towels
        if remaining_towels is not None:
            inventory.remaining_towels = remaining_towels

        inventory.last_updated = datetime.utcnow()
        self.db.commit()

    def add_towels_to_inventory(self, quantity: int) -> Dict:
        """Add towels to inventory"""
        inventory = self.db.query(Inventory).first()
        if not inventory:
            inventory = Inventory(total_towels=0, remaining_towels=0)
            self.db.add(inventory)

        inventory.total_towels += quantity
        inventory.remaining_towels += quantity
        inventory.last_updated = datetime.utcnow()
        self.db.commit()
        self.db.refresh(inventory)
        return self._inventory_to_dict(inventory)

    def remove_towels_from_inventory(self, quantity: int) -> Dict:
        """Remove old/damaged towels from inventory"""
        inventory = self.db.query(Inventory).first()
        if not inventory:
            inventory = Inventory(total_towels=0, remaining_towels=0)
            self.db.add(inventory)

        # Ensure we don't remove more than available
        if quantity > inventory.total_towels:
            quantity = inventory.total_towels

        inventory.total_towels -= quantity
        # Also reduce remaining if needed
        if quantity > inventory.remaining_towels:
            inventory.remaining_towels = 0
        else:
            inventory.remaining_towels -= quantity

        inventory.last_updated = datetime.utcnow()
        self.db.commit()
        self.db.refresh(inventory)
        return self._inventory_to_dict(inventory)

    # Report operations
    def get_report(self, period: str = 'today') -> Dict:
        """Get report for a period"""
        now = datetime.utcnow()
        
        if period == 'today':
            start_date = now.replace(hour=0, minute=0, second=0, microsecond=0)
        elif period == 'week':
            start_date = now - timedelta(days=7)
        elif period == 'month':
            start_date = now - timedelta(days=30)
        else:  # all
            start_date = datetime(2000, 1, 1)

        # Get transactions in period
        transactions = self.db.query(Transaction).filter(
            Transaction.created_at >= start_date
        ).all()

        given_towels = sum(
            t.quantity for t in transactions 
            if t.transaction_type == TransactionType.GIVEN
        )
        taken_towels = sum(
            t.quantity for t in transactions 
            if t.transaction_type == TransactionType.TAKEN
        )

        # Calculate total income (for taken towels, we would need price, but we removed it)
        # So for now, we'll just count transactions
        total_transactions = len(transactions)

        return {
            'given_towels': given_towels,
            'taken_towels': taken_towels,
            'total_transactions': total_transactions,
            'start_date': start_date.isoformat(),
            'end_date': now.isoformat()
        }

    # Helper methods
    def _user_to_dict(self, user: User) -> Dict:
        """Convert User model to dict"""
        return {
            'id': user.id,
            'name': user.name,
            'telegram_id': user.telegram_id,
            'phone_number': user.phone_number,
            'towel_count': user.towel_count,
            'is_active': user.is_active,
            'created_at': user.created_at.isoformat() if user.created_at else None,
            'updated_at': user.updated_at.isoformat() if user.updated_at else None
        }

    def _transaction_to_dict(self, transaction: Transaction) -> Dict:
        """Convert Transaction model to dict"""
        return {
            'id': transaction.id,
            'user_id': transaction.user_id,
            'transaction_type': transaction.transaction_type.value,
            'quantity': transaction.quantity,
            'notes': transaction.notes,
            'created_at': transaction.created_at.isoformat() if transaction.created_at else None
        }

    def _inventory_to_dict(self, inventory: Inventory) -> Dict:
        """Convert Inventory model to dict"""
        return {
            'id': inventory.id,
            'total_towels': inventory.total_towels,
            'remaining_towels': inventory.remaining_towels,
            'last_updated': inventory.last_updated.isoformat() if inventory.last_updated else None
        }


# Global instance function
def get_db_service():
    """Get database service instance"""
    return DatabaseService()

