# -*- coding: utf-8 -*-
"""
Panier d'achat
"""
from typing import List, Dict, Optional
from modules.products.product_manager import product_manager


class CartItem:
    """Article dans le panier"""
    
    def __init__(self, product: Dict, quantity: float = 1.0):
        self.product_id = product['id']
        self.product_name = product['name']
        self.product_name_ar = product.get('name_ar', '')
        self.barcode = product.get('barcode', '')
        self.unit_price = product['selling_price']
        self.purchase_price = product['purchase_price']
        self.quantity = quantity
        self.discount_percentage = product.get('discount_percentage', 0.0)
        self.is_on_promotion = product.get('is_on_promotion', 0)
        
    def get_subtotal(self) -> float:
        """Calculer le sous-total (avec réduction produit)"""
        price = self.unit_price * (1 - self.discount_percentage / 100.0)
        return round(price * self.quantity, 2)
    
    def get_profit(self) -> float:
        """Calculer le bénéfice sur cet article"""
        selling = self.unit_price * (1 - self.discount_percentage / 100.0)
        profit_per_unit = selling - self.purchase_price
        return round(profit_per_unit * self.quantity, 2)
    
    def to_dict(self) -> Dict:
        """Convertir en dictionnaire"""
        return {
            'product_id': self.product_id,
            'product_name': self.product_name,
            'product_name_ar': self.product_name_ar,
            'barcode': self.barcode,
            'quantity': self.quantity,
            'unit_price': self.unit_price,
            'purchase_price': self.purchase_price,
            'discount_percentage': self.discount_percentage,
            'subtotal': self.get_subtotal(),
            'profit': self.get_profit(),
        }


class Cart:
    """Panier d'achat"""
    
    def __init__(self):
        self.items: List[CartItem] = []
        self.discount_percentage = 0.0  # Réduction globale
        self.discount_amount = 0.0  # Réduction en montant fixe
    
    def add_item(self, product: Dict, quantity: float = 1.0) -> tuple[bool, str]:
        """
        Ajouter un article au panier
        
        Args:
            product: Dictionnaire du produit
            quantity: Quantité
            
        Returns:
            (success, message)
        """
        # Vérifier le stock disponible
        if product['stock_quantity'] < quantity:
            return False, f"Stock insuffisant. Disponible: {product['stock_quantity']}"
        
        # Vérifier si le produit est déjà dans le panier
        for item in self.items:
            if item.product_id == product['id']:
                # Vérifier le stock total
                new_quantity = item.quantity + quantity
                if product['stock_quantity'] < new_quantity:
                    return False, f"Stock insuffisant. Disponible: {product['stock_quantity']}"
                
                item.quantity = new_quantity
                return True, f"Quantité mise à jour: {new_quantity}"
        
        # Ajouter un nouvel article
        cart_item = CartItem(product, quantity)
        self.items.append(cart_item)
        return True, "Article ajouté au panier"
    
    def remove_item(self, product_id: int) -> tuple[bool, str]:
        """
        Retirer un article du panier
        
        Args:
            product_id: ID du produit
            
        Returns:
            (success, message)
        """
        for i, item in enumerate(self.items):
            if item.product_id == product_id:
                self.items.pop(i)
                return True, "Article retiré du panier"
        
        return False, "Article introuvable dans le panier"
    
    def update_quantity(self, product_id: int, quantity: float) -> tuple[bool, str]:
        """
        Mettre à jour la quantité d'un article
        
        Args:
            product_id: ID du produit
            quantity: Nouvelle quantité
            
        Returns:
            (success, message)
        """
        if quantity <= 0:
            return self.remove_item(product_id)
        
        for item in self.items:
            if item.product_id == product_id:
                # Vérifier le stock
                product = product_manager.get_product(product_id)
                if product and product['stock_quantity'] < quantity:
                    return False, f"Stock insuffisant. Disponible: {product['stock_quantity']}"
                
                item.quantity = quantity
                return True, f"Quantité mise à jour: {quantity}"
        
        return False, "Article introuvable dans le panier"
    
    def clear(self):
        """Vider le panier"""
        self.items = []
        self.discount_percentage = 0.0
        self.discount_amount = 0.0
    
    def get_item_count(self) -> int:
        """Obtenir le nombre d'articles différents"""
        return len(self.items)
    
    def get_total_quantity(self) -> float:
        """Obtenir la quantité totale d'articles"""
        return sum(item.quantity for item in self.items)
    
    def get_subtotal(self) -> float:
        """Calculer le sous-total (avant réduction globale)"""
        return round(sum(item.get_subtotal() for item in self.items), 2)
    
    def set_discount_percentage(self, percentage: float) -> tuple[bool, str]:
        """
        Appliquer une réduction en pourcentage
        
        Args:
            percentage: Pourcentage de réduction (0-100)
            
        Returns:
            (success, message)
        """
        if percentage < 0 or percentage > 100:
            return False, "Le pourcentage doit être entre 0 et 100"
        
        self.discount_percentage = percentage
        self.discount_amount = 0.0  # Réinitialiser la réduction fixe
        return True, f"Réduction de {percentage}% appliquée"
    
    def set_discount_amount(self, amount: float) -> tuple[bool, str]:
        """
        Appliquer une réduction en montant fixe
        
        Args:
            amount: Montant de la réduction
            
        Returns:
            (success, message)
        """
        if amount < 0:
            return False, "Le montant doit être positif"
        
        subtotal = self.get_subtotal()
        if amount > subtotal:
            return False, f"La réduction ne peut pas dépasser le sous-total ({subtotal} DA)"
        
        self.discount_amount = amount
        self.discount_percentage = 0.0  # Réinitialiser la réduction en %
        return True, f"Réduction de {amount} DA appliquée"
    
    def get_discount_amount(self) -> float:
        """Calculer le montant de la réduction"""
        if self.discount_amount > 0:
            return round(self.discount_amount, 2)
        elif self.discount_percentage > 0:
            subtotal = self.get_subtotal()
            return round(subtotal * self.discount_percentage / 100.0, 2)
        return 0.0
    
    def get_total(self) -> float:
        """Calculer le total final"""
        subtotal = self.get_subtotal()
        discount = self.get_discount_amount()
        return round(subtotal - discount, 2)
    
    def get_total_profit(self) -> float:
        """Calculer le bénéfice total"""
        return round(sum(item.get_profit() for item in self.items), 2)
    
    def to_dict(self) -> Dict:
        """Convertir le panier en dictionnaire"""
        return {
            'items': [item.to_dict() for item in self.items],
            'item_count': self.get_item_count(),
            'total_quantity': self.get_total_quantity(),
            'subtotal': self.get_subtotal(),
            'discount_percentage': self.discount_percentage,
            'discount_amount': self.get_discount_amount(),
            'total': self.get_total(),
            'profit': self.get_total_profit(),
        }
    
    def is_empty(self) -> bool:
        """Vérifier si le panier est vide"""
        return len(self.items) == 0
