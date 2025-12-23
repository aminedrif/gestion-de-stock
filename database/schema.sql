-- Schéma de base de données SQLite pour Gestion Mini-Market
-- Version 1.0.0

-- ============================================================================
-- TABLE: users (Utilisateurs)
-- ============================================================================
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    full_name TEXT NOT NULL,
    role TEXT NOT NULL CHECK(role IN ('admin', 'cashier')),
    email TEXT,
    phone TEXT,
    is_active INTEGER DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP,
    failed_login_attempts INTEGER DEFAULT 0,
    locked_until TIMESTAMP
);

-- Index pour recherche rapide
CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);
CREATE INDEX IF NOT EXISTS idx_users_role ON users(role);

-- ============================================================================
-- TABLE: categories (Catégories de produits)
-- ============================================================================
CREATE TABLE IF NOT EXISTS categories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    name_ar TEXT,  -- Nom en arabe
    description TEXT,
    parent_id INTEGER,  -- Pour sous-catégories
    is_active INTEGER DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (parent_id) REFERENCES categories(id) ON DELETE SET NULL
);

CREATE INDEX IF NOT EXISTS idx_categories_name ON categories(name);
CREATE INDEX IF NOT EXISTS idx_categories_parent ON categories(parent_id);

-- ============================================================================
-- TABLE: products (Produits)
-- ============================================================================
CREATE TABLE IF NOT EXISTS products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    barcode TEXT UNIQUE,
    name TEXT NOT NULL,
    name_ar TEXT,  -- Nom en arabe
    description TEXT,
    category_id INTEGER,
    
    -- Prix et coûts
    purchase_price REAL NOT NULL DEFAULT 0.0,  -- Prix d'achat
    selling_price REAL NOT NULL,  -- Prix de vente
    discount_percentage REAL DEFAULT 0.0,  -- Promotion
    is_on_promotion INTEGER DEFAULT 0,
    
    -- Stock
    stock_quantity INTEGER DEFAULT 0,
    min_stock_level INTEGER DEFAULT 10,  -- Alerte stock minimum
    unit TEXT DEFAULT 'pièce',  -- unité, kg, litre, etc.
    
    -- Dates
    expiry_date DATE,  -- Date d'expiration
    manufacturing_date DATE,
    
    -- Fournisseur
    supplier_id INTEGER,
    
    -- Statut
    is_active INTEGER DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by INTEGER,
    
    FOREIGN KEY (category_id) REFERENCES categories(id) ON DELETE SET NULL,
    FOREIGN KEY (supplier_id) REFERENCES suppliers(id) ON DELETE SET NULL,
    FOREIGN KEY (created_by) REFERENCES users(id)
);

-- Index pour performances
CREATE INDEX IF NOT EXISTS idx_products_barcode ON products(barcode);
CREATE INDEX IF NOT EXISTS idx_products_name ON products(name);
CREATE INDEX IF NOT EXISTS idx_products_category ON products(category_id);
CREATE INDEX IF NOT EXISTS idx_products_supplier ON products(supplier_id);
CREATE INDEX IF NOT EXISTS idx_products_active ON products(is_active);

-- ============================================================================
-- TABLE: price_history (Historique des prix)
-- ============================================================================
CREATE TABLE IF NOT EXISTS price_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    product_id INTEGER NOT NULL,
    old_purchase_price REAL,
    new_purchase_price REAL,
    old_selling_price REAL,
    new_selling_price REAL,
    changed_by INTEGER,
    changed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    reason TEXT,
    
    FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE,
    FOREIGN KEY (changed_by) REFERENCES users(id)
);

CREATE INDEX IF NOT EXISTS idx_price_history_product ON price_history(product_id);
CREATE INDEX IF NOT EXISTS idx_price_history_date ON price_history(changed_at);

-- ============================================================================
-- TABLE: customers (Clients)
-- ============================================================================
CREATE TABLE IF NOT EXISTS customers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    code TEXT UNIQUE,  -- Code client auto-généré
    full_name TEXT NOT NULL,
    phone TEXT,
    email TEXT,
    address TEXT,
    
    -- Crédit
    credit_limit REAL DEFAULT 0.0,  -- Limite de crédit autorisée
    current_credit REAL DEFAULT 0.0,  -- Crédit actuel (dette)
    
    -- Statistiques
    total_purchases REAL DEFAULT 0.0,
    purchase_count INTEGER DEFAULT 0,
    last_purchase_date TIMESTAMP,
    
    -- Fidélité
    loyalty_points INTEGER DEFAULT 0,
    
    is_active INTEGER DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    notes TEXT
);

CREATE INDEX IF NOT EXISTS idx_customers_code ON customers(code);
CREATE INDEX IF NOT EXISTS idx_customers_phone ON customers(phone);
CREATE INDEX IF NOT EXISTS idx_customers_name ON customers(full_name);

-- ============================================================================
-- TABLE: suppliers (Fournisseurs)
-- ============================================================================
CREATE TABLE IF NOT EXISTS suppliers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    code TEXT UNIQUE,
    company_name TEXT NOT NULL,
    contact_person TEXT,
    phone TEXT,
    email TEXT,
    address TEXT,
    
    -- Finances
    total_debt REAL DEFAULT 0.0,  -- Dette totale envers le fournisseur
    total_purchases REAL DEFAULT 0.0,  -- Total des achats effectués chez ce fournisseur
    
    is_active INTEGER DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    notes TEXT
);

CREATE INDEX IF NOT EXISTS idx_suppliers_code ON suppliers(code);
CREATE INDEX IF NOT EXISTS idx_suppliers_name ON suppliers(company_name);

-- ============================================================================
-- TABLE: sales (Ventes - En-tête)
-- ============================================================================
CREATE TABLE IF NOT EXISTS sales (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    sale_number TEXT UNIQUE NOT NULL,  -- Numéro de vente (auto-généré)
    
    -- Client et caissier
    customer_id INTEGER,
    cashier_id INTEGER NOT NULL,
    
    -- Montants
    subtotal REAL NOT NULL DEFAULT 0.0,  -- Sous-total
    discount_amount REAL DEFAULT 0.0,  -- Réduction
    tax_amount REAL DEFAULT 0.0,  -- TVA
    total_amount REAL NOT NULL,  -- Total final
    
    -- Paiement
    payment_method TEXT DEFAULT 'cash' CHECK(payment_method IN ('cash', 'card', 'credit', 'mixed')),
    amount_paid REAL DEFAULT 0.0,
    change_amount REAL DEFAULT 0.0,
    
    -- Caisse
    register_number INTEGER DEFAULT 1,  -- Numéro de caisse
    
    -- Statut
    status TEXT DEFAULT 'completed' CHECK(status IN ('completed', 'returned', 'cancelled')),
    
    sale_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    notes TEXT,
    
    FOREIGN KEY (customer_id) REFERENCES customers(id) ON DELETE SET NULL,
    FOREIGN KEY (cashier_id) REFERENCES users(id)
);

CREATE INDEX IF NOT EXISTS idx_sales_number ON sales(sale_number);
CREATE INDEX IF NOT EXISTS idx_sales_customer ON sales(customer_id);
CREATE INDEX IF NOT EXISTS idx_sales_cashier ON sales(cashier_id);
CREATE INDEX IF NOT EXISTS idx_sales_date ON sales(sale_date);
CREATE INDEX IF NOT EXISTS idx_sales_status ON sales(status);

-- ============================================================================
-- TABLE: sale_items (Détails des ventes - Lignes)
-- ============================================================================
CREATE TABLE IF NOT EXISTS sale_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    sale_id INTEGER NOT NULL,
    product_id INTEGER NOT NULL,
    
    product_name TEXT NOT NULL,  -- Copie du nom (au cas où produit supprimé)
    barcode TEXT,
    
    quantity REAL NOT NULL,
    unit_price REAL NOT NULL,  -- Prix unitaire au moment de la vente
    discount_percentage REAL DEFAULT 0.0,
    subtotal REAL NOT NULL,  -- quantity * unit_price * (1 - discount)
    
    -- Pour calcul du bénéfice
    purchase_price REAL,  -- Prix d'achat au moment de la vente
    
    FOREIGN KEY (sale_id) REFERENCES sales(id) ON DELETE CASCADE,
    FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE SET NULL
);

CREATE INDEX IF NOT EXISTS idx_sale_items_sale ON sale_items(sale_id);
CREATE INDEX IF NOT EXISTS idx_sale_items_product ON sale_items(product_id);

-- ============================================================================
-- TABLE: returns (Retours/Annulations)
-- ============================================================================
CREATE TABLE IF NOT EXISTS returns (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    return_number TEXT UNIQUE NOT NULL,
    original_sale_id INTEGER NOT NULL,
    
    return_amount REAL NOT NULL,
    refund_method TEXT DEFAULT 'cash',
    
    processed_by INTEGER NOT NULL,
    return_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    reason TEXT,
    
    FOREIGN KEY (original_sale_id) REFERENCES sales(id) ON DELETE CASCADE,
    FOREIGN KEY (processed_by) REFERENCES users(id)
);

CREATE INDEX IF NOT EXISTS idx_returns_sale ON returns(original_sale_id);
CREATE INDEX IF NOT EXISTS idx_returns_date ON returns(return_date);

-- ============================================================================
-- TABLE: return_items (Détails des retours)
-- ============================================================================
CREATE TABLE IF NOT EXISTS return_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    return_id INTEGER NOT NULL,
    sale_item_id INTEGER NOT NULL,
    product_id INTEGER NOT NULL,
    
    quantity_returned REAL NOT NULL,
    unit_price REAL NOT NULL,
    subtotal REAL NOT NULL,
    
    FOREIGN KEY (return_id) REFERENCES returns(id) ON DELETE CASCADE,
    FOREIGN KEY (sale_item_id) REFERENCES sale_items(id),
    FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE SET NULL
);

CREATE INDEX IF NOT EXISTS idx_return_items_return ON return_items(return_id);

-- ============================================================================
-- TABLE: supplier_transactions (Transactions fournisseurs)
-- ============================================================================
CREATE TABLE IF NOT EXISTS supplier_transactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    supplier_id INTEGER NOT NULL,
    transaction_type TEXT CHECK(transaction_type IN ('purchase', 'payment', 'adjustment')),
    
    amount REAL NOT NULL,
    description TEXT,
    
    processed_by INTEGER NOT NULL,
    transaction_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (supplier_id) REFERENCES suppliers(id) ON DELETE CASCADE,
    FOREIGN KEY (processed_by) REFERENCES users(id)
);

CREATE INDEX IF NOT EXISTS idx_supplier_trans_supplier ON supplier_transactions(supplier_id);
CREATE INDEX IF NOT EXISTS idx_supplier_trans_date ON supplier_transactions(transaction_date);

-- ============================================================================
-- TABLE: customer_credit_transactions (Transactions crédit client)
-- ============================================================================
CREATE TABLE IF NOT EXISTS customer_credit_transactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_id INTEGER NOT NULL,
    transaction_type TEXT CHECK(transaction_type IN ('credit_sale', 'payment', 'adjustment')),
    
    amount REAL NOT NULL,
    sale_id INTEGER,  -- Si lié à une vente
    
    processed_by INTEGER NOT NULL,
    transaction_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    notes TEXT,
    
    FOREIGN KEY (customer_id) REFERENCES customers(id) ON DELETE CASCADE,
    FOREIGN KEY (sale_id) REFERENCES sales(id) ON DELETE SET NULL,
    FOREIGN KEY (processed_by) REFERENCES users(id)
);

CREATE INDEX IF NOT EXISTS idx_customer_credit_customer ON customer_credit_transactions(customer_id);
CREATE INDEX IF NOT EXISTS idx_customer_credit_date ON customer_credit_transactions(transaction_date);

-- ============================================================================
-- TABLE: audit_log (Journal des actions)
-- ============================================================================
CREATE TABLE IF NOT EXISTS audit_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    action TEXT NOT NULL,  -- 'login', 'logout', 'create_product', 'delete_sale', etc.
    entity_type TEXT,  -- 'product', 'sale', 'customer', etc.
    entity_id INTEGER,
    old_value TEXT,  -- JSON des anciennes valeurs
    new_value TEXT,  -- JSON des nouvelles valeurs
    ip_address TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL
);

CREATE INDEX IF NOT EXISTS idx_audit_user ON audit_log(user_id);
CREATE INDEX IF NOT EXISTS idx_audit_action ON audit_log(action);
CREATE INDEX IF NOT EXISTS idx_audit_timestamp ON audit_log(timestamp);

-- ============================================================================
-- TABLE: settings (Paramètres de l'application)
-- ============================================================================
CREATE TABLE IF NOT EXISTS settings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    setting_key TEXT UNIQUE NOT NULL,
    setting_value TEXT,
    setting_type TEXT DEFAULT 'string',  -- 'string', 'integer', 'float', 'boolean', 'json'
    description TEXT,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_by INTEGER,
    
    FOREIGN KEY (updated_by) REFERENCES users(id)
);

CREATE INDEX IF NOT EXISTS idx_settings_key ON settings(setting_key);

-- ============================================================================
-- TRIGGERS (Déclencheurs automatiques)
-- ============================================================================

-- Trigger: Mettre à jour updated_at automatiquement
CREATE TRIGGER IF NOT EXISTS update_users_timestamp 
AFTER UPDATE ON users
BEGIN
    UPDATE users SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
END;

CREATE TRIGGER IF NOT EXISTS update_categories_timestamp 
AFTER UPDATE ON categories
BEGIN
    UPDATE categories SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
END;

CREATE TRIGGER IF NOT EXISTS update_products_timestamp 
AFTER UPDATE ON products
BEGIN
    UPDATE products SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
END;

CREATE TRIGGER IF NOT EXISTS update_customers_timestamp 
AFTER UPDATE ON customers
BEGIN
    UPDATE customers SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
END;

CREATE TRIGGER IF NOT EXISTS update_suppliers_timestamp 
AFTER UPDATE ON suppliers
BEGIN
    UPDATE suppliers SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
END;

-- Trigger: Enregistrer l'historique des prix lors de modification
CREATE TRIGGER IF NOT EXISTS track_price_changes
AFTER UPDATE OF purchase_price, selling_price ON products
WHEN OLD.purchase_price != NEW.purchase_price OR OLD.selling_price != NEW.selling_price
BEGIN
    INSERT INTO price_history (
        product_id, 
        old_purchase_price, 
        new_purchase_price,
        old_selling_price, 
        new_selling_price,
        changed_at
    ) VALUES (
        NEW.id,
        OLD.purchase_price,
        NEW.purchase_price,
        OLD.selling_price,
        NEW.selling_price,
        CURRENT_TIMESTAMP
    );
END;

-- ============================================================================
-- VUES (Views) pour rapports
-- ============================================================================

-- Vue: Produits avec stock faible
CREATE VIEW IF NOT EXISTS low_stock_products AS
SELECT 
    p.id,
    p.barcode,
    p.name,
    p.name_ar,
    p.stock_quantity,
    p.min_stock_level,
    c.name as category_name,
    p.selling_price
FROM products p
LEFT JOIN categories c ON p.category_id = c.id
WHERE p.stock_quantity <= p.min_stock_level 
  AND p.is_active = 1;

-- Vue: Produits expirant bientôt
CREATE VIEW IF NOT EXISTS expiring_products AS
SELECT 
    p.id,
    p.barcode,
    p.name,
    p.name_ar,
    p.expiry_date,
    p.stock_quantity,
    c.name as category_name,
    CAST((julianday(p.expiry_date) - julianday('now')) AS INTEGER) as days_until_expiry
FROM products p
LEFT JOIN categories c ON p.category_id = c.id
WHERE p.expiry_date IS NOT NULL 
  AND p.expiry_date > date('now')
  AND p.expiry_date <= date('now', '+30 days')
  AND p.is_active = 1
ORDER BY p.expiry_date ASC;

-- Vue: Ventes du jour
CREATE VIEW IF NOT EXISTS today_sales AS
SELECT 
    s.id,
    s.sale_number,
    s.total_amount,
    s.payment_method,
    s.sale_date,
    u.full_name as cashier_name,
    c.full_name as customer_name
FROM sales s
LEFT JOIN users u ON s.cashier_id = u.id
LEFT JOIN customers c ON s.customer_id = c.id
WHERE date(s.sale_date) = date('now')
  AND s.status = 'completed';

-- Vue: Top produits vendus
CREATE VIEW IF NOT EXISTS top_selling_products AS
SELECT 
    p.id,
    p.name,
    p.name_ar,
    SUM(si.quantity) as total_quantity_sold,
    SUM(si.subtotal) as total_revenue,
    COUNT(DISTINCT si.sale_id) as number_of_sales
FROM sale_items si
JOIN products p ON si.product_id = p.id
JOIN sales s ON si.sale_id = s.id
WHERE s.status = 'completed'
GROUP BY p.id, p.name, p.name_ar
ORDER BY total_quantity_sold DESC;

-- ============================================================================
-- DONNÉES INITIALES
-- ============================================================================

-- Utilisateur admin par défaut (mot de passe: admin123)
-- Hash bcrypt de "admin123"
INSERT OR IGNORE INTO users (username, password_hash, full_name, role, is_active) 
VALUES ('admin', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYqVr/qvIyW', 'Administrateur', 'admin', 1);

-- Catégories par défaut
INSERT OR IGNORE INTO categories (name, name_ar, description) VALUES 
('Alimentation', 'المواد الغذائية', 'Produits alimentaires'),
('Boissons', 'المشروبات', 'Boissons diverses'),
('Hygiène', 'النظافة', 'Produits d''hygiène'),
('Entretien', 'التنظيف', 'Produits d''entretien'),
('Divers', 'متنوعات', 'Produits divers');

-- Paramètres par défaut
INSERT OR IGNORE INTO settings (setting_key, setting_value, setting_type, description) VALUES
('store_name', 'Mini-Market', 'string', 'Nom du magasin'),
('store_address', '123 Rue Principale', 'string', 'Adresse du magasin'),
('store_phone', '+213 XX XX XX XX', 'string', 'Téléphone du magasin'),
('currency', 'DA', 'string', 'Devise'),
('tax_rate', '19.0', 'float', 'Taux de TVA (%)'),
('receipt_header', 'Merci pour votre visite !', 'string', 'En-tête du ticket'),
('receipt_footer', 'À bientôt !', 'string', 'Pied de page du ticket'),
('default_language', 'fr', 'string', 'Langue par défaut'),
('auto_backup', '1', 'boolean', 'Sauvegarde automatique activée'),
('low_stock_alert', '1', 'boolean', 'Alertes stock faible activées');
