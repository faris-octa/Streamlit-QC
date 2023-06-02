import sqlite3

# Create a connection to the database
conn = sqlite3.connect('qc.db')
c = conn.cursor()

# Define data to be inserted
data = [
    (310302940, 'NICEPOLE PR-99', 'A121212P', '120', 1.0876, 1.008, 5.9833, 3.0988, 7.65, 'Yusril'),
    (310302941, 'NICEPOLE PR-100', 'A121212P', '120', 1.0876, 1.008, 6.9833, 2.4488, 30.5, 'Azhar')
]

# Insert data into table
for row in data:
    c.execute('''INSERT INTO av_temp (sec_item_num, nama_item, LOT, suhu, FAKTOR_BURET, FAKTOR_NaOH, berat_sampel, jumlah_titran, AV, operator) 
                 VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''', row)

# Commit changes and close connection
conn.commit()
conn.close()