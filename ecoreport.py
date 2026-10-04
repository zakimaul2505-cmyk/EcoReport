
import csv
import os
import sqlite3
from datetime import datetime
import tkinter as tk
from tkinter import ttk, messagebox, filedialog

APP_NAME = "EcoReport"
APP_SUBTITLE = "Environmental Monitoring & Reporting System"
DB_DIR = "data"
DB_FILE = os.path.join(DB_DIR, "ecoreport.db")
FOCUS_REGION = "Kota Sukabumi"

os.makedirs(DB_DIR, exist_ok=True)

def db():
    con = sqlite3.connect(DB_FILE)
    con.row_factory = sqlite3.Row
    return con

def init_db():
    con = db()
    cur = con.cursor()
    cur.executescript("""
    CREATE TABLE IF NOT EXISTS users(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password TEXT,
        role TEXT
    );
    CREATE TABLE IF NOT EXISTS reports(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        code TEXT UNIQUE,
        reporter TEXT,
        category TEXT,
        location TEXT,
        district TEXT,
        latitude REAL,
        longitude REAL,
        severity TEXT,
        description TEXT,
        status TEXT,
        officer TEXT,
        created_at TEXT,
        updated_at TEXT
    );
    CREATE TABLE IF NOT EXISTS activity(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        report_code TEXT,
        actor TEXT,
        action TEXT,
        created_at TEXT
    );
    """)
    cur.execute("SELECT COUNT(*) FROM users")
    if cur.fetchone()[0] == 0:
        cur.execute("INSERT INTO users(username,password,role) VALUES(?,?,?)",
                    ("admin", "EcoEnv2026!", "Administrator"))
        cur.execute("INSERT INTO users(username,password,role) VALUES(?,?,?)",
                    ("petugas", "petugas123", "Petugas Lapangan"))

    cur.execute("SELECT COUNT(*) FROM reports")
    if cur.fetchone()[0] == 0:
        now = datetime.now().strftime("%Y-%m-%d %H:%M")
        samples = [
            ("ER-20261001-0001","Andi","Sampah","Jl. Pelabuhan II","Citamiang",-6.923,106.929,"Tinggi",
             "Tumpukan sampah di sekitar saluran drainase.","Diproses","Budi",now,now),
            ("ER-20261001-0002","Siti","Pencemaran Air","Sungai Cipelang","Lembursitu",-6.946,106.889,"Sedang",
             "Air terlihat keruh dan terdapat bau tidak normal.","Diverifikasi","Raka",now,now),
            ("ER-20261002-0003","Dimas","Ruang Hijau","Taman Kota","Cikole",-6.918,106.932,"Rendah",
             "Beberapa fasilitas taman mengalami kerusakan.","Baru","",now,now),
            ("ER-20261002-0004","Nina","Polusi Udara","Koridor Jalan A. Yani","Cikole",-6.917,106.930,"Sedang",
             "Keluhan asap kendaraan pada jam sibuk.","Selesai","Budi",now,now),
        ]
        cur.executemany("""INSERT INTO reports
            (code,reporter,category,location,district,latitude,longitude,severity,description,status,officer,created_at,updated_at)
            VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)""", samples)
    con.commit()
    con.close()

def next_code():
    stamp = datetime.now().strftime("%Y%m%d")
    con = db()
    n = con.execute("SELECT COUNT(*) FROM reports WHERE code LIKE ?", (f"ER-{stamp}-%",)).fetchone()[0] + 1
    con.close()
    return f"ER-{stamp}-{n:04d}"

class App(tk.Tk):
    def __init__(self, username, role):
        super().__init__()
        self.username, self.role = username, role
        self.title(f"{APP_NAME} • {APP_SUBTITLE}")
        self.geometry("1280x760")
        self.minsize(1100, 680)
        self.configure(bg="#F4F7F5")
        self.style = ttk.Style(self)
        try: self.style.theme_use("clam")
        except: pass
        self.style.configure("Treeview", rowheight=34, font=("Segoe UI",10), background="white", fieldbackground="white")
        self.style.configure("Treeview.Heading", font=("Segoe UI Semibold",10))
        self.style.map("Treeview", background=[("selected","#DDF3E5")], foreground=[("selected","#163D2A")])
        self.sidebar = tk.Frame(self, bg="#123B2A", width=245)
        self.sidebar.pack(side="left", fill="y")
        self.content = tk.Frame(self, bg="#F4F7F5")
        self.content.pack(side="right", fill="both", expand=True)
        self.build_sidebar()
        self.show_dashboard()

    def build_sidebar(self):
        for w in self.sidebar.winfo_children(): w.destroy()
        tk.Label(self.sidebar,text="🌿",font=("Segoe UI",32),bg="#123B2A",fg="#8BE0A9").pack(anchor="w",padx=24,pady=(28,0))
        tk.Label(self.sidebar,text=APP_NAME,font=("Segoe UI Semibold",22),bg="#123B2A",fg="white").pack(anchor="w",padx=24)
        tk.Label(self.sidebar,text="Environmental Monitoring",font=("Segoe UI",9),bg="#123B2A",fg="#A9C8B7").pack(anchor="w",padx=26,pady=(0,25))
        items = [
            ("⌂","Dashboard",self.show_dashboard),
            ("＋","Buat Pengaduan",self.show_form),
            ("▣","Data Pengaduan",self.show_reports),
            ("⌖","Peta & Wilayah",self.show_map),
            ("◈","Monitoring",self.show_monitoring),
            ("▥","Analitik",self.show_analytics),
            ("▤","Laporan",self.show_reporting),
        ]
        for icon,label,cmd in items:
            b=tk.Button(self.sidebar,text=f"  {icon}   {label}",command=cmd,anchor="w",
                        font=("Segoe UI",10),bg="#123B2A",fg="#E7F4EC",activebackground="#1D5A40",
                        activeforeground="white",bd=0,relief="flat",padx=20,pady=12,cursor="hand2")
            b.pack(fill="x",padx=10,pady=2)
        spacer=tk.Frame(self.sidebar,bg="#123B2A"); spacer.pack(fill="both",expand=True)
        tk.Label(self.sidebar,text=f"{self.username}  •  {self.role}",font=("Segoe UI",9),
                 bg="#123B2A",fg="#B8D2C2").pack(anchor="w",padx=24,pady=(0,4))
        tk.Label(self.sidebar,text=f"Fokus: {FOCUS_REGION}",font=("Segoe UI",9),
                 bg="#123B2A",fg="#B8D2C2").pack(anchor="w",padx=24,pady=(0,16))
        tk.Button(self.sidebar,text="↪  Keluar",command=self.logout,anchor="w",font=("Segoe UI",10),
                  bg="#0E3023",fg="#D7E8DE",activebackground="#1D5A40",bd=0,padx=20,pady=11).pack(fill="x",padx=10,pady=(0,15))

    def clear(self):
        for w in self.content.winfo_children(): w.destroy()

    def header(self, title, subtitle=""):
        top=tk.Frame(self.content,bg="#F4F7F5")
        top.pack(fill="x",padx=30,pady=(25,15))
        tk.Label(top,text=title,font=("Segoe UI Semibold",25),bg="#F4F7F5",fg="#163D2A").pack(anchor="w")
        if subtitle: tk.Label(top,text=subtitle,font=("Segoe UI",10),bg="#F4F7F5",fg="#718178").pack(anchor="w",pady=(4,0))

    def card(self,parent,title,value,accent="#2E8B57"):
        f=tk.Frame(parent,bg="white",highlightbackground="#E0E8E3",highlightthickness=1)
        tk.Frame(f,bg=accent,width=5).pack(side="left",fill="y")
        body=tk.Frame(f,bg="white"); body.pack(fill="both",expand=True,padx=18,pady=15)
        tk.Label(body,text=title.upper(),font=("Segoe UI Semibold",8),bg="white",fg="#7B8A82").pack(anchor="w")
        tk.Label(body,text=str(value),font=("Segoe UI Semibold",22),bg="white",fg="#163D2A").pack(anchor="w",pady=(5,0))
        return f

    def query(self, sql, args=()):
        con=db(); rows=con.execute(sql,args).fetchall(); con.close(); return rows

    def show_dashboard(self):
        self.clear(); self.header("Dashboard",f"Ringkasan kondisi pelaporan lingkungan • {FOCUS_REGION}")
        total=self.query("SELECT COUNT(*) n FROM reports")[0]["n"]
        high=self.query("SELECT COUNT(*) n FROM reports WHERE severity='Tinggi'")[0]["n"]
        active=self.query("SELECT COUNT(*) n FROM reports WHERE status IN ('Baru','Diverifikasi','Diproses')")[0]["n"]
        done=self.query("SELECT COUNT(*) n FROM reports WHERE status='Selesai'")[0]["n"]
        row=tk.Frame(self.content,bg="#F4F7F5"); row.pack(fill="x",padx=30)
        for i,(t,v,a) in enumerate([("Total Pengaduan",total,"#2E8B57"),("Prioritas Tinggi",high,"#D97706"),("Sedang Ditangani",active,"#2563EB"),("Selesai",done,"#16A34A")]):
            c=self.card(row,t,v,a); c.grid(row=0,column=i,sticky="nsew",padx=(0,12))
            row.grid_columnconfigure(i,weight=1)
        lower=tk.Frame(self.content,bg="#F4F7F5"); lower.pack(fill="both",expand=True,padx=30,pady=18)
        left=tk.Frame(lower,bg="white",highlightbackground="#E0E8E3",highlightthickness=1); left.pack(side="left",fill="both",expand=True,padx=(0,10))
        tk.Label(left,text="Distribusi Jenis Masalah",font=("Segoe UI Semibold",13),bg="white",fg="#163D2A").pack(anchor="w",padx=20,pady=18)
        rows=self.query("SELECT category,COUNT(*) n FROM reports GROUP BY category ORDER BY n DESC")
        for cat,n in rows:
            r=tk.Frame(left,bg="white"); r.pack(fill="x",padx=20,pady=8)
            tk.Label(r,text=cat,font=("Segoe UI",10),bg="white",fg="#43544A").pack(side="left")
            tk.Label(r,text=str(n),font=("Segoe UI Semibold",10),bg="white",fg="#163D2A").pack(side="right")
            bar=tk.Frame(left,bg="#EAF1ED",height=8); bar.pack(fill="x",padx=20)
            width=min(100,max(5,int(n/max(1,total)*100)))
            tk.Frame(bar,bg="#55A878",height=8,width=width*4).place(x=0,y=0)
        right=tk.Frame(lower,bg="white",highlightbackground="#E0E8E3",highlightthickness=1); right.pack(side="right",fill="both",expand=True,padx=(10,0))
        tk.Label(right,text="Laporan Terbaru",font=("Segoe UI Semibold",13),bg="white",fg="#163D2A").pack(anchor="w",padx=20,pady=18)
        for r in self.query("SELECT code,category,location,status FROM reports ORDER BY id DESC LIMIT 6"):
            line=tk.Frame(right,bg="white"); line.pack(fill="x",padx=20,pady=7)
            tk.Label(line,text=r["code"],font=("Consolas",9),bg="white",fg="#6C7B72").pack(side="left")
            tk.Label(line,text=r["category"],font=("Segoe UI Semibold",10),bg="white",fg="#163D2A").pack(side="left",padx=12)
            tk.Label(line,text=r["status"],font=("Segoe UI",9),bg="white",fg="#527061").pack(side="right")

    def show_form(self):
        self.clear(); self.header("Buat Pengaduan", "Masukkan informasi kejadian lingkungan secara lengkap.")
        box=tk.Frame(self.content,bg="white",highlightbackground="#DDE7E1",highlightthickness=1)
        box.pack(fill="both",expand=True,padx=30,pady=(0,25))
        fields={}
        labels=[("Nama Pelapor","reporter"),("Kategori","category"),("Lokasi","location"),("Kecamatan","district"),
                ("Latitude","lat"),("Longitude","lon"),("Tingkat Masalah","severity"),("Keterangan","description")]
        for i,(lab,key) in enumerate(labels):
            tk.Label(box,text=lab,font=("Segoe UI Semibold",9),bg="white",fg="#405248").grid(row=i//2*2,column=i%2,padx=22,pady=(20 if i<2 else 10,4),sticky="w")
            if key in ("category","severity"):
                vals={"category":["Sampah","Pencemaran Air","Polusi Udara","Ruang Hijau"],
                      "severity":["Rendah","Sedang","Tinggi"]}[key]
                v=ttk.Combobox(box,values=vals,state="readonly",font=("Segoe UI",10)); v.set(vals[0])
            else:
                v=tk.Entry(box,font=("Segoe UI",10),bg="#F8FAF9",relief="flat",highlightthickness=1,highlightbackground="#D7E2DB")
            v.grid(row=i//2*2+1,column=i%2,padx=22,pady=(0,8),sticky="ew",ipady=7)
            fields[key]=v
        fields["description"].grid(row=7,column=0,columnspan=2,padx=22,pady=(0,20),sticky="ew",ipady=20)
        # Fix label/field rows for description
        box.grid_columnconfigure(0,weight=1); box.grid_columnconfigure(1,weight=1)
        def save():
            reporter=fields["reporter"].get().strip()
            if not reporter or not fields["location"].get().strip() or not fields["description"].get().strip():
                messagebox.showwarning("Data belum lengkap","Nama, lokasi, dan keterangan wajib diisi."); return
            try:
                lat=float(fields["lat"].get() or 0); lon=float(fields["lon"].get() or 0)
            except:
                messagebox.showwarning("Lokasi","Latitude dan longitude harus berupa angka."); return
            code=next_code(); now=datetime.now().strftime("%Y-%m-%d %H:%M")
            sev=fields["severity"].get()
            status={"Rendah":"Baru","Sedang":"Diverifikasi","Tinggi":"Diproses"}[sev]
            con=db()
            con.execute("""INSERT INTO reports(code,reporter,category,location,district,latitude,longitude,severity,description,status,officer,created_at,updated_at)
                        VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                        (code,reporter,fields["category"].get(),fields["location"].get(),fields["district"].get(),lat,lon,sev,fields["description"].get(),status,"",now,now))
            con.execute("INSERT INTO activity(report_code,actor,action,created_at) VALUES(?,?,?,?)",(code,self.username,"Membuat laporan",now))
            con.commit(); con.close()
            messagebox.showinfo("Berhasil",f"Laporan {code} berhasil dibuat.")
            self.show_reports()
        tk.Button(box,text="SIMPAN LAPORAN",command=save,font=("Segoe UI Semibold",10),bg="#1F7A4D",fg="white",activebackground="#185E3A",bd=0,padx=24,pady=12,cursor="hand2").grid(row=9,column=1,padx=22,pady=10,sticky="e")

    def show_reports(self):
        self.clear(); self.header("Data Pengaduan","Pencarian, verifikasi, penugasan, dan pemantauan status.")
        toolbar=tk.Frame(self.content,bg="#F4F7F5"); toolbar.pack(fill="x",padx=30,pady=(0,10))
        search=tk.Entry(toolbar,font=("Segoe UI",10),bg="white",relief="flat",highlightthickness=1,highlightbackground="#D7E2DB")
        search.pack(side="left",fill="x",expand=True,ipady=8)
        status=ttk.Combobox(toolbar,values=["Semua","Baru","Diverifikasi","Diproses","Selesai"],state="readonly",width=16); status.set("Semua"); status.pack(side="left",padx=8)
        tree=ttk.Treeview(self.content,columns=("code","category","location","district","severity","status","officer","date"),show="headings")
        for col,text,w in [("code","Nomor",150),("category","Kategori",140),("location","Lokasi",180),("district","Kecamatan",120),("severity","Prioritas",90),("status","Status",110),("officer","Petugas",110),("date","Tanggal",120)]:
            tree.heading(col,text=text); tree.column(col,width=w)
        tree.pack(fill="both",expand=True,padx=30,pady=(0,10))
        def load():
            for x in tree.get_children(): tree.delete(x)
            q=search.get().strip(); st=status.get()
            sql="SELECT * FROM reports WHERE (code LIKE ? OR category LIKE ? OR location LIKE ? OR district LIKE ?)"
            args=[f"%{q}%"]*4
            if st!="Semua": sql+=" AND status=?"; args.append(st)
            sql+=" ORDER BY id DESC"
            for r in self.query(sql,args):
                tree.insert("", "end", values=(r["code"],r["category"],r["location"],r["district"],r["severity"],r["status"],r["officer"] or "-",r["created_at"][:10]))
        load(); search.bind("<KeyRelease>",lambda e:load()); status.bind("<<ComboboxSelected>>",lambda e:load())
        actions=tk.Frame(self.content,bg="#F4F7F5"); actions.pack(fill="x",padx=30,pady=(0,18))
        tk.Button(actions,text="Lihat Detail",command=lambda:self.detail(tree),bg="#1F7A4D",fg="white",bd=0,padx=18,pady=9).pack(side="left")
        tk.Button(actions,text="Export CSV",command=self.export_csv,bg="#E7EFEA",fg="#234C37",bd=0,padx=18,pady=9).pack(side="left",padx=8)

    def detail(self,tree):
        sel=tree.selection()
        if not sel: return
        code=tree.item(sel[0],"values")[0]
        r=self.query("SELECT * FROM reports WHERE code=?",(code,))[0]
        win=tk.Toplevel(self); win.title(code); win.geometry("650x560"); win.configure(bg="white")
        tk.Label(win,text=code,font=("Segoe UI Semibold",20),bg="white",fg="#163D2A").pack(anchor="w",padx=25,pady=(22,2))
        tk.Label(win,text=f"{r['category']} • {r['severity']} • {r['status']}",font=("Segoe UI",10),bg="white",fg="#6C7B72").pack(anchor="w",padx=25,pady=(0,18))
        info=tk.Frame(win,bg="#F5F8F6"); info.pack(fill="x",padx=25)
        for lab,val in [("Pelapor",r["reporter"]),("Lokasi",r["location"]),("Kecamatan",r["district"]),("Koordinat",f"{r['latitude']}, {r['longitude']}"),("Petugas",r["officer"] or "Belum ditugaskan")]:
            tk.Label(info,text=f"{lab}: {val}",font=("Segoe UI",10),bg="#F5F8F6",fg="#34483D").pack(anchor="w",padx=15,pady=6)
        tk.Label(win,text="Keterangan",font=("Segoe UI Semibold",10),bg="white",fg="#163D2A").pack(anchor="w",padx=25,pady=(20,6))
        txt=tk.Text(win,height=7,font=("Segoe UI",10),bg="#F8FAF9",relief="flat"); txt.pack(fill="x",padx=25); txt.insert("1.0",r["description"]); txt.config(state="disabled")
        tk.Button(win,text="Tutup",command=win.destroy,bg="#1F7A4D",fg="white",bd=0,padx=22,pady=9).pack(anchor="e",padx=25,pady=20)

    def export_csv(self):
        path=filedialog.asksaveasfilename(defaultextension=".csv",filetypes=[("CSV","*.csv")],initialfile="ecoreport_laporan.csv")
        if not path: return
        rows=self.query("SELECT * FROM reports ORDER BY id DESC")
        with open(path,"w",newline="",encoding="utf-8-sig") as f:
            w=csv.writer(f); w.writerow(rows[0].keys() if rows else ["data"])
            for r in rows: w.writerow(list(r))
        messagebox.showinfo("Export selesai",path)

    def show_map(self):
        self.clear(); self.header("Peta & Wilayah",f"Sebaran laporan • {FOCUS_REGION}")
        top=tk.Frame(self.content,bg="white",highlightbackground="#DDE7E1",highlightthickness=1); top.pack(fill="x",padx=30,pady=(0,12))
        tk.Label(top,text="GIS VIEW",font=("Segoe UI Semibold",9),bg="white",fg="#2E8B57").pack(anchor="w",padx=20,pady=(16,2))
        tk.Label(top,text="Peta interaktif siap dikembangkan dengan layer GIS",font=("Segoe UI Semibold",15),bg="white",fg="#163D2A").pack(anchor="w",padx=20,pady=(0,16))
        tk.Label(top,text="Titik laporan tersimpan dengan koordinat. Untuk deployment GIS, data dapat dihubungkan ke Folium/QGIS.",font=("Segoe UI",10),bg="white",fg="#6D7D74").pack(anchor="w",padx=20,pady=(0,16))
        mapbox=tk.Frame(self.content,bg="#DCE8E1"); mapbox.pack(fill="both",expand=True,padx=30,pady=(0,20))
        canvas=tk.Canvas(mapbox,bg="#EAF2ED",highlightthickness=0); canvas.pack(fill="both",expand=True)
        canvas.create_text(30,30,text=f"{FOCUS_REGION} • ENVIRONMENTAL REPORT MAP",anchor="nw",font=("Segoe UI Semibold",14),fill="#28563F")
        rows=self.query("SELECT code,category,latitude,longitude,severity FROM reports WHERE latitude<>0 OR longitude<>0")
        for i,r in enumerate(rows):
            x=120+(i%5)*150; y=120+(i//5)*95
            color={"Tinggi":"#C2410C","Sedang":"#D97706","Rendah":"#16A34A"}.get(r["severity"],"#2563EB")
            canvas.create_oval(x,y,x+18,y+18,fill=color,outline="")
            canvas.create_text(x+25,y+9,text=r["code"],anchor="w",font=("Segoe UI",9),fill="#345246")
        canvas.create_text(30,canvas.winfo_height()-30,text="Legenda:  ● Tinggi   ● Sedang   ● Rendah",anchor="sw",font=("Segoe UI",9),fill="#49665A")

    def show_monitoring(self):
        self.clear(); self.header("Monitoring Lingkungan","Modul awal untuk data kualitas lingkungan dan inspeksi lapangan.")
        cards=tk.Frame(self.content,bg="#F4F7F5"); cards.pack(fill="x",padx=30)
        for i,(t,v,a) in enumerate([("Titik Pantau Air","12","#2563EB"),("Objek Persampahan","24","#16A34A"),("Sumber Emisi","8","#D97706"),("RTH Terpantau","17","#2E8B57")]):
            c=self.card(cards,t,v,a); c.grid(row=0,column=i,sticky="nsew",padx=(0,12)); cards.grid_columnconfigure(i,weight=1)
        box=tk.Frame(self.content,bg="white",highlightbackground="#DDE7E1",highlightthickness=1); box.pack(fill="both",expand=True,padx=30,pady=20)
        tk.Label(box,text="Parameter Monitoring",font=("Segoe UI Semibold",14),bg="white",fg="#163D2A").pack(anchor="w",padx=20,pady=18)
        for item,desc in [("Kualitas Air","pH • DO • BOD • COD • TSS"),("Udara","PM2.5 • PM10 • CO • NO2 • SO2"),("Persampahan","volume • armada • TPS • TPA"),("Ruang Hijau","luas • kondisi • fasilitas")]:
            r=tk.Frame(box,bg="#F7FAF8"); r.pack(fill="x",padx=20,pady=5)
            tk.Label(r,text=item,font=("Segoe UI Semibold",10),bg="#F7FAF8",fg="#234B37").pack(side="left",padx=14,pady=10)
            tk.Label(r,text=desc,font=("Segoe UI",9),bg="#F7FAF8",fg="#6A7C72").pack(side="right",padx=14)

    def show_analytics(self):
        self.clear(); self.header("Analitik Lingkungan","Ringkasan data untuk membantu membaca pola pengaduan.")
        cats=self.query("SELECT category,COUNT(*) n FROM reports GROUP BY category")
        levels=self.query("SELECT severity,COUNT(*) n FROM reports GROUP BY severity")
        box=tk.Frame(self.content,bg="white",highlightbackground="#DDE7E1",highlightthickness=1); box.pack(fill="both",expand=True,padx=30,pady=(0,20))
        tk.Label(box,text="Insight Data",font=("Segoe UI Semibold",14),bg="white",fg="#163D2A").pack(anchor="w",padx=20,pady=18)
        if cats:
            top=max(cats,key=lambda x:x["n"])
            tk.Label(box,text=f"Kategori laporan terbanyak saat ini: {top['category']} ({top['n']} laporan).",font=("Segoe UI",11),bg="white",fg="#345246").pack(anchor="w",padx=20,pady=8)
        if levels:
            hi=next((x["n"] for x in levels if x["severity"]=="Tinggi"),0)
            tk.Label(box,text=f"Laporan prioritas tinggi: {hi}. Data ini dapat dipakai untuk menentukan prioritas tindak lanjut.",font=("Segoe UI",11),bg="white",fg="#345246").pack(anchor="w",padx=20,pady=8)
        tk.Label(box,text="Catatan: insight di atas dihitung langsung dari database lokal aplikasi.",font=("Segoe UI",9),bg="white",fg="#87958E").pack(anchor="w",padx=20,pady=(18,8))

    def show_reporting(self):
        self.clear(); self.header("Laporan & Ekspor","Output data untuk kebutuhan dokumentasi dan presentasi.")
        box=tk.Frame(self.content,bg="white",highlightbackground="#DDE7E1",highlightthickness=1); box.pack(fill="x",padx=30,pady=(0,15))
        tk.Label(box,text="Laporan Wilayah",font=("Segoe UI Semibold",15),bg="white",fg="#163D2A").pack(anchor="w",padx=22,pady=(20,5))
        total=self.query("SELECT COUNT(*) n FROM reports")[0]["n"]
        done=self.query("SELECT COUNT(*) n FROM reports WHERE status='Selesai'")[0]["n"]
        tk.Label(box,text=f"{FOCUS_REGION}  •  Total {total} pengaduan  •  {done} selesai",font=("Segoe UI",10),bg="white",fg="#66766D").pack(anchor="w",padx=22,pady=(0,18))
        tk.Button(box,text="EXPORT DATA CSV",command=self.export_csv,bg="#1F7A4D",fg="white",bd=0,padx=22,pady=11).pack(anchor="w",padx=22,pady=(0,20))
        note=tk.Frame(self.content,bg="#EDF7F0"); note.pack(fill="x",padx=30,pady=5)
        tk.Label(note,text="Portfolio-ready",font=("Segoe UI Semibold",11),bg="#EDF7F0",fg="#1F6B45").pack(anchor="w",padx=18,pady=(14,2))
        tk.Label(note,text="Prototype ini menunjukkan alur pengaduan, database SQLite, dashboard, GIS-ready coordinates, analytics, dan export.",font=("Segoe UI",10),bg="#EDF7F0",fg="#4D6B5B").pack(anchor="w",padx=18,pady=(0,14))

    def logout(self):
        if messagebox.askyesno("Keluar","Keluar dari aplikasi?"):
            self.destroy()
            Login().mainloop()

class Login(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("EcoReport • Login")
        self.geometry("900x560"); self.configure(bg="#123B2A"); self.resizable(False,False)
        left=tk.Frame(self,bg="#123B2A",width=450); left.pack(side="left",fill="both")
        tk.Label(left,text="🌿",font=("Segoe UI",48),bg="#123B2A",fg="#8BE0A9").pack(anchor="w",padx=55,pady=(90,5))
        tk.Label(left,text="EcoReport",font=("Segoe UI Semibold",34),bg="#123B2A",fg="white").pack(anchor="w",padx=55)
        tk.Label(left,text="Environmental Monitoring\n& Reporting System",font=("Segoe UI",15),bg="#123B2A",fg="#C5DED0",justify="left").pack(anchor="w",padx=58,pady=10)
        tk.Label(left,text="Prototype portfolio • Python + SQLite + GIS-ready",font=("Segoe UI",9),bg="#123B2A",fg="#89B39E").pack(anchor="w",padx=58,pady=35)
        right=tk.Frame(self,bg="white"); right.pack(side="right",fill="both",expand=True)
        tk.Label(right,text="Selamat datang",font=("Segoe UI Semibold",24),bg="white",fg="#163D2A").pack(anchor="w",padx=50,pady=(95,5))
        tk.Label(right,text="Masuk untuk mengelola data lingkungan.",font=("Segoe UI",10),bg="white",fg="#7A8981").pack(anchor="w",padx=50,pady=(0,30))
        tk.Label(right,text="USERNAME",font=("Segoe UI Semibold",8),bg="white",fg="#5E7066").pack(anchor="w",padx=50)
        self.u=tk.Entry(right,font=("Segoe UI",11),bg="#F7FAF8",relief="flat",highlightthickness=1,highlightbackground="#D7E2DB"); self.u.pack(fill="x",padx=50,pady=(5,15),ipady=9)
        tk.Label(right,text="PASSWORD",font=("Segoe UI Semibold",8),bg="white",fg="#5E7066").pack(anchor="w",padx=50)
        self.p=tk.Entry(right,show="•",font=("Segoe UI",11),bg="#F7FAF8",relief="flat",highlightthickness=1,highlightbackground="#D7E2DB"); self.p.pack(fill="x",padx=50,pady=(5,20),ipady=9)
        tk.Button(right,text="MASUK KE ECORERPORT".replace("ECORERPORT","ECOREPORT"),command=self.login,font=("Segoe UI Semibold",10),bg="#1F7A4D",fg="white",activebackground="#185E3A",bd=0,pady=12,cursor="hand2").pack(fill="x",padx=50)
        tk.Label(right,text="Demo: admin / EcoEnv2026!",font=("Segoe UI",9),bg="white",fg="#87958E").pack(anchor="w",padx=50,pady=15)
        self.u.focus()
        self.bind("<Return>",lambda e:self.login())
    def login(self):
        con=db(); r=con.execute("SELECT * FROM users WHERE username=? AND password=?",(self.u.get().strip(),self.p.get())).fetchone(); con.close()
        if not r:
            messagebox.showerror("Login gagal","Username atau password salah."); return
        self.destroy()
        App(r["username"],r["role"]).mainloop()

if __name__ == "__main__":
    init_db()
    Login().mainloop()
