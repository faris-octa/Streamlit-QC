import sqlite3

conn = sqlite3.connect('qc.db')
c = conn.cursor()

# #solid contents table
# c.execute('''CREATE TABLE solid_contents (
#     id INTEGER,
#     sec_item_num INTEGER NOT NULL,
#     nama_item TEXT,
#     berat_wadah REAL,
#     berat_sampel_basah REAL,
#     timestamp_init DATETIME NOT NULL DEFAULT (strftime('%Y-%m-%d %H:%M:%S', 'now', 'localtime')),
#     berat_sampel_kering REAL,
#     timestamp2 DATETIME,
#     PRIMARY KEY("id" AUTOINCREMENT)
#     );''')

# AV table
c.execute('''CREATE TABLE av_temp (
    id INTEGER,
    sec_item_num INTEGER NOT NULL,
    nama_item TEXT,
    LOT TEXT,
    timestamp DATETIME NOT NULL DEFAULT (strftime('%Y-%m-%d %H:%M:%S', 'now', 'localtime')),
    suhu TEXT,
    FAKTOR_BURET REAL,
    FAKTOR_NaOH REAL,
    berat_sampel REAL,
    jumlah_titran REAL,
    AV REAL,
    keterangan TEXT,
    operator TEXT,
    PRIMARY KEY("id" AUTOINCREMENT)
    );''')

conn.commit()
conn.close()