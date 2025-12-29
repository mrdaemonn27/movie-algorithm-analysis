import streamlit as st
import pandas as pd
import time
import sys
import matplotlib.pyplot as plt

# Konfigurasi batas rekursi
sys.setrecursionlimit(50000)

st.set_page_config(page_title="Sistem Pengelolaan Film", layout="wide")

# 1. ALGORITMA SORTING (PENGURUTAN)

def partition(data, low, high, key='rating'):
    # Pivot menggunakan elemen terakhir
    pivot = data[high][key]
    i = low - 1
    for j in range(low, high):
        # Sorting Descending (Besar ke Kecil)
        if data[j][key] >= pivot:
            i += 1
            data[i], data[j] = data[j], data[i]
    data[i + 1], data[high] = data[high], data[i + 1]
    return i + 1

# --- Quick Sort Rekursif ---
def quick_sort_recursive(data, low, high, key='rating'):
    if low < high:
        pi = partition(data, low, high, key)
        quick_sort_recursive(data, low, pi - 1, key)
        quick_sort_recursive(data, pi + 1, high, key)
    return data

# --- Quick Sort Iteratif ---
def quick_sort_iterative(data, low, high, key='rating'):
    size = high - low + 1
    stack = [0] * size
    top = -1
    
    top += 1
    stack[top] = low
    top += 1
    stack[top] = high
    
    while top >= 0:
        h = stack[top]
        top -= 1
        l = stack[top]
        top -= 1
        
        p = partition(data, l, h, key)
        
        if p - 1 > l:
            top += 1
            stack[top] = l
            top += 1
            stack[top] = p - 1
            
        if p + 1 < h:
            top += 1
            stack[top] = p + 1
            top += 1
            stack[top] = h
    return data

# --- Insertion Sort Iteratif ---
def insertion_sort_iterative(data, key='rating'):
    # Algoritma sederhana namun lambat untuk data besar (O(n^2))
    # Efektif untuk data < 100 baris
    for i in range(1, len(data)):
        key_item = data[i]
        j = i - 1
        # Descending: geser elemen yang lebih kecil dari key ke kanan
        while j >= 0 and key_item[key] > data[j][key]:
            data[j + 1] = data[j]
            j -= 1
        data[j + 1] = key_item
    return data

# --- Insertion Sort Rekursif ---
def insertion_sort_recursive(data, key='rating', n=None):
    # Jika n tidak diberikan, inisialisasi dengan panjang data
    if n is None:
        n = len(data)
    
    # Base case: jika hanya 1 elemen, sudah terurut
    if n <= 1:
        return data

    # Sort n-1 elemen pertama secara rekursif
    insertion_sort_recursive(data, key, n - 1)

    # Sisipkan elemen ke-n (index n-1) ke posisi yang benar
    last = data[n - 1]
    j = n - 2

    # Descending: geser elemen yang lebih kecil dari key ke kanan
    while j >= 0 and last[key] > data[j][key]:
        data[j + 1] = data[j]
        j -= 1
    data[j + 1] = last
    return data

# 2. ALGORITMA SEARCHING (PENCARIAN)

# --- Binary Search Iteratif ---
def binary_search_iterative(data, target, key='rating'):
    # Syarat Mutlak: Data HARUS terurut dulu (Descending)
    low = 0
    high = len(data) - 1
    
    while low <= high:
        mid = (low + high) // 2
        mid_val = data[mid][key]
        
        if mid_val == target:
            return mid  # Data ditemukan
        elif mid_val < target:
            # Karena descending, jika nilai tengah < target, cari di kiri
            high = mid - 1
        else:
            # Jika nilai tengah > target, cari di kanan
            low = mid + 1
            
    return -1 # Data tidak ditemukan


# FUNGSI BANTUAN (LOAD DATA)

@st.cache_data
def load_data(file):
    try:
        df = pd.read_csv(file)
        required = ['title', 'rating', 'year', 'votes', 'genre']
        if not all(c in df.columns for c in required):
            st.error("Format kolom salah.")
            return None
            
        df = df.dropna(subset=['rating', 'votes'])
        df['year'] = df['year'].astype(str).str.extract(r'(\d{4})').astype(float)
        df['votes'] = df['votes'].astype(str).str.replace(',', '', regex=False)
        df['votes'] = pd.to_numeric(df['votes'], errors='coerce')
        df['rating'] = pd.to_numeric(df['rating'], errors='coerce')
        df = df.dropna()
        return df.reset_index(drop=True)
    except:
        return None


# USER INTERFACE (UI)

st.title("Sistem Pengelolaan Film & Analisis Algoritma")
st.write("Studi Kasus: Pengurutan (Quick/Insertion) dan Pencarian (Binary Search).")

# Sidebar Upload
st.sidebar.header("Input Data")
uploaded_file = st.sidebar.file_uploader("Upload CSV", type=["csv"])

if uploaded_file:
    df = load_data(uploaded_file)
    if df is not None:
        st.sidebar.success(f"Total Data: {len(df)}")
        
        # MENU NAVIGASI UTAMA
        menu = st.sidebar.radio("Menu Utama", [
            "1. Pengurutan Data (Sorting)", 
            "2. Pencarian Data (Binary Search)",
            "3. Analisis Kompleksitas (Benchmark)"
        ])

        # --- FITUR 1: SORTING (Hybrid Logic) ---
        if menu == "1. Pengurutan Data (Sorting)":
            st.header("Pengurutan Data Film")
            st.write("Implementasi pemilihan algoritma berdasarkan ukuran data.")
            
            # Preview Data Mentah
            st.write("Data Awal (Belum Terurut):")
            st.dataframe(df)
            
            col1, col2 = st.columns(2)
            with col1:
                sort_key = st.selectbox("Urutkan Berdasarkan:", ["rating", "votes", "year"])
            with col2:
                # Logika Adaptif (Manual Override available)
                rekomen = "Insertion Sort (Iteratif)" if len(df) < 200 else "Quick Sort (Iteratif)"
                algo_choice = st.selectbox(
                    f"Pilih Algoritma (Rekomendasi: {rekomen})", 
                    ["Insertion Sort (Iteratif)", "Insertion Sort (Rekursif)", "Quick Sort (Iteratif)", "Quick Sort (Rekursif)"]
                )
            
            if st.button("Proses Sorting"):
                data_list = df.to_dict('records')
                start = time.perf_counter()
                
                # Pemilihan Algoritma
                if algo_choice == "Insertion Sort (Iteratif)":
                    sorted_data = insertion_sort_iterative(data_list, sort_key)
                elif algo_choice == "Insertion Sort (Rekursif)":
                    # Peringatan: Rekursi Insertion Sort di Python boros stack
                    sorted_data = insertion_sort_recursive(data_list, sort_key)
                elif algo_choice == "Quick Sort (Iteratif)":
                    sorted_data = quick_sort_iterative(data_list, 0, len(data_list)-1, sort_key)
                else:
                    sorted_data = quick_sort_recursive(data_list, 0, len(data_list)-1, sort_key)
                
                end = time.perf_counter()
                
                # Menampilkan Waktu Eksekusi dengan Jelas
                exec_time_ms = (end - start) * 1000
                st.success(f"Selesai! Menggunakan algoritma **{algo_choice}**")
                st.info(f"Waktu Eksekusi: **{exec_time_ms:.4f} ms**")
                
                st.dataframe(pd.DataFrame(sorted_data))

        # --- FITUR 2: SEARCHING (Binary Search) ---
        elif menu == "2. Pencarian Data (Binary Search)":
            st.header("Pencarian Cepat (Binary Search)")
            st.info("Binary Search memerlukan data yang SUDAH TERURUT. Sistem akan mengurutkan data terlebih dahulu secara otomatis.")
            
            search_target = st.number_input("Masukkan Rating yang dicari (Contoh: 8.5):", min_value=0.0, max_value=10.0, step=0.1)
            
            if st.button("Cari Film"):
                # 1. Sorting dulu (Syarat Binary Search)
                data_list = df.to_dict('records')
                # Gunakan Quick Sort Iteratif agar cepat
                sorted_data = quick_sort_iterative(data_list, 0, len(data_list)-1, 'rating')
                
                # 2. Proses Binary Search
                start_search = time.perf_counter()
                index_result = binary_search_iterative(sorted_data, search_target, 'rating')
                end_search = time.perf_counter()
                
                if index_result != -1:
                    # Menemukan satu data, ambil data di sekitarnya jika ada duplikat
                    found_movie = sorted_data[index_result]
                    st.success(f"Ditemukan dalam {(end_search-start_search)*1000:.6f} ms!")
                    
                    st.write(f"**Judul:** {found_movie['title']}")
                    st.write(f"**Rating:** {found_movie['rating']}")
                    st.write(f"**Genre:** {found_movie['genre']}")
                    st.write("---")
                    st.write("*Catatan: Binary Search mengembalikan salah satu hasil yang cocok pertama kali ditemukan.*")
                else:
                    st.warning(f"Tidak ada film dengan rating {search_target}")

        # --- FITUR 3: BENCHMARK ---
        elif menu == "3. Analisis Kompleksitas (Benchmark)":
            st.header("Analisis Perbandingan Algoritma")
            st.write("Benchmark: Quick Sort (Iter/Rec), Insertion Sort (Iter/Rec), dan Binary Search.")
            st.warning("Catatan: Insertion Sort (terutama Rekursif) akan sangat lambat pada data besar (N > 1500).")
            
            input_mode = st.radio("Mode Input Size:", ["Otomatis (Cepat)", "Manual"])
            input_sizes = []
            
            if input_mode == "Otomatis (Cepat)":
                base = len(df)
                # Dibatasi agar Insertion sort tidak hang komputer
                input_sizes = [100, 500, 1000, 1500]
            else:
                txt = st.text_input("Masukkan N (pisahkan koma):", "100, 500, 1000, 1500")
                try:
                    input_sizes = [int(x) for x in txt.split(',')]
                except:
                    pass
            
            if input_sizes and st.button("Mulai Analisis"):
                res_iter = []
                res_rec = []
                res_ins_iter = []
                res_ins_rec = [] # Penambahan list hasil Insertion Rekursif
                res_bin = []
                progress = st.progress(0)
                
                for i, n in enumerate(input_sizes):
                    # Persiapan data dummy
                    raw = df.to_dict('records')
                    if n <= len(raw):
                        data_test = raw[:n]
                    else:
                        data_test = (raw * (n // len(raw) + 1))[:n]
                    
                    # 1. Quick Sort Iteratif
                    d1 = data_test.copy()
                    s1 = time.perf_counter()
                    quick_sort_iterative(d1, 0, len(d1)-1, 'rating')
                    res_iter.append((time.perf_counter() - s1)*1000)
                    
                    # 2. Quick Sort Rekursif
                    d2 = data_test.copy()
                    s2 = time.perf_counter()
                    quick_sort_recursive(d2, 0, len(d2)-1, 'rating')
                    res_rec.append((time.perf_counter() - s2)*1000)

                    # 3a. Insertion Sort Iteratif (Skip jika N > 3000 agar tidak hang)
                    if n > 3000:
                         res_ins_iter.append(None)
                    else:
                         d3 = data_test.copy()
                         s3 = time.perf_counter()
                         insertion_sort_iterative(d3, 'rating')
                         res_ins_iter.append((time.perf_counter() - s3)*1000)

                    # 3b. Insertion Sort Rekursif (Sangat berat, skip jika N > 1500)
                    if n > 1500:
                         res_ins_rec.append(None)
                    else:
                         try:
                             d3b = data_test.copy()
                             s3b = time.perf_counter()
                             insertion_sort_recursive(d3b, 'rating')
                             res_ins_rec.append((time.perf_counter() - s3b)*1000)
                         except RecursionError:
                             res_ins_rec.append(None) # Handle error jika stack overflow

                    # 4. Binary Search (Harus diurutkan dulu)
                    d4_sorted = quick_sort_iterative(data_test.copy(), 0, len(data_test)-1, 'rating')
                    target = 8.5 # Dummy target
                    s4 = time.perf_counter()
                    binary_search_iterative(d4_sorted, target, 'rating')
                    res_bin.append((time.perf_counter() - s4)*1000)
                    
                    progress.progress((i+1)/len(input_sizes))
                
                # Visualisasi
                fig, ax = plt.subplots(figsize=(10, 6))
                ax.plot(input_sizes, res_iter, label='Quick Sort Iteratif', marker='o', color='blue')
                ax.plot(input_sizes, res_rec, label='Quick Sort Rekursif', marker='x', linestyle='--', color='red')
                
                # Filter None untuk Insertion Sort Iteratif
                valid_ins_iter = [(x, y) for x, y in zip(input_sizes, res_ins_iter) if y is not None]
                if valid_ins_iter:
                    ax.plot([x for x,y in valid_ins_iter], [y for x,y in valid_ins_iter], label='Insertion Sort (Iteratif)', marker='s', color='green')

                # Filter None untuk Insertion Sort Rekursif
                valid_ins_rec = [(x, y) for x, y in zip(input_sizes, res_ins_rec) if y is not None]
                if valid_ins_rec:
                    ax.plot([x for x,y in valid_ins_rec], [y for x,y in valid_ins_rec], label='Insertion Sort (Rekursif)', marker='^', linestyle=':', color='purple')
                
                ax.plot(input_sizes, res_bin, label='Binary Search', marker='*', color='orange')

                ax.set_xlabel('Jumlah Input (N)')
                ax.set_ylabel('Waktu (ms)')
                ax.set_title('Perbandingan Kompleksitas Waktu')
                ax.legend()
                ax.grid(True)
                st.pyplot(fig)
                
                # Tampilkan Tabel (Diperbaiki agar menampilkan semua kolom)
                st.write("### Data Hasil Benchmark")
                # Format angka float agar rapi (2 desimal)
                def format_ms(val):
                    return f"{val:.4f}" if val is not None else "-"

                # Membuat DataFrame hasil
                df_result = pd.DataFrame({
                    "N": input_sizes,
                    "Quick Iter (ms)": res_iter,
                    "Quick Rec (ms)": res_rec,
                    "Insertion Iter (ms)": res_ins_iter,
                    "Insertion Rec (ms)": res_ins_rec,
                    "Binary Search (ms)": res_bin
                })
                
                # Tampilkan DataFrame
                st.dataframe(df_result)

else:
    st.info("Silakan upload file CSV.")