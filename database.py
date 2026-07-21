import sqlite3

def init_db():
    conn = sqlite3.connect('instance/database.db')
    cursor = conn.cursor()
    
    # Tabel Admin
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS admin (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    ''')
    
    # Tabel Penghuni (Entitas 1)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS penghuni (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nama TEXT NOT NULL,
            no_kamar TEXT NOT NULL,
            no_hp TEXT NOT NULL
        )
    ''')
    
    # Tabel Pembayaran (Entitas 2)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS pembayaran (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            penghuni_id INTEGER NOT NULL,
            tanggal_bayar TEXT NOT NULL,
            bulan_tagihan TEXT NOT NULL,
            jumlah REAL NOT NULL,
            status TEXT NOT NULL,
            FOREIGN KEY (penghuni_id) REFERENCES penghuni (id) ON DELETE CASCADE
        )
    ''')
    
    # Menambahkan admin default jika belum ada (Username: admin, Password: admin123)
    cursor.execute("SELECT * FROM admin WHERE username = 'admin'")
    if not cursor.fetchone():
        cursor.execute("INSERT INTO admin (username, password) VALUES (?, ?)", ('admin', 'admin123'))
        
    conn.commit()
    conn.close()

if __name__ == '__main__':
    init_db()
    print("Database berhasil diinisialisasi.")