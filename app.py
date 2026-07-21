from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3
import os

app = Flask(__name__)
app.secret_key = 'kunci_rahasia_sistem_kos'  # Diperlukan untuk session dan flash message

def get_db_connection():
    conn = sqlite3.connect('instance/database.db')
    conn.row_factory = sqlite3.Row
    return conn

# Helper untuk memproteksi route admin
def login_required(f):
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'admin_logged_in' not in session:
            flash('Silakan login terlebih dahulu!', 'danger')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# --- ROUTE AUTHENTICATION ---
@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        conn = get_db_connection()
        admin = conn.execute('SELECT * FROM admin WHERE username = ? AND password = ?', 
                             (username, password)).fetchone()
        conn.close()
        
        if admin:
            session['admin_logged_in'] = True
            session['username'] = admin['username']
            flash('Berhasil login!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Username atau password salah!', 'danger')
            
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('Anda telah keluar.', 'info')
    return redirect(url_for('login'))

# --- DASHBOARD ADMIN ---
@app.route('/admin/dashboard')
@login_required
def dashboard():
    conn = get_db_connection()
    total_penghuni = conn.execute('SELECT COUNT(*) FROM penghuni').fetchone()[0]
    total_pembayaran = conn.execute('SELECT SUM(jumlah) FROM pembayaran WHERE status = "Lunas"').fetchone()[0] or 0
    pembayaran_terakhir = conn.execute('''
        SELECT p.*, h.nama, h.no_kamar 
        FROM pembayaran p 
        JOIN penghuni h ON p.penghuni_id = h.id 
        ORDER BY p.id DESC LIMIT 5
    ''').fetchall()
    conn.close()
    
    return render_template('admin/dashboard.html', 
                           total_penghuni=total_penghuni, 
                           total_pembayaran=total_pembayaran,
                           pembayaran_terakhir=pembayaran_terakhir)

# --- CRUD PENGHUNI ---
@app.route('/admin/penghuni')
@login_required
def penghuni():
    conn = get_db_connection()
    data_penghuni = conn.execute('SELECT * FROM penghuni').fetchall()
    conn.close()
    return render_template('admin/penghuni.html', penghuni=data_penghuni)

@app.route('/admin/penghuni/tambah', methods=['GET', 'POST'])
@login_required
def tambah_penghuni():
    if request.method == 'POST':
        nama = request.form['nama']
        no_kamar = request.form['no_kamar']
        no_hp = request.form['no_hp']
        
        if not nama or not no_kamar:
            flash('Semua field wajib diisi!', 'warning')
        else:
            conn = get_db_connection()
            conn.execute('INSERT INTO penghuni (nama, no_kamar, no_hp) VALUES (?, ?, ?)',
                         (nama, no_kamar, no_hp))
            conn.commit()
            conn.close()
            flash('Penghuni berhasil ditambahkan!', 'success')
            return redirect(url_for('penghuni'))
            
    return render_template('admin/form_penghuni.html')

@app.route('/admin/penghuni/hapus/<int:id>')
@login_required
def hapus_penghuni(id):
    conn = get_db_connection()
    conn.execute('DELETE FROM penghuni WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    flash('Data penghuni berhasil dihapus.', 'info')
    return redirect(url_for('penghuni'))

# --- CRUD PEMBAYARAN ---
@app.route('/admin/pembayaran')
@login_required
def pembayaran():
    conn = get_db_connection()
    data_pembayaran = conn.execute('''
        SELECT p.*, h.nama, h.no_kamar 
        FROM pembayaran p 
        JOIN penghuni h ON p.penghuni_id = h.id
    ''').fetchall()
    conn.close()
    return render_template('admin/pembayaran.html', pembayaran=data_pembayaran)

@app.route('/admin/pembayaran/tambah', methods=['GET', 'POST'])
@login_required
def tambah_pembayaran():
    conn = get_db_connection()
    penghuni_list = conn.execute('SELECT * FROM penghuni').fetchall()
    
    if request.method == 'POST':
        penghuni_id = request.form['penghuni_id']
        tanggal_bayar = request.form['tanggal_bayar']
        bulan_tagihan = request.form['bulan_tagihan']
        jumlah = request.form['jumlah']
        status = request.form['status']
        
        conn.execute('''
            INSERT INTO pembayaran (penghuni_id, tanggal_bayar, bulan_tagihan, jumlah, status)
            VALUES (?, ?, ?, ?, ?)
        ''', (penghuni_id, tanggal_bayar, bulan_tagihan, jumlah, status))
        conn.commit()
        conn.close()
        flash('Catatan pembayaran berhasil ditambahkan!', 'success')
        return redirect(url_for('pembayaran'))
        
    conn.close()
    return render_template('admin/form_pembayaran.html', penghuni_list=penghuni_list)

if __name__ == '__main__':
    # Memastikan folder instance ada
    if not os.path.exists('instance'):
        os.makedirs('instance')
    app.run(debug=True)